#!/usr/bin/env python3
"""Independent fixed-event raw-group fidelity audit; no runner imports."""
import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import io
import json
from pathlib import Path
import subprocess
import tempfile

EXP = Path(__file__).resolve().parents[1]
ROOT = EXP.parents[2]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read(path):
    return json.loads(path.read_text())


def sha(data):
    return hashlib.sha256(data).hexdigest()


def table(payload):
    return list(csv.DictReader(io.StringIO(payload.decode('utf-8')), delimiter='\t'))


def locked():
    lock = read(EXP / 'src/PREREG_LOCK.json')
    require(bool(lock), 'empty preregistration lock')
    for name, digest in lock.items():
        path = (ROOT / name).resolve()
        require(path.is_relative_to(ROOT) and path.is_file(), 'invalid locked source')
        require(sha(path.read_bytes()) == digest, 'locked bytes changed: ' + name)
    required = {str((EXP / p).relative_to(ROOT)) for p in ('METHOD.md', 'src/SPEC.json', 'src/run.py', 'src/validate.py')}
    require(required <= set(lock), 'incomplete executable preregistration lock')


def query_command(source, pages):
    command = [str(ROOT / 'vmanus-exp'), 'query-tsv', str(ROOT / source['path']), '--selector', source['selector']]
    for page in pages:
        command.extend(['--allow', page])
    command.extend(['--columns', ','.join(source['columns']), '--forbid-prefix', 'f84', '--forbid-prefix', 'f84r'])
    return command


def guard_control():
    # Synthetic fixture only; the guarded tool rejects the sealed selector
    # before materializing the fixture's remainder.
    runtime = EXP / 'runtime'
    runtime.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='validator_guard_fixture_', dir=runtime) as temporary:
        fixture = Path(temporary) / 'fixture.tsv'
        fixture.write_text('page\tpayload\nf1r\tONE\nf2v\tTWO\nf84r\tFORBIDDEN_FIXTURE\n')
        source = {'path': str(fixture), 'selector': 'page', 'columns': ['page', 'payload']}
        done = subprocess.run(query_command(source, ['f1r', 'f2v']), cwd=ROOT, capture_output=True, check=True)
        require(table(done.stdout) == [{'page': 'f1r', 'payload': 'ONE'}, {'page': 'f2v', 'payload': 'TWO'}], 'real guard repeated-allow fixture')
        stats = [json.loads(line[len('GUARD_STATS '):]) for line in done.stderr.decode().splitlines() if line.startswith('GUARD_STATS ')]
        require(stats == [{'selected': 2, 'skipped_forbidden': 1, 'skipped_not_allowed': 0}], 'real guard fixture counts')


def project(spec):
    projections = read(EXP / 'artifacts/PROJECTIONS.json')
    with (ROOT / spec['allowlist']).open(newline='') as handle:
        allowance = list(csv.DictReader(handle, delimiter='\t'))
    pages = [r['page'] for r in allowance]
    require(len(pages) == len(set(pages)) == 179, 'fixed 179 selectors')
    require(all(not p.startswith('f84') for p in pages), 'sealed selector allowance')
    output = {}
    require(set(projections) == set(spec['sources']) == {'EVENTS', 'CROSS', 'ATLAS'}, 'three projections required')
    for name, source in spec['sources'].items():
        require(source['selector'] == 'page', 'selector-first page gate')
        command = query_command(source, pages)
        done = subprocess.run(command, cwd=ROOT, capture_output=True, check=True)
        notices = [line[len('GUARD_STATS '):] for line in done.stderr.decode().splitlines() if line.startswith('GUARD_STATS ')]
        require(len(notices) == 1, 'one guard report required')
        record = projections[name]
        require(record['path'] == source['path'], 'projection source path')
        path = EXP / 'runtime' / (name + '.tsv')
        require(path.read_bytes() == done.stdout, 'independent guarded projection byte parity: ' + name)
        require(record['sha256'] == sha(done.stdout) and record['bytes'] == len(done.stdout), 'projection digest/length: ' + name)
        require(record['guard_stats'] == json.loads(notices[0]), 'guard statistics parity: ' + name)
        rows = table(done.stdout)
        require(json.loads(notices[0])['selected'] == len(rows), 'guard selected row count')
        require(all(r['page'] in pages and not r['page'].startswith('f84') for r in rows), 'projection selector scope')
        output[name] = rows
    return output


