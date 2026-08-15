#!/usr/bin/env python3
"""Independent reconstruction of the GDT148 retrieval and null."""
import csv, hashlib, json, random
from collections import Counter, defaultdict
from pathlib import Path
import numpy as np
R=Path(__file__).resolve().parent
SOURCE=R/'gdt062_right_family_inventory.tsv';META=R/'gdt137_herbal_visual_feature_inventory.tsv';INV=R/'gdt148_relation_inventory.tsv';RANKS=R/'gdt148_target_ranks.tsv';NULL=R/'gdt148_null_results.tsv';HOSTS=R/'gdt148_shared_host_candidates.tsv';COUNTER=R/'gdt148_counterexamples.tsv';RESULT=R/'gdt148_result.json';OUT=R/'gdt148_validation.json'
REPS=('PAGE_HOST_IDENTITY','PAGE_HOST_CHAR3','RAW_CHAR3','COMPILER_SIGNATURE');SCOPES=('ALL_SIX','COMPONENT_FOUR','WHOLE_PLANT_TWO');WORLDS=100000;SEED=148140
def read(p):
 with p.open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(x):return hashlib.sha256(json.dumps(x,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
def add3(c,s):
 s='^'+s+'$'
 for i in range(max(1,len(s)-2)):c[s[i:i+3]]+=1
def sim(a,b):
 k=set(a)|set(b);d=sum(max(a[x],b[x]) for x in k)
 return sum(min(a[x],b[x]) for x in k)/d if d else 0
checks=[]
def ck(n,x,d=''):checks.append({'check':n,'pass':bool(x),'detail':d})
meta={x['page']:x for x in read(META)};rels=read(INV);res=json.loads(RESULT.read_text());by=defaultdict(list);f84r=0;other=0
with SOURCE.open(encoding='utf8',newline='') as h:
 for x in csv.DictReader(h,delimiter='\t'):
  if x['page'].startswith('f84r'):f84r+=1;continue
  if x['page'].startswith('f84'):other+=1;continue
  if x['page'] in meta:by[x['page']].append(x)
ck('six_relations',len(rels)==6 and [x['relation_id'] for x in rels]==['MHI002','MHI003','MHI004','MHI005','MHI006','MHI007'])
ck('source_seal',f84r==0 and other==res['f84']['rejected_other_f84_rows'] and len(by)==127)
feat={p:{r:Counter() for r in REPS} for p in by}
for p,rows in by.items():
 for x in rows:
  feat[p]['PAGE_HOST_IDENTITY'][x['page_host']]+=1;add3(feat[p]['PAGE_HOST_CHAR3'],x['page_host']);add3(feat[p]['RAW_CHAR3'],x['token']);feat[p]['COMPILER_SIGNATURE']['|'.join((x['wrapper'],x['inner_d'],x['local_frame'],x['right_family'],x['dy_closure'],x['b3']))]+=1
cands=[];zs=[];raw=[];top6map=[];pub={(x['relation_id'],x['candidate_scope'],x['representation']):x for x in read(RANKS)}
for x in rels:
 s=x['source_page'];t=x['target_page'];tm=meta[t];primary=sorted(p for p,z in meta.items() if p in by and p!=s and z['physical_folio']!=meta[s]['physical_folio'] and z['currier']==tm['currier'] and z['hand']==tm['hand']);profile=[p for p in primary if meta[p]['illustration_profile']==tm['illustration_profile']];cands.append(primary);zi={};ri={};t6={}
 for rep in REPS:
  vals=np.array([sim(feat[s][rep],feat[p][rep]) for p in primary]);mu=float(vals.mean());sd=float(vals.std()) or 1;z=(vals-mu)/sd;zi[rep]=dict(zip(primary,z));ri[rep]=dict(zip(primary,vals));t6[rep]={p:(1+int(np.sum(vals>v+1e-12))<=6) for p,v in zip(primary,vals)}
  for label,pool in (('PRIMARY_CURRIER_HAND',primary),('PROFILE_MATCHED_SENSITIVITY',profile)):
   v=np.array([sim(feat[s][rep],feat[p][rep]) for p in pool]);score=sim(feat[s][rep],feat[t][rep]);rank=1+int(np.sum(v>score+1e-12));tail=float(np.mean(v>=score-1e-12));q=pub[(x['relation_id'],label,rep)]
   ck('rank_'+x['relation_id']+'_'+label+'_'+rep,int(q['candidate_pages'])==len(pool) and abs(float(q['similarity'])-score)<1e-9 and int(q['true_target_rank'])==rank and abs(float(q['inclusive_candidate_tail'])-tail)<1e-9 and int(q['top_six'])==int(rank<=6))
 zs.append(zi);raw.append(ri);top6map.append(t6)
idx={'ALL_SIX':list(range(6)),'COMPONENT_FOUR':[i for i,x in enumerate(rels) if x['relation_class']=='COMPONENT_SIMILARITY'],'WHOLE_PLANT_TWO':[i for i,x in enumerate(rels) if x['relation_class']=='WHOLE_PLANT_SIMILARITY']}
obs_m=np.zeros((3,4));obs_t=np.zeros((3,4),int)
for a,scope in enumerate(SCOPES):
 for b,rep in enumerate(REPS):
  ii=idx[scope];obs_m[a,b]=np.mean([zs[i][rep][rels[i]['target_page']] for i in ii]);obs_t[a,b]=sum(top6map[i][rep][rels[i]['target_page']] for i in ii)
rng=random.Random(SEED);nm=np.zeros((WORLDS,3,4));nt=np.zeros((WORLDS,3,4),int)
for w in range(WORLDS):
 while True:
  draw=[rng.choice(cands[i]) for i in range(6)]
  if len(set(draw))==6:break
 for a,scope in enumerate(SCOPES):
  ii=idx[scope]
  for b,rep in enumerate(REPS):
   nm[w,a,b]=np.mean([zs[i][rep][draw[i]] for i in ii]);nt[w,a,b]=sum(top6map[i][rep][draw[i]] for i in ii)
mm=nm.mean(0);ms=nm.std(0);ms[ms==0]=1;mz=(obs_m-mm)/ms;mnz=(nm-mm)/ms;tm=nt.mean(0);ts=nt.std(0);ts[ts==0]=1;tz=(obs_t-tm)/ts;tnz=(nt-tm)/ts;maxm=mnz.reshape(WORLDS,-1).max(1);maxt=tnz.reshape(WORLDS,-1).max(1);pn={(x['scope'],x['representation']):x for x in read(NULL)}
for a,scope in enumerate(SCOPES):
 for b,rep in enumerate(REPS):
  q=pn[(scope,rep)];exp=[obs_m[a,b],mm[a,b],ms[a,b],mz[a,b],np.mean(nm[:,a,b]>=obs_m[a,b]-1e-12),np.mean(maxm>=mz[a,b]-1e-12),obs_t[a,b],tm[a,b],ts[a,b],tz[a,b],np.mean(nt[:,a,b]>=obs_t[a,b]),np.mean(maxt>=tz[a,b]-1e-12)];got=[float(q[k]) for k in ('true_mean_source_z','null_mean_of_mean_z','null_sd_of_mean_z','true_standardized_mean_z','local_mean_p','max_12_mean_p','true_top_six_count','null_top_six_mean','null_top_six_sd','true_standardized_top_six','local_top_six_p','max_12_top_six_p')]
  ck('null_'+scope+'_'+rep,all(abs(x-y)<1e-8 for x,y in zip(got,exp)))
lead=pn[('COMPONENT_FOUR','PAGE_HOST_IDENTITY')];hits=[x['relation_id'] for x in rels if x['relation_class']=='COMPONENT_SIMILARITY' and int(pub[(x['relation_id'],'PRIMARY_CURRIER_HAND','PAGE_HOST_IDENTITY')]['top_six'])]
ck('hits_exact',hits==res['component_page_host_top_six_hits']==['MHI005','MHI006','MHI007'])
status='COMPONENT_RELATION_PAGE_HOST_RETRIEVAL_INTERESTING_POSTHOC' if len(hits)>=3 and float(lead['max_12_top_six_p'])<=.05 else 'FULL_CORPUS_RELATION_RETRIEVAL_NOT_SUPPORTED';ck('status_exact',res['status']==status)
ck('hosts_nonempty',len(read(HOSTS))>0);ck('counterexamples',len(read(COUNTER))==7)
for group in ('inputs','outputs','documents','implementation'):
 for name,h in res[group].items():ck(group+'_hash_'+name,sha(R/name)==h)
tmp=dict(res);got=tmp.pop('result_content_sha256');ck('result_content_hash',csha(tmp)==got)
ok=all(x['pass'] for x in checks);out={'schema':'GDT148_FULL_CORPUS_RELATION_RETRIEVAL_VALIDATION_V1','status':'PASS_INDEPENDENT_EXACT_RECONSTRUCTION' if ok else 'FAIL','checks_passed':sum(x['pass'] for x in checks),'checks_total':len(checks),'result_sha256':sha(RESULT),'validator_sha256':sha(Path(__file__)),'checks':checks}
OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n',encoding='utf8');print(json.dumps({'status':out['status'],'checks':f"{out['checks_passed']}/{out['checks_total']}"},sort_keys=True));raise SystemExit(0 if ok else 1)
