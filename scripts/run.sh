#!/bin/bash
# CPU job for the designer train/test evaluation split.
# Runs both new slice evaluators and writes scoring/scores_train.json and
# scoring/scores_test.json.

set -e

cd /home/user

echo "=== Running train slice ==="
bash /home/user/scripts/evaluate_train.sh 1000 42

echo ""
echo "=== Running held-out test slice ==="
bash /home/user/scripts/evaluate_test.sh 1000 42

echo ""
echo "=== Job complete ==="
