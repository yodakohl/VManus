"""Frozen post-reader direct nominal qualification diagnostic; C0 types only."""
import json,hashlib
from pathlib import Path
H=Path(__file__).resolve().parents[1]
def j(p):return json.loads((H/p).read_text())
def main():
 d=j('src/POST_READER_DIAGNOSTIC.json');m=j('src/MODEL.json')
 for p,key in [('src/SOURCE.json','source_sha256'),('src/MODEL.json','model_sha256')]:assert hashlib.sha256((H/p).read_bytes()).hexdigest()==d[key]
 cases=[]
 for u in j('src/SOURCE.json')['units']:
  gs=[(w,sid) for l in u['lines'] for w,sid in zip(l['words'],l['source_ids'])]
  for i,(w,sid) in enumerate(gs):
   if w!='chedy' or (i and gs[i-1][0]=='dal'):continue
   prior=gs[i-1] if i else None
   for c,v in m['candidates'].items():
    kind=d['candidate_types'][c].get(prior[0]) if prior else None
    if kind:outcome='ASSUMED_TYPE_COMPATIBLE_NOT_MEANING_CONFIRMATION' if kind in d['property_domain'][c] else 'CONDITIONAL_NOMINAL_PROPERTY_CONTRADICTION'
    else:outcome='NOT_NOMINAL_CONSTRUCTION' if prior and prior[0] in v['dictionary'] else 'UNBOUND_HEAD'
    cases.append({'candidate':c,'edition':u['edition'],'paragraph':u['id'],'positive_id':sid,'head_id':prior[1] if prior else None,'head_raw':prior[0] if prior else None,'assumed_head_type':kind,'assumed_property':v['joint_positive'],'result':outcome})
 outcomes={c:{e:{k:sum(v['candidate']==c and v['edition']==e and v['result']==k for v in cases) for k in d['outcomes'].values()} for e in m['editions']} for c in m['candidates']}
 result={'phase':d['phase'],'cases':cases,'summaries':outcomes,'contradiction_loci':{c:sorted({v['positive_id'].split('|')[1] for v in cases if v['candidate']==c and v['result']=='CONDITIONAL_NOMINAL_PROPERTY_CONTRADICTION'}) for c in m['candidates']},'independent_meaning_confirmation':False,'semantic_selection':None,'decision':'MED_PLUS_DIRECT_NOMINAL_PROPERTY_CONTRADICTED_LIQ_TYPED_CASES_COMPATIBLE_UNBOUND'}
 (H/'artifacts/POST_READER_DIAGNOSTIC.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='cases'}))
if __name__=='__main__':main()
