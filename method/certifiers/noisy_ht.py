#!/usr/bin/env python3
"""Certifier entry point: the paper's Noisy HT procedure (Algorithm 1).

Interface (shared by every certifier under ``method/certifiers/``)::

    python3 method/certifiers/<name>.py --input <instance_dir> --output <decisions.json>

``<instance_dir>`` holds one batch of independent certification instances:

* ``calib_human.npy``  uint8 [N, n_M]  ground-truth failure labels S_M (calibration set)
* ``calib_judge.npy``  uint8 [N, n_M]  judge labels S_J' on the same calibration items
* ``eval_judge.npy``   uint8 [N, n_J]  judge labels S_J on the large judge-only set
* ``alpha.npy``        float64 [N]     target failure-rate threshold
* ``zeta.npy``         float64 [N]     significance level

The certifier writes ``{"certify": [0/1, ...]}`` (length N, input order), where
1 means "reject H0: R_M >= alpha", i.e. certify the model as reliable.

Each decision uses only that instance's own data, deterministically.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from method.hypothesis_tests import noisy_hypothesis_test_dual  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    calib_human = np.load(args.input / "calib_human.npy", mmap_mode="r")
    calib_judge = np.load(args.input / "calib_judge.npy", mmap_mode="r")
    eval_judge = np.load(args.input / "eval_judge.npy", mmap_mode="r")
    alpha = np.load(args.input / "alpha.npy")
    zeta = np.load(args.input / "zeta.npy")

    decisions = []
    for i in range(calib_human.shape[0]):
        reject, _ = noisy_hypothesis_test_dual(
            np.asarray(calib_human[i]),
            np.asarray(calib_judge[i]),
            np.asarray(eval_judge[i]),
            float(alpha[i]),
            float(zeta[i]),
        )
        decisions.append(int(bool(reject)))

    args.output.write_text(json.dumps({"certify": decisions}) + "\n")


if __name__ == "__main__":
    main()
