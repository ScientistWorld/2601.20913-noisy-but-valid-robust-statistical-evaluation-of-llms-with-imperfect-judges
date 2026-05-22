# Progress: Noisy HT Paper Reproduction

## Paper
"Noisy but Valid: Robust Statistical Evaluation of LLMs with Imperfect Judges" (arXiv 2601.20913)

## What Works
- All four hypothesis testing algorithms implemented in `method/core.py`:
  - Direct HT (baseline)
  - Noisy HT (proposed method)
  - Oracle Noisy HT (upper bound)
  - PPI Family Wald Test
- Synthetic data generation in `data/synthetic.py`
- Monte Carlo method-artifact pipeline in `method/run_synthetic.py`, `scripts/run.sh`, `scripts/method.sh`, and `scripts/evaluate.sh`
- The reusable evaluator is independent from `method/`; it now reads method-produced artifacts instead of regenerating the experiment internally.
- Container builds with minimal ubuntu:22.04 base (no GPU needed)
- Scoring documentation now defines the optimization target, validity constraint, oracle-gap diagnostic, and scientist constraints for future benchmark users.
- The canonical evaluator can emit unscored diagnostics under `_diagnostics` when scores are regenerated, covering the paper's PPI/Oracle ordering and the high-FPR stress setting from Appendix H. These diagnostics do not affect the benchmark score, but they expose additional paper-aligned behavior for future agents.

## Results Achieved

### Experiment 1: synthetic_power_comparison (R_M=0.20, TPR=0.9, FPR=0.1)
| Method | Type-II Error | Type |
|--------|--------------|------|
| Direct HT | 0.721 | baseline |
| Noisy HT | 0.627 | proposed |
| Oracle HT | 0.000 | proposed |

**Core claim SUPPORTED**: Noisy HT (0.627) < Direct HT (0.721), 9.4pp reduction in Type-II error.

### Experiment 2: oracle_gap
Oracle gap = 0.627 (performance loss from estimating TPR/FPR vs knowing them)

### Experiment 3: synthetic_type2_curve
| R_M | Noisy HT Type-II |
|-----|-----------------|
| 0.01 | 0.423 |
| 0.10 | 0.075 |
| 0.20 | 0.623 |
| 0.30 | 0.999 |

### Experiment 4: synthetic_type1_control
| Method | Type-I Error |
|--------|------------|
| Direct HT | 0.037 |
| Noisy HT | 0.028 |
| Oracle HT | 0.038 |

All methods maintain Type-I error near the target zeta=0.05.

## Deviations from Paper
- Reference values in reference.json may not exactly match paper's reported values
  because most paper results are plotted in figures rather than tabulated.
- Our implementation reproduces the correct qualitative behavior and relative ordering
- Current scored reproduction focuses on the synthetic setting. The paper also evaluates Jigsaw, Hate Speech Offensive, and SafeRLHF with LLM classifiers/judges; those real-data experiments are not implemented in this workspace because they require running multiple local LLMs and downloading larger public datasets/models.

## What Remains
- Could increase MC trials (2000-5000) for more stable estimates
- Could add scored experiments with additional judge quality settings (TPR=0.8, TPR=0.7) if reliable paper-figure reference values are extracted.
- Could implement classification experiments on real datasets (if data available)
- CPU test job `8696ad73-c65` reran the packaged standalone scoring pipeline successfully and restored the reproduction to `core_claim_plus`.
- CPU test job `ebfc56ce-83e` reran independent train/test slices successfully:
  - Train: Direct Type-II `0.721`, Noisy Type-II `0.627`, Oracle Type-II `0.000`; Direct/Noisy/Oracle Type-I `0.037`/`0.028`/`0.038`.
  - Held-out test: Direct Type-II `0.732`, Noisy Type-II `0.628`, Oracle Type-II `0.000`; Direct/Noisy/Oracle Type-I `0.042`/`0.039`/`0.049`.
  - `validate.py` passed inside the compute container with scoring, import-separation, train/test independence, and shared-path checks.

## Issues Encountered
- Previous agent had 10 container build failures due to heavy nvidia/cuda base image
- Fixed by switching to minimal ubuntu:22.04 base with only numpy/scipy
- Final environment cleanup moved `numpy` and `scipy` to Ubuntu `apt` packages and made `environment/setup.sh` a no-op, which restored reliable job submission.
- Previous agent had lower-tail test direction bugs (fixed in prior session)
- Previous agent had seed independence bug in evaluate.py (fixed in prior session)
- Continuation audit found that `scripts/evaluate.sh` and `scripts/run.sh` imported directly from `method/`, violating the gym separation rule. Fixed by moving the standalone scoring procedure into `eval/evaluate.py` and making scripts call that entry point.
- The fixed evaluator was validated inside the compute container; `validate.py --compare` passed, including import-separation checks.
- Continuation audit on 2026-05-22 found the evaluator still regenerated synthetic trials internally, so future `method/` edits would not necessarily affect scores. Fixed by making `method/run_synthetic.py` produce trial artifacts and making `eval/evaluate.py` aggregate those artifacts only.
- The prior oracle-gap score incorrectly assigned the practical gap to the oracle row. Fixed the metric so Oracle Noisy HT has `oracle_gap=0.0` and Noisy HT reports its Type-II gap to oracle.
- Continuation handoff on 2026-05-22 06:26 confirmed the corrected artifact-based pipeline needs a fresh compute-container run. Submitted a CPU test job to regenerate canonical/train/test artifacts and validate the evaluator contract.

## April 24 Final Baseline Refresh
- CPU job `8f4134be-d14` reran the split evaluation after the environment cleanup and produced valid `scoring/scores_train.json` and `scoring/scores_test.json`.
- Train slice preserved the core claim: Direct/Noisy/Oracle Type-II `0.721`/`0.627`/`0.000`; Direct/Noisy/Oracle Type-I `0.037`/`0.028`/`0.038`.
- Held-out test slice preserved the core claim: Direct/Noisy/Oracle Type-II `0.732`/`0.628`/`0.000`; Direct/Noisy/Oracle Type-I `0.042`/`0.039`/`0.049`.
- The split is usable as a gym baseline because the train/test outputs are complete, method keys match exactly, and the slices are not byte-identical.
