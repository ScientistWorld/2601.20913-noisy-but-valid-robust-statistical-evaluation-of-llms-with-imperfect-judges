#!/bin/bash
# CPU job to regenerate canonical/train/test artifacts, aggregate scores, and validate.

set -e

cd /home/user

echo "=== Running canonical artifact ==="
/usr/bin/python3 /home/user/method/run_synthetic.py \
  --n-trials 1000 \
  --seed 42 \
  --output /home/user/outputs/synthetic_results.json
bash /home/user/scripts/evaluate.sh \
  /home/user/outputs/synthetic_results.json \
  /home/user/scoring/scores.json

echo ""
echo "=== Running train slice ==="
/usr/bin/python3 /home/user/method/run_synthetic.py \
  --n-trials 1000 \
  --seed 42 \
  --output /home/user/outputs/synthetic_train_results.json
bash /home/user/scripts/evaluate_train.sh \
  /home/user/outputs/synthetic_train_results.json \
  /home/user/scoring/scores_train.json

echo ""
echo "=== Running held-out test slice ==="
/usr/bin/python3 /home/user/method/run_synthetic.py \
  --n-trials 1000 \
  --seed 42 \
  --seed-offset 1000003 \
  --output /home/user/outputs/synthetic_test_results.json
bash /home/user/scripts/evaluate_test.sh \
  /home/user/outputs/synthetic_test_results.json \
  /home/user/scoring/scores_test.json

echo ""
echo "=== Final validation ==="
/usr/bin/python3 /home/user/validate.py --post-design

echo ""
echo "=== Job complete ==="