def category(raw, fragments, target):
    require(target in fragments, 'target absent from group fragments')
    return 'CLEANER_FRAGMENT' if len(fragments) > 1 else 'EXACT_RAW_WHOLE' if raw == target else 'NORMALIZED_WHOLE'


def line_map(groups, cleaned):
    ordered = sorted(groups, key=lambda r: int(r['source_group_index']))
    require(bool(ordered), 'missing atlas reader line')
    require([int(r['source_group_index']) for r in ordered] == list(range(1, len(ordered)+1)), 'group index sequence')
    require(all(int(r['source_group_count']) == len(ordered) for r in ordered), 'declared group count')
    require(len({r['source_group_id'] for r in ordered}) == len(ordered), 'duplicate group identity')
    flattened, positions, mapping = [], [], {}
    for i, group in enumerate(ordered):
        fragments = group['clean_ascii_fragments'].split()
        offsets = [int(p) for p in group['legacy_surface_positions_1based'].split(',')] if group['legacy_surface_positions_1based'] else []
        require(len(fragments) == int(group['clean_ascii_fragment_count']) == len(offsets), 'fragment count/positions mismatch')
        status = 'ZERO_ASCII_FRAGMENT' if not fragments else 'ONE_ASCII_FRAGMENT' if len(fragments) == 1 else 'MULTI_ASCII_FRAGMENT'
        require(group['legacy_mapping_status'] == status, 'fragment status mismatch')
        require(all(p not in mapping for p in offsets) and len(set(offsets)) == len(offsets), 'duplicate fragment position')
        for p, fragment in zip(offsets, fragments):
            mapping[p] = (group, fragment, fragments)
        if i:
            require(ordered[i-1]['right_separator'] == group['left_separator'], 'adjacent separator disagreement')
        positions.extend(offsets); flattened.extend(fragments)
    expected = cleaned.split()
    require(positions == list(range(1, len(expected)+1)), 'full clean positions not contiguous/exhaustive')
    require(flattened == expected, 'full clean token sequence differs')
    return ordered, mapping, flattened


