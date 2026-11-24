# Noisy but Valid: Robust Statistical Evaluation of LLMs with Imperfect Judges

<!-- scope-note -->
> [!NOTE]
> **Not a full reproduction of the paper.** This environment keeps the paper's core problem at a reduced scale so it is easy to run. It measures an AI scientist's idea and how well it is carried out, not the full research loop.

| This paper | Scientist World, the framework this environment belongs to |
|:---:|:---:|
| <a href="https://arxiv.org/abs/2601.20913"><img alt="This paper on arXiv" src="https://img.shields.io/badge/arXiv-2601.20913-b31b1b?logo=arxiv&logoColor=white"></a> | <a href="https://arxiv.org/abs/2611.08478"><img alt="Scientist World on arXiv" src="https://img.shields.io/badge/arXiv-2611.08478-b31b1b?logo=arxiv&logoColor=white"></a> <a href="https://github.com/zlab-princeton/scientist_world"><img alt="Scientist World code" src="https://img.shields.io/badge/Code-Scientist_World-181717?logo=github&logoColor=white"></a> <a href="https://github.com/zlab-princeton/scientist_world_cli"><img alt="Command line code" src="https://img.shields.io/badge/Code-Command_line-181717?logo=github&logoColor=white"></a> |

| **Paper ID** | [2601.20913](https://arxiv.org/abs/2601.20913) |
|:---|:---|
| **Domain** | Statistical Machine Learning / LLM Evaluation |
| **TL;DR** | A hypothesis testing framework that certifies LLM failure rates using large noisy judge-labeled datasets while guaranteeing finite-sample Type-I error control, outperforming direct human evaluation when the judge is reliable. |

## Summary

This paper addresses the challenge of statistically certifying that an LLM's failure rate is below a safety threshold. The authors propose a "Noisy Hypothesis Testing" approach that uses a small human-labeled calibration set to estimate an LLM judge's True Positive Rate (TPR) and False Positive Rate (FPR), then applies a variance-corrected hypothesis test on a large judge-labeled dataset. The method guarantees finite-sample Type-I error control (validity) and improves statistical power over direct testing when the judge is reliable. The paper validates the approach on synthetic data, toxicity classification (Jigsaw, Hate Speech datasets), and generative safety (SafeRLHF dataset), demonstrating alignment between theory and empirical results.

## Problem

How can we statistically certify that a Large Language Model's failure rate is below a specified safety threshold, when we have:
1. A **small dataset** with ground-truth human labels (`D_M` of size `n_M`)
2. A **large dataset** labeled by an imperfect LLM-as-a-Judge (`D_J` of size `n_J >> n_M`)

The challenge is that LLM judges are noisy — they have unknown True Positive Rate (TPR) and False Positive Rate (FPR) relative to ground truth. Naively trusting judge labels gives unreliable conclusions. Using only the small human-labeled set lacks statistical power.

## The paper's method

The paper introduces a **Noisy Hypothesis Testing (Noisy HT)** framework that certifies LLM failure rates using a large dataset labeled by an imperfect LLM-as-a-Judge, while providing finite-sample Type-I error control.

The key innovation is converting the original hypothesis test on the true failure rate R_M into an equivalent test on the noisy failure rate R_J, then using a small calibration set to estimate the judge's True Positive Rate (TPR) and False Positive Rate (FPR), and finally computing a **variance-corrected critical threshold** that accounts for both:
1. The variance of the noisy failure rate estimate from the large dataset
2. The variance of the TPR/FPR estimates from the small calibration set

## Key results of the paper

- **Type-I error control**: All procedures (Direct HT, Noisy HT, Oracle Noisy HT, PPI) control Type-I error at ζ=0.05 across all settings
- **Power improvement**: Noisy HT significantly outperforms Direct HT in the high-TPR/low-FPR regime (green region in the paper's Figure 1D), but is bounded above by Oracle Noisy HT (the "Oracle Gap")
- **Synthetic experiments**: With α=0.25, ζ=0.05, n_M=100, n_J=10,000, Noisy HT achieves substantially lower Type-II error than Direct HT in the high-quality judge setting used here (TPR=0.95, FPR=0.05) across a range of model failure rates
- **Real-data experiments**: Results on Jigsaw, Hate Speech, and SafeRLHF confirm theoretical predictions — Noisy HT works well with capable judges (LLaMA-3.1-8B, LLaMA-3.3-70B) as judges for smaller classifier models

## Run it

```bash
pip install sciworld
sw research 2601.20913 --mode innovate --agent claude-code
sw evaluate 2601.20913
```

## More

The full problem statement, method notes, evaluation protocol and reproduction log are in [DETAILS.md](DETAILS.md).

