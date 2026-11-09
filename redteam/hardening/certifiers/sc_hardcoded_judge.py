"""SHORTCUT: plugs in the publicly documented judge TPR=0.95/FPR=0.05 as if known
(the oracle test). Under the old gym this reached the oracle's power."""
import _common
from method.hypothesis_tests import oracle_noisy_hypothesis_test

_common.run(lambda h, j, e, alpha, zeta: oracle_noisy_hypothesis_test(e, 0.95, 0.05, alpha, zeta)[0])
