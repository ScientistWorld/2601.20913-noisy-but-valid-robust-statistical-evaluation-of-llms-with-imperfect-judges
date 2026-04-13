"""
Core statistical hypothesis testing procedures for the Noisy HT framework.

Implements:
- Algorithm 1: Noisy Hypothesis Testing
- Algorithm 2: Direct Hypothesis Testing (baseline)
- Algorithm 3: Oracle Noisy Hypothesis Testing
- Algorithm 4: Unified PPI Family Wald Test

All procedures test H0: R_M >= alpha (model is unreliable) against
H1: R_M < alpha (model is reliable/certifiable).

Type-I error: P(reject H0 | H0 true) - must be controlled below zeta
Type-II error: P(fail to reject H0 | H1 true) - should be minimized
"""

import numpy as np
from scipy.stats import norm


def estimate_tpr_fpr(s_m, s_j):
    """
    Estimate judge TPR and FPR from calibration data.

    TPR = P(S_J = 1 | S_M = 1) = P(judge flags incorrect | ground truth incorrect)
    FPR = P(S_J = 1 | S_M = 0) = P(judge flags incorrect | ground truth correct)

    Args:
        s_m: array of ground-truth labels (0 = correct, 1 = incorrect)
        s_j: array of judge labels (0 = judge says correct, 1 = judge says incorrect)

    Returns:
        tpr_hat: estimated True Positive Rate
        fpr_hat: estimated False Positive Rate
        n_m1: count of ground-truth failures (S_M = 1)
        n_m0: count of ground-truth successes (S_M = 0)
    """
    n = len(s_m)
    n_m1 = np.sum(s_m == 1)
    n_m0 = np.sum(s_m == 0)

    if n_m1 == 0:
        tpr_hat = 0.0
    else:
        tpr_hat = np.sum((s_j == 1) & (s_m == 1)) / n_m1

    if n_m0 == 0:
        fpr_hat = 0.0
    else:
        fpr_hat = np.sum((s_j == 1) & (s_m == 0)) / n_m0

    return tpr_hat, fpr_hat, n_m1, n_m0


def noisy_hypothesis_test(s_m, s_j, alpha, zeta):
    """
    Algorithm 1: Noisy Hypothesis Testing Procedure.

    Uses a small human-labeled calibration set D_M to estimate judge TPR/FPR,
    then tests on a large judge-labeled dataset D_J.

    Args:
        s_m: array of ground-truth labels from D_M
        s_j: array of judge labels for D_M samples
        alpha: target reliability threshold (certify if failure rate < alpha)
        zeta: significance level for Type-I error control

    Returns:
        reject: True if H0 is rejected (model is certified as reliable)
        details: dict with intermediate values
    """
    n_m = len(s_m)
    tpr_hat, fpr_hat, n_m1, n_m0 = estimate_tpr_fpr(s_m, s_j)

    # Compute noisy failure rate from D_J (if s_j_judge provided separately)
    # In this version, s_j is the judge labels for D_J (large dataset)
    n_j = len(s_j)
    r_j_hat = np.mean(s_j)

    # Compute transformed threshold
    alpha_prime_hat = fpr_hat + (tpr_hat - fpr_hat) * alpha

    # Compute variance-corrected critical threshold
    # Using lower-tail: z_zeta = Phi^{-1}(zeta) is negative for zeta < 0.5
    # c_J' = alpha_hat' + z_zeta * SE = alpha_hat' - |z_zeta| * SE (lower bound)
    # Reject H0 if R_J > c_J' (observed rate exceeds lower confidence bound)
    # At boundary R_M = alpha: P(reject) = P(Z < z_zeta) = zeta (Type-I error controlled)
    z_zeta = norm.ppf(zeta)  # negative for zeta < 0.5

    var_rj = alpha_prime_hat * (1 - alpha_prime_hat) / n_j
    var_tpr = (alpha ** 2) * tpr_hat * (1 - tpr_hat) / n_m1 if n_m1 > 0 else 0
    var_fpr = ((1 - alpha) ** 2) * fpr_hat * (1 - fpr_hat) / n_m0 if n_m0 > 0 else 0

    se = np.sqrt(var_rj + var_tpr + var_fpr)
    c_j_prime = alpha_prime_hat + z_zeta * se

    reject = r_j_hat > c_j_prime

    details = {
        'n_m': n_m,
        'n_j': n_j,
        'tpr_hat': tpr_hat,
        'fpr_hat': fpr_hat,
        'n_m1': n_m1,
        'n_m0': n_m0,
        'r_j_hat': r_j_hat,
        'alpha_prime_hat': alpha_prime_hat,
        'se': se,
        'c_j_prime': c_j_prime,
        'z_zeta': z_zeta,
    }

    return reject, details


