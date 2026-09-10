#!/usr/bin/env python3
"""Frozen GDT888 consequence evaluation, without a fitter or new decoder."""
import argparse
import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

E = Path(__file__).resolve().parents[1]
ROOT = E.parents[2]
OLD = ROOT / 'experiments/yolo/gdt888_alphita_joint_name_incidence'
ORDER = ['C', 'B', 'D', 'L', 'M', 'S']


def enc(x): return json.dumps(x, sort_keys=True, separators=(',', ':'))
def read(p): return json.loads(p.read_text())
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def freeze(name, data):
    p = E / 'artifacts' / name
    text = enc(data) + '\n'
    if p.exists(): assert p.read_text() == text, 'frozen output differs: ' + name
    else: p.write_text(text)


def source_counts(source):
    patterns = sorted([(k, re.findall('[a-z]+', v.lower())) for k, v in source['headwords'].items()],
                      key=lambda item: (-len(item[1]), item[0]))
    words = re.findall('[a-z]+', source['entries']['S']['body'].lower())
    counts = Counter(); i = 0
    while i < len(words):
        for role, pattern in patterns:
            if words[i:i+len(pattern)] == pattern:
                counts[role] += 1; i += len(pattern); break
        else: i += 1
    return {r: counts[r] for r in ORDER}


def predict():
    result = read(OLD / 'artifacts/RESULT.json')['panels']['IT2a']
    fit = read(OLD / 'artifacts/FIT_INPUT.json')
    source = read(OLD / 'src/SOURCE.json')
    assert result['complete'] and len(result['lexicons']) == 18
    heads = fit['panels']['IT2a']['held_heads']
    assert len(heads) == 239 and len({h['physical_folio'] for h in heads}) == 37
    expected = source_counts(source)
    assert expected == {'C': 0, 'B': 1, 'D': 1, 'L': 0, 'M': 0, 'S': 0}
    candidates = []; minima = set(); union = {}
    train = {x['paragraph_id']: x for x in fit['panels']['IT2a']['train']}
    for i, lex in enumerate(result['lexicons'], 1):
        matched = sorted([h for h in heads if h['head'] == lex['head_forms']['S']], key=lambda h: h['paragraph_id'])
        assert matched
        leaves = {h['physical_folio'] for h in matched}
        assert all(int(f[1:]) % 2 == 0 for f in leaves)
        minima.add(min(leaves, key=lambda f: int(f[1:])))
        assignments = []
        for j, solution in enumerate(result['solutions']):
            if all(solution[k] == lex[k] for k in ['head_forms', 'mention_forms']):
                assert solution['prefix_head'] == ['P1'] and solution['prefix_body'] == []
                assert solution['held_head_paragraphs'] == [h['paragraph_id'] for h in matched]
                assignments.append({'saved_solution_index': j, 'paragraphs': solution['paragraphs'],
                                    'physical_leaves': {r: train[p]['physical_folio'] for r, p in solution['paragraphs'].items()}})
        assert assignments
        for h in matched:
            assert not h['page'].startswith('f84')
            union[h['paragraph_id']] = h
        candidates.append(dict(candidate=f'K{i:02d}', saved_lexicon_index=i-1,
                               lexicon=lex, lexicon_sha256=hashlib.sha256(enc(lex).encode()).hexdigest(),
                               training_assignments=assignments, expected_counts=expected, paragraphs=matched))
    all_leaves = {h['physical_folio'] for h in union.values()}
    assert minima == {'f80', 'f104', 'f112'}
    assert all_leaves - minima == {'f108', 'f116'}
    exact = {}; positive = {}
    for c in candidates:
        for h in c['paragraphs']:
            h['phase'] = 'selection' if h['physical_folio'] in minima else 'confirmation'
        for groups, name, positives_only in [(exact, 'full_predicate_class', False), (positive, 'positive_only_class', True)]:
            constraints = sorted((form, expected[r]) for r, form in c['lexicon']['mention_forms'].items()
                                 if not positives_only or expected[r] > 0)
            key = enc([[h['paragraph_id'] for h in c['paragraphs']], constraints])
            if key not in groups: groups[key] = {'class': ('F' if not positives_only else 'P') + f'{len(groups)+1:02d}', 'members': []}
            groups[key]['members'].append(c['candidate']); c[name] = groups[key]['class']
    bindings = {str(p.relative_to(ROOT)): sha(p) for p in sorted(OLD.rglob('*'))
                if p.is_file() and '__pycache__' not in p.parts}
    predictions = dict(experiment_id='GDT913', node_order=ORDER, expected_counts=expected,
                       legacy_bindings=bindings, cache_path=fit['source'], cache_sha256=fit['source_sha256'],
                       selection_leaves=sorted(minima, key=lambda f: int(f[1:])),
                       confirmation_leaves=sorted(all_leaves-minima, key=lambda f: int(f[1:])),
                       candidates=candidates, exact_predicate_classes=list(exact.values()),
                       positive_only_classes=list(positive.values()),
                       exposure='Previously available project material; only GDT888 fit excluded even bodies. No historical blindness claimed.')
    freeze('PREDICTIONS.json', predictions)
    rows = []
    for c in candidates:
        row = dict(candidate=c['candidate'], full_class=c['full_predicate_class'], positive_class=c['positive_only_class'],
                   S_head='.'.join(c['lexicon']['head_forms']['S']),
                   selection=';'.join(h['paragraph_id']+'@'+h['page'] for h in c['paragraphs'] if h['phase']=='selection'),
                   confirmation=';'.join(h['paragraph_id']+'@'+h['page'] for h in c['paragraphs'] if h['phase']=='confirmation'))
        row.update({r+'_mention': '.'.join(c['lexicon']['mention_forms'][r]) for r in ORDER})
        row.update({r+'_expected': expected[r] for r in ORDER}); rows.append(row)
    import io
    buffer=io.StringIO(); writer=csv.DictWriter(buffer, fieldnames=list(rows[0]), delimiter='\t', lineterminator='\n');writer.writeheader();writer.writerows(rows)
    path=E/'artifacts/PREDICTIONS.tsv'
    if path.exists(): assert path.read_text()==buffer.getvalue()
    else: path.write_text(buffer.getvalue())
    print(json.dumps({'candidates':len(candidates), 'paragraphs':len(union), 'full_classes':len(exact),
                      'positive_classes':len(positive), 'selection_leaves':predictions['selection_leaves'],
                      'confirmation_leaves':predictions['confirmation_leaves'], 'held_bodies_opened':0}))


