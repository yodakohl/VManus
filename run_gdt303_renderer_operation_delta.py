#!/usr/bin/env python3
"""Run frozen GDT303 renderer-operation position-delta test."""
import csv,hashlib,itertools,json,math,statistics
from collections import Counter,defaultdict
from pathlib import Path
R=Path(__file__).resolve().parent;D=R/'gdt303_design.json';SOURCE=R/'gdt278_native_event_inventory.tsv';METHOD=R/'GDT303_RENDERER_OPERATION_POSITION_DELTA_METHOD.md';REPORT=R/'GDT303_RENDERER_OPERATION_POSITION_DELTA_REPORT.md';OPS=R/'gdt303_operation_scores.tsv';PAIRS=R/'gdt303_pair_deltas.tsv';NULL=R/'gdt303_null_max.tsv';COUNTER=R/'gdt303_counterexamples.tsv';RESULT=R/'gdt303_result.json';Y=('FIRST','MIDDLE','LAST')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def can(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
def rcan(v):q=dict(v);q.pop('content_sha256',None);return can(q)
def read(p):
 with Path(p).open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def write(p,rows):
 fs=[]
 for x in rows:
  for k in x:
   if k not in fs:fs.append(k)
 with Path(p).open('w',encoding='utf8',newline='') as h:w=csv.DictWriter(h,fs,delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
def out(x):
 i=int(x['group_index']);n=int(x['group_count']);return 'FIRST' if i==1 else 'LAST' if i==n else 'MIDDLE'
def population(rows):
 b=[x for x in rows if x['control_id']=='VOYNICH_REFERENCE' and int(x['group_count'])>=2];hf=defaultdict(set);sf=defaultdict(set)
 for x in b:hf[x['page_host']].add(x['physical_folio']);sf[x['source_surface_sha256']].add(x['physical_folio'])
 return [x for x in b if len(hf[x['page_host']])>1 and len(sf[x['source_surface_sha256']])>1]
def pairs(E,F):
 forms=defaultdict(lambda:defaultdict(list))
 for x in E:forms[x['page_host']][x['source_surface_sha256']].append(x)
 ans=[]
 for h,D in forms.items():
  ok=[]
  for s,v in D.items():
   if len(v)>=5 and len({x['physical_folio'] for x in v})>=3:ok.append((s,tuple(v[0][k] for k in F),v))
  for a,b in itertools.combinations(ok,2):
   diff=[i for i,(x,z) in enumerate(zip(a[1],b[1])) if x!=z]
   if len(diff)!=1:continue
   i=diff[0];va,vb=a[1][i],b[1][i]
   if va in ('NONE','0') and vb not in ('NONE','0'):src,tgt=a,b
   elif vb in ('NONE','0') and va not in ('NONE','0'):src,tgt=b,a
   elif va<vb:src,tgt=a,b
   else:src,tgt=b,a
   cs=Counter(out(x) for x in src[2]);ct=Counter(out(x) for x in tgt[2]);delta=tuple(ct[z]/len(tgt[2])-cs[z]/len(src[2]) for z in Y);ans.append({'operation':f'{F[i]}:{src[1][i]}>{tgt[1][i]}','field':F[i],'source_value':src[1][i],'target_value':tgt[1][i],'page_host':h,'source_surface_sha256':src[0],'target_surface_sha256':tgt[0],'source_events':len(src[2]),'target_events':len(tgt[2]),'delta':delta})
 return ans
def host_vectors(P):
 q=defaultdict(list)
 for x in P:q[(x['operation'],x['page_host'])].append(x['delta'])
 return {k:tuple(sum(v[i] for v in z)/len(z) for i in range(3)) for k,z in q.items()}
def evaluate(V,op,signs=None):
 H=sorted(h for o,h in V if o==op);Q={h:tuple((signs.get(h,1) if signs else 1)*x for x in V[(op,h)]) for h in H};s0=s1=0;correct=0;fold=[]
 for h in H:
  tr=[Q[z] for z in H if z!=h];pred=tuple(sum(v[i] for v in tr)/len(tr) for i in range(3));obs=Q[h];e0=sum(x*x for x in obs);e1=sum((x-y)**2 for x,y in zip(obs,pred));s0+=e0;s1+=e1;dot=sum(x*y for x,y in zip(obs,pred));correct+=dot>0;fold.append((h,obs,pred,dot,e0-e1))
 return {'hosts':len(H),'baseline_sse':s0,'model_sse':s1,'gain':s0-s1,'correct':correct,'fold':fold}
def sign(op,h,w,seed):return 1 if int(hashlib.sha256(f'{seed}|{w}|{op}|{h}'.encode()).hexdigest()[:16],16)&1 else -1
def main():
 d=json.loads(D.read_text());assert d['content_sha256']==rcan(d) and d['status']=='FROZEN_BEFORE_GDT303_POSITION_SCORING';rows=read(SOURCE);assert not any(x['page'].startswith('f84') or x['locus'].startswith('f84') for x in rows);P=pairs(population(rows),d['renderer_fields']);cap={x['operation']:x for x in read(R/'gdt303_capacity.tsv')};powered=sorted(o for o,x in cap.items() if x['capacity']=='POWERED');V=host_vectors(P);obs={o:evaluate(V,o) for o in powered};N={o:[] for o in powered}
 for w in range(d['null_worlds']):
  for o in powered:
   H=[h for q,h in V if q==o];N[o].append(evaluate(V,o,{h:sign(o,h,w,d['null_seed']) for h in H})['gain'])
 means={o:statistics.mean(N[o]) for o in powered};sds={o:statistics.pstdev(N[o]) for o in powered};z={o:(obs[o]['gain']-means[o])/sds[o] for o in powered if sds[o]};wm=[max((N[o][w]-means[o])/sds[o] for o in z) for w in range(d['null_worlds'])];oprows=[]
 for o in powered:
  q=obs[o];lp=(1+sum(v>=q['gain']-1e-15 for v in N[o]))/(1+d['null_worlds']);mp=(1+sum(v>=z[o]-1e-15 for v in wm))/(1+d['null_worlds']) if o in z else 1.;acc=q['correct']/q['hosts'];cl=d['decision']['transfer'] if q['gain']>0 and acc>=d['decision']['minimum_direction_accuracy'] and mp<=d['decision']['max_family_p_le'] else d['decision']['weak'] if q['gain']>0 else d['decision']['fail'];field,change=o.split(':',1);a,b=change.split('>');oprows.append({'operation':o,'field':field,'source_value':a,'target_value':b,'pairs':cap[o]['pairs'],'hosts':q['hosts'],'baseline_sse':f"{q['baseline_sse']:.12f}",'model_sse':f"{q['model_sse']:.12f}",'sse_gain':f"{q['gain']:.12f}",'direction_correct_hosts':q['correct'],'direction_accuracy':f'{acc:.12f}','mean_delta_first':f"{sum(V[(o,h)][0] for q0,h in V if q0==o)/q['hosts']:.12f}",'mean_delta_middle':f"{sum(V[(o,h)][1] for q0,h in V if q0==o)/q['hosts']:.12f}",'mean_delta_last':f"{sum(V[(o,h)][2] for q0,h in V if q0==o)/q['hosts']:.12f}",'null_mean_gain':f'{means[o]:.12f}','null_sd_gain':f'{sds[o]:.12f}','local_p':f'{lp:.12f}','max_family_p':f'{mp:.12f}','classification':cl})
 pairrows=[]
 for x in P:
  if x['operation'] not in powered:continue
  pairrows.append({k:x[k] for k in ('operation','field','source_value','target_value','page_host','source_surface_sha256','target_surface_sha256','source_events','target_events')}|{'delta_first':f"{x['delta'][0]:.12f}",'delta_middle':f"{x['delta'][1]:.12f}",'delta_last':f"{x['delta'][2]:.12f}"})
 nullrows=[{'world_index':w,'max_standardized_gain':f'{wm[w]:.12f}'} for w in range(d['null_worlds'])];cc=Counter(x['classification'] for x in oprows);status='RENDERER_OPERATION_POSITION_DELTAS_FOUND' if cc[d['decision']['transfer']] else 'NO_TRANSFERRED_RENDERER_DELTA';counter=[{'counterexample_id':'C01','finding':'Pairs are restricted to frequent exact forms differing one parsed renderer field.','impact':'Results do not cover rare forms or multi-field changes.'},{'counterexample_id':'C02','finding':'Operation directions between two nonneutral values use lexical field-value order.','impact':'Only consistent signed prediction under that frozen convention is evidential.'},{'counterexample_id':'C03','finding':'Role deltas are physical FIRST/MIDDLE/LAST probabilities.','impact':'No grammatical or semantic function follows.'},{'counterexample_id':'C04','finding':'Multiple compatible contexts within a host are averaged.','impact':'Context-specific reversals can be hidden by the host mean.'},{'counterexample_id':'C05','finding':'The family was selected by score-blind support but follows exposed GDT302.','impact':'This is a targeted mechanistic successor, not pristine discovery.'},{'counterexample_id':'C06','finding':'No f84 row occurs in the frozen source.','impact':'The seal remains intact.'}];write(OPS,sorted(oprows,key=lambda x:-float(x['sse_gain'])));write(PAIRS,pairrows);write(NULL,nullrows);write(COUNTER,counter)
 top=sorted(oprows,key=lambda x:-float(x['sse_gain']));report=['# GDT303 — matched renderer-operation position deltas','',f'Status: **{status}**.','',f"Among {len(powered)} score-blind powered operations, classifications are `{json.dumps(cc,sort_keys=True)}`.",'','| operation | hosts | mean delta F/M/L | SSE gain | direction | max p | class |','|---|---:|---:|---:|---:|---:|---|']
 for x in top:report.append(f"| `{x['operation']}` | {x['hosts']} | {float(x['mean_delta_first']):+.3f}/{float(x['mean_delta_middle']):+.3f}/{float(x['mean_delta_last']):+.3f} | {float(x['sse_gain']):+.4f} | {float(x['direction_accuracy']):.3f} | {x['max_family_p']} | {x['classification']} |")
 report+=['','## Interpretation','', 'A transferred operation predicts a held host positional delta from other opaque hosts under an exact one-field contrast. Weak and failed operations remain explicit; no operation is assigned a linguistic or semantic function.','','## Claim ceiling','',d['claim_ceiling']+' No f84 row was opened, parsed, retained, joined, or scored.'];REPORT.write_text('\n'.join(report)+'\n');outputs=[OPS,PAIRS,NULL,COUNTER,REPORT];inputs=['gdt303_design.json','gdt303_design_validation.json','gdt303_capacity.tsv','gdt303_freeze_manifest.tsv','gdt278_native_event_inventory.tsv','gdt302_result.json','gdt300_result.json'];res={'schema':'GDT303_RENDERER_OPERATION_POSITION_DELTA_RESULT_V1','status':status,'summary':{'powered_operations':len(powered),'class_counts':dict(cc),'best_operation':top[0]['operation'],'best_sse_gain':top[0]['sse_gain'],'best_max_family_p':top[0]['max_family_p']},'semantic_assignments':0,'claim_ceiling':d['claim_ceiling'],'f84':d['f84'],'inputs':{x:sha(R/x) for x in inputs},'documents':{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)},'implementation':{Path(__file__).name:sha(Path(__file__))},'outputs':{x.name:sha(x) for x in outputs}};res['content_sha256']=rcan(res);RESULT.write_text(json.dumps(res,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':status,'classes':dict(cc),'best':top[0]},sort_keys=True))
if __name__=='__main__':main()
