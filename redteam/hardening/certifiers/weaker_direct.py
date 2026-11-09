"""WEAKER: ignores the judge entirely (Direct HT on the human labels)."""
import _common
from method.hypothesis_tests import direct_hypothesis_test

_common.run(lambda h, j, e, alpha, zeta: direct_hypothesis_test(h, alpha, zeta)[0])
