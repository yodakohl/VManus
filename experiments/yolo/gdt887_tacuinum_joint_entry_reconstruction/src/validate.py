#!/usr/bin/env python3
"""Independent record-equation replay. Fitting reads only blind templates.

The producer is imported exclusively for selector-first source reconstruction.
Source-answer access is confined to audit_source(), outside the fit functions.
"""
import argparse
import copy
import hashlib
import itertools
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXPERIMENT = HERE.parent
EDITIONS = ('ZL3b', 'IT2a', 'RF1b', 'CONSENSUS')
CORE_KEYS = ('paragraphs', 'prefix_head', 'prefix_corrective', 'bodies',
             'dictionary', 'held_entity')


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'))


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_json(path):
    return json.loads(Path(path).read_text())


def word_scan(text):
    """ASCII letters/numerals; independent of the producer's regular expression."""
    result, current, kind = [], '', None
    for char in text + ' ':
        new_kind = 'letter' if char in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ' else (
            'number' if char in '0123456789' else None)
        if new_kind != kind or new_kind is None:
            if current:
                result.append(current)
            current = ''
        if new_kind:
            current += char
        kind = new_kind
    return result


def audit_source():
    source = read_json(HERE / 'SOURCE.json')
    fit = read_json(HERE / 'FIT_TEMPLATES.json')
    aliases = {}
    for name, forms in [
        ('@LACTUCA', 'lactuce lactucis'), ('@APIUM', 'apium apio appio'),
        ('@FENICULUM', 'feniculo'), ('CALIDUS', 'calida calidis'),
        ('FRIGIDUS', 'frigida frigidis'), ('SICCUS', 'sicca siccis'),
        ('HUMIDUS', 'humida'), ('DEGREE_I', 'primi 1'), ('DEGREE_II', '2'),
        ('NOCUMENTUM', 'nocumenti'), ('GENERARE', 'generant generat'),
        ('CONVENIRE', 'conueniunt conuenit')]:
        for form in forms.split():
            assert form not in aliases
            aliases[form] = name

    def atoms(text):
        return [aliases.get(w.lower(), w.upper()) for w in word_scan(text)
                if w.lower() not in ('et', 'in', 'cum')]

    entities = ['LACTUCA', 'PIRETRUM', 'APIUM', 'FENICULUM']
    assert source['entities'] == fit['entities'] == entities
    field_order = ['complexion', 'choice', 'benefit', 'harm', 'corrective',
                   'generated', 'suitability']
    expected = {'entities': entities, 'variants': []}
    for explicit in (False, True):
        entries = []
        for record in source['entries']:
            assert [f['field'] for f in record['fields']] == field_order
            assert word_scan(record['complete_transcription']) == [
                w for f in record['fields']
                for w in word_scan(f['heading'] + ' ' + f['text'])]
            slots = [{'field': 'head', 'atom': '@' + record['entity'], 'context': 'head'}]
            for field in record['fields']:
                if explicit:
                    slots += [{'field': field['field'], 'atom': atom, 'context': 'ordinary'}
                              for atom in atoms(field['heading'])]
                if record['entity'] == 'APIUM' and field['field'] == 'corrective':
                    values = ['@HELD']
                else:
                    values = atoms(field['text'])
                slots += [{'field': field['field'], 'atom': atom,
                           'context': 'corrective' if atom.startswith('@') else 'ordinary'}
                          for atom in values]
            entries.append({'entity': record['entity'], 'slots': slots})
        expected['variants'].append({'explicit_headers': explicit, 'entries': entries})
    assert fit == expected, 'independent source serialization differs'
    counts = [[len(r['slots']) for r in v['entries']] for v in expected['variants']]
    assert counts == [[34, 24, 17], [43, 33, 26]]
    return {'status': 'PASS', 'counts': counts,
            'source_sha256': digest(HERE / 'SOURCE.json'),
            'fit_templates_sha256': digest(HERE / 'FIT_TEMPLATES.json')}


def get_reading(frame, edition):
    if edition != 'CONSENSUS':
        return frame['readings'][edition]
    base = [frame['readings'][e] for e in EDITIONS[:3]]
    match = all(r['eligible'] for r in base)
    if match:
        signatures = [[(g['raw'], tuple(g['sta']), g['locus']) for g in r['groups']] for r in base]
        match = signatures[0] == signatures[1] == signatures[2]
    derived = {'eligible': match, 'groups': base[0]['groups'] if match else []}
    if 'CONSENSUS' in frame['readings']:
        reported = frame['readings']['CONSENSUS']
        assert reported['eligible'] == match, 'consensus eligibility mismatch'
        if match:
            assert [(g['raw'], g['sta'], g['locus']) for g in reported['groups']] == [
                (g['raw'], g['sta'], g['locus']) for g in derived['groups']]
    return derived


