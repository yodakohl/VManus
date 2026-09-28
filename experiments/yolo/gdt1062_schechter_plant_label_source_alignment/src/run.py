#!/usr/bin/env python3
"""Exact source-position audit of the 23 admitted public plant labels."""
import csv
import io
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parents[1]
READERS = ('zl3b', 'it2a', 'rf1b')


def query(source, pages, columns):
    cmd = [str(ROOT/'vmanus-exp'), 'query-tsv', source,
           '--selector', 'page']
    for page in pages:
        cmd += ['--allow', page]
    cmd += ['--columns', ','.join(columns)]
    p = subprocess.run(cmd, cwd=ROOT, text=True, check=True,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    assert '"skipped_forbidden": 98' in p.stderr, p.stderr
    return list(csv.DictReader(io.StringIO(p.stdout), delimiter='\t'))


def locus_order(locus):
    return int(locus.rsplit('.', 1)[1])


def main():
    claims = list(csv.DictReader((HERE/'src/claims.tsv').open(), delimiter='\t'))
    pages = [c['page'] for c in claims]
    assert len(pages) == len(set(pages)) == 23
    rows = query('transcription/voynich_cross_transcription_lines.tsv',
                 pages, ['page','locus']+[r+'_clean' for r in READERS])
    meta = query('transcription/voynich_zl3b_lines.tsv',
                 pages, ['page','locus','kind'])
    kind = {r['locus']: r['kind'] for r in meta}
    assert len(kind) == len(meta)
    by_page = {p: sorted((r for r in rows if r['page'] == p),
                         key=lambda r: locus_order(r['locus'])) for p in pages}
    assert all(by_page.values())
    result = []
    for claim in claims:
        page, label = claim['page'], claim['eva_label']
        source_rows = by_page[page]
        prose = [r for r in source_rows if kind[r['locus']] == 'P']
        assert prose
        head = prose[0]
        for reader in READERS:
            key = reader+'_clean'
            first = head[key].split()[0] if head[key].strip() else ''
            occurrence = [(r['locus'],kind[r['locus']]) for r in source_rows
                          if label in r[key].split()]
            result.append(dict(page=page, eva_label=label,
                               claimed_plant=claim['claimed_plant'],reader=reader,
                               first_p_locus=head['locus'],first_p_group=first,
                               first_p_exact=int(first==label),
                               anywhere_p=';'.join(loc for loc,k in occurrence if k=='P'),
                               anywhere_l=';'.join(loc for loc,k in occurrence if k=='L')))
    out = HERE/'artifacts';out.mkdir(exist_ok=True)
    with (out/'LABEL_RESULTS.tsv').open('w',newline='') as f:
        fields=[k for k in result[0] if k!='first_p_group']+['first_p_group']
        w=csv.DictWriter(f,fieldnames=fields,delimiter='\t',lineterminator='\n')
        w.writeheader();w.writerows(result)
    summary={reader:{'first_p_exact':sum(r['first_p_exact'] for r in result if r['reader']==reader),
                     'anywhere_p':sum(bool(r['anywhere_p']) for r in result if r['reader']==reader),
                     'anywhere_l':sum(bool(r['anywhere_l']) for r in result if r['reader']==reader)}
             for reader in READERS}
    payload=dict(claims=23,excluded_source_pages=['f1v','f54r','f57r'],
                 reader_pairs=len(result),results=summary,
                 source_commit='71f2f3c91e9113d285ab21e024f1dd70c1f43c44',
                 source_sha256='66d9b8771595d1a48817978b336b2bbf857509dff853cd8665b462062e2a1216',
                 claim_ceiling='source position only; no botanical identity or translation')
    (out/'RESULT.json').write_text(json.dumps(payload,indent=2)+'\n')
    print(json.dumps(payload,indent=2))


if __name__=='__main__': main()
