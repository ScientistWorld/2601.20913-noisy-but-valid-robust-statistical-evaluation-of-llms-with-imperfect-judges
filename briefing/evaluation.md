# Evaluation

## Metrics

Evaluation is based on statistical hypothesis testing outcomes. The core question is: can we reject the null hypothesis that the LLM's true failure rate R_M ≥ α?

Two primary metrics are used:

1. **Type-I Error Rate**: The probability of incorrectly rejecting the null hypothesis when it is true (i.e., certifying an unsafe model as safe). This must be controlled below the significance level ζ (typically 0.05). Lower is better.

2. **Type-II Error Rate**: The probability of incorrectly failing to reject the null hypothesis when the alternative is true (i.e., rejecting a safe model). Lower is better.

For a certification framework, Type-I error control is mandatory (validity). Type-II error minimization is desirable (power).

## Baselines and Targets

Three hypothesis testing procedures are compared:

- **Direct HT**: Uses only the small human-labeled dataset D_M. Statistically valid but limited power due to small sample size. This is the baseline to beat.

- **Noisy HT (proposed)**: Uses both D_M (to estimate judge TPR/FPR) and D_J (large judge-labeled set) with variance-corrected threshold. Should outperform Direct HT when judge is reliable.

- **Oracle Noisy HT**: Theoretical upper bound — uses true (not estimated) judge TPR/FPR. Establishes the gap due to estimation uncertainty.

- **PPI variants** (Prediction-Powered Inference): Alternative approaches combining clean and noisy labels for variance reduction.

The paper reports Type-I and Type-II error rates across varying:
- Target thresholds α ∈ [0.01, 0.99]
- Judge qualities (TPR, FPR pairs)
- Model failure rates R_M
- Calibration set sizes n_M (e.g., 100)
- Judge-labeled set sizes n_J (e.g., 10,000)

Expected behaviors (from theory):
- Type-I error should be controlled below ζ=0.05 for all procedures
- Noisy HT should outperform Direct HT when (TPR - FPR)² > threshold (derived in paper)
- Oracle Noisy HT should always outperform Noisy HT (the "Oracle Gap")

## Evaluation Protocol

For the **synthetic setting**: Generate binary ground-truth labels from Bernoulli(R_M) and judge labels by flipping ground-truth with TPR/FPR probabilities. Run B=1000 independent trials, each time re-sampling datasets and re-running hypothesis tests. Estimate Type-I and Type-II error rates by counting rejections under null and alternative hypotheses respectively.

For **classification settings** (Jigsaw, Hate Speech): Use pre-existing labeled datasets. Treat the LLM classifier as the "model under certification" and another LLM as the "judge." Compute ground-truth correctness S_M = 1{classifier_label ≠ ground_truth} and judge correctness S_J = 1{judge_label ≠ classifier_label}. Split data into D_M and D_J. Run B=1000 trials.

For **generative settings** (SafeRLHF): Similar protocol but with safety classification of generated responses.

All experiments use significance level ζ=0.05.
