#!/usr/bin/env python3
"""Fixed overt-anchor construction; opaque form labels are not word meanings."""
import argparse
import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parents[1]
ART = HERE / 'artifacts'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(name, value):
    (ART / name).write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + '\n')


def argument(groups, i):
    if i + 1 == len(groups):
        return None, 'NO_RIGHT_GROUP'
    g, h = groups[i], groups[i + 1]
    if int(h[1]) != int(g[1]) + 1:
        return None, 'NONCONSECUTIVE_INDEX'
    if g[4] != 'DEFINITE_SPACE' or h[3] != 'DEFINITE_SPACE':
        return None, 'NONDEFINITE_SEAM'
    return h, None


def resolve(prior, key):
    matching = [p for p in prior if p['key'] == key]
    selected = matching[-1] if matching else None
    return matching, selected, None if selected is None else copy.deepcopy(selected['payload'])


def analyze(lines):
    producers, cases = [], []
    for line in sorted(lines, key=lambda x: int(x['metadata']['source_row_index'])):
        md, groups = line['metadata'], line['groups']
        row = int(md['source_row_index'])
        for i, g in enumerate(groups):
            if g[2] not in ('sheckhy', 'lsheckhy'):
                continue
            h, reason = argument(groups, i)
            if g[2] == 'sheckhy':
                if h is not None:
                    span = [g[0], h[0]]
                    producers.append({'page': md['page'], 'locus': md['locus'],
                                      'span': span, 'key': h[2], 'end_order': [row, int(h[1])],
                                      'payload': {'head': 'sheckhy', 'argument': h[2], 'producer_span': span}})
                continue
            prior = [p for p in producers if p['page'] == md['page'] and p['end_order'] < [row, int(g[1])]]
            matching, selected, returned = ([], None, None) if h is None else resolve(prior, h[2])
            cases.append({'reference_id': g[0], 'page': md['page'], 'locus': md['locus'],
                          'argument': None if h is None else h[2],
                          'reference_span': [g[0]] if h is None else [g[0], h[0]],
                          'status': 'UNRESOLVED_ARGUMENT' if h is None else ('MATCH' if selected else 'NO_ANCHOR'),
                          'argument_problem': reason,
                          'prior_producer_spans': [p['span'] for p in prior],
                          'matching_prior_spans': [p['span'] for p in matching],
                          'selected_producer_span': None if selected is None else selected['span'],
                          'returned': returned})
    return {'producer_records': producers, 'cases': cases,
            'target_count': len(cases),
            'matched': sum(c['status'] == 'MATCH' for c in cases),
            'missing': sum(c['status'] == 'NO_ANCHOR' for c in cases),
            'unresolved': sum(c['status'] == 'UNRESOLVED_ARGUMENT' for c in cases)}


def fixture(words, row=1, page='fixture', gap=False, uncertain=False):
    groups = []
    for i, word in enumerate(words, 1):
        index = i + (1 if gap and i > 1 else 0)
        left = 'LINE_START' if i == 1 else 'DEFINITE_SPACE'
        right = 'LINE_END' if i == len(words) else 'DEFINITE_SPACE'
        if uncertain and i == 1:
            right = 'UNCERTAIN_SMALL_SPACE'
        groups.append([f'FIX|{page}.{row}|G{index:03}', str(index), word, left, right])
    return {'metadata': {'page': page, 'locus': f'{page}.{row}', 'source_row_index': str(row)}, 'groups': groups}


