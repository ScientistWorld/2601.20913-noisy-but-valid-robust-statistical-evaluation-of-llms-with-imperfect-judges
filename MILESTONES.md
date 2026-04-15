# Reproduction Milestones

**Current: core_claim**

## Progress Log

### [2026-04-15 16:10] - method_runs
- Implemented the paper's Direct HT, Noisy HT, Oracle Noisy HT, and PPI-family hypothesis-test procedures.
- Verified the end-to-end synthetic Monte Carlo pipeline in a CPU test job.

### [2026-04-15 16:10] - core_claim
- Ran the main synthetic setting with `alpha=0.25`, `zeta=0.05`, `n_M=100`, `n_J=10000`, `R_M=0.20`, `TPR=0.9`, and `FPR=0.1`.
- Reproduced the central qualitative claim: Noisy HT had lower Type-II error than Direct HT while Type-I error stayed near the configured significance level.
- Confirmed the oracle bound behavior: Oracle Noisy HT outperformed practical Noisy HT.
