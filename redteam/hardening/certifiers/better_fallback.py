"""BETTER: Noisy HT, plus an exact binomial test on the human labels when the
calibration set has no failures (or no successes), where the judge model
cannot be estimated. All other decisions are identical to the reference."""
from scipy.stats import binom

import _common
from method.hypothesis_tests import noisy_hypothesis_test_dual


def decide(h, j, e, alpha, zeta):
    n1 = int(h.sum())
    if n1 == 0 or n1 == h.size:
        return binom.cdf(n1, h.size, alpha) <= zeta
    return noisy_hypothesis_test_dual(h, j, e, alpha, zeta)[0]


_common.run(decide)
