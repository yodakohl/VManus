#!/usr/bin/env python3
"""Separately written source/whole-map audit, not a meaning validator."""
import argparse
import copy
import csv
import json
from pathlib import Path

EXP = Path(__file__).resolve().parent.parent
ROOT = EXP.parents[2]
PRIOR = ROOT / 'experiments/yolo/gdt822_qokeey_physical_fire_context/artifacts'


def read(path):
    with path.open(newline='') as f:
        return list(csv.DictReader(f, delimiter='\t'))


def audit(rows, models, coverage):
    spec = json.loads((EXP / 'src/SPEC.json').read_text())
    contexts = [c for c in read(PRIOR/'CONTEXTS.tsv') if c['block_id'] in spec['blocks']]
    expected = {(c['locus'], e) for c in contexts for e in spec['editions']}
    assert len(contexts) == 50 and len(rows) == 150
    assert {(r['locus'], r['edition']) for r in rows} == expected
    gs = read(PRIOR/'SOURCE_GROUPS.tsv')
    source = {}
    for g in gs:
        source.setdefault((g['locus'],g['edition']),[]).append(g)
    fields = {'source_ids_json':'source_group_id', 'groups_json':'ivtff_group_raw',
              'left_json':'left_separator', 'right_json':'right_separator',
              'start_json':'paragraph_start', 'end_json':'paragraph_end'}
    counts = {(m,e):0 for m in models for e in spec['editions']}
    totals = {e:0 for e in spec['editions']}
    candidates=read(EXP/'src/CANDIDATES.tsv')
    assert len(candidates)==32
    assert {(c['model'],c['whole']) for c in candidates}=={(m,w) for m in models for w in models[m]['glosses']}
    assert all(c['confidence']=='C0' and c['motivation'] and c['unresolved_or_counterevidence'] for c in candidates)
    display=(EXP/'artifacts/READER.md').read_text().splitlines()
    for r in rows:
        assert not r['page'].startswith('f84')
        native = source[r['locus'],r['edition']]
        assert all(json.loads(r[k]) == [g[v] for g in native] for k,v in fields.items())
        c = next(c for c in contexts if c['locus'] == r['locus'])
        assert r['page'] == c['page'] and r['block_id'] == c['block_id']
        words = json.loads(r['groups_json'])
        totals[r['edition']] += len(words)
        for name,model in models.items():
            assert 1 <= len(model['glosses']) <= 8
            assert model['confidence'] == 'C0_UNCONFIRMED_WHOLES'
            counts[name,r['edition']] += sum(w in model['glosses'] for w in words)
        if r['edition']=='ZL3b':
            marker=r['locus']+': '+' | '.join(words)
            assert display.count(marker)==1
            at=display.index(marker)
            expected_display=[name+': '+' | '.join(model['glosses'].get(w,'['+w+']') for w in words) for name,model in models.items()]
            assert display[at+1:at+1+len(models)]==expected_display
    assert sum(totals.values()) == 1157
    assert len(coverage) == len(models)*3
    for c in coverage:
        assert int(c['exact_gloss_positions']) == counts[c['model'],c['edition']]
        assert int(c['source_positions']) == totals[c['edition']]
        assert c['interpretation'] == 'HYPOTHESIS_COVERAGE_NOT_ACCURACY'
    assert set(models['TRANSFORMATION']['glosses']) == set(models['FLOW']['glosses'])
    for e in spec['editions']:
        assert counts['TRANSFORMATION',e] == counts['FLOW',e]


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');args=parser.parse_args()
    rows=read(EXP/'artifacts/SOURCE_LINES.tsv');models=json.loads((EXP/'src/MODELS.json').read_text())
    coverage=read(EXP/'artifacts/COVERAGE.tsv');audit(rows,models,coverage)
    mutations={}
    for name,locus,edition,field,change in [
        ('erase_repeat','f75r.38','ZL3b','groups_json',lambda v:v[:1]+v[2:]),
        ('erase_IT_boundary','f81r.23','IT2a','end_json',lambda v:['0']*len(v)),
        ('invent_RF_boundary','f81r.23','RF1b','end_json',lambda v:['1']*len(v)),
        ('split_entity','f77r.35','RF1b','groups_json',lambda v:[s for w in v for s in (['che','aiin'] if w=='che@152;aiin' else [w])])]:
        changed=copy.deepcopy(rows)
        r=next(r for r in changed if r['locus']==locus and r['edition']==edition)
        r[field]=json.dumps(change(json.loads(r[field])))
        try:audit(changed,models,coverage)
        except AssertionError:mutations[name]='REJECTED'
        else:raise AssertionError(name)
    out=json.dumps(dict(status='PASS_SOURCE_ACCOUNTING_NOT_MEANING',same_author=True,
        source_lines=150,source_groups=1157,models=len(models),mutations=mutations,
        identical_core_coverage_not_discrimination=True,semantic_validation=False),indent=2,sort_keys=True)+'\n'
    path=EXP/'artifacts/VALIDATION.json'
    if args.check:assert path.read_text()==out
    else:path.write_text(out)
    print('GDT827 source, boundary and coverage accounting pass; no semantic proof')


if __name__ == '__main__':
    main()
