"""WEAKER: Noisy HT run at zeta/2 (valid but needlessly conservative)."""
import _common
from method.hypothesis_tests import noisy_hypothesis_test_dual

_common.run(lambda h, j, e, alpha, zeta: noisy_hypothesis_test_dual(h, j, e, alpha, zeta / 2)[0])
