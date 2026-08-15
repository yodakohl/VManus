#!/usr/bin/env python3
"""Independent refit/null reconstruction for GDT139."""
import csv,hashlib,json
from collections import Counter,defaultdict
from pathlib import Path
import numpy as np
R=Path(__file__).resolve().parent;SOURCE=R/'gdt062_right_family_inventory.tsv';INV=R/'gdt139_identification_token_inventory.tsv';FREEZE=R/'gdt139_prediction.json';SCORE=R/'gdt139_panel_scores.tsv';TOKEN=R/'gdt139_token_scores.tsv';FOLD=R/'gdt139_folio_scores.tsv';CROSS=R/'gdt139_cross_source_scores.tsv';NULL=R/'gdt139_null_results.tsv';RESULT=R/'gdt139_result.json';OUT=R/'gdt139_validation.json';REPS=('PAGE_HOST_IDENTITY','PAGE_HOST_CHAR3','RAW_CHAR3','COMPILER_SIGNATURE');VIS=('DAISY_CUP','BROAD_CALYX','GRASS','ROOT_PLATFORM','LEAVES_ONE_SIDE','FUSED_PARALLEL_LEAVES','BULB_OR_TUBER_ROOT','LARGE_OR_EXTENSIVE_ROOT','MULTIPLE_PLANTS','BLUE_FLOWERS_OR_BUDS','FINGERED_OR_FRILLED_LEAVES','MULTIPLE_STEMS_OR_STALKS');K=7;SHRINK=8.;WORLDS=10000
def read(p):
 with Path(p).open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def csha(x):return hashlib.sha256(json.dumps(x,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
def add3(c,s):
 s='^'+s+'$'
 for i in range(max(1,len(s)-2)):c[s[i:i+3]]+=1.
def dist(a,b):
 k=set(a)|set(b);d=sum(max(a[x],b[x]) for x in k)
 return 1-sum(min(a[x],b[x]) for x in k)/d if d else 0.
def loss(y,p):p=np.clip(p,1e-12,1-1e-12);return -np.log2(np.where(y>0,p,1-p))
checks=[]
def ck(n,v):checks.append({'check':n,'pass':bool(v)});assert v,n
freeze=json.loads(FREEZE.read_text());result=json.loads(RESULT.read_text());rows=read(INV);ck('status',result['status']=='IDENTIFICATION_TOKEN_PAGE_HOST_ASSOCIATION_INTERESTING_EXPLORATORY');ck('panel',len(rows)==173 and Counter(x['panel'] for x in rows)==Counter({'ELV':81,'THP':92}) and not any(x['page'].startswith('f84') for x in rows))
pages=sorted({x['page'] for x in rows});src=[]
with SOURCE.open(encoding='utf8',newline='') as h:
 for x in csv.DictReader(h,delimiter='\t'):
  if x['page'].startswith('f84'):continue
  if x['page'] in pages:src.append(x)
ck('source_pages',set(x['page'] for x in src)==set(pages));bypage=defaultdict(list)
for x in src:bypage[x['page']].append(x)
formal={}
for p in pages:
 b={z:Counter() for z in REPS}
 for x in sorted(bypage[p],key=lambda x:(x['locus'],int(x['group_index']))):b['PAGE_HOST_IDENTITY']['H='+x['page_host']]+=1;add3(b['PAGE_HOST_CHAR3'],x['page_host']);add3(b['RAW_CHAR3'],x['token']);b['COMPILER_SIGNATURE']['|'.join((x['wrapper'],x['inner_d'],x['local_frame'],x['right_family'],x['dy_closure'],x['b3']))]+=1
 formal[p]=b
maxv={k:max(float(x[k] or 0) for x in rows) or 1 for k in ('catalogue_prose_lines','paragraph_starts','formal_lines','formal_groups')};nuis={}
for x in rows:
 n=Counter({'CUR='+x['currier']:1.,'HAND='+x['hand']:1.,'PROFILE='+x['illustration_profile']:1.,'LABEL='+x['catalogue_label_presence']:1.})
 for k in maxv:n[k]=float(x[k] or 0)/maxv[k]
 for k in VIS:n['VIS='+k]=float(x['VIS_'+k])
 nuis[x['panel'],x['page']]=n
stored={(x['panel'],x['representation']):x for x in read(SCORE)};stoken={(x['panel'],x['token'],x['representation']):x for x in read(TOKEN)};sfold={(x['panel'],x['representation'],x['physical_folio']):x for x in read(FOLD)};cache={};obs={};tobs={}
for panel in ('ELV','THP'):
 pr=[x for x in rows if x['panel']==panel]; names=[f'{panel}_{t.upper()}' for t in freeze['eligible_tokens'][panel]];y=np.array([[int(x[n]) for n in names] for x in pr],float);n=len(pr);folios=sorted({x['physical_folio'] for x in pr});fi={f:np.array([i for i,x in enumerate(pr) if x['physical_folio']==f],int) for f in folios}
 def weights(rep=None,train=None):
  train=train or pr;m=np.zeros((n,len(train)))
  for i,t in enumerate(pr):
   q=[]
   for j,s in enumerate(train):
    if s['physical_folio']==t['physical_folio']:continue
    d=dist(nuis[panel,t['page']],nuis[s['panel'],s['page']])+(dist(formal[t['page']][rep],formal[s['page']][rep]) if rep else 0);q.append((d,s['page'],j))
   for d,_,j in sorted(q)[:K]:m[i,j]=1/(.1+d)
  return m
 bw=weights();bp=(bw@y+.5)/(bw.sum(1)[:,None]+1);bl=loss(y,bp);rw={r:weights(r) for r in REPS};ml={r:loss(y,(rw[r]@y+SHRINK*bp)/(rw[r].sum(1)[:,None]+SHRINK)) for r in REPS};cache[panel]=(pr,names,y,bw,rw,bl,fi)
 for rep in REPS:
  gain=float((bl-ml[rep]).sum());obs[panel,rep]=gain;s=stored[panel,rep];ck('score_'+panel+rep,abs(gain-float(s['gain_bits']))<2e-9 and abs(float(s['baseline_bits'])-float(s['held_bits'])-gain)<2e-9)
  for j,name in enumerate(names):g=float((bl[:,j]-ml[rep][:,j]).sum());tobs[panel,name,rep]=g;ck('token_'+panel+name+rep,abs(g-float(stoken[panel,name.split('_',1)[1].lower(),rep]['gain_bits']))<2e-9)
  for f,idx in fi.items():ck('fold_'+panel+rep+f,abs(float((bl[idx]-ml[rep][idx]).sum())-float(sfold[panel,rep,f]['gain_bits']))<2e-9)
# Reconstruct fixed cross-source sensitivity.
shared=['polygonum','primula','scabiosa'];scross={(x['target_panel'],x['training_panel'],x['representation']):x for x in read(CROSS)}
for target,train in (('ELV','THP'),('THP','ELV')):
 pr,names,y,_,_,_,_=cache[target];tr=[x for x in rows if x['panel']==train];tn=[f'{train}_{t.upper()}' for t in freeze['eligible_tokens'][train]];ty=np.array([[int(x[n]) for n in tn] for x in tr],float)
 for rep in REPS:
  yy=[];bb=[];qq=[]
  for tok in shared:
   j=[x.split('_',1)[1].lower() for x in names].index(tok);k=[x.split('_',1)[1].lower() for x in tn].index(tok);w=np.zeros((len(pr),len(tr)));b=np.zeros_like(w)
   for i,t in enumerate(pr):
    z=[]
    for q,s in enumerate(tr):
     if s['physical_folio']==t['physical_folio']:continue
     dn=dist(nuis[target,t['page']],nuis[train,s['page']]);z.append((dn+dist(formal[t['page']][rep],formal[s['page']][rep]),s['page'],q,dn))
    for d,_,q,_ in sorted(z)[:K]:w[i,q]=1/(.1+d)
    for _,_,q,d in sorted(z,key=lambda a:(a[3],a[1]))[:K]:b[i,q]=1/(.1+d)
   base=(b@ty[:,k]+.5)/(b.sum(1)+1);pred=(w@ty[:,k]+SHRINK*base)/(w.sum(1)+SHRINK);yy.append(y[:,j]);bb.append(base);qq.append(pred)
  yy=np.array(yy).T;bb=np.array(bb).T;qq=np.array(qq).T;g=float((loss(yy,bb)-loss(yy,qq)).sum());ck('cross_'+target+rep,abs(g-float(scross[target,train,rep]['gain_bits']))<2e-9)
# Shared null.
local=Counter();max4=Counter();glob=0;tlocal=Counter();tmax=0;rng=np.random.default_rng(139001)
for _ in range(WORLDS):
 wg={};wt=[]
 for panel in ('ELV','THP'):
  pr,names,y,bw,rw,_,_=cache[panel];py=y.copy();strata=defaultdict(list)
  for i,x in enumerate(pr):strata[x['currier'],x['hand'],x['illustration_profile']].append(i)
  for idx in strata.values():idx=np.array(idx,int);py[idx]=py[rng.permutation(idx)]
  bp=(bw@py+.5)/(bw.sum(1)[:,None]+1);bl=loss(py,bp)
  for rep in REPS:
   m=loss(py,(rw[rep]@py+SHRINK*bp)/(rw[rep].sum(1)[:,None]+SHRINK));g=float((bl-m).sum());wg[panel,rep]=g;local[panel,rep]+=g>=obs[panel,rep]-1e-12
   for j,name in enumerate(names):v=float((bl[:,j]-m[:,j]).sum());tlocal[panel,name,rep]+=v>=tobs[panel,name,rep]-1e-12;wt.append(v)
  max4[panel]+=max(wg[panel,r] for r in REPS)>=max(obs[panel,r] for r in REPS)-1e-12
 glob+=max(wg.values())>=max(obs.values())-1e-12;tmax+=max(wt)>=max(tobs.values())-1e-12
sn={(x['panel'],x['representation']):x for x in read(NULL)}
for panel in ('ELV','THP'):
 for rep in REPS:
  z=sn[panel,rep];ck('null_'+panel+rep,abs((local[panel,rep]+1)/10001-float(z['local_inclusive_p']))<1e-12 and abs((max4[panel]+1)/10001-float(z['max_four_panel_inclusive_p']))<1e-12 and abs((glob+1)/10001-float(z['max_eight_global_inclusive_p']))<1e-12 and abs((tmax+1)/10001-float(z['max_token_model_inclusive_p']))<1e-12)
ck('row_counts',len(read(SCORE))==8 and len(read(TOKEN))==76 and len(read(CROSS))==8 and len(read(NULL))==8);ck('hashes',all(sha(R/n)==d for n,d in {**result['inputs'],**result['implementation'],**result['outputs'],**result['documents']}.items()));x=dict(result);d=x.pop('result_content_sha256');ck('content',csha(x)==d);ck('f84',result['f84']['all_rows_rejected_before_retention'] and not result['f84']['new_f84r_access']);v={'schema':'GDT139_VALIDATION_V1','status':'PASS_INDEPENDENT_PANEL_REFIT_CROSS_SOURCE_AND_NULL','checks':len(checks),'passed':sum(x['pass'] for x in checks),'result_sha256':sha(RESULT),'validator_sha256':sha(Path(__file__)),'check_rows':checks};OUT.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n',encoding='utf8');print(json.dumps({'status':v['status'],'checks':v['checks']},sort_keys=True))
