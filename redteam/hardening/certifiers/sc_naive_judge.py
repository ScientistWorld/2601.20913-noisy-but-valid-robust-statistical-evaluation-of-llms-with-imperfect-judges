"""SHORTCUT: trusts judge labels as ground truth (one-sample test on the judge set)."""
import math

from statistics import NormalDist

import _common


def decide(h, j, e, alpha, zeta):
    z = NormalDist().inv_cdf(zeta)
    return e.mean() < alpha + z * math.sqrt(alpha * (1 - alpha) / e.size)


_common.run(decide)
