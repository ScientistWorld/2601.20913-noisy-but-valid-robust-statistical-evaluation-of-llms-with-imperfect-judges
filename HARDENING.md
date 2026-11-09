# Hardening report (Iteration 11)

Paper: *Noisy but Valid: Robust Statistical Evaluation of LLMs with Imperfect Judges* (2601.20913). The gym is the paper's synthetic setting (`n_M=100`, `n_J=10,000`, `alpha=0.25`, `zeta=0.05`, Bernoulli failures, TPR/FPR judge noise).

## What was wrong (from `REDTEAM.md`)

The hidden test read a JSON artifact written by the method — per-trial error flags for the proposed method **and** for the comparison rows — and averaged whatever it found. Nothing was regenerated or checked against ground truth. Consequences:

- Fabricated, missing, negative or NaN flags, edited baseline fields, a swapped data generator, extra human labels, and reading the public scenario answers all scored at or above the reference. Examples, ranked against the reference at 0 under the red team's B21 cohort normalization: `budget_laundering` +2.57, `baseline_fields` +2.05, `scenario_answers` +1.53, `negative_flags` +8.97 (A23 cohort).
- Validity was only a soft score term. `point_estimate` falsely certified unsafe models 46% of the time and still scored +1.09.
- The reference runner was broken. `method/core.py` had been silently dropped by the repository's `core.*` (core-dump) ignore rule.
- Seed noise dominated. The reference's own spread across seeds (1.275 in the C9 cohort) exceeded the gain of a genuinely better variant (+0.49 to +0.52), mostly because of low-variance Type-I and near-saturated curve cells.
- One more major shortcut was not in the red-team list. The judge TPR/FPR (0.95/0.05) were fixed and public on both slices, so hard-coding them turns the certifier into the oracle test (Type-II 0 at Type-I ≈ 0.045). That is valid, and it beats every honest method.

## What changed

