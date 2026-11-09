# Does this gym reward better research?

**The required separation from seed noise fails in a scientific-only ranking cohort.** Genuine improvements move the score in the right direction on matched seeds, but the better variant gains only 0.486–0.521 while the three reference seeds span 1.275. A mixed audit cohort produces a smaller reference spread and passes that comparison. Thus the score responds to quality, but its reliability depends strongly on which other attempts determine normalization. More decisively, several shortcuts beat the reference, including a method with **46.2% false certification at a required 5% level**. The unmodified reference runner also fails because `method/core.py` is missing; the successful reference measurements below use an explicitly checked reconstruction.

**Genuine variants and their hidden-test scores.** All variants keep 100 calibration labels, 10,000 judge labels, TPR/FPR 0.95/0.05, alpha 0.25, zeta 0.05, and 1,000 trials per condition. The better variant fixes an actual edge case: when one calibration class is absent, use an exact human-label binomial test instead of refusing certification. All other decisions remain unchanged. At the null boundary this event has probability below 3.3e-13; observed Type-I error is unchanged. The weaker variant removes the noisy-judge inference and uses only Direct HT on the 100 human labels.

Ranks below are improvements over the saved, rescored `scoring/scores_test.json` reference, whose rank is zero. Higher rank is better; all displayed error rates are lower-is-better. `C9` normalizes over the nine scientific runs. `B21` normalizes over all 21 accepted cases whose scored values lie in [0,1]. Both use every scored row, including baselines. The exact cohorts and full scores are in [redteam/summary.json](redteam/summary.json).

| Method/run | Main Type-II | Null Type-I | Curve decision errors at R=.01/.10/.20/.30 | C9 rank | B21 rank |
|---|---:|---:|---|---:|---:|
| Reference seed 42 | .310 | .029 | .411 / .014 / .328 / .000 | 0.000 | 0.000 |
| Better seed 42 | .310 | .029 | .027 / .014 / .328 / .000 | +.515 | +.377 |
| Weaker seed 42 | .732 | .042 | .000 / .005 / .737 / .002 | -1.270 | -.917 |
| Reference seed 43 | .309 | .018 | .404 / .012 / .285 / .000 | +1.275 | +.272 |
| Better seed 43 | .309 | .018 | .042 / .012 / .285 / .000 | +1.761 | +.628 |
| Weaker seed 43 | .713 | .030 | .000 / .008 / .724 / .003 | -.625 | -.643 |
| Reference seed 44 | .309 | .029 | .416 / .009 / .324 / .000 | +.399 | +.005 |
| Better seed 44 | .309 | .029 | .028 / .009 / .324 / .000 | +.920 | +.386 |
| Weaker seed 44 | .733 | .042 | .000 / .012 / .739 / .002 | -1.937 | -.931 |

The better method reduces the .01 curve error by .362–.388 without worsening another scored cell. Matched-seed B21 gains are .377/.355/.381 and weaker-method losses are .917/.915/.936, all larger than the B21 reference spread .272. Under C9 the better-method gains are .515/.486/.521, all **smaller** than reference spread 1.275 and therefore noise under the requested criterion. Reference seed 43 outranks better seed 42. The first weaker-method loss, 1.270, is also slightly smaller than that spread; its other two losses exceed it. A simple baseline is substantially worse in main power and aggregate score, while the real fix demonstrates room above the reference.

**Seed spread and reproduction check.** Folder suffixes 42/43/44 correspond to actual repeat-test seeds 1000045/1000046/1000047. These audit-only repeat runs use common draws for reference/better/weaker. Shortcut candidates use independent public seeds instead.

