#!/bin/bash
# Run validation and Monte Carlo experiments inside compute container.
# CPU-only job — no GPU needed for statistical computations.
set -e

cd /home/user

echo "=== Running Monte Carlo experiments ==="

/usr/bin/python3 << 'PYEOF'
import sys
import os
import json
import numpy as np

sys.path.insert(0, '/home/user/method')
from core import direct_hypothesis_test, noisy_hypothesis_test_dual, oracle_noisy_hypothesis_test
from synthetic_data import generate_synthetic_data

# Paper settings
ALPHA = 0.25
ZETA = 0.05
N_M = 100       # calibration set size
N_J = 10000     # evaluation set size
N_TRIALS = 1000

# === Experiment 1: synthetic_power_comparison ===
# Core claim: Noisy HT has lower Type-II error than Direct HT
# Settings: R_M=0.20, TPR=0.9, FPR=0.1
print("Experiment 1: synthetic_power_comparison (R_M=0.20, TPR=0.9, FPR=0.1)")
TPR, FPR = 0.9, 0.1
R_M = 0.20

type2_direct = 0
type2_noisy = 0
type2_oracle = 0
type1_direct = 0
type1_noisy = 0
type1_oracle = 0

for trial in range(N_TRIALS):
    # Type-II: test at R_M = 0.20 (H1 true, model is reliable)
    seed_t2 = 42 + trial * 2
    D_M_sm, D_M_sj, D_J_sm, D_J_sj = generate_synthetic_data(N_M, N_J, R_M, TPR, FPR, seed=seed_t2)
    rd, _ = direct_hypothesis_test(D_M_sm, ALPHA, ZETA)
    rn, _ = noisy_hypothesis_test_dual(D_M_sm, D_M_sj, D_J_sj, ALPHA, ZETA)
    ro, _ = oracle_noisy_hypothesis_test(D_J_sj, TPR, FPR, ALPHA, ZETA)
    type2_direct += int(not rd)
    type2_noisy += int(not rn)
    type2_oracle += int(not ro)

    # Type-I: test at R_M = alpha (H0 boundary)
    seed_t1 = 42 + trial * 2 + 1
    D_M_sm, D_M_sj, D_J_sm, D_J_sj = generate_synthetic_data(N_M, N_J, ALPHA, TPR, FPR, seed=seed_t1)
    rd, _ = direct_hypothesis_test(D_M_sm, ALPHA, ZETA)
    rn, _ = noisy_hypothesis_test_dual(D_M_sm, D_M_sj, D_J_sj, ALPHA, ZETA)
    ro, _ = oracle_noisy_hypothesis_test(D_J_sj, TPR, FPR, ALPHA, ZETA)
    type1_direct += int(rd)
    type1_noisy += int(rn)
    type1_oracle += int(ro)

t2_direct = type2_direct / N_TRIALS
t2_noisy = type2_noisy / N_TRIALS
t2_oracle = type2_oracle / N_TRIALS
t1_direct = type1_direct / N_TRIALS
t1_noisy = type1_noisy / N_TRIALS
t1_oracle = type1_oracle / N_TRIALS

print(f"  Type-II: Direct={t2_direct:.3f}, Noisy={t2_noisy:.3f}, Oracle={t2_oracle:.3f}")
print(f"  Type-I:  Direct={t1_direct:.3f}, Noisy={t1_noisy:.3f}, Oracle={t1_oracle:.3f}")

# === Experiment 2: synthetic_type2_curve ===
# Type-II error across R_M values (TPR=0.9, FPR=0.1)
print("\nExperiment 2: synthetic_type2_curve")
r_m_values = [0.01, 0.10, 0.20, 0.30]
type2_curve = {}
for r_m in r_m_values:
    t2_n = 0
    for trial in range(N_TRIALS):
        seed = 42 + trial * 3 + int(r_m * 100) + 10000
        D_M_sm, D_M_sj, D_J_sm, D_J_sj = generate_synthetic_data(N_M, N_J, r_m, TPR, FPR, seed=seed)
        rn, _ = noisy_hypothesis_test_dual(D_M_sm, D_M_sj, D_J_sj, ALPHA, ZETA)
        t2_n += int(not rn)
    val = t2_n / N_TRIALS
    type2_curve[f"rm_{r_m:.2f}"] = val
    print(f"  R_M={r_m:.2f}: Noisy HT Type-II={val:.3f}")

# === Experiment 3: oracle_gap ===
# Oracle gap between Noisy HT (estimated TPR/FPR) and Oracle HT (known TPR/FPR)
print("\nExperiment 3: oracle_gap")
oracle_gap_val = t2_noisy - t2_oracle
print(f"  Oracle gap = {oracle_gap_val:.3f}")

# === Write scores.json ===
scores = {
    "synthetic_power_comparison": {
        "direct_ht": {"type2_error": round(t2_direct, 4)},
        "noisy_ht": {"type2_error": round(t2_noisy, 4)},
        "oracle_noisy_ht": {"type2_error": round(t2_oracle, 4)}
    },
    "oracle_gap": {
        "oracle_noisy_ht": {"type2_error_oracle": round(t2_oracle, 4), "oracle_gap": round(oracle_gap_val, 4)},
        "noisy_ht": {"type2_error_noisy": round(t2_noisy, 4), "oracle_gap": round(oracle_gap_val, 4)}
    },
    "synthetic_type2_curve": {
        k: {"type2_error": round(v, 4)} for k, v in type2_curve.items()
    },
    "synthetic_type1_control": {
        "direct_ht": {"type1_error": round(t1_direct, 4)},
        "noisy_ht": {"type1_error": round(t1_noisy, 4)},
        "oracle_noisy_ht": {"type1_error": round(t1_oracle, 4)}
    }
}

os.makedirs('scoring', exist_ok=True)
with open('scoring/scores.json', 'w') as f:
    json.dump(scores, f, indent=2)

print("\nScores written to scoring/scores.json")

# === Verify core claim ===
print("\n=== Core Claim Verification ===")
print(f"Noisy HT Type-II ({t2_noisy:.3f}) < Direct HT Type-II ({t2_direct:.3f}): {t2_noisy < t2_direct}")
if t2_noisy < t2_direct:
    print(f"CLAIM SUPPORTED: {abs(t2_direct - t2_noisy)*100:.1f}pp reduction in Type-II error")
else:
    print("CLAIM NOT SUPPORTED")
print(f"Type-I control: Noisy={t1_noisy:.3f} (target ~{ZETA})")
PYEOF

echo ""
echo "=== Running validation ==="
/usr/bin/python3 /home/user/validate.py --compare

echo ""
echo "=== Done ==="
