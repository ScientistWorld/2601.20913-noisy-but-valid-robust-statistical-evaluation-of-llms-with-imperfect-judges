"""BETTER: Bonferroni union of Noisy HT at 0.8*zeta and an exact binomial test
on the human labels at 0.2*zeta (valid by the union bound)."""
from scipy.stats import binom

import _common
from method.hypothesis_tests import noisy_hypothesis_test_dual


def decide(h, j, e, alpha, zeta):
    if binom.cdf(int(h.sum()), h.size, alpha) <= 0.2 * zeta:
        return True
    return noisy_hypothesis_test_dual(h, j, e, alpha, 0.8 * zeta)[0]


_common.run(decide)
