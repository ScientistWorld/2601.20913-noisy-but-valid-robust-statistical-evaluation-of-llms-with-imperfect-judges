#!/usr/bin/env python3
"""Standalone evaluation for the Noisy HT reproduction.

This file intentionally does not import from ``method/``.  It implements the
paper's public benchmark procedures directly so future methods can be scored
through the same script without depending on this reproduction's method module.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import numpy as np
from scipy.stats import norm

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from data.synthetic import generate_synthetic_data


def estimate_tpr_fpr(s_m: np.ndarray, s_j: np.ndarray):
    n_m1 = int(np.sum(s_m == 1))
    n_m0 = int(np.sum(s_m == 0))
    tpr_hat = float(np.sum((s_j == 1) & (s_m == 1)) / n_m1) if n_m1 else 0.0
    fpr_hat = float(np.sum((s_j == 1) & (s_m == 0)) / n_m0) if n_m0 else 0.0
    return tpr_hat, fpr_hat, n_m1, n_m0


def direct_hypothesis_test(s_m: np.ndarray, alpha: float, zeta: float) -> bool:
    c_m = alpha + norm.ppf(zeta) * np.sqrt(alpha * (1.0 - alpha) / len(s_m))
    return bool(np.mean(s_m) < c_m)


def noisy_hypothesis_test(d_m_sm: np.ndarray, d_m_sj: np.ndarray, d_j_sj: np.ndarray, alpha: float, zeta: float) -> bool:
    tpr_hat, fpr_hat, n_m1, n_m0 = estimate_tpr_fpr(d_m_sm, d_m_sj)
    alpha_prime_hat = fpr_hat + (tpr_hat - fpr_hat) * alpha
    var = alpha_prime_hat * (1.0 - alpha_prime_hat) / len(d_j_sj)
    if n_m1:
        var += alpha**2 * tpr_hat * (1.0 - tpr_hat) / n_m1
    if n_m0:
        var += (1.0 - alpha) ** 2 * fpr_hat * (1.0 - fpr_hat) / n_m0
    c_j_prime = alpha_prime_hat + norm.ppf(zeta) * np.sqrt(var)
    return bool(np.mean(d_j_sj) < c_j_prime)


def oracle_noisy_hypothesis_test(d_j_sj: np.ndarray, tpr: float, fpr: float, alpha: float, zeta: float) -> bool:
    alpha_prime = fpr + (tpr - fpr) * alpha
    c_j = alpha_prime + norm.ppf(zeta) * np.sqrt(alpha_prime * (1.0 - alpha_prime) / len(d_j_sj))
    return bool(np.mean(d_j_sj) < c_j)


def estimate_main_errors(n_trials: int, seed: int):
    n_m = 100
    n_j = 10000
    alpha = 0.25
    zeta = 0.05
    tpr = 0.9
    fpr = 0.1
    r_m_test = 0.20

    counts = {
        "type2_direct": 0,
        "type2_noisy": 0,
        "type2_oracle": 0,
        "type1_direct": 0,
        "type1_noisy": 0,
        "type1_oracle": 0,
    }

    for trial in range(n_trials):
        d_m_sm, d_m_sj, _, d_j_sj = generate_synthetic_data(
            n_m, n_j, r_m_test, tpr, fpr, seed + trial * 2
        )
        counts["type2_direct"] += int(not direct_hypothesis_test(d_m_sm, alpha, zeta))
        counts["type2_noisy"] += int(not noisy_hypothesis_test(d_m_sm, d_m_sj, d_j_sj, alpha, zeta))
        counts["type2_oracle"] += int(not oracle_noisy_hypothesis_test(d_j_sj, tpr, fpr, alpha, zeta))

        d_m_sm, d_m_sj, _, d_j_sj = generate_synthetic_data(
            n_m, n_j, alpha, tpr, fpr, seed + trial * 2 + 1
        )
        counts["type1_direct"] += int(direct_hypothesis_test(d_m_sm, alpha, zeta))
        counts["type1_noisy"] += int(noisy_hypothesis_test(d_m_sm, d_m_sj, d_j_sj, alpha, zeta))
        counts["type1_oracle"] += int(oracle_noisy_hypothesis_test(d_j_sj, tpr, fpr, alpha, zeta))

    return {k: v / n_trials for k, v in counts.items()}


def estimate_noisy_curve(n_trials: int, seed: int):
    n_m = 100
    n_j = 10000
    alpha = 0.25
    zeta = 0.05
    tpr = 0.9
    fpr = 0.1
    curve = {}
    for r_m in [0.01, 0.10, 0.20, 0.30]:
        failures = 0
        for trial in range(n_trials):
            d_m_sm, d_m_sj, _, d_j_sj = generate_synthetic_data(
                n_m, n_j, r_m, tpr, fpr, seed + trial * 3 + int(r_m * 100) + 10000
            )
            failures += int(not noisy_hypothesis_test(d_m_sm, d_m_sj, d_j_sj, alpha, zeta))
        curve[f"rm_{r_m:.2f}"] = {"type2_error": round(failures / n_trials, 4)}
    return curve


def build_scores(n_trials: int, seed: int):
    main = estimate_main_errors(n_trials, seed)
    curve = estimate_noisy_curve(n_trials, seed)
    gap = main["type2_noisy"] - main["type2_oracle"]
    return {
        "synthetic_power_comparison": {
            "direct_ht": {"type2_error": round(main["type2_direct"], 4)},
            "noisy_ht": {"type2_error": round(main["type2_noisy"], 4)},
            "oracle_noisy_ht": {"type2_error": round(main["type2_oracle"], 4)},
        },
        "oracle_gap": {
            "oracle_noisy_ht": {
                "type2_error_oracle": round(main["type2_oracle"], 4),
                "oracle_gap": round(gap, 4),
            },
            "noisy_ht": {
                "type2_error_noisy": round(main["type2_noisy"], 4),
                "oracle_gap": round(gap, 4),
            },
        },
        "synthetic_type2_curve": curve,
        "synthetic_type1_control": {
            "direct_ht": {"type1_error": round(main["type1_direct"], 4)},
            "noisy_ht": {"type1_error": round(main["type1_noisy"], 4)},
            "oracle_noisy_ht": {"type1_error": round(main["type1_oracle"], 4)},
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--n-trials", type=int, default=1000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output", type=Path, default=Path("scoring/scores.json"))
    args = parser.parse_args()

    scores = build_scores(args.n_trials, args.seed)
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
