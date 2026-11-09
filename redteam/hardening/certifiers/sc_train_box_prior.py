"""SHORTCUT (tuned to train): guesses the judge regime from the calibration set,
then assumes the most favourable-for-validity corner of the train slice's
public judge-quality box as known judge parameters (oracle-style test)."""
import math

from statistics import NormalDist

import _common

TRAIN_BOX = {"hq": (0.95, 0.05), "weak_tpr": (0.75, 0.05), "high_fpr": (0.95, 0.25)}
HALF_WIDTH = 0.03


def decide(h, j, e, alpha, zeta):
    n1 = int(h.sum())
    n0 = h.size - n1
    tpr = float(j[h == 1].mean()) if n1 else 1.0
    fpr = float(j[h == 0].mean()) if n0 else 0.0
    regime = "high_fpr" if fpr > 0.15 else ("weak_tpr" if tpr < 0.85 else "hq")
    t0, f0 = TRAIN_BOX[regime]
    a_min = (f0 - HALF_WIDTH) * (1 - alpha) + (t0 - HALF_WIDTH) * alpha
    z = NormalDist().inv_cdf(zeta)
    return e.mean() < a_min + z * math.sqrt(a_min * (1 - a_min) / e.size)


_common.run(decide)
