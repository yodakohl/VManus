#!/usr/bin/env python3
"""Independent retained-score and Voynich reconstruction for GDT289."""
from __future__ import annotations
import csv,hashlib,json,math,random,statistics
from collections import Counter,defaultdict
from pathlib import Path
R=Path(__file__).resolve().parent;RESULT=R/'gdt289_result.json';OUT=R/'gdt289_validation.json';MODELS=('POSITION_CONTEXT','OTHER_POSITION_HOST_BAG','CROSS_HOST_POSITION_TRANSFER');PRIOR=11.;ALPHA=.5
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def csha(v):q=dict(v);q.pop('content_sha256',None);return hashlib.sha256(json.dumps(q,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
def rows(p):
 with Path(p).open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def close(a,b,t=2e-8):return math.isclose(float(a),float(b),rel_tol=0,abs_tol=t)
def bucket(panel,h):return int(hashlib.sha256(f'GDT289_HOST_BUCKET|{panel}|{h}'.encode()).hexdigest()[:16],16)%8
def bk(r):return (r['section'],r['currier'],r['hand'],r['register'],r['within_field_position'],int(r['host_length']),r['page_host'][:1],r['page_host'][-1:])
def trans(profiles,panel,b,positions,wr):
 j=defaultdict(float);den=defaultdict(float)
 for h,pm in profiles.items():
  if bucket(panel,h)==b:continue
  for s in positions:
   if s not in pm:continue
   ns=sum(pm[s].values())
   for t in positions:
    if t==s or t not in pm:continue
    nt=sum(pm[t].values())
    for u,cu in pm[s].items():
     pu=cu/ns;den[s,t,u]+=pu
     for v,cv in pm[t].items():j[s,t,u,v]+=pu*cv/nt
 return j,den
def score(ev,split='physical_folio'):
 panel='VOYNICH_REFERENCE';wr=sorted({r['wrapper'] for r in ev});K=len(wr);pos=sorted({r['within_field_position'] for r in ev});folds=defaultdict(list)
 for i,r in enumerate(ev):folds[r[split]].append(i)
 bits=Counter();top=Counter();pred=[];detail=defaultdict(lambda:[0,0.]);foldout=[]
 for held,tests in sorted(folds.items()):
  train=[i for i,r in enumerate(ev) if r[split]!=held];g=Counter(ev[i]['wrapper'] for i in train);base=defaultdict(Counter);profiles=defaultdict(lambda:defaultdict(Counter))
  for i in train:r=ev[i];base[bk(r)][r['wrapper']]+=1;profiles[r['page_host']][r['within_field_position']][r['wrapper']]+=1
  tab={b:trans(profiles,panel,b,pos,wr) for b in range(8)};fb=Counter();ft=Counter();n=0
  for i in tests:
   r=ev[i];t=r['within_field_position'];h=r['page_host'];other={s:c for s,c in profiles.get(h,{}).items() if s!=t and sum(c.values())};nn=sum(sum(c.values()) for c in other.values())
   if not nn:continue
   bc=base[bk(r)];nb=sum(bc.values());p0={w:(g[w]+ALPHA)/(len(train)+ALPHA*K) for w in wr};pb={w:(bc[w]+PRIOR*p0[w])/(nb+PRIOR) for w in wr};cc=Counter()
   for c in other.values():cc.update(c)
   bag={w:(cc[w]+PRIOR*pb[w])/(nn+PRIOR) for w in wr};j,den=tab[bucket(panel,h)];ff={w:0. for w in wr}
   for s,c in other.items():
    ns=sum(c.values())
    for u,cu in c.items():
     dd=den[s,t,u]+ALPHA*K
     for v in wr:ff[v]+=cu*(j[s,t,u,v]+ALPHA)/dd
   tr={w:(ff[w]+PRIOR*pb[w])/(nn+PRIOR) for w in wr};actual=r['wrapper'];pp={'POSITION_CONTEXT':pb,'OTHER_POSITION_HOST_BAG':bag,'CROSS_HOST_POSITION_TRANSFER':tr}
   for m in MODELS:
    z=-math.log2(pp[m][actual]);bits[m]+=z;fb[m]+=z;ok=int(max(wr,key=lambda w:(pp[m][w],-wr.index(w)))==actual);top[m]+=ok;ft[m]+=ok
   gain=math.log2(tr[actual]/bag[actual]);detail['BUCKET',str(bucket(panel,h))][0]+=1;detail['BUCKET',str(bucket(panel,h))][1]+=gain;detail['POSITION',t][0]+=1;detail['POSITION',t][1]+=gain;pred.append({'actual':actual,'bag':bag,'transfer':tr,'key':(r['physical_folio'],)+bk(r)});n+=1
  for m in MODELS:foldout.append((held,m,n,fb[m],ft[m]))
 return dict(bits),dict(top),pred,detail,foldout
def nulls(pred):
 st=defaultdict(list)
 for i,r in enumerate(pred):st[r['key']].append(i)
 out=[];mob=0
 for world in range(64):
  yy=[r['actual'] for r in pred]
  for key,ids in sorted(st.items(),key=lambda z:repr(z[0])):
   seed=f"GDT289_HELD_WRAPPER_ALIGNMENT|VOYNICH_REFERENCE|{world}|"+'|'.join(map(str,key));rng=random.Random(int(hashlib.sha256(seed.encode()).hexdigest()[:16],16));v=[yy[i] for i in ids];rng.shuffle(v)
   for i,x in zip(ids,v):
    if world==0 and x!=yy[i]:mob+=1
    yy[i]=x
  out.append(sum(math.log2(r['transfer'][y]/r['bag'][y]) for r,y in zip(pred,yy))/len(pred))
 return out,mob
def main():
 checks=[]
 def ck(n,v):checks.append({'check':n,'pass':bool(v)});assert v,n
 d=json.loads((R/'gdt289_design.json').read_text());res=json.loads(RESULT.read_text());pr=rows(R/'gdt289_panel_scores.tsv');fr=rows(R/'gdt289_folio_scores.tsv');dr=rows(R/'gdt289_transfer_breakdown.tsv');nr=rows(R/'gdt289_null_results.tsv');sr=rows(R/'gdt289_voynich_sensitivities.tsv')
 ck('design',d['content_sha256']==csha(d) and d['status']=='CAPACITY_CORRECTED_FROZEN_BEFORE_GDT289_SCORING');mf=rows(R/'gdt289_freeze_manifest.tsv');ck('freeze',len(mf)==5 and all(sha(R/x['artifact'])==x['frozen_sha256'] for x in mf));ck('table_counts',len(pr)==24 and len(nr)==512 and len(sr)==6 and len(dr)>0 and len(fr)>0);native=rows(R/'gdt278_native_event_inventory.tsv');ck('no_f84',not any(x['page'].startswith('f84') or x['locus'].startswith('f84') for x in native));panels={p:[x for x in native if x['control_id']==p] for p in d['panels']};ck('panel_events',all(len(x)==8448 for x in panels.values()))
 for p in d['panels']:
  q=[x for x in pr if x['control_id']==p];ck('panel:'+p,len(q)==3 and len({x['scored_events'] for x in q})==1 and all(close(x['bits_per_event'],float(x['bits'])/int(x['scored_events'])) and close(x['top1_rate'],int(x['top1'])/int(x['scored_events'])) for x in q));f=[x for x in fr if x['control_id']==p];ck('folds:'+p,all(close(next(x for x in q if x['model']==m)['bits'],sum(float(x['bits']) for x in f if x['model']==m)) and int(next(x for x in q if x['model']==m)['top1'])==sum(int(x['top1']) for x in f if x['model']==m) for m in MODELS));ck('nulls:'+p,len([x for x in nr if x['control_id']==p])==64)
 ev=panels['VOYNICH_REFERENCE'];bits,top,pred,det,folds=score(ev);ck('voynich_scored',len(pred)==7347==int(res['voynich_summary']['scored_events']))
 for m in MODELS:
  x=next(q for q in pr if q['control_id']=='VOYNICH_REFERENCE' and q['model']==m);ck('voynich_model:'+m,close(x['bits'],bits[m]) and int(x['top1'])==top[m])
 for held,m,n,b,t in folds:
  x=next(q for q in fr if q['control_id']=='VOYNICH_REFERENCE' and q['held_value']==held and q['model']==m);ck('voynich_fold:'+held+':'+m,int(x['scored_events'])==n and close(x['bits'],b) and int(x['top1'])==t)
 ng,mob=nulls(pred);saved=[float(x['transfer_gain_bits_per_event']) for x in nr if x['control_id']=='VOYNICH_REFERENCE'];ck('voynich_nulls',all(close(a,b) for a,b in zip(ng,saved)));obs=(bits['OTHER_POSITION_HOST_BAG']-bits['CROSS_HOST_POSITION_TRANSFER'])/len(pred);mean=statistics.mean(ng);sd=statistics.pstdev(ng);v=res['voynich_summary'];ck('voynich_summary',close(v['transfer_gain_bits_per_event'],obs) and close(v['null_mean'],mean) and close(v['null_sd'],sd) and int(v['null_mobile_events_world0'])==mob and int(v['positive_host_buckets'])==sum(z[1]>0 for k,z in det.items() if k[0]=='BUCKET') and int(v['positive_positions'])==sum(z[1]>0 for k,z in det.items() if k[0]=='POSITION'))
 for split in ('section','hand'):
  b,t,p,dd,ff=score(ev,split);gain=(b['OTHER_POSITION_HOST_BAG']-b['CROSS_HOST_POSITION_TRANSFER'])/len(p);ck('sensitivity:'+split,close(res['voynich_sensitivity_gains']['HELD_'+split.upper()],gain))
 nullby={p:[float(x['transfer_gain_bits_per_event']) for x in nr if x['control_id']==p] for p in d['panels']};means={p:statistics.mean(nullby[p]) for p in d['panels']};sds={p:statistics.pstdev(nullby[p]) for p in d['panels']};ck('capacity_split',all(sds[p]>0 for p in d['maxT_panels']) and all(sds[p]==0 for p in d['zero_null_variance_panels']));observed={p:(float(next(x for x in pr if x['control_id']==p and x['model']=='OTHER_POSITION_HOST_BAG')['bits'])-float(next(x for x in pr if x['control_id']==p and x['model']=='CROSS_HOST_POSITION_TRANSFER')['bits']))/int(next(x for x in pr if x['control_id']==p)['scored_events']) for p in d['panels']};z={p:(observed[p]-means[p])/sds[p] for p in d['maxT_panels']};wm=[max((nullby[p][i]-means[p])/sds[p] for p in d['maxT_panels']) for i in range(64)];maxp=(1+sum(x>=z['VOYNICH_REFERENCE']-1e-15 for x in wm))/65;ck('max4',close(v['max4_p'],maxp))
 sg=res['voynich_sensitivity_gains'];g={'minimum_capacity':len(pred)>=d['minimum_voynich_scored_events'],'primary_gain_positive':obs>0,'at_least_six_positive_host_buckets':int(v['positive_host_buckets'])>=6,'at_least_three_positive_positions':int(v['positive_positions'])>=3,'max4_p_le_0_05':maxp<=.05,'held_section_gain_positive':sg['HELD_SECTION']>0,'held_hand_gain_positive':sg['HELD_HAND']>0};status=d['decision']['capacity'] if not g['minimum_capacity'] else d['decision']['support'] if all(g.values()) else d['decision']['fail'];ck('decision',g==res['frozen_gates'] and res['status']==status);ck('prohibitions',res['new_corpora']==res['new_architectures']==res['semantic_assignments']==res['page_host_substrings_mined']==0);ck('result_hashes',res['content_sha256']==csha(res) and all(sha(R/k)==v for k,v in res['inputs'].items()) and all(sha(R/k)==v for k,v in res['documents'].items()) and all(sha(R/k)==v for k,v in res['implementation'].items()) and all(sha(R/k)==v for k,v in res['outputs'].items()));ck('f84',res['f84']['input_files']==0 and not any(v for k,v in res['f84'].items() if k!='input_files'))
 out={'schema':'GDT289_CROSS_HOST_WRAPPER_POSITION_TRANSFER_VALIDATION_V1','status':'PASS','validation_scope':'INDEPENDENT_VOYNICH_ALL_FOLDS_SENSITIVITIES_AND_64_NULLS_PLUS_ALL_PANEL_ACCOUNTING_HASHES_AND_DECISION','checks_passed':len(checks),'checks_total':len(checks),'checks':checks,'result_sha256':sha(RESULT),'validator_sha256':sha(Path(__file__))};out['content_sha256']=csha(out);OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':'PASS','checks':len(checks)},sort_keys=True))
if __name__=='__main__':main()
