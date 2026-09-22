#!/usr/bin/env python3
"""Independent frozen-vocabulary census audit; never imports the primary runner."""
import argparse
import collections
import csv
import hashlib
import io
import json
import re
import subprocess
import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE = Path(__file__).resolve().parents[1]
READERS = ('ZL3b', 'IT2a', 'RF1b')
TARGET_SHA = '667ca3ae0705a6bb3ccfcd09ea7ee04e28747e58d810e8fa9379f28c0f4fc89b'
CSV_FIELDS = ['id', 'reader', 'paragraph_id', 'page', 'leaf', 'groups',
              'known_positions', 'unknown_positions', 'known_type_count',
              'unknown_type_count', 'known_fraction_numerator',
              'known_fraction_denominator', 'operation_values',
              'strict_anchor_eligible', 'eligible', 'reasons', 'pair_id']


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def read(path):
    return json.loads(Path(path).read_text())


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def natural(text):
    return tuple((1, int(x)) if x.isdigit() else (0, x)
                 for x in re.split(r'(\d+)', text))


def inventory(offer, operation_values):
    primary = offer['lexicon']
    aliases = offer['alternative_reading_values']
    require(not set(primary).intersection(aliases), 'Inventory key collision')
    entries = dict(primary, **aliases)
    operations = set(operation_values)
    tags = {}

    def visit(word, chain=()):
        require(word not in chain, 'Cyclic lexical alias/composition: ' + word)
        require(word in entries, 'Missing lexical dependency: ' + word)
        if word in tags:
            return tags[word]
        entry = entries[word]
        result = set()
        if entry.get('value') in operations:
            result.add(entry['value'])
        if 'same_hypothesized_value_as' in entry:
            result.update(visit(entry['same_hypothesized_value_as'], chain + (word,)))
        for part in entry.get('composition', []):
            result.update(visit(part, chain + (word,)))
        tags[word] = sorted(result)
        return tags[word]

    for word in entries:
        visit(word)
    return entries, tags


def guard_metadata(paragraph):
    page = paragraph['page']
    leaf = paragraph['leaf']
    require(isinstance(page, str) and isinstance(leaf, int) and not isinstance(leaf, bool),
            'Invalid page/leaf metadata')
    require(not page.startswith('f84') and leaf != 84 and not page.startswith('f116v'),
            'Sealed/unadmitted selector rejected before contents')
    match = re.match(r'^f(\d+)', page)
    require(match is not None and int(match.group(1)) == leaf, 'Page/leaf mismatch')


def row(reader, p, entries, tags, spec):
    guard_metadata(p)  # This precedes every access to paragraph lines/words.
    known = []; unknown = []; operations = set(); lines = []; all_ids = []
    strict = True
    for line in p['lines']:
        require(len(line['words']) == len(line['source_ids']), 'Words/source IDs differ')
        require(line['offset'] == len(all_ids), 'Noncontiguous paragraph offsets')
        flag = line.get('anchor_eligible')
        strict = strict and flag is True
        positions = []
        for word, sid in zip(line['words'], line['source_ids']):
            require(isinstance(word, str) and isinstance(sid, str), 'Nonstring raw group/ID')
            found = word in entries
            positions.append([sid, word, found])
            (known if found else unknown).append(word)
            if found:
                operations.update(tags[word])
            all_ids.append(sid)
        line_result = {k: v for k, v in line.items() if k not in ('words', 'source_ids')}
        line_result['positions'] = positions
        lines.append(line_result)
    require(len(all_ids) == p['groups'] and len(all_ids) == len(set(all_ids)),
            'Paragraph group total/unique IDs mismatch')
    groups = p['groups']; ktypes = sorted(set(known)); utypes = sorted(set(unknown))
    bounds = spec['bounds']; reasons = []
    tests = [
        (p['leaf'] in spec['excluded_leaves'], 'EXCLUDED_LEAF'),
        (groups < bounds['min_groups'], 'BELOW_MIN_GROUPS'),
        (groups > bounds['max_groups'], 'ABOVE_MAX_GROUPS'),
        (len(ktypes) < bounds['min_known_types'], 'BELOW_MIN_KNOWN_TYPES'),
        (len(utypes) > bounds['max_unknown_types'], 'ABOVE_MAX_UNKNOWN_TYPES'),
        (len(known) * bounds['min_known_fraction_denominator'] <
         groups * bounds['min_known_fraction_numerator'], 'BELOW_MIN_KNOWN_FRACTION'),
        (len(operations) < bounds['min_operation_values'], 'BELOW_MIN_OPERATION_VALUES')]
    for failed, reason in tests:
        if failed:
            reasons.append(reason)
    loci = [line['locus'] for line in p['lines']]
    return {'id': reader + '|' + p['id'], 'reader': reader,
            'paragraph_id': p['id'], 'page': p['page'], 'leaf': p['leaf'],
            'loci': loci, 'groups': groups, 'known_positions': len(known),
            'unknown_positions': len(unknown), 'known_types': ktypes,
            'unknown_types': utypes, 'known_type_count': len(ktypes),
            'unknown_type_count': len(utypes), 'operation_values': sorted(operations),
            'known_fraction': [len(known), groups], 'strict_anchor_eligible': strict,
            'lines': lines, 'eligible': not reasons, 'reasons': reasons,
            'pair_id': p['page'] + '|' + ','.join(loci)}


