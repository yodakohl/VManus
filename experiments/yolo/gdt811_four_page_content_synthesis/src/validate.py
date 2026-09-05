#!/usr/bin/env python3
"""Independent conservation/count checks; no builder import or meaning test."""
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

ROOT = next(p for p in Path(__file__).resolve().parents
            if (p / 'AGENTS.md').is_file() and (p / '.git').exists())
BASE = Path(__file__).resolve().parent.parent
ART = BASE / 'artifacts'
G791 = 'experiments/yolo/gdt791_thirty_page_visual_owner_spine/'
ATLAS = G791 + 'artifacts/GDT791_1007_LINE_OWNER_ATLAS.tsv'
SELECTORS = G791 + 'src/PAGE_SELECTOR_SPECS.tsv'
ALLOW = 'experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv'
CROSS = 'transcription/voynich_cross_transcription_lines.tsv'
RAW = 'transcription/voynich_zl3b_lines.tsv'
LINE_FIELDS = ('physical_page,source_selector,locus,line_number,line_kind,'
               'paragraph_start,paragraph_end,panel_ids,record_ids,eva_clean').split(',')
ALTERNATES = ['page', 'locus', 'zl3b_clean', 'it2a_clean', 'rf1b_clean']
CHECKS = []


def require(name, condition):
    CHECKS.append({'check': name, 'passed': bool(condition)})
    if not condition:
        raise AssertionError(name)


def read_tsv(path):
    with path.open(encoding='utf-8', newline='') as handle:
        return list(csv.DictReader(handle, delimiter='\t'))


def read_json(name):
    return json.loads((ART / name).read_text(encoding='utf-8'))


def stringify(rows):
    return [{k: str(v) for k, v in row.items()} for row in rows]


def positions(text, pattern):
    words, wanted = tuple(text.split()), tuple(pattern)
    return [i + 1 for i in range(len(words)) if words[i:i + len(wanted)] == wanted]


def selector_key(value):
    m = re.fullmatch(r'f(\d+)([rv])(\d*)', value)
    if m is None:
        raise ValueError('invalid admitted selector')
    return int(m[1]), m[2], int(m[3] or 0)


def query(source, selector, allowed, columns):
    if not allowed or any(v.startswith('f84') for v in allowed):
        raise ValueError('empty or forbidden query scope')
    command = [str(ROOT / 'vmanus-exp'), 'query-tsv', source, '--selector', selector]
    for value in allowed:
        command.extend(['--allow', value])
    command.extend(['--columns', ','.join(columns), '--forbid-prefix', 'f84',
                    '--forbid-prefix', 'f84r'])
    proc = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=True)
    rows = list(csv.DictReader(io.StringIO(proc.stdout), delimiter='\t'))
    stats = [json.loads(line.removeprefix('GUARD_STATS '))
             for line in proc.stderr.splitlines() if line.startswith('GUARD_STATS ')]
    if (len(stats) != 1 or stats[0]['selected'] != len(rows)
            or any(row[selector] not in allowed or list(row) != columns for row in rows)):
        raise ValueError('guarded selection contract failed')
    return rows, stats[0]


def digest(path):
    with path.open('rb') as handle:
        return hashlib.file_digest(handle, 'sha256').hexdigest()


