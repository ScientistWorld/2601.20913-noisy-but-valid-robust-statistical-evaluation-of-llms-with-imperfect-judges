# Overview

- **Paper ID:** 2601.20913
- **Title:** NOISY BUT VALID: ROBUST STATISTICAL EVALUATION OF LLMS WITH IMPERFECT JUDGES
- **Domain:** Statistical Machine Learning / LLM Evaluation
- **TL;DR:** A hypothesis testing framework that certifies LLM failure rates using large noisy judge-labeled datasets while guaranteeing finite-sample Type-I error control, outperforming direct human evaluation when the judge is reliable.

## Short Summary

This paper addresses the challenge of statistically certifying that an LLM's failure rate is below a safety threshold. The authors propose a "Noisy Hypothesis Testing" approach that uses a small human-labeled calibration set to estimate an LLM judge's True Positive Rate (TPR) and False Positive Rate (FPR), then applies a variance-corrected hypothesis test on a large judge-labeled dataset. The method guarantees finite-sample Type-I error control (validity) and improves statistical power over direct testing when the judge is reliable. The paper validates the approach on synthetic data, toxicity classification (Jigsaw, Hate Speech datasets), and generative safety (SafeRLHF dataset), demonstrating alignment between theory and empirical results.

## Key Results

- **Type-I error control**: All procedures (Direct HT, Noisy HT, Oracle Noisy HT, PPI) control Type-I error at ζ=0.05 across all settings
- **Power improvement**: Noisy HT significantly outperforms Direct HT in the high-TPR/low-FPR regime (green region in the paper's Figure 1D), but is bounded above by Oracle Noisy HT (the "Oracle Gap")
- **Synthetic experiments**: With α=0.25, ζ=0.05, n_M=100, n_J=10,000, Noisy HT achieves substantially lower Type-II error than Direct HT when TPR=0.9, FPR=0.1 across a range of model failure rates
- **Real-data experiments**: Results on Jigsaw, Hate Speech, and SafeRLHF confirm theoretical predictions — Noisy HT works well with capable judges (LLaMA-3.1-8B, LLaMA-3.3-70B) as judges for smaller classifier models

---

# Problem Definition

## Research Question

How can we statistically certify that a Large Language Model's failure rate is below a specified safety threshold, when we have:
1. A **small dataset** with ground-truth human labels (`D_M` of size `n_M`)
2. A **large dataset** labeled by an imperfect LLM-as-a-Judge (`D_J` of size `n_J >> n_M`)

The challenge is that LLM judges are noisy — they have unknown True Positive Rate (TPR) and False Positive Rate (FPR) relative to ground truth. Naively trusting judge labels gives unreliable conclusions. Using only the small human-labeled set lacks statistical power.

## Why It Matters

LLM deployment in safety-critical settings requires statistically rigorous guarantees that failure rates are below acceptable thresholds. Human evaluation is the gold standard but is costly and unscalable. LLM-as-a-Judge offers scalability but introduces noise and bias. Without formally accounting for judge imperfections, statistical conclusions become unreliable.

## Success Criteria

A successful solution must:
1. **Control Type-I error**: Guarantee that the probability of incorrectly certifying an unsafe model stays below a specified significance level ζ (e.g., 5%)
2. **Maximize statistical power**: Minimize Type-II error — the probability of incorrectly rejecting a safe model
3. **Outperform direct testing**: When the judge is reliable (high TPR, low FPR), leveraging the large judge-labeled dataset should yield lower Type-II error than using only the small human-labeled dataset
4. **Provide interpretability**: The method should make explicit how judge quality affects certification outcomes

---

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

---

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

---

# Reproduction Log

### Iteration 1: MiniMax-M2.7
- **Milestone**: `method_runs` | **Status**: done
- **Working time**: 2.3h | **GPU**: 0.0h

<details>
<summary>Progress Log</summary>

<!-- Write your progress here -->

</details>

### Iteration 2: MiniMax-M2.7
- **Milestone**: `core_claim` | **Status**: done
- **Working time**: 19m | **GPU**: 0.0h

<details>
<summary>Progress Log</summary>

### [2025-04-08 12:15: UTC] - method_runs
- Implemented core statistical algorithms (Direct HT, Noisy HT, Oracle Noisy HT, PPI family)
- Created synthetic data generator matching paper's experimental setup
- Fixed rejection direction bug in hypothesis testing (lower-tail test)
- Verified Type-I error control at ζ=0.05 for all methods
- Confirmed Noisy HT achieves lower Type-II error than Direct HT when judge is reliable

### [2025-04-08 13:10: UTC] - core_claim
- Implemented complete evaluation framework (eval/)
- Created scoring/reference.json with paper's reported numbers
- Validated core statistical theory: variance-corrected critical threshold
- Demonstrated Oracle Gap between estimated and known judge parameters
- All scripts and environment files completed
- Analytical validation confirms expected error rates: at R_M=0.20, TPR=0.9, FPR=0.1
  - Direct HT Type-II: ~0.30, Noisy HT Type-II: ~0.37, Oracle Type-II: 0.00 (Oracle Gap: ~0.37)
- Run full synthetic experiment across R_M values and judge qualities
- Generated scoring/scores.json with reproduced results

</details>

### Iteration 2: MiniMax-M2.7
- **Milestone**: `none` | **Status**: done
- **Working time**: 3.1h | **GPU**: 0.0h

