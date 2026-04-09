#!/usr/bin/env python3
"""
Generate scores.json in the format expected by the scoring system.
This runs targeted experiments to match the reference.json structure.
"""
import sys
sys.path.insert(0, '/home/user/method')
sys.path.insert(0, '/home/user/eval')

import numpy as np
import json
from evaluate import estimate_error_rates_mc

def run_experiment():
    """Run experiments matching paper's reported results."""

    # Parameters from paper Figure 1
    n_m = 100
    n_j = 10000
    alpha = 0.25
    zeta = 0.05
    n_trials = 1000  # Reduced for speed

    results = {
        "experiments": {}
    }

    print("=== Running Synthetic Experiments ===\n")

    # Experiment 1: synthetic_power_comparison
    # Type-II error at R_M=0.20, TPR=0.9, FPR=0.1
    print("[1/5] synthetic_power_comparison (R_M=0.20, TPR=0.9, FPR=0.1)...")
    error_rates = estimate_error_rates_mc(
        n_m=n_m, n_j=n_j, r_m=0.20, tpr=0.9, fpr=0.1,
        alpha=alpha, zeta=zeta, n_trials=n_trials, seed=42
    )
    results["experiments"]["synthetic_power_comparison"] = {
        "description": "Synthetic: Type-II error at R_M=0.20, alpha=0.25, zeta=0.05, n_M=100, n_J=10000, TPR=0.9, FPR=0.1. Central claim: Noisy HT should have lower Type-II error than Direct HT when judge is reliable.",
        "weight": 0.35,
        "primary_metric": "type2_error",
        "metrics": {"type2_error": {"higher_is_better": False, "coefficient": -1.0}},
        "results": {
            "direct_ht": {"type": "baseline", "type2_error": round(error_rates["type2"]["direct_ht"], 4)},
            "noisy_ht": {"type": "proposed", "type2_error": round(error_rates["type2"]["noisy_ht"], 4)},
            "oracle_noisy_ht": {"type": "proposed", "type2_error": round(error_rates["type2"]["oracle_noisy_ht"], 4)}
        }
    }
    print(f"  Direct HT Type-II: {error_rates['type2']['direct_ht']:.4f}")
    print(f"  Noisy HT Type-II: {error_rates['type2']['noisy_ht']:.4f}")
    print(f"  Oracle HT Type-II: {error_rates['type2']['oracle_noisy_ht']:.4f}\n")

    # Experiment 2: synthetic_judge_quality_impact
    print("[2/5] synthetic_judge_quality_impact (R_M=0.20)...")
    judge_qualities = [
        (0.9, 0.1, 'high'),
        (0.8, 0.1, 'good'),
        (0.7, 0.2, 'moderate'),
    ]
    quality_results = {}
    for tpr, fpr, quality in judge_qualities:
        err = estimate_error_rates_mc(
            n_m=n_m, n_j=n_j, r_m=0.20, tpr=tpr, fpr=fpr,
            alpha=alpha, zeta=zeta, n_trials=n_trials, seed=42
        )
        quality_results[f"noisy_ht_{quality}"] = {
            "type": "proposed",
            "description": f"TPR={tpr}, FPR={fpr}",
            "type2_error": round(err["type2"]["noisy_ht"], 4)
        }
    results["experiments"]["synthetic_judge_quality_impact"] = {
        "description": "Synthetic: Type-II error vs judge quality at R_M=0.20, alpha=0.25. Higher TPR and lower FPR reduce Type-II error for Noisy HT. Paper: Figure 1A/B/C",
        "weight": 0.15,
        "primary_metric": "type2_error",
        "metrics": {"type2_error": {"higher_is_better": False, "coefficient": -1.0}},
        "results": quality_results
    }
    for name, r in quality_results.items():
        print(f"  {name}: {r['type2_error']:.4f}")
    print()

    # Experiment 3: oracle_gap
    print("[3/5] oracle_gap...")
    err_high = estimate_error_rates_mc(
        n_m=n_m, n_j=n_j, r_m=0.20, tpr=0.9, fpr=0.1,
        alpha=alpha, zeta=zeta, n_trials=n_trials, seed=42
    )
    noisy_type2 = err_high["type2"]["noisy_ht"]
    oracle_type2 = err_high["type2"]["oracle_noisy_ht"]
    oracle_gap = noisy_type2 - oracle_type2
    results["experiments"]["oracle_gap"] = {
        "description": "Synthetic: Oracle Gap — Type-II error difference between Oracle (known TPR/FPR) and Noisy HT (estimated TPR/FPR from n_M=100). Shows cost of estimation. Paper: Figure 1, Oracle Gap annotation",
        "weight": 0.15,
        "primary_metric": "oracle_gap",
        "metrics": {
            "oracle_gap": {"higher_is_better": False, "coefficient": -1.0},
            "type2_error_noisy": {"higher_is_better": False, "coefficient": -1.0},
            "type2_error_oracle": {"higher_is_better": False, "coefficient": -1.0}
        },
        "results": {
            "oracle_noisy_ht": {"type": "proposed", "description": "TPR/FPR known", "type2_error_oracle": round(oracle_type2, 4)},
            "noisy_ht": {"type": "proposed", "description": "TPR/FPR estimated from n_M=100", "type2_error_noisy": round(noisy_type2, 4), "oracle_gap": round(oracle_gap, 4)}
        }
    }
    print(f"  Noisy HT Type-II: {noisy_type2:.4f}")
    print(f"  Oracle HT Type-II: {oracle_type2:.4f}")
    print(f"  Oracle Gap: {oracle_gap:.4f}\n")

    # Experiment 4: synthetic_type2_curve
    print("[4/5] synthetic_type2_curve (R_M sweep)...")
    r_m_sweep = [0.01, 0.10, 0.20, 0.30]
    curve_results = {}
    for r_m in r_m_sweep:
        err = estimate_error_rates_mc(
            n_m=n_m, n_j=n_j, r_m=r_m, tpr=0.9, fpr=0.1,
            alpha=alpha, zeta=zeta, n_trials=n_trials, seed=42
        )
        curve_results[f"rm_{r_m:.2f}"] = {
            "r_m": r_m,
            "direct_ht": round(err["type2"]["direct_ht"], 4),
            "noisy_ht": round(err["type2"]["noisy_ht"], 4),
            "oracle_noisy_ht": round(err["type2"]["oracle_noisy_ht"], 4)
        }
    results["experiments"]["synthetic_type2_curve"] = {
        "description": "Synthetic: Type-II error vs model failure rate R_M. Shows that Noisy HT power advantage varies with R_M. For R_M < alpha (H1 region), Noisy HT can outperform Direct HT when judge is good. Paper: Figure 1A (left region)",
        "weight": 0.20,
        "primary_metric": "type2_error",
        "metrics": {"type2_error": {"higher_is_better": False, "coefficient": -1.0}},
        "results": curve_results
    }
    for name, r in curve_results.items():
        print(f"  {name}: D={r['direct_ht']:.4f}, N={r['noisy_ht']:.4f}, O={r['oracle_noisy_ht']:.4f}")
    print()

    # Experiment 5: synthetic_type1_control
    print("[5/5] synthetic_type1_control (at R_M=alpha)...")
    # Test at R_M = alpha for Type-I error
    err_type1 = estimate_error_rates_mc(
        n_m=n_m, n_j=n_j, r_m=alpha, tpr=0.9, fpr=0.1,
        alpha=alpha, zeta=zeta, n_trials=n_trials, seed=42,
        true_r_m_for_type1=alpha
    )
    results["experiments"]["synthetic_type1_control"] = {
        "description": "Synthetic: Type-I error control at zeta=0.05. All methods must control Type-I error below ~0.05. Paper: Figure 1, Type-I error curves at boundary R_M = alpha",
        "weight": 0.15,
        "primary_metric": "type1_error",
        "metrics": {"type1_error": {"higher_is_better": False, "coefficient": -1.0}},
        "results": {
            "direct_ht": {"type": "baseline", "type1_error": round(err_type1["type1"]["direct_ht"], 4)},
            "noisy_ht": {"type": "proposed", "type1_error": round(err_type1["type1"]["noisy_ht"], 4)},
            "oracle_noisy_ht": {"type": "proposed", "type1_error": round(err_type1["type1"]["oracle_noisy_ht"], 4)}
        }
    }
    print(f"  Direct HT Type-I: {err_type1['type1']['direct_ht']:.4f}")
    print(f"  Noisy HT Type-I: {err_type1['type1']['noisy_ht']:.4f}")
    print(f"  Oracle HT Type-I: {err_type1['type1']['oracle_noisy_ht']:.4f}\n")

    return results

if __name__ == "__main__":
    results = run_experiment()

    output_path = "/home/user/scoring/scores.json"
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\n=== Results written to {output_path} ===")
    print("\nSummary:")
    for exp_name, exp_data in results["experiments"].items():
        print(f"\n{exp_name}:")
        if "results" in exp_data:
            for method, r in exp_data["results"].items():
                for k, v in r.items():
                    if k.startswith("type") and k != "type":
                        print(f"  {method} {k}: {v}")
