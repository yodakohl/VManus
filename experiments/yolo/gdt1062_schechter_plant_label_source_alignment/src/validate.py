#!/usr/bin/env python3
"""Pin the source table and verify the complete 23 x 3 result packet."""
import csv
import hashlib
import json
import re
from pathlib import Path
from urllib.request import urlopen

HERE = Path(__file__).resolve().parents[1]
URL = ('https://raw.githubusercontent.com/scott-schechter/voynich-decoded/'
       '71f2f3c91e9113d285ab21e024f1dd70c1f43c44/'
       'publication/04-plant-identifications.md')
SHA = '66d9b8771595d1a48817978b336b2bbf857509dff853cd8665b462062e2a1216'


def main():
    raw = urlopen(URL, timeout=20).read()
    assert hashlib.sha256(raw).hexdigest() == SHA
    source = []
    for line in raw.decode().splitlines():
        if re.match(r'^\|?\s*f\d+[rv]\s*\|',line):
            c = [x.strip() for x in line.strip().strip('|').split('|')]
            source.append((c[0],c[1],c[2]))
    claims = list(csv.DictReader((HERE/'src/claims.tsv').open(),delimiter='\t'))
    assert len(source)==26 and len(claims)==23
    assert ({(c['page'],c['eva_label'],c['claimed_plant']) for c in claims}
            == (set(source)-{r for r in source
                             if r[0] in ('f1v','f54r','f57r')}))
    rows=list(csv.DictReader((HERE/'artifacts/LABEL_RESULTS.tsv').open(),delimiter='\t'))
    assert len(rows)==69 and {(r['page'],r['reader']) for r in rows}=={
        (c['page'],x) for c in claims for x in ('zl3b','it2a','rf1b')}
    for r in rows:
        c=next(c for c in claims if c['page']==r['page'])
        assert r['eva_label']==c['eva_label'] and r['claimed_plant']==c['claimed_plant']
        assert int(r['first_p_exact'])==(r['first_p_group']==r['eva_label'])
    result=json.loads((HERE/'artifacts/RESULT.json').read_text())
    assert result['source_sha256']==SHA and result['reader_pairs']==69
    for reader in ('zl3b','it2a','rf1b'):
        rr=[r for r in rows if r['reader']==reader]
        assert result['results'][reader]['first_p_exact']==sum(int(r['first_p_exact']) for r in rr)
        assert result['results'][reader]['anywhere_p']==sum(bool(r['anywhere_p']) for r in rr)
        assert result['results'][reader]['anywhere_l']==sum(bool(r['anywhere_l']) for r in rr)
    print('PASS: pinned source, 23 complete claims and 69 reader outcomes')


if __name__=='__main__': main()
