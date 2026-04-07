#!/bin/bash
# Evaluation script — the standard way to evaluate work in this environment.
#
# This script runs evaluation using code in eval/ and writes scoring/scores.json.
#
# OUTPUT CONTRACT: writes scoring/scores.json with results matching reference.json
# structure. Experiment and metric names must match scoring/reference.json.
#
# Usage:
#   ./evaluate.sh                              # run default experiments
#   ./evaluate.sh synthetic_main 1000 42       # custom parameters

set -e

cd /home/user

mkdir -p scoring

EXPERIMENT="${1:-synthetic_main}"
N_TRIALS="${2:-1000}"
SEED="${3:-42}"

echo "Running evaluation: experiment=$EXPERIMENT, n_trials=$N_TRIALS, seed=$SEED"

/usr/bin/python3 << 'PYEOF'
import sys
sys.path.insert(0, '/home/user')
sys.path.insert(0, '/home/user/method')

from core import (
    direct_hypothesis_test,
    noisy_hypothesis_test_dual,
    oracle_noisy_hypothesis_test,
    ppi_family_wald_test,
)
from synthetic_data import generate_synthetic_data
import numpy as np
import json
import os

# Parameters matching the paper's Figure 1
n_m = 100
n_j = 10000
alpha = 0.25
zeta = 0.05
n_trials = int("$N_TRIALS")
seed = int("$SEED")

scores = {'experiments': {}}

# ============= EXPERIMENT 1: Power comparison (core claim) =============
# At R_M = 0.20 < alpha, with good judge TPR=0.9, FPR=0.1
# Noisy HT should have lower Type-II error than Direct HT
r_m_test = 0.20
tpr, fpr = 0.9, 0.1

type2_counts = {'direct_ht': 0, 'noisy_ht': 0, 'oracle_noisy_ht': 0}
for trial in range(n_trials):
    trial_seed = None if seed is None else (seed + trial * 17 + 31 + 1000)
    D_M_sm, D_M_sj, D_J_sm, D_J_sj = generate_synthetic_data(
        n_m, n_j, r_m_test, tpr, fpr, seed=trial_seed
    )
    reject_d, _ = direct_hypothesis_test(D_M_sm, alpha, zeta)
    reject_n, _ = noisy_hypothesis_test_dual(D_M_sm, D_M_sj, D_J_sj, alpha, zeta)
    reject_o, _ = oracle_noisy_hypothesis_test(D_J_sj, tpr, fpr, alpha, zeta)
    # Type-II error = P(not reject | H1 true)
    type2_counts['direct_ht'] += int(not reject_d)
    type2_counts['noisy_ht'] += int(not reject_n)
    type2_counts['oracle_noisy_ht'] += int(not reject_o)

scores['experiments']['synthetic_power_comparison'] = {
    'description': f'R_M={r_m_test}, alpha={alpha}, TPR={tpr}, FPR={fpr}, n_M={n_m}, n_J={n_j}',
    'results': {
        'direct_ht': {'type': 'baseline', 'type2_error': round(type2_counts['direct_ht']/n_trials, 4)},
        'noisy_ht': {'type': 'proposed', 'type2_error': round(type2_counts['noisy_ht']/n_trials, 4)},
        'oracle_noisy_ht': {'type': 'proposed', 'type2_error': round(type2_counts['oracle_noisy_ht']/n_trials, 4)},
    }
}
print(f"Power comparison: Direct={type2_counts['direct_ht']/n_trials:.3f}, Noisy={type2_counts['noisy_ht']/n_trials:.3f}, Oracle={type2_counts['oracle_noisy_ht']/n_trials:.3f}")

