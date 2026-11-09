#!/usr/bin/env python3
"""Rank audit runs against the saved reference and write summary tables.

rank(run) = sum over scored metrics of
            weight_e * |coefficient| * direction * (run - reference) / cohort_std
where direction = +1 for higher_is_better metrics and -1 otherwise, the
reference is the ``noisy_ht`` row of the saved scoring/scores_test.json, and
cohort_std is the population std of that metric over the cohort's accepted
runs (a constant metric contributes zero).
"""

from __future__ import annotations

import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RES = HERE / "results"
SCIENTIFIC = ["noisy_ht", "better_fallback", "better_union", "weaker_direct",
              "weaker_conservative", "weaker_half_calibration", "alt_ppi_pp"]
SEED_FILES = {"hidden": "test_hidden.json", "seed101": "test_seed101.json",
              "seed202": "test_seed202.json"}


def load(path: Path) -> dict:
    return json.loads(path.read_text())


def scored_metrics(ref: dict) -> list[tuple[str, str, float, int]]:
    out = []
    for exp, spec in ref["experiments"].items():
        for metric, mdef in spec["metrics"].items():
            coef = abs(float(mdef["coefficient"]))
            if coef == 0:
                continue
            direction = 1 if mdef["higher_is_better"] else -1
            out.append((exp, metric, float(spec["weight"]) * coef, direction))
    return out


def vector(scores: dict, row: str, metrics) -> list[float]:
    return [float(scores[e][row][m]) for e, m, _, _ in metrics]


def stds(vectors: list[list[float]]) -> list[float]:
    out = []
    for k in range(len(vectors[0])):
        vals = [v[k] for v in vectors]
        mu = sum(vals) / len(vals)
        out.append(math.sqrt(sum((x - mu) ** 2 for x in vals) / len(vals)))
    return out


def rank(v, r, sd, metrics) -> float:
    total = 0.0
    for k, (_, _, w, d) in enumerate(metrics):
        if sd[k] > 0:
            total += w * d * (v[k] - r[k]) / sd[k]
    return total


def passed(scores: dict, row: str) -> bool:
    return row not in scores["_metadata"].get("failed_certifiers", [])


def fmt(x: float) -> str:
    return f"{x:+.3f}"