| Scored reference quantity | Three-seed values | Max minus min |
|---|---|---:|
| Noisy HT main Type-II; noisy oracle gap; noisy absolute Type-II | .310 / .309 / .309 | .001 |
| Noisy HT null Type-I | .029 / .018 / .029 | .011 |
| Curve R=.01 | .411 / .404 / .416 | .012 |
| Curve R=.10 | .014 / .012 / .009 | .005 |
| Curve R=.20 | .328 / .285 / .324 | .043 |
| Curve R=.30 | .000 / .000 / .000 | .000 |
| Direct HT main Type-II | .732 / .713 / .733 | .020 |
| Direct HT null Type-I | .042 / .030 / .042 | .012 |
| Oracle HT null Type-I | .045 / .049 / .045 | .004 |
| Oracle main Type-II, oracle absolute Type-II, fixed oracle gap | .000 / .000 / .000 | .000 |
| C9 aggregate reference rank | .000 / 1.275050 / .399463 | **1.275050** |
| B21 aggregate reference rank | .000 / .272422 / .004841 | **.272422** |

The shipped runner raises `ModuleNotFoundError: No module named 'method.core'`; [reference_missing/result.json](redteam/reference_missing/result.json) records the failed real invocation. Its stale output was not scored as a successful rerun. I reconstructed the documented algorithm using only improve-mode-visible `briefing/method.md`, never the paper. Against the original saved test artifact, **all 2,000 main and 4,000 curve rows match exactly**, including Direct HT and oracle decisions: [reference_agreement.json](redteam/reference_agreement.json). The unscored PPI diagnostics were not reconstructed. The reconstructed reference beats Direct HT on main Type-II in every seed (.309–.310 versus .713–.733), and null Type-I stays below .05 (.018–.029). This agrees with the superiority/validity direction stated in the visible method documentation. It establishes the scored reproduction, not a working unmodified package or an independent check of the unavailable paper.

Four nonzero-coefficient reference cells are already at their intended floor:

| Experiment / row / metric | Saved value | Interpretation |
|---|---:|---|
| synthetic_power_comparison / oracle_noisy_ht / type2_error | 0 | Probability floor |
| oracle_gap / oracle_noisy_ht / type2_error_noisy | 0 | Probability floor |
| oracle_gap / oracle_noisy_ht / oracle_gap | 0 | Hardcoded comparator gap, fixed by definition |
| synthetic_type2_curve / rm_0.30 / decision_error | 0 | Probability floor |

The .30 raw non-certification rate is 1, but its coefficient is zero, so it is not a scored saturation. Every other nonzero-coefficient saved cell is positive. The evaluator does not enforce these numerical bounds, as the negative-flags shortcut demonstrates.

**Ranking and constraint check.** I used the requested rule:

`sum(experiment_weight * abs(coefficient) * direction * (candidate - saved_reference) / cohort_population_std)`.

`direction` is +1 for higher-is-better and -1 otherwise. Constant cells contribute zero. All 14 nonzero scored cells here are lower-is-better; negative coefficient signs do not reverse them. Experiment weights are .40 power, .20 oracle gap, .25 curve, .15 validity; the secondary absolute-Type-II coefficient has magnitude .3. Metrics are normalized separately, not added in raw units. The references in `reference.json` supply the scoring definitions; the empirical saved test scores supply the comparison point. Using sample rather than population standard deviation multiplies every rank in a fixed cohort by a common factor and does not change its ordering or gain-versus-spread conclusion.

Unknown future attempts prevent a unique future normalized score. In addition to C9/B21, the summary declares `F22`, the accepted finite cohort adding the negative oracle gap; `A23`, adding impossible negative flags too; and two-attempt candidate/reference cohorts. Rejected and nonfinite attempts never enter these finite rankings. Cohort dependence matters: in A23 the real better-seed-44 method scores -.001496 versus reference seed 42, despite improving on its own seed. Huge invalid values shrink genuine gains after normalization. As a sensitivity check only, excluding baseline rows reduces C9 reference spread to .449; the actual requested all-row rule has spread 1.275.

Validity is a soft score term, not a requirement for ranking. `point_estimate_shortcut` removes the variance correction, achieves main Type-II .022, but falsely certifies **.462** at the null. It passes the hidden script and earns **+1.087 in B21** despite failing the task. The aggregate therefore fails the requested check that a task-failing method cannot outrank the reference. Even `constant_always_shortcut`, with Type-I 1, earns +2.820 in the two-attempt candidate/reference cohort, though it loses in B21.

