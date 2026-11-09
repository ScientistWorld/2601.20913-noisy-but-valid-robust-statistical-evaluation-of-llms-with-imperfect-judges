# Evaluation Targets

All scored metrics are lower-is-better error rates computed by the evaluator from a certifier's raw decisions. Run `bash scripts/evaluate_train.sh` (public train slice) or `bash scripts/evaluate.sh` (same slice, canonical `scoring/scores.json`); the held-out test is `bash scripts/evaluate_test.sh`.

## Primary: synthetic_power_comparison (weight 0.40)
Reduce false rejections of a reliable model (`R_M = 0.20`) with an informative judge.

- **Metric**: `type2_error` (lower is better)
- **Comparison rows**: `direct_ht` (human labels only, should be clearly worse) and `oracle_noisy_ht` (knows the judge, unattainable bound)

## Secondary: synthetic_type2_curve (weight 0.20)
Power across failure rates {0.01, 0.15, 0.175, 0.225} with an informative judge, including the rare-failure regime.

- **Metric**: `type2_error`, mean over the four cells (lower is better)

## Secondary: judge_quality_sweep (weight 0.15)
Power with less reliable judges (many misses or many false alarms) at failure rates {0.05, 0.15, 0.20}.

- **Metric**: `type2_error`, mean over the six cells (lower is better)

## Secondary: oracle_gap (weight 0.20)
Average power lost relative to a test that knows each instance's judge reliability, over all eleven alternative cells.

- **Metric**: `oracle_gap` (lower is better); `mean_type2_error` is reported only

## Constraint: synthetic_type1_control (weight 0.05, coefficient 0)
Validity in every judge regime. Enforced as a gate: false certification at the null boundary and for clearly unreliable models must be at most `zeta + 0.015 = 0.065` in each regime, otherwise the run is scored as failed.

- **Metrics**: `type1_error` (informative judge), `type1_error_worst_regime`, `false_cert_interior` — reported, not rewarded
