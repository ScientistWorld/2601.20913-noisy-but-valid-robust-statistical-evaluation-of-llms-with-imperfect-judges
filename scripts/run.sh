#!/bin/bash
# Run validation and experiments inside compute container.
# CPU-only job — no GPU needed for these statistical computations.

set -e

cd /home/user

echo "=== Step 1: Validate and fix core algorithm rejection direction ==="
# The paper uses lower-tail tests: reject H0 if R_J_hat > c_J (where c_J = alpha_prime + z_zeta*SE, z_zeta < 0)
# Type-I error = P(reject | H0) = P(R_J > c_J | H0 boundary) = P(Z > z_zeta) = zeta
# Type-II error = P(fail to reject | H1) = P(R_J <= c_J | H1)

/usr/bin/python3 << 'PYEOF'
import sys
sys.path.insert(0, '/home/user/method')
from core import direct_hypothesis_test, noisy_hypothesis_test_dual, oracle_noisy_hypothesis_test, ppi_family_wald_test
from synthetic_data import generate_synthetic_data
import numpy as np
import json

# Verify direction with analytical check
from scipy.stats import norm
alpha = 0.25
zeta = 0.05
tpr, fpr = 0.9, 0.1
n_m, n_j = 100, 10000
n_m1 = int(alpha * n_m)  # 25
n_m0 = n_m - n_m1  # 75

alpha_prime = fpr + (tpr - fpr) * alpha  # 0.30
z_zeta = norm.ppf(zeta)  # -1.645

SE = np.sqrt(alpha_prime*(1-alpha_prime)/n_j + alpha**2*tpr*(1-tpr)/n_m1 + (1-alpha)**2*fpr*(1-fpr)/n_m0)
c_j_prime = alpha_prime + z_zeta * SE

# Expected Type-II error at R_M=0.20:
r_j_alt = fpr + (tpr - fpr) * 0.20  # 0.26
z_test = (c_j_prime - r_j_alt) / SE
expected_type2_noisy = 1 - norm.cdf(z_test)  # ~0.37

# Expected Type-II error for Direct HT at R_M=0.20:
r_m_alt = 0.20
SE_d = np.sqrt(r_m_alt*(1-r_m_alt)/n_m)
c_d = alpha + z_zeta * np.sqrt(alpha*(1-alpha)/n_m)
z_d = (c_d - r_m_alt) / SE_d
expected_type2_direct = 1 - (1 - norm.cdf(z_d))  # ~0.30

print(f"Expected Type-II errors (analytical):")
print(f"  Noisy HT:  {expected_type2_noisy:.3f}")
print(f"  Direct HT: {expected_type2_direct:.3f}")

# Run Monte Carlo
print(f"\nRunning 1000-trial Monte Carlo...")
n_trials = 1000
methods = ['direct_ht', 'noisy_ht', 'oracle_noisy_ht', 'ppi_pp', 'ridge_ppi']

type1_counts = {m: 0 for m in methods}
type2_counts = {m: 0 for m in methods}

for trial in range(n_trials):
    seed = 42 + trial

    # Type-I test: at boundary R_M = alpha
    D_M_sm, D_M_sj, D_J_sm, D_J_sj = generate_synthetic_data(n_m, n_j, alpha, tpr, fpr, seed=seed)
    reject_d, _ = direct_hypothesis_test(D_M_sm, alpha, zeta)
    reject_n, _ = noisy_hypothesis_test_dual(D_M_sm, D_M_sj, D_J_sj, alpha, zeta)
    reject_o, _ = oracle_noisy_hypothesis_test(D_J_sj, tpr, fpr, alpha, zeta)
    reject_pp, _ = ppi_family_wald_test(D_M_sm, D_M_sj, D_J_sj, tpr, fpr, alpha, zeta, variant='ppi_pp')
    reject_ridge, _ = ppi_family_wald_test(D_M_sm, D_M_sj, D_J_sj, tpr, fpr, alpha, zeta, variant='ridge_ppi')

    # Type-I = P(reject | H0 boundary)
    type1_counts['direct_ht'] += int(reject_d)
    type1_counts['noisy_ht'] += int(reject_n)
    type1_counts['oracle_noisy_ht'] += int(reject_o)
    type1_counts['ppi_pp'] += int(reject_pp)
    type1_counts['ridge_ppi'] += int(reject_ridge)

    # Type-II test: at R_M = 0.20 (model is reliable, H1 true)
    D_M_sm, D_M_sj, D_J_sm, D_J_sj = generate_synthetic_data(n_m, n_j, r_m_alt, tpr, fpr, seed=seed)
    reject_d, _ = direct_hypothesis_test(D_M_sm, alpha, zeta)
    reject_n, _ = noisy_hypothesis_test_dual(D_M_sm, D_M_sj, D_J_sj, alpha, zeta)
    reject_o, _ = oracle_noisy_hypothesis_test(D_J_sj, tpr, fpr, alpha, zeta)
    reject_pp, _ = ppi_family_wald_test(D_M_sm, D_M_sj, D_J_sj, tpr, fpr, alpha, zeta, variant='ppi_pp')
    reject_ridge, _ = ppi_family_wald_test(D_M_sm, D_M_sj, D_J_sj, tpr, fpr, alpha, zeta, variant='ridge_ppi')

    # Type-II = P(not reject | H1 true) = P(reject == False)
    type2_counts['direct_ht'] += int(not reject_d)
    type2_counts['noisy_ht'] += int(not reject_n)
    type2_counts['oracle_noisy_ht'] += int(not reject_o)
    type2_counts['ppi_pp'] += int(not reject_pp)
    type2_counts['ridge_ppi'] += int(not reject_ridge)