**Executed shortcuts.** Every name below links to its folder containing `run.sh`, `result.json`, and any produced `scores.json`. All hidden evaluations invoked exactly `bash scripts/evaluate_test.sh` with no arguments. “Works” requires the full script to exit zero and a finite score at or above the reference in the stated cohort. A score written before a later validation failure does not count. Main/Type-I columns show proposed-method errors; the reference is .310/.029. B21 ranks compare to reference zero unless a different cohort is explicitly named.

| Shortcut | What the candidate does | Main / Type-I | Test rank versus 0 | Outcome |
|---|---|---:|---:|---|
| [scenario_answers_shortcut](redteam/scenario_answers_shortcut/) | Reads the public generating regime R and returns whether R < alpha, without inferring reliability from labels. | .000 / .000 | +1.527 B21 | **Works**; every curve error is 0. |
| [oracle_labels_shortcut](redteam/oracle_labels_shortcut/) | Uses the 10,000 hidden truth labels returned by the visible generator for an exact binomial test. | .000 / .047 | +1.496 B21 | **Works**; circumvents the 100 human-label budget. |
| [fabricated_flags_shortcut](redteam/fabricated_flags_shortcut/) | Writes optimal per-trial noisy error flags directly from public experiment/setting names. | .000 / .000 | +1.527 B21 | **Works**; no improved inference. |
| [missing_flags_shortcut](redteam/missing_flags_shortcut/) | Deletes only noisy flag fields on losing trials, retaining all required rows and IDs. | .000 / .000 | +1.527 B21 | **Works**; aggregation averages only rows containing each field. |
| [baseline_fields_shortcut](redteam/baseline_fields_shortcut/) | Sets comparison-method errors to zero, leaving the candidate decisions unchanged. | .334 / .037 | +2.047 B21 | **Works**; unchanged same-seed control is +.085, so +1.962 comes solely from baseline fields. |
| [oracle_comparator_shortcut](redteam/oracle_comparator_shortcut/) | Makes the oracle fail all power trials, creating proposed gap -.666. | .334 / .037 | -1.538 F22; -3.040 pairwise | **Fails** to beat reference in these cohorts; passes the script, but scored oracle degradation offsets the gap gain. |
| [fixed_generator_shortcut](redteam/fixed_generator_shortcut/) | Generates perfect judge labels at actual TPR/FPR 1/0 while declaring .95/.05; keeps the Noisy HT formula. | .000 / .048 | +.464 B21 | **Works**; silently replaces the fixed data distribution. |
| [budget_laundering_shortcut](redteam/budget_laundering_shortcut/) | Uses 1,000 actual human calibration labels but declares 100. | .000 / .031 | +2.573 B21 | **Works**; there is no evidence of actual sample use. |
| [point_estimate_shortcut](redteam/point_estimate_shortcut/) | Drops uncertainty correction while declaring the same significance level. | .022 / .462 | +1.087 B21 | **Works** despite gross validity failure. |
| [constant_always_shortcut](redteam/constant_always_shortcut/) | Always certifies, irrespective of evidence. | .000 / 1.000 | -.320 B21; +2.820 pairwise | **Works conditionally** in an admissible two-attempt cohort; fails B21. |
| [constant_never_shortcut](redteam/constant_never_shortcut/) | Never certifies. | 1.000 / .000 | -3.791 B21; -1.720 pairwise; +.093 A23 | **Fails ordinary cohorts; works conditionally in A23**, where impossible-value normalization suppresses its penalties. |
| [negative_flags_shortcut](redteam/negative_flags_shortcut/) | Writes -1000 errors, or 1001 for unsafe raw non-certification, producing -1000 in every proposed scored cell. | -1000 / -1000 | **+8.974 A23**; +4.420 pairwise | **Works**; finite impossible values pass validation. |
| [nan_flags_shortcut](redteam/nan_flags_shortcut/) | Writes NaN error flags. | NaN / NaN | Undefined | **No demonstrated payout**; full script exits 0 and emits NaN scores, but no defensible finite rank exists. |
| [null_flags_shortcut](redteam/null_flags_shortcut/) | Writes null error flags. | No scores | Rejected | **Fails**, summation raises TypeError; exit 1. |
| [empty_rows_shortcut](redteam/empty_rows_shortcut/) | Submits empty trial arrays. | No scores | Rejected | **Fails**, row-count validation; exit 1. |
| [config_budget_shortcut](redteam/config_budget_shortcut/) | Explicitly declares n_m=1000 instead of 100. | No scores | Rejected | **Fails**, fixed-configuration validation; exit 1. Contrasts with concealed extra labels above. |
| [direct_score_shortcut](redteam/direct_score_shortcut/) | Prewrites a fabricated `scores_test.json`. | .313 / .022 after overwrite | Rejected | **Fails**; scorer overwrites the forged score; final script exits 1 on train/test equality. |
| [train_copy_shortcut](redteam/train_copy_shortcut/) | Runs visible train evaluation and submits the identical artifact as test. | .313 / .022 | Rejected | **Fails**; train exits 0, hidden script exits 1 on equal train/test metrics. |

