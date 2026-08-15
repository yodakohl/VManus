#!/usr/bin/env python3
"""Independent exact reconstruction of GDT147 from GDT140 matrices."""
import csv, hashlib, json
from pathlib import Path
import numpy as np
R=Path(__file__).resolve().parent
INV=R/'gdt140_herbal_relation_inventory.tsv';PAIR=R/'gdt140_pair_similarities.tsv';ORBIT=R/'gdt140_assignment_orbit.tsv';RESULT=R/'gdt147_result.json'
EDGES=R/'gdt147_edge_stability.tsv';BEST=R/'gdt147_best_assignments.tsv';SWAP=R/'gdt147_swap_diagnostics.tsv';COUNTER=R/'gdt147_counterexamples.tsv';OUT=R/'gdt147_validation.json'
NORMS=('RAW_SIMILARITY','SOURCE_RANK','TARGET_RANK','MUTUAL_RANK_MEAN','RECIPROCAL_RANK_MEAN','MUTUAL_TOP2')
def read(p):
 with p.open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(x):return hashlib.sha256(json.dumps(x,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
def ranks(v):return np.array([1+sum(y>x+1e-12 for y in v) for x in v],float)
checks=[]
def ck(n,x,d=''):checks.append({'check':n,'pass':bool(x),'detail':d})
rels=read(INV);pairs=read(PAIR);orbit=read(ORBIT);res=json.loads(RESULT.read_text())
s=[x['source_page'] for x in rels];t=[x['target_page'] for x in rels]
ck('inventory_exact',len(rels)==5 and [x['relation_id'] for x in rels]==['MHI002','MHI003','MHI004','MHI006','MHI007'])
ck('orbit_exact',len(orbit)==120 and sum(x['is_true']=='1' for x in orbit)==1)
ck('f84_absent',not any(x.startswith('f84') for x in s+t))
maps=[]
for x in orbit:
 d=dict(z.split('->') for z in x['mapping'].split('|'));maps.append([t.index(d[q]) for q in s])
ti=next(i for i,x in enumerate(orbit) if x['is_true']=='1');si=next(i for i,q in enumerate(maps) if q==[0,1,4,3,2])
m=np.zeros((5,5))
for x in pairs:
 if x['representation']=='PAGE_HOST_CHAR3':m[s.index(x['source_page']),t.index(x['candidate_target_page'])]=float(x['similarity'])
sr=np.stack([ranks(m[i]) for i in range(5)]);tr=np.stack([ranks(m[:,j]) for j in range(5)]).T
nm={'RAW_SIMILARITY':m,'SOURCE_RANK':(6-sr)/5,'TARGET_RANK':(6-tr)/5,'MUTUAL_RANK_MEAN':((6-sr)+(6-tr))/10,'RECIPROCAL_RANK_MEAN':.5*(1/sr+1/tr),'MUTUAL_TOP2':((sr<=2)&(tr<=2)).astype(float)}
pub_best={x['normalization']:x for x in read(BEST)};pub_swap={x['normalization']:x for x in read(SWAP)}
bm=np.zeros(5);tm=np.zeros(5);ab=np.zeros(5,int);xb=np.zeros(5,int)
for norm in NORMS:
 vals=np.array([sum(nm[norm][i,j] for i,j in enumerate(q))/5 for q in maps]);mx=float(vals.max());bi=[i for i,v in enumerate(vals) if abs(v-mx)<=1e-12];order=sorted(range(120),key=lambda i:(-vals[i],orbit[i]['assignment_id']))[:5]
 p=pub_best[norm]
 ck('best_'+norm,abs(float(p['best_score'])-mx)<1e-9 and int(p['tied_best_count'])==len(bi) and p['best_assignment_ids']=='|'.join(orbit[i]['assignment_id'] for i in bi) and int(p['true_rank_of_120'])==1+int(np.sum(vals>vals[ti]+1e-12)))
 q=pub_swap[norm];delta=float(vals[ti]-vals[si]);winner='TRUE' if delta>1e-12 else 'SWAPPED' if delta < -1e-12 else 'TIE'
 ck('swap_'+norm,abs(float(q['true_score'])-vals[ti])<1e-9 and abs(float(q['swapped_score'])-vals[si])<1e-9 and abs(float(q['true_minus_swapped'])-delta)<1e-9 and q['winner']==winner)
 for j in range(5):
  mass=sum(maps[k][j]==j for k in bi)/len(bi);top=sum(maps[k][j]==j for k in order)/5
  bm[j]+=mass/6;tm[j]+=top/6;ab[j]+=int(mass>0);xb[j]+=int(mass==1)
pe={x['relation_id']:x for x in read(EDGES)}
for i,x in enumerate(rels):
 p=pe[x['relation_id']];cl='STABLE_BACKBONE_EDGE' if bm[i]>=.75 and tm[i]>=.60 else 'EXCHANGEABLE_OR_UNSTABLE_EDGE'
 ck('edge_'+x['relation_id'],abs(float(p['best_assignment_inclusion_mass'])-bm[i])<1e-9 and abs(float(p['top5_inclusion_mass'])-tm[i])<1e-9 and int(p['normalizations_with_any_best_inclusion'])==ab[i] and int(p['normalizations_with_all_best_inclusion'])==xb[i] and p['descriptive_class']==cl)
stable=[x['relation_id'] for x in rels if pe[x['relation_id']]['descriptive_class']=='STABLE_BACKBONE_EDGE'];unstable=[x['relation_id'] for x in rels if pe[x['relation_id']]['descriptive_class']!='STABLE_BACKBONE_EDGE']
ck('backbone_exact',stable==res['stable_backbone_edges']==['MHI002','MHI003','MHI006'])
ck('unstable_exact',unstable==res['exchangeable_or_unstable_edges']==['MHI004','MHI007'])
ck('status_exact',res['status']=='PAGE_HOST_CHAR3_THREE_EDGE_BACKBONE_TWO_TARGETS_EXCHANGEABLE')
ck('counterexamples',len(read(COUNTER))==5)
for group in ('inputs','outputs','documents','implementation'):
 for name,h in res[group].items():ck(group+'_hash_'+name,sha(R/name)==h)
tmp=dict(res);got=tmp.pop('result_content_sha256');ck('result_content_hash',csha(tmp)==got)
ok=all(x['pass'] for x in checks)
out={'schema':'GDT147_RELATION_BACKBONE_STABILITY_VALIDATION_V1','status':'PASS_INDEPENDENT_EXACT_RECONSTRUCTION' if ok else 'FAIL','checks_passed':sum(x['pass'] for x in checks),'checks_total':len(checks),'result_sha256':sha(RESULT),'validator_sha256':sha(Path(__file__)),'checks':checks}
OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n',encoding='utf8')
print(json.dumps({'status':out['status'],'checks':f"{out['checks_passed']}/{out['checks_total']}"},sort_keys=True))
raise SystemExit(0 if ok else 1)