def check_hashes(result, input_key, output_key):
    return (all(digest(ROOT / name) == value for name, value in result[input_key].items())
            and all(digest(ART / name) == value for name, value in result[output_key].items()))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--no-write', action='store_true')
    args = parser.parse_args()
    spec = json.loads((BASE / 'src/SPEC.json').read_text())
    mapping = read_tsv(ROOT / SELECTORS)  # Scope metadata, not manuscript rows.
    released = {r['source_selector']: r['physical_page'] for r in mapping}
    inherited = {r['page'] for r in read_tsv(ROOT / ALLOW)}
    allowed = sorted(inherited | set(released), key=selector_key)
    require('declared existing page and sealed scope',
            len(inherited) == 179 and len(released) == 35 and len(set(released.values())) == 30
            and spec['physical_pages'] == ['f17r', 'f77r', 'f88r', 'f72r']
            and set(spec['source_selectors']) == {s for s, p in released.items() if p in spec['physical_pages']}
            and not any(p.startswith('f84') for p in allowed)
            and spec['sealed_data'] == {'f84': 'FORBIDDEN', 'f84r': 'FORBIDDEN'})
    atlas, _ = query(ATLAS, 'source_selector', list(released), LINE_FIELDS)
    raw, _ = query(RAW, 'page', allowed,
                   ['page', 'locus', 'line_number', 'section', 'kind', 'eva_clean'])
    alternatives, _ = query(CROSS, 'page', allowed, ALTERNATES)
    cross = {(r['page'], r['locus']): r for r in alternatives}
    raw_by_key = {(r['page'], r['locus']): r for r in raw}
    atlas_by_key = {(r['source_selector'], r['locus']): r for r in atlas}
    require('unique source identities and released-source agreement',
            len(cross) == len(alternatives) and len(raw_by_key) == len(raw)
            and len(atlas_by_key) == len(atlas)
            and all(r['eva_clean'] == cross[k]['zl3b_clean'] == raw_by_key[k]['eva_clean']
                    and r['physical_page'] == released[k[0]] for k, r in atlas_by_key.items()))
    rows = [{**r, **{col: cross[r['source_selector'], r['locus']][col]
                     for col in ['it2a_clean', 'rf1b_clean']}}
            for r in atlas if r['physical_page'] in spec['physical_pages']]
    require('all four-page source and alternate strings conserved',
            len(rows) == spec['expected_source_lines']
            and read_tsv(ART / 'FOUR_PAGE_LINES.tsv') == rows)
    fresh_queries = []
    for source, selector, values, columns in [
            (ATLAS, 'physical_page', spec['physical_pages'], LINE_FIELDS),
            (CROSS, 'page', spec['source_selectors'], ALTERNATES)]:
        _, stats = query(source, selector, values, columns)
        fresh_queries.append(dict(source=source, selector=selector, allowed=values,
                                  columns=columns, stats=stats))
    require('four-page guarded provenance rechecked', read_json('GUARDED_QUERY_STATS.json') == fresh_queries)

    expected_edges = []
    for label in rows:
        if label['line_kind'] != 'LOCAL_LABEL_OR_MARKER' or not label['eva_clean'].split():
            continue
        words = label['eva_clean'].split()
        for prose in rows:
            if prose['physical_page'] != label['physical_page'] or prose['line_kind'] != 'RUNNING_PROSE':
                continue
            starts = positions(prose['eva_clean'], words)
            support = 1 + sum(label[col].split() == words
                              and len(positions(prose[col], words)) == len(starts)
                              for col in ['it2a_clean', 'rf1b_clean'])
            for rank, start in enumerate(starts, 1):
                expected_edges.append(dict(edge_id=f'LR{len(expected_edges) + 1:03d}',
                    physical_page=label['physical_page'], label_locus=label['locus'],
                    complete_label=label['eva_clean'], prose_locus=prose['locus'],
                    start_token=start, end_token=start + len(words) - 1,
                    occurrence_rank=rank, reader_support=support, source_line=prose['eva_clean']))
    require('exhaustive complete-label reuse and same-multiplicity reader support',
            read_tsv(ART / 'EXACT_LABEL_PROSE_MATCHES.tsv') == stringify(expected_edges))
    summaries = []
    for page in spec['physical_pages']:
        selected = [r for r in rows if r['physical_page'] == page]
        prose = [r for r in selected if r['line_kind'] == 'RUNNING_PROSE']
        local = [r for r in selected if r['line_kind'] == 'LOCAL_LABEL_OR_MARKER']
        edges = [e for e in expected_edges if e['physical_page'] == page]
        summaries.append(dict(physical_page=page, source_lines=len(selected), prose_lines=len(prose),
            local_lines=len(local), total_tokens=sum(len(r['eva_clean'].split()) for r in selected),
            prose_tokens=sum(len(r['eva_clean'].split()) for r in prose),
            local_tokens=sum(len(r['eva_clean'].split()) for r in local),
            exact_reused_complete_labels=len({e['complete_label'] for e in edges}),
            reused_label_loci=len({e['label_locus'] for e in edges}), identity_edges=len(edges),
            all_reader_identity_edges=sum(e['reader_support'] == 3 for e in edges)))
    require('page summaries from source rows and exact identities',
            read_tsv(ART / 'PAGE_SUMMARY.tsv') == stringify(summaries))
    reader = (ART / 'FOUR_PAGES_FULL_TEXT.md').read_text()
    blocks = re.findall(r'^### (\S+) — [^\n]*\n\n([^\n]*)\n', reader, re.M)
    require('complete human-readable source text',
            dict(blocks) == {r['locus']: r['eva_clean'] or '[empty transcription]' for r in rows}
            and len(blocks) == len(rows))
    f77doc = (BASE / 'src/F77_HISTORICAL_READING.md').read_text()
    quotes = re.findall(r'^(f77r\.\d+) (.+)$', f77doc, re.M)
    require('historical note preserves all fifty f77r loci',
            len(quotes) == 50 and dict(quotes)
            == {r['locus']: r['eva_clean'] for r in rows if r['physical_page'] == 'f77r'})
    result = read_json('RESULT.json')
    require('main summary and no semantic/dictionary/new-page export',
            result['source_lines'] == len(rows) and result['summaries'] == summaries
            and result['physical_pages'] == spec['physical_pages']
            and result['exact_identity_edges'] == len(expected_edges)
            and result['sealed_data'] == spec['sealed_data']
            and all(result[k] == 0 for k in ['new_pages', 'confirmed_lexemes', 'component_exports'])
            and all(result[k] is False for k in ['translated_manuscript', 'dictionary_changed', 'edge_score_ready']))
    validate_reference(spec, released, inherited, raw, alternatives, cross, atlas_by_key)
    validate_scope(released, atlas, cross)
    require('main embeds the exact independently checked inventory results',
            result['reference_inventory'] == read_json('REFERENCE_RESULT.json')
            and result['scope_inventory'] == read_json('SCOPE_RESULT.json'))
    validate_packet(expected_edges)
    validation = dict(experiment_id='GDT811', status='PASS', checks=CHECKS,
        check_count=len(CHECKS), failed_checks=0, independent_builder_imports=False,
        meanings_validated=False, confirmed_lexemes=0, component_exports=0,
        source_lines=len(rows), exact_identity_edges=len(expected_edges), sealed_data=spec['sealed_data'])
    if not args.no_write:
        (ART / 'VALIDATION.json').write_text(json.dumps(validation, indent=2, sort_keys=True) + '\n')
    print(json.dumps({k: v for k, v in validation.items() if k != 'checks'}, sort_keys=True))
    return 0


