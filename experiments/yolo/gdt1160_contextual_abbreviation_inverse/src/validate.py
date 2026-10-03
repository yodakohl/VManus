#!/usr/bin/env python3
"""Independent GDT1160 validator. Never imports the runner or refits models."""
from __future__ import annotations
import argparse, collections, csv, hashlib, json, math
from pathlib import Path
EXP = Path(__file__).resolve().parents[1]
ROOT = EXP.parents[2]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_rows(name):
    with (ROOT / name).open(encoding='utf-8', newline='') as stream:
        for row in csv.DictReader(stream, delimiter='\t'):
            if row['corpus'] == 'NUREMBERG':
                yield row


def context_counts(groups, index, radius=8):
    counts = collections.Counter()
    for offset in range(-radius, radius + 1):
        if offset == 0 or not 0 <= index + offset < len(groups):
            continue
        token = groups[index + offset]
        for width in (2, 3, 4):
            for start in range(len(token) - width + 1):
                key = f'{offset}:{token[start:start + width]}'
                bucket = int.from_bytes(hashlib.sha256(key.encode('utf-8')).digest()[:8], 'big') % 4096
                counts[bucket] += 1
    return dict(counts)


def normalized(counts):
    norm = math.sqrt(sum(value * value for value in counts.values()))
    return {key: value / norm for key, value in counts.items()} if norm else {}


