#!/usr/bin/env python3
"""Run frozen GDT294 host-position renderer-tuple experiment."""
from __future__ import annotations
import csv,hashlib,json,math,random,statistics
from collections import Counter,defaultdict
from concurrent.futures import ProcessPoolExecutor,as_completed
from pathlib import Path
R=Path(__file__).resolve().parent;D=R/'gdt294_design.json';METHOD=R/'GDT294_HOST_POSITION_RENDERER_TUPLE_METHOD.md';REPORT=R/'GDT294_HOST_POSITION_RENDERER_TUPLE_REPORT.md';RESULT=R/'gdt294_result.json';PANEL=R/'gdt294_panel_scores.tsv';FOLIO=R/'gdt294_folio_scores.tsv';NEST=R/'gdt294_nested_increments.tsv';NULL=R/'gdt294_null_results.tsv';SENS=R/'gdt294_voynich_sensitivities.tsv';COUNTER=R/'gdt294_counterexamples.tsv';MODELS=('LAYOUT_CONTEXT','BOUNDARY_CONTEXT','EXACT_HOST','HOST_X_POSITION','HOST_X_RECORD_SLOT');C=('wrapper','local_frame','inner_d','right_family','dy_closure','b3');ALPHA=.5
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
def ob(v):
 n=int(v);return '1' if n==1 else '2' if n==2 else '3_4' if n<=4 else '5_PLUS'
def gp(r):
 i=int(r['group_index']);n=int(r['group_count']);return 'ONLY' if n==1 else 'FIRST' if i==1 else 'LAST' if i==n else 'MIDDLE'
def target(r):return '|'.join(r[x] for x in C)
def lk(r):return (r['section'],r['currier'],r['hand'],r['register'],r['within_field_position'],ob(r['record_ordinal']),ob(r['field_ordinal']),gp(r),int(r['host_length']))
def bk(r):return lk(r)+(r['line_close'],r['paragraph_close'],r['known_label_renderer'])
def pk(r):return (r['page_host'],r['within_field_position'])
def sk(r):return (r['page_host'],r['within_field_position'],ob(r['record_ordinal']),ob(r['field_ordinal']),gp(r))
def nk(r):return (r['physical_folio'],r['page_host'],r['section'],r['currier'],r['hand'],r['register'],ob(r['record_ordinal']),ob(r['field_ordinal']),gp(r),int(r['host_length']),r['line_close'],r['paragraph_close'],r['known_label_renderer'])
def score(ev,split='physical_folio',prior=11.,retain=False):
 yy=sorted({target(r) for r in ev});rank={x:i for i,x in enumerate(yy)};folds=defaultdict(list)
 for i,r in enumerate(ev):folds[r[split]].append(i)
 bits=Counter();top=Counter();fr=[];pred=[];fg={};pg=defaultdict(lambda:[0,0.]);eligible_total=0
 for held,test in sorted(folds.items()):
  train=[i for i,r in enumerate(ev) if r[split]!=held];th=Counter(ev[i]['page_host'] for i in train);g=Counter();lc=defaultdict(Counter);bc=defaultdict(Counter);hc=defaultdict(Counter);pc=defaultdict(Counter);sc=defaultdict(Counter)
  for i in train:
   r=ev[i];y=target(r);g[y]+=1;lc[lk(r)][y]+=1;bc[bk(r)][y]+=1;hc[r['page_host']][y]+=1;pc[pk(r)][y]+=1;sc[sk(r)][y]+=1
  test=[i for i in test if th[ev[i]['page_host']]>0];eligible_total+=len(test);fb=Counter();ft=Counter()
  for i in test:
   r=ev[i];actual=target(r);pp={m:{} for m in MODELS};K=len(yy)
   for y in yy:
    p0=(g[y]+ALPHA)/(len(train)+ALPHA*K);a=lc[lk(r)];p1=(a[y]+prior*p0)/(sum(a.values())+prior);a=bc[bk(r)];p2=(a[y]+prior*p1)/(sum(a.values())+prior);a=hc[r['page_host']];p3=(a[y]+prior*p2)/(sum(a.values())+prior);a=pc[pk(r)];p4=(a[y]+prior*p3)/(sum(a.values())+prior);a=sc[sk(r)];p5=(a[y]+prior*p4)/(sum(a.values())+prior)
    for m,p in zip(MODELS,(p1,p2,p3,p4,p5)):pp[m][y]=p
   for m in MODELS:
    z=-math.log2(pp[m][actual]);bits[m]+=z;fb[m]+=z;hit=int(max(yy,key=lambda y:(pp[m][y],-rank[y]))==actual);top[m]+=hit;ft[m]+=hit
   gpos=math.log2(pp['HOST_X_POSITION'][actual]/pp['EXACT_HOST'][actual]);pg[r['within_field_position']][0]+=1;pg[r['within_field_position']][1]+=gpos
   if retain:pred.append({'actual':actual,'host':pp['EXACT_HOST'],'position':pp['HOST_X_POSITION'],'null_key':nk(r)})
  fg[held]=fb['EXACT_HOST']-fb['HOST_X_POSITION']
  for m in MODELS:fr.append({'split':'HELD_'+split.upper(),'held_value':held,'prior_mass':prior,'model':m,'eligible_events':len(test),'bits':fb[m],'top1':ft[m]})
 return {'classes':yy,'bits':dict(bits),'top':dict(top),'foldrows':fr,'pred':pred,'folio_gain':fg,'position_gain':dict(pg),'eligible':eligible_total}
