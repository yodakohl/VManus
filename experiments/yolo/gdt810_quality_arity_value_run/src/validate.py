#!/usr/bin/env python3
"""Independent guarded-source audit; does not import the experiment builder."""
from __future__ import annotations
import argparse
from collections import Counter
import csv
import hashlib
import io
import json
from pathlib import Path
import re
import subprocess
import sys

sys.dont_write_bytecode = True
ROOT = next(p for p in Path(__file__).resolve().parents if (p / 'AGENTS.md').is_file())
BASE = Path(__file__).resolve().parent.parent
ART = BASE / 'artifacts'
ALLOW = 'experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv'
MATRIX = 'experiments/yolo/gdt628_chol_measure_frame/artifacts/OL_OR_QUALITY_CARRIER_MATRIX.tsv'
RAW = 'transcription/voynich_zl3b_lines.tsv'
CROSS = 'transcription/voynich_cross_transcription_lines.tsv'
SEALS = {'f84': 'FORBIDDEN', 'f84r': 'FORBIDDEN'}
ARITY = {'NONE': 0, 'k': 1, 't': 1, 'ch': 1, 'sh': 1,
         'kch': 2, 'ksh': 2, 'tch': 2, 'tsh': 2}
POPULATIONS = ('ALL', 'EXCLUDE_DISCOVERY_LOCUS', 'EXCLUDE_DISCOVERY_PAGE')


def read(path):
    with path.open(encoding='utf-8', newline='') as handle:
        return list(csv.DictReader(handle, delimiter='\t'))


def digest(path):
    with path.open('rb') as handle:
        return hashlib.file_digest(handle, 'sha256').hexdigest()


def query(source, pages, columns):
    command = [str(ROOT / 'vmanus-exp'), 'query-tsv', source, '--selector', 'page']
    for page in pages:
        command += ['--allow', page]
    command += ['--columns', columns, '--forbid-prefix', 'f84', '--forbid-prefix', 'f84r']
    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    if result.returncode:
        raise AssertionError('guarded query failed: ' + source)
    return list(csv.DictReader(io.StringIO(result.stdout), delimiter='\t'))


