"""Declare normalization cohorts instead of inventing unknown future ranks.

Ranking is the user-specified sum over all reference-scored cells, using
experiment weight, absolute coefficient, better direction, and population
standard deviation across the stated attempt cohort. No units-based raw sum
is presented as the gym's final rank. Future cohort-dependent ranks can differ.
"""
import json
import math
import statistics
from pathlib import Path

ROOT=Path('/home/user/redteam')


def main():
    reference=json.loads((ROOT/'_original/reference.json').read_text())
    saved=json.loads((ROOT/'reference_saved/scores.json').read_text())
    scores={p.parent.name:json.loads(p.read_text()) for p in sorted(ROOT.glob('*/scores.json'))}
    results={p.parent.name:json.loads(p.read_text()) for p in sorted(ROOT.glob('*/result.json'))}
    cells=[]
    for exp,definition in reference['experiments'].items():
        for row,rd in definition['results'].items():
            for metric,md in definition['metrics'].items():
                if md['coefficient'] == 0 or metric not in rd:
                    continue
                cells.append((exp,row,metric,definition['weight']*abs(md['coefficient']),
                              1 if md['higher_is_better'] else -1,rd['type']))

    def value(score,cell):
        return score[cell[0]][cell[1]][cell[2]]

    finite={k:v for k,v in scores.items() if all(
        isinstance(value(v,c),(int,float)) and math.isfinite(value(v,c)) for c in cells)}
    accepted={k:v for k,v in finite.items() if results[k].get('test_returncode')==0}
    scientific=[f'{k}_seed_{s}' for s in [42,43,44] for k in ['reference','better','weaker']]
    bounded=[k for k,v in accepted.items() if all(0 <= value(v,c) <= 1 for c in cells)]
    finite_cohort=[k for k in accepted if k!='negative_flags_shortcut']

    def rank(cohort, proposed_only=False):
        use=[c for c in cells if not proposed_only or c[-1]=='proposed']
        scales={c:statistics.pstdev([value(finite[k],c) for k in cohort]) for c in use}
        return {k:sum(c[3]*c[4]*(value(finite[k],c)-value(saved,c))/scales[c]
                      for c in use if scales[c]>1e-15) for k in cohort}

    sci=rank(scientific)
    sci_prop=rank(scientific,True)
    bounds=rank(bounded)
    prop=rank(bounded,True)
    finite_ranks=rank(finite_cohort)
    outlier_ranks=rank(list(accepted))
    pair={}
    for k,v in accepted.items():
        # Two-attempt normalization is an explicit admissible future cohort.
        pair[k]=rank(['reference_saved',k])[k]
    report=dict(
        formula='sum(weight * abs(coefficient) * direction * (attempt-reference_saved) / population_std_over_declared_cohort)',
        reference='reference_saved: frozen scoring/scores_test.json, recomputed by the unmodified hidden scorer',
        normalization_note='Absolute final rank depends on future attempts; these are explicit reproducible example cohorts. Constant cells contribute zero.',
        cohorts=dict(scientific=scientific,bounded=bounded,finite_without_impossible_flags=finite_cohort,
                     all_accepted_finite=list(accepted)),
        scientific_rank=sci,scientific_proposed_only_rank=sci_prop,bounded_cohort_rank=bounds,
        finite_cohort_rank=finite_ranks,outlier_cohort_rank=outlier_ranks,
        bounded_cohort_proposed_only_rank=prop,pairwise_rank=pair,
        cases={})
    for k,s in scores.items():
        report['cases'][k]=dict(
            test_returncode=results[k].get('test_returncode'),
            power=s['synthetic_power_comparison']['noisy_ht']['type2_error'],
            oracle_gap=s['oracle_gap']['noisy_ht']['oracle_gap'],
            type1=s['synthetic_type1_control']['noisy_ht']['type1_error'],
            curve={r:m['decision_error'] for r,m in s['synthetic_type2_curve'].items()},
            finite=k in finite,
            accepted=k in accepted,
            bounded_cohort_rank=bounds.get(k),pairwise_rank=pair.get(k))
    report['seed_spread']={}
    for kind in ['reference','better','weaker']:
        ks=[f'{kind}_seed_{s}' for s in [42,43,44]]
        rs=[sci[k] for k in ks]
        bs=[bounds[k] for k in ks]
        ps=[sci_prop[k] for k in ks]
        report['seed_spread'][kind]=dict(rank_min=min(rs),rank_max=max(rs),rank_range=max(rs)-min(rs),
            bounded_rank_values=bs,bounded_rank_range=max(bs)-min(bs),
            scientific_proposed_only_values=ps,scientific_proposed_only_range=max(ps)-min(ps),
            power_values=[report['cases'][k]['power'] for k in ks],
            type1_values=[report['cases'][k]['type1'] for k in ks])
    # Use standard JSON: nonfinite acceptance is recorded by its own result,
    # while the compact rank report has null for unsupported values.
    def clean(x):
        if isinstance(x,float) and not math.isfinite(x): return None
        if isinstance(x,dict): return {k:clean(v) for k,v in x.items()}
        if isinstance(x,list): return [clean(v) for v in x]
        return x
    (ROOT/'summary.json').write_text(json.dumps(clean(report),indent=2)+'\n')
    print(json.dumps(clean(report['seed_spread']),indent=2),flush=True)


if __name__=='__main__':
    main()
