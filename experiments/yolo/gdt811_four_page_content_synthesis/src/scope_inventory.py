#!/usr/bin/env python3
"""Enumerate exact otchol-to-next-chol scope in the GDT791 released prose."""
from __future__ import annotations
import csv
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys

sys.dont_write_bytecode = True
ROOT = next(p for p in Path(__file__).resolve().parents if (p / 'AGENTS.md').is_file())
BASE = Path(__file__).resolve().parent.parent
ART = BASE / 'artifacts'
G791 = 'experiments/yolo/gdt791_thirty_page_visual_owner_spine/'
SELECTORS = G791 + 'src/PAGE_SELECTOR_SPECS.tsv'
ATLAS = G791 + 'artifacts/GDT791_1007_LINE_OWNER_ATLAS.tsv'
CROSS = 'transcription/voynich_cross_transcription_lines.tsv'


def read(path):
    with path.open(encoding='utf-8', newline='') as handle:
        return list(csv.DictReader(handle, delimiter='\t'))


def digest(path):
    with path.open('rb') as handle:
        return hashlib.file_digest(handle, 'sha256').hexdigest()


def query(path, selector, allowed, columns):
    command = [str(ROOT / 'vmanus-exp'), 'query-tsv', path, '--selector', selector]
    for value in allowed:
        command += ['--allow', value]
    command += ['--columns', columns, '--forbid-prefix', 'f84', '--forbid-prefix', 'f84r']
    done = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, check=True)
    stats = [json.loads(s[12:]) for s in done.stderr.splitlines() if s.startswith('GUARD_STATS ')]
    assert len(stats) == 1
    return list(csv.DictReader(io.StringIO(done.stdout), delimiter='\t')), {
        'source': path, 'selector': selector, 'allow_count': len(allowed),
        'columns': columns, 'stats': stats[0]}


def segment_count(words, pattern):
    return sum(words[i:i + len(pattern)] == pattern for i in range(len(words) - len(pattern) + 1))


def strict_paragraphs(lines):
    """Do not repair truncated paragraphs or join across non-prose records."""
    paragraphs, pending = [], []
    for row in lines:
        row_records = {v for v in row['record_ids'].split('|') if v not in ('', 'NONE')}
        if row['line_kind'] != 'RUNNING_PROSE' or len(row_records) > 1:
            pending = []
            continue
        if pending:
            previous = pending[-1]
            known_records = {v for r in pending + [row] for v in r['record_ids'].split('|')
                             if v not in ('', 'NONE')}
            if (int(row['line_number']) != int(previous['line_number']) + 1
                    or row['source_selector'] != previous['source_selector'] or len(known_records) > 1):
                pending = []
        if row['paragraph_start'] == '1':
            pending = [row]
        elif pending:
            pending.append(row)
        if row['paragraph_end'] == '1' and pending:
            paragraphs.append(pending)
            pending = []
    return paragraphs