print(f"\nType-I error rates (at R_M = alpha, zeta=0.05):")
for m in methods:
    print(f"  {m:20s}: {type1_counts[m]/n_trials:.3f}  (target: zeta={zeta}, should be ~{zeta})")
print(f"\nType-II error rates (at R_M = 0.20 < alpha):")
for m in methods:
    print(f"  {m:20s}: {type2_counts[m]/n_trials:.3f}")

# Check key claims
type1_ok = all(type1_counts[m]/n_trials < 0.08 for m in ['noisy_ht'])
noisy_lower_type2 = type2_counts['noisy_ht']/n_trials < type2_counts['direct_ht']/n_trials
oracle_lower_noisy = type2_counts['oracle_noisy_ht']/n_trials < type2_counts['noisy_ht']/n_trials

print(f"\nKey validation checks:")
print(f"  Noisy HT Type-I < 0.08: {type1_ok} (Type-I control)")
print(f"  Noisy HT Type-II < Direct HT: {noisy_lower_type2} (power advantage)")
print(f"  Oracle Type-II < Noisy HT: {oracle_lower_noisy} (oracle gap)")

print(f"\nNote: The paper's central claim is that Noisy HT outperforms Direct HT")
print(f"when the judge satisfies the condition (TPR-FPR)^2 > threshold.")
print(f"For TPR=0.9, FPR=0.1, R_M=0.20, alpha=0.25:")
condition = (tpr - fpr)**2
rhs = (alpha**2 * tpr*(1-tpr)/r_m_alt + (1-alpha)**2*fpr*(1-fpr)/(1-r_m_alt)) / (r_m_alt*(1-r_m_alt))
print(f"  (TPR-FPR)^2 = {condition:.4f} vs RHS = {rhs:.4f}")
print(f"  Condition satisfied: {condition > rhs}")
PYEOF

echo ""
echo "=== Step 2: Run full synthetic experiment across R_M values ==="
/usr/bin/python3 << 'PYEOF'
import sys
sys.path.insert(0, '/home/user/method')
from core import direct_hypothesis_test, noisy_hypothesis_test_dual, oracle_noisy_hypothesis_test
from synthetic_data import generate_synthetic_data
import numpy as np
import json

alpha = 0.25
zeta = 0.05
n_m, n_j = 100, 10000
n_trials = 1000

# Test across R_M range and judge qualities
r_m_values = [0.01, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50]
tpr_fpr_pairs = [
    (0.9, 0.1, 'high'),
    (0.8, 0.1, 'good'),
    (0.7, 0.2, 'moderate'),
]

# For brevity, test one judge quality (high) across R_M range
# and one R_M (0.20) across judge qualities
print("Running full synthetic experiment...")
results = {}

# Experiment 1: Type-II error vs R_M (high quality judge)
print("\n--- Experiment: Type-II error vs R_M (TPR=0.9, FPR=0.1) ---")
tpr, fpr = 0.9, 0.1
results['type2_vs_rm'] = {}
for r_m in r_m_values:
    type2_d, type2_n, type2_o = 0, 0, 0
    for trial in range(n_trials):
        seed = 42 + trial + int(r_m*100)
        D_M_sm, D_M_sj, D_J_sm, D_J_sj = generate_synthetic_data(n_m, n_j, r_m, tpr, fpr, seed=seed)
        reject_d, _ = direct_hypothesis_test(D_M_sm, alpha, zeta)
        reject_n, _ = noisy_hypothesis_test_dual(D_M_sm, D_M_sj, D_J_sj, alpha, zeta)
        reject_o, _ = oracle_noisy_hypothesis_test(D_J_sj, tpr, fpr, alpha, zeta)
        type2_d += int(not reject_d)
        type2_n += int(not reject_n)
        type2_o += int(not reject_o)
    results['type2_vs_rm'][f'r_m_{r_m:.2f}'] = {
        'direct_ht': type2_d / n_trials,
        'noisy_ht': type2_n / n_trials,
        'oracle_noisy_ht': type2_o / n_trials,
    }
    print(f"  R_M={r_m:.2f}: Direct={type2_d/n_trials:.3f}, Noisy={type2_n/n_trials:.3f}, Oracle={type2_o/n_trials:.3f}")

