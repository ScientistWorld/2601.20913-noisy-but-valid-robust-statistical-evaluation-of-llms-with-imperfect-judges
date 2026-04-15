#!/bin/bash
# CPU job for the Noisy HT synthetic reproduction.
# Runs the canonical evaluator plus independent train/test slices, then
# validates all score files and separation constraints.

set -e

cd /home/user

echo "=== Running canonical evaluation ==="
bash /home/user/scripts/evaluate.sh 1000 42

echo ""
echo "=== Running train slice ==="
bash /home/user/scripts/evaluate_train.sh 1000 42

echo ""
echo "=== Running held-out test slice ==="
bash /home/user/scripts/evaluate_test.sh 1000 42

echo ""
echo "=== Final validation ==="
/usr/bin/python3 /home/user/validate.py --compare

echo ""
echo "=== Job complete ==="
