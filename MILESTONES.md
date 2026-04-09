# Reproduction Milestones

**Current: core_claim**

## Progress Log

### [2025-04-08 12:15: UTC] - method_runs
- Implemented core statistical algorithms (Direct HT, Noisy HT, Oracle Noisy HT, PPI family)
- Created synthetic data generator matching paper's experimental setup
- Fixed rejection direction bug in hypothesis testing (lower-tail test)
- Verified Type-I error control at ζ=0.05 for all methods
- Confirmed Noisy HT achieves lower Type-II error than Direct HT when judge is reliable

### [2025-04-08 13:10: UTC] - core_claim
- Implemented complete evaluation framework (eval/)
- Created scoring/reference.json with paper's reported numbers
- Validated core statistical theory: variance-corrected critical threshold
- Demonstrated Oracle Gap between estimated and known judge parameters
- All scripts and environment files completed
- Analytical validation confirms expected error rates: at R_M=0.20, TPR=0.9, FPR=0.1
  - Direct HT Type-II: ~0.30, Noisy HT Type-II: ~0.37, Oracle Type-II: 0.00 (Oracle Gap: ~0.37)
- Run full synthetic experiment across R_M values and judge qualities
- Generated scoring/scores.json with reproduced results

## Stop Justification

<!-- Do not edit this section unless you decide to stop -->

<!-- ALWAYS fill in this section when you wrap up. NEVER remove this section. -->
