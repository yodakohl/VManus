from pathlib import Path
from collections import Counter,defaultdict
import csv,gzip,hashlib,json,re
import numpy as np
B=Path(__file__).resolve().parents[1];R=B.parents[2];KS=[3,5,7,8]
CACHE='experiments/yolo/gdt1233_distinct_initial_fixed_expansion/artifacts/GROUPS.json.gz'
def save(p,x):p.write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
def sums(n,weights):
 a=np.zeros(1<<n,dtype=np.int64)
 for m,v in weights.items():a[m]+=v
 for bit in range(n):
  step=1<<bit;v=a.reshape(-1,2*step);v[:,step:]+=v[:,:step]
 return a
def controls():
 checked=0
 for spec in range(1,128):
  for mode in ['one','mask']:
   w={m:1 if mode=='one' else m for m in range(1,8) if spec>>(m-1)&1};z=sums(3,w)
   for r in range(8):assert int(z[7^r])==sum(v for m,v in w.items() if not(m&r))
   for k in range(4):
    cand=[r for r in range(8) if r.bit_count()==k];assert min((int(z[7^r]),r) for r in cand)==min((sum(v for m,v in w.items() if not(m&r)),r) for r in cand)
   checked+=1
 save(B/'artifacts/CONTROLS.json',{'status':'PASS','support_weight_cases':checked,'representative_masks_each':8,'all_budgets_checked':True})
def run():
 for p,h in json.loads((B/'src/REGISTRATION_LOCK.json').read_text())['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
 data=json.loads(gzip.decompress((R/CACHE).read_bytes()));allow={r['page'] for r in csv.DictReader((R/'experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv').open(),delimiter='\t')};panels={}
 ids=np.arange(1<<22,dtype=np.uint32);lut=np.array([i.bit_count() for i in range(256)],dtype=np.uint8);pop=lut[ids.view(np.uint8)].reshape(-1,4).sum(axis=1,dtype=np.uint8);candidates={k:ids[pop==k] for k in KS};allmask=(1<<22)-1
 for reader,rows in sorted(data.items()):
  forms=defaultdict(list)
  for r in rows:
   assert r['page'] in allow and not r['page'].startswith('f84') and r['page'] not in ('f1r','f116v');assert r['kind']=='P' and r['left_separator']==r['right_separator']=='DEFINITE_SPACE'
   f=r['ivtff_group_raw'];u=re.findall(r'ckh|cth|cph|cfh|ch|sh|[aoeindqysrlmktpf]',f);assert ''.join(u)==f and u==r['units'];forms[f].append(r)
  alpha=sorted({u for rr in forms.values() for u in rr[0]['units']});assert len(alpha)==22;ix={u:i for i,u in enumerate(alpha)}
  leaves={f:sorted({int(re.match(r'f(\d+)',r['page']).group(1)) for r in rr}) for f,rr in forms.items()}
  for panel in ['FULL','GE2']:
   chosen={f:rr for f,rr in forms.items() if panel=='FULL' or len(leaves[f])>=2};supports={f:sum(1<<ix[u] for u in set(rr[0]['units'])) for f,rr in chosen.items()};bygroups=Counter();bytypes=Counter()
   for f,rr in chosen.items():bygroups[supports[f]]+=len(rr);bytypes[supports[f]]+=1
   out={'alphabet':alpha,'groups':sum(len(rr) for rr in chosen.values()),'types':len(chosen),'K':{str(k):{} for k in KS}}
   for objective,weights in [('occurrences',bygroups),('types',bytypes)]:
    z=sums(22,weights)
    for k in KS:
     cs=candidates[k];vals=z[allmask^cs];minimum=int(vals.min());rm=int(cs[np.flatnonzero(vals==minimum)[0]]);missed=[f for f in sorted(chosen) if not(rm&supports[f])];ls=sorted({l for f in missed for l in leaves[f]});ng=sum(len(chosen[f]) for f in missed)
     assert (ng if objective=='occurrences' else len(missed))==minimum
     out['K'][str(k)][objective]={'minimum_uncovered':minimum,'representative_mask':rm,'representatives':[u for i,u in enumerate(alpha) if rm>>i&1],'uncovered_groups':ng,'uncovered_types':len(missed),'uncovered_physical_leaves':len(ls),'uncovered_forms':[{'form':f,'count':len(chosen[f]),'first_id':chosen[f][0]['id'],'physical_leaves':leaves[f]} for f in missed]}
   panels[reader+'_'+panel]=out;print(reader,panel,'groups',out['groups'],'misses',[(k,out['K'][str(k)]['occurrences']['minimum_uncovered'],out['K'][str(k)]['types']['minimum_uncovered']) for k in KS],flush=True)
 save(B/'artifacts/RESULT.json',{'status':'EXACT_MINIMUM_NUCLEUS_OMISSION_ENVELOPE','panels':panels,'scope':'Optimistic unit-support lower bounds on nucleuscarrier-free wholegroups only; no actual vowels, omission, source meaning or abjad evidence.'})
if __name__=='__main__':
 import sys
 controls() if '--controls' in sys.argv else run()
