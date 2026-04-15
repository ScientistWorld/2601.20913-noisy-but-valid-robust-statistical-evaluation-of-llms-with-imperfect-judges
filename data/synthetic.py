"""Synthetic label generator shared by evaluation and method implementations.

The generator defines the benchmark data distribution: a binary ground-truth
failure label and a correlated binary auxiliary-judge label with specified
true-positive and false-positive rates.
"""

from __future__ import annotations

import numpy as np


def generate_synthetic_data(
    n_m: int,
    n_j: int,
    r_m: float,
    tpr: float,
    fpr: float,
    seed: int | None = None,
):
    """Generate paired human-label and auxiliary-judge samples.

    Args:
        n_m: Number of paired calibration samples.
        n_j: Number of auxiliary-judge evaluation samples.
        r_m: Ground-truth failure probability.
        tpr: Auxiliary judge true-positive rate.
        fpr: Auxiliary judge false-positive rate.
        seed: Optional random seed.

    Returns:
        Tuple ``(d_m_sm, d_m_sj, d_j_sm, d_j_sj)`` containing calibration
        ground-truth labels, calibration judge labels, evaluation ground-truth
        labels, and evaluation judge labels.
    """
    rng = np.random.default_rng(seed)
    d_m_sm = rng.binomial(1, r_m, size=n_m)
    d_m_sj = np.where(
        d_m_sm == 1,
        rng.binomial(1, tpr, size=n_m),
        rng.binomial(1, fpr, size=n_m),
    )
    d_j_sm = rng.binomial(1, r_m, size=n_j)
    d_j_sj = np.where(
        d_j_sm == 1,
        rng.binomial(1, tpr, size=n_j),
        rng.binomial(1, fpr, size=n_j),
    )
    return d_m_sm, d_m_sj, d_j_sm, d_j_sj