def pairs_and_ranks(rows):
    by_pair = {}
    for r in rows:
        key = (r['page'], tuple(r['loci']))
        readers = by_pair.setdefault(key, {})
        require(r['reader'] not in readers, 'Duplicate reader/page/full-locus list')
        readers[r['reader']] = r
    pairs = []
    for (page, loci), readers in by_pair.items():
        first = next(iter(readers.values()))
        require(all(r['leaf'] == first['leaf'] for r in readers.values()), 'Pair leaf mismatch')
        missing = ['MISSING_' + reader for reader in READERS[:2] if reader not in readers]
        metrics = None
        if missing:
            reasons = missing
        else:
            rr = [readers[r] for r in READERS[:2]]
            fraction = min(Fraction(*r['known_fraction']) for r in rr)
            metrics = {'max_unknown_types': max(r['unknown_type_count'] for r in rr),
                       'min_known_fraction': [fraction.numerator, fraction.denominator],
                       'min_known_types': min(r['known_type_count'] for r in rr)}
            reasons = [r['reader'] + ':' + reason for r in rr for reason in r['reasons']]
        pairs.append({'id': first['pair_id'], 'page': page, 'leaf': first['leaf'],
                      'loci': list(loci), 'readers': {r: readers[r]['id'] for r in READERS if r in readers},
                      'eligible': not reasons, 'reasons': reasons, 'metrics': metrics})

    def location(p):
        return (p['leaf'], p['page'], tuple(natural(x) for x in p['loci']))

    def rank(p):
        m = p['metrics']
        return (m['max_unknown_types'], -Fraction(*m['min_known_fraction']),
                -m['min_known_types'], *location(p),
                tuple(p['readers'][r] for r in READERS[:2]))

    pairs.sort(key=location)
    ranked = [dict(p, rank=i + 1) for i, p in enumerate(sorted(
        (p for p in pairs if p['eligible']), key=rank))]
    return pairs, ranked


def selection(ranked, originals, entries, tags):
    if not ranked:
        return {'pair': None, 'paragraphs': {}, 'bindings': {}}
    pair = ranked[0]; paragraphs = {}; bindings = {}
    for reader in READERS[:2]:
        p = originals[pair['readers'][reader]]
        guard_metadata(p)
        paragraphs[reader] = p
        bindings[reader] = [
            {'source_id': sid, 'raw': word, 'known': word in entries,
             'value': entries.get(word), 'operation_values': tags.get(word, [])}
            for line in p['lines'] for word, sid in zip(line['words'], line['source_ids'])]
    return {'pair': pair, 'paragraphs': paragraphs, 'bindings': bindings}


