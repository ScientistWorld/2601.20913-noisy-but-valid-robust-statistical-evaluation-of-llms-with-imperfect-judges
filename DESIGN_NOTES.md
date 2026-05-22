# Design Notes - Train/Test Evaluation Pass

## Checked

- Read `eval/train/evaluate.py` and `eval/test/evaluate.py` side by side.
- Checked `scripts/evaluate_train.sh` and `scripts/evaluate_test.sh` for copy/paste errors.
- Grepped for test-to-train imports, train/test cross-imports, hardcoded paper-agreement metric names, and stray `scores_train.json` / `scores_test.json` files.
- Reviewed `scoring/reference.json` against the target claim: lower Type-II error, finite-sample Type-I control, and the oracle calibration gap.

## Changed

- Fixed a held-out dependency leak: `eval/test/evaluate.py` no longer reads `scoring/scores_train.json` or filters its methods through visible train results. The test scorer is now self-contained and scores only the held-out artifact it is given.
- Updated `scripts/evaluate_test.sh` to stop passing `--train-scores`, matching the self-contained test evaluator.
- Added missing metric descriptions in `scoring/reference.json` for `type2_error` and `type1_error`. The metric definitions now all include `higher_is_better`, `coefficient`, and `description`.

## Static Checks

- `bash -n scripts/evaluate_train.sh` passed.
- `bash -n scripts/evaluate_test.sh` passed.
- No `scoring/scores_train.json` or `scoring/scores_test.json` stubs exist.
- Grep found no `eval/test` dependency on `scores_train`, `eval/train`, paper-agreement metric names, or `scoring/scores.json`.
- `jq` is not installed on this node, so JSON validity was checked by direct inspection only; the next runner should validate with the repository validator.

## Runtime Concerns for Next Iteration

- 2026-05-22 runner update: `scripts/run.sh` now regenerates train/test artifacts and invokes the split-specific `scripts/evaluate_train.sh` and `scripts/evaluate_test.sh`; the completed CPU job passed post-design validation.
- 2026-05-22 runtime metric fix: the original curve score treated the unsafe `rm_0.30` setting as if non-certification were bad. The split evaluators now report a threshold-aware `decision_error` primary metric for `synthetic_type2_curve`, while retaining the raw non-certification rate as zero-weight diagnostic `type2_error`.
- 2026-05-22 final runner check: job `8b240b1b-ee1` regenerated both split score files and passed `validate.py --post-design`. Train/test are close but distinct: Noisy HT Type-II is `0.627` train vs `0.628` test, Noisy HT Type-I is `0.028` train vs `0.039` test, and the largest curve primary-metric gap is `0.038` at `rm_0.01`.
- The split currently differs mainly by random seed while keeping the same synthetic regime (`tpr=0.9`, `fpr=0.1`, `alpha=0.25`, `n_m=100`, `n_j=10000`). That is calibrated for reproducibility but only moderately resistant to a method tuned to this single judge-quality regime. A stronger future design would add held-out judge-quality or calibration-size regimes if method artifact generation is allowed to change.
- The evaluator remains artifact-only, which is good for method independence, but it trusts the artifact fields. A future runner should ensure the method-generation step, not the evaluator, is responsible for producing honest held-out artifacts.
