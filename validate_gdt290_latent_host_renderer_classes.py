#!/usr/bin/env python3
"""Independent Voynich reconstruction and retained-panel validation for GDT290."""
from __future__ import annotations
import csv,hashlib,json,math,random,statistics
from collections import Counter,defaultdict
from pathlib import Path
import numpy as np
R=Path(__file__).resolve().parent;RESULT=R/'gdt290_result.json';OUT=R/'gdt290_validation.json';MODELS=('POSITION_CONTEXT','OTHER_POSITION_HOST_BAG','LATENT_HOST_CLASS');PRIOR=11.;ALPHA=.5
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def csha(v):q=dict(v);q.pop('content_sha256',None);return hashlib.sha256(json.dumps(q,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
def rows(p):
 with Path(p).open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def close(a,b,t=2e-8):return math.isclose(float(a),float(b),rel_tol=0,abs_tol=t)
def bucket(h):return int(hashlib.sha256(f'GDT289_HOST_BUCKET|VOYNICH_REFERENCE|{h}'.encode()).hexdigest()[:16],16)%8
def bk(r):return (r['section'],r['currier'],r['hand'],r['register'],r['within_field_position'],int(r['host_length']),r['page_host'][:1],r['page_host'][-1:])
def feat(pm,t,pos,wr):
 z=[]
 for s in pos:
  if s==t:continue
  c=pm.get(s,{});n=sum(c.values());z.extend([c.get(w,0)/n if n else 0. for w in wr]);z.append(0. if n else 1.)
 return np.asarray(z,float)
def model(profiles,b,t,pos,wr,k):
 hh=sorted(h for h,pm in profiles.items() if bucket(h)!=b and t in pm and any(s!=t and sum(c.values()) for s,c in pm.items()))
 if len(hh)<3*k:return None
 X=np.vstack([feat(profiles[h],t,pos,wr) for h in hh]);first=min(range(len(hh)),key=lambda i:(hashlib.sha256(f'GDT290_KMEANS_INIT|VOYNICH_REFERENCE|{t}|{hh[i]}'.encode()).hexdigest(),hh[i]));sel=[first]
 while len(sel)<k:
  dd=np.min(np.sum((X[:,None,:]-X[np.asarray(sel)][None,:,:])**2,axis=2),axis=1);dd[np.asarray(sel)]=-1.;sel.append(sorted((i for i in range(len(hh)) if i not in sel),key=lambda i:(-dd[i],hh[i]))[0])
 cen=X[np.asarray(sel)].copy();lab=np.full(len(hh),-1,int)
 for _ in range(30):
  nl=np.argmin(np.sum((X[:,None,:]-cen[None,:,:])**2,axis=2),axis=1)
  if np.array_equal(nl,lab):break
  lab=nl
  for j in range(k):
   if np.any(lab==j):cen[j]=X[lab==j].mean(axis=0)
 acc=np.zeros((k,len(wr)));nh=np.zeros(k,int)
 for i,h in enumerate(hh):
  c=profiles[h][t];n=sum(c.values());nh[lab[i]]+=1
  for j,w in enumerate(wr):acc[lab[i],j]+=c[w]/n
 return cen,(acc+ALPHA)/(nh[:,None]+ALPHA*len(wr))
def score(ev,k=4,split='physical_folio'):
 wr=sorted({r['wrapper'] for r in ev});K=len(wr);pos=sorted({r['within_field_position'] for r in ev});folds=defaultdict(list)
 for i,r in enumerate(ev):folds[r[split]].append(i)
 bits=Counter();top=Counter();pred=[];detail=defaultdict(lambda:[0,0.]);foldout=[]
 for held,tests in sorted(folds.items()):
  train=[i for i,r in enumerate(ev) if r[split]!=held];g=Counter(ev[i]['wrapper'] for i in train);base=defaultdict(Counter);profiles=defaultdict(lambda:defaultdict(Counter))
  for i in train:r=ev[i];base[bk(r)][r['wrapper']]+=1;profiles[r['page_host']][r['within_field_position']][r['wrapper']]+=1
  mm={(b,t):model(profiles,b,t,pos,wr,k) for b in range(8) for t in pos};fb=Counter();ft=Counter();n=0
  for i in tests:
   r=ev[i];h=r['page_host'];t=r['within_field_position'];b=bucket(h);pm=profiles.get(h,{});other={s:c for s,c in pm.items() if s!=t and sum(c.values())};nn=sum(sum(c.values()) for c in other.values());md=mm[b,t]
   if not nn or md is None:continue
   bc=base[bk(r)];nb=sum(bc.values());p0={w:(g[w]+ALPHA)/(len(train)+ALPHA*K) for w in wr};pb={w:(bc[w]+PRIOR*p0[w])/(nb+PRIOR) for w in wr};cc=Counter()
   for c in other.values():cc.update(c)
   bag={w:(cc[w]+PRIOR*pb[w])/(nn+PRIOR) for w in wr};cen,cp=md;cl=int(np.argmin(np.sum((cen-feat(pm,t,pos,wr)[None,:])**2,axis=1)));cls={w:(nn*cp[cl,j]+PRIOR*pb[w])/(nn+PRIOR) for j,w in enumerate(wr)};actual=r['wrapper'];pp={'POSITION_CONTEXT':pb,'OTHER_POSITION_HOST_BAG':bag,'LATENT_HOST_CLASS':cls}
   for m in MODELS:
    z=-math.log2(pp[m][actual]);bits[m]+=z;fb[m]+=z;ok=int(max(wr,key=lambda w:(pp[m][w],-wr.index(w)))==actual);top[m]+=ok;ft[m]+=ok
   gain=math.log2(cls[actual]/bag[actual]);detail['BUCKET',str(b)][0]+=1;detail['BUCKET',str(b)][1]+=gain;detail['POSITION',t][0]+=1;detail['POSITION',t][1]+=gain;pred.append({'actual':actual,'bag':bag,'class':cls,'key':(r['physical_folio'],)+bk(r)});n+=1
  for m in MODELS:foldout.append((held,m,n,fb[m],ft[m]))
 return dict(bits),dict(top),pred,detail,foldout
def nulls(pred):
 st=defaultdict(list)
 for i,r in enumerate(pred):st[r['key']].append(i)
 out=[];mob=0
 for world in range(64):
  yy=[r['actual'] for r in pred]
  for key,ids in sorted(st.items(),key=lambda z:repr(z[0])):
   seed=f"GDT290_HELD_WRAPPER_ALIGNMENT|VOYNICH_REFERENCE|4|{world}|"+'|'.join(map(str,key));rng=random.Random(int(hashlib.sha256(seed.encode()).hexdigest()[:16],16));v=[yy[i] for i in ids];rng.shuffle(v)
   for i,x in zip(ids,v):
    if world==0 and x!=yy[i]:mob+=1
    yy[i]=x
  out.append(sum(math.log2(r['class'][y]/r['bag'][y]) for r,y in zip(pred,yy))/len(pred))
 return out,mob
def main():
 cc=[]
 def ck(n,v):cc.append({'check':n,'pass':bool(v)});assert v,n
 d=json.loads((R/'gdt290_design.json').read_text());res=json.loads(RESULT.read_text());pr=rows(R/'gdt290_panel_scores.tsv');fr=rows(R/'gdt290_folio_scores.tsv');nr=rows(R/'gdt290_null_results.tsv');sr=rows(R/'gdt290_voynich_sensitivities.tsv');dr=rows(R/'gdt290_class_breakdown.tsv');ck('design',d['content_sha256']==csha(d) and d['status']=='CAPACITY_CORRECTED_FROZEN_BEFORE_GDT290_SCORING');mf=rows(R/'gdt290_freeze_manifest.tsv');ck('freeze',len(mf)==5 and all(sha(R/x['artifact'])==x['frozen_sha256'] for x in mf));ck('counts',len(pr)==24 and len(sr)==4 and len(nr)==448 and len(fr)>0 and len(dr)>0);native=rows(R/'gdt278_native_event_inventory.tsv');ck('no_f84',not any(x['page'].startswith('f84') or x['locus'].startswith('f84') for x in native));panels={p:[x for x in native if x['control_id']==p] for p in d['panels']};ck('events',all(len(x)==8448 for x in panels.values()))
 for p in d['panels']:
  q=[x for x in pr if x['control_id']==p];ck('panel_rows:'+p,len(q)==3 and len({x['scored_events'] for x in q})==1);n=int(q[0]['scored_events']);f=[x for x in fr if x['control_id']==p]
  if n:ck('panel_arithmetic:'+p,all(close(x['bits_per_event'],float(x['bits'])/n) and close(x['top1_rate'],int(x['top1'])/n) for x in q) and all(close(next(x for x in q if x['model']==m)['bits'],sum(float(x['bits']) for x in f if x['model']==m)) for m in MODELS))
  else:ck('panel_capacity:'+p,p=='LATIN_SCHOLASTIC_GRAPHEMATIC' and all(x['bits']=='NA' for x in q))
 ev=panels['VOYNICH_REFERENCE'];bits,top,pred,det,folds=score(ev);ck('voynich_n',len(pred)==7347==int(res['voynich_summary']['scored_events']))
 for m in MODELS:
  x=next(r for r in pr if r['control_id']=='VOYNICH_REFERENCE' and r['model']==m);ck('voynich_model:'+m,close(x['bits'],bits[m]) and int(x['top1'])==top[m])
 for held,m,n,b,t in folds:
  x=next(r for r in fr if r['control_id']=='VOYNICH_REFERENCE' and r['held_value']==held and r['model']==m);ck('voynich_fold:'+held+':'+m,int(x['scored_events'])==n and close(x['bits'],b) and int(x['top1'])==t)
 ng,mob=nulls(pred);saved=[float(x['class_gain_bits_per_event']) for x in nr if x['control_id']=='VOYNICH_REFERENCE'];ck('nulls',len(saved)==64 and all(close(a,b) for a,b in zip(ng,saved)));obs=(bits['OTHER_POSITION_HOST_BAG']-bits['LATENT_HOST_CLASS'])/len(pred);v=res['voynich_summary'];ck('summary',close(v['k4_gain_bits_per_event'],obs) and close(v['null_mean'],statistics.mean(ng)) and close(v['null_sd'],statistics.pstdev(ng)) and int(v['null_mobile_world0'])==mob and int(v['positive_host_buckets'])==sum(z[1]>0 for a,z in det.items() if a[0]=='BUCKET') and int(v['positive_positions'])==sum(z[1]>0 for a,z in det.items() if a[0]=='POSITION'))
 for k in (2,8):
  b,t,p,dd,ff=score(ev,k);gain=(b['OTHER_POSITION_HOST_BAG']-b['LATENT_HOST_CLASS'])/len(p);x=next(x for x in res['voynich_sensitivities'] if x['split']=='HELD_PHYSICAL_FOLIO' and x['k']==k);ck('k_sensitivity:'+str(k),len(p)==x['scored_events'] and close(gain,x['gain_bits_per_event']))
 for split in ('section','hand'):
  b,t,p,dd,ff=score(ev,4,split);gain=(b['OTHER_POSITION_HOST_BAG']-b['LATENT_HOST_CLASS'])/len(p);x=next(x for x in res['voynich_sensitivities'] if x['split']=='HELD_'+split.upper());ck('split_sensitivity:'+split,len(p)==x['scored_events'] and close(gain,x['gain_bits_per_event']))
 nullby={p:[float(x['class_gain_bits_per_event']) for x in nr if x['control_id']==p] for p in d['panels']};cap=[p for p in d['panels'] if nullby[p]];means={p:statistics.mean(nullby[p]) for p in cap};sds={p:statistics.pstdev(nullby[p]) for p in cap};var=[p for p in cap if sds[p]>0];ck('null_family',var==res['null_variable_panels']);observed={p:(float(next(x for x in pr if x['control_id']==p and x['model']=='OTHER_POSITION_HOST_BAG')['bits'])-float(next(x for x in pr if x['control_id']==p and x['model']=='LATENT_HOST_CLASS')['bits']))/int(next(x for x in pr if x['control_id']==p)['scored_events']) for p in cap};z={p:(observed[p]-means[p])/sds[p] for p in var};wm=[max((nullby[p][i]-means[p])/sds[p] for p in var) for i in range(64)];mp=(1+sum(x>=z['VOYNICH_REFERENCE']-1e-15 for x in wm))/65;ck('maxT',close(v['max_variable_family_p'],mp));ss={x['split']:x for x in res['voynich_sensitivities']};g={'minimum_capacity':len(pred)>=d['minimum_voynich_scored_events'],'primary_gain_positive':obs>0,'at_least_six_positive_host_buckets':int(v['positive_host_buckets'])>=6,'at_least_three_positive_positions':int(v['positive_positions'])>=3,'maxT_p_le_0_05':mp<=.05,'held_section_gain_positive':ss['HELD_SECTION']['gain_bits_per_event']>0,'held_hand_gain_positive':ss['HELD_HAND']['gain_bits_per_event']>0};status=d['decision']['capacity'] if not g['minimum_capacity'] else d['decision']['support'] if all(g.values()) else d['decision']['fail'];ck('decision',g==res['frozen_gates'] and res['status']==status);ck('prohibitions',res['new_corpora']==res['new_architectures']==res['semantic_assignments']==res['page_host_substrings_mined']==0);ck('hashes',res['content_sha256']==csha(res) and all(sha(R/k)==v for k,v in res['inputs'].items()) and all(sha(R/k)==v for k,v in res['documents'].items()) and all(sha(R/k)==v for k,v in res['implementation'].items()) and all(sha(R/k)==v for k,v in res['outputs'].items()));ck('f84',res['f84']['input_files']==0 and not any(v for k,v in res['f84'].items() if k!='input_files'));out={'schema':'GDT290_LATENT_HOST_RENDERER_CLASSES_VALIDATION_V1','status':'PASS','validation_scope':'INDEPENDENT_VOYNICH_K2_K4_K8_ALL_FOLDS_SECTION_HAND_AND_64_NULL_RECONSTRUCTION_PLUS_PANEL_ACCOUNTING_HASHES_DECISION','checks_passed':len(cc),'checks_total':len(cc),'checks':cc,'result_sha256':sha(RESULT),'validator_sha256':sha(Path(__file__))};out['content_sha256']=csha(out);OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':'PASS','checks':len(cc)},sort_keys=True))
if __name__=='__main__':main()