def candidate(entry, frame, edition):
    reading = get_reading(frame, edition)
    if not reading['eligible'] or len(reading['groups']) != len(entry['slots']):
        return None
    groups = [tuple(g['sta']) for g in reading['groups']]
    assert all(g and all(isinstance(c, str) and c for c in g) for g in groups)
    dictionary, reverse = {}, {}
    for slot, group in zip(entry['slots'], groups):
        if slot['context'] != 'ordinary':
            continue
        atom = slot['atom']
        if atom in dictionary and dictionary[atom] != group:
            return None
        if group in reverse and reverse[group] != atom:
            return None
        dictionary[atom], reverse[group] = group, atom
    return {'frame': frame, 'groups': groups, 'dictionary': dictionary}


def merged_dictionary(records):
    dictionary, reverse = {}, {}
    for record in records:
        for atom, group in record['dictionary'].items():
            if atom in dictionary and dictionary[atom] != group:
                return None
            if group in reverse and reverse[group] != atom:
                return None
            dictionary[atom], reverse[group] = group, atom
    return dictionary


def fit_panel(entities, variant, frames, edition):
    """Complete enumeration: no source text or expected answer is an input."""
    entries = variant['entries']
    assert len({f['paragraph_id'] for f in frames}) == len(frames)
    candidates = [[c for f in frames if (c := candidate(entry, f, edition)) is not None]
                  for entry in entries]
    candidate_ids = {e['entity']: [c['frame']['paragraph_id'] for c in cc]
                     for e, cc in zip(entries, candidates)}
    length_counts = {e['entity']: sum(
        get_reading(f, edition)['eligible'] and
        len(get_reading(f, edition)['groups']) == len(e['slots']) for f in frames)
        for e in entries}
    solutions = []
    triples = dictionary_triples = 0
    for records in itertools.product(*candidates):
        if len({r['frame']['physical_folio'] for r in records}) != len(records):
            continue
        triples += 1
        dictionary = merged_dictionary(records)
        if dictionary is None:
            continue
        observations = [(s, g) for e, r in zip(entries, records)
                        for s, g in zip(e['slots'], r['groups']) if s['context'] != 'ordinary']
        if any(g in dictionary.values() for _, g in observations):
            continue
        dictionary_triples += 1
        exemplars = {context: next(g for s, g in observations if s['context'] == context)
                     for context in ('head', 'corrective')}
        for h_length, c_length in itertools.product(range(3), repeat=2):
            lengths = {'head': h_length, 'corrective': c_length}
            if any(len(exemplars[c]) <= lengths[c] for c in lengths):
                continue
            prefixes = {c: exemplars[c][:lengths[c]] for c in lengths}
            bodies, held_body = {}, None
            valid = True
            for slot, group in observations:
                prefix = prefixes[slot['context']]
                if len(group) <= len(prefix) or group[:len(prefix)] != prefix:
                    valid = False
                    break
                body = group[len(prefix):]
                entity = slot['atom'][1:]
                if entity == 'HELD':
                    assert held_body is None, 'more than one held slot'
                    held_body = body
                elif entity in bodies and bodies[entity] != body:
                    valid = False
                    break
                else:
                    bodies[entity] = body
            if not valid or set(bodies) != set(entities):
                continue
            if len(set(bodies.values())) != len(entities):
                continue
            if any(prefix + body in dictionary.values()
                   for prefix in prefixes.values() for body in bodies.values()):
                continue
            held = [entity for entity in entities if bodies[entity] == held_body]
            if len(held) != 1:
                continue
            solutions.append({
                'paragraphs': {e['entity']: r['frame']['paragraph_id']
                               for e, r in zip(entries, records)},
                'prefix_head': list(prefixes['head']),
                'prefix_corrective': list(prefixes['corrective']),
                'bodies': {e: list(bodies[e]) for e in sorted(bodies)},
                'dictionary': {a: list(dictionary[a]) for a in sorted(dictionary)},
                'held_entity': held[0]})
    solutions.sort(key=canonical)
    assert len(solutions) == len({canonical(s) for s in solutions})
    return {'candidates': candidate_ids, 'solutions': solutions,
            'length_counts': length_counts, 'distinct_folio_triples': triples,
            'dictionary_triples': dictionary_triples, 'complete': True,
            'held_entities': sorted({s['held_entity'] for s in solutions})}


