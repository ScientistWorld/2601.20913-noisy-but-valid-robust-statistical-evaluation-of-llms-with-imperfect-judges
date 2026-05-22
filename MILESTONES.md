# Reproduction Milestones

**Current: core_claim_plus**

## Progress Log

### [2026-05-22 06:29] - core_claim_plus
- Packaged the paper's Noisy Hypothesis Testing procedure, Direct HT baseline, Oracle Noisy HT upper bound, and PPI diagnostics.
- Verified the artifact-based evaluator reads method outputs rather than regenerating the experiment internally.
- Reproduced the synthetic core claim on canonical and held-out slices: Noisy HT has lower Type-II error than Direct HT while Type-I error remains controlled near `zeta = 0.05`.
- Ran `python validate.py --compare`; all scoring, import-separation, artifact-reading, and train/test checks passed.

## Stop Justification
- Completed at milestone `core_claim_plus`.
