#!/bin/bash
# CPU smoke job for the packaged reproduction environment.
# Runs the reusable evaluator and validates scoring/scores.json.

set -e

cd /home/user

echo "=== Running Noisy HT evaluation smoke job ==="
bash /home/user/scripts/evaluate.sh 1000 42

echo ""
echo "=== Job complete ==="
