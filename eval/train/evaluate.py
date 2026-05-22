#!/usr/bin/env python3
"""Aggregate visible train-slice method artifacts into benchmark scores.

This evaluator is intentionally artifact-only: it reads outputs produced by a
method runner and does not import or execute anything from ``method/``.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

EVAL_ROOT = Path(__file__).resolve().parents[1]
if str(EVAL_ROOT) not in sys.path:
    sys.path.insert(0, str(EVAL_ROOT))

from artifact_validation import validate_synthetic_artifact

SLICE = "train"


def mean(values: list[int | float]) -> float:
    if not values:
        raise ValueError("cannot average an empty list")
    return float(sum(values) / len(values))


def rounded(value: float) -> float:
    return round(float(value), 4)


def load_artifact(path: Path) -> dict[str, Any]:
    artifact = json.loads(path.read_text())
    validate_synthetic_artifact(artifact)
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


def parse_rm(setting: str) -> float:
    if not setting.startswith("rm_"):
        raise ValueError(f"unexpected curve setting: {setting}")
    return float(setting.removeprefix("rm_"))


def build_curve_scores(
    rows: list[dict[str, Any]], alpha: float
) -> dict[str, dict[str, float]]:
    suffix = "_type2_failure"
    grouped: dict[str, dict[str, list[int | float]]] = {}
    for row in rows:
        setting = row["setting"]
        rm = parse_rm(setting)
        for field in (key for key in row if key.endswith(suffix)):
            method = method_name(field, suffix)
            entry = setting if method == "noisy_ht" else f"{method}__{setting}"
            raw_type2_failure = row[field]
            decision_error = (
                raw_type2_failure if rm < alpha else 1 - raw_type2_failure
            )
            metrics = grouped.setdefault(
                entry, {"type2_error": [], "decision_error": []}
            )
            metrics["type2_error"].append(raw_type2_failure)
            metrics["decision_error"].append(decision_error)
    return {
        entry: {
            "type2_error": rounded(mean(metrics["type2_error"])),
            "decision_error": rounded(mean(metrics["decision_error"])),
        }
        for entry, metrics in sorted(grouped.items())
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
        "synthetic_type2_curve": build_curve_scores(
            artifact["curve"]["rows"], artifact["curve"]["config"]["alpha"]
        ),
        "synthetic_type1_control": summarize_rows(
            type1_rows, "_type1_error", "type1_error"
        ),
    }

    diagnostics = build_diagnostics(artifact)
    if diagnostics:
        scores["_diagnostics"] = diagnostics
    return scores


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--artifact", type=Path, default=Path("outputs/synthetic_train_results.json")
    )
    parser.add_argument(
        "--output", type=Path, default=Path("scoring/scores_train.json")
    )
    args = parser.parse_args()

    scores = build_scores(load_artifact(args.artifact), args.artifact)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(scores, indent=2) + "\n")
    print(f"Train slice scores written to {args.output}")


if __name__ == "__main__":
    main()
