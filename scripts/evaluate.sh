#!/bin/bash
# Evaluation script — the standard way to evaluate work in this environment.
#
# Aggregates a method artifact and writes scoring/scores.json.  This script
# intentionally calls only eval/ code so the scorer is independent of any
# implementation in method/.
#
# Usage:
#   ./scripts/evaluate.sh
#   ./scripts/evaluate.sh outputs/synthetic_results.json scoring/scores.json

set -e

cd /home/user

ARTIFACT="${1:-/home/user/outputs/synthetic_results.json}"
OUTPUT="${2:-/home/user/scoring/scores.json}"

echo "Running evaluation for artifact: ${ARTIFACT}"
/usr/bin/python3 /home/user/eval/evaluate.py \
  --artifact "${ARTIFACT}" \
  --output "${OUTPUT}"

echo ""
echo "=== Validation ==="
/usr/bin/python3 /home/user/validate.py --compare
