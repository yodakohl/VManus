"""1363 subset-zeta engine adapted to the predeclared RAW_CHAR representation."""
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
 assert min(r.bit_count() for r in range(4) if all(r&m for m in [1,2]))==2
 assert min(r.bit_count() for r in range(8) if all(r&m for m in [3,5]))==1
 save(B/'artifacts/CONTROLS.json',{'status':'PASS','support_weight_cases':checked,'representative_masks_each':8,'all_budgets_checked':True,'refinement_fixture_tau':[2,1]})
def run():
 for p,h in json.loads((B/'src/REGISTRATION_LOCK.json').read_text())['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
 data=json.loads(gzip.decompress((R/CACHE).read_bytes()));allow={r['page'] for r in csv.DictReader((R/'experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv').open(),delimiter='\t')};panels={}
 old=json.loads((R/'experiments/yolo/gdt1363_nucleus_omission_envelope/artifacts/RESULT.json').read_text())['panels'];oldzero=json.loads((R/'experiments/yolo/gdt1355_fixed_null_erasure_capacity/artifacts/RESULT.json').read_text())['panels']
 for reader,rows in sorted(data.items()):
  forms=defaultdict(list)
  for r in rows:
   assert r['page'] in allow and not r['page'].startswith('f84') and r['page'] not in ('f1r','f116v');assert r['kind']=='P' and r['left_separator']==r['right_separator']=='DEFINITE_SPACE'
   f=r['ivtff_group_raw'];u=re.findall(r'ckh|cth|cph|cfh|ch|sh|[aoeindqysrlmktpf]',f);assert ''.join(u)==f and u==r['units'];forms[f].append(r)
  alpha=sorted({c for f in forms for c in f});n=len(alpha);ix={u:i for i,u in enumerate(alpha)}
  ids=np.arange(1<<n,dtype=np.uint32);lut=np.array([i.bit_count() for i in range(256)],dtype=np.uint8);pop=lut[ids.view(np.uint8)].reshape(-1,4).sum(axis=1,dtype=np.uint8);candidates={k:ids[pop==k] for k in KS};allmask=(1<<n)-1
  leaves={f:sorted({int(re.match(r'f(\d+)',r['page']).group(1)) for r in rr}) for f,rr in forms.items()}
  for panel in ['FULL','GE2']:
   chosen={f:rr for f,rr in forms.items() if panel=='FULL' or len(leaves[f])>=2};supports={f:sum(1<<ix[u] for u in set(f)) for f,rr in chosen.items()};bygroups=Counter();bytypes=Counter()
   for f,rr in chosen.items():bygroups[supports[f]]+=len(rr);bytypes[supports[f]]+=1
   out={'alphabet':alpha,'groups':sum(len(rr) for rr in chosen.values()),'types':len(chosen),'K':{str(k):{} for k in KS}}
   for objective,weights in [('occurrences',bygroups),('types',bytypes)]:
    z=sums(n,weights)
    if objective=='occurrences':
     covers=ids[z[allmask^ids]==0];tau=int(pop[covers].min());hm=int(covers[pop[covers]==tau][0]);out.update(min_hitting_size=tau,hitting_witness_mask=hm,hitting_witness_representatives=[u for i,u in enumerate(alpha) if hm>>i&1])
    for k in KS:
     cs=candidates[k];vals=z[allmask^cs];minimum=int(vals.min());rm=int(cs[np.flatnonzero(vals==minimum)[0]]);missed=[f for f in sorted(chosen) if not(rm&supports[f])];ls=sorted({l for f in missed for l in leaves[f]});ng=sum(len(chosen[f]) for f in missed)
     assert (ng if objective=='occurrences' else len(missed))==minimum
     out['K'][str(k)][objective]={'minimum_uncovered':minimum,'representative_mask':rm,'representatives':[u for i,u in enumerate(alpha) if rm>>i&1],'uncovered_groups':ng,'uncovered_types':len(missed),'uncovered_physical_leaves':len(ls),'uncovered_forms':[{'form':f,'count':len(chosen[f]),'first_id':chosen[f][0]['id'],'physical_leaves':leaves[f]} for f in missed]}
   key=reader+'_'+panel;assert out['groups']==old[key]['groups'] and out['types']==old[key]['types'];assert out['min_hitting_size']<=22-oldzero[key]['max_types']['null_types']
   for k in KS:
    for objective in ['occurrences','types']:assert out['K'][str(k)][objective]['minimum_uncovered']<=old[key]['K'][str(k)][objective]['minimum_uncovered']
   panels[key]=out;print(reader,panel,'alphabet',n,'tau',out['min_hitting_size'],'groups',out['groups'],'misses',[(k,out['K'][str(k)]['occurrences']['minimum_uncovered'],out['K'][str(k)]['types']['minimum_uncovered']) for k in KS],flush=True)
 save(B/'artifacts/RESULT.json',{'status':'RAW_CHARACTER_NUCLEUS_SENSITIVITY','panels':panels,'scope':'Predeclared RAW_CHAR representation sensitivity only; no actual glyph atoms, vowels, omission, source meaning or abjad evidence.'})
if __name__=='__main__':
 import sys
 controls() if '--controls' in sys.argv else run()
