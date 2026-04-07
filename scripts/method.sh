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

echo "=== Running Noisy HT Method ==="

# Run the evaluation
bash scripts/evaluate.sh

echo "=== Method run complete ==="