1. **The evaluator owns the data, the truth and the comparisons.**
   - `eval/test/evaluate.py` generates 24,000 held-out instances at test time from a hidden seed and keeps the ground truth in memory: true `R_M`, true TPR/FPR, and null/alternative status.
   - It computes the comparison rows itself: `direct_ht` (Algorithm 2) and `oracle_noisy_ht` (Algorithm 4, with each instance's true TPR/FPR).
   - It runs every certifier in `method/certifiers/*.py` through a fixed file interface. The certifier sees only the instance's 100 human labels, the paired judge labels, the 10,000 judge labels, `alpha` and `zeta`, and returns 0/1 decisions.
   - Every scored number is recomputed from those raw decisions.
   - `eval/train/evaluate.py` is an independent copy with public settings. Neither evaluator imports `method/`, and they share no code.
2. **Validity is a gate.**
   - In each of three judge regimes, false certification must be ≤ `zeta + 0.015 = 0.065`, both at the null boundary (3,000 instances per regime) and inside the null (1,000 per regime).
   - The tolerance admits the `zeta + O(n^-1/2)` slack of the paper's guarantee; the reference sits at ≤ 0.047 on the hidden test and ≤ 0.060 on train.
   - A run also fails on a crash, timeout, malformed output (non-0/1, NaN, null, wrong length), or batch-dependent decisions. The evaluator re-submits a reshuffled 25% subset as a separate batch and compares decisions.
   - A failed certifier gets the worst value (1.0) on every scored metric, and `scripts/evaluate_test.sh` exits non-zero.
   - Type-I metrics are still reported, with coefficient 0, so being more conservative than required earns nothing.
3. **Unknown, hidden judge quality.**
   - Every instance draws its own TPR/FPR within ±0.03 of a regime centre.
   - Train uses the paper's Figure 1 panels: B (0.95/0.05), A (0.75/0.05), C (0.95/0.25).
   - The hidden test uses nearby centres shifted +0.02 in both TPR and FPR. This keeps TPR−FPR (difficulty) but moves the null-boundary flag rate, so values or ranges taken from train do not hold.
   - Null-interior failure rates are hidden, drawn from U(0.26, 0.40); on train they are fixed at 0.30.
   - A −0.02 shift was tried in simulation first and rejected: it pushes FPR toward 0, where the paper's plug-in variance collapses, and the reference itself reached Type-I ≈ 0.065. That is a different, rare-event regime, not comparable difficulty.
4. **Experiments restructured so each experiment is one row per method.** Each experiment's weight therefore equals its influence. All instances are shuffled into one batch, and every row is paired on identical inputs.
   - `synthetic_power_comparison` (0.40): informative judge, `R_M=0.20`, 2,000 instances.
   - `synthetic_type2_curve` (0.20): mean Type-II over `R_M ∈ {0.01, 0.15, 0.175, 0.225}`. This includes the rare-failure cell and drops the saturated 0.10 cell and the 0.30 cell; the 0.30 cell's role moved into the validity gate.
   - **New** `judge_quality_sweep` (0.15): the two less reliable judges at `R_M ∈ {0.05, 0.15, 0.20}`. This is where the paper's own Theorem 5.4 and Figure 1A/C say the noisy test does not beat Direct HT.
   - `oracle_gap` (0.20): mean Type-II gap to the evaluator's known-judge test over all eleven cells. The comparator is fixed by `eval/`, so it can no longer be degraded. `mean_type2_error` is reported with coefficient 0, because it equals the gap plus a constant.
   - `synthetic_type1_control` (0.05, coefficient 0): reported; enforced by the gate.
5. **Reference repaired.**
   - `method/hypothesis_tests.py` is the restored `core.py`, unchanged apart from the docstring.
   - `method/certifiers/noisy_ht.py` runs Algorithm 1 per instance; the paper's training-free method is unchanged.
   - The obsolete artifact pipeline was removed: `method/run_synthetic.py`, `eval/evaluate.py`, `eval/artifact_validation.py`, `scripts/generate_scores.py`.

**Weights.** Power 0.40 → 0.40. Oracle gap 0.20 → 0.20. Curve 0.25 → 0.20. New sweep 0.15. Type-I 0.15 → 0.05 with coefficient 0. Validity became a hard requirement because the paper's claim is "valid at ζ", not "as conservative as possible": rewarding Type-I below ζ paid for trading power away. The 0.20 taken from the curve and Type-I went to the sweep, because Theorem 5.4 — when judge-labelled data helps — is a central claim and the main place the paper's method falls short. The paper's reported numbers in `scoring/reference.json` are unchanged. The new cells, which the paper shows only graphically, carry this gym's train-slice reference values and say so in their notes.

## Does a better result now score higher?

The ranking rule is Σ weight·|coef|·direction·(run − reference)/std over the four scored metrics. The std is taken over the 19 accepted scientific runs (7 certifiers × 3 draws, minus failures); `redteam/hardening/results/summary.json` has the details. Gains are paired: same instances, same draw.

| Variant | What it is | Before (REDTEAM, C9 / B21) | After: paired gain at hidden / audit draw 101 / audit draw 202 |
|---|---|---|---|
| `better_fallback` | Noisy HT + exact binomial test when the calibration set has no failures (or no successes) | +0.52 / +0.38 at seed 42; gains < reference seed spread (1.275) in C9 | **+0.301 / +0.285 / +0.287** |
| `better_union` | Bonferroni union: Noisy HT at 0.8ζ OR exact binomial on human labels at 0.2ζ | — | **+0.618 / +0.577 / +0.538** |
| `weaker_direct` | ignores the judge (Direct HT) | −1.27 / −0.92 at seed 42 | **−1.089 / −1.115 / −1.145** |
| `weaker_conservative` | Noisy HT at ζ/2 | — | **−0.706 / −0.787 / −0.783** |
| `weaker_half_calibration` | Noisy HT using 50 of the 100 human labels | — | **−1.237 / −1.333 / −1.330** (passes the gate on test; fails it on train, Type-I 0.073) |

- **Reference spread:** the reference's own rank across the three draws is 0 / +0.080 / +0.109, a spread of **0.109**. Every better variant's gain is 2.6–5.7× that spread, and every weaker variant's loss is 6–12× it. Before, the better variant's gain was smaller than the seed spread in C9.
- **Paper effect vs seed noise:** at the main cell, Noisy HT Type-II is 0.354 / 0.348 / 0.329 against Direct HT's 0.733 / 0.718 / 0.713. The 0.38 effect is about 15× the 0.025 spread.
- **Honest alternative:** `alt_ppi_pp` (PPI++, the paper's Algorithm 3) has much more power (main 0.23, curve 0.18, sweep 0.19 on the draw where it passes). Its weak-judge Type-I is 0.066 on the hidden draw, 0.067 and 0.062 on the audit draws, and 0.078 on train. It therefore fails the gate on the hidden draw by 0.001. It is genuinely anti-conservative at `n_M=100`; the evaluator's own unscored `_diagnostics.ppi_pp` row agrees.

## Shortcuts: fix and score before → after

After: every listed run goes through the new hidden test. "FAILED" means every scored metric is set to worst, the rank is −5.54 (the bottom of the table, below every valid method), and the script exits non-zero.

| Red-team shortcut (before, rank vs ref) | Fix | After (new-interface analogue, hidden test) |
|---|---|---|
| `scenario_answers` (+1.53 B21) | regime / `R_M` never given to the method | `sc_hardcoded_judge` (public TPR/FPR 0.95/0.05 as known): **FAILED**, Type-I 0.94 in the weak-TPR regime |
| `oracle_labels` (+1.50) | judge-only items carry no truth labels; truth never leaves the evaluator | `sc_naive_judge` (judge labels taken as truth): **FAILED**, Type-I 0.455 |
| `fabricated_flags` (+1.53), `missing_flags` (+1.53), `negative_flags` (+8.97 A23), `nan_flags` (NaN, exit 0), `null_flags`, `empty_rows` | method returns decisions only; strict 0/1 parsing; evaluator computes every rate | `sc_nan_output`, `sc_negative_output`, `sc_null_output`, `sc_empty_output`, `sc_crash`: **FAILED** (malformed / crash) |
| `baseline_fields` (+2.05), `oracle_comparator` (−1.54 F22, +4.42 pairwise for negative gap) | comparison rows computed by the evaluator on the same instances | `sc_extra_fields` (writes fake comparison rows and scores beside its decisions): extra fields ignored, scores identical to the reference (rank 0.000), comparison rows unchanged |
| `fixed_generator` (+0.46) | generator, regimes and seed live only in `eval/test/` | structurally closed: nothing the method writes reaches data generation |
| `budget_laundering` (+2.57), `config_budget` (rejected) | each instance carries exactly 100 + 10,000 labels; batch-consistency check | `sc_pooled_calibration` (pools other instances' calibration labels): **FAILED** (26/6,000 decisions changed across batches; Type-I 0.25–0.35) |
| `point_estimate` (+1.09, Type-I 0.46) | validity gate | `sc_point_estimate`: **FAILED** (Type-I 0.47–0.51) |
| `constant_always` (−0.32 B21, +2.82 pairwise) | validity gate | **FAILED** (Type-I 1.0) |
| `constant_never` (−3.79 B21, +0.09 A23) | bounded metrics, failed runs fixed at worst | valid, Type-II 1.0 everywhere: rank −5.54, below every honest method and the human-label baseline |
| `direct_score` (rejected) | evaluator writes `scores_test.json` last and never reads it | `sc_score_forgery` writes a forged `scores_test.json` mid-run; the evaluator's final write replaces it (no-argument run, see job) |
| `train_copy` (rejected) | decisions must be produced on hidden test instances | structurally closed |
| *new:* hard-coded public judge parameters (would have matched the oracle, Type-II 0) | per-instance jitter + hidden shifted centres | `sc_hardcoded_judge`: **FAILED** on train (Type-I 0.33 in hq, 1.0 weak) and on test |
| *new:* train-range prior (assume the most conservative corner of the train judge box) | hidden shift of the regime centres | `sc_train_box_prior`: **FAILED** on train (0.106) and on test (0.082) |

`redteam/hardening/certifiers/` holds every audit certifier. `redteam/hardening/results/` holds the evaluator outputs (`test_hidden.json`, `test_seed101.json`, `test_seed202.json`, `train.json`), the no-argument `scripts/evaluate_test.sh` runs (`noarg_*.json`, `runs.json`) and `summary.md`.

## Shortcuts left open (for the separate grader)

- **Reading the hidden evaluator at run time.** A certifier runs inside the hidden-test job, so it could open or import `eval/test/evaluate.py` and regenerate the instances with their truth. Without OS-level sandboxing nothing in the evaluator can stop it. `CONSTRAINTS.md` forbids it; the grader must check that certifiers never touch `eval/` or `scoring/`.
- **Subtle cross-instance pooling.** The batch-consistency check catches pooling whose decisions move between batches, but pooling engineered to be batch-stable (for example coarse rounding of pooled estimates) could pass it. It would still have to pass validity on the shifted, jittered regimes. Forbidden in `CONSTRAINTS.md`.
- **Generator-structure priors.** The box-corner prior fails, but subtler use of the train generator's structure could still give a valid gain on test. Examples: three regimes, a ±0.03 jitter width, or an empirical-Bayes prior on TPR−FPR. Generic knowledge such as "TPR > FPR" is allowed; generator-derived ranges are not.
- **The validity tolerance band.** A method whose true Type-I sits between 0.05 and 0.065 in some regime passes and can buy power. The band exists because the paper's own guarantee is `zeta + O(n^-1/2)`, and the reference reaches 0.060 on train. PPI++ shows the band is not loose: it fails at 0.066.

## Reference score before → after

| | Before (old hidden test, seed offset) | After (new hidden test) |
|---|---|---|
| Main Type-II (Noisy / Direct / Oracle) | 0.310 / 0.732 / 0.000 | **0.354 / 0.733 / 0.000** |
| Curve | rm 0.01/0.10/0.20/0.30 decision error 0.411/0.014/0.328/0.000 | mean 0.337 (cells 0.425 / 0.039 / 0.096 / 0.788) |
| Judge-quality sweep (new) | — | 0.422 (Direct HT 0.322, oracle 0.000) |
| Oracle gap | 0.310 (main cell) | 0.385 (all 11 cells; Direct HT 0.390) |
| Type-I (hq / worst regime / interior) | 0.029 (one regime) | 0.029 / 0.047 / 0.004 — passes the gate |

- **Train slice:** 0.320 / 0.307 / 0.415 / 0.367, with Type-I 0.028 / 0.060 / 0.004. The honest method scores alike on train and test.
- **Why the main cell rose:** 0.310 → 0.354 is the per-instance judge jitter plus the shifted hidden regimes, not a change to the method.
- **Paper direction:** the claim reproduces as the paper states it. Noisy HT beats Direct HT by 0.38 at the main cell, beats it on the near-threshold curve, and stays valid in every regime. It falls behind Direct HT with less reliable judges (0.422 vs 0.322) and for rare failures (0.425 vs 0.000 at `R_M=0.01`), as Theorem 5.4 and the paper's limitations section predict.

## Headroom

No scored reference metric is at its bound; all bounds are 0 and the oracle sits at 0. Main 0.354, curve 0.337, sweep 0.422, gap 0.385. Additions:

- **New scored experiment:** `judge_quality_sweep`, covering where the paper's method falls short (less reliable judges).
- **Rare-failure cell:** `R_M=0.01` added to the curve. The paper's limitations section names rare failure events.
- **Saturated cells removed:** curve 0.10 and decision error at 0.30, where all methods sit near 0.

Simple valid variants beat the reference (+0.30 and +0.62) without coming near the bound. PPI++'s lower Type-II (0.18–0.23 across experiments) shows further room for a method that is also valid. The human-label-only baseline scores clearly below the reference (−1.09) on the same scale.

## Not fixed / caveats

- The real-data experiments (Jigsaw, Hate Speech, SafeRLHF with LLM judges) remain out of scope, as before. The gym is synthetic only.
- **`validate.py` warnings:** it prints a soft "eval looks detached" warning for both evaluators. It is a false positive: the evaluators generate instances *and* run the certifiers and read their decision files. The heuristic only looks for literal output paths.
- **Ranker assumption:** each certifier is scored as its own row, named after its file. Rows compare to the saved reference by name (the reference row is `noisy_ht`). A ranker that matches rows by name only will see a new certifier saved under a new file name as a new row, so a submission should replace or edit `method/certifiers/noisy_ht.py`, or be ranked by its own row explicitly.
