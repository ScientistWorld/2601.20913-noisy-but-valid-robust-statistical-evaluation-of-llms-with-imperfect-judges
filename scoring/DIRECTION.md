# Research Direction

## Research Problem

This benchmark studies statistically valid certification of model reliability when only a small set of human labels and a much larger set of imperfect judge labels are available. The central question is how to use the noisy judge labels to improve certification power without losing Type-I error control, across judges of different quality and across model failure rates.

## Core Contribution

The paper's contribution is an explicit judge-noise model for certification. It estimates judge reliability through interpretable TPR/FPR parameters and propagates calibration uncertainty into the rejection threshold. Future work should improve this family of statistically valid judge-aware certification procedures.

## Where There Is Room

- **Rare failures**: when the true failure rate is very low, the calibration set may contain no or very few failures, and judge reliability on failures cannot be estimated well.
- **Less reliable judges**: with a judge that misses many failures or raises many false alarms, using the judge can cost power relative to using the human labels alone.
- **The oracle gap**: the distance to a test that knows the judge's reliability exactly.

## Approach Scope

In scope: better finite-sample corrections, alternative uncertainty estimates for judge reliability (e.g. exact or score-based intervals), principled combinations of judge-based and human-label-only evidence that keep the overall level, generic regularization of TPR/FPR estimation that does not assume the generator's values, and control-variate style estimators that preserve the certification hypothesis and the validity gate.

## Out Of Bounds

Replacing the task with ordinary supervised classification, using information the instance does not contain (the true failure rate, the true judge TPR/FPR, the regime, the generator's parameter ranges, or other instances' labels), reading or modifying the evaluators, or improving Type-II error by exceeding the Type-I limit. Those changes bypass the certification trade-off the paper addresses.
