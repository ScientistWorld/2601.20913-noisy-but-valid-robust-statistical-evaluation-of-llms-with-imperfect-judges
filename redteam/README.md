This audit uses one CPU job: `python3 redteam/bundle.py`. Each named folder has
a standalone `run.sh` that constructs its candidate artifact and runs
`bash scripts/evaluate_test.sh` **with no arguments**, in a new process. Outputs
are incrementally saved as `scores.json` and `result.json` in that folder.
No evaluator, Python environment, validation code, or process is patched.
The temporary artifact, score files, and candidate method entry point are
restored after every run.

The shipped `method/run_synthetic.py` imports a missing `method/core.py`.
`reference_missing` records the actual unmodified runner's failure. For the
other runs, the candidate replaces the broken method entry point with its own
entry point, a permitted method change. `algorithm.py` reconstructs the
documented Noisy HT, Direct HT and oracle formulas using only improve-mode
visible `briefing/method.md`. `reference_agreement.json` will compare all
6,000 scored decisions with the original saved held-out artifact; matching
is checked, never assumed. The unscored PPI diagnostics are not reconstructed.

The better variant adds an exact binomial human-label fallback when calibration
has no failures or no successes. The weaker variant uses only human labels.
Both retain the fixed data distribution, 100/10,000 samples, alpha and zeta.
Each is evaluated on the same three draws as the reconstructed reference.

All shortcuts start from independently generated **visible seed 42**, not the
saved test artifact, hidden seeds, test answers, or score files. The audit-only
`reference_saved` control reads the old artifact; no shortcut reads it.
The private `_original/` snapshot is for audit comparison and restoration only.
The shared cache contains reproducible synthetic artifacts, not trained models.

`summary.json` declares the exact normalization cohorts and computes the
specified coefficient-magnitude, direction-aware, experiment-weighted,
standard-deviation-normalized rank improvement over the saved reference.
Final future-attempt standard deviations are unknowable, so results include a
scientific cohort, a bounded-metric audit cohort, and individual two-attempt
cohorts. The summary also provides proposed-row-only sensitivity results.
The actual score vectors are saved so other future cohorts can be recomputed.
Impossible negative outcomes are kept out of the bounded-metric cohort;
nonfinite scores are recorded but never assigned a numeric rank.

Large artifacts and logs remain ignored. Small requested scores, result
records, source, integrity hashes and the final report are committed.
