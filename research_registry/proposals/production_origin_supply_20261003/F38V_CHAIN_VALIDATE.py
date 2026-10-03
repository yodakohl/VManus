#!/usr/bin/env python3
"""Validate raw conservation only; no semantic validation."""
import csv, hashlib, json, re
from collections import Counter
from pathlib import Path
p=Path(__file__).resolve().parent
raw=(p/'F38V_CHAIN_PROJECTION.tsv').read_bytes()
rows=list(csv.DictReader(raw.decode().splitlines(), delimiter='\t'))
assert hashlib.sha256(raw).hexdigest()=='1e1c77be1f9bfb6f3fecd8a00bd70a311649cc725bec7a487af002f8844a8bc7'
report=(p/'F38V_CHAIN_CONSTRUCTION.md').read_text()
checks={}
for edition,n in [('ZL3b',68),('IT2a',66),('RF1b',65)]:
    er=[r for r in rows if r['edition']==edition]
    assert len(er)==n
    section=report.split('### '+edition+'\n',1)[1].split('```text\n',1)[1].split('```',1)[0]
    for line in range(1,9):
        locus=f'f38v.{line}'
        lr=[r for r in er if r['locus']==locus]
        expected=locus+'  '+' '.join(r['ivtff_group_raw'] for r in lr)
        checks[edition+':'+locus]=expected in section.splitlines()
    chain=[r for r in er if (r['locus']=='f38v.6' and int(r['source_group_index'])>=5) or (r['locus']=='f38v.7' and r['source_group_index']=='1')]
    assert [r['ivtff_group_raw'] for r in chain]==['daiin','daiiin','dain','dain','daiin']
    assert chain[1]['right_separator']==chain[2]['left_separator']=='DRAWING_INTERRUPTION'
assert len(rows)==199 and all(checks.values())
print(json.dumps({'status':'PASS','scope':'raw conservation only, not meaning','groups':len(rows),'lines':len(checks),'drawing_interruption':True,'semantic_continuity_proved':False},indent=2))
