# Problem Definition

## Research Question

How can we statistically certify that a Large Language Model's failure rate is below a specified safety threshold, when we have:
1. A **small dataset** with ground-truth human labels (`D_M` of size `n_M`), on which the judge's labels are also available
2. A **large dataset** labeled only by an imperfect LLM-as-a-Judge (`D_J` of size `n_J >> n_M`)

The challenge is that LLM judges are noisy — they have unknown True Positive Rate (TPR) and False Positive Rate (FPR) relative to ground truth, and these differ from judge to judge and task to task. Naively trusting judge labels gives unreliable conclusions. Using only the small human-labeled set lacks statistical power.

## Why It Matters

LLM deployment in safety-critical settings requires statistically rigorous guarantees that failure rates are below acceptable thresholds. Human evaluation is the gold standard but is costly and unscalable. LLM-as-a-Judge offers scalability but introduces noise and bias. Without formally accounting for judge imperfections, statistical conclusions become unreliable.

## Success Criteria

A successful solution must:
1. **Control Type-I error**: the probability of incorrectly certifying an unsafe model must stay at the specified significance level ζ (here 5%), whatever the (unknown) quality of the judge. This is a hard requirement, not a quantity to trade off.
2. **Maximize statistical power**: minimize Type-II error — the probability of failing to certify a genuinely safe model — across model failure rates and judge qualities.
3. **Use the available supervision effectively**: when the judge is informative, the large judge-labeled dataset should improve certification power; when it is not, the method should not do worse than it has to.
4. **Respect the label budget**: each certification decision uses only its own `n_M` human labels and `n_J` judge labels; judge reliability must be learned from that data, not assumed.

## Benchmark Setting

The benchmark is synthetic: ground-truth labels are Bernoulli(R_M) and judge labels flip them with the judge's TPR/FPR. Each instance has `n_M = 100`, `n_J = 10,000`, `alpha = 0.25`, `zeta = 0.05`, and its own judge TPR/FPR drawn around one of three judge-quality regimes. See `briefing/evaluation.md` for the instance format, the certifier interface, and how scores are computed.
