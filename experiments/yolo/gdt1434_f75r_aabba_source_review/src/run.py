#!/usr/bin/env python3
"""Summarize fixed saved observations; no image interpretation or decoding."""
from pathlib import Path
import json,hashlib
D=Path(__file__).resolve().parents[1];R=D.parents[2];A=D/'artifacts'
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
s=read(D/'src/SPEC.json');lock=read(D/'src/PROTOCOL_LOCK.json')
for p,h in lock['pins'].items():assert sha(R/p)==h,p
o=read(A/'OBSERVATION.json')
assert o['status'] in ('OBSERVED','TARGET_LOCALIZATION_STOP')
if o['status']=='OBSERVED':
 assert [v['id'] for v in o['gaps']]==s['gaps'] and [v['id'] for v in o['pairs']]==s['pairs']
 assert all(v['category'] in s['gap_categories'] and v['reason'].strip() for v in o['gaps'])
 assert all(v['category'] in s['pair_categories'] and v['reason'].strip() for v in o['pairs'])
 supported=all(v['category']=='SPACE_LIKE' for v in o['gaps']) and [v['category'] for v in o['pairs']]==['SIMILAR','SIMILAR','SIMILAR','DIFFERENT']
 status='LOCAL_REPEAT_AND_CONTRAST_SUPPORT' if supported else 'MIXED_OR_UNRESOLVED'
else:
 assert not o['gaps'] and not o['pairs'];status='TARGET_LOCALIZATION_STOP'
x={'status':status,'observation':o,'observation_sha256':sha(A/'OBSERVATION.json'),'protocol_lock_sha256':sha(D/'src/PROTOCOL_LOCK.json'),'confirmed_words':0,'claim_ceiling':'One informed AI spacing/coarse-shape observation; no exact e-count, signidentity, linguisticword, meaning, independentconfirmation or old-modelrescue.'}
(A/'RESULT.json').write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'status':status,'judgments':len(o['gaps'])+len(o['pairs']),'confirmed_words':0}))
