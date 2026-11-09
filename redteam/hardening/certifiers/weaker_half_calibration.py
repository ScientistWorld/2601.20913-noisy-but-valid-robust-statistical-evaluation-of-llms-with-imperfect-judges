"""WEAKER: Noisy HT that discards half of the human calibration labels."""
import _common
from method.hypothesis_tests import noisy_hypothesis_test_dual

_common.run(lambda h, j, e, alpha, zeta: noisy_hypothesis_test_dual(h[:50], j[:50], e, alpha, zeta)[0])
