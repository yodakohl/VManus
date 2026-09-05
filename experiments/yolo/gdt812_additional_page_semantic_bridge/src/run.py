#!/usr/bin/env python3
"""Reconstruct four explicitly admitted pages; no semantic scoring or decoding."""
import csv
import hashlib
import io
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = next(p for p in Path(__file__).resolve().parents if (p / 'AGENTS.md').is_file())
BASE = Path(__file__).resolve().parent.parent
ART = BASE / 'artifacts'
PAGES = ['f21r', 'f32v', 'f100v', 'f101r']
BASE_SOURCE = 'transcription/voynich_zl3b_lines.tsv'
CROSS_SOURCE = 'transcription/voynich_cross_transcription_lines.tsv'
BASE_FIELDS = ['page_order', 'page', 'locus', 'line_number', 'code', 'relation',
               'kind', 'subtype', 'section', 'language', 'hand', 'quire',
               'folio_type', 'paragraph_start', 'paragraph_end', 'token_count',
               'eva_clean', 'ivtff_raw']
CROSS_FIELDS = ['page', 'locus', 'all_three_present', 'all_present_exact',
                'zl3b_it2a_similarity', 'zl3b_rf1b_similarity', 'zl3b_clean',
                'it2a_clean', 'rf1b_clean']
ADDED_FIELDS = ['physical_page', 'source_selector'] + CROSS_FIELDS[2:]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def authorized_spec():
    """Validate the complete admission packet before touching source payload."""
    spec_path = BASE / 'src/SPEC.json'
    admissions_path = BASE / 'src/PAGE_ADMISSIONS.tsv'
    require(spec_path.is_file() and admissions_path.is_file(),
            'Both SPEC.json and PAGE_ADMISSIONS.tsv are required before querying.')
    spec_bytes = spec_path.read_bytes()
    admissions_bytes = admissions_path.read_bytes()
    spec = json.loads(spec_bytes)
    require(spec['physical_pages'] == PAGES, 'Physical-page scope differs from the four-page authorization.')
    require(spec['source_selectors'] == PAGES, 'Source-selector scope differs from the four-page authorization.')
    require({'f84', 'f84r'} <= set(spec['sealed_data']), 'Both sealed selectors must be explicit.')
    admissions = list(csv.DictReader(io.StringIO(admissions_bytes.decode('utf-8')), delimiter='\t'))
    require(len(admissions) == len(PAGES), 'Admission packet must have exactly four rows.')
    require({(r['physical_page'], r['source_selector']) for r in admissions}
            == {(p, p) for p in PAGES}, 'Admission records differ from the authorized page-selector pairs.')
    require(all(r.get('decision') == 'ADMITTED' for r in admissions),
            'Every page requires an explicit ADMITTED decision.')
    require(all(r.get('grant_id') == spec['grant_id'] for r in admissions),
            'Admission records and specification must identify the same authorization grant.')
    return spec, {
        'spec': str(spec_path.relative_to(ROOT)),
        'spec_sha256': hashlib.sha256(spec_bytes).hexdigest(),
        'admissions': str(admissions_path.relative_to(ROOT)),
        'admissions_sha256': hashlib.sha256(admissions_bytes).hexdigest(),
    }


def guarded_query(source, columns):
    cmd = ['./vmanus-exp', 'query-tsv', source, '--selector', 'page']
    for page in PAGES:
        cmd += ['--allow', page]
    cmd += ['--columns', ','.join(columns), '--forbid-prefix', 'f84', '--forbid-prefix', 'f84r']
    completed = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True, check=True)
    stats = [json.loads(line[len('GUARD_STATS '):]) for line in completed.stderr.splitlines()
             if line.startswith('GUARD_STATS ')]
    require(len(stats) == 1, 'Missing or ambiguous selector-first guard audit.')
    reader = csv.DictReader(io.StringIO(completed.stdout), delimiter='\t')
    require(reader.fieldnames == columns, 'Guarded projection columns differ from request.')
    rows = list(reader)
    require({r['page'] for r in rows} == set(PAGES), 'Guarded projection does not cover exactly the admitted pages.')
    require(len({r['locus'] for r in rows}) == len(rows), 'Duplicate source locus in projection.')
    return rows, {
        'source': source, 'selector': 'page', 'allowed': PAGES, 'columns': columns,
        'forbidden_prefixes': ['f84', 'f84r'], 'command': cmd, 'stats': stats[0],
        'projected_tsv_sha256': hashlib.sha256(completed.stdout.encode('utf-8')).hexdigest(),
    }


