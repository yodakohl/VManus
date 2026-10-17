#!/usr/bin/env python3
"""Serialize the fixed observations; never rejudge images or decode meanings."""
import hashlib,json
from pathlib import Path
D=Path(__file__).resolve().parents[1]
ROOT=D.parents[2]
def read(name):return json.loads((D/name).read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
spec=read('src/SPEC.json');lock=read('src/PROTOCOL_LOCK.json')
for path,digest in lock['pins'].items():assert sha(ROOT/path)==digest,path
obs=read('artifacts/OBSERVATION.json')
assert obs['status'] in ('OBSERVED','TARGET_LOCALIZATION_STOP')
overview=read('artifacts/OVERVIEW_SOURCE.json')
if obs['status']=='OBSERVED':
 assert obs['oneoverview_onecrop'] is True
 assert [x['id'] for x in obs['observations']]==[x['id'] for x in spec['seams']]
 assert all(x['category'] in spec['categories'] and x['reason'].strip() for x in obs['observations'])
 detail=read('artifacts/DETAIL_SOURCE.json')
else:
 assert obs['observations']==[] and not (D/'artifacts/DETAIL_SOURCE.json').exists()
 detail=None
result={'status':obs['status'],'observation':obs,'source_receipts':{'overview':overview,'detail':detail},'pins':{'SPEC':sha(D/'src/SPEC.json'),'OBSERVATION':sha(D/'artifacts/OBSERVATION.json'),'PROTOCOL_LOCK':sha(D/'src/PROTOCOL_LOCK.json')},'claim_ceiling':'One informed AI clearance observation on one original photograph; no meaning, true word boundary, numeral, independent confirmation or old-model rescue.','confirmed_words':0}
(D/'artifacts/RESULT.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'status':result['status'],'reported_clearances':len(obs['observations']),'confirmed_words':0}))