def next_values(words, index, values):
    stop = index + 1
    while stop < len(words) and words[stop] in values:
        stop += 1
    return words[index + 1:stop], words[stop] if stop < len(words) else 'LINE_END'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--no-write', action='store_true')
    parser.add_argument('--output-dir', type=Path, default=ART)
    args = parser.parse_args()
    artifacts = args.output_dir.resolve()
    checks, errors = [], []

    def require(name, condition):
        if not condition:
            raise AssertionError(name)
        checks.append(name)

    try:
        manifest = json.loads((BASE / 'experiment.json').read_text())
        require('manifest identity and seals', manifest['experiment_id'] == 'GDT810'
                and manifest['sealed_data'] == SEALS)
        bound = manifest['inputs'] + manifest['outputs']
        paths = [r['path'] for r in bound]
        require('unique portable manifest paths', len(paths) == len(set(paths)) and all(
            not Path(p).is_absolute() and '..' not in Path(p).parts for p in paths))
        require('manifest file hashes', all((ROOT / r['path']).is_file()
                and digest(ROOT / r['path']) == r['sha256'] for r in bound))
        required = {ALLOW, MATRIX, RAW, CROSS, str((BASE / 'src/SPEC.json').relative_to(ROOT))}
        require('all consumed sources bound', required <= {r['path'] for r in manifest['inputs']})
        require('implementation bound', all(str((BASE / 'src' / n).relative_to(ROOT)) in paths
                for n in ('run.py', 'validate.py')))
        spec = json.loads((BASE / 'src/SPEC.json').read_text())
        heads = spec['heads']
        projected = [{k: r[k] for k in ('surface', 'ending', 'quality_core', 'wrapper')}
                     | {'arity': ARITY[r['quality_core']]} for r in read(ROOT / MATRIX)]
        require('54 exact matrix heads including empty cells', len(heads) == 54
                and sorted(heads, key=lambda r: r['surface']) == sorted(projected, key=lambda r: r['surface']))
        head_map = {r['surface']: r for r in heads}
        require('unique complete heads', len(head_map) == 54)
        require('declared value forms and discovery', spec['value_forms'] == ['dan', 'dain', 'daiin', 'daiiin']
                and spec['discovery_locus'] == 'f32v.8' and spec['discovery_page'] == 'f32v')
        values = set(spec['value_forms'])
        pages = [r['page'] for r in read(ROOT / ALLOW)]
        require('179 inherited selectors exclude seals', len(pages) == len(set(pages)) == 179
                and not any(p.startswith('f84') for p in pages))
        raw = query(RAW, pages, 'page,locus,eva_clean')
        cross_rows = query(CROSS, pages, 'page,locus,zl3b_clean,it2a_clean,rf1b_clean')
        cross = {r['locus']: r for r in cross_rows}
        require('raw and alternate locus uniqueness', len({r['locus'] for r in raw}) == len(raw)
                and len(cross) == len(cross_rows))
        require('source and alternate coverage parity', set(cross) == {r['locus'] for r in raw}
                and all(cross[r['locus']]['page'] == r['page']
                        and cross[r['locus']]['zl3b_clean'] == r['eva_clean'] for r in raw))
        expected = {}
        for line in raw:
            words = line['eva_clean'].split()
            ranks = Counter()
            for index, head in enumerate(words):
                ranks[head] += 1
                if head not in head_map:
                    continue
                run, stop = next_values(words, index, values)
                support = 1
                for reader in ('it2a_clean', 'rf1b_clean'):
                    alternate = cross[line['locus']][reader].split()
                    hits = [i for i, w in enumerate(alternate) if w == head]
                    if len(hits) == words.count(head):
                        support += int(next_values(alternate, hits[ranks[head] - 1], values) == (run, stop))
                expected[line['locus'], str(index + 1)] = {
                    'page': line['page'], 'locus': line['locus'], 'token_index': str(index + 1),
                    'head': head, **{k: str(head_map[head][k]) for k in ('arity', 'ending', 'quality_core', 'wrapper')},
                    'value_run_length': str(len(run)), 'value_run': ' '.join(run),
                    'value_equal': str(int(len(run) >= 2 and len(set(run)) == 1)),
                    'right_stop': stop, 'right_censored': str(int(stop == 'LINE_END')),
                    'reader_support': str(support), 'source_line': line['eva_clean']}
        events = read(artifacts / 'HEAD_VALUE_RUNS.tsv')
        observed = {(r['locus'], r['token_index']): r for r in events}
        require('one event for every exact head occurrence', len(observed) == len(events) == len(expected)
                and set(observed) == set(expected))
        require('event ids unique', len({r['event_id'] for r in events}) == len(events))
        require('all maximal runs stops and alternate-reader counts independently reconstructed',
                all(all(observed[key][k] == v for k, v in row.items()) for key, row in expected.items()))
        wanted_summary = {}
        for population in POPULATIONS:
            eligible = [r for r in expected.values() if r['reader_support'] == '3'
                        and r['right_censored'] == '0' and int(r['value_run_length']) >= 1
                        and (population != 'EXCLUDE_DISCOVERY_LOCUS' or r['locus'] != spec['discovery_locus'])
                        and (population != 'EXCLUDE_DISCOVERY_PAGE' or r['page'] != spec['discovery_locus'].split('.')[0])]
            for ending in ('OL', 'OR'):
                for arity in ('0', '1', '2'):
                    group = [r for r in eligible if r['ending'] == ending and r['arity'] == arity]
                    multi = [r for r in group if int(r['value_run_length']) >= 2]
                    wanted_summary[population, ending, arity] = {
                        'eligible': str(len(group)), 'value_single': str(len(group) - len(multi)),
                        'value_multiple': str(len(multi)), 'multiple_pages': str(len({r['page'] for r in multi})),
                        'identical_multiple': str(sum(r['value_equal'] == '1' for r in multi)),
                        'mixed_multiple': str(sum(r['value_equal'] == '0' for r in multi))}
        summary_rows = read(artifacts / 'SUMMARY.tsv')
        summary = {(r['population'], r['ending'], r['arity']): r for r in summary_rows}
        require('all 18 summary strata including empty cells', len(summary) == len(summary_rows) == 18
                and set(summary) == set(wanted_summary))
        require('primary summary reconstruction and both discovery exclusions', all(
            all(summary[key][k] == v for k, v in row.items()) for key, row in wanted_summary.items()))
        result = json.loads((artifacts / 'RESULT.json').read_text())
        require('result identity census and discovery', result['experiment_id'] == 'GDT810'
                and result['selectors'] == len(pages) and result['source_lines'] == len(raw)
                and result['head_types'] == len(head_map) and result['head_occurrences'] == len(expected)
                and result['discovery_locus'] == spec['discovery_locus'])
        result_summaries = [{k: str(v) for k, v in row.items()} for row in result['summaries']]
        require('result and summary-table parity', result_summaries == summary_rows)
        q1 = wanted_summary['EXCLUDE_DISCOVERY_PAGE', 'OL', '1']
        q2 = wanted_summary['EXCLUDE_DISCOVERY_PAGE', 'OL', '2']
        n1, n2, m1, m2 = (int(q1['eligible']), int(q2['eligible']),
                          int(q1['value_multiple']), int(q2['value_multiple']))
        if not m2:
            status = 'NO_EXTERNAL_PAIRED_QUALITY_MULTIPLE_VALUE_SUPPORT'
        elif int(q2['multiple_pages']) < 2 or not n1 or m2 * n1 <= m1 * n2:
            status = 'EXTERNAL_EXAMPLES_WITHOUT_CLEAR_ARITY_PREFERENCE'
        else:
            status = 'PROVISIONAL_PAIRED_QUALITY_MULTIPLE_VALUE_LEAD'
        require('decision reconstructed without floating-point rate rounding', result['status'] == status)
        require('zero semantic and component credit', result['confirmed_lexemes'] == result['component_exports'] == 0
                and result['semantic_identity_selected'] is False)
        require('no new pages and explicit seals', result['new_pages'] == 0 and result['sealed_data'] == SEALS)
        hashes = result['artifact_sha256']
        require('result hashes cover every builder artifact', {'HEAD_VALUE_RUNS.tsv', 'SUMMARY.tsv',
                'GUARDED_QUERY_STATS.json', 'GDT388_RELATION_PACKET.tsv', 'GDT388_EDGE_INTAKE.json'} == set(hashes))
        require('result artifact hashes portable and exact', all(Path(name).name == name
                and digest(artifacts / name) == value for name, value in hashes.items()))
        edge = json.loads((artifacts / 'GDT388_EDGE_INTAKE.json').read_text())
        packet = read(artifacts / 'GDT388_RELATION_PACKET.tsv')
        candidates = {r['event_id']: r for r in events if r['reader_support'] == '3'
                      and r['ending'] == 'OL' and r['arity'] == '2' and int(r['value_run_length']) >= 2}
        require('packet membership exactly all supported OL paired-head multiple runs',
                len(packet) == len(candidates) and {r['edge_id'] for r in packet} == set(candidates))
        for row in packet:
            event = candidates[row['edge_id']]
            expected_packet = {'batch_id': 'GDT810_TEXT_ARITY', 'page': event['page'],
                'physical_folio': re.match(r'f\d+', event['page'])[0], 'diagram_unit_id': event['event_id'],
                'pivot_visual_id': 'TEXT_HEAD', 'pivot_locus': event['locus'] + '@' + event['token_index'],
                'target_visual_id': 'TEXT_VALUE',
                'target_locus': event['locus'] + '@' + str(int(event['token_index']) + int(event['value_run_length'])),
                'relation_type': 'FORMAL_HEAD_THEN_MULTIPLE_VALUES', 'direction_basis': 'WRITTEN_ADJACENCY',
                'ownership_basis': 'TEXT_ONLY_NO_VISUAL_OWNER', 'geometry_only_selection': 'FALSE',
                'source_manifest_id': 'GDT810', 'page_crop_sha256': 'NONE', 'pivot_crop_sha256': 'NONE',
                'target_crop_sha256': 'NONE', 'source_aware_localizer': 'cached_reader',
                'relation_reviewer': 'source_sequence_audit', 'relation_confidence': 'LOW',
                'ambiguity_state': 'TEXT_RELATION_ONLY', 'formal_access_state': 'UNSEALED_ALREADY_INSPECTED',
                'fold_assignment': 'EXPLORATORY', 'eligibility_status': 'INELIGIBLE_TEXT_ONLY'}
            require('packet exact text provenance ' + row['edge_id'], all(row[k] == v for k, v in expected_packet.items()))
        intake = subprocess.run([str(ROOT / 'vmanus-exp'), 'check-edge-packet',
                str((artifacts / 'GDT388_RELATION_PACKET.tsv').relative_to(ROOT))],
                cwd=ROOT, capture_output=True, text=True)
        require('executable GDT388 intake replay', json.loads(intake.stdout) == edge
                and intake.returncode == int(bool(packet)))
        require('only expected unsealed formal errors', edge['packet_rows'] == len(packet)
                and edge['eligible_edges'] == 0 and edge['errors'] == [
                    f'edge row {i}: formal access is not sealed' for i in range(2, len(packet) + 2)])
        require('formal packet not semantic score ready', edge.get('score_ready') is False
                and result['edge_score_ready'] is False)
    except (AssertionError, KeyError, ValueError, OSError, IndexError, TypeError) as exc:
        errors.append(str(exc).replace(str(ROOT), '<repo>'))
    output = {'experiment_id': 'GDT810', 'status': 'PASS' if not errors else 'FAIL',
              'checks_passed': len(checks), 'checks': checks, 'errors': errors,
              'builder_imported': False, 'confirmed_lexemes': 0, 'component_exports': 0}
    if not args.no_write:
        (artifacts / 'VALIDATION.json').write_text(json.dumps(output, indent=2, ensure_ascii=False) + '\n')
    print(json.dumps(output, indent=2, ensure_ascii=False))
    return int(bool(errors))


if __name__ == '__main__':
    raise SystemExit(main())
