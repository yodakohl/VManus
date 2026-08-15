#!/usr/bin/env python3
"""Independent reconstruction of GDT142 from published GDT140 matrices."""
import csv, hashlib, json
from pathlib import Path
import numpy as np

R=Path(__file__).resolve().parent
INV=R/'gdt140_herbal_relation_inventory.tsv';PAIR=R/'gdt140_pair_similarities.tsv';ORBIT=R/'gdt140_assignment_orbit.tsv'
RESULT=R/'gdt142_result.json';SCORES=R/'gdt142_normalization_scores.tsv';ASSIGN=R/'gdt142_assignment_scores.tsv';RECIP=R/'gdt142_relation_reciprocity.tsv';NEAR=R/'gdt142_near_optimal_assignments.tsv';COUNTER=R/'gdt142_counterexamples.tsv'
OUT=R/'gdt142_validation.json'
REPS=('PAGE_HOST_IDENTITY','PAGE_HOST_CHAR3','RAW_CHAR3','COMPILER_SIGNATURE')
NORMS=('RAW_SIMILARITY','SOURCE_RANK','TARGET_RANK','MUTUAL_RANK_MEAN','RECIPROCAL_RANK_MEAN','MUTUAL_TOP2')

def read(p):
 with p.open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(x):return hashlib.sha256(json.dumps(x,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
def ranks(v):return np.array([1+sum(y>x+1e-12 for y in v) for x in v],float)
def mats(m):
 sr=np.stack([ranks(m[i]) for i in range(5)]);tr=np.stack([ranks(m[:,j]) for j in range(5)]).T
 return {'RAW_SIMILARITY':m,'SOURCE_RANK':(6-sr)/5,'TARGET_RANK':(6-tr)/5,'MUTUAL_RANK_MEAN':((6-sr)+(6-tr))/10,'RECIPROCAL_RANK_MEAN':.5*(1/sr+1/tr),'MUTUAL_TOP2':((sr<=2)&(tr<=2)).astype(float)},sr,tr

checks=[]
def ck(name,ok,detail=''):
 checks.append({'check':name,'pass':bool(ok),'detail':detail})

rels=read(INV);pairs=read(PAIR);orbit=read(ORBIT);res=json.loads(RESULT.read_text())
src=[x['source_page'] for x in rels];tgt=[x['target_page'] for x in rels]
ck('five_relations',len(rels)==5);ck('hundred_pair_rows',len(pairs)==100);ck('one_twenty_worlds',len(orbit)==120)
ck('sealed_prefix_absent',not any(x.startswith('f84') for x in src+tgt))
maps=[]
for x in orbit:
 d=dict(z.split('->') for z in x['mapping'].split('|'));maps.append([tgt.index(d[s]) for s in src])
ti=next(i for i,x in enumerate(orbit) if x['is_true']=='1')
mm={r:np.zeros((5,5)) for r in REPS}
for x in pairs:mm[x['representation']][src.index(x['source_page']),tgt.index(x['candidate_target_page'])]=float(x['similarity'])

published={(x['representation'],x['normalization']):x for x in read(SCORES)}
zall=[];computed={};ranked={}
for rep in REPS:
 nm,sr,tr=mats(mm[rep]);ranked[rep]=(sr,tr)
 for norm in NORMS:
  v=np.array([sum(nm[norm][i,j] for i,j in enumerate(q))/5 for q in maps]);z=(v-v.mean())/(v.std() or 1)
  computed[(rep,norm)]=(v,z);zall.append(z);p=published[(rep,norm)]
  vals=(float(p['true_score']),float(p['null_mean']),float(p['null_sd']),float(p['true_z']),int(p['inclusive_rank_of_120']),float(p['local_inclusive_p']))
  exp=(float(v[ti]),float(v.mean()),float(v.std()),float(z[ti]),1+int(np.sum(v>v[ti]+1e-12)),float(np.mean(v>=v[ti]-1e-12)))
  ck(f'score_{rep}_{norm}',all(abs(a-b)<1e-9 for a,b in zip(vals[:4],exp[:4])) and vals[4]==exp[4] and abs(vals[5]-exp[5])<1e-9)
mx=np.max(np.stack(zall),axis=0);maxp=float(np.mean(mx>=mx[ti]-1e-12))
ck('max24_exact',abs(maxp-float(res['max_24_inclusive_p']))<1e-12 and all(abs(float(x['max_24_inclusive_p'])-maxp)<1e-12 for x in published.values()))

rec={(x['relation_id'],x['representation']):x for x in read(RECIP)}
for rep in REPS:
 sr,tr=ranked[rep]
 for i,x in enumerate(rels):
  q=rec[(x['relation_id'],rep)]
  ck(f'reciprocity_{rep}_{x["relation_id"]}',int(q['source_rank_of_true_target'])==int(sr[i,i]) and int(q['target_rank_of_true_source'])==int(tr[i,i]) and int(q['mutual_top2'])==int(sr[i,i]<=2 and tr[i,i]<=2))

arows=read(ASSIGN);ck('assignment_row_count',len(arows)==24*120)
for x in arows:
 i=next(k for k,a in enumerate(orbit) if a['assignment_id']==x['assignment_id']);v,z=computed[(x['representation'],x['normalization'])]
 ck(f'assignment_{x["representation"]}_{x["normalization"]}_{x["assignment_id"]}',abs(float(x['score'])-v[i])<1e-9 and abs(float(x['standardized_score'])-z[i])<1e-9 and abs(float(x['max_24_standardized_score'])-mx[i])<1e-9)

v,z=computed[('PAGE_HOST_CHAR3','RECIPROCAL_RANK_MEAN')];w=np.exp(z-z.max());w/=w.sum();entropy=-float(np.sum(w*np.log2(np.maximum(w,1e-300))))
ck('entropy_exact',abs(entropy-float(res['key_variant']['descriptive_assignment_entropy_bits']))<1e-9)
near=read(NEAR);order=sorted(range(120),key=lambda i:(-v[i],orbit[i]['assignment_id']))[:12]
ck('near_order_exact',[x['assignment_id'] for x in near]==[orbit[i]['assignment_id'] for i in order])
char=[published[('PAGE_HOST_CHAR3',n)] for n in NORMS];g1=all(int(x['inclusive_rank_of_120'])<=6 for x in char);g2=maxp<=.05
status='RELATION_ASSIGNMENT_GEOMETRY_ROBUST_WITHIN_EXPOSED_5X5' if g1 and g2 else 'RELATION_ASSIGNMENT_GEOMETRY_SENSITIVE'
ck('status_exact',res['status']==status);ck('gates_exact',res['gates']=={'all_six_page_host_char3_ranks_le_6':g1,'max_24_inclusive_p_le_0_05':g2})
for name,h in res['inputs'].items():ck('input_hash_'+name,sha(R/name)==h)
for name,h in res['outputs'].items():ck('output_hash_'+name,sha(R/name)==h)
for name,h in res['documents'].items():ck('document_hash_'+name,sha(R/name)==h)
for name,h in res['implementation'].items():ck('implementation_hash_'+name,sha(R/name)==h)
tmp=dict(res);got=tmp.pop('result_content_sha256');ck('result_content_hash',csha(tmp)==got)
ck('counterexamples_nonempty',len(read(COUNTER))>=3)
ok=all(x['pass'] for x in checks)
out={'schema':'GDT142_RELATION_ASSIGNMENT_GEOMETRY_VALIDATION_V1','status':'PASS_INDEPENDENT_EXACT_RECONSTRUCTION' if ok else 'FAIL','checks_passed':sum(x['pass'] for x in checks),'checks_total':len(checks),'result_sha256':sha(RESULT),'validator_sha256':sha(Path(__file__)),'checks':checks}
OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n',encoding='utf8')
print(json.dumps({'status':out['status'],'checks':f"{out['checks_passed']}/{out['checks_total']}"},sort_keys=True))
raise SystemExit(0 if ok else 1)
