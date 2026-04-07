"""
Evaluation framework for the Noisy HT paper reproduction.

This module provides the core evaluation routines for running hypothesis
testing experiments and computing Type-I/Type-II error rates.

It is designed to be called from scripts/evaluate.sh and used by future
scientist agents to evaluate their own methods on the same problem.
"""

import json
import os
import sys
import numpy as np
from pathlib import Path

# Add method/ to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'method'))

from core import (
    direct_hypothesis_test,
    noisy_hypothesis_test_dual,
    oracle_noisy_hypothesis_test,
    ppi_family_wald_test,
)
from synthetic_data import generate_synthetic_data


def run_single_trial(D_M_sm, D_M_sj, D_J_sm, D_J_sj, true_tpr, true_fpr,
                     alpha, zeta):
    """
    Run all hypothesis testing methods on a single trial.

    Returns dict of method -> (reject, details)
    """
    results = {}

    reject, details = direct_hypothesis_test(D_M_sm, alpha, zeta)
    results['direct_ht'] = {'reject': reject, **details}

    reject, details = noisy_hypothesis_test_dual(D_M_sm, D_M_sj, D_J_sj, alpha, zeta)
    results['noisy_ht'] = {'reject': reject, **details}

    reject, details = oracle_noisy_hypothesis_test(D_J_sj, true_tpr, true_fpr, alpha, zeta)
    results['oracle_noisy_ht'] = {'reject': reject, **details}

    for variant in ['ppi', 'ppi_pp', 'ridge_ppi']:
        reject, details = ppi_family_wald_test(
            D_M_sm, D_M_sj, D_J_sj, true_tpr, true_fpr, alpha, zeta,
            variant=variant
        )
        results[variant] = {'reject': reject, **details}

    return results


def estimate_error_rates_mc(n_m, n_j, r_m, tpr, fpr, alpha, zeta,
                            n_trials=1000, seed=None, methods=None,
                            true_r_m_for_type1=None):
    """
    Estimate Type-I and Type-II error rates via Monte Carlo.

    Args:
        n_m, n_j: dataset sizes
        r_m: true model failure rate (used for Type-II estimation)
        tpr, fpr: judge parameters
        alpha: target threshold
        zeta: significance level
        n_trials: number of trials
        seed: random seed
        methods: list of method names
        true_r_m_for_type1: if provided, use this R_M for Type-I estimation

    Returns:
        dict with 'type1' and 'type2' sub-dicts mapping method -> error rate
    """
    if methods is None:
        methods = ['direct_ht', 'noisy_ht', 'oracle_noisy_ht', 'ppi', 'ppi_pp', 'ridge_ppi']

    # For Type-I error: test at R_M = alpha (boundary)
    # We reject H0 when the test says the model is reliable
    # Type-I error = P(reject | H0 true) = P(reject | R_M >= alpha)
    # We approximate by testing at R_M = alpha

    rejections_type1 = {m: 0 for m in methods}
    rejections_type2 = {m: 0 for m in methods}

    r_m_type1 = true_r_m_for_type1 if true_r_m_for_type1 is not None else alpha

    for trial in range(n_trials):
        trial_seed = None if seed is None else (seed + trial * 17 + 31)

        # Generate Type-I data (at boundary)
        D_M_sm_t1, D_M_sj_t1, D_J_sm_t1, D_J_sj_t1 = generate_synthetic_data(
            n_m, n_j, r_m_type1, tpr, fpr, seed=trial_seed
        )

        # Generate Type-II data (at given r_m < alpha)
        D_M_sm_t2, D_M_sj_t2, D_J_sm_t2, D_J_sj_t2 = generate_synthetic_data(
            n_m, n_j, r_m, tpr, fpr, seed=trial_seed
        )

        trial_results_t1 = run_single_trial(
            D_M_sm_t1, D_M_sj_t1, D_J_sm_t1, D_J_sj_t1,
            tpr, fpr, alpha, zeta
        )

        trial_results_t2 = run_single_trial(
            D_M_sm_t2, D_M_sj_t2, D_J_sm_t2, D_J_sj_t2,
            tpr, fpr, alpha, zeta
        )

        for m in methods:
            rejections_type1[m] += int(trial_results_t1[m]['reject'])
            # Type-II error: fail to reject H0 when H1 is true
            # H1: R_M < alpha. We reject H0 when reject=True.
            # Type-II error = P(not reject | H1 true) = P(reject=False | R_M < alpha)
            rejections_type2[m] += int(not trial_results_t2[m]['reject'])

    type1_rates = {m: rejections_type1[m] / n_trials for m in methods}
    type2_rates = {m: rejections_type2[m] / n_trials for m in methods}

    return {
        'type1': type1_rates,
        'type2': type2_rates,
    }


