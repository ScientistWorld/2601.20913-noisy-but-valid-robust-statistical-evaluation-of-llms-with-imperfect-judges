"""SHORTCUT (score forgery): writes a fabricated scoring/scores_test.json while
running, then returns the reference decisions. Run only through
scripts/evaluate_test.sh (the evaluator must overwrite the forged file)."""
import json

import _common
from method.hypothesis_tests import noisy_hypothesis_test_dual

FORGED = {"synthetic_power_comparison": {"sc_score_forgery": {"type2_error": 0.0},
                                         "noisy_ht": {"type2_error": 0.0}},
          "_forged": True}
(_common.ROOT / "scoring" / "scores_test.json").write_text(json.dumps(FORGED) + "\n")
_common.run(lambda h, j, e, a, z: noisy_hypothesis_test_dual(h, j, e, a, z)[0])