def validate_reference(spec, released, inherited, raw, alternatives, cross, atlas):
    surfaces = spec['reference_wholes']
    require('seven complete reference wholes fixed',
            surfaces == ['okol', 'chokol', 'qokol', 'okoldy', 'qoekol', 'ofaldo', 'ofal'])
    expected = []
    for r in sorted(raw, key=lambda r: (selector_key(r['page']), int(r['line_number']))):
        ranks = Counter()
        key = r['page'], r['locus']
        known = atlas.get(key)
        for ordinal, word in enumerate(r['eva_clean'].split(), 1):
            if word not in surfaces:
                continue
            ranks[word] += 1
            rank, other = ranks[word], cross[key]
            if other['zl3b_clean'] != r['eva_clean']:
                raise AssertionError('reference source mismatch')
            it, rf = positions(other['it2a_clean'], [word]), positions(other['rf1b_clean'], [word])
            expected.append(dict(page=r['page'], locus=r['locus'], section=r['section'],
                source_line=r['eva_clean'], surface=word, ordinal=ordinal,
                within_line_occurrence_rank=rank, line_number=r['line_number'],
                physical_page=known['physical_page'] if known else re.fullmatch(r'(f\d+[rv])\d*', r['page'])[1],
                physical_page_basis='GDT791_EXPLICIT_MAPPING' if known else 'NORMALIZED_SIDE_HEURISTIC',
                released_physical_page=known['physical_page'] if known else 'NOT_IN_GDT791',
                released_gdt791_status=known['line_kind'] if known else 'NOT_IN_GDT791',
                raw_kind=r['kind'], raw_role={'P': 'PROSE', 'L': 'LOCAL_LABEL'}.get(r['kind'], 'OTHER'),
                zl3b_occurrences_in_line=len(positions(r['eva_clean'], [word])), it2a_occurrences_in_line=len(it),
                rf1b_occurrences_in_line=len(rf), it2a_rank_ordinal=it[rank - 1] if len(it) >= rank else 'ABSENT',
                rf1b_rank_ordinal=rf[rank - 1] if len(rf) >= rank else 'ABSENT',
                it2a_rank_supported=int(len(it) >= rank), rf1b_rank_supported=int(len(rf) >= rank),
                reader_support_count=1 + int(len(it) >= rank) + int(len(rf) >= rank),
                reader_support_definition='NTH_EXACT_WHOLE_IN_SAME_LINE__NOT_ALIGNMENT_PROOF',
                semantic_credit=0, component_export_credit=0))
    require('exhaustive exact reference inventory and occurrence-rank alternate support',
            read_tsv(ART / 'REFERENCE_INVENTORY.tsv') == stringify(expected))

    def counts(group):
        return dict(occurrences=len(group), distinct_loci=len({r['locus'] for r in group}),
            source_selectors=len({r['page'] for r in group}), physical_pages=len({r['physical_page'] for r in group}),
            three_reading_rank_supported=sum(r['reader_support_count'] == 3 for r in group),
            outside_f88r_occurrences=sum(r['physical_page'] != 'f88r' for r in group))

    summary, distributions = [], []
    for word in surfaces:
        group = [r for r in expected if r['surface'] == word]
        row = dict(surface=word, **counts(group),
            f88r_occurrences=sum(r['physical_page'] == 'f88r' for r in group),
            outside_f88r_physical_pages=len({r['physical_page'] for r in group if r['physical_page'] != 'f88r'}),
            raw_prose_occurrences=sum(r['raw_role'] == 'PROSE' for r in group),
            raw_label_occurrences=sum(r['raw_role'] == 'LOCAL_LABEL' for r in group),
            raw_other_occurrences=sum(r['raw_role'] == 'OTHER' for r in group),
            released_running_occurrences=sum(r['released_gdt791_status'] == 'RUNNING_PROSE' for r in group),
            released_local_occurrences=sum(r['released_gdt791_status'] == 'LOCAL_LABEL_OR_MARKER' for r in group),
            outside_gdt791_occurrences=sum(r['released_gdt791_status'] == 'NOT_IN_GDT791' for r in group),
            semantic_credit=0, component_export_credit=0)
        for field, out in [('section', 'section'), ('physical_page', 'physical_page'),
                           ('raw_role', 'raw_role'), ('released_gdt791_status', 'released_status')]:
            frequencies = Counter(r[field] for r in group)
            row['counts_by_' + out + '_json'] = json.dumps(dict(frequencies), sort_keys=True, separators=(',', ':'))
            for category in sorted(frequencies):
                selected = [r for r in group if r[field] == category]
                distributions.append(dict(surface=word, dimension=field, category=category,
                    **counts(selected), semantic_credit=0, component_export_credit=0))
        summary.append(row)
    require('reference whole and section/role/page counts',
            read_tsv(ART / 'REFERENCE_WHOLE_SUMMARY.tsv') == stringify(summary)
            and read_tsv(ART / 'REFERENCE_DISTRIBUTION_COUNTS.tsv') == stringify(distributions))
    result = read_json('REFERENCE_RESULT.json')
    wanted = dict(inherited_selector_count=len(inherited), released_source_selector_count=len(released),
        released_physical_page_count=len(set(released.values())), union_selector_count=len(inherited | set(released)),
        raw_lines_selected=len(raw), alternate_lines_selected=len(alternatives),
        released_line_status_rows_selected=len(atlas), inventory_occurrences=len(expected),
        summary_rows=len(summary), distribution_rows=len(distributions),
        f88r_seed_occurrences=sum(r['physical_page'] == 'f88r' for r in expected),
        three_reading_rank_supported=sum(r['reader_support_count'] == 3 for r in expected),
        new_pages_opened=0, new_images_opened=0, semantic_credit=0, component_export_credit=0)
    require('reference result counts, zero export and source/artifact binding',
            all(result[k] == v for k, v in wanted.items()) and result['surfaces'] == surfaces
            and result['status'] == 'DESCRIPTIVE_WHOLE_INVENTORY__NO_MEANING_SELECTION'
            and check_hashes(result, 'source_hashes', 'artifact_hashes'))


