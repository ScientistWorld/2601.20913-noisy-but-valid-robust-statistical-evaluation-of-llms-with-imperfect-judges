#!/bin/bash
# Evaluation script — the standard way to evaluate work in this environment.
#
# Runs Monte Carlo experiments and writes scoring/scores.json.
# This paper uses purely synthetic data — no external datasets needed.
#
# OUTPUT CONTRACT: writes scoring/scores.json with results matching reference.json
# structure. Experiment and metric names must match scoring/reference.json.
#
# Usage:
#   ./evaluate.sh                    # run default experiments (1000 trials)
#   ./evaluate.sh 500 42             # custom: n_trials=500, seed=42

set -e

cd /home/user

mkdir -p scoring

N_TRIALS="${1:-1000}"
SEED="${2:-42}"

echo "Running evaluation: n_trials=$N_TRIALS, seed=$SEED"

/usr/bin/python3 << PYEOF
import sys
sys.path.insert(0, '/home/user/method')

from core import (
    direct_hypothesis_test,
    noisy_hypothesis_test_dual,
    oracle_noisy_hypothesis_test,
)
from synthetic_data import generate_synthetic_data
import numpy as np
import json
import os

# Paper settings
n_m = 100
n_j = 10000
alpha = 0.25
zeta = 0.05
n_trials = $N_TRIALS
seed = $SEED

scores = {}

# === Experiment 1: synthetic_power_comparison ===
# Core claim: Noisy HT has lower Type-II error than Direct HT
# Settings: R_M=0.20, TPR=0.9, FPR=0.1
print("Experiment 1: synthetic_power_comparison")
tpr, fpr = 0.9, 0.1
r_m_test = 0.20

t2_d, t2_n, t2_o = 0, 0, 0
t1_d, t1_n, t1_o = 0, 0, 0

for trial in range(n_trials):
    # Type-II: H1 true (R_M < alpha)
    s = seed + trial * 2
    D_M_sm, D_M_sj, D_J_sm, D_J_sj = generate_synthetic_data(n_m, n_j, r_m_test, tpr, fpr, seed=s)
    rd, _ = direct_hypothesis_test(D_M_sm, alpha, zeta)
    rn, _ = noisy_hypothesis_test_dual(D_M_sm, D_M_sj, D_J_sj, alpha, zeta)
    ro, _ = oracle_noisy_hypothesis_test(D_J_sj, tpr, fpr, alpha, zeta)
    t2_d += int(not rd)
    t2_n += int(not rn)
    t2_o += int(not ro)

    # Type-I: H0 boundary (R_M = alpha)
    s = seed + trial * 2 + 1
    D_M_sm, D_M_sj, D_J_sm, D_J_sj = generate_synthetic_data(n_m, n_j, alpha, tpr, fpr, seed=s)
    rd, _ = direct_hypothesis_test(D_M_sm, alpha, zeta)
    rn, _ = noisy_hypothesis_test_dual(D_M_sm, D_M_sj, D_J_sj, alpha, zeta)
    ro, _ = oracle_noisy_hypothesis_test(D_J_sj, tpr, fpr, alpha, zeta)
    t1_d += int(rd)
    t1_n += int(rn)
    t1_o += int(ro)

scores['synthetic_power_comparison'] = {
    'direct_ht': {'type2_error': round(t2_d/n_trials, 4)},
    'noisy_ht': {'type2_error': round(t2_n/n_trials, 4)},
    'oracle_noisy_ht': {'type2_error': round(t2_o/n_trials, 4)},
}
print(f"  Type-II: Direct={t2_d/n_trials:.3f}, Noisy={t2_n/n_trials:.3f}, Oracle={t2_o/n_trials:.3f}")

# === Experiment 2: oracle_gap ===
print("Experiment 2: oracle_gap")
gap = (t2_n - t2_o) / n_trials
scores['oracle_gap'] = {
    'oracle_noisy_ht': {'type2_error_oracle': round(t2_o/n_trials, 4), 'oracle_gap': round(gap, 4)},
    'noisy_ht': {'type2_error_noisy': round(t2_n/n_trials, 4), 'oracle_gap': round(gap, 4)},
}
print(f"  Oracle gap = {gap:.3f}")

# === Experiment 3: synthetic_type2_curve ===
print("Experiment 3: synthetic_type2_curve")
r_m_values = [0.01, 0.10, 0.20, 0.30]
curve = {}
for r_m in r_m_values:
    cnt = 0
    for trial in range(n_trials):
        s = seed + trial * 3 + int(r_m * 100) + 10000
        D_M_sm, D_M_sj, D_J_sm, D_J_sj = generate_synthetic_data(n_m, n_j, r_m, tpr, fpr, seed=s)
        rn, _ = noisy_hypothesis_test_dual(D_M_sm, D_M_sj, D_J_sj, alpha, zeta)
        cnt += int(not rn)
    val = cnt / n_trials
    curve[f'rm_{r_m:.2f}'] = {'type2_error': round(val, 4)}
    print(f"  R_M={r_m:.2f}: Type-II={val:.3f}")

scores['synthetic_type2_curve'] = curve

# === Experiment 4: synthetic_type1_control ===
print("Experiment 4: synthetic_type1_control")
scores['synthetic_type1_control'] = {
    'direct_ht': {'type1_error': round(t1_d/n_trials, 4)},
    'noisy_ht': {'type1_error': round(t1_n/n_trials, 4)},
    'oracle_noisy_ht': {'type1_error': round(t1_o/n_trials, 4)},
}
print(f"  Type-I: Direct={t1_d/n_trials:.3f}, Noisy={t1_n/n_trials:.3f}, Oracle={t1_o/n_trials:.3f}")

# Write scores
with open('scoring/scores.json', 'w') as f:
    json.dump(scores, f, indent=2)

print(f"\nScores written to scoring/scores.json")

# Verify core claim
print("\n=== Core Claim ===")
claim = t2_n/n_trials < t2_d/n_trials
print(f"Noisy HT ({t2_n/n_trials:.3f}) < Direct HT ({t2_d/n_trials:.3f}): {claim}")
if claim:
    print(f"SUPPORTED: {abs(t2_d/n_trials - t2_n/n_trials)*100:.1f}pp reduction")
PYEOF

echo ""
echo "=== Validation ==="
/usr/bin/python3 /home/user/validate.py --compare
