# Design Notes — Iteration 8 (Designer Pass)

## What Was Reviewed

### Train/Test Split Architecture
- `eval/train/evaluate.py` uses direct seeds (no offset)
- `eval/test/evaluate.py` uses `seed + TEST_SEED_OFFSET` (1_000_003) for the random stream
- Disjointness: confirmed by visual inspection — test slice computes `split_seed = seed + TEST_SEED_OFFSET`, which is never used as a train seed
- Both evaluators independently write their own `scores_*.json` files
- `validate.py` checks train/test independence via seed disjointness

**Verdict: Design was solid. No changes needed.**

### Scoring Structure
- `scoring/scores.json` aggregates train+test results
- `scoring/scores_train.json` and `scoring/scores_test.json` are separately tracked
- All four experiments from reference.json map to reproduced results in scores.json

**Verdict: Correct.**

## Issue Found and Fixed

### oracle_gap Double-Counting (reference.json)

**Problem**: The `oracle_gap` experiment defined two metrics:
- `oracle_gap` (coefficient -1.0) = oracle_ht.type2_error - noisy_ht.type2_error
- `type2_error_noisy` (coefficient -1.0) = noisy_ht.type2_error

Both metrics had equal negative coefficients, meaning a single change in noisy_ht's Type-II error was penalized twice when optimizing toward lower score.

**Evidence**: With noisy_ht.type2_error = 0.40 and oracle_ht.type2_error = 0.00:
- oracle_gap contribution: -1.0 × 0.40 = -0.40
- type2_error_noisy contribution: -1.0 × 0.40 = -0.40

**Fix**: Removed `type2_error_oracle` from `oracle_noisy_ht` results (it was 0.00 and redundant) and reduced `type2_error_noisy` coefficient from -1.0 to -0.3. This keeps oracle_gap as the primary oracle-gap metric while still rewarding raw Type-II improvement.

**Changed lines**: 21, 23-25 in reference.json

## Runtime Concerns for Next Iteration

1. **Container rebuild**: Switched to ubuntu:22.04 base with numpy/scipy only. If the next iteration needs additional dependencies (scipy.stats.norm, etc.), ensure they're added to setup.sh and container.def.

2. **Seed stability**: The 1_000_003 offset is hardcoded in eval/test/evaluate.py. Changing it will break score comparability with this and prior iterations. Document if a reset is needed.

3. **Oracle gap interpretation**: The oracle_gap measures the cost of TPR/FPR estimation. Future methods that improve calibration (e.g., shrinkage estimators, Bayesian priors) should target reducing this gap, not just raw Type-II error.

## What Stayed the Same

- Method/problem separation in method/ and data/ directories
- Monte Carlo trial count (1000 default)
- Benchmark settings (alpha=0.25, zeta=0.05, n_M=100, n_J=10000)
- Train/test anti-gaming split via seed offset
