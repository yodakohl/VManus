#!/usr/bin/env python3
"""Independent direct-map validator; no primary imports or source selection."""
import argparse
import hashlib
import itertools
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
EXP = Path(__file__).resolve().parents[1]
ART = EXP / 'artifacts'

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def read(path):
    return json.loads(path.read_text(encoding='utf-8'))

def constraints(groups):
    first = {}
    out = []
    for i, g in enumerate(groups):
        if g in first:
            out.append([first[g], i])
        else:
            first[g] = i
    return out

def scan(groups, text, reverse=False):
    """Each start gets a fresh function dictionary; collisions are legal."""
    size = len(groups)
    rejected = [0] * len(constraints(groups))
    hits = []
    for start in range(max(0, len(text) - size + 1)):
        table = {}
        comparison = 0
        for index, group in enumerate(groups):
            char = text[start + (size - index - 1 if reverse else index)]
            if group in table:
                if table[group] != char:
                    rejected[comparison] += 1
                    break
                comparison += 1
            else:
                table[group] = char
        else:
            hits.append(start)
    survivor = [max(0, len(text) - size + 1)]
    for count in rejected:
        survivor.append(survivor[-1] - count)
    assert survivor[-1] == len(hits)
    return hits, rejected, survivor

def patterns(n):
    def extend(prefix):
        if len(prefix) == n:
            yield tuple(prefix)
        else:
            for c in range(max(prefix, default=-1) + 2):
                yield from extend(prefix + [c])
    yield from extend([])

def oracle(groups, text, reverse=False):
    classes = sorted(set(groups))
    found = set()
    for outputs in itertools.product('ab', repeat=len(classes)):
        mapping = dict(zip(classes, outputs))
        encoded = ''.join(mapping[g] for g in groups)
        if reverse:
            encoded = encoded[::-1]
        for start in range(max(0, len(text) - len(groups) + 1)):
            if text[start:start + len(groups)] == encoded:
                found.add(start)
    return sorted(found)

def controls():
    checked = 0
    for n in range(1, 5):
        for group_pattern in patterns(n):
            for size in range(8):
                for chars in itertools.product('ab', repeat=size):
                    text = ''.join(chars)
                    for reverse in (False, True):
                        assert scan(group_pattern, text, reverse)[0] == oracle(group_pattern, text, reverse)
                        checked += 1
    assert scan(['A','B','A'], 'aaa')[0] == [0]
    assert scan(['A','B','A'], 'abc')[0] == []
    assert scan(['A','A','B'], 'abb')[0] == []
    assert scan(['A','A','B'], 'abb', True)[0] == [0]
    assert scan(['A','B','A'], 'aa')[0] == []
    return {'status':'PASS', 'exhaustive_comparisons':checked, 'named_checks':5,
            'oracle':'All total maps from equality classes to binary letters, allowing collisions.'}

def lock_check():
    path = EXP / 'LOCK.json'
    lock = read(path)
    entries = lock.get('files', lock.get('entries'))
    if isinstance(entries, dict):
        entries = [{'path':p, 'sha256':h} for p,h in entries.items()]
    assert isinstance(entries, list)
    pins = {}
    for entry in entries:
        p = entry['path']
        assert not Path(p).is_absolute()
        assert digest(ROOT / p) == entry['sha256'], p
        pins[p] = entry['sha256']
    for p in [Path(__file__), EXP/'src/SPEC.json', EXP/'src/run.py']:
        assert p.relative_to(ROOT).as_posix() in pins
    return pins

def validate():
    pins = lock_check()
    spec = read(EXP / 'src/SPEC.json')
    for key in ['projections_path','native_path','worksheet_path']:
        assert spec[key] in pins
    worksheet = read(ROOT / spec['worksheet_path'])
    unit = worksheet['source_original_wrapper']['source_unit']
    inherited = read(ROOT / spec['native_path'])
    assert inherited['original_source'] == unit
    assert unit['edition'] == spec['required_native_edition']
    lines = unit['lines']
    assert [line['metadata']['locus'] for line in lines] == spec['required_loci']
    columns = unit['group_columns']
    raw_index = columns.index('ivtff_group_raw')
    original = [g for line in lines for g in line['groups']]
    groups = [g[raw_index] for g in original]
    assert len(groups) == spec['required_native_groups'] == 77
    assert inherited['full_original_group_count'] == 77
    projections = read(ROOT / spec['projections_path'])
    assert len(projections['projections']) == 70
    assert len({p['id'] for p in projections['projections']}) == 70
    for name in ['source_pin','record_pin']:
        pin = projections[name]
        assert digest(ROOT / pin['path']) == pin['sha256']
    result_path = ART / 'RESULT.json'
    result = read(result_path)
    assert result['experiment_id'] == 'GDT1410'
    assert result['status'] == 'COMPLETE_FIXED_SOURCE_EQUALITY_CAPACITY'
    assert result['native_group_count'] == 77
    assert result['distinct_native_forms'] == len(set(groups))
    assert result['equality_constraints'] == constraints(groups)
    assert result['word_meanings_assigned'] == 0
    assert result['claim_ceiling'] == spec['claim_ceiling']
    assert len(result['cases']) == 140
    receipts = []
    for i, projection in enumerate(projections['projections']):
        text, offsets = projection['text'], projection['source_offsets']
        assert len(text) == projection['characters'] == len(offsets)
        assert projection['id'] == projection['rule'] + ':' + projection['base']
        for j, direction in enumerate(spec['directions']):
            hits, rejected, survivors = scan(groups, text, direction == 'REVERSE')
            witnesses = [{'start':s,'end':s+77,'text':text[s:s+77],
                          'source_start_offset':offsets[s],
                          'source_last_offset':offsets[s+76]} for s in hits[:spec['witness_limit_per_case']]]
            expected = {'projection_id':projection['id'],'direction':direction,
                        'characters':len(text),'candidate_windows':max(0,len(text)-76),
                        'matches':len(hits),'first_rejections':rejected,'survivor_counts':survivors,
                        'witnesses':witnesses,'decision':'EQUALITY_CAPACITY_ONLY' if hits else 'NO_FIXED_GROUP_LETTER_WINDOW'}
            assert result['cases'][2*i+j] == expected, (projection['id'], direction)
            receipts.append({'projection_id':projection['id'],'direction':direction,
                             'candidate_windows':expected['candidate_windows'],'matches':len(hits)})
    receipt = {'status':'PASS_INDEPENDENT_DIRECT_MAP_VALIDATION',
               'experiment_id':'GDT1410', 'controls':controls(), 'pins':pins,
               'lock_sha256':digest(EXP/'LOCK.json'),'result_sha256':digest(result_path),
               'original_groups':77,'cases':receipts,
               'scope':'Exact fixed-source whole-group equality capacity only; source projections inherit GDT1409 provenance. No meaning, injectivity, source identity or complete writer claim.'}
    destination = ART / 'VALIDATION.json'
    if destination.exists():
        assert read(destination) == receipt
    else:
        destination.write_text(json.dumps(receipt,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf-8')
    return {'status':receipt['status'],'cases':len(receipts)}

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--controls', action='store_true')
    mode.add_argument('--validate', action='store_true')
    args = parser.parse_args()
    print(json.dumps(controls() if args.controls else validate(),sort_keys=True))
