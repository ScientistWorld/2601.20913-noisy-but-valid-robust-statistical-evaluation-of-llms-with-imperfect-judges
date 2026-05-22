#!/usr/bin/env python3
"""Aggregate method artifacts into benchmark scores.

The evaluator intentionally does not import from ``method/`` and does not
generate synthetic trials. It reads trial-level outputs produced by a method
runner and computes the benchmark metrics.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def mean(values: list[int | float]) -> float:
    if not values:
        raise ValueError("cannot average an empty list")
    return float(sum(values) / len(values))


def load_artifact(path: Path) -> dict:
    artifact = json.loads(path.read_text())
    if artifact.get("schema") != "noisy_ht_synthetic_artifact_v1":
        raise ValueError(f"{path} is not a Noisy HT synthetic artifact")
    return artifact


def build_scores(artifact: dict) -> dict:
    main_rows = artifact["main"]["rows"]
    power_rows = [row for row in main_rows if row["experiment"] == "synthetic_power_comparison"]
    type1_rows = [row for row in main_rows if row["experiment"] == "synthetic_type1_control"]

    type2_direct = mean([row["direct_ht_type2_failure"] for row in power_rows])
    type2_noisy = mean([row["noisy_ht_type2_failure"] for row in power_rows])
    type2_oracle = mean([row["oracle_noisy_ht_type2_failure"] for row in power_rows])
    type1_direct = mean([row["direct_ht_type1_error"] for row in type1_rows])
    type1_noisy = mean([row["noisy_ht_type1_error"] for row in type1_rows])
    type1_oracle = mean([row["oracle_noisy_ht_type1_error"] for row in type1_rows])

    curve = {}
    for row in artifact["curve"]["rows"]:
        setting = row["setting"]
        curve.setdefault(setting, []).append(row["noisy_ht_type2_failure"])
    curve_scores = {
        setting: {"type2_error": round(mean(values), 4)}
        for setting, values in sorted(curve.items())
    }

    diagnostics = {}
    if "_diagnostics" in artifact:
        ppi_rows = artifact["_diagnostics"].get("rows", [])
        if ppi_rows:
            diagnostics["ppi_oracle_ordering_type2"] = {
                key: round(mean([row[key] for row in ppi_rows]), 4)
                for key in ["noisy_ht", "ppi", "ppi_pp", "ridge_ppi", "oracle_noisy_ht"]
            }

    gap = type2_noisy - type2_oracle
    scores = {
        "synthetic_power_comparison": {
            "direct_ht": {"type2_error": round(type2_direct, 4)},
            "noisy_ht": {"type2_error": round(type2_noisy, 4)},
            "oracle_noisy_ht": {"type2_error": round(type2_oracle, 4)},
        },
        "oracle_gap": {
            "oracle_noisy_ht": {
                "type2_error_noisy": round(type2_oracle, 4),
                "oracle_gap": 0.0,
            },
            "noisy_ht": {
                "type2_error_noisy": round(type2_noisy, 4),
                "oracle_gap": round(gap, 4),
            },
        },
        "synthetic_type2_curve": curve_scores,
        "synthetic_type1_control": {
            "direct_ht": {"type1_error": round(type1_direct, 4)},
            "noisy_ht": {"type1_error": round(type1_noisy, 4)},
            "oracle_noisy_ht": {"type1_error": round(type1_oracle, 4)},
        },
    }
    if diagnostics:
        scores["_diagnostics"] = diagnostics
    return scores


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", type=Path, default=Path("outputs/synthetic_results.json"))
    parser.add_argument("--output", type=Path, default=Path("scoring/scores.json"))
    args = parser.parse_args()

    scores = build_scores(load_artifact(args.artifact))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(scores, indent=2) + "\n")

    power = scores["synthetic_power_comparison"]
    type1 = scores["synthetic_type1_control"]
    print(f"Type-II: Direct={power['direct_ht']['type2_error']:.3f}, "
          f"Noisy={power['noisy_ht']['type2_error']:.3f}, "
          f"Oracle={power['oracle_noisy_ht']['type2_error']:.3f}")
    print(f"Type-I: Direct={type1['direct_ht']['type1_error']:.3f}, "
          f"Noisy={type1['noisy_ht']['type1_error']:.3f}, "
          f"Oracle={type1['oracle_noisy_ht']['type1_error']:.3f}")
    print(f"Scores written to {args.output}")


if __name__ == "__main__":
    main()
