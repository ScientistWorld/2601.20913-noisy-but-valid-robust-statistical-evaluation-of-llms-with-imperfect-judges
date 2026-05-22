#!/bin/bash
# Held-out test-slice evaluation entry point.
#
# Mirrors scripts/evaluate.sh:
#   ./scripts/evaluate_test.sh
#   ./scripts/evaluate_test.sh outputs/synthetic_test_results.json scoring/scores_test.json
#
# The test scorer reads scoring/scores_train.json and emits the same
# experiment/method entries for the held-out artifact.

set -e

cd /home/user

ARTIFACT="${1:-/home/user/outputs/synthetic_test_results.json}"
OUTPUT="${2:-/home/user/scoring/scores_test.json}"
TRAIN_SCORES="/home/user/scoring/scores_train.json"

echo "Running held-out test-slice evaluation for artifact: ${ARTIFACT}"
/usr/bin/python3 /home/user/eval/test/evaluate.py \
  --artifact "${ARTIFACT}" \
  --output "${OUTPUT}" \
  --train-scores "${TRAIN_SCORES}"

echo ""
echo "=== Reference schema validation ==="
/usr/bin/python3 /home/user/validate.py --reference-only