def synthetic_fixture(held='A', head=('h',), corrective=('r',)):
    def slot(atom, context='ordinary'):
        return {'atom': atom, 'context': context, 'field': context}
    entries = [
        {'entity': 'A', 'slots': [slot('@A', 'head'), slot('X'), slot('U'),
                                 slot('@C', 'corrective'), slot('@D', 'corrective'), slot('X')]},
        {'entity': 'B', 'slots': [slot('@B', 'head'), slot('X'), slot('@C', 'corrective'),
                                 slot('V'), slot('X')]},
        {'entity': 'C', 'slots': [slot('@C', 'head'), slot('U'),
                                 slot('@HELD', 'corrective'), slot('X')]},
    ]
    bodies = {e: (e.lower(),) for e in 'ABCD'}
    dictionary = {a: (a.lower(),) for a in 'XUV'}
    frames = []
    for index, entry in enumerate(entries):
        groups = []
        for s in entry['slots']:
            if s['context'] == 'ordinary':
                value = dictionary[s['atom']]
            else:
                entity = held if s['atom'] == '@HELD' else s['atom'][1:]
                value = (head if s['context'] == 'head' else corrective) + bodies[entity]
            groups.append({'raw': ''.join(value), 'sta': list(value), 'locus': 'synthetic',
                           'source_group_id': 'synthetic'})
        reading = {'eligible': True, 'reasons': [], 'groups': groups}
        frames.append({'paragraph_id': 'synthetic_' + entry['entity'],
                       'physical_folio': 'synthetic_' + str(index), 'page': 'synthetic',
                       'readings': {e: copy.deepcopy(reading) for e in EDITIONS[:3]}})
    return list('ABCD'), {'explicit_headers': False, 'entries': entries}, frames


def brute_prefix_oracle(entities, variant, frames):
    """Tiny oracle: enumerate all alphabet prefixes and all four held choices."""
    groups = [[tuple(g['sta']) for g in f['readings']['ZL3b']['groups']] for f in frames]
    alphabet = sorted({c for row in groups for g in row for c in g})
    prefixes = [()] + [(a,) for a in alphabet] + list(itertools.product(alphabet, repeat=2))
    result = set()
    for hp, cp in itertools.product(prefixes, repeat=2):
        for held in entities:
            bodies, dictionary = {}, {}
            valid = True
            for entry, row in zip(variant['entries'], groups):
                for slot, group in zip(entry['slots'], row):
                    atom = slot['atom']
                    if slot['context'] == 'ordinary':
                        if atom in dictionary and dictionary[atom] != group:
                            valid = False
                        dictionary[atom] = group
                    else:
                        prefix = hp if slot['context'] == 'head' else cp
                        entity = held if atom == '@HELD' else atom[1:]
                        body = group[len(prefix):]
                        if not body or prefix + body != group:
                            valid = False
                        if entity in bodies and bodies[entity] != body:
                            valid = False
                        bodies[entity] = body
                if not valid:
                    break
            if not valid or set(bodies) != set(entities):
                continue
            if len(set(dictionary.values())) != len(dictionary) or len(set(bodies.values())) != len(bodies):
                continue
            if any(p + b in dictionary.values() for p in (hp, cp) for b in bodies.values()):
                continue
            result.add(canonical({'paragraphs': {e['entity']: f['paragraph_id']
                                                 for e, f in zip(variant['entries'], frames)},
                                  'prefix_head': list(hp), 'prefix_corrective': list(cp),
                                  'bodies': {e: list(b) for e, b in bodies.items()},
                                  'dictionary': {a: list(g) for a, g in dictionary.items()},
                                  'held_entity': held}))
    return result


def selftest():
    passed = []

    def evaluate(fixture):
        return fit_panel(*fixture, 'ZL3b')

    base = synthetic_fixture()
    positive = evaluate(base)
    assert len(positive['solutions']) == 1
    assert positive['solutions'][0]['held_entity'] == 'A'
    passed.append('complete_positive')
    alternative = evaluate(synthetic_fixture('B'))
    assert len(alternative['solutions']) == 1 and alternative['solutions'][0]['held_entity'] == 'B'
    passed.append('alternative_held_identity_retained')
    for name, mutations in [
        ('ordinary_repeat_conflict', [(0, 5, ['z'])]),
        ('ordinary_injection_conflict', [(0, 2, ['x'])]),
        ('cross_record_dictionary_conflict', [(1, 1, ['z']), (1, 4, ['z'])]),
        ('known_entity_conflict', [(1, 2, ['r', 'z'])]),
        ('empty_entity_body', [(0, 0, ['h'])]),
        ('distinct_body_conflict', [(1, 0, ['h', 'a'])]),
        ('observed_entity_dictionary_collision', [(0, 2, ['h', 'a']), (2, 1, ['h', 'a'])]),
        ('unobserved_entity_dictionary_collision', [(1, 3, ['r', 'b'])]),
    ]:
        fixture = copy.deepcopy(base)
        for frame, group, value in mutations:
            fixture[2][frame]['readings']['ZL3b']['groups'][group]['sta'] = value
        assert not evaluate(fixture)['solutions'], name
        passed.append(name)
    same_folio = copy.deepcopy(base)
    same_folio[2][1]['physical_folio'] = same_folio[2][0]['physical_folio']
    assert not evaluate(same_folio)['solutions']
    passed.append('distinct_physical_folios')
    assert len(evaluate(synthetic_fixture(head=('h', 'j'), corrective=('r', 'k')))['solutions']) == 1
    assert not evaluate(synthetic_fixture(head=('h', 'j', 'q'), corrective=('r', 'k', 's')))['solutions']
    passed.append('prefix_length_boundary')
    ambiguity = synthetic_fixture(head=('s',), corrective=('s',))
    ambiguous_solutions = evaluate(ambiguity)['solutions']
    assert len(ambiguous_solutions) == 2
    assert {s['held_entity'] for s in ambiguous_solutions} == {'A'}
    passed.append('all_prefix_decompositions_retained')
    for fixture in (base, ambiguity):
        assert {canonical(s) for s in evaluate(fixture)['solutions']} == brute_prefix_oracle(*fixture)
    passed.append('exhaustive_alphabet_prefix_oracle')
    assert fit_panel(*base, 'CONSENSUS') == positive
    disagreed = copy.deepcopy(base)
    disagreed[2][0]['readings']['RF1b']['groups'][0]['raw'] = 'different'
    assert not fit_panel(*disagreed, 'CONSENSUS')['solutions']
    passed.append('consensus_requires_all_three_raw_and_sta')
    return passed