def controls():
    a = fixture(['sheckhy', 'A'], 1)
    b = fixture(['sheckhy', 'B'], 2)
    q = fixture(['lsheckhy', 'A'], 3)
    x = analyze([q, b, a])
    assert x['cases'][0]['selected_producer_span'] == [g[0] for g in a['groups']]
    assert x['cases'][0]['returned']['argument'] == 'A'
    assert x['producer_records'][-1]['key'] == 'B'
    assert analyze([a, fixture(['lsheckhy', 'C'], 2)])['missing'] == 1
    assert analyze([q, fixture(['sheckhy', 'A'], 4)])['missing'] == 1
    assert analyze([a, fixture(['lsheckhy', 'A'], 2, page='other')])['missing'] == 1
    assert analyze([a, fixture(['lsheckhy', 'A'], 2, uncertain=True)])['unresolved'] == 1
    assert analyze([fixture(['sheckhy', 'A'], 1, uncertain=True), q])['missing'] == 1
    assert analyze([fixture(['sheckhy', 'A'], 1, gap=True), q])['missing'] == 1
    assert analyze([a, fixture(['lsheckhy'], 2)])['unresolved'] == 1
    assert analyze([a])['target_count'] == 0
    overlapping = analyze([fixture(['sheckhy', 'lsheckhy', 'lsheckhy'])])
    assert overlapping['cases'][0]['status'] == 'NO_ANCHOR'
    # Exercise the same resolver used by real queries at a fixed stored key.
    record = x['producer_records'][0]
    record['payload']['argument'] = 'INTERVENED'
    assert resolve(x['producer_records'], 'A')[2]['argument'] == 'INTERVENED'
    changed = fixture(['sheckhy', 'C'], 1)
    assert analyze([changed, b, q])['missing'] == 1
    return {'status': 'PASS', 'checks': 14, 'scope': 'source-free sorting, argument, reference, scope, overlap and payload fixtures; not meanings'}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--controls-only', action='store_true')
    opts = ap.parse_args()
    write('PRIMARY_CONTROLS.json', controls())
    if opts.controls_only:
        print('Source-free primary controls PASS; native counts NOT_RUN')
        return
    lock = json.loads((HERE / 'LOCK.json').read_text())
    for item in lock['entries']:
        assert digest(ROOT / item['path']) == item['sha256'], item['path']
    spec = json.loads((HERE / 'src/SPEC.json').read_text())
    planpath = ROOT / spec['plan']
    assert digest(planpath) == spec['plan_sha256']
    plan = json.loads(planpath.read_text())
    columns = None
    readers = {ed: [] for ed in spec['editions']}
    for pin in spec['sources']:
        path = ROOT / pin['path']
        assert digest(path) == pin['sha256'], pin['path']
        data = json.loads(path.read_text())
        if columns is None:
            columns = data['group_columns']
        assert data['group_columns'] == columns
        for line in data['lines']:
            md = line['metadata']
            if md['page'] not in spec['pages'] or md['kind'] != 'P':
                continue
            assert not md['page'].startswith('f84')
            assert md['edition'] in readers
            readers[md['edition']].append(line)
    for ed, lines in readers.items():
        lines.sort(key=lambda line: int(line['metadata']['source_row_index']))
        assert len({line['metadata']['locus'] for line in lines}) == len(lines)
        assert all(line['metadata']['edition'] == ed for line in lines)
        assert {line['metadata']['page'] for line in lines} == set(spec['pages'])
    source = {'source_pins': spec['sources'], 'group_columns': columns, 'readers': readers}
    write('SOURCE.json', source)
    panels = {ed: analyze(lines) for ed, lines in readers.items()}
    assert {ed: z['target_count'] for ed, z in panels.items()} == {'IT2a': 2, 'ZL3b': 2, 'RF1b': 1}, 'Known profile target coverage mismatch'
    it = panels['IT2a']
    decision = ('NO_PRIMARY_TARGET_CAPACITY' if it['target_count'] == 0 else
                'FIXED_OVERT_CONSTRUCTION_MISSING_ANCHOR' if it['missing'] else
                'UNRESOLVED_SOURCE_OR_ARGUMENT' if it['unresolved'] else
                'ALL_PRIMARY_TARGETS_HAVE_OVERT_ANCHORS_SCOPED')
    profilepin = next(q for q in plan['source_pins'] if q['path'].endswith('LEXICAL_WORKSHEET_CONTEXT_20261016.json'))
    assert digest(ROOT / profilepin['path']) == profilepin['sha256']
    original = json.loads((ROOT / profilepin['path']).read_text())['source_original_wrapper']['source_unit']['lines']
    it77 = [line for line in readers['IT2a'] if line['metadata']['locus'] in {f'f75v.{n}' for n in range(43, 50)}]
    assert it77 == original and sum(len(line['groups']) for line in it77) == 77
    known_ids = {i for p in it['producer_records'] for i in p['span']}
    query_ids = {i for c in it['cases'] for i in c['reference_span']}
    trace = [{'metadata': line['metadata'], 'groups': [
        {'original_group': g, 'structural_annotation': ('CONSTRUCTOR_SPAN' if g[0] in known_ids else
         'REFERENCE_SPAN' if g[0] in query_ids else 'UNKNOWN_CONTRIBUTION'),
         'meaning': 'UNASSIGNED'} for g in line['groups']]} for line in it77]
    write('TRACE_77.json', {'scope': 'complete original77groups with proposed construction spans only; other semantic effects unknown', 'lines': trace})
    write('RESULT.json', {'status': decision, 'primary_reader': 'IT2a', 'panels': panels,
                          'meaning_selection': 'NONE', 'unknowns_are_noops': False,
                          'scope': plan['claim_ceiling']})
    print(json.dumps({'status': decision, 'panels': {ed: {k: z[k] for k in ('target_count', 'matched', 'missing', 'unresolved')} for ed, z in panels.items()}}))


if __name__ == '__main__':
    main()

