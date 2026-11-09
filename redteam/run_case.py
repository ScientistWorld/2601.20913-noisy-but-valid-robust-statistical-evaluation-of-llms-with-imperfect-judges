"""Install one method artifact and run the restored hidden test with no args.

Only the audit controller can read _original/. Every shortcut starts from
independently generated public-seed trials and the public train-side schema.
Comparison-field shortcuts use seed 43; the other shortcuts use seed 42.
All test invocations run as new shell/Python processes, with no surviving
method process, altered evaluator, environment, or Python module state.
"""
import argparse
import copy
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path('/home/user')
sys.path.insert(0, str(ROOT))
from redteam.generate import generate, path

ARTIFACT = ROOT / 'outputs/synthetic_test_results.json'
SCORES = ROOT / 'scoring/scores_test.json'
ORIGINAL = ROOT / 'redteam/_original'
METHOD_RUNNER = ROOT / 'method/run_synthetic.py'


def mutate_shortcut(a, name):
    """SHORTCUT implementations use only the visible artifact contract."""
    for section in ['main', 'curve']:
        for row in a[section]['rows']:
            fields = [k for k in row if k.endswith(('_type2_failure', '_type1_error'))]
            for field in fields:
                is_noisy = field.startswith('noisy_ht_')
                unsafe = section == 'curve' and float(row['setting'][3:]) >= 0.25
                desired = int(unsafe) if field.endswith('_type2_failure') else 0
                if name == 'fabricated_flags_shortcut' and is_noisy:
                    row[field] = desired
                elif name == 'negative_flags_shortcut' and is_noisy:
                    row[field] = 1001 if unsafe else -1000
                elif name == 'nan_flags_shortcut' and is_noisy:
                    row[field] = float('nan')
                elif name == 'null_flags_shortcut' and is_noisy:
                    row[field] = None
                elif name == 'constant_never_shortcut' and is_noisy:
                    row[field] = int(field.endswith('_type2_failure'))
                elif name == 'constant_always_shortcut' and is_noisy:
                    row[field] = int(field.endswith('_type1_error'))
                elif name == 'baseline_fields_shortcut' and not is_noisy:
                    row[field] = 0
                elif name == 'oracle_comparator_shortcut' and field == 'oracle_noisy_ht_type2_failure':
                    row[field] = 1
                elif name == 'missing_flags_shortcut' and is_noisy and row[field] != desired:
                    del row[field]
    if name == 'empty_rows_shortcut':
        a['main']['rows'] = []
        a['curve']['rows'] = []
    if name == 'config_budget_shortcut':
        a['main']['config']['n_m'] = 1000
        a['curve']['config']['n_m'] = 1000
    return a


