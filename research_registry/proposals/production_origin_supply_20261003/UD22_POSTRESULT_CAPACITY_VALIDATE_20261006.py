"""Independent finite-substring check of the separately stated hand closure."""
from pathlib import Path
from datetime import datetime,timezone
import json,gzip,hashlib
P=Path('research_registry/proposals/production_origin_supply_20261003');D=Path('experiments/yolo/gdt1235_ud_short_word_capacity');result=P/'UD22_POSTRESULT_CAPACITY_CLOSURE_20261006.json';R=json.loads(result.read_text())
for p,h in R['sources'].items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h,p
spec=json.loads((D/'src/SPEC.json').read_text());data=json.loads(gzip.decompress(Path(spec['source']).read_bytes()))
def parses(w,C):
 reachable={0}
 for i in range(len(w)):
  if i in reachable:
   for c in C:
    if w[i:i+len(c)]==c:reachable.add(i+len(c))
 return len(w)in reachable
checks={}
for reader,old in R['readers'].items():
 rows=data[reader];W=set(tuple(r['units'])for r in rows);cert=json.loads(gzip.decompress((D/f'artifacts/CERTIFICATE_{reader}.json.gz').read_bytes()));cases=[r for r in cert['rows']if r['ud']['status']=='UD'and r['bound']<=22]
 assert {r['mask']for r in cases}=={r['mask']for r in old['all_remaining_cases']}
 for form,wit in old['whole_form_witnesses'].items():
  hit=[r for r in rows if r['ivtff_group_raw']==form];assert len(hit)==wit['panel_count'];assert wit['pages']==sorted({r['page']for r in hit});assert wit['first_occurrence']==(hit[0]if hit else None)
 proofs=[]
 for row in cases:
  S=set(row['singletons']);missing=set(spec['signs'])-S;B={(x,)for x in S}
  for w in W:
   if len(w)==2 and not all(x in S for x in w):B.add(w)
  assert tuple('ain')in W and tuple('aiin')in W
  if 'i'in missing:
   assert len(B)==21 and all('i'not in c for c in B)
   # Every possible additional i-containing code must be a contiguous part
   # of ain, because it is the only available entry able to carry its i.
   w=tuple('ain');possible={w[a:b]for a in range(len(w))for b in range(a+1,len(w)+1)if'i'in w[a:b]}
   assert possible=={tuple(x)for x in('i','ai','in','ain')}
   trials=[]
   for c in sorted(possible):
    legal_singletons=not(len(c)==1 and c[0]not in S)
    both=parses(tuple('ain'),B|{c})and parses(tuple('aiin'),B|{c})
    assert not(legal_singletons and both);trials.append({'candidate':list(c),'keeps_exact_singletons':legal_singletons,'covers_both':both})
   proofs.append({'mask':row['mask'],'finite_substring_checks':trials})
  else:
   assert missing=={'n'}and len(B)==22
   assert not parses(tuple('aiin'),B);proofs.append({'mask':row['mask'],'fixed_table_aiin_parse':False})
 checks[reader]={'status':'PASS','remaining_sets_checked':len(cases),'proofs':proofs}
out={'status':'PASS_POST_RESULT_HAND_CONSEQUENCE','validated_utc':datetime.now(timezone.utc).isoformat(),'result_sha256':hashlib.sha256(result.read_bytes()).hexdigest(),'readers':checks,'scope':'Independent finite substring/parse argument and old-input bindings; original5373-case exhaustive UD accounting is inherited from the unchanged independently validated1235certificate. Not independent ink or semantics.'}
(P/'UD22_POSTRESULT_CAPACITY_VALIDATION_20261006.json').write_text(json.dumps(out,indent=2)+'\n');print(out['status'],{r:v['remaining_sets_checked']for r,v in checks.items()})
