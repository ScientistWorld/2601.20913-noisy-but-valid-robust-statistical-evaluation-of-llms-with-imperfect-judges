"""Validation helpers for method-produced Noisy HT synthetic artifacts."""

from __future__ import annotations

from typing import Any


EXPECTED_MAIN_CONFIG = {
    "n_trials": 1000,
    "n_m": 100,
    "n_j": 10000,
    "alpha": 0.25,
    "zeta": 0.05,
    "tpr": 0.95,
    "fpr": 0.05,
    "r_m_test": 0.20,
}

EXPECTED_CURVE_CONFIG = {
    "n_trials": 1000,
    "n_m": 100,
    "n_j": 10000,
    "alpha": 0.25,
    "zeta": 0.05,
    "tpr": 0.95,
    "fpr": 0.05,
}

EXPECTED_CURVE_SETTINGS = {"rm_0.01", "rm_0.10", "rm_0.20", "rm_0.30"}
EXPECTED_MAIN_EXPERIMENTS = {
    "synthetic_power_comparison",
    "synthetic_type1_control",
}


def _close(lhs: Any, rhs: Any) -> bool:
    if isinstance(rhs, float):
        return abs(float(lhs) - rhs) < 1e-12
    return lhs == rhs


def _require_config(config: dict[str, Any], expected: dict[str, Any], section: str) -> None:
    for key, expected_value in expected.items():
        if key not in config:
            raise ValueError(f"{section} missing config key {key!r}")
        if not _close(config[key], expected_value):
            raise ValueError(
                f"{section} config {key!r}={config[key]!r}, expected {expected_value!r}"
            )


def _require_trial_ids(rows: list[dict[str, Any]], n_trials: int, section: str) -> None:
    trials = sorted(row.get("trial") for row in rows)
    expected = list(range(n_trials))
    if trials != expected:
        raise ValueError(f"{section} trial IDs are incomplete or duplicated")


def validate_synthetic_artifact(artifact: dict[str, Any]) -> None:
    """Reject artifacts that do not match the fixed benchmark contract."""

    if artifact.get("schema") != "noisy_ht_synthetic_artifact_v1":
        raise ValueError("not a Noisy HT synthetic artifact")

    main = artifact.get("main")
    curve = artifact.get("curve")
    if not isinstance(main, dict) or not isinstance(curve, dict):
        raise ValueError("artifact must contain main and curve sections")

    _require_config(main.get("config", {}), EXPECTED_MAIN_CONFIG, "main")
    _require_config(curve.get("config", {}), EXPECTED_CURVE_CONFIG, "curve")

    main_rows = main.get("rows", [])
    curve_rows = curve.get("rows", [])
    if not isinstance(main_rows, list) or not isinstance(curve_rows, list):
        raise ValueError("artifact rows must be lists")

    n_trials = EXPECTED_MAIN_CONFIG["n_trials"]
    expected_main_rows = n_trials * len(EXPECTED_MAIN_EXPERIMENTS)
    if len(main_rows) != expected_main_rows:
        raise ValueError(f"main has {len(main_rows)} rows, expected {expected_main_rows}")

    for experiment in EXPECTED_MAIN_EXPERIMENTS:
        rows = [row for row in main_rows if row.get("experiment") == experiment]
        if len(rows) != n_trials:
            raise ValueError(f"{experiment} has {len(rows)} rows, expected {n_trials}")
        _require_trial_ids(rows, n_trials, experiment)

    unknown_main = {row.get("experiment") for row in main_rows} - EXPECTED_MAIN_EXPERIMENTS
    if unknown_main:
        raise ValueError(f"unexpected main experiments: {sorted(unknown_main)}")

    curve_trials = EXPECTED_CURVE_CONFIG["n_trials"]
    expected_curve_rows = curve_trials * len(EXPECTED_CURVE_SETTINGS)
    if len(curve_rows) != expected_curve_rows:
        raise ValueError(f"curve has {len(curve_rows)} rows, expected {expected_curve_rows}")

    for setting in EXPECTED_CURVE_SETTINGS:
        rows = [row for row in curve_rows if row.get("setting") == setting]
        if len(rows) != curve_trials:
            raise ValueError(f"{setting} has {len(rows)} rows, expected {curve_trials}")
        _require_trial_ids(rows, curve_trials, f"synthetic_type2_curve/{setting}")

    unknown_curve = {row.get("setting") for row in curve_rows} - EXPECTED_CURVE_SETTINGS
    if unknown_curve:
        raise ValueError(f"unexpected curve settings: {sorted(unknown_curve)}")
