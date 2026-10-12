from pathlib import Path
from collections import Counter
import argparse
import csv
import hashlib
import itertools
import json

BASE = Path(__file__).resolve().parents[1]
ROOT = BASE.parents[2]
OLD = 'experiments/yolo/gdt1274_shorter_reference_doublet_bound/artifacts/RESULT.json'
MANIFEST = 'experiments/yolo/gdt1274_shorter_reference_doublet_bound/experiment.json'


def read(path):
    return json.loads(path.read_text())


def roster(context, subjects, observations):
    groups = [('FRAME', context)]
    groups.extend(('SUBJECT', x) for x in sorted(subjects))
    keys = sorted({key for subject, key in observations})
    for key in keys:
        groups.append(('HEAD',) + key)
        members = Counter(subject for subject, observed in observations if observed == key)
        assert members and set(members) <= set(subjects)
        groups.extend(('MEMBER', subject, count) for subject, count in sorted(members.items()))
    return groups


def decode_roster(groups):
    context = None
    subjects = set()
    head = None
    observations = []
    for group in groups:
        if group[0] == 'FRAME':
            assert context is None
            context = group[1]
        elif group[0] == 'SUBJECT':
            assert head is None and group[1] not in subjects
            subjects.add(group[1])
        elif group[0] == 'HEAD':
            head = group[1:]
        else:
            assert group[0] == 'MEMBER' and head is not None
            _, subject, count = group
            assert subject in subjects and count > 0
            observations.extend([(subject, head)] * count)
    return context, subjects, Counter(observations)


def contextual_decode(words):
    assert len(words) == 4 and words[0] == 0 and words[1] == 1 and words[3] == 2
    assert words[2] in (2, 3)
    return [['FRAME', 'C'], ['SUBJECT', 'A'],
            ['HEAD', 'DRY', '+' if words[2] == 2 else '-', []], ['MEMBER', 'A', 1]]


def contrasts():
    group = ['PHASE', [1, 1], [['DRY', '+', 1]]]
    phase = {'groups': [group, group], 'intervals': [[0, 1], [1, 2]], 'native_binding': False}
    outside = {'encoded_plus': [0, 1, 2, 2], 'encoded_minus': [0, 1, 3, 2],
               'decoded_plus': contextual_decode([0, 1, 2, 2]),
               'decoded_minus': contextual_decode([0, 1, 3, 2]),
               'global_word_decoder': False, 'native_binding': False}
    return phase, outside


def controls():
    primitive = [('A', ('DRY', '+')), ('A', ('DRY', '-')),
                 ('B', ('INTACT', '+')), ('A', ('MASS', '+', 0, 1, 'g')),
                 ('A', ('LINK', '+', 'A')), ('B', ('LINK', '+', 'EXTERNAL'))]
    checked = variation_checks = 0
    for amounts in itertools.product(range(3), repeat=len(primitive)):
        facts = [fact for fact, amount in zip(primitive, amounts) for _ in range(amount)]
        groups = roster('C', {'A', 'B', 'EMPTY'}, facts)
        assert decode_roster(groups) == ('C', {'A', 'B', 'EMPTY'}, Counter(facts))
        assert all(a != b for a, b in zip(groups, groups[1:]))
        # Arbitrary spellings can vary within a type, but not overlap across types.
        ids = {g: i for i, g in enumerate(sorted(set(groups)))}
        for phase in (0, 1):
            spelled = [(ids[g], (i + phase) % 2) for i, g in enumerate(groups)]
            assert all(a != b for a, b in zip(spelled, spelled[1:]))
            variation_checks += 1
        checked += 1
    boundaries = [roster('C', set(), []), roster('D', set(), []),
                  roster('E', {'A'}, []), roster('F', {'A'}, [('A', ('DRY', '+'))])]
    joined = sum(boundaries, [])
    assert all(a != b for a, b in zip(joined, joined[1:]))
    phase, outside = contrasts()
    assert phase['groups'][0] == phase['groups'][1] and phase['intervals'][0] != phase['intervals'][1]
    assert outside['encoded_plus'][2] == outside['encoded_plus'][3]
    assert outside['decoded_plus'][2] != outside['decoded_plus'][3]
    assert outside['decoded_plus'] != outside['decoded_minus']
    return {'status': 'PASS', 'source_free': True, 'native_data_read': False,
            'primary_runner_read_or_imported': False, 'observation_multisets': checked,
            'disjoint_multispelling_cases': variation_checks, 'frame_boundary_fixture': True,
            'phase_repeat_countermodel': True, 'contextual_homograph_countermodel': True}