def layout_vector(row):
    result = [0.] * 10
    result[row['record_position_quartile']] = 1.
    result[4 + (4 * row['line_group_index'] // row['line_group_count'])] = 1.
    result[8] = float(row['first_line'])
    result[9] = float(row['last_line'])
    return result


def masked_probabilities(logits, prior_counts, candidates, all_outputs):
    """Log-prior offset followed by softmax on train-licensed candidates only."""
    total = sum(prior_counts.values())
    adjusted = [logits[all_outputs.index(value)] + math.log(prior_counts[value] / total)
                for value in candidates]
    maximum = max(adjusted)
    exps = [math.exp(value - maximum) for value in adjusted]
    return [value / sum(exps) for value in exps]


def mean_probabilities(vectors):
    if not vectors or len({len(vector) for vector in vectors}) != 1:
        raise ValueError('Probability vector size')
    for vector in vectors:
        if any(not math.isfinite(x) or x < 0 for x in vector) or abs(sum(vector) - 1) > 1e-5:
            raise ValueError('Invalid candidate probabilities')
    return [sum(row[i] for row in vectors) / len(vectors) for i in range(len(vectors[0]))]


def choose(candidates, probabilities):
    if candidates != sorted(set(candidates)) or len(candidates) != len(probabilities):
        raise ValueError('Candidate alignment')
    return candidates[max(range(len(candidates)), key=lambda i: probabilities[i])]


def macro_type_accuracy(rows):
    types = collections.defaultdict(list)
    for row in rows:
        types[row['marked_group']].append(row['prediction'] == row['truth'])
    return sum(sum(v) / len(v) for v in types.values()) / len(types) if types else None


def gates(metrics):
    means = {arm: sum(values) / len(values) for arm, values in metrics.items()}
    context = {}
    for arm in ('C', 'N'):
        gain = means[arm] - max(means['F'], means['L'])
        folds = sum(x > f and x > l for x, f, l in zip(metrics[arm], metrics['F'], metrics['L']))
        context[arm] = {'gain': gain, 'positive_folds': folds, 'pass': gain >= .03 and folds >= 3}
    gain = means['N'] - means['C']
    folds = sum(n > c for n, c in zip(metrics['N'], metrics['C']))
    return {'means': means, 'context': context, 'neural': {'gain': gain, 'positive_folds': folds,
            'pass': context['N']['pass'] and gain >= .01 and folds >= 3}}


def reconstruct(spec):
    lines = list(source_rows('gdt155_blinded_diplomatic.tsv'))
    records = collections.defaultdict(list)
    for line in lines:
        records[line['record_id']].append(line)
    marker_positions, groups_by_record = {}, {}
    for record, members in records.items():
        members.sort(key=lambda row: int(row['line_index']))
        assert [int(row['line_index']) for row in members] == list(range(1, len(members) + 1))
        assert {int(row['record_line_count']) for row in members} == {len(members)}
        groups, markers = [], []
        for line_index, line in enumerate(members):
            tokens = line['diplomatic_marked'].split()
            # Historical surface_group_count is a separate bare representation;
            # registered context uses whitespace groups of diplomatic_marked.
            for token_index, token in enumerate(tokens):
                location = {'line_id': line['line_id'], 'group_index': len(groups), 'line_group_index': token_index,
                            'line_group_count': len(tokens), 'record_position_quartile': int(line['record_position_quartile']),
                            'first_line': line_index == 0, 'last_line': line_index == len(members) - 1,
                            'page_id': line['page_id'], 'book': line['book_or_ms'], 'group': token}
                markers.extend([location] * token.count('¤'))
                groups.append(token)
        marker_positions[record] = markers
        groups_by_record[record] = groups
    blind = list(source_rows('gdt155_blinded_abbreviation_sites.tsv'))
    truths = {row['site_id']: row for row in source_rows('gdt155_unblinded_abbreviation_sites.tsv')}
    assert len(truths) == len(blind) == sum(len(v) for v in marker_positions.values())
    eligible = []
    for site in blind:
        record = site['record_id']
        location = marker_positions[record][int(site['site_index_in_record']) - 1]
        assert location['line_id'] == site['line_id']
        if location['group'] != site['surface_span_marked'] or location['group'].count('¤') != 1:
            continue
        truth = truths[site['site_id']]
        assert truth['record_id'] == record and truth['line_id'] == site['line_id']
        eligible.append(dict(location, site_id=site['site_id'], record_id=record,
                             marked_group=site['surface_span_marked'], truth=truth['expanded_span']))
    assert len(eligible) == spec['expected_source_eligible_sites']
    folds = []
    for held, expected in zip(spec['books'], spec['expected_held_sites']):
        training = [row for row in eligible if row['book'] != held]
        counts = collections.defaultdict(collections.Counter)
        pages = collections.defaultdict(lambda: collections.defaultdict(set))
        for row in training:
            key, value = row['marked_group'], row['truth']
            counts[key][value] += 1
            pages[key][value].add((row['book'], row['page_id']))
        qualified = sorted(key for key, values in counts.items() if sum(n >= 5 and len(pages[key][value]) >= 3
                            for value, n in values.items()) >= 2)
        domains = {key: sorted(counts[key]) for key in qualified}
        testing = [row for row in eligible if row['book'] == held and row['marked_group'] in domains]
        assert len(testing) == expected
        folds.append({'held_book': held, 'domains': domains, 'counts': {key: dict(counts[key]) for key in qualified},
                      'pages': {key: {value: len(pages[key][value]) for value in counts[key]} for key in qualified},
                      'training': [row for row in training if row['marked_group'] in domains], 'testing': testing})
    return {'lines': lines, 'records': records, 'groups': groups_by_record, 'eligible': eligible, 'folds': folds}


def fixtures():
    assert context_counts(['secret¤'], 0) == {}
    assert context_counts(['ab', 'secret¤'], 1) == {1123: 1}
    assert context_counts(['x'] * 19, 9) == {}
    assert context_counts(['ſe', 't'], 1) != context_counts(['se', 't'], 1)
    assert abs(sum(v*v for v in normalized({1: 3, 2: 4}).values()) - 1) < 1e-12
    assert normalized({}) == {}
    assert mean_probabilities([[.9, .1], [.1, .9]]) == [.5, .5]
    assert choose(['a', 'ſ'], [.5, .5]) == 'a'
    assert all(abs(x-y) < 1e-12 for x,y in zip(masked_probabilities(
        [0., 1000., 0.], {'a': 3, 'c': 1}, ['a','c'], ['a','b','c']), [.75,.25]))
    assert layout_vector({'record_position_quartile':2,'line_group_index':3,'line_group_count':4,
                          'first_line':False,'last_line':True}) == [0.,0.,1.,0.,0.,0.,0.,1.,0.,1.]
    assert macro_type_accuracy([{'marked_group':'a', 'prediction':'a', 'truth':'a'}] * 9 +
                               [{'marked_group':'b', 'prediction':'b', 'truth':'unknown'}]) == .5
    bad = gates({'F':[.9]*4, 'L':[.5]*4, 'C':[.8]*4, 'N':[.85]*4})
    assert not bad['context']['C']['pass'] and not bad['neural']['pass']
    return 'PASS (invented fixtures, not scientific findings)'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--prepare', action='store_true')
    parser.parse_args()
    spec = json.loads((EXP / 'SPEC.json').read_text())
    pins = {name: sha(ROOT / name) == expected for name, expected in spec['source_inputs'].items()}
    assert all(pins.values()), pins
    panel = reconstruct(spec)
    summary = {'mode':'PREPARATION', 'source_pins':pins, 'fixtures':fixtures(),
               'source_lines':len(panel['lines']), 'source_records':len(panel['records']),
               'eligible_sites':len(panel['eligible']), 'held_sites':[len(f['testing']) for f in panel['folds']],
               'training_types':[len(f['domains']) for f in panel['folds']],
               'oov_truths':[sum(r['truth'] not in f['domains'][r['marked_group']] for r in f['testing']) for f in panel['folds']],
               'claim_ceiling':'Source bookkeeping and registered feature fixtures; no model or meaning certification.'}
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