def result(rows, pairs, ranked, offer, commit):
    rejections = collections.Counter(reason for r in rows for reason in r['reasons'])
    return {'experiment': 'GDT1036',
            'decision': 'ONE_COMPLETE_EXTENSION_TARGET' if ranked else 'PARK_WITHIN_FROZEN_CAPACITY_LIMITS',
            'rows': len(rows), 'reader_counts': {r: sum(x['reader'] == r for x in rows) for r in READERS},
            'pairs': len(pairs), 'matched_pairs': sum(p['metrics'] is not None for p in pairs),
            'eligible_pairs': len(ranked), 'selected_pair_id': ranked[0]['id'] if ranked else None,
            'inventory': {'primary_types': len(offer['lexicon']),
                          'alternate_types': len(offer['alternative_reading_values']),
                          'total_types': len(offer['lexicon']) + len(offer['alternative_reading_values'])},
            'fully_covered_rows': [r['id'] for r in rows if r['unknown_positions'] == 0],
            'eligible_rows': [r['id'] for r in rows if r['eligible']],
            'source_uncertain_rows': [r['id'] for r in rows if not r['strict_anchor_eligible']],
            'rejection_counts': dict(sorted(rejections.items())), 'registration_commit': commit,
            'claims': {'confirmed_words': 0, 'independent_meaning_capacity': 0,
                       'significance': False, 'readers_independent': False}}


def csv_rows(rows):
    out = []
    for r in rows:
        v = {k: r[k] for k in CSV_FIELDS if k in r}
        v['known_fraction_numerator'], v['known_fraction_denominator'] = r['known_fraction']
        for k in ['operation_values', 'reasons']:
            v[k] = '|'.join(v[k])
        out.append({k: str(v[k]) for k in CSV_FIELDS})
    return out


def equal(actual, expected, where):
    require(type(actual) is type(expected), where + ': type differs')
    if isinstance(expected, dict):
        require(actual.keys() == expected.keys(), where + ': key set differs')
        for k in expected:
            equal(actual[k], expected[k], where + '.' + str(k))
    elif isinstance(expected, list):
        require(len(actual) == len(expected), where + ': length differs')
        for i, (a, e) in enumerate(zip(actual, expected)):
            equal(a, e, where + '[' + str(i) + ']')
    else:
        require(actual == expected, where + ': value differs')


def execute():
    spec = read(BASE / 'src/SPEC.json')
    lock_path = BASE / 'PREREG_LOCK.json'; lock = read(lock_path)
    files = lock['files']
    required = [Path(__file__).resolve().relative_to(ROOT).as_posix(),
                (BASE / 'src/SPEC.json').relative_to(ROOT).as_posix(),
                (BASE / 'PREREGISTRATION.md').relative_to(ROOT).as_posix(),
                spec['offer'], spec['source_packet'], spec['paragraphs']]
    require(all(x in files for x in required), 'Required lock binding absent')
    for name, digest in files.items():
        require(not Path(name).is_absolute() and '..' not in Path(name).parts, 'Nonrepository lock path')
        require(sha(ROOT / name) == digest, 'Hash mismatch: ' + name)
    require(files[spec['paragraphs']] == TARGET_SHA, 'Wrong owned paragraph packet hash')
    receipt = read(BASE / 'artifacts/PUBLIC_REGISTRATION.json'); commit = receipt['commit']
    require(isinstance(commit, str) and re.fullmatch(r'[0-9a-f]{7,40}', commit), 'Invalid registration commit')
    rel = lock_path.relative_to(ROOT).as_posix()
    committed = subprocess.run(['git', 'show', commit + ':' + rel], cwd=ROOT,
                               capture_output=True, check=True).stdout
    require(committed == lock_path.read_bytes(), 'Public commit does not contain this exact lock')
    offer = read(ROOT / spec['offer'])
    require(offer['source_packet'] == spec['source_packet'], 'Offer source packet path mismatch')
    require(sha(ROOT / spec['source_packet']) == offer['source_packet_sha256'], 'Offer packet hash mismatch')
    entries, tags = inventory(offer, spec['operation_values'])
    require((len(offer['lexicon']), len(offer['alternative_reading_values']), len(entries)) == (65, 15, 80),
            'Frozen inventory size differs')
    source = read(ROOT / spec['paragraphs'])  # Authorized execution only, after all locks.
    rows = []; originals = {}; seen_ids = set()
    require(set(source).issubset(set(READERS)), 'Unexpected reader')
    for reader in READERS:
        pp = source.get(reader, [])
        require(len(pp) == spec['expected_rows'][reader], 'Reader paragraph count mismatch: ' + reader)
        for p in pp:
            guard_metadata(p)
            r = row(reader, p, entries, tags, spec)
            require(r['id'] not in originals, 'Duplicate row ID')
            for line in r['lines']:
                for sid, _, _ in line['positions']:
                    require(sid not in seen_ids, 'Repeated source ID across rows')
                    seen_ids.add(sid)
            originals[r['id']] = p; rows.append(r)
    pairs, ranked = pairs_and_ranks(rows)
    expected = {'ROWS.json': rows, 'PAIRS.json': pairs, 'RANKED.json': ranked,
                'SELECTED.json': selection(ranked, originals, entries, tags),
                'RESULT.json': result(rows, pairs, ranked, offer, commit)}
    for name, data in expected.items():
        equal(read(BASE / 'artifacts' / name), data, name)
    with (BASE / 'artifacts/COUNTS.csv').open(newline='') as f:
        table = csv.DictReader(f)
        equal(table.fieldnames, CSV_FIELDS, 'COUNTS.csv.header')
        equal(list(table), csv_rows(rows), 'COUNTS.csv')
    return {'success': True, 'reasons': [], 'status': 'PASS',
            'experiment': 'GDT1036', 'hashlocks_checked': len(files),
            'rows_checked': len(rows), 'pairs_checked': len(pairs),
            'eligible_pairs': len(ranked), 'decision': expected['RESULT.json']['decision'],
            'confirmed_words': 0, 'independent_meaning_capacity': 0,
            'significance': False, 'selection_validation_only': True}


