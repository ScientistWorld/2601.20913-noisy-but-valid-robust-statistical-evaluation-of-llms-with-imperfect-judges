#!/bin/bash
# CPU job for the train/test evaluation split.
# This iteration's deliverable is the visible and held-out score baselines, so
# run only the split scorers and validate their outputs.

set -e

cd /home/user

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
