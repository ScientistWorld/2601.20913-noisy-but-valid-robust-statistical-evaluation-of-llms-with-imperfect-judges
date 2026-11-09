# Scientist Constraints

## Problem Formulation

Keep the binary certification problem fixed: test `H0: R_M >= alpha` against `H1: R_M < alpha` at level `zeta`, where `S_M=1` denotes a model failure and `S_J=1` denotes that an imperfect judge flags a failure. Changing the task to ordinary accuracy estimation, threshold tuning, or classifier training would sidestep the claim.

## Fixed Settings

`alpha=0.25`, `zeta=0.05`, `n_M=100` human-labelled calibration items and `n_J=10000` judge-only items per instance. The evaluators generate the instances, own the ground truth, and compute the comparison rows; they reject certifiers that change none of this but fail validity.

## Per-Instance Information Only

Each instance is an independent certification problem. A certifier's decision for an instance may use only that instance's own `n_M` human labels, `n_M` paired judge labels, `n_J` judge labels, `alpha` and `zeta`. Pooling labels across instances (it multiplies the human-label budget), using the position of an instance in the batch, or randomness that is not a deterministic function of the instance's data is not allowed; the evaluator re-runs a reshuffled subset and fails batch-dependent certifiers.

## No Assumed Judge Reliability

Judge TPR/FPR differ per instance and are unknown. Do not hard-code judge TPR/FPR values, regime centres, or ranges taken from the generator, the train slice, or the documentation; the held-out regimes differ from the train ones. Generic, documented prior knowledge such as "the judge is better than random (TPR > FPR)" is acceptable.

## Validity Requirement

In every judge regime, false certification at the null boundary and for clearly unreliable models must stay at or below `zeta + 0.015`. Lower Type-II error is never acceptable at the price of validity; violating runs are scored as failed.

## Do Not Touch the Evaluation

Do not modify, read at run time, or depend on files under `eval/`, and do not write to `scoring/`. Certifiers communicate only through the interface in `briefing/evaluation.md`.

## Compliance Checklist

- [ ] Same binary certification problem, `alpha=0.25`, `zeta=0.05`.
- [ ] Uses exactly the instance's own 100 human labels and 10,000 judge labels.
- [ ] No hard-coded judge reliability values or ranges; no cross-instance pooling.
- [ ] Deterministic decisions that do not depend on the batch.
- [ ] Passes the validity gate in every regime on the train slice.
