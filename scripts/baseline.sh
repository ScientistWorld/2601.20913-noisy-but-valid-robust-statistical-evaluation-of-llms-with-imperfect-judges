#!/bin/bash
# Run a baseline method from the paper.
#
# Baselines are simple reference methods the paper compares against. 
# Implement this only if applicable, i.e. the paper has baselines.
# You do not need to implement all baselines to begin — 
# just enough to validate that the evaluation pipeline works 
# and provide a reference point. You can decide to expand more baselines later.
# Each baseline must be actually run and scored through evaluate.sh
# so the numbers are verified, not self-reported.
# You can decide what this baseline script should do yourself.
#
# Usage:
#   bash scripts/baseline.sh <name>

set -euo pipefail

cd /home/user

TRIALS="${1:-1000}"
SEED="${2:-42}"

echo "Running Direct HT baseline through the shared evaluation pipeline."
echo "The resulting scoring/scores.json includes the direct_ht baseline rows."
bash scripts/evaluate.sh "$TRIALS" "$SEED"