# ============= EXPERIMENT 2: Judge quality impact =============
judge_qualities = [
    (0.9, 0.1, 'high'),
    (0.8, 0.1, 'good'),
    (0.7, 0.2, 'moderate'),
]
scores['experiments']['synthetic_judge_quality_impact'] = {
    'description': f'R_M={r_m_test}, alpha={alpha}',
    'results': {}
}
for tpr, fpr, quality in judge_qualities:
    key = f'noisy_ht_{quality}'
    type2_count = 0
    for trial in range(n_trials):
        trial_seed = None if seed is None else (seed + trial * 17 + 31 + 2000 + int(tpr*10) + int(fpr*10))
        D_M_sm, D_M_sj, D_J_sm, D_J_sj = generate_synthetic_data(
            n_m, n_j, r_m_test, tpr, fpr, seed=trial_seed
        )
        reject, _ = noisy_hypothesis_test_dual(D_M_sm, D_M_sj, D_J_sj, alpha, zeta)
        type2_count += int(not reject)
    scores['experiments']['synthetic_judge_quality_impact']['results'][key] = {
        'type': 'proposed',
        'description': f'TPR={tpr}, FPR={fpr}',
        'type2_error': round(type2_count/n_trials, 4),
    }
print(f"Judge quality impact: high={scores['experiments']['synthetic_judge_quality_impact']['results']['noisy_ht_high']['type2_error']:.3f}, good={scores['experiments']['synthetic_judge_quality_impact']['results']['noisy_ht_good']['type2_error']:.3f}, moderate={scores['experiments']['synthetic_judge_quality_impact']['results']['noisy_ht_moderate']['type2_error']:.3f}")

# ============= EXPERIMENT 3: Oracle Gap =============
scores['experiments']['oracle_gap'] = {
    'description': f'R_M={r_m_test}, alpha={alpha}, TPR={tpr}, FPR={fpr}',
    'results': {
        'oracle_noisy_ht': {
            'type': 'proposed',
            'description': 'TPR/FPR known',
            'type2_error_oracle': round(type2_counts['oracle_noisy_ht']/n_trials, 4),
        },
        'noisy_ht': {
            'type': 'proposed',
            'description': 'TPR/FPR estimated from n_M=100',
            'type2_error_noisy': round(type2_counts['noisy_ht']/n_trials, 4),
            'oracle_gap': round((type2_counts['noisy_ht'] - type2_counts['oracle_noisy_ht'])/n_trials, 4),
        }
    }
}

# ============= EXPERIMENT 4: Type-II error vs R_M (curve) =============
r_m_values = [0.01, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50]
scores['experiments']['synthetic_type2_curve'] = {
    'description': f'Type-II error vs R_M, alpha={alpha}, TPR=0.9, FPR=0.1',
    'results': {}
}
tpr, fpr = 0.9, 0.1
for r_m in r_m_values:
    type2_d, type2_n, type2_o = 0, 0, 0
    for trial in range(n_trials):
        trial_seed = None if seed is None else (seed + trial * 17 + 31 + int(r_m*1000))
        D_M_sm, D_M_sj, D_J_sm, D_J_sj = generate_synthetic_data(
            n_m, n_j, r_m, tpr, fpr, seed=trial_seed
        )
        reject_d, _ = direct_hypothesis_test(D_M_sm, alpha, zeta)
        reject_n, _ = noisy_hypothesis_test_dual(D_M_sm, D_M_sj, D_J_sj, alpha, zeta)
        reject_o, _ = oracle_noisy_hypothesis_test(D_J_sj, tpr, fpr, alpha, zeta)
        type2_d += int(not reject_d)
        type2_n += int(not reject_n)
        type2_o += int(not reject_o)
    key = f'rm_{r_m:.2f}'
    scores['experiments']['synthetic_type2_curve']['results'][key] = {
        'r_m': r_m,
        'direct_ht': round(type2_d/n_trials, 4),
        'noisy_ht': round(type2_n/n_trials, 4),
        'oracle_noisy_ht': round(type2_o/n_trials, 4),
    }

# Write scores
with open('scoring/scores.json', 'w') as f:
    json.dump(scores, f, indent=2)

print(f"\nScores written to scoring/scores.json")
print(f"Total experiments: {len(scores['experiments'])}")
PYEOF