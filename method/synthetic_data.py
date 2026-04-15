"""Synthetic experiment helpers for reproducing the paper's method.

The reusable benchmark generator lives in :mod:`data.synthetic` so evaluation
and future methods can share the same data distribution without importing from
``method/``.
"""

from data.synthetic import generate_synthetic_data


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
