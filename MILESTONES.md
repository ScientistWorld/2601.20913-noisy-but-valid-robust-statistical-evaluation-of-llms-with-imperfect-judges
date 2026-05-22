# Reproduction Milestones

**Current: core_claim**

## Progress Log

### [2026-05-22 06:29] - core_claim_plus
- Packaged the paper's Noisy Hypothesis Testing procedure, Direct HT baseline, Oracle Noisy HT upper bound, and PPI diagnostics.
- Verified the artifact-based evaluator reads method outputs rather than regenerating the experiment internally.
- Reproduced the synthetic core claim on canonical and held-out slices: Noisy HT has lower Type-II error than Direct HT while Type-I error remains controlled near `zeta = 0.05`.
- Ran `python validate.py --compare`; all scoring, import-separation, artifact-reading, and train/test checks passed.

### [2026-05-22 06:35] - core_claim
- Continued audit from the reset `core_claim` milestone.
- Confirmed the implementation is the paper's actual Noisy HT procedure, not a surrogate: calibration estimates TPR/FPR, transforms `alpha`, and applies the variance-corrected rejection threshold on separate judge-labeled evaluation data.
- Confirmed `scripts/evaluate.sh` works standalone and `python validate.py --compare` passes.
- Fixed an unused legacy `noisy_hypothesis_test` helper so its public signature now requires separate calibration and evaluation judge labels, matching Algorithm 1.
- Submitted a CPU test job to verify the cleanup inside the packaged runtime before restoring `core_claim_plus`.

## Stop Justification
- Pending CPU test verification after audit cleanup.