def validate_scope(released, atlas, cross):
    # Independently start at each marked paragraph; any restart, gap, non-prose
    # or known-record change invalidates it before a marked end is reached.
    paragraphs = []
    for selector in released:
        lines = sorted((r for r in atlas if r['source_selector'] == selector), key=lambda r: int(r['line_number']))
        for start, first in enumerate(lines):
            if first['line_kind'] != 'RUNNING_PROSE' or first['paragraph_start'] != '1':
                continue
            selected, records = [], set()
            for offset, row in enumerate(lines[start:]):
                if (row['line_kind'] != 'RUNNING_PROSE'
                        or (offset and row['paragraph_start'] == '1')
                        or int(row['line_number']) != int(first['line_number']) + offset):
                    break
                if row['record_ids'] not in ('', 'NONE'):
                    records.add(row['record_ids'])
                if len(records) > 1:
                    break
                selected.append(row)
                if row['paragraph_end'] == '1':
                    paragraphs.append(selected)
                    break
    owners = {(r['source_selector'], r['locus']): p for p in paragraphs for r in p}
    if len(owners) != sum(len(p) for p in paragraphs):
        raise AssertionError('overlapping independently rebuilt paragraphs')
    inventory = read_tsv(ART / 'SCOPE_INVENTORY.tsv')
    source_targets = [(r, i) for r in atlas if r['line_kind'] == 'RUNNING_PROSE'
                      for i, w in enumerate(r['eva_clean'].split(), 1) if w == 'otchol']
    require('every released running otchol retained, including excluded scopes',
            [(r['page'], r['source_locus'], int(r['source_token_index'])) for r in inventory]
            == [(r['source_selector'], r['locus'], i) for r, i in source_targets])
    expected = []
    for number, (row, index) in enumerate(source_targets, 1):
        p = owners.get((row['source_selector'], row['locus']))
        event = dict(event_id=f'SC{number:04d}', page=row['source_selector'], physical_page=row['physical_page'],
            source_locus=row['locus'], source_token_index=index, paragraph_id='NONE',
            scope_eligibility='EXCLUDED_NO_STRICT_COMPLETE_PARAGRAPH', next_chol_present='NA',
            target_locus='NONE', target_token_index='NA', intervening_width='NA', exact_width_two=0,
            crossed_physical_line=0, segment_source_loci='NONE', segment_eva='NONE', interior_eva='NONE',
            following_token='NA', zl3b_segment_count=0, it2a_segment_count=0, rf1b_segment_count=0,
            it2a_suffix_exact=0, rf1b_suffix_exact=0, reader_support=0,
            discovery_case=int(row['source_selector'] == 'f17r' and row['locus'] in ('f17r.2', 'f17r.11')),
            confirmed_lexemes=0, component_exports=0)
        if p:
            cells = [(r['locus'], i, w) for r in p for i, w in enumerate(r['eva_clean'].split(), 1)]
            source_index = [(loc, i) for loc, i, _ in cells].index((row['locus'], index))
            later = [i for i, c in enumerate(cells) if i > source_index and c[2] == 'chol']
            end = later[0] if later else len(cells) - 1
            part = cells[source_index:end + 1]
            loci = list(dict.fromkeys(c[0] for c in part))
            segment_rows = [r for r in p if r['locus'] in loci]
            pattern = [c[2] for c in part]
            texts = {'zl3b': ' '.join(r['eva_clean'] for r in segment_rows)}
            for name in ['it2a', 'rf1b']:
                texts[name] = ' '.join(cross[r['source_selector'], r['locus']][name + '_clean'] for r in segment_rows)
            source_count = len(positions(texts['zl3b'], pattern))
            event.update(paragraph_id=p[0]['locus'] + ':' + p[-1]['locus'],
                scope_eligibility='STRICT_COMPLETE_PARAGRAPH', next_chol_present=int(bool(later)),
                target_locus=cells[end][0] if later else 'ABSENT_TO_PARAGRAPH_END',
                target_token_index=cells[end][1] if later else 'NA',
                intervening_width=end - source_index - 1 if later else 'NA',
                exact_width_two=int(bool(later) and end - source_index == 3),
                crossed_physical_line=int(len(loci) > 1), segment_source_loci='|'.join(loci),
                segment_eva=' '.join(pattern), interior_eva=' '.join(pattern[1:-1] if later else pattern[1:]),
                following_token=cells[end + 1][2] if later and end + 1 < len(cells) else 'PARAGRAPH_END',
                zl3b_segment_count=source_count, reader_support=1)
            for name in ['it2a', 'rf1b']:
                available = all(cross[r['source_selector'], r['locus']][name + '_clean'] for r in segment_rows)
                count = len(positions(texts[name], pattern)) if available else 0
                suffix = bool(available and texts[name].split()[-len(pattern):] == pattern)
                event[name + '_segment_count'] = count
                event[name + '_suffix_exact'] = int(suffix)
                event['reader_support'] += int(count == source_count and (bool(later) or suffix))
        expected.append(event)
    require('strict paragraph boundaries, first chol, absence suffix and exact reader support',
            inventory == stringify(expected))
    eligible = [r for r in expected if r['scope_eligibility'] == 'STRICT_COMPLETE_PARAGRAPH']
    two = [r for r in eligible if r['exact_width_two']]
    external = [r for r in two if r['physical_page'] != 'f17r']
    wanted = dict(physical_pages=len(set(released.values())), source_selectors=len(released), atlas_lines=len(atlas),
        running_prose_lines=sum(r['line_kind'] == 'RUNNING_PROSE' for r in atlas),
        strict_complete_paragraphs=len(paragraphs), strict_prose_lines=len(owners),
        otchol_occurrences=len(expected), eligible_occurrences=len(eligible), excluded_occurrences=len(expected) - len(eligible),
        next_chol_found=sum(r['next_chol_present'] == 1 for r in eligible),
        next_chol_absent=sum(r['next_chol_present'] == 0 for r in eligible),
        width_two_occurrences=len(two), width_two_three_readers=sum(r['reader_support'] == 3 for r in two),
        width_two_line_crossings=sum(r['crossed_physical_line'] for r in two),
        external_width_two_occurrences=len(external), external_width_two_three_readers=sum(r['reader_support'] == 3 for r in external),
        discovery_events=[r['event_id'] for r in expected if r['discovery_case']], confirmed_lexemes=0, component_exports=0, new_pages=0)
    result = read_json('SCOPE_RESULT.json')
    require('scope result counts, zero export and source/artifact binding',
            all(result[k] == v for k, v in wanted.items())
            and result['semantic_identity_selected'] is False and result['edge_score_ready'] is False
            and result['sealed_data'] == {'f84': 'FORBIDDEN', 'f84r': 'FORBIDDEN'}
            and check_hashes(result, 'source_sha256', 'artifact_sha256'))


