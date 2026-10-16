#!/usr/bin/env python3
"""Independent source partition and expanded invocation-string validation."""
import hashlib
import itertools
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PLAN = HERE/'E1063_CONSTRUCTION_PLAN_20261016.json'
LOCK = HERE/'E1063_CODE_LOCK_20261016.json'
BUILD = HERE/'E1063_BUILD_20261016.py'
OUTPUT = HERE/'E1063_SCAFFOLD_20261016.json'
VALIDATION = HERE/'E1063_VALIDATION_20261016.json'


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def read(p):
    return json.loads(p.read_text())


def classify(raw):
    if not raw.startswith('qok'):
        return None
    rest = raw[3:]
    if rest.endswith('dy'):
        core, family, root = rest[:-2], 'D', 'F'
    elif rest.endswith('y'):
        core, family, root = rest[:-1], 'Y', 'G'
    else:
        return None
    if any(c != 'e' for c in core):
        return None
    return family, root, len(core)


def normal_form(factors):
    expanded = []
    for f in factors:
        assert isinstance(f['exponent'],int) and f['exponent'] >= 0
        expanded.extend([(f['root'],f['source_group_id'])]*f['exponent'])
    result = []
    for root, same in itertools.groupby(expanded,lambda pair:pair[0]):
        invocations = list(same)
        ids = list(dict.fromkeys(pair[1] for pair in invocations))
        result.append({'root':root,'exponent':len(invocations),'source_ids':ids})
    return result


def joined(left, right):
    return (int(right['source_group_index']) == int(left['source_group_index'])+1
            and left['right_separator'] == 'DEFINITE_SPACE'
            and right['left_separator'] == 'DEFINITE_SPACE')


def boundary(groups, begin, end, side):
    if side == 'left':
        if begin == 0:
            return {'reason':'line_start','source_id':None}
        neighbor, a, b = groups[begin-1], groups[begin-1], groups[begin]
    else:
        if end == len(groups):
            return {'reason':'line_end','source_id':None}
        neighbor, a, b = groups[end], groups[end-1], groups[end]
    if classify(neighbor['ivtff_group_raw']) is None:
        reason = 'unknown'
    elif int(b['source_group_index']) != int(a['source_group_index'])+1:
        reason = 'nonconsecutive'
    else:
        assert not joined(a,b)
        reason = 'uncertain_seam'
    return {'reason':reason,'source_id':neighbor['source_group_id']}


