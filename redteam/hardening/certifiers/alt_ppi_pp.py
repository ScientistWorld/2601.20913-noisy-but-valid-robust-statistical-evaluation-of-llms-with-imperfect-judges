"""ALTERNATIVE: PPI++ Wald test (the paper's Algorithm 3, power-tuned weight)."""
import _common
from method.hypothesis_tests import ppi_family_wald_test

_common.run(lambda h, j, e, alpha, zeta: ppi_family_wald_test(
    h, j, e, None, None, alpha, zeta, variant="ppi_pp")[0])