def validate_packet(edges):
    packet = read_tsv(ART / 'GDT388_RELATION_PACKET.tsv')
    expected = [(e['edge_id'], e['label_locus'].split('.')[0], e['label_locus'],
                 f"{e['prose_locus']}@{e['start_token']}", 'EXACT_COMPLETE_LABEL_SEQUENCE_REUSE') for e in edges]
    expected += [(r['event_id'], r['page'], f"{r['source_locus']}@{r['source_token_index']}",
                  f"{r['target_locus']}@{r['target_token_index']}", 'OTCHOL_NEXT_CHOL_WRITTEN_SPAN')
                 for r in read_tsv(ART / 'SCOPE_INVENTORY.tsv') if r['next_chol_present'] == '1']
    require('all textual relations retain original loci and explicit unsealed status',
            [(p['edge_id'], p['page'], p['pivot_locus'], p['target_locus'], p['relation_type']) for p in packet] == expected
            and all(p['formal_access_state'] == 'UNSEALED_ALREADY_INSPECTED'
                and p['eligibility_status'] == 'INELIGIBLE_TEXT_ONLY'
                and p['ownership_basis'] == 'NO_VISUAL_REFERENT_IDENTITY'
                and p['geometry_only_selection'] == 'FALSE'
                and all(p[k] == 'NONE' for k in ['page_crop_sha256', 'pivot_crop_sha256', 'target_crop_sha256'])
                for p in packet))
    proc = subprocess.run([str(ROOT / 'vmanus-exp'), 'check-edge-packet',
        str((ART / 'GDT388_RELATION_PACKET.tsv').relative_to(ROOT))],
        cwd=ROOT, capture_output=True, text=True)
    intake, errors = json.loads(proc.stdout), []
    for index, row in enumerate(packet, 2):
        if row['target_locus'].split('.')[0] != row['page']:
            errors.append(f'edge row {index}: target_locus is not on page')
        errors.append(f'edge row {index}: formal access is not sealed')
    require('GDT388 rerun: zero eligible edges; unsealed and cross-selector errors disclosed',
            intake == read_json('GDT388_EDGE_INTAKE.json') and not intake['score_ready']
            and intake['eligible_edges'] == 0 and intake['errors'] == errors)


if __name__ == '__main__':
    raise SystemExit(main())