def self_test():
    spec = read(BASE / 'src/SPEC.json')
    offer = read(ROOT / spec['offer'])
    require(sha(ROOT / spec['source_packet']) == offer['source_packet_sha256'], 'Source offer hash mismatch')
    entries, tags = inventory(offer, spec['operation_values'])
    require(len(entries) == 80 and len(offer['lexicon']) == 65, 'Inventory count')
    require(tags['cphol'] == ['KNEAD'] and tags['chyky'] == ['GRIND'] and
            tags['shcthey'] == ['SPREAD'] and tags['cpho[s:r]'] == ['CRUSH'], 'Composition/alias operations')
    require('cpho[s:r]' in entries and 'cphos' in entries and 'cphor' in entries,
            'Raw ambiguity and explicit aliases retained')
    toy = {'lexicon': {c: {'value': ('DRY' if c == 'a' else 'CRUSH' if c == 'b' else 'X')}
                       for c in 'abcdefgh'}, 'alternative_reading_values': {}}
    en, ts = inventory(toy, spec['operation_values']); checks = 0

    def make(words, leaf=1, ident='x', flag=True, locus=None):
        return {'id': ident, 'page': 'f' + str(leaf) + 'r', 'leaf': leaf, 'groups': len(words),
                'lines': [{'locus': locus or ('f' + str(leaf) + 'r.1'), 'anchor_eligible': flag,
                           'offset': 0, 'words': words,
                           'source_ids': [ident + ':' + str(i) for i in range(len(words))]}]}

    words = list('abcdefgh') + ['a'] * 5 + ['unknown'] * 13
    baseline = row('ZL3b', make(words), en, ts, spec)
    require(baseline['eligible'] and baseline['known_fraction'] == [13, 26], 'Exact half threshold'); checks += 1
    for n, reason in [(24, 'BELOW_MIN_GROUPS'), (101, 'ABOVE_MAX_GROUPS')]:
        r = row('ZL3b', make((list('abcdefgh') * 13)[:n]), en, ts, spec)
        require(reason in r['reasons'], 'Size bound'); checks += 1
    for n in [25, 100]:
        require(row('ZL3b', make((list('abcdefgh') * 13)[:n]), en, ts, spec)['eligible'], 'Inclusive size'); checks += 1
    for leaf in spec['excluded_leaves']:
        require('EXCLUDED_LEAF' in row('ZL3b', make(words, leaf), en, ts, spec)['reasons'], 'Whole leaf exclusion'); checks += 1
    low = words.copy(); low[12] = 'unknown'
    require('BELOW_MIN_KNOWN_FRACTION' in row('ZL3b', make(low), en, ts, spec)['reasons'], 'Below half'); checks += 1
    low = ['a' if x == 'h' else x for x in words]
    require('BELOW_MIN_KNOWN_TYPES' in row('ZL3b', make(low), en, ts, spec)['reasons'], 'Known types boundary'); checks += 1
    for n in [20, 21]:
        r = row('ZL3b', make(list('abcdefgh') * 3 + ['u' + str(i) for i in range(n)]), en, ts, spec)
        require(('ABOVE_MAX_UNKNOWN_TYPES' in r['reasons']) == (n == 21), 'Unknown type boundary'); checks += 1
    low = ['a' if x == 'b' else x for x in words]
    require('BELOW_MIN_OPERATION_VALUES' in row('ZL3b', make(low), en, ts, spec)['reasons'], 'Operations boundary'); checks += 1
    for flag in [False, None, 1]:
        r = row('ZL3b', make(words, flag=flag), en, ts, spec)
        require(r['eligible'] and not r['strict_anchor_eligible'], 'Uncertain flags only reported'); checks += 1

    class Poison(dict):
        def __getitem__(self, key):
            if key == 'lines':
                raise RuntimeError('contents were touched')
            return super().__getitem__(key)

    for page, leaf in [('f84r', 84), ('f84v', 84), ('f116v', 116)]:
        try:
            row('ZL3b', Poison(page=page, leaf=leaf), en, ts, spec)
        except AssertionError:
            checks += 1
        else:
            raise AssertionError('Sealed metadata not rejected')
    z = row('ZL3b', make(words, ident='z'), en, ts, spec)
    it = row('IT2a', make(words, ident='it'), en, ts, spec)
    pp, ranked = pairs_and_ranks([z, it])
    require(len(ranked) == 1 and ranked[0]['metrics']['min_known_fraction'] == [1, 2], 'Paired exact metric'); checks += 1
    pp, ranked = pairs_and_ranks([z])
    require(not ranked and pp[0]['reasons'] == ['MISSING_IT2a'] and pp[0]['metrics'] is None, 'Unpaired complete row'); checks += 1
    it2 = dict(it, loci=['f1r.2'], pair_id='f1r|f1r.2')
    require(not pairs_and_ranks([z, it2])[1], 'Different boundaries cannot pair'); checks += 1
    try:
        pairs_and_ranks([z, z])
    except AssertionError:
        checks += 1
    else:
        raise AssertionError('Duplicate pair member accepted')
    # Fractions intentionally below binary-float distinguishability.
    rows = []
    for leaf, frac in [(1, [10**18, 2 * 10**18]), (2, [10**18 + 1, 2 * 10**18])]:
        for rr in [z, it]:
            q = dict(rr, id=rr['id'] + str(leaf), leaf=leaf, page='f' + str(leaf) + 'r',
                     loci=['f' + str(leaf) + 'r.1'], pair_id='f' + str(leaf) + 'r|f' + str(leaf) + 'r.1',
                     known_fraction=frac)
            rows.append(q)
    require(pairs_and_ranks(rows)[1][0]['leaf'] == 2, 'Ranking must use exact rationals'); checks += 1
    require(natural('f1r.2') < natural('f1r.10'), 'Natural locus order'); checks += 1
    return {'success': True, 'status': 'SYNTHETIC_PREFLIGHT_PASS', 'synthetic_checks': checks,
            'inventory_types': len(entries), 'target_packet_opened': False}


def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--self-test', action='store_true')
    group.add_argument('--execute', action='store_true')
    args = parser.parse_args()
    try:
        outcome = execute() if args.execute else self_test()
    except Exception as exc:
        outcome = {'success': False, 'status': 'FAIL', 'experiment': 'GDT1036',
                   'reasons': [type(exc).__name__ + ': ' + str(exc)]}
    if args.execute:
        (BASE / 'artifacts/VALIDATION.json').write_text(json.dumps(outcome, indent=2, ensure_ascii=False) + '\n')
    print(json.dumps(outcome, sort_keys=True))
    return 0 if outcome['success'] else 1


if __name__ == '__main__':
    sys.exit(main())
