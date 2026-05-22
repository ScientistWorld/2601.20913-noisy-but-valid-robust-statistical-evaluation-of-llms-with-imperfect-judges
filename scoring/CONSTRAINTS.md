# Scientist Constraints

## Problem Formulation

The scientist must keep the binary certification problem fixed: test `H0: R_M >= alpha` against `H1: R_M < alpha`, where `S_M=1` denotes a model failure and `S_J=1` denotes that an imperfect judge flags a failure. Changing the task to ordinary accuracy estimation, threshold tuning, or classifier training would sidestep the paper's claim.

## Evaluation Settings

The benchmark settings are fixed at `alpha=0.25`, `zeta=0.05`, `n_M=100`, `n_J=10000`, judge `TPR=0.95`, and judge `FPR=0.05` for the existing synthetic experiments unless a new experiment explicitly declares otherwise. Improvements must come from better statistical certification under the same sample budgets and judge-quality regime, not from simply collecting more human labels, more judge labels, or easier judge outputs.

## Data-Generating Process

Synthetic trials must use the Bernoulli failure model and TPR/FPR judge-noise model described in the paper. The existing curve settings are `R_M in {0.01, 0.10, 0.20, 0.30}` with the same fixed threshold and judge parameters above. A scientist may add additional synthetic regimes, but the existing regimes must remain unchanged so scores stay comparable.

## Validity Requirement

Any improved method must report Type-I error on the null boundary. Lower Type-II error is not acceptable if Type-I error exceeds the configured significance level by ignoring the safety constraint.

## Compliance Checklist

- [ ] Uses the same binary failure-label certification problem.
- [ ] Keeps `alpha=0.25`, `zeta=0.05`, `n_M=100`, `n_J=10000`, `TPR=0.95`, and `FPR=0.05` for the existing synthetic benchmark.
- [ ] Uses the same Bernoulli/TPR/FPR synthetic data generator for existing experiments.
- [ ] Reports both benefit metrics (`type2_error`) and validity metrics (`type1_error`).
- [ ] Does not improve scores by increasing calibration or judge sample sizes in the fixed benchmark.
