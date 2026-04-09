#!/bin/bash
# Reproduce Noisy HT paper's results end-to-end.
#
# This script runs full reproduction pipeline:
# 1. Run synthetic experiments with high trial count
# 2. Generate evaluation results in scoring/scores.json
# 3. Display comparison summary
#
# Assumes:
#   - Container is built (environment/container.sif)
#   - Dependencies installed (environment/setup.sh)
#   - Python packages available (numpy, scipy)
#
# This is the "gold standard" reproduction —
# you don't need to run this, but keep it in good shape
# so other agents can easily run a full loop of reproduction
# and get paper's numbers.

set -e

cd /home/user

echo "=========================================="
echo "Noisy Hypothesis Testing Framework - End-to-End Reproduction"
echo "=========================================="

# Run synthetic experiments with 10000 trials for accurate estimates
echo ""
echo "[Step 1/3] Running synthetic experiments..."
python -c "
import sys
sys.path.insert(0, '/home/user/method')
sys.path.insert(0, '/home/user/eval')

from evaluate import run_synth_experiment
import numpy as np
import json

# Parameters matching paper's Figure 1
n_m = 100
n_j = 10000
alpha = 0.25
zeta = 0.05
n_trials = 10000  # High trial count for accurate estimates

# Judge qualities from paper's Figure 1
tpr_fpr_pairs = [
    (0.9, 0.1, 'high'),
    (0.8, 0.1, 'good'),
    (0.7, 0.2, 'moderate'),
]

print(f'Running {n_trials}-trial Monte Carlo validation...')
print(f'Parameters: n_M={n_m}, n_J={n_j}, alpha={alpha}, zeta={zeta}')
print()

# R_M values from paper's curves (0.01 to 0.50)
r_m_values = [0.01, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50]

# Run experiments
results = run_synth_experiment(
    n_m=n_m, n_j=n_j, alpha=alpha, zeta=zeta,
    r_m_range=r_m_values,
    tpr_fpr_pairs=tpr_fpr_pairs,
    n_trials=n_trials,
    seed=42
)

print(f'\nExperiment complete. Results in scoring/scores.json')
print()
echo '[Step 2/3] Validation and scoring comparison...'

# Load scores and compare to reference
with open('scoring/scores.json') as f:
    scores = json.load(f)

with open('scoring/reference.json') as f:
    reference = json.load(f)

print(f'=== COMPARISON SUMMARY ===')
for exp_name, exp_data in scores.get('experiments', {}).items():
    print(f'\nExperiment: {exp_name}')
    print(f'  Description: {exp_data[\"description\"]}')

    if 'results' in exp_data:
        print(f'  Method Results (Type-II Error):')
        print(f'  {'  ':<20} {' ':<10} {' ':<10}".format('direct_ht', 'noisy_ht', 'oracle_noisy_ht'))
        print(f'-{' ':<20} {' ':<10}".format('direct_ht', 'noisy_ht', 'oracle_noisy_ht'))
        for method, method_data in exp_data['results'].items():
            type2 = method_data.get('type2_error', 0)
            print(f'  {method:12s}: {type2:.4f}')

    print()

echo ""
echo "=========================================="
echo "Full reproduction complete."
echo "Results saved to scoring/scores.json"
print(f"To run experiments on real datasets (Jigsaw, Hate Speech, SafeRLHF), download datasets"
echo "and run: bash scripts/evaluate.sh classification"
"