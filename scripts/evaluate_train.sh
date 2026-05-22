#!/bin/bash
# Visible train-slice evaluation entry point.
#
# Mirrors scripts/evaluate.sh:
#   ./scripts/evaluate_train.sh
#   ./scripts/evaluate_train.sh outputs/synthetic_train_results.json scoring/scores_train.json

set -e

cd /home/user

ARTIFACT="${1:-/home/user/outputs/synthetic_train_results.json}"
OUTPUT="${2:-/home/user/scoring/scores_train.json}"

echo "Running train-slice evaluation for artifact: ${ARTIFACT}"
/usr/bin/python3 /home/user/eval/train/evaluate.py \
  --artifact "${ARTIFACT}" \
  --output "${OUTPUT}"

echo ""
echo "=== Reference schema validation ==="
/usr/bin/python3 /home/user/validate.py --reference-only
