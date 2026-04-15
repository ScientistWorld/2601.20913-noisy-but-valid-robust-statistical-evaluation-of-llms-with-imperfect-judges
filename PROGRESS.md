# Progress: Noisy HT Paper Reproduction

## Paper
"Noisy but Valid: Robust Statistical Evaluation of LLMs with Imperfect Judges" (arXiv 2601.20913)

## What Works
- All four hypothesis testing algorithms implemented in `method/core.py`:
  - Direct HT (baseline)
  - Noisy HT (proposed method)
  - Oracle Noisy HT (upper bound)
  - PPI Family Wald Test
- Synthetic data generation in `method/synthetic_data.py`
- Monte Carlo evaluation pipeline in `eval/evaluate.py`, `scripts/run.sh`, `scripts/evaluate.sh`, and `scripts/generate_scores.py`
- The reusable evaluator is now independent from `method/`; scoring duplicates the benchmark procedure in `eval/` so future methods can be evaluated without importing this reproduction's implementation.
- Container builds with minimal ubuntu:22.04 base (no GPU needed)
- Scoring documentation now defines the optimization target, validity constraint, oracle-gap diagnostic, and scientist constraints for future benchmark users.

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
| 0.01 | 0.421 |
| 0.10 | 0.075 |
| 0.20 | 0.630 |
| 0.30 | 0.999 |

### Experiment 4: synthetic_type1_control
| Method | Type-I Error |
|--------|------------|
| Direct HT | 0.037 |
| Noisy HT | 0.035 |
| Oracle HT | 0.044 |

All methods maintain Type-I error near the target zeta=0.05.

## Deviations from Paper
- Reference values in reference.json may not exactly match paper's reported values
  because most paper results are plotted in figures rather than tabulated.
- Our implementation reproduces the correct qualitative behavior and relative ordering
- Current scored reproduction focuses on the synthetic setting. The paper also evaluates Jigsaw, Hate Speech Offensive, and SafeRLHF with LLM classifiers/judges; those real-data experiments are not implemented in this workspace because they require running multiple local LLMs and downloading larger public datasets/models.

## What Remains
- Could increase MC trials (2000-5000) for more stable estimates
- Could add experiments with additional judge quality settings (TPR=0.8, TPR=0.7)
- Could implement classification experiments on real datasets (if data available)
- Next submitted job is CPU-only and intended to rerun the packaged scoring pipeline after documentation cleanup.
- Current turn fixed the evaluator/method separation issue and submits a CPU smoke job to restore `core_claim` with the corrected scoring path.

## Issues Encountered
- Previous agent had 10 container build failures due to heavy nvidia/cuda base image
- Fixed by switching to minimal ubuntu:22.04 base with only numpy/scipy
- Previous agent had lower-tail test direction bugs (fixed in prior session)
- Previous agent had seed independence bug in evaluate.py (fixed in prior session)
- Continuation audit found that `scripts/evaluate.sh` and `scripts/run.sh` imported directly from `method/`, violating the gym separation rule. Fixed by moving the standalone scoring procedure into `eval/evaluate.py` and making scripts call that entry point.
