#!/bin/bash
# Visible train-slice evaluation. Same measurement and certifier interface as
# the held-out test, on a public batch of instances generated in eval/train/.
#
# Runs every certifier found under method/certifiers/ and writes
# scoring/scores_train.json. Exits non-zero if any certifier fails.
#
# Usage:
#   bash scripts/evaluate_train.sh            # public train seed
#   bash scripts/evaluate_train.sh 12345      # another public draw (dev only)

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT}"
PY="${PYTHON:-python3}"
SEED_ARGS=()
if [ "$#" -ge 1 ]; then
  SEED_ARGS=(--seed "$1")
fi

"${PY}" "${ROOT}/eval/train/evaluate.py" ${SEED_ARGS[@]+"${SEED_ARGS[@]}"} --output "${ROOT}/scoring/scores_train.json"

echo ""
echo "=== Reference schema validation ==="
# Informational only: the validator also cross-checks other score files, which
# must not change this script's verdict (that comes from the evaluator).
"${PY}" "${ROOT}/validate.py" --reference-only || echo "(validate.py reported issues; see above)"
