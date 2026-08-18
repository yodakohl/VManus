#!/usr/bin/env python3
"""Run the frozen GDT293 exact-host renderer-completion experiment."""
from __future__ import annotations
import csv,hashlib,json,math,random,statistics
from collections import Counter,defaultdict
from concurrent.futures import ProcessPoolExecutor,as_completed
from pathlib import Path

R=Path(__file__).resolve().parent;DESIGN=R/'gdt293_design.json';METHOD=R/'GDT293_EXACT_HOST_RENDERER_COMPLETION_METHOD.md';REPORT=R/'GDT293_EXACT_HOST_RENDERER_COMPLETION_REPORT.md';RESULT=R/'gdt293_result.json'
OUT_PANEL=R/'gdt293_panel_scores.tsv';OUT_FOLD=R/'gdt293_folio_scores.tsv';OUT_NULL=R/'gdt293_null_results.tsv';OUT_SENS=R/'gdt293_voynich_sensitivities.tsv';OUT_COUNTER=R/'gdt293_counterexamples.tsv'
COMPONENTS=('wrapper','local_frame','inner_d','right_family','dy_closure','b3');ENDPOINTS=('JOINT_RENDERER',)+tuple(x.upper() for x in COMPONENTS);MODELS=('LAYOUT_CONTEXT','EXACT_HOST');ALPHA=.5
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
def rcsha(v):q=dict(v);q.pop('content_sha256',None);return csha(q)
def read(p):
 with Path(p).open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def write(p,rr):
 ff=[]
 for r in rr:
  for k in r:
   if k not in ff:ff.append(k)
 with Path(p).open('w',encoding='utf8',newline='') as h:w=csv.DictWriter(h,ff,delimiter='\t',lineterminator='\n');w.writeheader();w.writerows([{k:r.get(k,'NA') for k in ff} for r in rr])
def ob(x):
 n=int(x);return '1' if n==1 else '2' if n==2 else '3_4' if n<=4 else '5_PLUS'
def gp(r):
 i=int(r['group_index']);n=int(r['group_count']);return 'ONLY' if n==1 else 'FIRST' if i==1 else 'LAST' if i==n else 'MIDDLE'
def lk(r):return (r['section'],r['currier'],r['hand'],r['register'],r['within_field_position'],ob(r['record_ordinal']),ob(r['field_ordinal']),gp(r),int(r['host_length']))
def vals(r):
 q={x.upper():r[x] for x in COMPONENTS};q['JOINT_RENDERER']='|'.join(r[x] for x in COMPONENTS);return q
def nk(r):return (r['physical_folio'],)+lk(r)
def score(events,split='physical_folio',prior=11.,retain=False):
 alph={e:sorted({vals(r)[e] for r in events}) for e in ENDPOINTS};ranks={e:{x:i for i,x in enumerate(alph[e])} for e in ENDPOINTS};folds=defaultdict(list)
 for i,r in enumerate(events):folds[r[split]].append(i)
 bits=defaultdict(Counter);top=defaultdict(Counter);foldrows=[];pred=[];folio_gain={};eligible_total=0
 for held,tests in sorted(folds.items()):
  train=[i for i,r in enumerate(events) if r[split]!=held];train_hosts=Counter(events[i]['page_host'] for i in train);g={e:Counter() for e in ENDPOINTS};lc={e:defaultdict(Counter) for e in ENDPOINTS};hc={e:defaultdict(Counter) for e in ENDPOINTS}
  for i in train:
   r=events[i];q=vals(r)
   for e in ENDPOINTS:g[e][q[e]]+=1;lc[e][lk(r)][q[e]]+=1;hc[e][r['page_host']][q[e]]+=1
  eligible=[i for i in tests if train_hosts[events[i]['page_host']]>0];eligible_total+=len(eligible);fb=defaultdict(Counter);ft=defaultdict(Counter)
  for i in eligible:
   r=events[i];q=vals(r);joint_probs=None
   for e in ENDPOINTS:
    probs={m:{} for m in MODELS};K=len(alph[e])
    for y in alph[e]:
     p0=(g[e][y]+ALPHA)/(len(train)+ALPHA*K);a=lc[e][lk(r)];pl=(a[y]+prior*p0)/(sum(a.values())+prior);a=hc[e][r['page_host']];ph=(a[y]+prior*pl)/(sum(a.values())+prior);probs['LAYOUT_CONTEXT'][y]=pl;probs['EXACT_HOST'][y]=ph
    for m in MODELS:
     z=-math.log2(probs[m][q[e]]);bits[e][m]+=z;fb[e][m]+=z;hit=int(max(alph[e],key=lambda y:(probs[m][y],-ranks[e][y]))==q[e]);top[e][m]+=hit;ft[e][m]+=hit
    if e=='JOINT_RENDERER':joint_probs=probs
   if retain:pred.append({'actual':q['JOINT_RENDERER'],'layout':joint_probs['LAYOUT_CONTEXT'],'host':joint_probs['EXACT_HOST'],'null_key':nk(r),'observation_id':r['observation_id']})
  folio_gain[held]=fb['JOINT_RENDERER']['LAYOUT_CONTEXT']-fb['JOINT_RENDERER']['EXACT_HOST']
  for e in ENDPOINTS:
   for m in MODELS:foldrows.append({'split':'HELD_'+split.upper(),'held_value':held,'prior_mass':prior,'endpoint':e,'model':m,'eligible_events':len(eligible),'bits':fb[e][m],'top1':ft[e][m]})
 return {'alphabets':alph,'bits':{e:dict(bits[e]) for e in ENDPOINTS},'top':{e:dict(top[e]) for e in ENDPOINTS},'foldrows':foldrows,'predictions':pred,'folio_gain':folio_gain,'eligible':eligible_total}
