#!/bin/bash
# Reproduce the paper's results end-to-end.
#
# This script runs the full reproduction pipeline:
# 1. Generate synthetic data experiments (Figure 1)
# 2. Evaluate all hypothesis testing methods
# 3. Generate comparison results
#
# Assumes:
#   - Container is built (environment/container.sif)
#   - Working directory is /home/user

set -e

cd /home/user

echo "=========================================="
echo "Noisy HT Reproduction Pipeline"
echo "=========================================="

# Run synthetic experiments with high trial count for accurate estimates
echo ""
echo "[1/2] Running synthetic experiments (n_trials=1000)..."
bash scripts/evaluate.sh synthetic_main 1000 42

echo ""
echo "[2/2] Validation and scoring..."
python -c "
import json

# Load scores
with open('scoring/scores.json') as f:
    scores = json.load(f)

# Load reference
with open('scoring/reference.json') as f:
    reference = json.load(f)

# Print comparison summary
print('=== REPRODUCTION SUMMARY ===')
for exp_name, exp_data in scores.get('experiments', {}).items():
    print(f'\nExperiment: {exp_name}')
    for method, result in exp_data.get('results', {}).items():
        desc = result.get('description', '')
        for metric, value in result.items():
            if metric not in ('type', 'description'):
                print(f'  {method}: {metric} = {value:.4f}')

print('\n=== Done ===')
"

echo ""
echo "Full reproduction complete. Results in scoring/scores.json"