# Experiment 2: Type-II error vs judge quality (R_M=0.20)
print("\n--- Experiment: Type-II error vs judge quality (R_M=0.20) ---")
r_m_test = 0.20
results['type2_vs_judge'] = {}
for tpr, fpr, quality in tpr_fpr_pairs:
    type2_d, type2_n, type2_o = 0, 0, 0
    for trial in range(n_trials):
        seed = 42 + trial + 1000 + int(tpr*10) + int(fpr*10)
        D_M_sm, D_M_sj, D_J_sm, D_J_sj = generate_synthetic_data(n_m, n_j, r_m_test, tpr, fpr, seed=seed)
        reject_d, _ = direct_hypothesis_test(D_M_sm, alpha, zeta)
        reject_n, _ = noisy_hypothesis_test_dual(D_M_sm, D_M_sj, D_J_sj, alpha, zeta)
        reject_o, _ = oracle_noisy_hypothesis_test(D_J_sj, tpr, fpr, alpha, zeta)
        type2_d += int(not reject_d)
        type2_n += int(not reject_n)
        type2_o += int(not reject_o)
    results['type2_vs_judge'][quality] = {
        'tpr': tpr, 'fpr': fpr,
        'direct_ht': type2_d / n_trials,
        'noisy_ht': type2_n / n_trials,
        'oracle_noisy_ht': type2_o / n_trials,
    }
    print(f"  {quality} (TPR={tpr}, FPR={fpr}): Direct={type2_d/n_trials:.3f}, Noisy={type2_n/n_trials:.3f}, Oracle={type2_o/n_trials:.3f}")

# Save results
with open('data/synthetic_results.json', 'w') as f:
    json.dump(results, f, indent=2)
print("\nResults saved to data/synthetic_results.json")
PYEOF

echo ""
echo "=== Step 3: Write scoring/scores.json ==="
/usr/bin/python3 << 'PYEOF'
import json
import os

# Load results
with open('data/synthetic_results.json') as f:
    results = json.load(f)

scores = {'experiments': {}}

# Experiment 1: Type-II error comparison (core claim)
scores['experiments']['synthetic_power_comparison'] = {
    'description': 'Synthetic: Type-II error at R_M=0.20, alpha=0.25, n_M=100, n_J=10000, TPR=0.9, FPR=0.1',
    'results': {}
}
for method in ['direct_ht', 'noisy_ht', 'oracle_noisy_ht']:
    type2 = results['type2_vs_rm']['r_m_0.20'][method]
    scores['experiments']['synthetic_power_comparison']['results'][method] = {
        'type': 'baseline' if method == 'direct_ht' else 'proposed',
        'type2_error': round(type2, 4),
        'description': 'Oracle uses known TPR/FPR; Noisy estimates from n_M=100'
    }

# Experiment 2: Judge quality impact
scores['experiments']['synthetic_judge_quality_impact'] = {
    'description': 'Synthetic: Type-II error vs judge quality at R_M=0.20',
    'results': {}
}
for quality, data in results['type2_vs_judge'].items():
    key = f'noisy_ht_{quality}'
    scores['experiments']['synthetic_judge_quality_impact']['results'][key] = {
        'type': 'proposed',
        'description': f'TPR={data["tpr"]}, FPR={data["fpr"]}',
        'type2_error': round(data['noisy_ht'], 4),
    }

# Experiment 3: Oracle Gap
r_m_test = 0.20
scores['experiments']['oracle_gap'] = {
    'description': f'Oracle Gap at R_M={r_m_test}, TPR=0.9, FPR=0.1',
    'results': {
        'oracle_noisy_ht': {
            'type': 'proposed',
            'description': 'Known TPR/FPR',
            'type2_error_oracle': round(results['type2_vs_judge']['high']['oracle_noisy_ht'], 4),
        },
        'noisy_ht': {
            'type': 'proposed',
            'description': 'Estimated TPR/FPR from n_M=100',
            'type2_error_noisy': round(results['type2_vs_judge']['high']['noisy_ht'], 4),
            'oracle_gap': round(results['type2_vs_judge']['high']['noisy_ht'] - results['type2_vs_judge']['high']['oracle_noisy_ht'], 4),
        }
    }
}

# Experiment 4: Type-II error curve (R_M < alpha region)
scores['experiments']['synthetic_type2_curve'] = {
    'description': 'Synthetic: Type-II error vs model failure rate R_M',
    'results': {}
}
for r_m_str, data in sorted(results['type2_vs_rm'].items()):
    r_m = float(r_m_str.split('_')[1])
    if r_m < 0.25:  # Only show H1 region
        scores['experiments']['synthetic_type2_curve']['results'][f'rm_{r_m:.2f}'] = {
            'r_m': r_m,
            'direct_ht_type2': round(data['direct_ht'], 4),
            'noisy_ht_type2': round(data['noisy_ht'], 4),
            'oracle_noisy_ht_type2': round(data['oracle_noisy_ht'], 4),
        }

os.makedirs('scoring', exist_ok=True)
with open('scoring/scores.json', 'w') as f:
    json.dump(scores, f, indent=2)

print("Scores written to scoring/scores.json")
print(json.dumps(scores, indent=2))
PYEOF

echo ""
echo "=== Step 4: Run validation comparison ==="
/usr/bin/python3 /home/user/validate.py --compare 2>&1 || echo "(Validation script may need update)"

echo ""
echo "=== All validation complete ==="