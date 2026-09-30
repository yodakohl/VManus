#!/usr/bin/env python3
"""Check retained array, group boundaries and source identities; not meanings."""
import hashlib,json
from pathlib import Path
B=Path(__file__).resolve().parent
ROOT=B.parents[3]
x=json.loads((B/'BZ_CAPTIONS.json').read_text())
assert hashlib.sha256((ROOT/x['source_packet']).read_bytes()).hexdigest()==x['source_packet_sha256']
assert [c['label'] for c in x['captions']]==list(range(1,11))
assert len(x['annotations'])==20
for c in x['captions']:
 assert c['loci']==['f75v.'+str(16+2*c['label']),'f75v.'+str(17+2*c['label'])]
 for e,v in c['readings'].items():
  for locus,groups,display in zip(c['loci'],v['fields'],v['display']):
   assert all(r['edition']==e and r['locus']==locus and r['page']=='f75v' and r['kind']=='L' for r in groups)
   assert display==' '.join(r['ivtff_group_raw'] for r in groups)
assert x['exact_field_repetitions']['ZL3b']['1']==[{'groups':['daldy'],'labels':[3,8]}]
assert x['exact_field_repetitions']['RF1b']['1']==[{'groups':['daldy'],'labels':[3,8]}]
assert x['exact_field_repetitions']['IT2a']['1']==[]
assert all(v['2']==[] for v in x['exact_field_repetitions'].values())
assert x['confirmed_words']==x['independent_meaning_confirmation_leaves']==0
native=json.loads((B/'BZ_NATIVE.json').read_text())
assert hashlib.sha256((B/native['image']).read_bytes()).hexdigest()==native['image_sha256']
priors=json.loads((B/'BZ_WORD_PRIORS.json').read_text())
counts={p['form']:[p['editions'][e]['count'] for e in ['ZL3b','IT2a','RF1b']] for p in priors['profiles']}
assert counts=={'daldy':[17,16,8],'dokal':[2,1,2],'darol':[2,2,2],'darolsy':[1,1,1]}
files=['BZ_CAPTION_DECISION.md','BZ_CAPTION_REPORT.md','BZ_CAPTION_TABLE.md','BZ_CAPTIONS.json','BZ_NATIVE.json','BZ_WORD_PRIORS.json','BZ_RETAIN.py','BZ_VALIDATE.py']
r={'status':'PASS_BOOKKEEPING_ONLY','meaning_verified':False,'files_sha256':{f:hashlib.sha256((B/f).read_bytes()).hexdigest() for f in files},'confirmed_words':0}
(B/'BZ_VALIDATION.json').write_text(json.dumps(r,indent=2)+'\n')
print('PASS ten complete pairs, reader distinctions, word counts, source/image identities; no meaning validation.')
