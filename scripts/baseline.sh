#!/bin/bash
# Baselines (the small-label-only test "direct_ht" and the known-judge
# reference "oracle_noisy_ht") are computed by the evaluators themselves on
# the same instances every certifier sees, so they cannot be altered by a
# method. This script prints them from the public train-slice evaluation.
#
# Usage:
#   bash scripts/baseline.sh

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT}"
bash "${ROOT}/scripts/evaluate_train.sh"
"${PYTHON:-python3}" - << 'PYEOF'
import json
s = json.load(open("scoring/scores_train.json"))
for exp, rows in s.items():
    if exp.startswith("_"):
        continue
    for row in ("direct_ht", "oracle_noisy_ht"):
        print(f"{exp:<30} {row:<18} {rows.get(row)}")
PYEOF