def main():
    design = BASE / 'src/F17_SCOPE_PROPOSAL.md'
    assert design.is_file(), 'write the disclosed design before execution'
    mapping = read(ROOT / SELECTORS)
    selectors = [r['source_selector'] for r in mapping]
    assert len(selectors) == len(set(selectors)) == 35
    assert len({r['physical_page'] for r in mapping}) == 30
    assert not any(s.startswith('f84') for s in selectors)
    columns = ('source_selector,physical_page,locus,line_number,paragraph_start,paragraph_end,'
               'line_kind,record_ids,eva_clean')
    lines, atlas_stats = query(ATLAS, 'source_selector', selectors, columns)
    alternatives, cross_stats = query(CROSS, 'page', selectors,
        'page,locus,zl3b_clean,it2a_clean,rf1b_clean')
    cross = {(r['page'], r['locus']): r for r in alternatives}
    assert len(cross) == len(alternatives)
    assert all(cross[r['source_selector'], r['locus']]['zl3b_clean'] == r['eva_clean'] for r in lines)
    paragraphs = []
    for selector in selectors:
        group = sorted((r for r in lines if r['source_selector'] == selector), key=lambda r: int(r['line_number']))
        paragraphs.extend(strict_paragraphs(group))
    owners = {}
    for paragraph in paragraphs:
        pid = paragraph[0]['locus'] + ':' + paragraph[-1]['locus']
        for row in paragraph:
            key = row['source_selector'], row['locus']
            assert key not in owners
            owners[key] = pid, paragraph
    events = []
    for row in lines:
        if row['line_kind'] != 'RUNNING_PROSE':
            continue
        for source_index, word in enumerate(row['eva_clean'].split(), 1):
            if word != 'otchol':
                continue
            event = dict(event_id=f'SC{len(events) + 1:04d}', page=row['source_selector'],
                physical_page=row['physical_page'], source_locus=row['locus'], source_token_index=source_index,
                paragraph_id='NONE', scope_eligibility='EXCLUDED_NO_STRICT_COMPLETE_PARAGRAPH',
                next_chol_present='NA', target_locus='NONE', target_token_index='NA', intervening_width='NA',
                exact_width_two=0, crossed_physical_line=0, segment_source_loci='NONE', segment_eva='NONE',
                interior_eva='NONE', following_token='NA', zl3b_segment_count=0, it2a_segment_count=0,
                rf1b_segment_count=0, it2a_suffix_exact=0, rf1b_suffix_exact=0, reader_support=0,
                discovery_case=int(row['source_selector'] == 'f17r' and row['locus'] in ('f17r.2', 'f17r.11')),
                confirmed_lexemes=0, component_exports=0)
            owner = owners.get((row['source_selector'], row['locus']))
            if owner:
                pid, paragraph = owner
                cells = [(r['locus'], i, w) for r in paragraph for i, w in enumerate(r['eva_clean'].split(), 1)]
                begin = next(i for i, c in enumerate(cells) if c[:2] == (row['locus'], source_index))
                target = next((i for i in range(begin + 1, len(cells)) if cells[i][2] == 'chol'), None)
                end = target if target is not None else len(cells) - 1
                pattern = [c[2] for c in cells[begin:end + 1]]
                loci = list(dict.fromkeys(c[0] for c in cells[begin:end + 1]))
                segment_lines = [r for r in paragraph if r['locus'] in loci]
                source_words = [w for r in segment_lines for w in r['eva_clean'].split()]
                source_count = segment_count(source_words, pattern)
                assert source_count > 0
                event.update(paragraph_id=pid, scope_eligibility='STRICT_COMPLETE_PARAGRAPH',
                    next_chol_present=int(target is not None),
                    target_locus=cells[target][0] if target is not None else 'ABSENT_TO_PARAGRAPH_END',
                    target_token_index=cells[target][1] if target is not None else 'NA',
                    intervening_width=target - begin - 1 if target is not None else 'NA',
                    exact_width_two=int(target is not None and target - begin - 1 == 2),
                    crossed_physical_line=int(len(loci) > 1), segment_source_loci='|'.join(loci),
                    segment_eva=' '.join(pattern),
                    interior_eva=' '.join(pattern[1:-1] if target is not None else pattern[1:]),
                    following_token=cells[target + 1][2] if target is not None and target + 1 < len(cells)
                                    else 'PARAGRAPH_END', zl3b_segment_count=source_count, reader_support=1)
                for reader, prefix in (('it2a_clean', 'it2a'), ('rf1b_clean', 'rf1b')):
                    available = all(cross[r['source_selector'], r['locus']][reader] for r in segment_lines)
                    other = [w for r in segment_lines for w in cross[r['source_selector'], r['locus']][reader].split()]
                    count = segment_count(other, pattern) if available else 0
                    suffix = bool(available and other[-len(pattern):] == pattern)
                    event[prefix + '_segment_count'] = count
                    event[prefix + '_suffix_exact'] = int(suffix)
                    event['reader_support'] += int(count == source_count and (target is not None or suffix))
            events.append(event)
    fields = list(events[0]) if events else ['event_id', 'page', 'source_locus', 'scope_eligibility']
    with (ART / 'SCOPE_INVENTORY.tsv').open('w', encoding='utf-8', newline='') as handle:
        writer = csv.DictWriter(handle, fields, delimiter='\t', lineterminator='\n')
        writer.writeheader()
        writer.writerows(events)
    eligible = [r for r in events if r['scope_eligibility'] == 'STRICT_COMPLETE_PARAGRAPH']
    exact = [r for r in eligible if r['exact_width_two']]
    external = [r for r in exact if r['physical_page'] != 'f17r']
    result = dict(experiment_id='GDT811', inventory='OTCHOL_TO_NEXT_CHOL_STRICT_PARAGRAPH',
        status='FORMAL_TWO_FIELD_FRAME_RECURS_OUTSIDE_F17R__MEANINGS_OPEN' if external
               else 'NO_RELEASED_PAGE_EXTENSION_OF_F17R_TWO_FIELD_FRAME',
        physical_pages=30, source_selectors=35, atlas_lines=len(lines),
        running_prose_lines=sum(r['line_kind'] == 'RUNNING_PROSE' for r in lines),
        strict_complete_paragraphs=len(paragraphs), strict_prose_lines=sum(map(len, paragraphs)),
        otchol_occurrences=len(events), eligible_occurrences=len(eligible), excluded_occurrences=len(events) - len(eligible),
        next_chol_found=sum(r['next_chol_present'] == 1 for r in eligible),
        next_chol_absent=sum(r['next_chol_present'] == 0 for r in eligible),
        width_two_occurrences=len(exact), width_two_three_readers=sum(r['reader_support'] == 3 for r in exact),
        width_two_line_crossings=sum(r['crossed_physical_line'] for r in exact),
        external_width_two_occurrences=len(external), external_width_two_three_readers=sum(r['reader_support'] == 3 for r in external),
        discovery_events=[r['event_id'] for r in events if r['discovery_case']],
        query_stats=[atlas_stats, cross_stats],
        source_sha256={p: digest(ROOT / p) for p in (SELECTORS, ATLAS, CROSS,
            str(design.relative_to(ROOT)), str(Path(__file__).resolve().relative_to(ROOT)))},
        artifact_sha256={'SCOPE_INVENTORY.tsv': digest(ART / 'SCOPE_INVENTORY.tsv')},
        confirmed_lexemes=0, component_exports=0, new_pages=0, semantic_identity_selected=False,
        edge_score_ready=False, relation_intake='ENCLOSING_EXPERIMENT_REQUIRED',
        sealed_data={'f84': 'FORBIDDEN', 'f84r': 'FORBIDDEN'})
    (ART / 'SCOPE_RESULT.json').write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + '\n')
    print(json.dumps({k: v for k, v in result.items() if k not in ('source_sha256', 'query_stats', 'artifact_sha256')}, sort_keys=True))


if __name__ == '__main__':
    main()