def noisy_hypothesis_test_dual(D_M_sm, D_M_sj, D_J_sj, alpha, zeta):
    """
    Full noisy HT using separate calibration and evaluation datasets.

    Args:
        D_M_sm: ground-truth labels for calibration set (n_M samples)
        D_M_sj: judge labels for calibration set samples (n_M samples)
        D_J_sj: judge labels for evaluation set (n_J samples)
        alpha: target reliability threshold
        zeta: significance level

    Returns:
        reject: True if H0 is rejected
        details: dict with intermediate values
    """
    n_m = len(D_M_sm)
    n_j = len(D_J_sj)

    tpr_hat, fpr_hat, n_m1, n_m0 = estimate_tpr_fpr(D_M_sm, D_M_sj)

    r_j_hat = np.mean(D_J_sj)
    alpha_prime_hat = fpr_hat + (tpr_hat - fpr_hat) * alpha

    z_zeta = norm.ppf(1 - zeta)

    var_rj = alpha_prime_hat * (1 - alpha_prime_hat) / n_j
    var_tpr = (alpha ** 2) * tpr_hat * (1 - tpr_hat) / n_m1 if n_m1 > 0 else 0
    var_fpr = ((1 - alpha) ** 2) * fpr_hat * (1 - fpr_hat) / n_m0 if n_m0 > 0 else 0

    se = np.sqrt(var_rj + var_tpr + var_fpr)
    c_j_prime = alpha_prime_hat + z_zeta * se

    reject = r_j_hat > c_j_prime

    details = {
        'n_m': n_m,
        'n_j': n_j,
        'tpr_hat': tpr_hat,
        'fpr_hat': fpr_hat,
        'n_m1': n_m1,
        'n_m0': n_m0,
        'r_j_hat': r_j_hat,
        'alpha_prime_hat': alpha_prime_hat,
        'se': se,
        'c_j_prime': c_j_prime,
        'z_zeta': z_zeta,
    }

    return reject, details


def direct_hypothesis_test(s_m, alpha, zeta):
    """
    Algorithm 2: Direct Hypothesis Testing (baseline).

    Uses only the small human-labeled dataset D_M.

    Args:
        s_m: array of ground-truth labels
        alpha: target reliability threshold
        zeta: significance level

    Returns:
        reject: True if H0 is rejected
        details: dict with intermediate values
    """
    n_m = len(s_m)
    r_m_hat = np.mean(s_m)

    # Lower-tail test: z_zeta is negative for zeta < 0.5
    # c_M = alpha + z_zeta * SE = alpha - |z_zeta| * SE
    # Reject H0 if R_M > c_M (observed rate exceeds lower confidence bound)
    z_zeta = norm.ppf(zeta)
    se = np.sqrt(alpha * (1 - alpha) / n_m)
    c_m = alpha + z_zeta * se

    reject = r_m_hat > c_m

    details = {
        'n_m': n_m,
        'r_m_hat': r_m_hat,
        'se': se,
        'c_m': c_m,
        'z_zeta': z_zeta,
    }

    return reject, details


def oracle_noisy_hypothesis_test(s_j, tpr, fpr, alpha, zeta):
    """
    Algorithm 4: Oracle Noisy Hypothesis Testing.

    Uses true (oracle) TPR and FPR values, plus the large judge-labeled dataset.

    Args:
        s_j: array of judge labels from D_J
        tpr: true True Positive Rate (known)
        fpr: true False Positive Rate (known)
        alpha: target reliability threshold
        zeta: significance level

    Returns:
        reject: True if H0 is rejected
        details: dict with intermediate values
    """
    n_j = len(s_j)
    r_j_hat = np.mean(s_j)

    alpha_prime = fpr + (tpr - fpr) * alpha
    # Lower-tail test: z_zeta is negative for zeta < 0.5
    # Reject H0 if R_J > c_J (observed rate exceeds lower confidence bound)
    z_zeta = norm.ppf(zeta)

    se = np.sqrt(alpha_prime * (1 - alpha_prime) / n_j)
    c_j = alpha_prime + z_zeta * se

    reject = r_j_hat > c_j

    details = {
        'n_j': n_j,
        'tpr': tpr,
        'fpr': fpr,
        'r_j_hat': r_j_hat,
        'alpha_prime': alpha_prime,
        'se': se,
        'c_j': c_j,
        'z_zeta': z_zeta,
    }

    return reject, details


