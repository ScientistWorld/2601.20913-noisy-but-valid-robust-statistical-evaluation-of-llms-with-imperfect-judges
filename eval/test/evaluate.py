#!/usr/bin/env python3
"""Held-out (hidden) test for the judge-assisted certification benchmark.

Everything that defines the test lives in this file and is produced at test
time: the instances are generated here from a hidden seed, the ground truth
(true failure rate, true judge TPR/FPR, null/alternative status) never leaves
this process, and the comparison rows (small-label-only test, known-judge
reference test) are computed here, not by the method.

Each certifier found under ``method/certifiers/<name>.py`` is executed through
the fixed file interface (see ``briefing/evaluation.md``) and scored from its
raw 0/1 decisions only.  A certifier that crashes, returns malformed output,
makes batch-dependent decisions, or violates the Type-I validity limit in any
judge regime is scored as failed (every scored metric at its worst value) and
the script exits non-zero.

This file shares no code with ``eval/train/`` and does not import ``method/``.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from statistics import NormalDist
from typing import Any

import numpy as np

SLICE = "test"
WORKSPACE = Path(__file__).resolve().parents[2]
DEFAULT_CERTIFIER_DIR = WORKSPACE / "method" / "certifiers"
DEFAULT_OUTPUT = WORKSPACE / "scoring" / "scores_test.json"

# ── Fixed benchmark contract (same on train and test) ────────────────────────
N_M = 100          # human-labelled calibration items per instance
N_J = 10_000       # judge-only items per instance
ALPHA = 0.25       # certification threshold: H0 R_M >= ALPHA vs H1 R_M < ALPHA
ZETA = 0.05        # required significance level
Z_ZETA = NormalDist().inv_cdf(ZETA)

POWER_CELL = ("hq", 0.20)
CURVE_CELLS = [("hq", 0.01), ("hq", 0.15), ("hq", 0.175), ("hq", 0.225)]
SWEEP_CELLS = [(r, rm) for r in ("weak_tpr", "high_fpr") for rm in (0.05, 0.15, 0.20)]

N_POWER = 2000      # instances in the main power cell
N_ALT = 1000        # instances in every other alternative cell
N_NULL = 3000       # instances at the null boundary R_M = ALPHA, per regime
N_INTERIOR = 1000   # instances strictly inside the null, per regime

# ── Hidden test-only parameters ──────────────────────────────────────────────
SEED = 7_301_955_118
# Judge-quality regimes (centres). They sit near, not on, the public train
# centres: TPR and FPR are both shifted by +0.02, which keeps TPR - FPR (the
# main difficulty driver) unchanged but moves the null-boundary judge flag
# rate, so judge values or ranges assumed from the train slice do not hold.
REGIMES = {
    "hq": (0.97, 0.07),        # informative judge
    "weak_tpr": (0.77, 0.07),  # judge misses many failures
    "high_fpr": (0.97, 0.27),  # judge raises many false alarms
}
JITTER = 0.03                  # half-width of per-instance TPR/FPR jitter
INTERIOR_RM = (0.26, 0.40)     # null-interior failure rates ~ Uniform(range)

# Validity gate, per judge regime: the measured false-certification rate at
# the null boundary and inside the null must not exceed ZETA + VALIDITY_TOL.
# The tolerance admits the finite-sample slack of normal-approximation tests
# (the guarantee is ZETA + O(n^-1/2)); gross violations fail the run.
VALIDITY_TOL = 0.015
DEFAULT_TIMEOUT = 1800         # seconds per certifier invocation
CHECK_FRACTION = 0.25          # share of instances re-run in a reshuffled batch
BASELINES = ("direct_ht", "oracle_noisy_ht")
CHUNK = 1000


def rm_label(x: float) -> str:
    s = f"{x:.3f}".rstrip("0")
    if len(s.split(".")[1]) < 2:
        s += "0"
    return s


def cell_name(regime: str, kind: str) -> str:
    return f"{regime}__{kind}"


def cell_table() -> list[dict[str, Any]]:
    cells: list[dict[str, Any]] = []
    for regime, rm in [POWER_CELL] + CURVE_CELLS + SWEEP_CELLS:
        n = N_POWER if (regime, rm) == POWER_CELL else N_ALT
        cells.append({"name": cell_name(regime, f"rm_{rm_label(rm)}"),
                      "regime": regime, "role": "alt", "rm": rm, "n": n})
    for regime in REGIMES:
        cells.append({"name": cell_name(regime, "null"), "regime": regime,
                      "role": "null", "rm": ALPHA, "n": N_NULL})
        cells.append({"name": cell_name(regime, "interior"), "regime": regime,
                      "role": "interior", "rm": None, "n": N_INTERIOR})
    return cells


def generate(seed: int) -> dict[str, Any]:
    """Generate the shuffled instance batch and keep its ground truth."""
    cells = cell_table()
    rng = np.random.default_rng(seed)
    cell_of = np.concatenate([np.full(c["n"], k) for k, c in enumerate(cells)])
    cell_of = cell_of[rng.permutation(cell_of.size)]
    n = cell_of.size

    tpr_c = np.array([REGIMES[c["regime"]][0] for c in cells])[cell_of]
    fpr_c = np.array([REGIMES[c["regime"]][1] for c in cells])[cell_of]
    tpr = np.clip(tpr_c + rng.uniform(-JITTER, JITTER, n), 0.001, 0.999)
    fpr = np.clip(fpr_c + rng.uniform(-JITTER, JITTER, n), 0.001, 0.999)

    rm = np.array([np.nan if c["rm"] is None else c["rm"] for c in cells])[cell_of]
    interior = np.isnan(rm)
    rm[interior] = rng.uniform(INTERIOR_RM[0], INTERIOR_RM[1], int(interior.sum()))
    rj = fpr + (tpr - fpr) * rm

    calib_human = np.empty((n, N_M), dtype=np.uint8)
    calib_judge = np.empty((n, N_M), dtype=np.uint8)
    eval_judge = np.empty((n, N_J), dtype=np.uint8)
    for i0 in range(0, n, CHUNK):
        sl = slice(i0, min(n, i0 + CHUNK))
        m = sl.stop - sl.start
        human = rng.random((m, N_M)) < rm[sl, None]
        p_flag = np.where(human, tpr[sl, None], fpr[sl, None])
        calib_human[sl] = human
        calib_judge[sl] = rng.random((m, N_M)) < p_flag
        eval_judge[sl] = rng.random((m, N_J)) < rj[sl, None]

    return {"cells": cells, "cell_of": cell_of, "tpr": tpr, "fpr": fpr, "rm": rm,
            "calib_human": calib_human, "calib_judge": calib_judge,
            "eval_judge": eval_judge}


def baseline_decisions(inst: dict[str, Any]) -> tuple[dict[str, np.ndarray], dict[str, np.ndarray]]:
    """Comparison rows fixed by the evaluator, plus unscored diagnostics."""
    h = inst["calib_human"].astype(np.float64)
    j = inst["calib_judge"].astype(np.float64)
    r_m = h.mean(axis=1)
    r_j = inst["eval_judge"].sum(axis=1, dtype=np.int64) / N_J

    direct = r_m <= ALPHA + Z_ZETA * math.sqrt(ALPHA * (1 - ALPHA) / N_M)

    a_true = inst["fpr"] + (inst["tpr"] - inst["fpr"]) * ALPHA
    oracle = r_j < a_true + Z_ZETA * np.sqrt(a_true * (1 - a_true) / N_J)

    r_jp = j.mean(axis=1)
    r_11 = (h * j).mean(axis=1)
    big_a = r_j * (1 - r_j) / N_J + r_jp * (1 - r_jp) / N_M
    big_b = (r_11 - r_m * r_jp) / N_M

    def ppi(lam: np.ndarray) -> np.ndarray:
        est = r_m + lam * (r_j - r_jp)
        var = np.maximum(r_m * (1 - r_m) / N_M + lam ** 2 * big_a - 2 * lam * big_b, 0.0)
        return est < ALPHA + Z_ZETA * np.sqrt(var)

    lam_pp = np.divide(big_b, big_a, out=np.zeros_like(big_a), where=big_a > 0)
    diagnostics = {"ppi": ppi(np.ones_like(r_m)), "ppi_pp": ppi(lam_pp)}
    return {"direct_ht": direct, "oracle_noisy_ht": oracle}, diagnostics


def write_batch(directory: Path, inst: dict[str, Any], idx: np.ndarray | None) -> None:
    """Write the method-visible inputs only (no ground truth) for rows ``idx``."""
    directory.mkdir(parents=True)
    count = inst["cell_of"].size if idx is None else idx.size
    for key in ("calib_human", "calib_judge", "eval_judge"):
        arr = inst[key] if idx is None else np.ascontiguousarray(inst[key][idx])
        np.save(directory / f"{key}.npy", arr)
    np.save(directory / "alpha.npy", np.full(count, ALPHA))
    np.save(directory / "zeta.npy", np.full(count, ZETA))
    (directory / "meta.json").write_text(json.dumps(
        {"n_instances": int(count), "n_m": N_M, "n_j": N_J}) + "\n")
    for path in directory.iterdir():
        path.chmod(0o444)


def parse_decisions(payload: Any, n: int) -> tuple[np.ndarray | None, str | None]:
    if not isinstance(payload, dict) or "certify" not in payload:
        return None, "output must be a JSON object with key 'certify'"
    values = payload["certify"]
    if not isinstance(values, list) or len(values) != n:
        got = len(values) if isinstance(values, list) else type(values).__name__
        return None, f"expected a list of {n} decisions, got {got}"
    out = np.zeros(n, dtype=bool)
    for i, v in enumerate(values):
        if isinstance(v, bool) or (isinstance(v, int) and v in (0, 1)):
            out[i] = bool(v)
        else:
            return None, f"decision {i} is {v!r}; every decision must be 0/1 or true/false"
    return out, None


def run_certifier(path: Path, batch: Path, out: Path, n: int,
                  timeout: int) -> tuple[np.ndarray | None, str | None, float]:
    if out.exists():
        out.unlink()
    cmd = [sys.executable, str(path), "--input", str(batch), "--output", str(out)]
    start = time.time()
    try:
        proc = subprocess.run(cmd, cwd=str(WORKSPACE), timeout=timeout,
                              capture_output=True, text=True)
    except subprocess.TimeoutExpired:
        return None, f"timed out after {timeout}s", time.time() - start
    elapsed = time.time() - start
    if proc.returncode != 0:
        tail = (proc.stderr or proc.stdout or "")[-1500:]
        return None, f"exit code {proc.returncode}: {tail}", elapsed
    try:
        payload = json.loads(out.read_text())
    except Exception as exc:  # noqa: BLE001 - any unreadable output is a failure
        return None, f"unreadable output: {exc}", elapsed
    decisions, err = parse_decisions(payload, n)
    return decisions, err, elapsed


def cell_rates(decisions: np.ndarray, inst: dict[str, Any]) -> dict[str, float]:
    """Error rate per cell: Type-II for alternatives, false certification for nulls."""
    rates = {}
    for k, cell in enumerate(inst["cells"]):
        cert = float(decisions[inst["cell_of"] == k].mean())
        rates[cell["name"]] = 1.0 - cert if cell["role"] == "alt" else cert
    return rates


def alt_names(cells: list[tuple[str, float]]) -> list[str]:
    return [cell_name(r, f"rm_{rm_label(rm)}") for r, rm in cells]


def summarize(rates: dict[str, float]) -> dict[str, float]:
    power = rates[alt_names([POWER_CELL])[0]]
    curve = float(np.mean([rates[c] for c in alt_names(CURVE_CELLS)]))
    sweep = float(np.mean([rates[c] for c in alt_names(SWEEP_CELLS)]))
    grid = float(np.mean([rates[c] for c in alt_names([POWER_CELL] + CURVE_CELLS + SWEEP_CELLS)]))
    return {
        "power": power, "curve": curve, "sweep": sweep, "grid": grid,
        "type1_hq": rates[cell_name("hq", "null")],
        "type1_worst": max(rates[cell_name(r, "null")] for r in REGIMES),
        "interior_worst": max(rates[cell_name(r, "interior")] for r in REGIMES),
    }


WORST = {"power": 1.0, "curve": 1.0, "sweep": 1.0, "grid": 1.0,
         "type1_hq": 1.0, "type1_worst": 1.0, "interior_worst": 1.0}


def gate_limit(n: int) -> float:
    del n  # fixed limit; instance counts are reported for context only
    return ZETA + VALIDITY_TOL


def validity_reasons(rates: dict[str, float]) -> list[str]:
    reasons = []
    for regime in REGIMES:
        t1 = rates[cell_name(regime, "null")]
        if t1 > gate_limit(N_NULL):
            reasons.append(f"Type-I error {t1:.4f} at the null boundary in regime "
                           f"'{regime}' exceeds the limit {gate_limit(N_NULL):.4f}")
        fc = rates[cell_name(regime, "interior")]
        if fc > gate_limit(N_INTERIOR):
            reasons.append(f"false-certification rate {fc:.4f} inside the null in regime "
                           f"'{regime}' exceeds the limit {gate_limit(N_INTERIOR):.4f}")
    return reasons


def r4(x: float) -> float:
    return round(float(x), 4)


def build_scores(summaries: dict[str, dict[str, float]], meta: dict[str, Any]) -> dict[str, Any]:
    oracle_grid = summaries["oracle_noisy_ht"]["grid"]
    scores: dict[str, Any] = {"_metadata": meta}
    scores["synthetic_power_comparison"] = {m: {"type2_error": r4(s["power"])} for m, s in summaries.items()}
    scores["synthetic_type2_curve"] = {m: {"type2_error": r4(s["curve"])} for m, s in summaries.items()}
    scores["judge_quality_sweep"] = {m: {"type2_error": r4(s["sweep"])} for m, s in summaries.items()}
    scores["oracle_gap"] = {
        m: {"oracle_gap": r4(s["grid"] - oracle_grid) if m != "oracle_noisy_ht" else 0.0,
            "mean_type2_error": r4(s["grid"])}
        for m, s in summaries.items()
    }
    scores["synthetic_type1_control"] = {
        m: {"type1_error": r4(s["type1_hq"]),
            "type1_error_worst_regime": r4(s["type1_worst"]),
            "false_cert_interior": r4(s["interior_worst"])}
        for m, s in summaries.items()
    }
    return scores


def discover(certifier_dir: Path) -> list[Path]:
    if not certifier_dir.is_dir():
        return []
    return sorted(p for p in certifier_dir.glob("*.py")
                  if not p.name.startswith("_") and p.is_file())


def main() -> None:
    parser = argparse.ArgumentParser(description="Hidden test: score every certifier on disk.")
    parser.add_argument("--certifier-dir", type=Path, default=DEFAULT_CERTIFIER_DIR)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--workdir", type=Path, default=None)
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT)
    parser.add_argument("--audit-seed", type=int, default=None,
                        help="audit only: replace the hidden seed (never used for ranking)")
    args = parser.parse_args()

    seed = SEED if args.audit_seed is None else args.audit_seed
    t0 = time.time()
    inst = generate(seed)
    n = inst["cell_of"].size
    print(f"[{SLICE}] generated {n} held-out instances in {time.time() - t0:.1f}s")

    baselines, diagnostics = baseline_decisions(inst)
    rates = {m: cell_rates(d, inst) for m, d in baselines.items()}
    diag_rates = {m: cell_rates(d, inst) for m, d in diagnostics.items()}

    certifiers = discover(args.certifier_dir)
    work = Path(tempfile.mkdtemp(prefix="cert_eval_", dir=args.workdir))
    validity: dict[str, Any] = {}
    failed: list[str] = []
    try:
        check_rng = np.random.default_rng([seed, 1])
        subset = check_rng.permutation(n)[: int(n * CHECK_FRACTION)]
        if certifiers:
            write_batch(work / "batch_full", inst, None)
            write_batch(work / "batch_check", inst, subset)
        for path in certifiers:
            name = path.stem
            reasons: list[str] = []
            info: dict[str, Any] = {}
            if not re.fullmatch(r"[A-Za-z0-9_]+", name) or name in BASELINES:
                # Never let a certifier file shadow an evaluator comparison row.
                name = "invalid_name_" + re.sub(r"[^A-Za-z0-9_]", "_", name)
                reasons.append("certifier name must be [A-Za-z0-9_]+ and differ from the "
                               f"evaluator's comparison rows {list(BASELINES)}")
            else:
                dec, err, sec = run_certifier(path, work / "batch_full",
                                              work / f"{name}_full.json", n, args.timeout)
                print(f"[{SLICE}] {name}: main run {sec:.1f}s")
                if err:
                    reasons.append(f"main run: {err}")
                else:
                    dec_b, err_b, sec_b = run_certifier(
                        path, work / "batch_check", work / f"{name}_check.json",
                        subset.size, args.timeout)
                    print(f"[{SLICE}] {name}: consistency run {sec_b:.1f}s")
                    if err_b:
                        reasons.append(f"consistency run: {err_b}")
                    else:
                        mismatch = int((dec[subset] != dec_b).sum())
                        info["consistency_mismatches"] = mismatch
                        if mismatch:
                            reasons.append(
                                f"{mismatch} of {subset.size} decisions changed when the same "
                                "instances were re-submitted in a different batch; decisions "
                                "must depend only on each instance's own data")
                    cert_rates = cell_rates(dec, inst)
                    info["cell_error_rates"] = {k: r4(v) for k, v in cert_rates.items()}
                    reasons.extend(validity_reasons(cert_rates))
                    rates[name] = cert_rates
            info["passed"] = not reasons
            info["reasons"] = reasons
            validity[name] = info
            if reasons:
                failed.append(name)
                print(f"[{SLICE}] FAILED {name}: " + " | ".join(r[:300] for r in reasons))
            else:
                print(f"[{SLICE}] passed {name}")
    finally:
        shutil.rmtree(work, ignore_errors=True)

    summaries = {m: summarize(r) for m, r in rates.items()}
    for name in failed:
        summaries[name] = dict(WORST)

    meta = {
        "schema": "certifier_scores_v2",
        "slice": SLICE,
        "n_instances": int(n),
        "certifiers": [p.stem for p in certifiers],
        "failed_certifiers": failed,
        "validity_limits": {"null_boundary": r4(gate_limit(N_NULL)),
                            "null_interior": r4(gate_limit(N_INTERIOR))},
    }
    if args.audit_seed is not None:
        meta["audit_seed"] = int(args.audit_seed)
    scores = build_scores(summaries, meta)
    scores["_validity"] = validity
    scores["_cells"] = {m: {k: r4(v) for k, v in r.items()} for m, r in rates.items()}
    scores["_diagnostics"] = {m: {k: r4(v) for k, v in r.items()} for m, r in diag_rates.items()}

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(scores, indent=2) + "\n")

    print(f"[{SLICE}] {'row':<28}{'power':>8}{'curve':>8}{'sweep':>8}{'gap':>8}{'T1(hq)':>8}{'T1max':>8}")
    for m in summaries:
        s = summaries[m]
        print(f"[{SLICE}] {m:<28}{s['power']:>8.3f}{s['curve']:>8.3f}{s['sweep']:>8.3f}"
              f"{s['grid'] - summaries['oracle_noisy_ht']['grid']:>8.3f}"
              f"{s['type1_hq']:>8.3f}{s['type1_worst']:>8.3f}")
    print(f"[{SLICE}] scores written to {args.output} ({time.time() - t0:.1f}s)")

    if not certifiers:
        print(f"[{SLICE}] no certifier found under {args.certifier_dir}")
        sys.exit(1)
    if failed:
        print(f"[{SLICE}] run FAILED for: {', '.join(failed)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
