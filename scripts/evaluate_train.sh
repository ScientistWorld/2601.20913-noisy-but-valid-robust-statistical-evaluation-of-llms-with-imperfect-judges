#!/bin/bash
# Train-slice evaluation entry point.
#
# Mirrors scripts/evaluate.sh:
#   ./scripts/evaluate_train.sh          # run default experiments (1000 trials)
#   ./scripts/evaluate_train.sh 500 42   # custom: n_trials=500, seed=42

set -e

cd /home/user

N_TRIALS="${1:-1000}"
SEED="${2:-42}"

echo "Running train evaluation: n_trials=${N_TRIALS}, seed=${SEED}"
/usr/bin/python3 /home/user/eval/train/evaluate.py \
  --n-trials "${N_TRIALS}" \
  --seed "${SEED}" \
  --output /home/user/scoring/scores_train.json

echo ""
echo "=== Validation ==="
/usr/bin/python3 /home/user/validate.py