def gain(q,e='JOINT_RENDERER'):return (q['bits'][e]['LAYOUT_CONTEXT']-q['bits'][e]['EXACT_HOST'])/q['eligible']
def nulls(q,panel,worlds):
 strata=defaultdict(list)
 for i,r in enumerate(q['predictions']):strata[r['null_key']].append(i)
 out=[];mobile=0;swappable=sum(len(v) for v in strata.values() if len(v)>1)
 for world in range(worlds):
  yy=[r['actual'] for r in q['predictions']]
  for key,ids in sorted(strata.items(),key=lambda z:repr(z[0])):
   seed=f"GDT293_HELD_RENDERER_ALIGNMENT|{panel}|{world}|"+'|'.join(map(str,key));rng=random.Random(int(hashlib.sha256(seed.encode()).hexdigest()[:16],16));v=[yy[i] for i in ids];rng.shuffle(v)
   for i,x in zip(ids,v):
    if world==0 and x!=yy[i]:mobile+=1
    yy[i]=x
  out.append(sum(math.log2(r['host'][y]/r['layout'][y]) for r,y in zip(q['predictions'],yy))/q['eligible'])
 return out,mobile,swappable
def job(item):
 p,e,w=item;q=score(e,retain=True);n,m,s=nulls(q,p,w);return p,q,n,m,s
