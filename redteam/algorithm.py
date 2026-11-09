"""Reconstruct the documented algorithm; never imported by the evaluator.

The shipped method/core.py is missing. This implementation uses only the
formula in visible briefing/method.md. Agreement with saved decisions is
checked by the audit, rather than assumed.
"""
import numpy as np
from scipy.stats import binom, norm

Z = float(norm.ppf(0.05))


def direct(sm, alpha=0.25):
    return bool(np.mean(sm) < alpha + Z * np.sqrt(alpha * (1-alpha) / len(sm)))


def noisy(sm, sj, uj, alpha=0.25):
    n1 = int(np.sum(sm))
    n0 = len(sm) - n1
    if not n1 or not n0:
        return False
    tpr = float(np.mean(sj[sm == 1]))
    fpr = float(np.mean(sj[sm == 0]))
    if tpr <= fpr:
        return False
    a = alpha * tpr + (1-alpha) * fpr
    variance = (a * (1-a) / len(uj) + alpha**2 * tpr * (1-tpr) / n1
                + (1-alpha)**2 * fpr * (1-fpr) / n0)
    return bool(np.mean(uj) < a + Z * np.sqrt(variance))


def better(sm, sj, uj, alpha=0.25):
    # Real fix: absent calibration classes should not erase the independent
    # evidence in human labels. A lower-tail exact binomial test supplies a
    # useful fallback. At the null, absent-class events have probability
    # alpha**100 + (1-alpha)**100 < 3.3e-13; all other decisions are unchanged.
    if not np.any(sm) or np.all(sm):
        return bool(binom.cdf(int(np.sum(sm)), len(sm), alpha) <= 0.05)
    return noisy(sm, sj, uj, alpha)


def oracle(uj, tpr=0.95, fpr=0.05, alpha=0.25):
    a = fpr + (tpr-fpr) * alpha
    return bool(np.mean(uj) < a + Z * np.sqrt(a * (1-a) / len(uj)))


def oracle_labels_shortcut(hidden_sm, alpha=0.25):
    """SHORTCUT: use all 10,000 supposedly unobserved ground-truth labels."""
    return bool(binom.cdf(int(np.sum(hidden_sm)), len(hidden_sm), alpha) <= 0.05)


def point_estimate_shortcut(sm, sj, uj, alpha=0.25):
    """SHORTCUT: drop uncertainty control while declaring zeta=0.05."""
    if not np.any(sm) or np.all(sm):
        return direct(sm, alpha)
    tpr = float(np.mean(sj[sm == 1]))
    fpr = float(np.mean(sj[sm == 0]))
    return bool(tpr > fpr and np.mean(uj) < alpha*tpr + (1-alpha)*fpr)
