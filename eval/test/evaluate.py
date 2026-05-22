#!/usr/bin/env python3
"""Aggregate held-out test-slice artifacts into benchmark scores.

The held-out pass scores the same experiment/method entries that were present
in ``scoring/scores_train.json``. It reads method artifacts only and does not
import or execute anything from ``method/``.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

SLICE = "test"


def mean(values: list[int | float]) -> float:
    if not values:
        raise ValueError("cannot average an empty list")
    return float(sum(values) / len(values))


def rounded(value: float) -> float:
    return round(float(value), 4)


def load_artifact(path: Path) -> dict[str, Any]:
    artifact = json.loads(path.read_text())
    if artifact.get("schema") != "noisy_ht_synthetic_artifact_v1":
        raise ValueError(f"{path} is not a Noisy HT synthetic artifact")
    return artifact


def method_fields(rows: list[dict[str, Any]], suffix: str) -> list[str]:
    fields: set[str] = set()
    for row in rows:
        fields.update(key for key in row if key.endswith(suffix))
    return sorted(fields)


def method_name(field: str, suffix: str) -> str:
    return field[: -len(suffix)]


def summarize_rows(
    rows: list[dict[str, Any]], suffix: str, output_metric: str
) -> dict[str, dict[str, float]]:
    scores: dict[str, dict[str, float]] = {}
    for field in method_fields(rows, suffix):
        values = [row[field] for row in rows if field in row]
        scores[method_name(field, suffix)] = {output_metric: rounded(mean(values))}
    return scores


def build_curve_scores(rows: list[dict[str, Any]]) -> dict[str, dict[str, float]]:
    suffix = "_type2_failure"
    grouped: dict[str, list[int | float]] = {}
    for row in rows:
        setting = row["setting"]
        for field in (key for key in row if key.endswith(suffix)):
            method = method_name(field, suffix)
            entry = setting if method == "noisy_ht" else f"{method}__{setting}"
            grouped.setdefault(entry, []).append(row[field])
    return {
        entry: {"type2_error": rounded(mean(values))}
        for entry, values in sorted(grouped.items())
    }


def build_oracle_gap_scores(
    power_scores: dict[str, dict[str, float]],
) -> dict[str, dict[str, float]]:
    if "oracle_noisy_ht" not in power_scores:
        return {}
    oracle = power_scores["oracle_noisy_ht"]["type2_error"]
    scores = {
        "oracle_noisy_ht": {
            "type2_error_noisy": oracle,
            "oracle_gap": 0.0,
        }
    }
    for method, metrics in sorted(power_scores.items()):
        if method in {"oracle_noisy_ht", "direct_ht"}:
            continue
        type2 = metrics["type2_error"]
        scores[method] = {
            "type2_error_noisy": type2,
            "oracle_gap": rounded(type2 - oracle),
        }
    return scores


def build_diagnostics(artifact: dict[str, Any]) -> dict[str, Any]:
    diagnostics: dict[str, Any] = {}
    ppi_rows = artifact.get("_diagnostics", {}).get("rows", [])
    if ppi_rows:
        method_keys = sorted(
            key
            for row in ppi_rows
            for key, value in row.items()
            if key not in {"experiment", "trial"} and isinstance(value, (int, float))
        )
        diagnostics["ppi_oracle_ordering_type2"] = {
            key: rounded(mean([row[key] for row in ppi_rows if key in row]))
            for key in method_keys
        }
    return diagnostics


def build_scores(artifact: dict[str, Any], artifact_path: Path) -> dict[str, Any]:
    main_rows = artifact["main"]["rows"]
    power_rows = [
        row for row in main_rows if row["experiment"] == "synthetic_power_comparison"
    ]
    type1_rows = [
        row for row in main_rows if row["experiment"] == "synthetic_type1_control"
    ]

    power_scores = summarize_rows(power_rows, "_type2_failure", "type2_error")
    scores: dict[str, Any] = {
        "_metadata": {
            "schema": "noisy_ht_slice_scores_v1",
            "slice": SLICE,
            "artifact": str(artifact_path),
        },
        "synthetic_power_comparison": power_scores,
        "oracle_gap": build_oracle_gap_scores(power_scores),
        "synthetic_type2_curve": build_curve_scores(artifact["curve"]["rows"]),
        "synthetic_type1_control": summarize_rows(
            type1_rows, "_type1_error", "type1_error"
        ),
    }

    diagnostics = build_diagnostics(artifact)
    if diagnostics:
        scores["_diagnostics"] = diagnostics
    return scores


def score_experiments(scores: dict[str, Any]) -> dict[str, dict[str, Any]]:
    raw = scores.get("experiments", scores)
    return {
        exp_name: exp_scores.get("results", exp_scores)
        for exp_name, exp_scores in raw.items()
        if not exp_name.startswith("_") and isinstance(exp_scores, dict)
    }


def filter_to_train_entries(
    test_scores: dict[str, Any], train_scores: dict[str, Any]
) -> dict[str, Any]:
    train_experiments = score_experiments(train_scores)
    test_experiments = score_experiments(test_scores)
    filtered: dict[str, Any] = {
        "_metadata": {
            **test_scores.get("_metadata", {}),
            "matched_train_methods_from": "scoring/scores_train.json",
        }
    }
    missing: list[str] = []

    for exp_name, train_methods in train_experiments.items():
        if exp_name not in test_experiments:
            missing.append(exp_name)
            continue
        filtered[exp_name] = {}
        for method, train_metrics in train_methods.items():
            if method.startswith("_"):
                continue
            if method not in test_experiments[exp_name]:
                missing.append(f"{exp_name}.{method}")
                continue
            filtered[exp_name][method] = {}
            for metric in train_metrics:
                if metric not in test_experiments[exp_name][method]:
                    missing.append(f"{exp_name}.{method}.{metric}")
                    continue
                filtered[exp_name][method][metric] = test_experiments[exp_name][method][
                    metric
                ]

    if missing:
        missing_text = "\n  - ".join(missing)
        raise ValueError(
            "held-out artifact cannot score every train entry; missing:\n"
            f"  - {missing_text}"
        )
    return filtered


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--artifact", type=Path, default=Path("outputs/synthetic_test_results.json")
    )
    parser.add_argument(
        "--output", type=Path, default=Path("scoring/scores_test.json")
    )
    parser.add_argument(
        "--train-scores", type=Path, default=Path("scoring/scores_train.json")
    )
    args = parser.parse_args()

    if not args.train_scores.exists():
        raise FileNotFoundError(
            f"{args.train_scores} does not exist; run the train-slice scorer first"
        )

    raw_test_scores = build_scores(load_artifact(args.artifact), args.artifact)
    train_scores = json.loads(args.train_scores.read_text())
    scores = filter_to_train_entries(raw_test_scores, train_scores)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(scores, indent=2) + "\n")
    print(f"Held-out test slice scores written to {args.output}")


if __name__ == "__main__":
    main()
