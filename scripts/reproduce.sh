#!/bin/bash
# End-to-end reproduction script.
# Runs inside the container to reproduce the paper's results from scratch.
#
# This paper uses synthetic data only, so no download step is needed.
# The script runs the evaluation pipeline and writes scoring/scores.json.

set -e

cd /home/user

echo "=== Noisy HT Paper Reproduction ==="
echo "Paper: Noisy but Valid: Robust Statistical Evaluation of LLMs with Imperfect Judges"
echo ""

# Run evaluation (which generates scores.json)
bash scripts/evaluate.sh 1000 42

echo ""
echo "=== Reproduction Complete ==="
echo "Results are in scoring/scores.json"
