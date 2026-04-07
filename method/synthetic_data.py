"""
Synthetic data generation for reproducing the paper's experimental results.

The paper generates synthetic ground-truth and judge labels by:
1. Drawing S_M ~ Bernoulli(R_M) — binary ground-truth failure labels
2. Drawing S_J from S_M with flip probabilities: P(S_J != S_M) depends on TPR/FPR
   - If S_M = 1: P(S_J = 1 | S_M = 1) = TPR, P(S_J = 0 | S_M = 1) = 1 - TPR
   - If S_M = 0: P(S_J = 1 | S_M = 0) = FPR, P(S_J = 0 | S_M = 0) = 1 - FPR

This produces the joint distribution:
   R_J = E[S_J] = R_M * TPR + (1 - R_M) * FPR
"""

import numpy as np


def generate_synthetic_data(n_m, n_j, r_m, tpr, fpr, seed=None):
    """
    Generate synthetic calibration and evaluation datasets.

    Args:
        n_m: size of calibration set D_M
        n_j: size of evaluation set D_J
        r_m: true model failure rate (ground truth)
        tpr: judge True Positive Rate
        fpr: judge False Positive Rate
        seed: random seed

    Returns:
        D_M_sm: ground-truth labels for calibration set
        D_M_sj: judge labels for calibration set (augmented)
        D_J_sm: ground-truth labels for evaluation set (for oracle comparison)
        D_J_sj: judge labels for evaluation set
    """
    if seed is not None:
        rng = np.random.default_rng(seed)
    else:
        rng = np.random.default_rng()

    # Generate ground-truth labels for calibration set
    D_M_sm = rng.binomial(1, r_m, size=n_m)

    # Generate judge labels for calibration set
    D_M_sj = np.zeros(n_m, dtype=int)
    for i in range(n_m):
        if D_M_sm[i] == 1:
            # Ground truth says incorrect → judge flags with probability TPR
            D_M_sj[i] = rng.binomial(1, tpr)
        else:
            # Ground truth says correct → judge incorrectly flags with probability FPR
            D_M_sj[i] = rng.binomial(1, fpr)

    # Generate ground-truth labels for evaluation set
    D_J_sm = rng.binomial(1, r_m, size=n_j)

    # Generate judge labels for evaluation set
    D_J_sj = np.zeros(n_j, dtype=int)
    for i in range(n_j):
        if D_J_sm[i] == 1:
            D_J_sj[i] = rng.binomial(1, tpr)
        else:
            D_J_sj[i] = rng.binomial(1, fpr)

    return D_M_sm, D_M_sj, D_J_sm, D_J_sj


def generate_synthetic_data_batch(n_m, n_j, r_m, tpr, fpr, n_trials=1000, seed=None):
    """
    Generate multiple synthetic trials for Monte Carlo estimation of error rates.

    Args:
        n_m: size of calibration set
        n_j: size of evaluation set
        r_m: true model failure rate
        tpr: judge True Positive Rate
        fpr: judge False Positive Rate
        n_trials: number of independent trials
        seed: base random seed

    Yields:
        tuples of (D_M_sm, D_M_sj, D_J_sm, D_J_sj) for each trial
    """
    if seed is not None:
        rng = np.random.default_rng(seed)
    else:
        rng = np.random.default_rng()

    for trial in range(n_trials):
        # Different seed for each trial
        trial_seed = None if seed is None else (seed + trial)
        yield generate_synthetic_data(n_m, n_j, r_m, tpr, fpr, seed=trial_seed)


def estimate_error_rates(n_m, n_j, r_m, tpr, fpr, alpha, zeta, n_trials=1000,
                         seed=None, methods=None):
    """
    Estimate Type-I and Type-II error rates for all hypothesis testing methods.

    Type-I error: fraction of trials where H0 is rejected when true R_M >= alpha
    Type-II error: fraction of trials where H0 is NOT rejected when true R_M < alpha

    For Type-I error: we test at R_M = alpha (boundary)
    For Type-II error: we test at the given R_M < alpha

    Args:
        n_m, n_j: dataset sizes
        r_m: true model failure rate
        tpr, fpr: judge parameters
        alpha: target threshold
        zeta: significance level
        n_trials: number of Monte Carlo trials
        seed: random seed
        methods: list of method names to evaluate (default: all)

    Returns:
        dict mapping method name to (type1_rate, type2_rate)
    """
    from .core import (
        direct_hypothesis_test, noisy_hypothesis_test_dual,
        oracle_noisy_hypothesis_test, ppi_family_wald_test
    )

    if methods is None:
        methods = ['direct_ht', 'noisy_ht', 'oracle_noisy_ht', 'ppi', 'ppi_pp', 'ridge_ppi']

    # Track rejections for each method
    rejections = {m: 0 for m in methods}

    for trial in range(n_trials):
        trial_seed = None if seed is None else (seed + trial)

        # Generate data
        D_M_sm, D_M_sj, D_J_sm, D_J_sj = generate_synthetic_data(
            n_m, n_j, r_m, tpr, fpr, seed=trial_seed
        )

        # Direct HT
        if 'direct_ht' in methods:
            reject, _ = direct_hypothesis_test(D_M_sm, alpha, zeta)
            rejections['direct_ht'] += reject

        # Noisy HT
        if 'noisy_ht' in methods:
            reject, _ = noisy_hypothesis_test_dual(D_M_sm, D_M_sj, D_J_sj, alpha, zeta)
            rejections['noisy_ht'] += reject

        # Oracle Noisy HT
        if 'oracle_noisy_ht' in methods:
            reject, _ = oracle_noisy_hypothesis_test(D_J_sj, tpr, fpr, alpha, zeta)
            rejections['oracle_noisy_ht'] += reject

        # PPI variants
        for variant in ['ppi', 'ppi_pp', 'ridge_ppi']:
            if variant in methods:
                reject, _ = ppi_family_wald_test(
                    D_M_sm, D_M_sj, D_J_sj, tpr, fpr, alpha, zeta,
                    variant=variant
                )
                rejections[variant] += reject

    # Compute error rates
    results = {}
    for m in methods:
        rate = rejections[m] / n_trials
        results[m] = rate

    return results


def estimate_type1_error(n_m, n_j, r_m, tpr, fpr, alpha, zeta, n_trials=1000, seed=None):
    """
    Estimate Type-I error rate. Tests at R_M = alpha (the boundary).
    Type-I error = fraction of trials rejecting H0 when R_M >= alpha.
    At the boundary R_M = alpha, we count rejections.
    """
    return estimate_error_rates(n_m, n_j, alpha, tpr, fpr, alpha, zeta, n_trials, seed)


def estimate_type2_error(n_m, n_j, r_m, tpr, fpr, alpha, zeta, n_trials=1000, seed=None):
    """
    Estimate Type-II error rate. Tests at the given R_M < alpha.
    Type-II error = fraction of trials NOT rejecting H0 when R_M < alpha.
    """
    type1 = estimate_error_rates(n_m, n_j, r_m, tpr, fpr, alpha, zeta, n_trials, seed)

    # Type-II error = 1 - power = 1 - (1 - type1 rate of accepting)
    # Actually: Type-II = fraction of NOT rejecting when alternative is true
    # = fraction where reject = False
    # For noisy_ht specifically:
    type2 = {}
    for m, rate in type1.items():
        type2[m] = 1 - rate  # rate is rejection fraction; type2 is failure-to-reject fraction
    return type2