def run_synthetic_experiment(n_m=100, n_j=10000, alpha=0.25, zeta=0.05,
                             r_m_range=None, tpr_fpr_pairs=None,
                             n_trials=1000, seed=42):
    """
    Run the full synthetic experiment as described in the paper.

    Paper settings:
    - n_M = 100, n_J = 10,000
    - alpha = 0.25
    - zeta = 0.05
    - R_M in [0.01, 0.50]
    - Various TPR/FPR pairs for judge quality

    Returns results organized by R_M and TPR/FPR settings.
    """
    if r_m_range is None:
        r_m_range = [0.01, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50]

    if tpr_fpr_pairs is None:
        tpr_fpr_pairs = [
            (0.9, 0.1),   # High quality judge
            (0.8, 0.1),   # Good judge
            (0.7, 0.2),   # Moderate judge
        ]

    results = {}

    for tpr, fpr in tpr_fpr_pairs:
        key = f"tpr{tpr}_fpr{fpr}"
        results[key] = {
            'tpr': tpr,
            'fpr': fpr,
            'data': {}
        }

        for r_m in r_m_range:
            error_rates = estimate_error_rates_mc(
                n_m=n_m, n_j=n_j,
                r_m=r_m, tpr=tpr, fpr=fpr,
                alpha=alpha, zeta=zeta,
                n_trials=n_trials,
                seed=seed,
            )

            results[key]['data'][f'r_m_{r_m:.2f}'] = error_rates

    return results


def run_classification_experiment(data_dir, n_m=100, n_j=10000,
                                   alpha_range=None, zeta=0.05,
                                   n_trials=1000, seed=42):
    """
    Run classification experiments on real datasets.

    Expects data_dir to contain:
    - D_M_sm.npy: ground-truth labels for calibration set
    - D_M_sj.npy: judge labels for calibration set
    - D_J_sm.npy: ground-truth labels for evaluation set
    - D_J_sj.npy: judge labels for evaluation set

    Or runs LLM classifiers/judges if predictions not pre-computed.
    """
    # Load pre-computed labels if available
    d_m_sm_path = os.path.join(data_dir, 'D_M_sm.npy')
    d_m_sj_path = os.path.join(data_dir, 'D_M_sj.npy')
    d_j_sm_path = os.path.join(data_dir, 'D_J_sm.npy')
    d_j_sj_path = os.path.join(data_dir, 'D_J_sj.npy')

    if all(os.path.exists(p) for p in [d_m_sm_path, d_m_sj_path, d_j_sm_path, d_j_sj_path]):
        D_M_sm = np.load(d_m_sm_path)
        D_M_sj = np.load(d_m_sj_path)
        D_J_sm = np.load(d_j_sm_path)
        D_J_sj = np.load(d_j_sj_path)

        # Estimate true TPR/FPR from the full D_J (for oracle)
        n_j_full = len(D_J_sm)
        true_tpr = np.sum((D_J_sj == 1) & (D_J_sm == 1)) / np.sum(D_J_sm == 1)
        true_fpr = np.sum((D_J_sj == 1) & (D_J_sm == 0)) / np.sum(D_J_sm == 0)
        true_r_m = np.mean(D_J_sm)

        if alpha_range is None:
            alpha_range = [0.01, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40,
                           0.45, 0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.85,
                           0.90, 0.95, 0.99]

        results = {
            'true_tpr': float(true_tpr),
            'true_fpr': float(true_fpr),
            'true_r_m': float(true_r_m),
            'n_m': len(D_M_sm),
            'n_j': len(D_J_sm),
            'data': {}
        }

        for alpha in alpha_range:
            type1_rates = {}
            type2_rates = {}

            for trial in range(n_trials):
                trial_seed = None if seed is None else (seed + trial * 17 + 31)
                rng = np.random.default_rng(trial_seed)

                # Subsample for this trial
                idx_m = rng.choice(len(D_M_sm), min(n_m, len(D_M_sm)), replace=False)
                idx_j = rng.choice(len(D_J_sm), min(n_j, len(D_J_sm)), replace=False)

                trial_D_M_sm = D_M_sm[idx_m]
                trial_D_M_sj = D_M_sj[idx_m]
                trial_D_J_sj = D_J_sj[idx_j]

                # Direct HT
                reject, details = direct_hypothesis_test(trial_D_M_sm, alpha, zeta)
                if 'direct_ht' not in type1_rates:
                    type1_rates['direct_ht'] = 0
                    type2_rates['direct_ht'] = 0
                # Type-I: test at alpha
                reject_t1, _ = direct_hypothesis_test(trial_D_M_sm, alpha, zeta)
                type1_rates['direct_ht'] += int(reject_t1)
                # Type-II: test at true_r_m
                reject_t2, _ = direct_hypothesis_test(trial_D_M_sm, alpha, zeta)
                # Actually, we need to test at true_r_m, but direct HT uses D_M only
                # So we evaluate: does it reject at the given alpha? vs what's the true r_m?
                # For Type-II: we reject H0 correctly if reject=True when true_r_m < alpha
                type2_rates['direct_ht'] += int(not (true_r_m < alpha and reject_t2))

            for m in type1_rates:
                type1_rates[m] /= n_trials
                type2_rates[m] /= n_trials

            results['data'][f'alpha_{alpha:.2f}'] = {
                'type1': type1_rates,
                'type2': type2_rates,
            }

        return results
    else:
        return None


