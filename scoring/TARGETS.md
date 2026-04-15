# Evaluation Targets

## Primary: synthetic_power_comparison
Tests whether a certification procedure can reduce false rejections of reliable models in the high-quality judge regime.

- **Metric**: `type2_error` (lower is better)
- **Constraint metric**: the paired Type-I control experiment must remain near the configured significance level.
- **How to run**: `bash scripts/evaluate.sh`

## Constraint: synthetic_type1_control
Tests whether certification remains statistically valid under the null boundary.

- **Metric**: `type1_error` (lower is better, target is the configured significance level)
- **How to run**: `bash scripts/evaluate.sh`

## Constraint: oracle_gap
Tests the cost of estimating judge reliability from a finite calibration set rather than knowing it exactly.

- **Metric**: `oracle_gap` (lower is better)
- **How to run**: `bash scripts/evaluate.sh`

## Diagnostic: synthetic_type2_curve
Tests how certification power changes as the true model failure rate varies around the deployment threshold.

- **Metric**: `type2_error` (lower is better)
- **How to run**: `bash scripts/evaluate.sh`
