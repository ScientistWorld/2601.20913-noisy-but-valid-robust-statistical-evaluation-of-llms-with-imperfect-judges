# Reproduction Milestones

**Current: core_claim_plus**

## Progress Log

### [2026-05-22 06:40] - core_claim_plus
- CPU test job `9ace5902-843` completed successfully after the continuation audit cleanup.
- The job regenerated canonical, train, and held-out artifacts, scored them through `eval/evaluate.py`, and passed `validate.py --compare` inside the packaged container.
- Canonical Direct/Noisy/Oracle Type-II error remained `0.721`/`0.627`/`0.000`; Type-I error remained `0.037`/`0.028`/`0.038`.
- Held-out test Direct/Noisy/Oracle Type-II error was `0.732`/`0.628`/`0.000`; Type-I error was `0.042`/`0.039`/`0.049`.

### [2026-05-22 06:36] - core_claim_plus
- Confirmed the packaged CPU compute job `137b2a6c-ca0` completed successfully with `validate.py --compare`.
- The implementation runs the paper's actual Noisy HT procedure: calibration-set TPR/FPR estimation, transformed noisy threshold, and variance-corrected critical cutoff.
- Reproduced the core synthetic power claim: Direct/Noisy/Oracle Type-II error `0.721`/`0.627`/`0.000`, with Type-I errors `0.037`/`0.028`/`0.038`.
- Added additional coverage beyond the minimum through train/test slices and a synthetic Type-II curve over multiple true failure rates.

## Stop Justification
- Completed at milestone `core_claim_plus`. The reusable environment is packaged and compute-validated; remaining paper experiments require larger real LLM classification/generation runs and are documented as future extensions.
