#!/usr/bin/env python3
"""Source/draft conservation only; no automatic medical or meaning validation."""
import hashlib,json
from pathlib import Path
B=Path(__file__).resolve().parent;ROOT=B.parents[3]
p=json.loads((B/'CE_SOURCE.json').read_text());r=json.loads((B/'CE_RESULT.json').read_text())
assert hashlib.sha256((ROOT/p['command'][2]).read_bytes()).hexdigest()==p['source_sha256']
assert len(p['rows'])==253 and len(p['lines'])==36
assert {e:sum(x['edition']==e for x in p['rows']) for e in ['ZL3b','IT2a','RF1b']}=={'ZL3b':86,'IT2a':84,'RF1b':83}
assert all(x['page']=='f9v' for x in p['rows'])
assert [x['source_group_id'] for l in p['lines'] for x in l['groups']]==[x['source_group_id'] for x in r['positions']]
for raw,out in zip([x for l in p['lines'] for x in l['groups']],r['positions']):
 assert raw['ivtff_group_raw']==out['raw']
 assert out['hypothesis']==r['whole_form_assumptions'].get(out['raw'])
assert r['hypothesis_positions']==16 and r['unread_positions']==237
assert r['confirmed_words']==r['independent_meaning_confirmation_leaves']==0
f={l['edition']:[g['ivtff_group_raw'] for g in l['groups']] for l in p['lines'] if l['locus']=='f9v.11'}
assert f=={'ZL3b':['ychor','chshoty','oky','kaiin'],'IT2a':['ychor','chshoty','oky','kaiin'],'RF1b':['ychor','chshoty','okykaiin']}
assert r['external_current_counts']['chshoty']=={'ZL3b':1,'IT2a':1,'RF1b':1}
files=['CE_DECISION.md','CE_REPORT.md','CE_SOURCE.json','CE_RESULT.json','CE_WORD_PRIORS.json','CE_MAGNINUS_REVIEW.json','CE_CONTEXTS.md','CE_FULL_SPARSE_DRAFT.md','CE_RETAIN.py','CE_VALIDATE.py']
v={'status':'PASS_SOURCE_AND_DRAFT_CONSERVATION_ONLY','meaning_verified':False,'file_sha256':{f:hashlib.sha256((B/f).read_bytes()).hexdigest() for f in files}}
(B/'CE_VALIDATION.json').write_text(json.dumps(v,indent=2)+'\n')
print(v['status'],'253 groups;16 assumptions;237 unread;0confirmed')
