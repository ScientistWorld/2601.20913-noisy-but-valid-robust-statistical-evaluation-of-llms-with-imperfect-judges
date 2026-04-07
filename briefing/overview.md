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
