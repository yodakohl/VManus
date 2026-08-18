#!/usr/bin/env python3
"""Independently replay GDT329, including all 8,192 worlds."""
import csv,hashlib,json,math,random
from collections import Counter,defaultdict
from pathlib import Path
R=Path(__file__).resolve().parent;RESULT=R/'gdt329_result.json';OUT=R/'gdt329_validation.json';WORLDS=8192;SEED=329
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def can(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
def read(n):
 with (R/n).open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def main():
 checks=[]
 def ck(n,c):
  if not c:raise AssertionError(n)
  checks.append(n)
 res=json.loads(RESULT.read_text());stored=res.pop('content_sha256');ck('content',stored==can(res));rows=read('gdt327_joint_tuple_interlinear.tsv');ck('source',len(rows)==8448 and not any(x['page'].startswith('f84') or x['locus'].startswith('f84') for x in rows));fields=defaultdict(list)
 for x in rows:fields[(x['page'],x['locus'],x['field_ordinal'])].append(x)
 atlas=read('gdt328_formula_atlas.tsv');occ=read('gdt328_formula_occurrences.tsv');scores=read('gdt329_formula_position_scores.tsv');by=defaultdict(list)
 for x in occ:by[x['formula_id']].append((x['page'],x['locus'],x['field_ordinal']))
 base=defaultdict(Counter);strata=defaultdict(list)
 for k,v in fields.items():base[(len(v),v[0]['register'])][k[2]]+=1;strata[(len(v),v[0]['register'])].append(k)
 def stat(a,assign=None):
  z=by[a['formula_id']];num=var=0.
  for i in range(len(z)):
   for j in range(i+1,len(z)):
    ki,kj=z[i],z[j];vi,vj=fields[ki],fields[kj];pi=base[(len(vi),vi[0]['register'])];pj=base[(len(vj),vj[0]['register'])];ni=sum(pi.values());nj=sum(pj.values());e=sum(pi[o]/ni*pj[o]/nj for o in set(pi)|set(pj));num+=((assign[ki] if assign else ki[2])==(assign[kj] if assign else kj[2]))-e;var+=e*(1-e)
  return num/math.sqrt(var) if var else 0.
 obs=[stat(a) for a in atlas];hits=[0]*len(atlas);mx=[];rng=random.Random(SEED)
 for w in range(WORLDS):
  assign={}
  for s,keys in sorted(strata.items()):
   vals=[k[2] for k in keys];rng.shuffle(vals)
   for k,o in zip(keys,vals):assign[k]=o
  vals=[stat(a,assign) for a in atlas];mx.append(max(vals))
  for i,v in enumerate(vals):hits[i]+=v>=obs[i]-1e-12
 ck('score_rows',len(scores)==44)
 sd={x['formula_id']:x for x in scores}
 for i,(a,o) in enumerate(zip(atlas,obs)):
  x=sd[a['formula_id']];ck(f'score_{i}',abs(float(x['pair_agreement_z'])-o)<1e-11 and abs(float(x['local_inclusive_p'])-(hits[i]+1)/(WORLDS+1))<1e-11 and abs(float(x['max44_inclusive_p'])-(sum(v>=o-1e-12 for v in mx)+1)/(WORLDS+1))<1e-11)
 null=read('gdt329_null.tsv');ck('null',len(null)==8193 and all(abs(float(null[i+1]['max_pair_agreement_z'])-mx[i])<1e-11 for i in range(WORLDS)));lead=max(range(len(obs)),key=lambda i:obs[i]);ck('lead',res['lead']['formula_id']==atlas[lead]['formula_id'] and abs(float(res['lead']['max44_inclusive_p'])-(sum(v>=obs[lead]-1e-12 for v in mx)+1)/(WORLDS+1))<1e-11);ck('status',res['status']=='FORMULA_POSITION_SPECIFICITY_NOT_ABOVE_SEARCH_NULL')
 ck('inputs',all(res['inputs'][n]==sha(R/n) for n in res['inputs']));ck('docs',all(res['documents'][n]==sha(R/n) for n in res['documents']));ck('impl',all(res['implementation'][n]==sha(R/n) for n in res['implementation']));ck('outputs',all(res['outputs'][n]==sha(R/n) for n in res['outputs']));ck('f84',res['f84']['input_rows']==0 and not any(v for k,v in res['f84'].items() if k!='input_rows'))
 v={'schema':'GDT329_VALIDATION_V1','status':'PASS','scope':'INDEPENDENT_ALL_CANDIDATE_STATISTICS_ALL_PERMUTATION_WORLDS_ALL_PVALUES_HASHES','checks_passed':len(checks),'result_sha256':sha(RESULT),'f84_rows':0};v['content_sha256']=can(v);OUT.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':'PASS','checks':len(checks)},sort_keys=True))
if __name__=='__main__':main()
