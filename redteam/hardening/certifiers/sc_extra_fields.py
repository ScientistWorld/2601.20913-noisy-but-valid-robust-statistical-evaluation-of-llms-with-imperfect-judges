"""SHORTCUT (comparison tampering): reference decisions plus fabricated
comparison-row and score fields; the evaluator must ignore everything except
the certifier's own decisions."""
import _common
from method.hypothesis_tests import noisy_hypothesis_test_dual

args, data = _common.load()
n = data["calib_human"].shape[0]
dec = _common.per_instance(data, lambda h, j, e, a, z: noisy_hypothesis_test_dual(h, j, e, a, z)[0])
_common.write_raw(args, {"certify": [int(x) for x in dec],
                         "direct_ht": [0] * n, "oracle_noisy_ht": [0] * n,
                         "type2_error": 0.0, "oracle_gap": -1.0, "type1_error": 0.0})
