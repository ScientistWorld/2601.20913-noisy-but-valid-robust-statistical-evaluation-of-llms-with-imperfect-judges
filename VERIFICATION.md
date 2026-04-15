# Verification Report

## Initial Assessment

The workspace already contained a working `core_claim_plus` reproduction of the paper's synthetic certification experiments. Prior CPU jobs had produced `scoring/scores.json`, `scoring/scores_train.json`, and `scoring/scores_test.json`, with the reproduced method improving Type-II error over the small-label baseline while keeping Type-I error below the configured significance level.

## Issues Found

- Minor: `briefing/evaluation.md` named the paper's specific procedures in a method-agnostic file, which leaked solution details to from-scratch scientists.
- Minor: the reusable synthetic data distribution was defined inside `method/` and duplicated in evaluators instead of living under `data/`.
- Minor: `environment/container.def` installed Python packages during the container build rather than keeping Python dependency installation in `environment/setup.sh`.

## Fixes Applied

- Rewrote the method-agnostic evaluation briefing to describe metrics, data budgets, and expected statistical behavior without naming the paper's implementation.
- Added `data/synthetic.py` and updated evaluation and method helpers to use that shared generator without importing from `method/`.
- Updated `scripts/download.sh` to point at the data-owned generator and confirmed no external downloads are required.
- Moved Python package installation out of `environment/container.def` and into `environment/setup.sh`.

## Final Judgment

The workspace is ready to serve as a research gym for the reproduced synthetic certification subset. Improve-mode agents can run and modify the packaged method, while from-scratch agents can use the problem definition, data generator, evaluation scripts, constraints, and scoring files without needing the method implementation.

- Milestone: core_claim_plus
- Ready for gym use: yes
- Confidence: medium
- Key limitation: the gym reproduces the synthetic experiments and train/test slices, not the paper's full real-dataset evaluation suite.
