"""Compute genuine trials on the job node; cache only within redteam/.

No hidden evaluator, score, test seed, saved test artifact, or paper is read
here. Seed offsets for audit-only repeat runs are supplied by the caller.
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from data.synthetic import generate_synthetic_data
from redteam.algorithm import (direct, noisy, better, oracle,
                               oracle_labels_shortcut, point_estimate_shortcut)

CACHE = ROOT / 'redteam/_cache'
KINDS = ['reference', 'better', 'weaker', 'oracle_labels_shortcut',
         'point_estimate_shortcut', 'scenario_answers_shortcut']


def path(kind, seed):
    return CACHE / f'{kind}_{seed}.artifact.json'


def generate(seed, kinds=KINDS, source='standard'):
    if all(path(k, seed).exists() for k in kinds):
        return
    conf = dict(n_trials=1000, n_m=100, n_j=10000, alpha=0.25,
                zeta=0.05, tpr=0.95, fpr=0.05, seed=seed)
    arts = {k: {'schema': 'noisy_ht_synthetic_artifact_v1',
                'main': {'config': dict(conf, r_m_test=0.20), 'rows': []},
                'curve': {'config': dict(conf), 'rows': []}} for k in kinds}

    def draw(rm, s):
        # These two source choices are explicitly SHORTCUTS: the reported
        # benchmark configuration remains fixed while actual data change.
        return generate_synthetic_data(1000 if source == 'budget' else 100,
                                       10000, rm,
                                       1.0 if source == 'perfect' else 0.95,
                                       0.0 if source == 'perfect' else 0.05, s)

    def decisions(sm, sj, hidden_sm, uj, rm):
        return dict(reference=noisy(sm, sj, uj), better=better(sm, sj, uj),
                    weaker=direct(sm),
                    oracle_labels_shortcut=oracle_labels_shortcut(hidden_sm),
                    point_estimate_shortcut=point_estimate_shortcut(sm, sj, uj),
                    scenario_answers_shortcut=rm < 0.25,
                    fixed_generator_shortcut=noisy(sm, sj, uj),
                    budget_laundering_shortcut=noisy(sm, sj, uj))

    for trial in range(1000):
        for rm, experiment, suffix, off in [
                (0.20, 'synthetic_power_comparison', 'type2_failure', 0),
                (0.25, 'synthetic_type1_control', 'type1_error', 1)]:
            sm, sj, hidden_sm, uj = draw(rm, seed+trial*2+off)
            ds = decisions(sm, sj, hidden_sm, uj, rm)
            baseline = {'direct_ht': direct(sm), 'oracle_noisy_ht': oracle(uj)}
            for k, art in arts.items():
                ds_k = dict(baseline, noisy_ht=ds[k])
                row = dict(experiment=experiment, trial=trial)
                row.update({f'{m}_{suffix}': int(not d if suffix == 'type2_failure' else d)
                            for m, d in ds_k.items()})
                art['main']['rows'].append(row)
        if trial % 200 == 0:
            print('main', seed, source, trial, flush=True)

    for rm in [0.01, 0.10, 0.20, 0.30]:
        for trial in range(1000):
            sm, sj, hidden_sm, uj = draw(rm, seed+trial*3+int(rm*100)+10000)
            ds = decisions(sm, sj, hidden_sm, uj, rm)
            for k, art in arts.items():
                art['curve']['rows'].append(dict(experiment='synthetic_type2_curve',
                    setting=f'rm_{rm:.2f}', trial=trial,
                    noisy_ht_type2_failure=int(not ds[k])))
        print('curve', seed, source, rm, flush=True)

    CACHE.mkdir(parents=True, exist_ok=True)
    for k, art in arts.items():
        path(k, seed).write_text(json.dumps(art) + '\n')


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--seed', type=int, default=42)
    p.add_argument('--source', choices=['standard', 'perfect', 'budget'], default='standard')
    args = p.parse_args()
    kinds = KINDS if args.source == 'standard' else [
        'fixed_generator_shortcut' if args.source == 'perfect' else 'budget_laundering_shortcut']
    generate(args.seed, kinds, args.source)
