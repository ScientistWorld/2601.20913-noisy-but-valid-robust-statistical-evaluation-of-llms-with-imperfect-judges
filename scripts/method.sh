#!/bin/bash
# Run the Noisy HT method (synthetic + classification experiments).
#
# This script runs the paper's statistical hypothesis testing methods
# on synthetic data and (if available) real datasets.
#
# Usage:
#   bash scripts/method.sh

set -e

cd /home/user

N_TRIALS="${1:-1000}"
SEED="${2:-42}"
OUTPUT="${3:-/home/user/outputs/synthetic_results.json}"

echo "=== Running Noisy HT Method ==="
echo "Writing method artifact to ${OUTPUT}"

/usr/bin/python3 /home/user/method/run_synthetic.py \
  --n-trials "${N_TRIALS}" \
  --seed "${SEED}" \
  --output "${OUTPUT}"

echo "=== Method run complete ==="