def reconstruct(data, spec):
    events, cross, atlas = data['EVENTS'], data['CROSS'], data['ATLAS']
    require(len(events) == spec['expected_events'] == 1777 and len({r['event_id'] for r in events}) == 1777, 'fixed 1777 unique events')
    require(all(e['axis'] in ('L', 'DY') for e in events), 'event axis')
    previous = read(ROOT / spec['baseline_metadata'])
    previous_by = {e['event_id']: e for e in previous}
    require(len(previous) == len(previous_by) == 1777 and set(previous_by) == {e['event_id'] for e in events}, '865 fixed cohort identity')
    for e in events:
        require(all(str(previous_by[e['event_id']][k]) == e[k] for k in ('carrier', 'axis', 'surface', 'page', 'locus', 'token_index')), '865 fixed event metadata')
    require(len({r['source_group_id'] for r in atlas}) == len(atlas), 'global atlas group identity uniqueness')
    cross_by = {}
    for row in cross:
        key = row['page'], row['locus']
        require(key not in cross_by, 'duplicate cross line')
        cross_by[key] = row
    focal = {(e['page'], e['locus']) for e in events}
    grouped = defaultdict(list)
    for row in atlas:
        if (row['page'], row['locus']) in focal and row['edition'] in spec['editions']:
            grouped[(row['page'], row['locus'], row['edition'])].append(row)
    maps, lines, sources = {}, [], {ed: [] for ed in spec['editions']}
    for page, locus in sorted(focal):
        require((page, locus) in cross_by, 'missing focal cross line')
        for ed, fields in sorted(spec['editions'].items()):
            rows, mapping, flat = line_map(grouped[(page, locus, ed)], cross_by[(page, locus)][fields['clean']])
            maps[(page, locus, ed)] = mapping
            sources[ed].extend(rows)
            lines.append({'page': page, 'locus': locus, 'edition': ed, 'groups': len(rows), 'tokens': len(flat),
                          'sequence_sha256': sha(' '.join(flat).encode()), 'passed': True})
    targets = []
    for event in sorted(events, key=lambda r: r['event_id']):
        for ed, fields in sorted(spec['editions'].items()):
            pos = int(event[fields['position']])
            mapping = maps[(event['page'], event['locus'], ed)]
            require(pos in mapping, 'focal position absent from full mapping')
            group, fragment, fragments = mapping[pos]
            require(fragment == event['surface'], 'focal fragment differs from fixed event surface')
            targets.append({'event_id': event['event_id'], 'edition': ed, 'page': event['page'], 'locus': event['locus'],
                            'axis': event['axis'], 'carrier': event['carrier'], 'surface': event['surface'], 'position': pos,
                            'source_group_id': group['source_group_id'], 'source_group_index': int(group['source_group_index']),
                            'raw': group['ivtff_group_raw'], 'fragment_count': len(fragments),
                            'category': category(group['ivtff_group_raw'], fragments, fragment),
                            'left_separator': group['left_separator'], 'right_separator': group['right_separator']})
    cats = spec['categories']
    by_ed = {ed: {cat: 0 for cat in cats} for ed in spec['editions']}
    by_axis = {ed: {axis: {cat: 0 for cat in cats} for axis in ('L', 'DY')} for ed in spec['editions']}
    event_targets = defaultdict(list)
    for t in targets:
        by_ed[t['edition']][t['category']] += 1
        by_axis[t['edition']][t['axis']][t['category']] += 1
        event_targets[t['event_id']].append(t)
    require(all(len(rows) == 3 for rows in event_targets.values()), 'three reader targets per event')
    result = {'status': 'COMPLETE_FIXED_EVENT_RAW_GROUP_FIDELITY', 'claim_ceiling': spec['claim_ceiling'],
              'event_count': len(events), 'target_count': len(targets), 'line_reading_count': len(lines),
              'by_edition': by_ed, 'by_edition_axis': by_axis,
              'all_three_exact': sum(all(t['category'] == 'EXACT_RAW_WHOLE' for t in ts) for ts in event_targets.values()),
              'all_three_single_group': sum(all(t['fragment_count'] == 1 for t in ts) for ts in event_targets.values()),
              'events_any_cleaner_fragment': sum(any(t['category'] == 'CLEANER_FRAGMENT' for t in ts) for ts in event_targets.values()),
              'uncertain_boundary_targets': sum(any(t[k] == 'UNCERTAIN_SMALL_SPACE' for k in ('left_separator', 'right_separator')) for t in targets),
              'drawing_boundary_targets': sum(any(t[k].startswith('DRAWING_') for k in ('left_separator', 'right_separator')) for t in targets)}
    return events, sources, lines, targets, result


