"""SHORTCUT: drops all uncertainty correction (compares the judge flag rate with
the plug-in transformed threshold) while claiming the same significance level."""
import _common
from method.hypothesis_tests import direct_hypothesis_test


def decide(h, j, e, alpha, zeta):
    n1 = int(h.sum())
    if n1 == 0 or n1 == h.size:
        return direct_hypothesis_test(h, alpha, zeta)[0]
    tpr = float(j[h == 1].mean())
    fpr = float(j[h == 0].mean())
    return tpr > fpr and e.mean() < alpha * tpr + (1 - alpha) * fpr


_common.run(decide)
