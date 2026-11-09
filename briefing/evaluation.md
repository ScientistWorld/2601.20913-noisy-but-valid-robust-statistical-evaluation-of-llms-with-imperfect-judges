# Evaluation

## What is measured

Each **instance** is one certification problem: decide whether to certify that a
model's true failure rate `R_M` is below the threshold `alpha`, i.e. reject
`H0: R_M >= alpha` in favour of `H1: R_M < alpha`, at significance level `zeta`.
For every instance the method sees only:

- `n_M = 100` calibration items with the ground-truth failure label `S_M` and the
  judge's label `S_J'` on the same items;
- `n_J = 10,000` further items with the judge's label `S_J` only;
- `alpha = 0.25` and `zeta = 0.05`.

Labels are i.i.d.: `S_M ~ Bernoulli(R_M)`, and the judge flags a failure with
probability TPR when `S_M = 1` and FPR when `S_M = 0`. **Every instance has its own
judge TPR/FPR**, drawn around the centre of one of three judge-quality regimes
(an informative judge, a judge that misses many failures, a judge with many false
alarms). The method is never told `R_M`, TPR, FPR, the regime, or which instances
are null cases.

Error rates:

1. **Type-I error / false certification**: certifying when `R_M >= alpha`.
   Measured at the null boundary `R_M = alpha` (3,000 instances per regime) and
   for clearly unreliable models `R_M > alpha` (1,000 instances per regime).
2. **Type-II error**: failing to certify when `R_M < alpha` (lower is better).

## Validity is a gate, not a score

In every regime, both false-certification rates must stay at or below
`zeta + 0.015 = 0.065` (the tolerance admits ordinary finite-sample slack of
approximate tests). A certifier that exceeds the limit anywhere, crashes, times
out (30 min per run), returns malformed output, or makes decisions that change
when the same instances are re-submitted in a different batch is **failed**: all
of its scored metrics are set to their worst value and the evaluation script
exits non-zero. Among valid certifiers, a lower Type-I error earns nothing extra.

## Scored experiments (lower is better for all)

| Experiment | Metric | Cells |
|---|---|---|
| `synthetic_power_comparison` | `type2_error` | informative judge, `R_M = 0.20` (2,000 instances) |
| `synthetic_type2_curve` | `type2_error` (mean over cells) | informative judge, `R_M` in {0.01, 0.15, 0.175, 0.225} |
| `judge_quality_sweep` | `type2_error` (mean over cells) | the two less reliable judges, `R_M` in {0.05, 0.15, 0.20} |
| `oracle_gap` | `oracle_gap` | mean Type-II over all eleven cells above minus that of a reference test that knows each instance's true TPR/FPR |
| `synthetic_type1_control` | `type1_error`, `type1_error_worst_regime`, `false_cert_interior` | reported for transparency (coefficient 0; enforced by the gate) |

Alternative cells hold 1,000 instances unless stated. All instances of all cells
are shuffled together into one batch.

## Comparison rows (computed by the evaluator, not by any method)

- `direct_ht`: a one-sample normal-approximation test that uses only the 100
  ground-truth labels.
- `oracle_noisy_ht`: an idealized test that is given each instance's true judge
  TPR/FPR and uses the judge-only items (not achievable in practice).

Every certifier and both comparison rows are scored on exactly the same instances
(paired comparison), and the instance seeds are fixed.

## Certifier interface

A method is a **certifier**: any file `method/certifiers/<name>.py` (names starting
with `_` are helpers and are not run). The evaluators run each one as

```
python3 method/certifiers/<name>.py --input <dir> --output <decisions.json>
```

from the workspace root. `<dir>` contains one batch of `N` instances:

| File | Content |
|---|---|
| `calib_human.npy` | uint8 `[N, 100]`, ground-truth labels `S_M` of the calibration items |
| `calib_judge.npy` | uint8 `[N, 100]`, judge labels `S_J'` of the same items |
| `eval_judge.npy` | uint8 `[N, 10000]`, judge labels `S_J` of the judge-only items |
| `alpha.npy`, `zeta.npy` | float64 `[N]` |
| `meta.json` | `n_instances`, `n_m`, `n_j` |

The certifier writes `{"certify": [0 or 1, ...]}` with one entry per instance in
input order (1 = certify, i.e. reject `H0`). Rules: each decision may use only
that instance's own data (instances are independent certification problems; the
evaluator re-runs a reshuffled subset in a separate batch and fails a certifier
whose decisions change), and decisions must be deterministic. Each certifier is
scored as its own row, named after its file.

## How to run

- `bash scripts/evaluate_train.sh` — public train-slice instances (judge regimes
  centred on TPR/FPR 0.95/0.05, 0.75/0.05 and 0.95/0.25, per-instance spread
  +/-0.03, unreliable-model cells at `R_M = 0.30`); writes `scoring/scores_train.json`.
  An optional argument draws another public batch: `bash scripts/evaluate_train.sh 123`.
- `bash scripts/evaluate.sh` — the same train-slice evaluation written to the
  canonical `scoring/scores.json`.
- `bash scripts/evaluate_test.sh` — the held-out test (no arguments). Its
  instances are generated at test time from hidden settings: the three regimes
  sit near, but not on, the train centres, and unreliable models have hidden
  failure rates above `alpha`. A method that relies on the exact public judge
  parameters or their ranges will not transfer.
