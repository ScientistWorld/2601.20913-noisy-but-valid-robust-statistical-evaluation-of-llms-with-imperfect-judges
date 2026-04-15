# Research Direction

## Research Problem

This benchmark studies statistically valid certification of model reliability when only a small set of human labels and a much larger set of imperfect judge labels are available. The central question is how to use the noisy judge labels to improve certification power without losing Type-I error control.

## Core Contribution

The paper's contribution is an explicit judge-noise model for certification. It estimates judge reliability through interpretable TPR/FPR parameters and propagates calibration uncertainty into the rejection threshold. Future work should improve this family of statistically valid judge-aware certification procedures.

## Approach Scope

In-scope improvements include better finite-sample corrections, alternative uncertainty estimates for judge reliability, bounded or regularized TPR/FPR estimation, stratified judge models, and combinations with control-variate style estimators that still preserve the certification hypothesis and Type-I error target.

## Out Of Bounds

Replacing the task with ordinary supervised classification, using a perfect oracle labeler for all samples, increasing the fixed sample budgets, or optimizing only Type-II error while ignoring Type-I error is out of bounds. Those changes would bypass the certification tradeoff the paper is designed to address.