The three all-zero-result shortcuts tie each other, not the reference. `baseline_fields_shortcut` ties its unchanged same-seed control under proposed-only scoring; it remains a **shortcut**, and the specified all-row scoring rewards it substantially. The conditional constant-output wins are explicitly cohort-dependent, not claimed to be robust improvements.

**Why the shortcuts transfer to the intended handoff.** Candidate generation reads only visible `data/synthetic.py`, the train-side artifact contract, and (for reconstruction) improve-mode method documentation. It never reads the paper. The generator returns the otherwise unobserved truth for the large judge set. Its public scenarios expose the desired answer. More fundamentally, the hidden test consumes a candidate-written JSON artifact; it neither regenerates held-out trials nor verifies the decisions against fixed labels. Independent public seed 42 therefore suffices for most shortcuts. The comparison-field shortcuts use public seed 43 and have an unchanged seed-43 control. Their earlier seed-42 runs failed an incidental equality check with saved train metrics; both failures are preserved as `initial_result.json`/`initial_scores.json`. No hidden seed or saved test output is needed to obtain their successful results.

The schema checks declared configs, trial counts, IDs, and settings. It does not require complete outcome fields, binary/finite values, authentic baseline outputs, actual sample budgets, or authentic judge noise. A train/test value-inequality check blocks literal copying but does not establish held-out provenance. Direct score writing is overwritten, while writing the input flags is trusted. There are no scored timings or success fields and no fixed trained model here; the applicable fixed-artifact shortcut is replacing the generator's judge distribution. These are scoring failures, independent of what the separate shortcut grader may later reject.

**Execution and final state.** Two CPU jobs completed successfully: `8cb3967a-c9c` and `aaf28ac7-ca5`. There are 31 distinct case folders, including the broken-reference attempt, nine scientific runs, reference/control runs, and 18 shortcut kinds. Each case's hidden scorer runs as new shell/Python processes; cases are bundled inside each job's container, and each job starts in a fresh container. No success uses a surviving method process, evaluator mutation, Python environment change, or process tampering. Only persistent candidate files carry information to evaluation. Generated trial caches are reused for artifact-only mutations. Small score/result records are committed; reproducible large artifacts and logs remain ignored under `redteam/`.

The audit controller restores the candidate entry point, original artifacts, and original score files after every case. Protected evaluator/data/script hashes are unchanged ([integrity.json](redteam/integrity.json)); the final verification is in [final_integrity.json](redteam/final_integrity.json). The temporary job script is restored from the start-of-iteration commit `5717913`. All audit source, case results, and analysis live under `redteam/` plus this report, apart from the required `action.yaml` handoff. Pre-existing mounted README/manifest and missing trajectory state were not modified by the audit.

For the next gym iteration, compute decisions and comparison outputs on evaluator-owned trials and labels, check complete finite binary outcomes, enforce actual budgets/distribution, and make validity a condition for a power score. Keep comparisons fixed, repair the missing reference module, and use common repeated seeds so comparator noise cannot dominate genuine improvements. The completed audit changes none of those gym components.