def controls():
    guard_control()
    def group(index, raw, frags, positions, left, right, total=2):
        n = len(frags.split())
        return {'source_group_id': str(index), 'source_group_index': str(index), 'source_group_count': str(total),
                'ivtff_group_raw': raw, 'clean_ascii_fragments': frags, 'clean_ascii_fragment_count': str(n),
                'legacy_surface_positions_1based': positions, 'left_separator': left, 'right_separator': right,
                'legacy_mapping_status': 'ZERO_ASCII_FRAGMENT' if n == 0 else 'ONE_ASCII_FRAGMENT' if n == 1 else 'MULTI_ASCII_FRAGMENT'}
    groups = [group(1, '[a:b]', 'a b', '1,2', 'LINE_START', 'DEFINITE_SPACE'),
              group(2, 'c', 'c', '3', 'DEFINITE_SPACE', 'LINE_END')]
    ordered, mapping, flat = line_map(groups, 'a b c')
    require(flat == ['a', 'b', 'c'] and mapping[2][1] == 'b', 'full-line fixture')
    require(category('[a:b]', ['a', 'b'], 'b') == 'CLEANER_FRAGMENT', 'fragment category')
    require(category('[c]', ['c'], 'c') == 'NORMALIZED_WHOLE', 'normalized category')
    require(category('c', ['c'], 'c') == 'EXACT_RAW_WHOLE', 'exact category')
    for field, value in [('source_group_index', '3'), ('source_group_count', '9'), ('clean_ascii_fragment_count', '1'),
                         ('legacy_mapping_status', 'ONE_ASCII_FRAGMENT'), ('legacy_surface_positions_1based', '1,1'),
                         ('right_separator', 'UNCERTAIN_SMALL_SPACE')]:
        bad = [dict(g) for g in groups]; bad[0][field] = value
        try:
            line_map(bad, 'a b c')
        except ValueError:
            pass
        else:
            raise AssertionError('negative line contract accepted: ' + field)
    try:
        line_map(groups, 'a DIFFERENT c')
    except ValueError:
        pass
    else:
        raise AssertionError('clean sequence mismatch accepted')
    zero = [group(1, '@x;', '', '', 'LINE_START', 'DEFINITE_SPACE'), group(2, 'c', 'c', '1', 'DEFINITE_SPACE', 'LINE_END')]
    require(line_map(zero, 'c')[2] == ['c'], 'zero-fragment handling')
    print(json.dumps({'status': 'CONTROLS_PASS', 'target_access': False}, sort_keys=True))


def validate():
    locked()
    spec = read(EXP / 'src/SPEC.json')
    data = project(spec)
    artifacts = EXP / 'artifacts'
    try:
        events, sources, lines, targets, result = reconstruct(data, spec)
    except (ValueError, KeyError) as exc:
        recorded = read(artifacts / 'RESULT.json')
        require(recorded['status'] == 'STOP_SOURCE_CONTRACT' and recorded['claim_ceiling'] == spec['claim_ceiling'], 'source-contract failure must stop runner')
        require(not (artifacts / 'TARGETS.json').exists(), 'stopped contract must not publish target categories')
        return {'status': 'PASS', 'validated_source_contract_stop': True, 'independent_stop_reason': str(exc), 'independent_guarded_projections': 3, 'claim_ceiling': spec['claim_ceiling'], 'image_analysis': False, 'model_scoring': False}
    require(read(artifacts / 'EVENTS.json') == events, 'published events parity')
    for ed, rows in sources.items():
        require(table((artifacts / ('SOURCE_GROUPS_' + ed + '.tsv')).read_bytes()) == rows, 'published source groups parity: ' + ed)
    require(read(artifacts / 'LINE_PARITY.json') == lines, 'published full line contracts parity')
    require(read(artifacts / 'TARGETS.json') == targets, 'published all targets parity')
    require(read(artifacts / 'RESULT.json') == result, 'independent aggregate parity')
    return {'status': 'PASS', 'event_count': len(events), 'target_count': len(targets), 'line_reading_count': len(lines),
            'independent_guarded_projections': 3, 'claim_ceiling': spec['claim_ceiling'],
            'image_analysis': False, 'model_scoring': False}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--controls', action='store_true')
    parser.add_argument('--no-write', action='store_true')
    args = parser.parse_args()
    if args.controls:
        controls()
        return 0
    try:
        result = validate()
    except (ValueError, KeyError, OSError, TypeError, subprocess.CalledProcessError) as exc:
        result = {'status': 'FAIL', 'reason': str(exc), 'image_analysis': False, 'model_scoring': False}
    payload = json.dumps(result, sort_keys=True, indent=2) + '\n'
    if not args.no_write:
        (EXP / 'artifacts/VALIDATION.json').write_text(payload)
    print(payload, end='')
    return 0 if result['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
