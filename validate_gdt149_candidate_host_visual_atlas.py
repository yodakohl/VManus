#!/usr/bin/env python3
"""Independent exact reconstruction of GDT149."""
import csv,hashlib,json,random
from collections import defaultdict
from pathlib import Path
import numpy as np
R=Path(__file__).resolve().parent;SOURCE=R/'gdt062_right_family_inventory.tsv';VIS=R/'gdt137_herbal_visual_feature_inventory.tsv';ATLAS=R/'gdt149_candidate_host_visual_atlas.tsv';OCC=R/'gdt149_candidate_host_occurrences.tsv';COUNTER=R/'gdt149_counterexamples.tsv';RESULT=R/'gdt149_result.json';OUT=R/'gdt149_validation.json'
HOSTS=('pch','olo','kor','oko');FEATURES=('DAISY_CUP','BROAD_CALYX','GRASS','ROOT_PLATFORM','LEAVES_ONE_SIDE','FUSED_PARALLEL_LEAVES','BULB_OR_TUBER_ROOT','LARGE_OR_EXTENSIVE_ROOT','MULTIPLE_PLANTS','BLUE_FLOWERS_OR_BUDS','FINGERED_OR_FRILLED_LEAVES','MULTIPLE_STEMS_OR_STALKS');WORLDS=100000;SENS=50000;SEED=149148;ORIGIN={'pch':('f50r','f6r'),'olo':('f19r','f2v'),'kor':('f90r1','f3v'),'oko':('f90r1','f3v')}
def read(p):
 with p.open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(x):return hashlib.sha256(json.dumps(x,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
def groups(rows):
 g=defaultdict(list)
 for i,x in enumerate(rows):g[(x['currier'],x['hand'],x['illustration_profile'])].append(i)
 return list(g.values())
def calc(X,Y,g,n,seed):
 e=np.zeros((len(X),Y.shape[1]))
 for ii in g:e+=X[:,ii].sum(1)[:,None]*Y[ii].mean(0)[None,:]
 o=X@Y-e;r=random.Random(seed);z=np.zeros((n,len(X),Y.shape[1]),np.float32);base=np.arange(len(Y))
 for w in range(n):
  p=base.copy()
  for ii in g:q=ii[:];r.shuffle(q);p[ii]=q
  z[w]=X@Y[p]-e
 return o,z
checks=[]
def ck(n,x,d=''):checks.append({'check':n,'pass':bool(x),'detail':d})
vis=read(VIS);pages=[x['page'] for x in vis];res=json.loads(RESULT.read_text());by=defaultdict(list);f84r=0;other=0
with SOURCE.open(encoding='utf8',newline='') as h:
 for x in csv.DictReader(h,delimiter='\t'):
  if x['page'].startswith('f84r'):f84r+=1;continue
  if x['page'].startswith('f84'):other+=1;continue
  if x['page'] in pages and x['page_host'] in HOSTS:by[x['page_host']].append(x)
ck('panel',len(vis)==127 and not any(p.startswith('f84') for p in pages));ck('source_seal',f84r==0 and other==res['f84']['rejected_other_f84_rows'])
X=np.array([[any(x['page']==p for x in by[h]) for p in pages] for h in HOSTS],float);Y=np.array([[int(x[f]) for f in FEATURES] for x in vis],float);obs,null=calc(X,Y,groups(vis),WORLDS,SEED);mu=null.mean(0);sd=null.std(0);sd[sd==0]=1;z=(obs-mu)/sd;mx=((null-mu)/sd).reshape(WORLDS,-1).max(1);sens={}
for a,h in enumerate(HOSTS):
 keep=[i for i,p in enumerate(pages) if p not in ORIGIN[h]];rv=[vis[i] for i in keep];oo,nn=calc(X[a:a+1,keep],Y[keep],groups(rv),SENS,SEED+100+a);sens[h]=(oo[0],nn[:,0,:],X[a,keep],Y[keep])
pub={(x['page_host'],x['visual_feature']):x for x in read(ATLAS)}
for a,h in enumerate(HOSTS):
 for b,f in enumerate(FEATURES):
  q=pub[(h,f)];so,sn,sx,sy=sens[h];local=float(np.mean(null[:,a,b]>=obs[a,b]-1e-12));maxp=float(np.mean(mx>=z[a,b]-1e-12));sp=float(np.mean(sn[:,b]>=so[b]-1e-12));label='INTERESTING_EXPLORATORY' if maxp<=.05 else 'PROVISIONAL_POSTSELECTED' if local<=.05 and so[b]>0 else 'WEAK' if local<=.10 else 'NO_SIGNAL'
  got=[float(q[k]) for k in ('within_stratum_effect','standardized_effect_z','local_enrichment_p','max_48_p','endpoint_excluded_effect','endpoint_excluded_local_p')];exp=[obs[a,b],z[a,b],local,maxp,so[b],sp]
  ck('cell_'+h+'_'+f,all(abs(x-y)<1e-8 for x,y in zip(got,exp)) and int(q['host_pages'])==int(X[a].sum()) and int(q['host_feature_positive_pages'])==int(np.sum(X[a]*Y[:,b])) and q['label']==label)
lead=pub[('kor','BULB_OR_TUBER_ROOT')];ck('lead_exact',res['lead']['page_host']=='kor' and res['lead']['visual_feature']=='BULB_OR_TUBER_ROOT' and res['status']=='KOR_BULB_OR_TUBER_ROOT_PROVISIONAL_POSTSELECTED_SEED')
ck('occurrence_count',len(read(OCC))==sum(len(x) for x in by.values()));ck('counterexamples',len(read(COUNTER))==8)
for group in ('inputs','outputs','documents','implementation'):
 for name,h in res[group].items():ck(group+'_hash_'+name,sha(R/name)==h)
tmp=dict(res);got=tmp.pop('result_content_sha256');ck('result_content_hash',csha(tmp)==got);ok=all(x['pass'] for x in checks);out={'schema':'GDT149_CANDIDATE_HOST_VISUAL_ATLAS_VALIDATION_V1','status':'PASS_INDEPENDENT_EXACT_RECONSTRUCTION' if ok else 'FAIL','checks_passed':sum(x['pass'] for x in checks),'checks_total':len(checks),'result_sha256':sha(RESULT),'validator_sha256':sha(Path(__file__)),'checks':checks};OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':out['status'],'checks':f"{out['checks_passed']}/{out['checks_total']}"},sort_keys=True));raise SystemExit(0 if ok else 1)
