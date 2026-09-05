#!/usr/bin/env python3
"""Lossless four-page text and explicit exact-label reuse, without gloss export."""
import csv
import io
import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = next(p for p in Path(__file__).resolve().parents if (p / 'AGENTS.md').is_file())
BASE = Path(__file__).resolve().parent.parent
ART = BASE / 'artifacts'
SPINE = 'experiments/yolo/gdt791_thirty_page_visual_owner_spine/artifacts/GDT791_1007_LINE_OWNER_ATLAS.tsv'
CROSS = 'transcription/voynich_cross_transcription_lines.tsv'
LINE_FIELDS = ['physical_page', 'source_selector', 'locus', 'line_number', 'line_kind',
               'paragraph_start', 'paragraph_end', 'panel_ids', 'record_ids', 'eva_clean']
EDGE_FIELDS = ['edge_id', 'physical_page', 'label_locus', 'complete_label', 'prose_locus',
               'start_token', 'end_token', 'occurrence_rank', 'reader_support', 'source_line']


def query(path, selector, allowed, columns):
    cmd = [str(ROOT / 'vmanus-exp'), 'query-tsv', path, '--selector', selector]
    for value in allowed:
        cmd += ['--allow', value]
    cmd += ['--columns', ','.join(columns), '--forbid-prefix', 'f84', '--forbid-prefix', 'f84r']
    result = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True, check=True)
    stats = [json.loads(line[12:]) for line in result.stderr.splitlines() if line.startswith('GUARD_STATS ')]
    assert len(stats) == 1
    return list(csv.DictReader(io.StringIO(result.stdout), delimiter='\t')), {
        'source': path, 'selector': selector, 'allowed': allowed, 'columns': columns, 'stats': stats[0]}


def write_tsv(name, rows, fields):
    with (ART / name).open('w', encoding='utf-8', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter='\t', lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)


def matches(tokens, pattern):
    return [i for i in range(len(tokens) - len(pattern) + 1) if tokens[i:i+len(pattern)] == pattern]


