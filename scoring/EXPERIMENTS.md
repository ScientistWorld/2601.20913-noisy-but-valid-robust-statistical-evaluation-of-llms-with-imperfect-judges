# Experiment Overview

All experiments are computed by the evaluator from each certifier's raw 0/1 decisions on the same shuffled batch of evaluator-generated instances. Comparison rows (`direct_ht`, `oracle_noisy_ht`) are computed by the evaluator itself. A certifier that violates validity in any judge regime, crashes, returns malformed output, or makes batch-dependent decisions is scored as failed (worst value everywhere).

## synthetic_power_comparison

Tests whether a certification procedure has enough power to certify a reliable model (true failure rate 0.20, threshold 0.25) when the auxiliary judge is informative and many judge labels are available. This is the benchmark's main claim: auxiliary labels should buy power over using the small human-labelled set alone.

## synthetic_type2_curve

Checks how the chance of failing to certify a reliable model behaves across failure rates, from very rare failures (0.01) to just below the threshold (0.225), with an informative judge. Rare failures are included on purpose: there, the small calibration set may contain almost no failures.

## judge_quality_sweep

Checks power when the judge is less reliable — it misses many failures, or raises many false alarms. This is where using judge labels is hardest, and where a procedure may fall behind one that ignores the judge.

## oracle_gap

Measures the average power lost, over all the cells above, relative to an idealized test that knows each instance's judge reliability exactly — the cost of having to learn judge reliability from a small calibration set.

## synthetic_type1_control

Reports false certification of unreliable models (at the threshold and clearly above it) in every judge regime. It is enforced as a hard limit (`zeta + 0.015`) and reported for transparency, not rewarded: being more conservative than required earns nothing.
