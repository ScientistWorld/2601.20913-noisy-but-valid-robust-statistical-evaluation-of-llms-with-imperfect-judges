"""Shared I/O for the hardening-audit certifiers (leading underscore: never scored).

Every audit certifier implements the benchmark's certifier interface:
``python3 <file>.py --input <instance_dir> --output <decisions.json>``.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np


def _find_root() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / "method" / "hypothesis_tests.py").is_file():
            return parent
    raise RuntimeError("workspace root not found")


ROOT = _find_root()
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def load():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    data = {k: np.load(args.input / f"{k}.npy", mmap_mode="r")
            for k in ("calib_human", "calib_judge", "eval_judge")}
    data["alpha"] = np.load(args.input / "alpha.npy")
    data["zeta"] = np.load(args.input / "zeta.npy")
    return args, data


def per_instance(data, fn):
    out = []
    for i in range(data["calib_human"].shape[0]):
        out.append(bool(fn(np.asarray(data["calib_human"][i]),
                           np.asarray(data["calib_judge"][i]),
                           np.asarray(data["eval_judge"][i]),
                           float(data["alpha"][i]), float(data["zeta"][i]))))
    return out


def write(args, decisions) -> None:
    args.output.write_text(json.dumps({"certify": [int(bool(x)) for x in decisions]}) + "\n")


def write_raw(args, payload) -> None:
    args.output.write_text(json.dumps(payload) + "\n")


def run(fn) -> None:
    args, data = load()
    write(args, per_instance(data, fn))
