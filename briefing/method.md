# Paper's Method

## Key Contribution

The paper introduces a **Noisy Hypothesis Testing (Noisy HT)** framework that certifies LLM failure rates using a large dataset labeled by an imperfect LLM-as-a-Judge, while providing finite-sample Type-I error control.

The key innovation is converting the original hypothesis test on the true failure rate R_M into an equivalent test on the noisy failure rate R_J, then using a small calibration set to estimate the judge's True Positive Rate (TPR) and False Positive Rate (FPR), and finally computing a **variance-corrected critical threshold** that accounts for both:
1. The variance of the noisy failure rate estimate from the large dataset
2. The variance of the TPR/FPR estimates from the small calibration set

## Approach

**Step 1: Hypothesis Reformulation**
Convert the test on R_M ≥ α to an equivalent test on R_J ≥ α', where α' = FPR + (TPR - FPR) × α. This follows from R_J = R_M × TPR + (1 - R_M) × FPR (law of total probability).

**Step 2: Judge Calibration**
Estimate TPR and FPR from the small human-labeled calibration set D_M augmented with judge predictions:
- TPR = P(judge flags incorrect | ground truth says incorrect)
- FPR = P(judge flags incorrect | ground truth says correct)
Compute α' estimate: α̂' = FPR̂ + (TPR̂ - FPR̂) × α

**Step 3: Variance-Corrected Hypothesis Test**
On the large judge-labeled dataset D_J:
1. Compute test statistic: R̂_J = (1/n_J) × Σ S_J_i
2. Compute critical threshold:
   c_J' = α̂' + z_ζ × √(α̂'(1-α̂')/n_J + α²×TPR̂(1-TPR̂)/n_M1 + (1-α)²×FPR̂(1-FPR̂)/n_M0)
   where z_ζ is the standard normal quantile, n_M1 = # ground-truth failures, n_M0 = # ground-truth successes
3. Decision: Reject H₀ if R̂_J < c_J', else accept H₀

The variance term includes contributions from both the large dataset (sampling variance) and the small calibration set (estimation variance of TPR/FPR).

## Main Claims

1. **Validity**: Type-I error is controlled at level ζ (finite-sample guarantee, up to O(1/√n) corrections)
2. **Superiority condition**: Noisy HT outperforms Direct HT when judge quality satisfies (TPR - FPR)² > [α²×TPR(1-TPR)/R_M + (1-α)²×FPR(1-FPR)/(1-R_M)] / [R_M(1-R_M)]
3. **Oracle Gap**: Noisy HT always has higher Type-II error than Oracle Noisy HT (gap quantifies cost of estimation)
4. **Interpretability**: TPR and FPR are explicit parameters — practitioners can diagnose judge quality and plan data collection
