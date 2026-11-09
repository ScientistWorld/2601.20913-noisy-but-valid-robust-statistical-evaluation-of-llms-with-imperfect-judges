The audit completed in two CPU jobs. `python3 redteam/bundle.py` now runs all
31 final cases; `followup.py` records the second job's three-case follow-up.
Each named folder has a standalone `run.sh` that constructs its candidate
artifact and invokes `bash scripts/evaluate_test.sh` **with no arguments**.
Results are incrementally saved as `scores.json` and `result.json` in that
folder. The broken original reference has no scores; rejected artifact cases
may also have no scores. A written score file alone does not establish success:
the entire hidden script must exit zero.

Each hidden evaluation runs in new shell/Python processes. Cases within a job
share a container, and the two jobs started in fresh containers. No result
depends on a live method process, patched evaluator, altered Python
environment, module state, or access to a hidden answer during generation.
The audit controller backs up and restores the original artifact, score files,
and candidate method entry point after every case. These backups are never
inputs to shortcut decisions.

The shipped `method/run_synthetic.py` imports a missing `method/core.py`.
`reference_missing` records the actual unmodified runner's failure. Other
runs replace the broken method entry point with a candidate entry point, an
ordinary permitted method change. `algorithm.py` reconstructs the documented
Noisy HT, Direct HT, and oracle formulas using only improve-mode-visible
`briefing/method.md`. `reference_agreement.json` checks all 6,000 scored rows
against the saved original held-out artifact: zero mismatches. The unscored
PPI diagnostics are not reconstructed. Only the audit control
`reference_saved` uses the original artifact as its candidate.

The better variant adds an exact binomial human-label fallback when calibration
has no failures or no successes. The weaker variant uses only human labels.
Both retain the fixed distribution, 100/10,000 samples, alpha, and zeta.
Both are evaluated on the same three draws as the reconstructed reference.
Folder seed suffixes 42/43/44 have actual audit-test seeds 1000045/46/47.

All shortcuts use public seeds, independent of the saved test artifact and
hidden test seeds. `baseline_fields_shortcut` and `oracle_comparator_shortcut`
use visible seed 43, with `visible_seed_43_reference` as their exact unchanged
control. All other shortcuts use visible seed 42. The comparison shortcuts'
first seed-42 runs were rejected by train/test equality checks; their
`initial_result.json` and `initial_scores.json` retain those failures. The
shared cache contains reproducible synthetic artifacts, not trained models.

`summary.json` declares the normalization cohorts and computes the specified
coefficient-magnitude, direction-aware, experiment-weighted, population-
standard-deviation-normalized rank improvement over the saved reference.
All nonzero reference-scored cells, including baseline rows, count. Final
future-attempt standard deviations are unknown. Results therefore include
the nine scientific variants, the 21 accepted bounded-score cases, a
22-case finite cohort including the negative oracle gap, a 23-case cohort
including impossible negative flags, and individual two-attempt cohorts.
Proposed-row-only results are sensitivity checks, not the specified ranking.
Rejected attempts never enter normalization. Nonfinite scores are retained in
their case folder but never receive a numerical rank (`accepted` in the
summary requires both exit zero and finite scored values).

Large generated artifacts and logs remain ignored. Small requested scores,
result records, source, integrity hashes, and the final report are committed.
`REDTEAM.md` at the workspace root gives findings and limitations.
