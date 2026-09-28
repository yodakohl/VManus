#!/usr/bin/env python3
"""GDT1061: selector-first exact alignment of six pinned public case strings."""
import csv
import io
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parents[1]
PAGES = ('f56r', 'f77r', 'f88r')
READERS = ('zl3b', 'it2a', 'rf1b')


def guarded(source, columns):
    cmd = [str(ROOT / 'vmanus-exp'), 'query-tsv', source,
           '--selector', 'page']
    for page in PAGES:
        cmd += ['--allow', page]
    cmd += ['--columns', ','.join(columns)]
    result = subprocess.run(cmd, cwd=ROOT, check=True, text=True,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    assert '"skipped_forbidden": 98' in result.stderr, result.stderr
    return list(csv.DictReader(io.StringIO(result.stdout), delimiter='\t'))


def contains(seq, needle):
    return any(seq[i:i+len(needle)] == needle
               for i in range(len(seq)-len(needle)+1))


def main():
    claims = list(csv.DictReader((HERE / 'src/claims.tsv').open(), delimiter='\t'))
    assert len(claims) == 6
    records = guarded('transcription/voynich_cross_transcription_lines.tsv',
                      ['page', 'locus'] + [x+'_clean' for x in READERS])
    metadata = guarded('transcription/voynich_zl3b_lines.tsv',
                       ['page', 'locus', 'kind'])
    kinds = {r['locus']: r['kind'] for r in metadata}
    assert len(kinds) == len(metadata)
    by_page = {p: [] for p in PAGES}
    for row in records:
        if kinds[row['locus']] == 'P':
            by_page[row['page']].append(row)
    assert all(by_page.values())
    results = []
    for claim in claims:
        target = claim['quoted_raw_eva'].split('.')
        page = claim['page']
        for reader in READERS:
            key = reader + '_clean'
            rows = by_page[page]
            tokens = [r[key].split() for r in rows]
            all_rows = [r for r in records if r['page'] == page]
            all_tokens = [r[key].split() for r in all_rows]
            whole = [r['locus'] for r, t in zip(rows, tokens) if t == target]
            span = [r['locus'] for r, t in zip(rows, tokens) if contains(t, target)]
            across = [rows[i]['locus'] + '|' + rows[i+1]['locus']
                      for i in range(len(rows)-1)
                      if int(rows[i+1]['locus'].rsplit('.', 1)[1]) ==
                         int(rows[i]['locus'].rsplit('.', 1)[1]) + 1
                      if contains(tokens[i] + tokens[i+1], target)
                      and not contains(tokens[i], target)
                      and not contains(tokens[i+1], target)]
            max_overlap = max((length for t in tokens
                               for length in range(1, len(target)+1)
                               for i in range(len(target)-length+1)
                               if contains(t, target[i:i+length])), default=0)
            results.append(dict(id=claim['id'], page=page, reader=reader,
                                groups=len(target), prose_loci=len(rows),
                                whole_line=';'.join(whole),
                                same_line_span=';'.join(span),
                                adjacent_line_span=';'.join(across),
                                any_kind_span=';'.join(r['locus'] for r, t in zip(all_rows, all_tokens)
                                                       if contains(t, target)),
                                longest_same_line_group_run=max_overlap))
    out = HERE / 'artifacts'
    out.mkdir(exist_ok=True)
    with (out / 'CASE_RESULTS.tsv').open('w', newline='') as fh:
        writer = csv.DictWriter(fh, fieldnames=list(results[0]), delimiter='\t',
                                lineterminator='\n')
        writer.writeheader()
        writer.writerows(results)
    kostain = {page: {reader: [r['locus'] for r in by_page[page]
                                  if 'kostain' in r[reader+'_clean'].split()]
                      for reader in READERS}
               for page in ('f77r', 'f88r')}
    payload = dict(source_url='https://github.com/denoflore/ZFD/blob/3f030a9293b8db15dc2c7b0d0e7c703e71711f62/05_Case_Studies/CASE_STUDIES.md',
                   source_sha256='234c7689f9d1ee4cb3592009b8c468151399fff55015c971b633dfff45a75fb3',
                   prose_loci={p: len(rows) for p, rows in by_page.items()},
                   tested_claims=len(claims), tested_reader_pairs=len(results),
                   whole_line_matches=sum(bool(r['whole_line']) for r in results),
                   same_line_span_matches=sum(bool(r['same_line_span']) for r in results),
                   adjacent_line_span_matches=sum(bool(r['adjacent_line_span']) for r in results),
                   all_kind_span_matches=sum(bool(r['any_kind_span']) for r in results),
                   kostain_exact_group_loci=kostain,
                   exposure='f88r previously seen in this turn; all three pages have prior project exposure; no blind confirmation')
    (out / 'RESULT.json').write_text(json.dumps(payload, indent=2, ensure_ascii=False)+'\n')
    print(json.dumps(payload, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
