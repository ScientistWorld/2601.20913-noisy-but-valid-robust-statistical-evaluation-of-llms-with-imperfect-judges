#!/bin/bash
# Evaluation script — the standard way to evaluate work in this environment.
#
# Runs the paper's synthetic Monte Carlo benchmark and writes
# scoring/scores.json.  This script intentionally calls only eval/ code so the
# scorer is independent of any implementation in method/.
#
# Usage:
#   ./scripts/evaluate.sh          # run default experiments (1000 trials)
#   ./scripts/evaluate.sh 500 42   # custom: n_trials=500, seed=42

set -e

cd /home/user

N_TRIALS="${1:-1000}"
SEED="${2:-42}"

echo "Running evaluation: n_trials=${N_TRIALS}, seed=${SEED}"
/usr/bin/python3 /home/user/eval/evaluate.py \
  --n-trials "${N_TRIALS}" \
  --seed "${SEED}" \
  --output /home/user/scoring/scores.json

echo ""
echo "=== Validation ==="
/usr/bin/python3 /home/user/validate.py --compare
