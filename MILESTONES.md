# Reproduction Milestones

**Current: core_claim_plus**

## Progress Log

### [2026-05-22 07:01] - core_claim_plus
- Audited the existing `core_claim_plus` reproduction after reactivation.
- Fixed the canonical evaluator to include the `synthetic_type2_curve` primary `decision_error` metric in `scoring/scores.json`, matching `reference.json` and the existing train/test evaluators.
- Local `bash scripts/evaluate.sh /home/user/outputs/synthetic_results.json /home/user/scoring/scores.json` passed `validate.py --compare`.
- Aligned the core synthetic setting with the paper's high-quality judge panel (`TPR=0.95`, `FPR=0.05`) and added artifact-config validation so the evaluator rejects changed sample budgets or incomplete trial grids.
- Submitted a CPU test job to rerun canonical, train, and held-out scoring inside the packaged container after these evaluator and setting cleanups.

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
- Completed at milestone `core_claim_plus`.
