#!/usr/bin/env python3
"""Hardening audit: run the reference, variants and shortcuts through the tests.

Phases (all results under redteam/hardening/results/):
  A. hidden test (hidden seed): every audit certifier in one evaluator run
  B. hidden-test generator at two audit seeds: scientific certifiers only
  C. public train slice: scientific certifiers + train-tuned shortcuts
  D. ``bash scripts/evaluate_test.sh`` with no arguments, with a single
     shortcut as the only certifier on disk (backup/restore of the reference)
Then ``summarize.py`` computes ranks.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CERTS = HERE / "certifiers"
RESULTS = HERE / "results"
RUNS = HERE / "_runs"
PY = sys.executable

SCIENTIFIC = ["noisy_ht", "better_fallback", "better_union", "weaker_direct",
              "weaker_conservative", "weaker_half_calibration", "alt_ppi_pp"]
PHASE_D_ONLY = ["sc_score_forgery"]
PHASE_D = ["sc_point_estimate", "sc_score_forgery", "sc_constant_never", "sc_hardcoded_judge"]
TRAIN_EXTRA = ["sc_train_box_prior", "sc_hardcoded_judge"]
AUDIT_SEEDS = [101, 202]


def stage(group: str, names: list[str]) -> Path:
    d = RUNS / group
    if d.exists():
        shutil.rmtree(d)
    d.mkdir(parents=True)
    shutil.copy(CERTS / "_common.py", d / "_common.py")
    for name in names:
        shutil.copy(CERTS / f"{name}.py", d / f"{name}.py")
    return d


def run_eval(evaluator: str, cert_dir: Path, out: Path, extra: list[str]) -> int:
    cmd = [PY, str(ROOT / "eval" / evaluator / "evaluate.py"),
           "--certifier-dir", str(cert_dir), "--output", str(out)] + extra
    proc = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True)
    out.with_suffix(".log").write_text(proc.stdout + "\n--- stderr ---\n" + proc.stderr)
    print(f"[audit] {' '.join(cmd[1:])} -> exit {proc.returncode}", flush=True)
    return proc.returncode


def phase_d(record: dict) -> None:
    method_dir = ROOT / "method" / "certifiers"
    ref_file = method_dir / "noisy_ht.py"
    scores_file = ROOT / "scoring" / "scores_test.json"
    ref_backup = ref_file.read_bytes()
    scores_backup = scores_file.read_bytes() if scores_file.exists() else None
    try:
        for name in PHASE_D:
            ref_file.unlink()
            shutil.copy(CERTS / "_common.py", method_dir / "_common.py")
            shutil.copy(CERTS / f"{name}.py", method_dir / f"{name}.py")
            try:
                proc = subprocess.run(["bash", "scripts/evaluate_test.sh"], cwd=str(ROOT),
                                      capture_output=True, text=True)
                (RESULTS / f"noarg_{name}.log").write_text(proc.stdout + "\n--- stderr ---\n" + proc.stderr)
                text = scores_file.read_text() if scores_file.exists() else ""
                (RESULTS / f"noarg_{name}.json").write_text(text)
                try:
                    forged = bool(json.loads(text).get("_forged")) if text else None
                except json.JSONDecodeError:
                    forged = None
                record[name] = {"exit_code": proc.returncode, "scores_file_forged_after_run": forged}
                print(f"[audit] no-arg evaluate_test.sh with only {name}: exit {proc.returncode}", flush=True)
            finally:
                (method_dir / f"{name}.py").unlink(missing_ok=True)
                (method_dir / "_common.py").unlink(missing_ok=True)
                ref_file.write_bytes(ref_backup)
    finally:
        ref_file.write_bytes(ref_backup)
        if scores_backup is not None:
            scores_file.write_bytes(scores_backup)
    record["_restored_reference_scores_identical"] = (
        scores_backup is not None and scores_file.read_bytes() == scores_backup)


def main() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    all_names = sorted(p.stem for p in CERTS.glob("*.py") if not p.name.startswith("_"))
    combined = [n for n in all_names if n not in PHASE_D_ONLY]
    exits: dict = {}

    d = stage("hidden_all", combined)
    exits["test_hidden"] = run_eval("test", d, RESULTS / "test_hidden.json", [])
    d = stage("scientific", SCIENTIFIC)
    for seed in AUDIT_SEEDS:
        exits[f"test_seed{seed}"] = run_eval("test", d, RESULTS / f"test_seed{seed}.json",
                                             ["--audit-seed", str(seed)])
    d = stage("train", SCIENTIFIC + TRAIN_EXTRA)
    exits["train"] = run_eval("train", d, RESULTS / "train.json", [])

    noarg: dict = {}
    phase_d(noarg)
    (RESULTS / "runs.json").write_text(json.dumps({"evaluator_exit_codes": exits,
                                                   "noarg_evaluate_test": noarg}, indent=2) + "\n")
    shutil.rmtree(RUNS, ignore_errors=True)


if __name__ == "__main__":
    main()
