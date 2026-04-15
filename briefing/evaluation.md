# Evaluation

## Metrics

Evaluation is based on statistical hypothesis testing outcomes. The core question is: can we reject the null hypothesis that the LLM's true failure rate R_M ≥ α?

Two primary metrics are used:

1. **Type-I Error Rate**: The probability of incorrectly rejecting the null hypothesis when it is true (i.e., certifying an unsafe model as safe). This must be controlled below the significance level ζ (typically 0.05). Lower is better.

2. **Type-II Error Rate**: The probability of incorrectly failing to reject the null hypothesis when the alternative is true (i.e., rejecting a safe model). Lower is better.

For a certification framework, Type-I error control is mandatory (validity). Type-II error minimization is desirable (power).

## Evaluation Axes

The benchmark compares certification procedures under the same data budget:
a small set with ground-truth labels, a much larger set with auxiliary-judge
labels, a target failure threshold, and a required significance level.
Methods are scored by the rejection decisions they produce across repeated
trials. Comparison rows may include a small-label-only baseline and an
idealized reference that receives extra information about the judge; those rows
are included to calibrate difficulty, not to constrain future methods.

Reported error rates vary across:
- Target thresholds α ∈ [0.01, 0.99]
- Judge qualities (TPR, FPR pairs)
- Model failure rates R_M
- Calibration set sizes n_M (e.g., 100)
- Judge-labeled set sizes n_J (e.g., 10,000)

Expected behavior:
- Type-I error should be controlled below ζ=0.05 for valid procedures
- Type-II error should fall when the auxiliary judge is informative and many auxiliary labels are available
- The gap between feasible methods and the idealized reference estimates the cost of not knowing judge reliability exactly

## Evaluation Protocol

For the **synthetic setting**: Generate binary ground-truth labels from Bernoulli(R_M) and judge labels by flipping ground-truth with TPR/FPR probabilities. Run B=1000 independent trials, each time re-sampling datasets and re-running hypothesis tests. Estimate Type-I and Type-II error rates by counting rejections under null and alternative hypotheses respectively.

For **classification settings** (Jigsaw, Hate Speech): Use pre-existing labeled datasets. Treat the LLM classifier as the "model under certification" and another LLM as the "judge." Compute ground-truth correctness S_M = 1{classifier_label ≠ ground_truth} and judge correctness S_J = 1{judge_label ≠ classifier_label}. Split data into D_M and D_J. Run B=1000 trials.

For **generative settings** (SafeRLHF): Similar protocol but with safety classification of generated responses.

All experiments use significance level ζ=0.05.
