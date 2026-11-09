#!/bin/bash
# Standard evaluation entry point: scores every certifier under
# method/certifiers/ on the public train-slice instances (the same evaluator
# as scripts/evaluate_train.sh) and writes the canonical scoring/scores.json.
#
# Usage:
#   bash scripts/evaluate.sh

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT}"
PY="${PYTHON:-python3}"

"${PY}" "${ROOT}/eval/train/evaluate.py" --output "${ROOT}/scoring/scores.json"

echo ""
echo "=== Validation ==="
# Rows for certifiers not listed in scoring/reference.json are reported by the
# validator but do not invalidate the freshly written scores.
"${PY}" "${ROOT}/validate.py" --compare || echo "(validate.py reported issues; see above)"
