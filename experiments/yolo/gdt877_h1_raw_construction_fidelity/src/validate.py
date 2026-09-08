#!/usr/bin/env python3
"""Independent raw-construction replay. Never imports the producer."""
import argparse
import csv
import hashlib
import io
import json
import re
import subprocess
import tempfile
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
ROOT = BASE.parents[2]


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def read(path):
    return json.loads(path.read_text())


def classify(groups, clean, pattern):
    groups = sorted(groups, key=lambda r: int(r['source_group_index']))
    if groups:
        count = int(groups[0]['source_group_count'])
        require([int(g['source_group_index']) for g in groups] == list(range(1, count + 1)), 'complete raw locus')
        require(all(int(g['source_group_count']) == count for g in groups), 'raw count consistency')
    flat, mapping = [], []
    for g in groups:
        fragments = g['clean_ascii_fragments'].split()
        require(len(fragments) == int(g['clean_ascii_fragment_count']), 'fragment count')
        positions = [int(x) for x in g['legacy_surface_positions_1based'].split(',')] if g['legacy_surface_positions_1based'] else []
        require(positions == list(range(len(flat)+1, len(flat)+1+len(fragments))), 'fragment source offsets')
        flat.extend(fragments)
        mapping.extend([g] * len(fragments))
    require(flat == clean.split(), 'full clean-line cross parity')
    starts = [i+1 for i in range(len(flat)-len(pattern)+1) if flat[i:i+len(pattern)] == pattern]
    out = dict(clean_match_starts=starts, status='MISSING_READING' if not groups else 'ABSENT_PATTERN', consecutive_raw_groups=False, literal_single_raw_groups=False, clear_internal_gaps=False, eligible=False, raw_groups=[], internal_separators=[], group_indices=[])
    if len(starts) > 1:
        out['status'] = 'AMBIGUOUS_PATTERN'
    elif len(starts) == 1:
        selected = mapping[starts[0]-1:starts[0]+2]
        indices = [int(g['source_group_index']) for g in selected]
        consecutive = indices == list(range(indices[0], indices[0]+3))
        literal = all(g['ivtff_group_raw'] == word and re.fullmatch('[a-z]+', word) is not None and g['clean_ascii_fragments'].split() == [word] and int(g['clean_ascii_fragment_count']) == 1 for g, word in zip(selected, pattern))
        gaps = [g['right_separator'] for g in selected[:2]] if consecutive else []
        require(all(g in {'DEFINITE_SPACE', 'UNCERTAIN_SMALL_SPACE', 'DRAWING_INTERRUPTION', 'DRAWING_INTERRUPTION_UNALIGNED'} for g in gaps), 'known internal separator')
        clear = consecutive and gaps == ['DEFINITE_SPACE', 'DEFINITE_SPACE']
        eligible = bool(consecutive and literal and clear)
        out.update(status='EXACT_CLEAR' if eligible else 'QUALIFIED', consecutive_raw_groups=consecutive, literal_single_raw_groups=literal, clear_internal_gaps=clear, eligible=eligible, raw_groups=selected, internal_separators=gaps, group_indices=indices)
    return out


def fixtures():
    def rows(items):
        result, offset = [], 1
        for index, (raw, fragments, gap) in enumerate(items, 1):
            n = len(fragments.split())
            result.append(dict(source_group_index=str(index), source_group_count=str(len(items)), ivtff_group_raw=raw, clean_ascii_fragments=fragments, clean_ascii_fragment_count=str(n), legacy_surface_positions_1based=','.join(str(i) for i in range(offset, offset+n)), right_separator=gap))
            offset += n
        return result
    pat = ['aaa', 'bbb', 'ccc']
    good = [('aaa','aaa','DEFINITE_SPACE'), ('bbb','bbb','DEFINITE_SPACE'), ('ccc','ccc','LINE_END')]
    checks = []
    for name, data, clean, status in [
        ('clear',good,'aaa bbb ccc','EXACT_CLEAR'),
        ('entity', [('@152;aaa','aaa','DEFINITE_SPACE')]+good[1:],'aaa bbb ccc','QUALIFIED'),
        ('annotation', [('aaa!','aaa','DEFINITE_SPACE')]+good[1:],'aaa bbb ccc','QUALIFIED'),
        ('fragmentation', [('aaa.bbb','aaa bbb','DEFINITE_SPACE'),good[2]],'aaa bbb ccc','QUALIFIED'),
        ('empty_raw_interruption', [good[0], ('@152;', '', 'DEFINITE_SPACE')]+good[1:], 'aaa bbb ccc', 'QUALIFIED'),
        ('outer_gap_irrelevant', good[:2]+[('ccc','ccc','DRAWING_INTERRUPTION')], 'aaa bbb ccc', 'EXACT_CLEAR'),
        ('uncertain', [('aaa','aaa','UNCERTAIN_SMALL_SPACE')]+good[1:],'aaa bbb ccc','QUALIFIED'),
        ('drawing', [('aaa','aaa','DRAWING_INTERRUPTION')]+good[1:],'aaa bbb ccc','QUALIFIED'),
        ('multiple',good+good,'aaa bbb ccc aaa bbb ccc','AMBIGUOUS_PATTERN'),
        ('absent',good,'aaa bbb ccc','ABSENT_PATTERN'),
        ('missing',[],'','MISSING_READING')]:
        result = classify(rows(data), clean, ['zzz','bbb','ccc'] if name == 'absent' else pat)
        require(result['status'] == status, 'fixture '+name)
        require(result['eligible'] == (status == 'EXACT_CLEAR'), 'fixture eligibility '+name)
        checks.append(name)
    try:
        classify(rows(good), 'aaa bbb xxx', pat)
    except AssertionError:
        checks.append('cross_parity_rejected')
    else:
        raise AssertionError('cross corruption accepted')
    return checks