def check_lock():
    lock=read(E/'src/PREREG_LOCK.json')
    for name, digest in lock.items(): assert sha(ROOT/name)==digest, name
    p=read(E/'artifacts/PREDICTIONS.json')
    for name, digest in p['legacy_bindings'].items(): assert sha(ROOT/name)==digest, name
    return p


def evaluate(phase):
    p=check_lock()
    selection=None
    if phase=='confirmation':
        receipt=read(E/'src/SELECTION_LOCK.json')
        for name,digest in receipt.items(): assert sha(ROOT/name)==digest,name
        selection=read(E/'artifacts/SELECTION.json')
    approved={h['paragraph_id']:h for c in p['candidates'] for h in c['paragraphs'] if h['phase']==phase}
    from intake import select_frames
    frames=select_frames(ROOT/p['cache_path'],p['cache_sha256'],list(approved.values()))
    packet=dict(phase=phase, cache_sha256=p['cache_sha256'], paragraphs=frames)
    freeze(phase.upper()+'_INPUT.json',packet)
    index={f['paragraph_id']:f for f in frames}; outcomes=[]
    for c in p['candidates']:
        observations=[]
        for h in c['paragraphs']:
            if h['phase']!=phase: continue
            frame=index[h['paragraph_id']]
            inverse={tuple(v):r for r,v in c['lexicon']['mention_forms'].items()}
            assert len(inverse)==6
            counts=Counter(); hits=[]
            for ordinal,g in enumerate(frame['groups'][1:],1):
                role=inverse.get(tuple(g['sta']))
                if role is not None:
                    counts[role]+=1
                    hits.append(dict(role=role, body_ordinal_one_based=ordinal, source_group_id=g['source_group_id'],
                                     locus=g['locus'], raw=g['raw'], sta=g['sta']))
            actual={r:counts[r] for r in ORDER}
            contradictions=[dict(role=r, expected=c['expected_counts'][r], observed=actual[r],
                                 delta=actual[r]-c['expected_counts'][r]) for r in ORDER if actual[r]!=c['expected_counts'][r]]
            observations.append(dict(paragraph_id=h['paragraph_id'], page=h['page'], physical_folio=h['physical_folio'],
                                     observed_counts=actual, expected_counts=c['expected_counts'],
                                     passed=not contradictions, contradictions=contradictions, matched_groups=hits))
        status='NO_CAPACITY' if not observations else 'ALL_PASS' if all(o['passed'] for o in observations) else 'CONTRADICTED'
        outcomes.append(dict(candidate=c['candidate'], status=status, observations=observations,
                             independent_leaves=sorted({o['physical_folio'] for o in observations},key=lambda f:int(f[1:]))))
    out=dict(phase=phase,predictions_sha256=sha(E/'artifacts/PREDICTIONS.json'),
             input_sha256=sha(E/'artifacts'/ (phase.upper()+'_INPUT.json')), candidates=outcomes)
    if phase=='selection': out['survivors']=[c['candidate'] for c in outcomes if c['status']=='ALL_PASS']
    else:
        out['selection_survivors_frozen']=selection['survivors']
        out['additionally_confirmed']=[c['candidate'] for c in outcomes if c['status']=='ALL_PASS' and c['candidate'] in selection['survivors']]
        out['selection_only_no_confirmation']=[c['candidate'] for c in outcomes if c['status']=='NO_CAPACITY' and c['candidate'] in selection['survivors']]
        out['full_contract_survivors']=out['additionally_confirmed']+out['selection_only_no_confirmation']
    freeze(phase.upper()+'.json',out)
    print(json.dumps({k:v for k,v in out.items() if k!='candidates'}))
    print(json.dumps({'candidate_statuses':{c['candidate']:c['status'] for c in outcomes}}))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('phase', choices=['predict','selection','confirmation']);args=parser.parse_args()
    if args.phase=='predict': predict()
    else: evaluate(args.phase)