def main() -> None:
    ref_spec = load(ROOT / "scoring" / "reference.json")
    metrics = scored_metrics(ref_spec)
    saved = load(ROOT / "scoring" / "scores_test.json")
    r = vector(saved, "noisy_ht", metrics)

    seeds = {k: load(RES / f) for k, f in SEED_FILES.items() if (RES / f).exists()}
    hidden = seeds["hidden"]
    sanity = vector(hidden, "noisy_ht", metrics) == r

    cohort = []
    for s in seeds.values():
        for row in SCIENTIFIC:
            if row in s.get("synthetic_power_comparison", {}) and passed(s, row):
                cohort.append(vector(s, row, metrics))
    sd = stds(cohort)

    summary: dict = {"metrics": [f"{e}/{m}" for e, m, _, _ in metrics],
                     "reference_vector": r, "cohort_size": len(cohort), "cohort_std": sd,
                     "audit_reference_matches_saved": sanity, "runs": {}, "seed_check": {}}

    # Every certifier at the hidden seed (shortcuts included).
    lines = ["| Certifier | Passed | Main T2 | Curve T2 | Sweep T2 | Oracle gap | T1 (hq) | T1 worst | Rank vs ref |",
             "|---|---|---:|---:|---:|---:|---:|---:|---:|"]
    certs = hidden["_metadata"]["certifiers"]
    for row in certs:
        v = vector(hidden, row, metrics)
        ok = passed(hidden, row)
        rk = rank(v, r, sd, metrics)
        t1 = hidden["synthetic_type1_control"][row]
        summary["runs"][f"hidden/{row}"] = {"passed": ok, "rank": rk, "values": v,
                                            "reasons": hidden["_validity"][row]["reasons"]}
        lines.append(f"| {row} | {'yes' if ok else '**FAILED**'} | "
                     f"{hidden['synthetic_power_comparison'][row]['type2_error']:.3f} | "
                     f"{hidden['synthetic_type2_curve'][row]['type2_error']:.3f} | "
                     f"{hidden['judge_quality_sweep'][row]['type2_error']:.3f} | "
                     f"{hidden['oracle_gap'][row]['oracle_gap']:.3f} | "
                     f"{t1['type1_error']:.3f} | {t1['type1_error_worst_regime']:.3f} | {fmt(rk)} |")
    for row in ("direct_ht", "oracle_noisy_ht"):
        t1 = hidden["synthetic_type1_control"][row]
        lines.append(f"| {row} (evaluator row) | n/a | "
                     f"{hidden['synthetic_power_comparison'][row]['type2_error']:.3f} | "
                     f"{hidden['synthetic_type2_curve'][row]['type2_error']:.3f} | "
                     f"{hidden['judge_quality_sweep'][row]['type2_error']:.3f} | "
                     f"{hidden['oracle_gap'][row]['oracle_gap']:.3f} | "
                     f"{t1['type1_error']:.3f} | {t1['type1_error_worst_regime']:.3f} | n/a |")
    table_hidden = "\n".join(lines)

    # Paired seed check: gains of each scientific variant vs the reference on
    # the same instances, against the reference's own spread across draws.
    ref_ranks = {k: rank(vector(s, "noisy_ht", metrics), r, sd, metrics) for k, s in seeds.items()}
    spread = max(ref_ranks.values()) - min(ref_ranks.values())
    seed_lines = ["| Variant | " + " | ".join(f"paired gain @{k}" for k in seeds) + " | min |gain| / ref spread |",
                  "|---|" + "---:|" * (len(seeds) + 1)]
    for row in SCIENTIFIC[1:]:
        gains = []
        cells = []
        for k, s in seeds.items():
            if not passed(s, row):
                cells.append("FAILED")
                continue
            g = rank(vector(s, row, metrics), r, sd, metrics) - ref_ranks[k]
            gains.append(g)
            cells.append(fmt(g))
        ratio = (min(abs(g) for g in gains) / spread) if gains and spread > 0 else float("nan")
        summary["seed_check"][row] = {"paired_gains": gains, "min_abs_gain_over_ref_spread": ratio}
        seed_lines.append(f"| {row} | " + " | ".join(cells) + f" | {ratio:.2f} |")
    summary["seed_check"]["reference_rank_by_seed"] = ref_ranks
    summary["seed_check"]["reference_spread"] = spread
    table_seed = "\n".join(seed_lines)

    # Train vs test transfer.
    tr_lines = ["| Certifier | Train passed | Train main/curve/sweep | Test passed | Test main/curve/sweep |",
                "|---|---|---|---|---|"]
    if (RES / "train.json").exists():
        train = load(RES / "train.json")
        for row in train["_metadata"]["certifiers"]:
            def trio(s):
                return "/".join(f"{s[e][row]['type2_error']:.3f}" for e in
                                ("synthetic_power_comparison", "synthetic_type2_curve", "judge_quality_sweep"))
            te_ok = passed(hidden, row) if row in hidden["_metadata"]["certifiers"] else None
            te = trio(hidden) if row in hidden["_metadata"]["certifiers"] else "n/a"
            tr_lines.append(f"| {row} | {'yes' if passed(train, row) else '**FAILED**'} | {trio(train)} | "
                            f"{'yes' if te_ok else ('**FAILED**' if te_ok is False else 'n/a')} | {te} |")
    table_train = "\n".join(tr_lines)

    runs = load(RES / "runs.json") if (RES / "runs.json").exists() else {}
    md = ["## Hidden test, every audit certifier (hidden seed)", "", table_hidden, "",
          f"Reference spread across draws (rank units): {spread:.3f}; reference rank by draw: "
          + ", ".join(f"{k} {fmt(v)}" for k, v in ref_ranks.items()), "",
          "## Paired gains vs the reference on identical inputs", "", table_seed, "",
          "## Train vs test", "", table_train, "",
          "## Evaluator exit codes and no-argument runs", "", "```json",
          json.dumps(runs, indent=2), "```", "",
          f"Audit reference row equals saved scores_test.json reference: {sanity}",
          f"Cohort for normalization: {len(cohort)} accepted scientific runs over {len(seeds)} draws."]
    (RES / "summary.md").write_text("\n".join(md) + "\n")
    (RES / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()
