#!/usr/bin/env python3
"""Fixed GDT1036 lexical-capacity census; no semantic parser or vocabulary fit."""
from pathlib import Path
from collections import Counter
from fractions import Fraction
import argparse
import csv
import hashlib
import json
import re
import subprocess

ROOT = Path(__file__).resolve().parents[4]
EXP = Path(__file__).resolve().parents[1]
READERS = ('ZL3b', 'IT2a', 'RF1b')


class InputMismatch(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise InputMismatch(message)


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def compact(value):
    return (json.dumps(value, ensure_ascii=False, separators=(',', ':')) + '\n').encode('utf-8')


def inventory(offer, allowed_operations, check_sizes=True):
    primary = offer['lexicon']
    alternate = offer['alternative_reading_values']
    require(not set(primary) & set(alternate), 'overlapping primary/alternate keys')
    if check_sizes:
        require(len(primary) == 65 and len(alternate) == 15, 'inventory size mismatch')
    entries = {**primary, **alternate}
    allowed = set(allowed_operations)
    cache = {}

    def resolve(word, active=()):
        require(word in entries, 'unbound inventory dependency')
        require(word not in active, 'cyclic inventory dependency')
        if word in cache:
            return cache[word]
        entry = entries[word]
        require(isinstance(entry, dict), 'invalid inventory entry')
        found = {entry['value']} if isinstance(entry.get('value'), str) and entry['value'] in allowed else set()
        dependencies = list(entry.get('composition', []))
        if 'same_hypothesized_value_as' in entry:
            dependencies.append(entry['same_hypothesized_value_as'])
        for child in dependencies:
            found.update(resolve(child, (*active, word)))
        cache[word] = sorted(found)
        return cache[word]

    for word in entries:
        resolve(word)
    return entries, cache


def natural(value):
    return tuple((1, int(x)) if x.isdigit() else (0, x)
                 for x in re.split(r'(\d+)', str(value)) if x)


def pair_natural(pair):
    return (pair['leaf'], pair['page'], tuple(natural(x) for x in pair['loci']))


def rank_key(pair):
    m = pair['metrics']
    ids = tuple(pair['readers'][r] for r in ('ZL3b', 'IT2a'))
    return (m['max_unknown_types'], -Fraction(*m['min_known_fraction']),
            -m['min_known_types'], *pair_natural(pair), ids)


def rejection_reasons(row, spec):
    b = spec['bounds']
    conditions = [
        ('EXCLUDED_LEAF', row['leaf'] in spec['excluded_leaves']),
        ('BELOW_MIN_GROUPS', row['groups'] < b['min_groups']),
        ('ABOVE_MAX_GROUPS', row['groups'] > b['max_groups']),
        ('BELOW_MIN_KNOWN_TYPES', row['known_type_count'] < b['min_known_types']),
        ('ABOVE_MAX_UNKNOWN_TYPES', row['unknown_type_count'] > b['max_unknown_types']),
        ('BELOW_MIN_KNOWN_FRACTION', row['known_positions'] * b['min_known_fraction_denominator'] < row['groups'] * b['min_known_fraction_numerator']),
        ('BELOW_MIN_OPERATION_VALUES', len(row['operation_values']) < b['min_operation_values']),
    ]
    return [name for name, fails in conditions if fails]


def make_row(reader, paragraph, entries, tags, spec):
    page = paragraph['page']
    require(not page.startswith('f84') and page != 'f116v', 'forbidden source selector')
    require(isinstance(paragraph['leaf'], int), 'noninteger physical leaf')
    lines = []
    raw_words = []
    for line in paragraph['lines']:
        words, source_ids = line['words'], line['source_ids']
        require(len(words) == len(source_ids), 'word/source-id length mismatch')
        require(isinstance(line['anchor_eligible'], bool), 'nonboolean source flag')
        require(all(isinstance(w, str) for w in words), 'nonstring raw group')
        # Preserve every line field except the two arrays replaced by lossless triplets.
        out_line = {k: v for k, v in line.items() if k not in ('words', 'source_ids')}
        out_line['positions'] = [[sid, word, word in entries] for sid, word in zip(source_ids, words)]
        lines.append(out_line)
        raw_words.extend(words)
    require(len(raw_words) == paragraph['groups'] and len(raw_words) > 0, 'paragraph group count mismatch')
    loci = [line['locus'] for line in paragraph['lines']]
    require(len(loci) == len(set(loci)), 'duplicate locus in whole paragraph')
    known = sorted(set(raw_words) & entries.keys())
    unknown = sorted(set(raw_words) - entries.keys())
    known_positions = sum(w in entries for w in raw_words)
    operations = sorted({tag for word in known for tag in tags[word]})
    row = dict(id=reader + '|' + paragraph['id'], reader=reader,
               paragraph_id=paragraph['id'], page=page, leaf=paragraph['leaf'], loci=loci,
               groups=len(raw_words), known_positions=known_positions,
               unknown_positions=len(raw_words)-known_positions, known_types=known,
               unknown_types=unknown, known_type_count=len(known), unknown_type_count=len(unknown),
               operation_values=operations, known_fraction=[known_positions, len(raw_words)],
               strict_anchor_eligible=all(line['anchor_eligible'] for line in paragraph['lines']),
               lines=lines, pair_id=page + '|' + ','.join(loci))
    row['reasons'] = rejection_reasons(row, spec)
    row['eligible'] = not row['reasons']
    return row


def evaluate(packet, offer, spec, registration_commit, check_sizes=True):
    require(set(packet) == set(READERS), 'unexpected reader population')
    counts = {reader: len(packet[reader]) for reader in READERS}
    require(counts == spec['expected_rows'], 'paragraph population mismatch')
    entries, tags = inventory(offer, spec['operation_values'], check_sizes)
    rows, original, grouped, row_ids = [], {}, {}, set()
    for reader in READERS:
        for paragraph in packet[reader]:
            row = make_row(reader, paragraph, entries, tags, spec)
            require(row['id'] not in row_ids, 'duplicate reader paragraph ID')
            row_ids.add(row['id'])
            key = (row['page'], tuple(row['loci']))
            group = grouped.setdefault(key, {})
            require(reader not in group, 'duplicate counterpart for exact whole locus list')
            require(not group or next(iter(group.values()))['leaf'] == row['leaf'], 'paired physical leaf mismatch')
            group[reader] = row
            rows.append(row)
            original[row['id']] = paragraph
    pairs = []
    pair_ids = set()
    for (page, loci), group in grouped.items():
        first = next(iter(group.values()))
        pair = dict(id=first['pair_id'], page=page, leaf=first['leaf'], loci=list(loci),
                    readers={r: group[r]['id'] for r in READERS if r in group})
        require(pair['id'] not in pair_ids, 'pair serialization ID collision')
        pair_ids.add(pair['id'])
        missing = ['MISSING_' + r for r in ('ZL3b', 'IT2a') if r not in group]
        if missing:
            pair.update(eligible=False, reasons=missing, metrics=None)
        else:
            fractions = [Fraction(*group[r]['known_fraction']) for r in ('ZL3b', 'IT2a')]
            fraction = min(fractions)
            reasons = [r + ':' + reason for r in ('ZL3b', 'IT2a') for reason in group[r]['reasons']]
            pair.update(eligible=not reasons, reasons=reasons, metrics={
                'max_unknown_types': max(group[r]['unknown_type_count'] for r in ('ZL3b', 'IT2a')),
                'min_known_fraction': [fraction.numerator, fraction.denominator],
                'min_known_types': min(group[r]['known_type_count'] for r in ('ZL3b', 'IT2a'))})
        pairs.append(pair)
    pairs.sort(key=pair_natural)
    ranked = [{**p, 'rank': i+1} for i, p in enumerate(sorted((p for p in pairs if p['eligible']), key=rank_key))]
    selected = dict(pair=ranked[0] if ranked else None, paragraphs={}, bindings={})
    if ranked:
        for reader in ('ZL3b', 'IT2a'):
            p = original[ranked[0]['readers'][reader]]
            selected['paragraphs'][reader] = p
            selected['bindings'][reader] = [
                dict(source_id=sid, raw=word, known=word in entries,
                     value=entries.get(word), operation_values=tags.get(word, []))
                for line in p['lines'] for sid, word in zip(line['source_ids'], line['words'])]
    result = dict(experiment='GDT1036',
                  decision='ONE_COMPLETE_EXTENSION_TARGET' if ranked else 'PARK_WITHIN_FROZEN_CAPACITY_LIMITS',
                  rows=len(rows), reader_counts=counts, pairs=len(pairs),
                  matched_pairs=sum(p['metrics'] is not None for p in pairs), eligible_pairs=len(ranked),
                  selected_pair_id=ranked[0]['id'] if ranked else None,
                  inventory=dict(primary_types=len(offer['lexicon']), alternate_types=len(offer['alternative_reading_values']), total_types=len(entries)),
                  fully_covered_rows=[r['id'] for r in rows if not r['unknown_positions']],
                  eligible_rows=[r['id'] for r in rows if r['eligible']],
                  source_uncertain_rows=[r['id'] for r in rows if not r['strict_anchor_eligible']],
                  rejection_counts=dict(sorted(Counter(reason for row in rows for reason in row['reasons']).items())),
                  registration_commit=registration_commit,
                  claims=dict(confirmed_words=0, independent_meaning_capacity=0, significance=False, readers_independent=False))
    return {'ROWS.json': rows, 'PAIRS.json': pairs, 'RANKED.json': ranked,
            'SELECTED.json': selected, 'RESULT.json': result}


def registration(spec):
    lock_path = EXP / 'PREREG_LOCK.json'
    lock = load(lock_path)
    receipt = load(EXP / 'artifacts/PUBLIC_REGISTRATION.json')
    commit = receipt['commit']
    require(isinstance(commit, str) and bool(re.fullmatch(r'[0-9a-f]{40}', commit)), 'invalid public registration commit')
    lock_relative = lock_path.relative_to(ROOT).as_posix()
    sealed = subprocess.run(['git', 'show', commit + ':' + lock_relative], cwd=ROOT, capture_output=True)
    require(sealed.returncode == 0 and sealed.stdout == lock_path.read_bytes(), 'public commit does not contain exact preregistration lock')
    required = [spec['offer'], spec['source_packet'], spec['paragraphs'],
                (EXP / 'src/SPEC.json').relative_to(ROOT).as_posix(),
                Path(__file__).resolve().relative_to(ROOT).as_posix(),
                (EXP / 'PREREGISTRATION.md').relative_to(ROOT).as_posix()]
    require(all(p in lock['files'] for p in required), 'lock omits required scientific input or runner')
    for name, digest in lock['files'].items():
        path = (ROOT / name).resolve()
        require(path.is_relative_to(ROOT), 'nonrepository lock path')
        require(hashlib.sha256(path.read_bytes()).hexdigest() == digest, 'locked input changed: ' + name)
    return commit


CSV_FIELDS = ['id', 'reader', 'paragraph_id', 'page', 'leaf', 'groups', 'known_positions',
              'unknown_positions', 'known_type_count', 'unknown_type_count',
              'known_fraction_numerator', 'known_fraction_denominator', 'operation_values',
              'strict_anchor_eligible', 'eligible', 'reasons', 'pair_id']


def execute():
    spec = load(EXP / 'src/SPEC.json')
    commit = registration(spec)  # All access below requires the exact public lock.
    offer = load(ROOT / spec['offer'])
    packet = load(ROOT / spec['paragraphs'])
    artifacts = evaluate(packet, offer, spec, commit)
    encoded = {name: compact(value) for name, value in artifacts.items()}
    require(len(encoded['ROWS.json']) < 5_000_000, 'compact ROWS exceeds 5MB artifact bound')
    for name, data in encoded.items():
        (EXP / 'artifacts' / name).write_bytes(data)
    with (EXP / 'artifacts/COUNTS.csv').open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS, lineterminator='\n')
        writer.writeheader()
        for row in artifacts['ROWS.json']:
            out = {key: row[key] for key in CSV_FIELDS if key in row}
            out.update(known_fraction_numerator=row['known_fraction'][0], known_fraction_denominator=row['known_fraction'][1])
            out['operation_values'] = '|'.join(row['operation_values'])
            out['reasons'] = '|'.join(row['reasons'])
            writer.writerow(out)
    return artifacts['RESULT.json']