def increments(q):return {'BOUNDARY_GIVEN_LAYOUT':(q['bits']['LAYOUT_CONTEXT']-q['bits']['BOUNDARY_CONTEXT'])/q['eligible'],'HOST_GIVEN_BOUNDARY':(q['bits']['BOUNDARY_CONTEXT']-q['bits']['EXACT_HOST'])/q['eligible'],'HOST_POSITION_GIVEN_HOST':(q['bits']['EXACT_HOST']-q['bits']['HOST_X_POSITION'])/q['eligible'],'RECORD_SLOT_GIVEN_HOST_POSITION':(q['bits']['HOST_X_POSITION']-q['bits']['HOST_X_RECORD_SLOT'])/q['eligible']}
def nulls(q,panel,worlds):
 st=defaultdict(list)
 for i,r in enumerate(q['pred']):st[r['null_key']].append(i)
 out=[];mobile=0;swap=sum(len(v) for v in st.values() if len(v)>1)
 for world in range(worlds):
  y=[r['actual'] for r in q['pred']]
  for key,ids in sorted(st.items(),key=lambda z:repr(z[0])):
   seed=f"GDT294_HELD_HOST_POSITION_RENDERER_ALIGNMENT|{panel}|{world}|"+'|'.join(map(str,key));rng=random.Random(int(hashlib.sha256(seed.encode()).hexdigest()[:16],16));v=[y[i] for i in ids];rng.shuffle(v)
   for i,x in zip(ids,v):
    if world==0 and x!=y[i]:mobile+=1
    y[i]=x
  out.append(sum(math.log2(r['position'][x]/r['host'][x]) for r,x in zip(q['pred'],y))/q['eligible'])
 return out,mobile,swap
def job(item):
 p,e,w=item;q=score(e,retain=True);n,m,s=nulls(q,p,w);return p,q,n,m,s
