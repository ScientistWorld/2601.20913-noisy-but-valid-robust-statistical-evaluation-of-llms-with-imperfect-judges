#!/usr/bin/env python3
"""Compatibility wrapper for generating scoring/scores.json.

The canonical scoring implementation lives in eval/evaluate.py so it remains
independent of method/.  This wrapper is kept for older notes/scripts that may
still reference scripts/generate_scores.py.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, "/home/user/eval")
from evaluate import main as evaluate_main  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--n-trials", default="1000")
    parser.add_argument("--seed", default="42")
    parser.add_argument("--output", default="/home/user/scoring/scores.json")
    args = parser.parse_args()

    sys.argv = [
        "evaluate.py",
        "--n-trials",
        str(args.n_trials),
        "--seed",
        str(args.seed),
        "--output",
        str(Path(args.output)),
    ]
    evaluate_main()


if __name__ == "__main__":
    main()
