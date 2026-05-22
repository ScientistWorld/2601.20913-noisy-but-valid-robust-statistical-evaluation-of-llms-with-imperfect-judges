#!/bin/bash
# End-to-end reproduction script.
# Runs inside the container to reproduce the paper's results from scratch.
#
# This paper uses synthetic data only, so no download step is needed.
# The script runs the method and then evaluates its artifact.

set -e

cd /home/user

echo "=== Noisy HT Paper Reproduction ==="
echo "Paper: Noisy but Valid: Robust Statistical Evaluation of LLMs with Imperfect Judges"
echo ""

bash scripts/method.sh 1000 42 /home/user/outputs/synthetic_results.json
bash scripts/evaluate.sh /home/user/outputs/synthetic_results.json /home/user/scoring/scores.json

echo ""
echo "=== Reproduction Complete ==="
echo "Results are in scoring/scores.json"