def main():
 d=json.loads(D.read_text());assert d['status']=='FROZEN_BEFORE_GDT294_SCORING' and d['content_sha256']==rcsha(d)
 for x in read(R/'gdt294_freeze_manifest.tsv'):assert sha(R/x['artifact'])==x['frozen_sha256']
 native=read(R/'gdt278_native_event_inventory.tsv');assert not any(x['page'].startswith('f84') or x['locus'].startswith('f84') for x in native);panels={p:[x for x in native if x['control_id']==p] for p in d['panels']};assert all(len(v)==8448 for v in panels.values());rr={}
 with ProcessPoolExecutor(max_workers=4) as ex:
  fs={ex.submit(job,(p,e,d['null_worlds'])):p for p,e in panels.items()}
  for f in as_completed(fs):z=f.result();rr[z[0]]=z[1:];print(json.dumps({'panel':z[0],'increments':increments(z[1])},sort_keys=True),flush=True)
 prows=[];frows=[];irows=[];nrows=[];obs={};means={};sds={}
 for p in d['panels']:
  q,n,mob,swap=rr[p];inc=increments(q);obs[p]=inc['HOST_POSITION_GIVEN_HOST'];means[p]=statistics.mean(n);sds[p]=statistics.pstdev(n)
  for m in MODELS:prows.append({'control_id':p,'model':m,'eligible_events':q['eligible'],'classes':len(q['classes']),'bits':f"{q['bits'][m]:.12f}",'bits_per_event':f"{q['bits'][m]/q['eligible']:.12f}",'top1':q['top'][m],'top1_rate':f"{q['top'][m]/q['eligible']:.12f}"})
  for x in q['foldrows']:
   h=next(y for y in q['foldrows'] if y['held_value']==x['held_value'] and y['model']=='EXACT_HOST');pos=next(y for y in q['foldrows'] if y['held_value']==x['held_value'] and y['model']=='HOST_X_POSITION');frows.append({'control_id':p,**x,'bits':f"{x['bits']:.12f}",'primary_position_gain_bits':f"{h['bits']-pos['bits']:.12f}" if x['model']=='HOST_X_POSITION' else 'NA'})
  for k,v in inc.items():irows.append({'control_id':p,'increment':k,'gain_bits_per_event':f'{v:.12f}'})
  for w,v in enumerate(n):nrows.append({'control_id':p,'world_index':w,'host_position_gain_bits_per_event':f'{v:.12f}'})
 variable=[p for p in d['panels'] if sds[p]>1e-15];fixed=[p for p in d['panels'] if p not in variable];zs={p:(obs[p]-means[p])/sds[p] for p in variable};mx=[max((rr[p][1][i]-means[p])/sds[p] for p in variable) for i in range(64)];summary=[]
 for p in d['panels']:
  q,n,mob,swap=rr[p];var=p in variable;lp=(1+sum(v>=obs[p]-1e-15 for v in n))/65 if var else None;mp=(1+sum(v>=zs[p]-1e-15 for v in mx))/65 if var else None;summary.append({'control_id':p,'eligible_events':q['eligible'],'folios':len(q['folio_gain']),'classes':len(q['classes']),'increments':{k:float(f'{v:.12f}') for k,v in increments(q).items()},'positive_folios':sum(v>0 for v in q['folio_gain'].values()),'positive_positions':sum(v[1]>0 for v in q['position_gain'].values()),'positions':len(q['position_gain']),'null_mean':f'{means[p]:.12f}','null_sd':f'{sds[p]:.12f}','observed_z':f'{zs[p]:.12f}' if var else 'NA_ZERO_NULL_VARIANCE','local_p':f'{lp:.12f}' if var else 'NA_ZERO_NULL_VARIANCE','max_variable_family_p':f'{mp:.12f}' if var else 'NA_ZERO_NULL_VARIANCE','null_mobile_events_world0':mob,'null_swappable_events':swap})
 voy=panels['VOYNICH_REFERENCE'];sens=[]
 for prior in d['voynich_prior_sensitivities']:
  q=score(voy,prior=prior);sens.append({'split':'HELD_PHYSICAL_FOLIO','prior_mass':prior,'eligible_events':q['eligible'],**increments(q)})
 for split in ('section','hand'):
  q=score(voy,split=split,prior=11);sens.append({'split':'HELD_'+split.upper(),'prior_mass':11,'eligible_events':q['eligible'],**increments(q)})
 srows=[]
 for x in sens:
  for k in ('HOST_POSITION_GIVEN_HOST','RECORD_SLOT_GIVEN_HOST_POSITION'):srows.append({'split':x['split'],'prior_mass':x['prior_mass'],'eligible_events':x['eligible_events'],'increment':k,'gain_bits_per_event':f"{x[k]:.12f}"})
 v=next(x for x in summary if x['control_id']=='VOYNICH_REFERENCE');sg={x['split']:x['HOST_POSITION_GIVEN_HOST'] for x in sens};gates={'host_position_gain_positive':v['increments']['HOST_POSITION_GIVEN_HOST']>0,'at_least_sixty_of_ninety_one_folios_positive':v['folios']==91 and v['positive_folios']>=60,'held_section_gain_positive':sg['HELD_SECTION']>0,'held_hand_gain_positive':sg['HELD_HAND']>0,'maxT_p_le_0_05':not str(v['max_variable_family_p']).startswith('NA') and float(v['max_variable_family_p'])<=.05};status=d['decision']['support'] if all(gates.values()) else d['decision']['fail'];write(PANEL,prows);write(FOLIO,frows);write(NEST,irows);write(NULL,nrows);write(SENS,srows)
 qv=rr['VOYNICH_REFERENCE'][0];bad=min(qv['folio_gain'].items(),key=lambda x:x[1]);p5=next(x['HOST_POSITION_GIVEN_HOST'] for x in sens if x['split']=='HELD_PHYSICAL_FOLIO' and x['prior_mass']==5);p22=next(x['HOST_POSITION_GIVEN_HOST'] for x in sens if x['split']=='HELD_PHYSICAL_FOLIO' and x['prior_mass']==22);counter=[{'counterexample':'PRIOR_SIGN_CHANGE','evidence':f"prior5 {p5:+.6f}; prior11 {v['increments']['HOST_POSITION_GIVEN_HOST']:+.6f}; prior22 {p22:+.6f}",'impact':'position effect is smoothing-sensitive and not a stable magnitude'}, {'counterexample':'RECORD_SLOT_INCREMENT','evidence':f"Voynich {v['increments']['RECORD_SLOT_GIVEN_HOST_POSITION']:+.6f} bits/event",'impact':'negative increment rejects richer slot table'}, {'counterexample':'WORST_HELD_FOLIO','evidence':f'{bad[0]} {bad[1]:+.6f} bits','impact':'shows strongest local exception'}, {'counterexample':'CONTROL_NULLS_ZERO_VARIANCE','evidence':','.join(fixed),'impact':'corrected variable-family p effectively tests Voynich alone'}, {'counterexample':'NULL_MOBILITY','evidence':f"{v['null_swappable_events']} swappable; world0 {v['null_mobile_events_world0']} changed",'impact':'bounds exact host-preserving null'}, {'counterexample':'PARSER_COUPLING','evidence':'host and target tuple share one frozen parse','impact':'no causal morphology or lexicality'}, {'counterexample':'F84_USED','evidence':'only f84-free native inventory read','impact':'no f84 access'}];write(COUNTER,counter)
 report=['# GDT294 — host-position renderer tuple','',f'Status: **{status}**.','','## Held-folio nested gains','', '| panel | boundary | exact host | host×position | record slot | positive folios | local p | max-family p |','|---|---:|---:|---:|---:|---:|---:|---:|']
 for x in summary:report.append(f"| {x['control_id']} | {x['increments']['BOUNDARY_GIVEN_LAYOUT']:+.4f} | {x['increments']['HOST_GIVEN_BOUNDARY']:+.4f} | {x['increments']['HOST_POSITION_GIVEN_HOST']:+.4f} | {x['increments']['RECORD_SLOT_GIVEN_HOST_POSITION']:+.4f} | {x['positive_folios']}/{x['folios']} | {x['local_p']} | {x['max_variable_family_p']} |")
 report+=['','The primary host×position increment is measured after physical boundary context and exact opaque host. The record-slot column adds the finer host×position×record/field/group table.','','Every control panel has an exact zero-variance null under the strict host-preserving strata, so the reported corrected variable-family p-value effectively contains only Voynich. It is not an eight-powered-family correction. The prior-5 sensitivity also changes the primary sign; treat the frozen support label as a weak, smoothing-sensitive positional lead rather than a stable magnitude.','','## Voynich sensitivities','']+[f"- {x['split']} prior={x['prior_mass']}: host×position {x['HOST_POSITION_GIVEN_HOST']:+.6f}; record slot {x['RECORD_SLOT_GIVEN_HOST_POSITION']:+.6f} bits/event (n={x['eligible_events']})." for x in sens]+['','## Frozen gates','']+[f"- `{k}`: **{'PASS' if z else 'FAIL'}**" for k,z in gates.items()]+['','## Claim ceiling','','This can identify only a host-specific positional renderer distribution. It cannot establish a productive morphological rule, lexical class, word, code value, language, meaning, plaintext, or translation. Host and renderer remain complementary parser outputs. No f84 row was opened, parsed, retained, joined, or scored.'];REPORT.write_text('\n'.join(report)+'\n')
 outputs=[PANEL,FOLIO,NEST,NULL,SENS,COUNTER,REPORT];inputs=['gdt294_design.json','gdt294_design_validation.json','gdt294_capacity.tsv','gdt294_freeze_manifest.tsv','gdt278_native_event_inventory.tsv','gdt293_result.json','gdt291_result.json','gdt286_result.json','gdt288_result.json'];res={'schema':'GDT294_HOST_POSITION_RENDERER_TUPLE_RESULT_V1','status':status,'summary':summary,'voynich_summary':v,'voynich_sensitivities':sens,'frozen_gates':gates,'variable_null_panels':variable,'zero_null_variance_panels':fixed,'new_corpora':0,'new_architectures':0,'semantic_assignments':0,'page_host_substrings_mined':0,'claim_ceiling':d['claim_ceiling'],'f84':d['f84'],'inputs':{x:sha(R/x) for x in inputs},'documents':{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)},'implementation':{Path(__file__).name:sha(Path(__file__))},'outputs':{x.name:sha(x) for x in outputs}};res['content_sha256']=rcsha(res);RESULT.write_text(json.dumps(res,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':status,'voynich':v,'gates':gates},sort_keys=True))
if __name__=='__main__':main()
