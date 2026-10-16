#!/usr/bin/env python3
"""Frozen exploratory six-group literal census; no meanings assigned."""
import csv
import hashlib
import json
import re
from collections import defaultdict
from functools import lru_cache
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
ROOT = BASE.parents[2]

def load(p):
    return json.loads((ROOT / p).read_text())

def write(name, value):
    (BASE / 'artifacts' / name).write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + '\n')

def unique_parser(signs):
    @lru_cache(None)
    def parses(s):
        if not s:
            return ((),)
        found = []
        for sign in signs:
            if s.startswith(sign):
                for tail in parses(s[len(sign):]):
                    found.append((sign,) + tail)
                    if len(found) > 1:
                        return tuple(found)
        return tuple(found)
    def one(s):
        p = parses(s)
        return list(p[0]) if len(p) == 1 else None
    return one

def classify(rows, one):
    if len(rows) != 6 or len({(r['edition'], r['page'], r['locus'], r['kind']) for r in rows}) != 1 or rows[0]['kind'] != 'P':
        return None
    if any(int(b['source_group_index']) != int(a['source_group_index']) + 1 or a['right_separator'] != 'DEFINITE_SPACE' or b['left_separator'] != 'DEFINITE_SPACE' for a, b in zip(rows, rows[1:])):
        return None
    raw = [r['ivtff_group_raw'] for r in rows]
    if raw[2] != raw[3] or raw[4] != 'l' + raw[1]:
        return None
    p = [one(s) for s in raw]
    strict = False
    if all(x is not None for x in p) and len(p[0]) == len(p[5]):
        delta = [(a, b) for a, b in zip(p[0], p[5]) if a != b]
        strict = delta == [('t', 'k')]
    return dict(edition=rows[0]['edition'], page=rows[0]['page'], locus=rows[0]['locus'], start_group=int(rows[0]['source_group_index']), raw=raw, parses=p, strict=strict)

def controls(one):
    def rows(words):
        return [dict(edition='IT2a', page='f75v', locus='f75v.46', kind='P', source_group_index=str(i + 1), ivtff_group_raw=w, left_separator='DEFINITE_SPACE', right_separator='DEFINITE_SPACE') for i, w in enumerate(words)]
    good = ['qotain','sheckhy','qokedy','qokedy','lsheckhy','qokain']
    cases = []
    def test(name, words, expected, mutate=None):
        r = rows(words)
        if mutate: mutate(r)
        f = classify(r, one)
        got = None if f is None else f['strict']
        assert got == expected, (name, got, expected)
        cases.append(dict(name=name, expected=expected))
    test('known', good, True)
    test('reverse_direction', [good[5],*good[1:5],good[0]], False)
    test('two_unit_changes', ['qotain',*good[1:5],'qokaiin'], False)
    test('cth_ckh_are_whole_units', ['qocthain',*good[1:5],'qockhain'], False)
    test('head_prefix', [*good[:4],'olsheckhy',good[5]], None)
    test('pivot_exact', [*good[:3],'qokeedy',*good[4:]], None)
    test('index_gap', good, None, lambda r:r[3].update(source_group_index='99'))
    test('uncertain_seam', good, None, lambda r:r[2].update(right_separator='UNCERTAIN'))
    test('line_crossing', good, None, lambda r:r[5].update(locus='f75v.47'))
    test('opaque_reader_kept_descriptive', ['qotain',"{ch'}eckhy",'qokedy','qokedy',"l{ch'}eckhy",'qokain'], False)
    test('identical_endpoints_descriptive', ['qokain',*good[1:5],'qokain'], False)
    return dict(status='PASS', cases=cases)

def main():
    spec = json.loads((BASE/'src/SPEC.json').read_text())
    lock = json.loads((BASE/'LOCK.json').read_text())
    for path, expected in lock['files'].items():
        assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest() == expected, path
    one = unique_parser(load(spec['signs_path'])['signs'])
    write('CONTROLS.json', controls(one))
    cache = ROOT/spec['cache_path']
    assert hashlib.sha256(cache.read_bytes()).hexdigest() == load(spec['guard_path'])['sha256']
    allowed = set(load(spec['scope_spec_path'])['allowed'])
    lines = defaultdict(list)
    with cache.open(newline='') as f:
        for row in csv.DictReader(f, delimiter='\t'):
            assert row['page'] in allowed and not row['page'].startswith('f84')
            if row['edition'] in spec['editions'] and row['kind'] == 'P':
                lines[row['edition'],row['page'],row['locus']].append(row)
    frames = []
    for key, rows in sorted(lines.items()):
        rows.sort(key=lambda r:int(r['source_group_index']))
        assert len({r['source_group_index'] for r in rows}) == len(rows)
        for i in range(len(rows)-5):
            frame = classify(rows[i:i+6], one)
            if frame is not None: frames.append(frame)
    frames.sort(key=lambda f:(f['edition'],f['page'],f['locus'],f['start_group']))
    counts = {}
    for ed in spec['editions']:
        fs = [f for f in frames if f['edition']==ed]
        strict = [f for f in fs if f['strict']]
        breadth = [f for f in strict if re.match(r'f\d+',f['page']).group()!='f75' and f['raw'][1]!='sheckhy']
        counts[ed] = dict(descriptive=len(fs),strict=len(strict),breadth=len(breadth))
    passed = counts['IT2a']['breadth'] > 0
    result = dict(experiment_id='GDT1413',counts=counts,breadth_gate_pass=passed,status='FORMAL_BREADTH_PRESENT' if passed else 'FORMAL_BREADTH_MISSING')
    worksheet = load(spec['worksheet_path'])['source_original_wrapper']['source_unit']
    roles = {}
    for num, ids in enumerate(spec['whole_passage_frame_groups'], 1):
        for slot, gid in zip(['LEFT','HEAD','RIGHT'], ids):
            assert gid not in roles
            roles[gid] = dict(frame=num, proposed_slot=slot)
    passage=[]
    for line in worksheet['lines']:
        for group in line['groups']:
            gid, index, raw, left, right = group
            passage.append(dict(source_group_id=gid, source_group_index=int(index), raw=raw, left_separator=left, right_separator=right, meaning='UNASSIGNED', proposed_frame=roles.get(gid), semantic_contribution='UNKNOWN'))
    assert len(passage)==77 and sum(p['proposed_frame'] is not None for p in passage)==9
    write('PASSAGE.json', dict(groups=passage,frame_positions=9,other_unknown_contributions=68, branches=dict(independent=['P(ol,qokain)','P(qotain,qokedy)','Q(qokedy,qokain)'], identity=['P(ol,qokain)','P(qotain,qokedy)','P(qokedy,qokain)'], converse=['P(ol,qokain)','P(qotain,qokedy)','P(qokain,qokedy)']), selected_branch=None, claim='Hypothetical local frames, not confirmed syntax or a complete passage reading; all words unglossed.'))
    write('FRAMES.json',frames)
    write('RESULT.json',result)
    print(json.dumps(result,sort_keys=True))

if __name__ == '__main__': main()