def main():
    spec = json.loads((BASE / 'src/SPEC.json').read_text())
    for script in ['reference_inventory.py', 'scope_inventory.py']:
        subprocess.run([sys.executable, '-B', str((BASE / 'src' / script).relative_to(ROOT))], cwd=ROOT, check=True)
    rows, stats = query(SPINE, 'physical_page', spec['physical_pages'], LINE_FIELDS)
    cross, cstats = query(CROSS, 'page', spec['source_selectors'],
                         ['page', 'locus', 'zl3b_clean', 'it2a_clean', 'rf1b_clean'])
    lookup = {r['locus']: r for r in cross}
    assert len(rows) == spec['expected_source_lines'] == len(lookup)
    assert set(r['locus'] for r in rows) == set(lookup)
    for row in rows:
        other = lookup[row['locus']]
        assert other['page'] == row['source_selector']
        assert other['zl3b_clean'] == row['eva_clean']
        row['it2a_clean'] = other['it2a_clean']
        row['rf1b_clean'] = other['rf1b_clean']
    write_tsv('FOUR_PAGE_LINES.tsv', rows, LINE_FIELDS + ['it2a_clean', 'rf1b_clean'])

    edges = []
    for label in rows:
        if label['line_kind'] != 'LOCAL_LABEL_OR_MARKER' or not label['eva_clean']:
            continue
        seq = label['eva_clean'].split()
        for prose in rows:
            if prose['physical_page'] != label['physical_page'] or prose['line_kind'] != 'RUNNING_PROSE':
                continue
            positions = matches(prose['eva_clean'].split(), seq)
            support = 1 + sum(label[col].split() == seq and len(matches(prose[col].split(), seq)) == len(positions)
                              for col in ['it2a_clean', 'rf1b_clean'])
            for rank, i in enumerate(positions, 1):
                edges.append(dict(edge_id=f'LR{len(edges)+1:03d}', physical_page=label['physical_page'],
                    label_locus=label['locus'], complete_label=label['eva_clean'], prose_locus=prose['locus'],
                    start_token=i+1, end_token=i+len(seq), occurrence_rank=rank, reader_support=support,
                    source_line=prose['eva_clean']))
    write_tsv('EXACT_LABEL_PROSE_MATCHES.tsv', edges, EDGE_FIELDS)

    summaries = []
    reader = ['# Four complete admitted pages', '',
              'EVA is transcription, not plaintext. All local inscriptions are retained separately.',
              'Alternate strings are shown when they differ; physical page f72r contains three selectors.', '']
    for page in spec['physical_pages']:
        group = [r for r in rows if r['physical_page'] == page]
        kinds = Counter(r['line_kind'] for r in group)
        local = [r for r in group if r['line_kind'] == 'LOCAL_LABEL_OR_MARKER']
        prose = [r for r in group if r['line_kind'] == 'RUNNING_PROSE']
        pe = [e for e in edges if e['physical_page'] == page]
        summaries.append(dict(physical_page=page, source_lines=len(group), prose_lines=len(prose),
            local_lines=len(local), total_tokens=sum(len(r['eva_clean'].split()) for r in group),
            prose_tokens=sum(len(r['eva_clean'].split()) for r in prose),
            local_tokens=sum(len(r['eva_clean'].split()) for r in local),
            exact_reused_complete_labels=len({e['complete_label'] for e in pe}),
            reused_label_loci=len({e['label_locus'] for e in pe}), identity_edges=len(pe),
            all_reader_identity_edges=sum(e['reader_support'] == 3 for e in pe)))
        reader += [f'## {page}', '']
        for row in group:
            kind = 'LOCAL INSCRIPTION' if row['line_kind'] != 'RUNNING_PROSE' else 'RUNNING'
            flags = (' PARAGRAPH_START' if row['paragraph_start'] == '1' else '') + (
                     ' PARAGRAPH_END' if row['paragraph_end'] == '1' else '')
            reader += [f"### {row['locus']} — {kind}{flags}", '', row['eva_clean'] or '[empty transcription]', '']
            for col, name in [('it2a_clean', 'IT2a'), ('rf1b_clean', 'RF1b')]:
                if row[col] != row['eva_clean']:
                    reader += [f"{name}: {row[col] or '[no reading in cache]'}", '']
    write_tsv('PAGE_SUMMARY.tsv', summaries, list(summaries[0]))
    (ART / 'FOUR_PAGES_FULL_TEXT.md').write_text('\n'.join(reader).rstrip() + '\n', encoding='utf-8')
    (ART / 'GUARDED_QUERY_STATS.json').write_text(json.dumps([stats, cstats], indent=2, sort_keys=True) + '\n')

    packet_fields = ['edge_id', 'batch_id', 'page', 'physical_folio', 'diagram_unit_id', 'pivot_visual_id',
        'pivot_locus', 'target_visual_id', 'target_locus', 'relation_type', 'direction_basis', 'ownership_basis',
        'geometry_only_selection', 'source_manifest_id', 'page_crop_sha256', 'pivot_crop_sha256', 'target_crop_sha256',
        'source_aware_localizer', 'relation_reviewer', 'relation_confidence', 'ambiguity_state', 'formal_access_state',
        'fold_assignment', 'eligibility_status']
    packet = []
    for e in edges:
        label_selector = e['label_locus'].split('.')[0]
        values = [e['edge_id'], 'GDT811_COMPLETE_LABEL', label_selector, re.match(r'f\d+', e['physical_page'])[0],
            'TEXT_ONLY', 'UNASSIGNED_LABEL_OBJECT', e['label_locus'], 'UNASSIGNED_PROSE_REFERENT',
            f"{e['prose_locus']}@{e['start_token']}", 'EXACT_COMPLETE_LABEL_SEQUENCE_REUSE', 'WRITTEN_IDENTITY',
            'NO_VISUAL_REFERENT_IDENTITY', 'FALSE', 'GDT811', 'NONE', 'NONE', 'NONE', 'cached_transcription',
            'text_identity_audit', 'LOW', 'TEXT_RELATION_ONLY', 'UNSEALED_ALREADY_INSPECTED', 'EXPLORATORY',
            'INELIGIBLE_TEXT_ONLY']
        packet.append(dict(zip(packet_fields, values)))
    with (ART / 'SCOPE_INVENTORY.tsv').open(encoding='utf-8', newline='') as handle:
        scope_rows = list(csv.DictReader(handle, delimiter='\t'))
    for row in scope_rows:
        if row['next_chol_present'] != '1':
            continue
        values = [row['event_id'], 'GDT811_LOCAL_SCOPE', row['page'], re.match(r'f\d+', row['page'])[0],
            'TEXT_ONLY', 'TEXT_OTCHOL', f"{row['source_locus']}@{row['source_token_index']}",
            'TEXT_CHOL', f"{row['target_locus']}@{row['target_token_index']}",
            'OTCHOL_NEXT_CHOL_WRITTEN_SPAN', 'WRITTEN_ORDER', 'NO_VISUAL_REFERENT_IDENTITY',
            'FALSE', 'GDT811', 'NONE', 'NONE', 'NONE', 'cached_transcription', 'text_scope_audit',
            'LOW', 'TEXT_RELATION_ONLY', 'UNSEALED_ALREADY_INSPECTED', 'EXPLORATORY', 'INELIGIBLE_TEXT_ONLY']
        packet.append(dict(zip(packet_fields, values)))
    write_tsv('GDT388_RELATION_PACKET.tsv', packet, packet_fields)
    done = subprocess.run([str(ROOT / 'vmanus-exp'), 'check-edge-packet',
                           str((ART / 'GDT388_RELATION_PACKET.tsv').relative_to(ROOT))], cwd=ROOT,
                          text=True, capture_output=True)
    intake = json.loads(done.stdout)
    assert not intake['score_ready'] and not intake['eligible_edges']
    expected_errors = []
    for i, row in enumerate(packet, 2):
        if row['target_locus'].split('.')[0] != row['page']:
            expected_errors.append(f'edge row {i}: target_locus is not on page')
        expected_errors.append(f'edge row {i}: formal access is not sealed')
    assert intake['errors'] == expected_errors
    (ART / 'GDT388_EDGE_INTAKE.json').write_text(json.dumps(intake, indent=2, sort_keys=True) + '\n')
    result = dict(experiment_id='GDT811', status='COMPLETE_PAGE_SYNTHESIS__MEANINGS_UNRESOLVED',
        source_lines=len(rows), physical_pages=spec['physical_pages'], summaries=summaries,
        exact_identity_edges=len(edges), new_pages=0, confirmed_lexemes=0, component_exports=0,
        translated_manuscript=False, dictionary_changed=False, edge_score_ready=False,
        reference_inventory=json.loads((ART / 'REFERENCE_RESULT.json').read_text()),
        scope_inventory=json.loads((ART / 'SCOPE_RESULT.json').read_text()),
        sealed_data=spec['sealed_data'])
    (ART / 'RESULT.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps({k: v for k, v in result.items() if k not in ['reference_inventory', 'scope_inventory']}, sort_keys=True))


if __name__ == '__main__':
    main()
