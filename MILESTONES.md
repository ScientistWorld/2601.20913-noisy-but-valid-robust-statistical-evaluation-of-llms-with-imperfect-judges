# Reproduction Milestones

**Current: core_claim**

## Progress Log

### [2026-04-15 19:54] - core_claim
- Container built successfully (ubuntu:22.04 + numpy/scipy)
- Job 652fc088-2f2 completed (rc=0, CPU-only)
- Monte Carlo (1000 trials): Noisy HT Type-II=0.627 < Direct HT Type-II=0.721 (9.4pp reduction)
- Type-I error controlled: Noisy=0.035, Direct=0.037, Oracle=0.044 (target ~0.05)
- All validation checks passed
- Core claim SUPPORTED: Noisy HT outperforms Direct HT when judge quality is high (TPR=0.9, FPR=0.1)

### [2026-04-15 19:50] - method_runs
- Fixed container.def: switched from nvidia/cuda to ubuntu:22.04 (no GPU needed)
- Reduced dependencies from 6 packages to 2 (numpy, scipy only)
- Fixed download.sh shared/ reference
- Method executes end-to-end: all hypothesis tests run correctly on synthetic data

### [2026-04-15 19:45] - none
- Previous agent left workspace with container build failures (10 attempts)
- Core algorithm already implemented correctly in method/core.py
- Fixed lower-tail test direction bugs, seed independence bug
