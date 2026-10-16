#!/usr/bin/env python3
"""Retrieve the existing exact-form occurrences for a bounded manual review."""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT))
from tools import word_profiles as w
c=w.ensure_cache();rows=[]
for form in ['sheckhy','lsheckhy']:
    for item in w.occurrences(c,form):
        previous=c.execute('SELECT right_separator FROM groups WHERE edition=? AND page=? AND locus=? AND source_group_index=?',
                           (item['edition'],item['page'],item['locus'],item['source_group_index']-1)).fetchone()
        item['previous_right_separator']=None if previous is None else previous['right_separator']
        rows.append(item)
out={'source_receipt':w.receipt(c),'occurrences':rows,
     'retrieval':'Existing tools.word_profiles.ensure_cache/occurrences, plus exact addressed predecessor right_separator from same guarded cache. No new corpus parser.',
     'claim_ceiling':'Raw occurrence retrieval for manual review; no semantic conclusions.'}
c.close()
dest=Path(__file__).with_name('L_PREFIX_KEDY_OCCURRENCES_20261016.json')
text=json.dumps(out,ensure_ascii=False,indent=2)+'\n'
if '--check' in sys.argv:
    assert dest.read_text()==text
    print('PASS: exact existing-tool occurrence retrieval; no meaning inference')
else:
    dest.write_text(text)