def selftest():
    # Synthetic fixtures only: do not read SPEC, the real offer or any corpus source.
    ops = ['DRY', 'GRIND']
    spec = dict(excluded_leaves=[21, 32], expected_rows={'ZL3b': 1, 'IT2a': 1, 'RF1b': 0},
                operation_values=ops, bounds=dict(min_groups=25, max_groups=100, min_known_types=8,
                max_unknown_types=20, min_known_fraction_numerator=1, min_known_fraction_denominator=2,
                min_operation_values=2))
    primary = {f'k{i}': {'value': 'DRY' if i == 0 else 'GRIND' if i == 1 else 'NOUN'} for i in range(8)}
    offer = dict(lexicon=primary, alternative_reading_values={
        'alias': {'same_hypothesized_value_as': 'k0'},
        'combo': {'composition': ['alias', 'k1'], 'value': 'DRY_AND_GRIND'},
        '[a:?]': {'same_hypothesized_value_as': 'combo'}})
    entries, tags = inventory(offer, ops, False)
    require(tags['[a:?]'] == ['DRY', 'GRIND'] and '[a:?]' in entries and 'a' not in entries, 'synthetic alias/composition/raw failure')
    def para(words, leaf=22, locus='f22r.2', eligible=False, identifier='P'):
        return dict(id=identifier, page=f'f{leaf}r', leaf=leaf, groups=len(words), lines=[
            dict(locus=locus, anchor_eligible=eligible, offset=0, words=words,
                 source_ids=[f'{locus}:{i}' for i in range(len(words))])])
    words = [f'k{i}' for i in range(8)] + ['k0']*5 + ['u']*12
    p = para(words)
    row = make_row('ZL3b', p, entries, tags, spec)
    require(row['eligible'] and not row['strict_anchor_eligible'], 'source flags incorrectly gate row')
    checks = 3
    base = dict(row, groups=40, known_positions=20, known_type_count=8, unknown_type_count=20, operation_values=ops, leaf=22)
    require(not rejection_reasons(base, spec), 'equality bounds rejected')
    for field, value, reason in [
        ('groups',24,'BELOW_MIN_GROUPS'), ('groups',101,'ABOVE_MAX_GROUPS'),
        ('known_type_count',7,'BELOW_MIN_KNOWN_TYPES'), ('unknown_type_count',21,'ABOVE_MAX_UNKNOWN_TYPES'),
        ('known_positions',19,'BELOW_MIN_KNOWN_FRACTION'), ('operation_values',['DRY'],'BELOW_MIN_OPERATION_VALUES'),
        ('leaf',21,'EXCLUDED_LEAF'), ('leaf',32,'EXCLUDED_LEAF')]:
        require(reason in rejection_reasons({**base, field:value}, spec), 'boundary failed: '+reason)
        checks += 1
    for n in (25,100):
        require(not rejection_reasons({**base,'groups':n,'known_positions':n},spec), 'group equality failed')
        checks += 1
    packet = {'ZL3b':[p], 'IT2a':[para(words)], 'RF1b':[]}
    out = evaluate(packet, offer, spec, 'synthetic', False)
    require(out['RESULT.json']['eligible_pairs']==1 and len(out['SELECTED.json']['bindings']['ZL3b'])==25, 'complete pair fixture')
    require(out['ROWS.json'][0]['lines'][0]['positions'][0] == ['f22r.2:0','k0',True], 'lossless position fixture')
    changed = {'ZL3b':[p], 'IT2a':[para(words,locus='f22r.3')], 'RF1b':[]}
    require(evaluate(changed,offer,spec,'synthetic',False)['RESULT.json']['eligible_pairs']==0, 'mismatched full loci paired')
    try:
        duplicate = {'ZL3b':[p,para(words,identifier='P2')], 'IT2a':[para(words)], 'RF1b':[]}
        evaluate(duplicate,offer,{**spec,'expected_rows':{'ZL3b':2,'IT2a':1,'RF1b':0}},'synthetic',False)
    except InputMismatch:
        checks += 1
    else:
        raise AssertionError('duplicate counterpart accepted')
    def candidate(frac=(1,2), locus='f22r.2', unknown=1, known=8, leaf=22, page='f22r', ids=('a','b')):
        return dict(leaf=leaf,page=page,loci=[locus],readers=dict(zip(('ZL3b','IT2a'),ids)),
                    metrics=dict(max_unknown_types=unknown,min_known_fraction=list(frac),min_known_types=known))
    require(rank_key(candidate((2,3))) < rank_key(candidate((1,2))), 'fraction direction')
    require(rank_key(candidate((10**30+1,2*10**30))) < rank_key(candidate()), 'fraction precision lost')
    require(rank_key(candidate(locus='f22r.2')) < rank_key(candidate(locus='f22r.10')), 'natural locus ordering')
    require(rank_key(candidate(unknown=0)) < rank_key(candidate(unknown=1)), 'unknown priority')
    require(rank_key(candidate(known=9)) < rank_key(candidate(known=8)), 'known type direction')
    require(rank_key(candidate(leaf=2)) < rank_key(candidate(leaf=10)), 'numeric leaf order')
    require(rank_key(candidate(page='f22r')) < rank_key(candidate(page='f22v')), 'page string order')
    require(rank_key(candidate(ids=('a','b'))) < rank_key(candidate(ids=('a','c'))), 'ID tiebreak')
    require(compact(out['ROWS.json']).endswith(b'\n'), 'artifact newline')
    return dict(status='PASS',synthetic_checks=checks+13,target_opened=False,artifacts_written=False)


def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--self-test', action='store_true')
    group.add_argument('--execute', action='store_true')
    args = parser.parse_args()
    if args.self_test:
        print(json.dumps(selftest()))
        return 0
    try:
        result = execute()
    except (InputMismatch, KeyError, OSError, json.JSONDecodeError) as exc:
        print(json.dumps(dict(status='INPUT_MISMATCH',error=str(exc))))
        return 2
    print(json.dumps({key:result[key] for key in ('decision','rows','pairs','eligible_pairs','selected_pair_id')}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
