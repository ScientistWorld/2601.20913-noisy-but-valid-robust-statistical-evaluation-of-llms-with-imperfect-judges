## Hidden test, every audit certifier (hidden seed)

| Certifier | Passed | Main T2 | Curve T2 | Sweep T2 | Oracle gap | T1 (hq) | T1 worst | Rank vs ref |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| alt_ppi_pp | **FAILED** | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | -5.542 |
| better_fallback | yes | 0.354 | 0.238 | 0.420 | 0.348 | 0.029 | 0.047 | +0.301 |
| better_union | yes | 0.364 | 0.227 | 0.307 | 0.283 | 0.025 | 0.044 | +0.618 |
| noisy_ht | yes | 0.354 | 0.337 | 0.422 | 0.385 | 0.029 | 0.047 | +0.000 |
| sc_constant_always | **FAILED** | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | -5.542 |
| sc_constant_never | yes | 1.000 | 1.000 | 1.000 | 1.000 | 0.000 | 0.000 | -5.542 |
| sc_crash | **FAILED** | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | -5.542 |
| sc_empty_output | **FAILED** | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | -5.542 |
| sc_extra_fields | yes | 0.354 | 0.337 | 0.422 | 0.385 | 0.029 | 0.047 | +0.000 |
| sc_hardcoded_judge | **FAILED** | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | -5.542 |
| sc_naive_judge | **FAILED** | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | -5.542 |
| sc_nan_output | **FAILED** | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | -5.542 |
| sc_negative_output | **FAILED** | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | -5.542 |
| sc_null_output | **FAILED** | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | -5.542 |
| sc_point_estimate | **FAILED** | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | -5.542 |
| sc_pooled_calibration | **FAILED** | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | -5.542 |
| sc_train_box_prior | **FAILED** | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | -5.542 |
| weaker_conservative | yes | 0.473 | 0.376 | 0.505 | 0.455 | 0.008 | 0.025 | -0.706 |
| weaker_direct | yes | 0.733 | 0.407 | 0.322 | 0.390 | 0.043 | 0.043 | -1.089 |
| weaker_half_calibration | yes | 0.507 | 0.470 | 0.557 | 0.521 | 0.026 | 0.062 | -1.237 |
| direct_ht (evaluator row) | n/a | 0.733 | 0.407 | 0.322 | 0.390 | 0.043 | 0.043 | n/a |
| oracle_noisy_ht (evaluator row) | n/a | 0.000 | 0.000 | 0.000 | 0.000 | 0.052 | 0.052 | n/a |

Reference spread across draws (rank units): 0.109; reference rank by draw: hidden +0.000, seed101 +0.080, seed202 +0.109

## Paired gains vs the reference on identical inputs

| Variant | paired gain @hidden | paired gain @seed101 | paired gain @seed202 | min |gain| / ref spread |
|---|---:|---:|---:|---:|
| better_fallback | +0.301 | +0.285 | +0.287 | 2.62 |
| better_union | +0.618 | +0.577 | +0.538 | 4.95 |
| weaker_direct | -1.089 | -1.115 | -1.145 | 10.01 |
| weaker_conservative | -0.706 | -0.787 | -0.783 | 6.49 |
| weaker_half_calibration | -1.237 | -1.333 | -1.330 | 11.37 |
| alt_ppi_pp | FAILED | FAILED | +1.399 | 12.86 |

## Train vs test

| Certifier | Train passed | Train main/curve/sweep | Test passed | Test main/curve/sweep |
|---|---|---|---|---|
| alt_ppi_pp | **FAILED** | 1.000/1.000/1.000 | **FAILED** | 1.000/1.000/1.000 |
| better_fallback | yes | 0.320/0.214/0.411 | yes | 0.354/0.238/0.420 |
| better_union | yes | 0.318/0.203/0.299 | yes | 0.364/0.227/0.307 |
| noisy_ht | yes | 0.320/0.307/0.415 | yes | 0.354/0.337/0.422 |
| sc_hardcoded_judge | **FAILED** | 1.000/1.000/1.000 | **FAILED** | 1.000/1.000/1.000 |
| sc_train_box_prior | **FAILED** | 1.000/1.000/1.000 | **FAILED** | 1.000/1.000/1.000 |
| weaker_conservative | yes | 0.425/0.354/0.502 | yes | 0.473/0.376/0.505 |
| weaker_direct | yes | 0.745/0.393/0.324 | yes | 0.733/0.407/0.322 |
| weaker_half_calibration | **FAILED** | 1.000/1.000/1.000 | yes | 0.507/0.470/0.557 |

## Evaluator exit codes and no-argument runs

```json
{
  "evaluator_exit_codes": {
    "test_hidden": 1,
    "test_seed101": 1,
    "test_seed202": 0,
    "train": 1
  },
  "noarg_evaluate_test": {
    "sc_point_estimate": {
      "exit_code": 1,
      "scores_file_forged_after_run": false
    },
    "sc_score_forgery": {
      "exit_code": 0,
      "scores_file_forged_after_run": false
    },
    "sc_constant_never": {
      "exit_code": 0,
      "scores_file_forged_after_run": false
    },
    "sc_hardcoded_judge": {
      "exit_code": 1,
      "scores_file_forged_after_run": false
    },
    "_restored_reference_scores_identical": true
  }
}
```

Audit reference row equals saved scores_test.json reference: True
Cohort for normalization: 19 accepted scientific runs over 3 draws.