def ppi_family_wald_test(D_M_sm, D_M_sj, D_J_sj, tpr, fpr, alpha, zeta,
                         variant='ridge_ppi', tau=0.0):
    """
    Algorithm 3: Unified PPI Family Wald Test.

    Prediction-Powered Inference variants for hypothesis testing.
    Variants: 'ppi', 'ppi_pp', 'ridge_ppi'

    Args:
        D_M_sm: ground-truth labels for calibration set
        D_M_sj: judge labels for calibration set
        D_J_sj: judge labels for evaluation set
        tpr: judge TPR (used for computing R_J_prime estimate)
        fpr: judge FPR (used for computing R_J_prime estimate)
        alpha: target reliability threshold
        zeta: significance level
        variant: 'ppi', 'ppi_pp', or 'ridge_ppi'
        tau: ridge penalty (for ridge_ppi only)

    Returns:
        reject: True if H0 is rejected
        details: dict with intermediate values
    """
    n_m = len(D_M_sm)
    n_j = len(D_J_sj)

    r_m_hat = np.mean(D_M_sm)
    r_j_prime_hat = np.mean(D_M_sj)
    r_j_hat = np.mean(D_J_sj)

    # R_11 = P(S_J=1, S_M=1) estimate
    r_11 = np.mean((D_M_sj == 1) & (D_M_sm == 1))

    # Compute A and B
    A = (r_j_hat * (1 - r_j_hat) / n_j) + (r_j_prime_hat * (1 - r_j_prime_hat) / n_m)
    B = (r_11 - r_m_hat * r_j_prime_hat) / n_m

    # Determine weight lambda
    if variant == 'ppi':
        lam = 1.0
    elif variant in ('ppi_pp', 'ridge_ppi'):
        A_adj = A + tau
        if A_adj == 0:
            lam = 0.0
        else:
            lam = B / A_adj
    else:
        raise ValueError(f"Unknown PPI variant: {variant}")

    # Compute test statistic
    r_hat = r_m_hat + lam * (r_j_hat - r_j_prime_hat)

    # Standard error
    var_term = (r_m_hat * (1 - r_m_hat) / n_m) + (lam ** 2) * A - 2 * lam * B
    if var_term < 0:
        var_term = 0  # safeguard
    nse = np.sqrt(var_term)

    # Lower-tail test: z_zeta is negative for zeta < 0.5
    # Reject H0 if R_hat > c_zeta
    z_zeta = norm.ppf(zeta)
    c_zeta = alpha + z_zeta * nse

    reject = r_hat > c_zeta

    details = {
        'n_m': n_m,
        'n_j': n_j,
        'r_m_hat': r_m_hat,
        'r_j_prime_hat': r_j_prime_hat,
        'r_j_hat': r_j_hat,
        'r_11': r_11,
        'lam': lam,
        'r_hat': r_hat,
        'nse': nse,
        'c_zeta': c_zeta,
        'variant': variant,
        'tau': tau,
    }

    return reject, details


def run_all_methods(D_M_sm, D_M_sj, D_J_sj, true_tpr, true_fpr, alpha, zeta):
    """
    Run all hypothesis testing methods and return results.

    Args:
        D_M_sm: ground-truth labels for calibration set
        D_M_sj: judge labels for calibration set (for D_M samples)
        D_J_sj: judge labels for evaluation set
        true_tpr: true TPR (for oracle method)
        true_fpr: true FPR (for oracle method)
        alpha: target reliability threshold
        zeta: significance level

    Returns:
        dict mapping method name to (reject, details)
    """
    results = {}

    # Direct HT
    reject, details = direct_hypothesis_test(D_M_sm, alpha, zeta)
    results['direct_ht'] = (reject, details)

    # Noisy HT (using D_J_sj as the judge labels for testing)
    reject, details = noisy_hypothesis_test_dual(D_M_sm, D_M_sj, D_J_sj, alpha, zeta)
    results['noisy_ht'] = (reject, details)

    # Oracle Noisy HT
    reject, details = oracle_noisy_hypothesis_test(D_J_sj, true_tpr, true_fpr, alpha, zeta)
    results['oracle_noisy_ht'] = (reject, details)

    # PPI variants
    for variant in ['ppi', 'ppi_pp', 'ridge_ppi']:
        reject, details = ppi_family_wald_test(
            D_M_sm, D_M_sj, D_J_sj, true_tpr, true_fpr, alpha, zeta,
            variant=variant
        )
        results[variant] = (reject, details)

    return results
