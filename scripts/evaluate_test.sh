#!/bin/bash
# Held-out (hidden) test. Runs with no arguments.
#
# Generates the held-out certification instances inside eval/test/ at run
# time, runs every certifier found under method/certifiers/ through the fixed
# file interface, scores each from its raw decisions, and writes
# scoring/scores_test.json. Exits non-zero if no certifier is found or any
# certifier fails (crash, malformed output, batch-dependent decisions, or a
# Type-I validity violation); failed certifiers are written with worst scores.
#
# Usage:
#   bash scripts/evaluate_test.sh

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT}"
PY="${PYTHON:-python3}"

"${PY}" "${ROOT}/eval/test/evaluate.py" --output "${ROOT}/scoring/scores_test.json"

echo ""
echo "=== Reference schema validation ==="
"${PY}" "${ROOT}/validate.py" --reference-only
