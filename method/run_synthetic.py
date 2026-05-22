#!/usr/bin/env python3
"""Run the paper's hypothesis-testing methods on the synthetic benchmark."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from data.synthetic import generate_synthetic_data
from method.core import (
    direct_hypothesis_test,
    noisy_hypothesis_test_dual,
    oracle_noisy_hypothesis_test,
    ppi_family_wald_test,
)


def bool_result(value: bool) -> int:
    return int(bool(value))


def run_main_trials(n_trials: int, seed: int) -> dict:
    n_m = 100
    n_j = 10000
    alpha = 0.25
    zeta = 0.05
    tpr = 0.9
    fpr = 0.1
    r_m_test = 0.20

    rows = []
    for trial in range(n_trials):
        d_m_sm, d_m_sj, _, d_j_sj = generate_synthetic_data(
            n_m, n_j, r_m_test, tpr, fpr, seed + trial * 2
        )
        direct_reject, _ = direct_hypothesis_test(d_m_sm, alpha, zeta)
        noisy_reject, _ = noisy_hypothesis_test_dual(d_m_sm, d_m_sj, d_j_sj, alpha, zeta)
        oracle_reject, _ = oracle_noisy_hypothesis_test(d_j_sj, tpr, fpr, alpha, zeta)

        rows.append(
            {
                "experiment": "synthetic_power_comparison",
                "trial": trial,
                "direct_ht_type2_failure": bool_result(not direct_reject),
                "noisy_ht_type2_failure": bool_result(not noisy_reject),
                "oracle_noisy_ht_type2_failure": bool_result(not oracle_reject),
            }
        )

        d_m_sm, d_m_sj, _, d_j_sj = generate_synthetic_data(
            n_m, n_j, alpha, tpr, fpr, seed + trial * 2 + 1
        )
        direct_reject, _ = direct_hypothesis_test(d_m_sm, alpha, zeta)
        noisy_reject, _ = noisy_hypothesis_test_dual(d_m_sm, d_m_sj, d_j_sj, alpha, zeta)
        oracle_reject, _ = oracle_noisy_hypothesis_test(d_j_sj, tpr, fpr, alpha, zeta)

        rows.append(
            {
                "experiment": "synthetic_type1_control",
                "trial": trial,
                "direct_ht_type1_error": bool_result(direct_reject),
                "noisy_ht_type1_error": bool_result(noisy_reject),
                "oracle_noisy_ht_type1_error": bool_result(oracle_reject),
            }
        )

    return {
        "config": {
            "n_trials": n_trials,
            "seed": seed,
            "n_m": n_m,
            "n_j": n_j,
            "alpha": alpha,
            "zeta": zeta,
            "tpr": tpr,
            "fpr": fpr,
            "r_m_test": r_m_test,
        },
        "rows": rows,
    }


def run_curve_trials(n_trials: int, seed: int) -> dict:
    n_m = 100
    n_j = 10000
    alpha = 0.25
    zeta = 0.05
    tpr = 0.9
    fpr = 0.1
    rows = []

    for r_m in [0.01, 0.10, 0.20, 0.30]:
        for trial in range(n_trials):
            d_m_sm, d_m_sj, _, d_j_sj = generate_synthetic_data(
                n_m, n_j, r_m, tpr, fpr, seed + trial * 3 + int(r_m * 100) + 10000
            )
            noisy_reject, _ = noisy_hypothesis_test_dual(d_m_sm, d_m_sj, d_j_sj, alpha, zeta)
            rows.append(
                {
                    "experiment": "synthetic_type2_curve",
                    "setting": f"rm_{r_m:.2f}",
                    "trial": trial,
                    "noisy_ht_type2_failure": bool_result(not noisy_reject),
                }
            )

    return {
        "config": {
            "n_trials": n_trials,
            "seed": seed,
            "n_m": n_m,
            "n_j": n_j,
            "alpha": alpha,
            "zeta": zeta,
            "tpr": tpr,
            "fpr": fpr,
        },
        "rows": rows,
    }


def run_diagnostics(n_trials: int, seed: int) -> dict:
    n_m = 100
    n_j = 10000
    alpha = 0.25
    zeta = 0.05
    r_m_test = 0.20
    tpr = 0.9
    fpr = 0.1
    ppi_rows = []

    for trial in range(n_trials):
        d_m_sm, d_m_sj, _, d_j_sj = generate_synthetic_data(
            n_m, n_j, r_m_test, tpr, fpr, seed + 200000 + trial
        )
        noisy_reject, _ = noisy_hypothesis_test_dual(d_m_sm, d_m_sj, d_j_sj, alpha, zeta)
        oracle_reject, _ = oracle_noisy_hypothesis_test(d_j_sj, tpr, fpr, alpha, zeta)
        row = {
            "experiment": "ppi_oracle_ordering_type2",
            "trial": trial,
            "noisy_ht": bool_result(not noisy_reject),
            "oracle_noisy_ht": bool_result(not oracle_reject),
        }
        for variant in ["ppi", "ppi_pp", "ridge_ppi"]:
            reject, _ = ppi_family_wald_test(
                d_m_sm,
                d_m_sj,
                d_j_sj,
                tpr,
                fpr,
                alpha,
                zeta,
                variant=variant,
                tau=1e-4 if variant == "ridge_ppi" else 0.0,
            )
            row[variant] = bool_result(not reject)
        ppi_rows.append(row)

    return {"rows": ppi_rows}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--n-trials", type=int, default=1000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--seed-offset", type=int, default=0)
    parser.add_argument("--output", type=Path, default=Path("outputs/synthetic_results.json"))
    args = parser.parse_args()

    seed = args.seed + args.seed_offset
    artifact = {
        "schema": "noisy_ht_synthetic_artifact_v1",
        "main": run_main_trials(args.n_trials, seed),
        "curve": run_curve_trials(args.n_trials, seed),
        "_diagnostics": run_diagnostics(args.n_trials, seed),
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(artifact, indent=2) + "\n")
    print(f"Wrote method artifact to {args.output}")


if __name__ == "__main__":
    main()