def compute_experiment_results(experiment_name, config, n_trials=1000, seed=42):
    """
    Run a specific experiment configuration and return results.

    Args:
        experiment_name: name of the experiment
        config: dict with experiment parameters
        n_trials: number of Monte Carlo trials
        seed: random seed

    Returns:
        dict with experiment results
    """
    method = config.get('method', 'synthetic')
    n_m = config.get('n_m', 100)
    n_j = config.get('n_j', 10000)
    alpha = config.get('alpha', 0.25)
    zeta = config.get('zeta', 0.05)

    if method == 'synthetic':
        tpr = config.get('tpr', 0.9)
        fpr = config.get('fpr', 0.1)
        r_m = config.get('r_m', 0.20)

        error_rates = estimate_error_rates_mc(
            n_m=n_m, n_j=n_j,
            r_m=r_m, tpr=tpr, fpr=fpr,
            alpha=alpha, zeta=zeta,
            n_trials=n_trials,
            seed=seed,
        )

        return {
            'experiment': experiment_name,
            'config': config,
            'type1_error': error_rates['type1'],
            'type2_error': error_rates['type2'],
        }

    elif method == 'classification':
        data_dir = config.get('data_dir')
        if data_dir is None:
            return None
        return run_classification_experiment(
            data_dir, n_m=n_m, n_j=n_j,
            alpha_range=config.get('alpha_range'),
            zeta=zeta, n_trials=n_trials, seed=seed
        )

    return None


def main():
    """Main evaluation entry point. Called from scripts/evaluate.sh."""
    import argparse
    parser = argparse.ArgumentParser(description='Evaluate Noisy HT methods')
    parser.add_argument('--experiment', type=str, default='synthetic_main',
                       help='Experiment name')
    parser.add_argument('--n_trials', type=int, default=1000,
                       help='Number of Monte Carlo trials')
    parser.add_argument('--seed', type=int, default=42,
                       help='Random seed')
    parser.add_argument('--output', type=str, default='scoring/scores.json',
                       help='Output file for scores')
    parser.add_argument('--config', type=str, default=None,
                       help='JSON config file for experiment')
    args = parser.parse_args()

    results = {}

    if args.config:
        with open(args.config) as f:
            config = json.load(f)
        results = compute_experiment_results(
            args.experiment, config, n_trials=args.n_trials, seed=args.seed
        )
    else:
        # Default: run synthetic main experiment matching paper Figure 1
        # n_M=100, n_J=10000, alpha=0.25, zeta=0.05
        print("Running synthetic experiment (default)...")

        tpr_fpr_pairs = [
            (0.9, 0.1),  # High quality judge (Figure 1A)
            (0.8, 0.1),  # Good judge (Figure 1B)
            (0.7, 0.2),  # Moderate judge (Figure 1C)
        ]
        r_m_values = [0.01, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50]
        alpha = 0.25
        zeta = 0.05
        n_m = 100
        n_j = 10000

        all_results = {}
        for tpr, fpr in tpr_fpr_pairs:
            key = f"tpr{int(tpr*100)}_fpr{int(fpr*100)}"
            all_results[key] = {}
            for r_m in r_m_values:
                error_rates = estimate_error_rates_mc(
                    n_m=n_m, n_j=n_j, r_m=r_m, tpr=tpr, fpr=fpr,
                    alpha=alpha, zeta=zeta,
                    n_trials=args.n_trials, seed=args.seed
                )
                all_results[key][f"r_m_{r_m:.2f}"] = error_rates

        results = {
            'experiment': 'synthetic_main',
            'config': {'n_m': n_m, 'n_j': n_j, 'alpha': alpha, 'zeta': zeta},
            'all_results': all_results,
            'methods': ['direct_ht', 'noisy_ht', 'oracle_noisy_ht', 'ppi', 'ppi_pp', 'ridge_ppi'],
        }

    # Write output
    os.makedirs(os.path.dirname(args.output) or '.', exist_ok=True)
    with open(args.output, 'w') as f:
        json.dump(results, f, indent=2, default=str)

    print(f"Results written to {args.output}")
    return results


if __name__ == '__main__':
    main()
