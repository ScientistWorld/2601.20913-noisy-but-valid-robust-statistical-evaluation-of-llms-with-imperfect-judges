# Reproduction Milestones

**Current: core_claim_plus**

## Progress Log

### [2026-04-15 16:10] - method_runs
- Implemented the paper's Direct HT, Noisy HT, Oracle Noisy HT, and PPI-family hypothesis-test procedures.
- Verified the end-to-end synthetic Monte Carlo pipeline in a CPU test job.

### [2026-04-15 16:10] - core_claim
- Ran the main synthetic setting with `alpha=0.25`, `zeta=0.05`, `n_M=100`, `n_J=10000`, `R_M=0.20`, `TPR=0.9`, and `FPR=0.1`.
- Reproduced the central qualitative claim: Noisy HT had lower Type-II error than Direct HT while Type-I error stayed near the configured significance level.
- Confirmed the oracle bound behavior: Oracle Noisy HT outperformed practical Noisy HT.

### [2026-04-15 20:41] - method_runs
- Audited the continuation workspace after milestone reset from the prior claimed `core_claim`.
- Confirmed the method implementation is the paper's actual statistical testing algorithm, not a surrogate.
- Found and fixed an evaluation-separation issue: the reusable evaluator no longer imports from `method/`.
- Submitted a CPU smoke job to rerun the packaged evaluator before restoring `core_claim`.

### [2026-04-15 20:45] - core_claim_plus
- CPU test job `8696ad73-c65` completed successfully with the corrected standalone evaluator.
- Revalidated the core claim: Noisy HT Type-II error was `0.627`, below Direct HT `0.721`, while Noisy HT Type-I error was `0.028` at target `zeta=0.05`.
- Also reproduced additional synthetic diagnostics: the R_M Type-II curve and the oracle-gap comparison.
- `validate.py --compare` passed inside the compute container, including import-separation checks.

### [2026-04-15 21:21] - core_claim_plus
- CPU test job `ebfc56ce-83e` completed successfully with independent train/test evaluators.
- Held-out test slice preserved the core qualitative claim: Noisy HT Type-II error `0.628` was below Direct HT `0.732`, while Noisy HT Type-I error `0.039` stayed below `zeta=0.05`.
- Validation passed inside the compute container for scoring files, evaluator/method separation, train/test independence, and shared-path checks.

### [2026-04-15 21:42] - core_claim_plus
- Final verification preserved the claimed milestone.
- Tightened method-agnostic evaluation documentation and moved the shared synthetic data generator into `data/`.
- Confirmed the gym remains focused on the synthetic certification subset with independent train/test scoring artifacts.

### [2026-04-15 22:32] - core_claim_plus
- Final verification preserved the claimed milestone.
- Rechecked scoring files, method/problem separation, train/test independence, shared-path constraints, and root cleanliness.
- `validate.py --compare` passed locally for the packaged scoring files; no additional compute job was needed.

### [2026-04-24 05:00] - core_claim_plus
- CPU job `8f4134be-d14` reran the finalized train/test evaluation harness after the environment cleanup.
- Reconfirmed the central claim on the visible slice: Noisy HT Type-II `0.627` remained below Direct HT `0.721` while Noisy HT Type-I stayed at `0.028`.
- Reconfirmed the same qualitative claim on the held-out slice: Noisy HT Type-II `0.628` remained below Direct HT `0.732` while Noisy HT Type-I stayed at `0.039`.
- Validation passed for scores coverage, train/test key matching, train/test value differentiation, evaluator separation, and shared-path constraints.

### [2026-05-22 06:23] - core_claim
- Audited the continuation workspace and found the method implementation still matches the paper's actual Noisy HT algorithm.
- Tightened the gym contract so `method/` writes trial-level artifacts under `outputs/` and `eval/` only aggregates those artifacts into scores.
- Corrected the oracle-gap metric so the oracle row has zero gap and Noisy HT carries the practical gap.
- Demoted the current milestone from `core_claim_plus` to `core_claim` pending a fresh CPU job for the revised artifact-based pipeline.

### [2026-05-22 06:26] - core_claim
- Rechecked the continuation state and confirmed only unrelated workspace/system files remain dirty.
- Kept the current milestone at `core_claim` while submitting a fresh CPU test job for the artifact-producing method pipeline.
- The submitted job regenerates canonical, train, and held-out artifacts, aggregates scores from those artifacts, and runs `validate.py --compare`.

### [2026-05-22 06:28] - core_claim_plus
- CPU test job `abaa881d-a9e` completed successfully with the corrected artifact-based pipeline.
- Revalidated the core claim from method artifacts: Noisy HT Type-II `0.627` remained below Direct HT `0.721`, while Noisy HT Type-I `0.028` stayed below the target `zeta=0.05`.
- Revalidated additional settings: the held-out slice preserved the same qualitative claim with Noisy HT Type-II `0.628` below Direct HT `0.732`, and the R_M Type-II curve matched the packaged reference values.
- `validate.py --compare` passed inside the compute container, including evaluator/method separation, method-output reading, train/test independence, and shared-path checks.