def main():
    lock = read(LOCK)
    pins = {p['path']:p['sha256'] for p in lock['files']}
    assert len(pins) == len(lock['files'])
    for path, digest in pins.items():
        assert sha(ROOT/path) == digest, path
    for path in (PLAN, BUILD, Path(__file__).resolve()):
        assert str(path.relative_to(ROOT)) in pins
    plan = read(PLAN)
    expected_pins = {str(PLAN.relative_to(ROOT)):sha(PLAN)}
    for p in plan['inputs']:
        assert sha(ROOT/p['path']) == p['sha256'], p['path']
        expected_pins[p['path']] = p['sha256']
    for p in (BUILD,Path(__file__).resolve()):
        expected_pins[str(p.relative_to(ROOT))] = sha(p)
    output = read(OUTPUT)
    assert output['schema_version'] == 1
    assert output['idea'] == 'IDEA001063'
    assert output['status'] == 'PARTIAL_SHARED_POWER_CONSTRUCTION_NO_MEANING_SELECTION'
    assert all(pins.get(p) == h for p,h in expected_pins.items())
    assert output['pins'] == [{'path':p,'sha256':h} for p,h in sorted(pins.items())]
    assert output['code_lock'] == {'path':str(LOCK.relative_to(ROOT)),'sha256':sha(LOCK),'locked_utc':lock['locked_utc']}
    # Source-free checks of algebra and literal matching, after the lock check.
    assert classify('qokdy') == ('D','F',0)
    assert classify('qokeeey') == ('Y','G',3)
    assert classify('qokedy<!corr?>') is None and classify('qokXy') is None
    fixture = [{'root':'F','exponent':1,'source_group_id':'a'},
               {'root':'G','exponent':0,'source_group_id':'b'},
               {'root':'F','exponent':2,'source_group_id':'c'}]
    assert normal_form(fixture) == [{'root':'F','exponent':3,'source_ids':['a','c']}]
    fixture[1]['exponent'] = 1
    assert [x['root'] for x in normal_form(fixture)] == ['F','G','F']
    profiles = {}
    for name in ('E1063_DY_PROFILES_20261016.json','E1063_Y_PROFILES_20261016.json'):
        for p in read(HERE/name)['profiles']:
            assert p['form'] not in profiles
            profiles[p['form']] = p
    expected_forms = sorted('qok'+'e'*n+suffix for suffix in ('dy','y') for n in range(5))
    assert sorted(profiles) == output['profiled_forms'] == expected_forms
    source_units, annotations, blocks, unknown_spans, accounts = [],[],[],[],[]
    seen_ids = set()
    profile_occurrences = Counter()
    for document in plan['source_scope']['documents']:
        for unit in read(ROOT/document)['units']:
            reader = unit['edition']
            page = unit['lines'][0]['metadata']['page']
            assert page in ('f75r','f75v')
            unit_id = page+'_'+reader
            source_units.append({'unit_id':unit_id,'source_path':document,'source_unit':unit})
            count = Counter(source_groups=0,candidates=0,unknown_groups=0,blocks=0,unknown_spans=0)
            for line in unit['lines']:
                locus = line['metadata']['locus']
                groups = [dict(zip(unit['group_columns'],row)) for row in line['groups']]
                for g in groups:
                    assert len(g) == len(unit['group_columns'])
                    sid, raw = g['source_group_id'],g['ivtff_group_raw']
                    assert sid not in seen_ids
                    seen_ids.add(sid)
                    c = classify(raw)
                    count['source_groups'] += 1
                    count['candidates' if c else 'unknown_groups'] += 1
                    profile_occurrences[(reader,raw)] += 1
                    annotations.append({'unit_id':unit_id,'source_group_id':sid,'locus':locus,'raw':raw,
                                        'status':'CANDIDATE' if c else 'UNKNOWN','family':c[0] if c else None,
                                        'root':c[1] if c else None,'e_count':c[2] if c else None,
                                        'exponents':{'ZERO':c[2],'ONE':c[2]+1} if c else None})
                # Connected components over source positions with candidate links.
                marks = [classify(g['ivtff_group_raw']) is not None for g in groups]
                starts = [i for i in range(len(groups)) if marks[i] and (i==0 or not marks[i-1] or not joined(groups[i-1],groups[i]))]
                for begin in starts:
                    end = begin+1
                    while end < len(groups) and marks[end] and joined(groups[end-1],groups[end]):
                        end += 1
                    selected = groups[begin:end]
                    block_id = 'B%04d' % (len(blocks)+1)
                    terms = []
                    for g in selected:
                        family, root, n = classify(g['ivtff_group_raw'])
                        terms.append({'source_group_id':g['source_group_id'],'raw':g['ivtff_group_raw'],'family':family,'root':root,'e_count':n})
                    formulas = {}
                    for label,delta in [('ZERO',0),('ONE',1)]:
                        factors = [{'root':t['root'],'exponent':t['e_count']+delta,'source_group_id':t['source_group_id']} for t in terms]
                        formulas[label] = {'ordered_factors':factors,'normal_form':normal_form(factors)}
                    blocks.append({'block_id':block_id,'unit_id':unit_id,'locus':locus,'source_ids':[g['source_group_id'] for g in selected],
                                   'terms':terms,'formulas':formulas,'input':'s_'+block_id,
                                   'left_boundary':boundary(groups,begin,end,'left'),'right_boundary':boundary(groups,begin,end,'right')})
                    count['blocks'] += 1
                for candidate, indices in itertools.groupby(range(len(groups)),lambda i:marks[i]):
                    ix = list(indices)
                    if not candidate:
                        unknown_spans.append({'unit_id':unit_id,'locus':locus,'source_ids':[groups[i]['source_group_id'] for i in ix],
                                              'raw':[groups[i]['ivtff_group_raw'] for i in ix]})
                        count['unknown_spans'] += 1
            assert count['source_groups'] == count['candidates']+count['unknown_groups']
            accounts.append(dict(unit_id=unit_id,**dict(count)))
    assert len(source_units) == 6
    assert output['source_units'] == source_units
    assert output['annotations'] == annotations
    assert output['blocks'] == blocks
    assert output['unknown_spans'] == unknown_spans
    totals = {key:sum(row[key] for row in accounts) for key in ['source_groups','candidates','unknown_groups','blocks','unknown_spans']}
    totals['source_units'] = 6
    assert output['accounting'] == {'units':accounts,'total':totals}
    for (reader,raw),n in profile_occurrences.items():
        if raw in profiles:
            editions = profiles[raw].get('editions',profiles[raw].get('readers'))
            assert n <= editions[reader]['count'], (reader,raw,n)
    candidate_ids = [t['source_group_id'] for b in blocks for t in b['terms']]
    unknown_ids = [sid for s in unknown_spans for sid in s['source_ids']]
    assert set(candidate_ids).isdisjoint(unknown_ids)
    assert len(candidate_ids)+len(unknown_ids) == len(seen_ids)
    assert set(candidate_ids+unknown_ids) == seen_ids
    receipt = {'idea':'IDEA001063','status':'PASS_SOURCE_AND_ALGEBRA_ACCOUNTING_ONLY',
               'implementation_lock_utc':lock['locked_utc'],'code_lock_sha256':sha(LOCK),'plan_sha256':sha(PLAN),'derivation_sha256':sha(OUTPUT),
               'source_units':6,'accounting':totals,'independent_method':'Literal prefix/suffix recognizer, source-position connected blocks, and expanded ordered F/G invocation strings compressed by same-root runs; no primary import.',
               'limits':['Source and conditional symbolic algebra only; no phoneme, operation, state type, participant, meaning or native success selected.','Zero factors remain in source terms and ordered factors; no F/G commutation and no semantic reset inferred from block boundaries.','No new raw source, image, reserve or corpus census.']}
    VALIDATION.write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    print(json.dumps(receipt,sort_keys=True))


if __name__ == '__main__':
    main()