def main():
    spec, authorization = authorized_spec()
    rows, base_guard = guarded_query(BASE_SOURCE, BASE_FIELDS)
    alternate, cross_guard = guarded_query(CROSS_SOURCE, CROSS_FIELDS)
    alternate_by_locus = {r['locus']: r for r in alternate}
    require({r['locus'] for r in rows} == set(alternate_by_locus),
            'Base and cross-reader locus sets differ; no unmatched locus may be dropped.')
    for row in rows:
        cross = alternate_by_locus[row['locus']]
        require(cross['page'] == row['page'], 'Cross-reader page mismatch.')
        require(cross['zl3b_clean'] == row['eva_clean'], 'Base ZL3b and cross-reader ZL3b differ.')
        row.update({k: cross[k] for k in CROSS_FIELDS[2:]})
        row['physical_page'] = row['source_selector'] = row['page']

    rendered = [
        '# Complete GDT812 admitted-page text', '',
        'EVA is transcription, not plaintext. All source loci and all three cached readings are retained.',
        'ZL3b, IT2a and RF1b are alternative readings of one manuscript, not independent witnesses.',
        'Source kind and paragraph flags are retained; physical lines are not declared to be sentences.',
        'This text-only reader supplies no new visual ownership or object-name identification.', '',
    ]
    summaries = []
    ordered_rows = []
    for page in PAGES:
        group = [r for r in rows if r['page'] == page]
        ordered_rows.extend(group)
        summaries.append({
            'physical_page': page, 'source_selector': page, 'source_lines': len(group),
            'source_kind_counts': dict(sorted(Counter(r['kind'] for r in group).items())),
            'paragraph_starts': sum(r['paragraph_start'] == '1' for r in group),
            'paragraph_ends': sum(r['paragraph_end'] == '1' for r in group),
            'tokens': {name: sum(len(r[col].split()) for r in group)
                       for name, col in [('ZL3b', 'eva_clean'), ('IT2a', 'it2a_clean'), ('RF1b', 'rf1b_clean')]},
            'missing_cached_readings': {name: sum(not r[col] for r in group)
                                       for name, col in [('IT2a', 'it2a_clean'), ('RF1b', 'rf1b_clean')]},
        })
        rendered += [f'## {page}', '']
        for row in group:
            flags = ''.join(' ' + label for field, label in [
                ('paragraph_start', 'PARAGRAPH_START'), ('paragraph_end', 'PARAGRAPH_END')]
                if row[field] == '1')
            rendered += [f"### {row['locus']} — source kind {row['kind']}{flags}", '']
            for name, col in [('ZL3b', 'eva_clean'), ('IT2a', 'it2a_clean'), ('RF1b', 'rf1b_clean')]:
                rendered += [f'{name}:', '', '```text', row[col] or '[no reading in cache]', '```', '']

    ART.mkdir(parents=True, exist_ok=True)
    with (ART / 'ADMITTED_PAGE_LINES.tsv').open('w', encoding='utf-8', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=BASE_FIELDS + ADDED_FIELDS,
                                delimiter='\t', lineterminator='\n')
        writer.writeheader()
        writer.writerows(ordered_rows)
    (ART / 'COMPLETE_ADMITTED_PAGES.md').write_text('\n'.join(rendered).rstrip() + '\n', encoding='utf-8')
    result = {
        'experiment_id': 'GDT812', 'status': 'COMPLETE_ADMITTED_READER__SEMANTICS_UNRESOLVED',
        'physical_pages': PAGES, 'source_selectors': PAGES, 'admitted_physical_pages': len(PAGES),
        'source_lines': len(rows), 'total_tokens': sum(len(r['eva_clean'].split()) for r in rows),
        'summaries': summaries, 'authorization': authorization,
        'guarded_queries': [base_guard, cross_guard], 'sealed_data': spec['sealed_data'],
        'new_relations_counted': 0, 'semantic_ranking_performed': False,
        'confirmed_lexemes': 0, 'confirmed_plaintext_clauses': 0, 'dictionary_changed': False,
        'visual_ownership_inferred': False,
    }
    (ART / 'gdt812_result.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    print(json.dumps({'experiment_id': 'GDT812', 'source_lines': len(rows),
                      'total_tokens': result['total_tokens'], 'physical_pages': PAGES}, sort_keys=True))


if __name__ == '__main__':
    main()