def compare_panel(expected, reported):
    for key in ('length_counts', 'distinct_folio_triples', 'dictionary_triples',
                'complete', 'held_entities'):
        assert expected[key] == reported[key], ('panel statistic mismatch', key)
    assert set(expected['candidates']) == set(reported['candidates'])
    for entity, ids in expected['candidates'].items():
        actual = reported['candidates'][entity]
        assert len(actual) == len(set(actual))
        assert sorted(ids) == sorted(actual), ('candidate mismatch', entity)
    actual = [{key: solution[key] for key in CORE_KEYS} for solution in reported['solutions']]
    assert len(actual) == len({canonical(s) for s in actual}), 'duplicate reported solutions'
    assert sorted(map(canonical, expected['solutions'])) == sorted(map(canonical, actual)), 'solution set mismatch'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--selftest', action='store_true', help='source and synthetic checks only; no target access')
    parser.add_argument('--check', action='store_true', help='compare rather than write VALIDATION.json')
    args = parser.parse_args()
    source_check = audit_source()
    tests = selftest()
    if args.selftest:
        print(json.dumps({'status': 'PASS', 'source': source_check, 'selftests': tests}, sort_keys=True))
        return 0
    from run import select  # Only guarded source replay; no producer fitting logic.
    root = EXPERIMENT.parents[2]
    for relative, expected_hash in read_json(HERE / 'PREREG_LOCK.json').items():
        assert digest(root / relative) == expected_hash, ('preregistration hash mismatch', relative)
    selected_path = EXPERIMENT / 'artifacts/SELECTED.json'
    result_path = EXPERIMENT / 'artifacts/RESULT.json'
    selected = read_json(selected_path)
    assert select() == selected, 'guarded source selection replay mismatch'
    result = read_json(result_path)
    fit = read_json(HERE / 'FIT_TEMPLATES.json')
    panels = {}
    for edition in EDITIONS:
        for variant in fit['variants']:
            key = edition + ':' + str(int(variant['explicit_headers']))
            expected = fit_panel(fit['entities'], variant, selected['frames'], edition)
            compare_panel(expected, result['panels'][key])
            panels[key] = {'candidate_counts': {e: len(ids) for e, ids in expected['candidates'].items()},
                           'solutions': len(expected['solutions']),
                           'held_entities': sorted({s['held_entity'] for s in expected['solutions']})}
    assert set(result['panels']) == set(panels), 'unexpected or missing panels'
    assert result['complete'] is True
    assert result['held_entities'] == sorted({e for p in panels.values() for e in p['held_entities']})
    assert result['eligible'] == {edition: sum(get_reading(f, edition)['eligible']
                                             for f in selected['frames']) for edition in EDITIONS}
    validation = {'status': 'PASS', 'selected_sha256': digest(selected_path),
                  'result_sha256': digest(result_path), 'source': source_check,
                  'validator_sha256': digest(__file__), 'selftests': tests, 'panels': panels,
                  'guarded_selection_replayed': True, 'independent_complete_fit_replayed': True}
    destination = EXPERIMENT / 'artifacts/VALIDATION.json'
    if args.check:
        assert read_json(destination) == validation, 'stored validation mismatch'
    else:
        destination.write_text(json.dumps(validation, indent=2, sort_keys=True) + '\n')
    print(json.dumps(validation, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
