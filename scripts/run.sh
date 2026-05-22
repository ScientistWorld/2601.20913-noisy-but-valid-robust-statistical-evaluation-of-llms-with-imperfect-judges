#!/bin/bash
# CPU job to regenerate method artifacts, aggregate scores, and validate.

set -e

cd /home/user

echo "=== Running canonical method artifact ==="
bash /home/user/scripts/method.sh 1000 42 /home/user/outputs/synthetic_results.json

echo ""
echo "=== Smoke-testing public Noisy HT API ==="
/usr/bin/python3 - <<'PY'
from data.synthetic import generate_synthetic_data
from method.core import noisy_hypothesis_test, noisy_hypothesis_test_dual

D_M_sm, D_M_sj, _, D_J_sj = generate_synthetic_data(100, 1000, 0.2, 0.9, 0.1, 123)
wrapped = noisy_hypothesis_test(D_M_sm, D_M_sj, D_J_sj, 0.25, 0.05)
direct = noisy_hypothesis_test_dual(D_M_sm, D_M_sj, D_J_sj, 0.25, 0.05)
assert wrapped[0] == direct[0]
assert wrapped[1] == direct[1]
print("Noisy HT wrapper smoke test passed")
PY

echo ""
echo "=== Evaluating canonical artifact ==="
bash /home/user/scripts/evaluate.sh /home/user/outputs/synthetic_results.json /home/user/scoring/scores.json

echo ""
echo "=== Running train slice ==="
/usr/bin/python3 /home/user/method/run_synthetic.py \
  --n-trials 1000 \
  --seed 42 \
  --output /home/user/outputs/synthetic_train_results.json
/usr/bin/python3 /home/user/eval/evaluate.py \
  --artifact /home/user/outputs/synthetic_train_results.json \
  --output /home/user/scoring/scores_train.json

echo ""
echo "=== Running held-out test slice ==="
/usr/bin/python3 /home/user/method/run_synthetic.py \
  --n-trials 1000 \
  --seed 42 \
  --seed-offset 1000003 \
  --output /home/user/outputs/synthetic_test_results.json
/usr/bin/python3 /home/user/eval/evaluate.py \
  --artifact /home/user/outputs/synthetic_test_results.json \
  --output /home/user/scoring/scores_test.json

echo ""
echo "=== Final validation ==="
/usr/bin/python3 /home/user/validate.py --compare

echo ""
echo "=== Job complete ==="