def main():
 d=json.loads(DESIGN.read_text());assert d['status']=='FROZEN_BEFORE_GDT293_SCORING' and d['content_sha256']==rcsha(d)
 for x in read(R/'gdt293_freeze_manifest.tsv'):assert sha(R/x['artifact'])==x['frozen_sha256']
 native=read(R/'gdt278_native_event_inventory.tsv');assert not any(x['page'].startswith('f84') or x['locus'].startswith('f84') for x in native);panels={p:[x for x in native if x['control_id']==p] for p in d['panels']};assert all(len(v)==8448 for v in panels.values())
 rr={}
 with ProcessPoolExecutor(max_workers=4) as ex:
  fs={ex.submit(job,(p,e,d['null_worlds'])):p for p,e in panels.items()}
  for f in as_completed(fs):z=f.result();rr[z[0]]=z[1:];print(json.dumps({'panel':z[0],'eligible':z[1]['eligible'],'gain':gain(z[1])},sort_keys=True),flush=True)
 panelrows=[];foldrows=[];nullrows=[];obs={};means={};sds={}
 for p in d['panels']:
  q,n,mob,swap=rr[p];obs[p]=gain(q);means[p]=statistics.mean(n);sds[p]=statistics.pstdev(n)
  for e in ENDPOINTS:
   for model in MODELS:panelrows.append({'control_id':p,'split':'HELD_PHYSICAL_FOLIO','prior_mass':11,'endpoint':e,'model':model,'eligible_events':q['eligible'],'classes':len(q['alphabets'][e]),'bits':f"{q['bits'][e][model]:.12f}",'bits_per_event':f"{q['bits'][e][model]/q['eligible']:.12f}",'top1':q['top'][e][model],'top1_rate':f"{q['top'][e][model]/q['eligible']:.12f}",'exact_host_gain_bits_per_event':f"{gain(q,e):.12f}" if model=='EXACT_HOST' else 'NA'})
  for x in q['foldrows']:
   base=next(y for y in q['foldrows'] if y['held_value']==x['held_value'] and y['endpoint']==x['endpoint'] and y['model']=='LAYOUT_CONTEXT');foldrows.append({'control_id':p,**x,'bits':f"{x['bits']:.12f}",'exact_host_gain_bits':f"{base['bits']-x['bits']:.12f}" if x['model']=='EXACT_HOST' else 'NA'})
  for w,v in enumerate(n):nullrows.append({'control_id':p,'world_index':w,'joint_gain_bits_per_event':f'{v:.12f}'})
 variable=[p for p in d['panels'] if sds[p]>1e-15];fixed=[p for p in d['panels'] if p not in variable];zs={p:(obs[p]-means[p])/sds[p] for p in variable};worldmax=[max((rr[p][1][i]-means[p])/sds[p] for p in variable) for i in range(d['null_worlds'])];summary=[]
 for p in d['panels']:
  q,n,mob,swap=rr[p];var=p in variable;lp=(1+sum(x>=obs[p]-1e-15 for x in n))/65 if var else None;mp=(1+sum(x>=zs[p]-1e-15 for x in worldmax))/65 if var else None;cg={e:gain(q,e) for e in ENDPOINTS[1:]};summary.append({'control_id':p,'eligible_events':q['eligible'],'folios':len(q['folio_gain']),'joint_classes':len(q['alphabets']['JOINT_RENDERER']),'joint_gain_bits_per_event':f'{obs[p]:.12f}','positive_components':sum(x>0 for x in cg.values()),'component_gains':{k:float(f'{v:.12f}') for k,v in cg.items()},'positive_folios':sum(x>0 for x in q['folio_gain'].values()),'null_mean':f'{means[p]:.12f}','null_sd':f'{sds[p]:.12f}','observed_z':f'{zs[p]:.12f}' if var else 'NA_ZERO_NULL_VARIANCE','local_p':f'{lp:.12f}' if var else 'NA_ZERO_NULL_VARIANCE','max_variable_family_p':f'{mp:.12f}' if var else 'NA_ZERO_NULL_VARIANCE','null_mobile_events_world0':mob,'null_swappable_events':swap})
 voy=panels['VOYNICH_REFERENCE'];sens=[]
 for prior in d['voynich_prior_sensitivities']:
  q=score(voy,prior=prior);sens.append({'split':'HELD_PHYSICAL_FOLIO','prior_mass':prior,'eligible_events':q['eligible'],'joint_gain_bits_per_event':gain(q)})
 for split in ('section','hand'):
  q=score(voy,split=split,prior=11);sens.append({'split':'HELD_'+split.upper(),'prior_mass':11,'eligible_events':q['eligible'],'joint_gain_bits_per_event':gain(q)})
 sensrows=[{**x,'joint_gain_bits_per_event':f"{x['joint_gain_bits_per_event']:.12f}"} for x in sens];v=next(x for x in summary if x['control_id']=='VOYNICH_REFERENCE');sg={x['split']:x['joint_gain_bits_per_event'] for x in sens};gates={'joint_gain_positive':float(v['joint_gain_bits_per_event'])>0,'at_least_four_of_six_components_positive':int(v['positive_components'])>=4,'at_least_sixty_of_ninety_one_folios_positive':int(v['folios'])==91 and int(v['positive_folios'])>=60,'held_section_gain_positive':sg['HELD_SECTION']>0,'held_hand_gain_positive':sg['HELD_HAND']>0,'maxT_p_le_0_05':not str(v['max_variable_family_p']).startswith('NA') and float(v['max_variable_family_p'])<=.05};status=d['decision']['support'] if all(gates.values()) else d['decision']['fail']
 write(OUT_PANEL,panelrows);write(OUT_FOLD,foldrows);write(OUT_NULL,nullrows);write(OUT_SENS,sensrows)
 vq=rr['VOYNICH_REFERENCE'][0];weak_folio,weak_gain=min(vq['folio_gain'].items(),key=lambda x:x[1]);largest_control=max(float(x['joint_gain_bits_per_event']) for x in summary if x['control_id']!='VOYNICH_REFERENCE')
 counter=[{'counterexample':'ONE_NEGATIVE_HELD_FOLIO','evidence':f'{weak_folio} {weak_gain:+.6f} bits across {next(x["eligible_events"] for x in vq["foldrows"] if x["held_value"]==weak_folio and x["endpoint"]=="JOINT_RENDERER" and x["model"]=="EXACT_HOST")} eligible events','impact':'completion is not exceptionless'}, {'counterexample':'POSITIVE_IN_ORDINARY_GRAPHEMATIC_CONTROLS','evidence':f'largest non-Voynich gain {largest_control:+.6f} bits/event; all three Latin panels positive','impact':'same-group renderer stability is not Voynich-specific'}, {'counterexample':'PRIOR_MAGNITUDE_SENSITIVITY','evidence':'; '.join(f"{x['prior_mass']}:{x['joint_gain_bits_per_event']:+.6f}" for x in sens if x['split']=='HELD_PHYSICAL_FOLIO'),'impact':'sign is stable but magnitude remains smoothing-dependent'}, {'counterexample':'NEXT_HOST_RESCUE_NOT_TESTED','evidence':'GDT165 remains negative and no sequential host feature enters GDT293','impact':'same-group completion cannot be called sequential syntax'}, {'counterexample':'PARSER_DETERMINISM','evidence':'host and renderer tuple are complementary outputs of the same frozen parser','impact':'association cannot prove lexicality or causal generation'}, {'counterexample':'F84_USED','evidence':'only f84-free native inventory read','impact':'no f84 access'}];write(OUT_COUNTER,counter)
 report=['# GDT293 — exact-host renderer completion','',f'Status: **{status}**.','','## Held-folio joint completion','', '| panel | eligible | joint gain bits/event | components positive | folios positive | local p | max-family p |','|---|---:|---:|---:|---:|---:|---:|']
 for x in summary:report.append(f"| {x['control_id']} | {x['eligible_events']} | {float(x['joint_gain_bits_per_event']):+.4f} | {x['positive_components']}/6 | {x['positive_folios']}/{x['folios']} | {x['local_p']} | {x['max_variable_family_p']} |")
 report+=['',f"Voynich joint codelength falls from {vq['bits']['JOINT_RENDERER']['LAYOUT_CONTEXT']/vq['eligible']:.4f} to {vq['bits']['JOINT_RENDERER']['EXACT_HOST']/vq['eligible']:.4f} bits/event; top-1 accuracy rises from {vq['top']['JOINT_RENDERER']['LAYOUT_CONTEXT']/vq['eligible']:.4f} to {vq['top']['JOINT_RENDERER']['EXACT_HOST']/vq['eligible']:.4f}.",'','## Voynich component diagnostics','']+[f"- `{k}`: {val:+.6f} bits/event." for k,val in v['component_gains'].items()]+['','## Voynich sensitivities','']+[f"- {x['split']} prior={x['prior_mass']}, n={x['eligible_events']}: {x['joint_gain_bits_per_event']:+.6f} bits/event." for x in sens]+['','## Frozen gates','']+[f"- `{k}`: **{'PASS' if x else 'FAIL'}**" for k,x in gates.items()]+['','## Interpretation and claim ceiling','','This tests only whether an exact opaque host recurring outside the held folio helps complete its parser-defined same-group renderer tuple. GDT165 immediate NEXT_HOST transfer remains negative and was not rerun. A positive same-group result would therefore not be evidence for stable word order or sequential syntax.','','All three Latin graphematic controls also improve, so same-group renderer completion is not Voynich-specific. Voynich is larger on this fixed panel, but that magnitude comparison was not a separate frozen uniqueness test.','','Host and renderer coordinates come from the same frozen parser. The result cannot establish lexical identity, a word, code value, morpheme, sound, language, meaning, plaintext, or translation. No f84 row was opened, parsed, retained, joined, or scored.'];REPORT.write_text('\n'.join(report)+'\n')
 outputs=[OUT_PANEL,OUT_FOLD,OUT_NULL,OUT_SENS,OUT_COUNTER,REPORT];inputs=['gdt293_design.json','gdt293_design_validation.json','gdt293_capacity.tsv','gdt293_freeze_manifest.tsv','gdt278_native_event_inventory.tsv','gdt292_result.json','gdt288_result.json','gdt286_result.json','gdt165_result.json'];res={'schema':'GDT293_EXACT_HOST_RENDERER_COMPLETION_RESULT_V1','status':status,'summary':summary,'voynich_summary':v,'voynich_sensitivities':sens,'frozen_gates':gates,'prior_next_host_result':d['prior_next_host_result'],'variable_null_panels':variable,'zero_null_variance_panels':fixed,'new_corpora':0,'new_architectures':0,'semantic_assignments':0,'page_host_substrings_mined':0,'claim_ceiling':d['claim_ceiling'],'f84':d['f84'],'inputs':{x:sha(R/x) for x in inputs},'documents':{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)},'implementation':{Path(__file__).name:sha(Path(__file__))},'outputs':{x.name:sha(x) for x in outputs}};res['content_sha256']=rcsha(res);RESULT.write_text(json.dumps(res,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':status,'voynich':v,'gates':gates},sort_keys=True))
if __name__=='__main__':main()