def run_case(name):
    folder = ROOT / 'redteam' / name
    folder.mkdir(parents=True, exist_ok=True)
    saved = {p: p.read_bytes() if p.exists() else None for p in [ARTIFACT, SCORES, METHOD_RUNNER]}
    result = dict(case=name, command=['bash', 'scripts/evaluate_test.sh'], no_arguments=True)
    try:
        if name == 'reference_missing':
            # An actual attempt to execute the shipped reference, unmodified.
            cmd = ['/usr/bin/python3', 'method/run_synthetic.py', '--output', str(ARTIFACT)]
            p = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
            (folder/'method.log').write_text(p.stdout+p.stderr)
            result.update(method_returncode=p.returncode, method_error=p.stderr)
            result['test_not_run'] = 'Reference failed before producing an artifact; stale outputs are not scored.'
            return

        # Each candidate replaces the unusable legacy method entry point with
        # its own reproducible entry point, an ordinary permitted method edit.
        # This also allows validate.py's tracked-import checks to run normally.
        # No evaluator or validation code is changed or bypassed.
        METHOD_RUNNER.write_text(
            '"""Audit candidate entry point; algorithm and artifact writer are in redteam/."""\n'
            'import sys\n'
            'sys.path.insert(0, "/home/user")\n'
            'from redteam.run_case import run_case\n'
            'if __name__ == "__main__":\n'
            f'    run_case({name!r})\n')
        result['method_entrypoint_replaced'] = True

        if name == 'reference_saved':
            # Audit control only; not used by any shortcut.
            a = json.loads((ORIGINAL/'reference.artifact.json').read_text())
        elif name.startswith(('reference_seed_', 'better_seed_', 'weaker_seed_')):
            kind, _, seed_text = name.split('_')
            seed = int(seed_text) + 1000003
            generate(seed)
            a = json.loads(path(kind if kind != 'weaker' else 'weaker', seed).read_text())
        else:
            # Comparison-row shortcuts need an independent public seed so
            # incidental equality with the saved train column cannot fail
            # the gym's generic train/test-differentiation check.
            visible_seed = 43 if name in ['visible_seed_43_reference',
                'baseline_fields_shortcut', 'oracle_comparator_shortcut'] else 42
            source = 'perfect' if name == 'fixed_generator_shortcut' else 'budget' if name == 'budget_laundering_shortcut' else 'standard'
            if source == 'standard':
                generate(visible_seed)
                kind = name if name in ['oracle_labels_shortcut', 'point_estimate_shortcut', 'scenario_answers_shortcut'] else 'reference'
            else:
                kind = name
                generate(visible_seed, [kind], source)
            a = json.loads(path(kind, visible_seed).read_text())
            if name not in ['visible_seed_reference', 'visible_seed_43_reference', 'train_copy_shortcut']:
                a = mutate_shortcut(a, name)

        ARTIFACT.parent.mkdir(exist_ok=True)
        ARTIFACT.write_text(json.dumps(a) + '\n')
        if name == 'train_copy_shortcut':
            # SHORTCUT attempt: submit the identical train-produced artifact.
            # The scorer writes metrics, but final train/test checks reject it.
            train_path = ROOT/'outputs/synthetic_train_results.json'
            train_saved = train_path.read_bytes() if train_path.exists() else None
            train_path.write_bytes(ARTIFACT.read_bytes())
            train_scores = ROOT/'scoring/scores_train.json'
            train_score_saved = train_scores.read_bytes() if train_scores.exists() else None
            try:
                p = subprocess.run(['bash','scripts/evaluate_train.sh'], cwd=ROOT, capture_output=True, text=True)
                (folder/'train.log').write_text(p.stdout+p.stderr)
                result['train_returncode'] = p.returncode
                if train_scores.exists():
                    (folder/'scores_train.json').write_bytes(train_scores.read_bytes())
            finally:
                for pth, data in [(train_path,train_saved),(train_scores,train_score_saved)]:
                    if data is None:
                        pth.unlink(missing_ok=True)
                    else:
                        pth.write_bytes(data)
        if name == 'direct_score_shortcut':
            # SHORTCUT attempt: directly write scores. Hidden eval overwrites it.
            forged = {'synthetic_power_comparison': {'noisy_ht': {'type2_error': -1000}}}
            SCORES.write_text(json.dumps(forged))

        (folder/'artifact.artifact.json').write_bytes(ARTIFACT.read_bytes())
        result['artifact_sha256'] = hashlib.sha256(ARTIFACT.read_bytes()).hexdigest()
        # Remove stale scores so failures cannot be mistaken for successes.
        if name != 'direct_score_shortcut':
            SCORES.unlink(missing_ok=True)
        proc = subprocess.run(['bash', 'scripts/evaluate_test.sh'], cwd=ROOT,
                              capture_output=True, text=True)
        (folder/'evaluator.log').write_text(proc.stdout+proc.stderr)
        result['test_returncode'] = proc.returncode
        if SCORES.exists():
            (folder/'scores.json').write_bytes(SCORES.read_bytes())
            if name == 'direct_score_shortcut':
                result['forged_score_survived'] = json.loads(SCORES.read_text()) == forged
        else:
            result['scores_missing'] = True
        if proc.returncode:
            result['test_error'] = proc.stderr[-3000:]
    finally:
        (folder/'result.json').write_text(json.dumps(result, indent=2)+'\n')
        for p, data in saved.items():
            if data is None:
                p.unlink(missing_ok=True)
            else:
                p.write_bytes(data)


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('name')
    run_case(p.parse_args().name)
