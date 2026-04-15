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
3. **Use the available supervision effectively**: When the auxiliary judge is informative, the large judge-labeled dataset should improve certification power without weakening Type-I error control
4. **Expose reliability tradeoffs**: The evaluation should make clear how certification outcomes change as auxiliary-judge quality, model failure rate, and sample sizes change
