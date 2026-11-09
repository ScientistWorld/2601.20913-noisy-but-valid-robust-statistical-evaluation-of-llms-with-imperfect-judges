"""One CPU job, fresh evaluator processes, incremental results and cleanup."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path('/home/user')
sys.path.insert(0, str(ROOT))
from redteam.generate import generate, path

CASES = ['reference_missing', 'reference_saved', 'visible_seed_reference']
CASES += [f'{kind}_seed_{seed}' for seed in [42, 43, 44]
          for kind in ['reference', 'better', 'weaker']]
CASES += ['scenario_answers_shortcut', 'fabricated_flags_shortcut',
          'missing_flags_shortcut', 'oracle_labels_shortcut',
          'fixed_generator_shortcut', 'budget_laundering_shortcut',
          'baseline_fields_shortcut', 'oracle_comparator_shortcut',
          'point_estimate_shortcut', 'constant_always_shortcut',
          'constant_never_shortcut', 'negative_flags_shortcut',
          'nan_flags_shortcut', 'null_flags_shortcut', 'empty_rows_shortcut',
          'config_budget_shortcut', 'direct_score_shortcut', 'train_copy_shortcut']


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def agreement():
    original = json.loads((ROOT/'redteam/_original/reference.artifact.json').read_text())
    rerun = json.loads(path('reference', 1000045).read_text())
    out = {}
    for section in ['main','curve']:
        pairs = list(zip(original[section]['rows'], rerun[section]['rows']))
        mismatches = []
        for a,b in pairs:
            if a != b:
                mismatches.append(dict(saved=a, reconstructed=b))
        out[section] = dict(saved_rows=len(original[section]['rows']),
                            reconstructed_rows=len(rerun[section]['rows']),
                            mismatch_count=len(mismatches), examples=mismatches[:5])
    (ROOT/'redteam/reference_agreement.json').write_text(json.dumps(out,indent=2)+'\n')


def main():
    # Capture pristine test/evaluation files once. No shortcut reads this dir.
    original_dir = ROOT/'redteam/_original'
    original_dir.mkdir(exist_ok=True)
    for source, dest in [
            ('outputs/synthetic_test_results.json','reference.artifact.json'),
            ('scoring/scores_test.json','scores_test.json'),
            ('scoring/reference.json','reference.json')]:
        p = original_dir/dest
        if not p.exists():
            p.write_bytes((ROOT/source).read_bytes())
    protected = list((ROOT/'eval').rglob('*.py')) + [
        ROOT/'scripts/evaluate_test.sh',ROOT/'scripts/evaluate_train.sh',
        ROOT/'validate.py', ROOT/'data/synthetic.py']
    before = {str(p.relative_to(ROOT)):sha(p) for p in protected}

    # Cache all variants on identical draws. No model training is needed.
    for seed in [42, 1000045, 1000046, 1000047]:
        generate(seed)
    agreement()
    for name in CASES:
        print('RUN',name,flush=True)
        proc = subprocess.run(['bash',f'redteam/{name}/run.sh'], cwd=ROOT)
        if proc.returncode:
            print('HARNESS FAILURE',name,proc.returncode,flush=True)
        p = ROOT/'redteam'/name/'result.json'
        if p.exists():
            r = json.loads(p.read_text())
            print('RESULT',name,r.get('test_returncode',r.get('method_returncode')),flush=True)
    after = {str(p.relative_to(ROOT)):sha(p) for p in protected}
    (ROOT/'redteam/integrity.json').write_text(json.dumps(
        dict(before=before, after=after, unchanged=before==after), indent=2)+'\n')
    subprocess.run(['/usr/bin/python3','redteam/summarize.py'],cwd=ROOT,check=True)


if __name__ == '__main__':
    main()
