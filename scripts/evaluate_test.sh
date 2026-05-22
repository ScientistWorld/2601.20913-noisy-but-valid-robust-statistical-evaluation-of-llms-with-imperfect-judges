#!/bin/bash
# Held-out test-slice evaluation entry point.
#
# Mirrors scripts/evaluate.sh:
#   ./scripts/evaluate_test.sh          # run default experiments (1000 trials)
#   ./scripts/evaluate_test.sh 500 42   # custom: n_trials=500, seed=42

set -e

cd /home/user

N_TRIALS="${1:-1000}"
SEED="${2:-42}"

ARTIFACT="/home/user/outputs/synthetic_test_results.json"

echo "Running held-out test method artifact: n_trials=${N_TRIALS}, seed=${SEED}"
/usr/bin/python3 /home/user/method/run_synthetic.py \
  --n-trials "${N_TRIALS}" \
  --seed "${SEED}" \
  --seed-offset 1000003 \
  --output "${ARTIFACT}"

echo "Aggregating held-out test scores"
/usr/bin/python3 /home/user/eval/evaluate.py \
  --artifact "${ARTIFACT}" \
  --output /home/user/scoring/scores_test.json

echo ""
echo "=== Validation ==="
/usr/bin/python3 /home/user/validate.py