def main():
    for path, expected in read(BASE / 'src/REGISTRATION_LOCK.json')['hashes'].items():
        assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == expected, path
    manifest = read(ROOT / MANIFEST)
    matches = [r for r in manifest['outputs'] if r['path'] == OLD]
    assert len(matches) == 1
    assert hashlib.sha256((ROOT / OLD).read_bytes()).hexdigest() == matches[0]['sha256']
    old = read(ROOT / OLD)
    result = read(BASE / 'artifacts/RESULT.json')
    allowed = {r['page'] for r in csv.DictReader(
        (ROOT / 'experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv').open(),
        delimiter='\t')}
    assert result['status'] == 'ROSTER_WORD_REALIZATION_CONTRADICTED'
    assert [c['reader'] for c in old['cases']] == ['ZL3b', 'IT2a', 'RF1b']
    assert len(result['cases']) == len(old['cases']) == 3
    receipts = []
    for previous, current in zip(old['cases'], result['cases']):
        reader, locus = previous['reader'], previous['locus']
        start = previous['first_group_index']
        form = previous['form']
        assert form and ''.join(previous['working_units']) == form
        assert previous['width'] == len(previous['working_units'])
        line = sorted(previous['complete_line'], key=lambda r: int(r['source_group_index']))
        indexes = [int(r['source_group_index']) for r in line]
        assert len(set(indexes)) == len(indexes)
        assert start in indexes
        position = indexes.index(start)
        assert position >= 1 and position + 2 < len(line)
        span = line[position - 1:position + 3]
        assert [int(r['source_group_index']) for r in span] == [start - 1, start, start + 1, start + 2]
        for row in line:
            assert row['edition'] == reader and row['locus'] == locus and row['kind'] == 'P'
            assert row['page'] in allowed and not row['page'].startswith('f84')
            assert row['page'] not in ['f1r', 'f116v']
            assert int(row['source_group_count']) >= int(row['source_group_index']) >= 1
        assert len({r['page'] for r in span}) == 1
        assert span[1]['ivtff_group_raw'] == span[2]['ivtff_group_raw'] == form
        for left, right in zip(span, span[1:]):
            assert left['right_separator'] == right['left_separator'] == 'DEFINITE_SPACE'
        expected = {'reader': reader, 'locus': locus, 'first_group_index': start,
                    'form': form, 'selected_rows': span, 'roster_realization_possible': False}
        assert current == expected
        receipts.append({'reader': reader, 'locus': locus, 'consecutive_equal_wholes': True,
                         'three_definite_seams': True, 'old_manifest_output_hash_verified': True})
    phase, outside = contrasts()
    assert result['phase_counterexample'] == phase
    assert result['outside_contract'] == outside
    assert isinstance(result['scope'], str) and result['scope']
    output = {'status': 'PASS', 'old_cases_checked': 3, 'cases': receipts,
              'source_free_controls': controls(),
              'scope': 'Independent old-packet identity/seam replay and typed-record proofs only; no new native count, perceptual validation, word meaning or native time interpretation.'}
    (BASE / 'artifacts/VALIDATION.json').write_text(json.dumps(output, indent=2, sort_keys=True) + '\n')
    print(json.dumps(output, sort_keys=True))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--controls', action='store_true')
    args = parser.parse_args()
    if args.controls:
        output = controls()
        (BASE / 'artifacts/VALIDATOR_CONTROLS.json').write_text(json.dumps(output, indent=2, sort_keys=True) + '\n')
        print(json.dumps(output, sort_keys=True))
    else:
        main()