def fresh_projection(spec, name, targets):
    source = spec['sources'][name]
    command = [str(ROOT/'vmanus-exp'), 'query-tsv', source['path'], '--selector', source['selector'], *[item for page in spec['selectors'] for item in ('--allow', page)], '--columns', ','.join(source['columns']), '--forbid-prefix', 'f84', '--forbid-prefix', 'f84r']
    done = subprocess.run(command, cwd=ROOT, capture_output=True, check=True)
    rows = list(csv.DictReader(io.StringIO(done.stdout.decode()), delimiter='\t'))
    notices = [json.loads(line[len('GUARD_STATS '):]) for line in done.stderr.decode().splitlines() if line.startswith('GUARD_STATS ')]
    require(len(notices) == 1, 'one guard statistics receipt')
    stats = notices[0]
    require(stats['selected'] == len(rows) and len(rows) > 0, 'positive guard selected row count')
    require(all(r['page'] in spec['selectors'] and not r['page'].startswith('f84') for r in rows), 'explicit permitted pages')
    keys = {(t['page'], t['locus']) for t in targets}
    retained = [r for r in rows if (r['page'],r['locus']) in keys]
    return retained, dict(guard_stats=stats, selectors=spec['selectors'], projection_sha256=hashlib.sha256(done.stdout).hexdigest(), retained_rows=len(retained))


def cli_fixture():
    runtime = BASE/'runtime'
    runtime.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='validator_cli_', dir=runtime) as temp:
        path = Path(temp)/'fixture.tsv'
        path.write_text('page\tlocus\nfa\tfa.1\nfb\tfb.1\nf84r\tf84r.1\nfc\tfc.1\n')
        spec = {'selectors':['fa','fb'], 'sources':{'TEST':{'path':str(path.relative_to(ROOT)), 'selector':'page', 'columns':['page','locus']}}}
        retained, receipt = fresh_projection(spec, 'TEST', [{'page':'fa','locus':'fa.1'},{'page':'fb','locus':'fb.1'}])
        require({r['page'] for r in retained} == {'fa','fb'}, 'real CLI repeated allow values')
        require(receipt['guard_stats'] == {'selected':2,'skipped_forbidden':1,'skipped_not_allowed':1}, 'real CLI filtering stats')
    return 'actual_cli_repeated_allow'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--synthetic-only', action='store_true')
    args = parser.parse_args()
    tests = fixtures()
    tests.append(cli_fixture())
    if args.synthetic_only:
        print(json.dumps(dict(status='PASS', synthetic_checks=tests)))
        return
    spec, targets = read(BASE/'src/SPEC.json'), read(BASE/'src/TARGETS.json')
    require(not any(p.startswith('f84') for p in spec['selectors']), 'sealed selectors')
    artifacts = BASE/'artifacts'
    atlas, cross = read(artifacts/'SOURCE_ATLAS.json'), read(artifacts/'SOURCE_CROSS.json')
    receipts = {}
    for name, retained in [('ATLAS', atlas), ('CROSS', cross)]:
        fresh, receipts[name] = fresh_projection(spec, name, targets)
        canonical = lambda rs: sorted(json.dumps(r, sort_keys=True) for r in rs)
        require(canonical(retained) == canonical(fresh), 'fresh guarded subset parity '+name)
    cross_map = {(r['page'],r['locus']):r for r in cross}
    require(len(cross_map) == len(cross) == len(targets), 'five unique cross records')
    report = read(artifacts/'RESULT.json')
    actual = report['readings']
    keyed = {(r['h1_field_id'],r['edition']):r for r in actual}
    require(len(keyed) == len(actual) == 15, 'fifteen unique readings')
    eligible, all_three = 0, []
    eligible_by_edition = {edition: 0 for edition in spec['editions']}
    for target in targets:
        flags = []
        for edition in spec['editions']:
            groups = [r for r in atlas if r['page']==target['page'] and r['locus']==target['locus'] and r['edition']==edition]
            expected = classify(groups, cross_map[(target['page'],target['locus'])][spec['clean_columns'][edition]], target['written_pattern_eva'].split())
            got = keyed[(target['h1_field_id'],edition)]
            for field, value in expected.items():
                require(got.get(field) == value, f'{target["h1_field_id"]}/{edition}/{field}')
            flags.append(expected['eligible'])
            eligible += expected['eligible']
            eligible_by_edition[edition] += expected['eligible']
        if all(flags):
            all_three.append(target['h1_field_id'])
    require(report['all_three_eligible'] == len(all_three), 'aggregate all-three count')
    require(report['reading_results'] == len(keyed) == 15, 'aggregate reading count')
    require(report['constructions'] == len(targets) == 5, 'aggregate construction count')
    require(report['eligible_by_edition'] == eligible_by_edition, 'aggregate per-edition eligibility')
    result = dict(status='PASS', readings_checked=15, eligible_readings=eligible, all_three_eligible_fields=all_three, synthetic_checks=tests, guarded_fresh_source_checks=receipts, scope='Independent source, mapping and endpoint replay only; no semantic or native-vision validation.')
    (artifacts/'VALIDATION.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))

if __name__ == '__main__':
    main()
