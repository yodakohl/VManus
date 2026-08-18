#!/usr/bin/env python3
"""Run frozen GDT295 online page-local renderer adaptation."""
from __future__ import annotations
import csv,hashlib,itertools,json,math,random,statistics
from collections import Counter,defaultdict
from concurrent.futures import ProcessPoolExecutor,as_completed
from pathlib import Path
R=Path(__file__).resolve().parent;D=R/'gdt295_design.json';METHOD=R/'GDT295_ONLINE_PAGE_LOCAL_RENDERER_METHOD.md';REPORT=R/'GDT295_ONLINE_PAGE_LOCAL_RENDERER_REPORT.md';RESULT=R/'gdt295_result.json';PANEL=R/'gdt295_panel_scores.tsv';FOLIO=R/'gdt295_folio_scores.tsv';BREAK=R/'gdt295_breakdown.tsv';NULL=R/'gdt295_null_results.tsv';SENS=R/'gdt295_voynich_sensitivities.tsv';COUNTER=R/'gdt295_counterexamples.tsv';MODELS=('CROSS_FOLIO_HOST_X_POSITION','PAGE_LOCAL_HOST','PAGE_LOCAL_HOST_X_POSITION');C=('wrapper','local_frame','inner_d','right_family','dy_closure','b3');ALPHA=.5
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
def pk(r):return r['page_host'],r['within_field_position']
def score(ev,prior=11.,retain=False):
 alphabet=sorted({target(r) for r in ev});rank={x:i for i,x in enumerate(alphabet)};folios=[]
 for r in ev:
  if r['physical_folio'] not in folios:folios.append(r['physical_folio'])
 bits=Counter();top=Counter();foldrows=[];pred=[];page_gain=defaultdict(float);section_gain=defaultdict(float);hand_gain=defaultdict(float);eligible_total=0
 for held in folios:
  train=[r for r in ev if r['physical_folio']!=held];test=[r for r in ev if r['physical_folio']==held];th=Counter(r['page_host'] for r in train);g=Counter();lc=defaultdict(Counter);bc=defaultdict(Counter);hc=defaultdict(Counter);pc=defaultdict(Counter)
  for r in train:
   y=target(r);g[y]+=1;lc[lk(r)][y]+=1;bc[bk(r)][y]+=1;hc[r['page_host']][y]+=1;pc[pk(r)][y]+=1
  ph=defaultdict(Counter);php=defaultdict(Counter);fb=Counter();ft=Counter();fn=0
  for locus,group in itertools.groupby(test,key=lambda r:r['locus']):
   line=list(group)
   for r in line:
    if th[r['page_host']]==0 or sum(ph[r['page'],r['page_host']].values())==0:continue
    actual=target(r);pp={m:{} for m in MODELS};K=len(alphabet)
    for y in alphabet:
     p0=(g[y]+ALPHA)/(len(train)+ALPHA*K);a=lc[lk(r)];p1=(a[y]+prior*p0)/(sum(a.values())+prior);a=bc[bk(r)];p2=(a[y]+prior*p1)/(sum(a.values())+prior);a=hc[r['page_host']];p3=(a[y]+prior*p2)/(sum(a.values())+prior);a=pc[pk(r)];pcross=(a[y]+prior*p3)/(sum(a.values())+prior);a=ph[r['page'],r['page_host']];ppage=(a[y]+prior*pcross)/(sum(a.values())+prior);a=php[r['page'],r['page_host'],r['within_field_position']];ppos=(a[y]+prior*ppage)/(sum(a.values())+prior);pp['CROSS_FOLIO_HOST_X_POSITION'][y]=pcross;pp['PAGE_LOCAL_HOST'][y]=ppage;pp['PAGE_LOCAL_HOST_X_POSITION'][y]=ppos
    for m in MODELS:
     z=-math.log2(pp[m][actual]);bits[m]+=z;fb[m]+=z;hit=int(max(alphabet,key=lambda y:(pp[m][y],-rank[y]))==actual);top[m]+=hit;ft[m]+=hit
    gain=math.log2(pp['PAGE_LOCAL_HOST_X_POSITION'][actual]/pp['CROSS_FOLIO_HOST_X_POSITION'][actual]);page_gain[r['page']]+=gain;section_gain[r['section']]+=gain;hand_gain[r['hand']]+=gain;fn+=1;eligible_total+=1
    if retain:pred.append({'actual':actual,'cross':pp['CROSS_FOLIO_HOST_X_POSITION'],'page':pp['PAGE_LOCAL_HOST_X_POSITION'],'null_key':(r['page'],r['page_host']),'observation_id':r['observation_id']})
   for r in line:
    y=target(r);ph[r['page'],r['page_host']][y]+=1;php[r['page'],r['page_host'],r['within_field_position']][y]+=1
  for m in MODELS:foldrows.append({'held_folio':held,'prior_mass':prior,'model':m,'eligible_events':fn,'bits':fb[m],'top1':ft[m]})
 return {'classes':alphabet,'bits':dict(bits),'top':dict(top),'foldrows':foldrows,'pred':pred,'page_gain':dict(page_gain),'section_gain':dict(section_gain),'hand_gain':dict(hand_gain),'eligible':eligible_total}
def increments(q):return {'PAGE_HOST_GIVEN_CROSS_FOLIO_POSITION':(q['bits']['CROSS_FOLIO_HOST_X_POSITION']-q['bits']['PAGE_LOCAL_HOST'])/q['eligible'],'PAGE_POSITION_GIVEN_PAGE_HOST':(q['bits']['PAGE_LOCAL_HOST']-q['bits']['PAGE_LOCAL_HOST_X_POSITION'])/q['eligible'],'TOTAL_PAGE_LOCAL_GAIN':(q['bits']['CROSS_FOLIO_HOST_X_POSITION']-q['bits']['PAGE_LOCAL_HOST_X_POSITION'])/q['eligible']}
def nulls(q,panel,worlds):
 st=defaultdict(list)
 for i,r in enumerate(q['pred']):st[r['null_key']].append(i)
 out=[];mobile=0;swap=sum(len(v) for v in st.values() if len(v)>1)
 for world in range(worlds):
  y=[r['actual'] for r in q['pred']]
  for key,ids in sorted(st.items(),key=lambda z:repr(z[0])):
   seed=f"GDT295_ONLINE_PAGE_RENDERER_ALIGNMENT|{panel}|{world}|"+'|'.join(map(str,key));rng=random.Random(int(hashlib.sha256(seed.encode()).hexdigest()[:16],16));v=[y[i] for i in ids];rng.shuffle(v)
   for i,x in zip(ids,v):
    if world==0 and x!=y[i]:mobile+=1
    y[i]=x
  out.append(sum(math.log2(r['page'][x]/r['cross'][x]) for r,x in zip(q['pred'],y))/q['eligible'])
 return out,mobile,swap
def job(item):
 p,e,w=item;q=score(e,retain=True);n,m,s=nulls(q,p,w);return p,q,n,m,s
def main():
 d=json.loads(D.read_text());assert d['status']=='FROZEN_BEFORE_GDT295_SCORING' and d['content_sha256']==rcsha(d)
 for x in read(R/'gdt295_freeze_manifest.tsv'):assert sha(R/x['artifact'])==x['frozen_sha256']
 native=read(R/'gdt278_native_event_inventory.tsv');assert not any(x['page'].startswith('f84') or x['locus'].startswith('f84') for x in native);panels={p:[x for x in native if x['control_id']==p] for p in d['panels']};assert all(len(v)==8448 for v in panels.values());rr={}
 with ProcessPoolExecutor(max_workers=4) as ex:
  fs={ex.submit(job,(p,panels[p],d['null_worlds'])):p for p in d['powered_panels']}
  for f in as_completed(fs):z=f.result();rr[z[0]]=z[1:];print(json.dumps({'panel':z[0],'increments':increments(z[1])},sort_keys=True),flush=True)
 prows=[];frows=[];brows=[];nrows=[];obs={};means={};sds={}
 for p in d['panels']:
  if p not in rr:
   for m in MODELS:
    prows.append({'control_id':p,'capacity_status':'UNSCORED_ZERO_ONLINE_CAPACITY','model':m,'eligible_events':0,'classes':'NA','bits':'NA','bits_per_event':'NA','top1':'NA','top1_rate':'NA'})
   continue
  q,n,mob,swap=rr[p];inc=increments(q);obs[p]=inc['TOTAL_PAGE_LOCAL_GAIN'];means[p]=statistics.mean(n);sds[p]=statistics.pstdev(n)
  for m in MODELS:prows.append({'control_id':p,'capacity_status':'SCORED','model':m,'eligible_events':q['eligible'],'classes':len(q['classes']),'bits':f"{q['bits'][m]:.12f}",'bits_per_event':f"{q['bits'][m]/q['eligible']:.12f}",'top1':q['top'][m],'top1_rate':f"{q['top'][m]/q['eligible']:.12f}"})
  for x in q['foldrows']:
   base=next(y for y in q['foldrows'] if y['held_folio']==x['held_folio'] and y['model']=='CROSS_FOLIO_HOST_X_POSITION');alt=next(y for y in q['foldrows'] if y['held_folio']==x['held_folio'] and y['model']=='PAGE_LOCAL_HOST_X_POSITION');frows.append({'control_id':p,**x,'bits':f"{x['bits']:.12f}",'total_page_local_gain_bits':f"{base['bits']-alt['bits']:.12f}" if x['model']=='PAGE_LOCAL_HOST_X_POSITION' else 'NA'})
  for kind,data in (('PAGE',q['page_gain']),('SECTION',q['section_gain']),('HAND',q['hand_gain'])):
   for key,val in sorted(data.items()):brows.append({'control_id':p,'breakdown':kind,'value':key,'gain_bits':f'{val:.12f}'})
  for w,val in enumerate(n):nrows.append({'control_id':p,'world_index':w,'page_local_gain_bits_per_event':f'{val:.12f}'})
 variable=[p for p in d['powered_panels'] if sds[p]>1e-15];fixed=[p for p in d['powered_panels'] if p not in variable];zs={p:(obs[p]-means[p])/sds[p] for p in variable};mx=[max((rr[p][1][i]-means[p])/sds[p] for p in variable) for i in range(64)] if variable else [];summary=[]
 for p in d['panels']:
  if p not in rr:summary.append({'control_id':p,'capacity_status':'UNSCORED_ZERO_ONLINE_CAPACITY','eligible_events':0});continue
  q,n,mob,swap=rr[p];var=p in variable;lp=(1+sum(x>=obs[p]-1e-15 for x in n))/65 if var else None;mp=(1+sum(x>=zs[p]-1e-15 for x in mx))/65 if var else None;summary.append({'control_id':p,'capacity_status':'SCORED','eligible_events':q['eligible'],'folios':len({x['physical_folio'] for x in panels[p] if x['page'] in q['page_gain']}),'pages':len(q['page_gain']),'sections':len(q['section_gain']),'increments':{k:float(f'{v:.12f}') for k,v in increments(q).items()},'positive_pages':sum(v>0 for v in q['page_gain'].values()),'positive_sections':sum(v>0 for v in q['section_gain'].values()),'null_mean':f'{means[p]:.12f}','null_sd':f'{sds[p]:.12f}','observed_z':f'{zs[p]:.12f}' if var else 'NA_ZERO_NULL_VARIANCE','local_p':f'{lp:.12f}' if var else 'NA_ZERO_NULL_VARIANCE','max_variable_family_p':f'{mp:.12f}' if var else 'NA_ZERO_NULL_VARIANCE','null_mobile_events_world0':mob,'null_swappable_events':swap})
 voy=panels['VOYNICH_REFERENCE'];sens=[]
 for prior in d['voynich_prior_sensitivities']:
  q=score(voy,prior=prior);sens.append({'prior_mass':prior,'eligible_events':q['eligible'],**increments(q)})
 write(PANEL,prows);write(FOLIO,frows);write(BREAK,brows);write(NULL,nrows);write(SENS,[{**x,**{k:f'{v:.12f}' for k,v in x.items() if k not in ('prior_mass','eligible_events')}} for x in sens]);v=next(x for x in summary if x['control_id']=='VOYNICH_REFERENCE');gates={'total_gain_positive':v['increments']['TOTAL_PAGE_LOCAL_GAIN']>0,'at_least_one_hundred_of_one_hundred_fifty_three_pages_positive':v['pages']==153 and v['positive_pages']>=100,'at_least_four_of_six_sections_positive':v['sections']==6 and v['positive_sections']>=4,'both_prior_sensitivities_positive':all(x['TOTAL_PAGE_LOCAL_GAIN']>0 for x in sens),'maxT_p_le_0_05':not str(v['max_variable_family_p']).startswith('NA') and float(v['max_variable_family_p'])<=.05};status=d['decision']['support'] if all(gates.values()) else d['decision']['fail']
 bad=min(rr['VOYNICH_REFERENCE'][0]['page_gain'].items(),key=lambda x:x[1]);counter=[{'counterexample':'PAGE_LOCAL_GAIN_NONPOSITIVE','evidence':f"Voynich {v['increments']['TOTAL_PAGE_LOCAL_GAIN']:+.6f} bits/event",'impact':'nonpositive fails adaptation'}, {'counterexample':'PAGE_CONCENTRATION','evidence':f"positive pages {v['positive_pages']}/{v['pages']}; worst {bad[0]} {bad[1]:+.6f} bits",'impact':'fewer than100 or a dominant page weakens transfer'}, {'counterexample':'SECTION_CONCENTRATION','evidence':f"positive sections {v['positive_sections']}/{v['sections']}",'impact':'fewer than4 fails breadth'}, {'counterexample':'LATIN_ZERO_CAPACITY','evidence':','.join(d['unscored_zero_capacity_panels']),'impact':'ordinary Latin page-local renderer calibration unavailable'}, {'counterexample':'ONLINE_HISTORY_IS_TARGET_FOLIO_DATA','evidence':'only earlier physical lines are used, but they belong to the held folio','impact':'this is online page adaptation, not strict held-folio transfer'}, {'counterexample':'F84_USED','evidence':'only f84-free native inventory read','impact':'no f84 access'}];write(COUNTER,counter)
 report=['# GDT295 — online page-local renderer adaptation','',f'Status: **{status}**.','','## Online line-safe result','', '| panel | capacity | eligible | total page gain | page-host | page-position | positive pages | local p | max-family p |','|---|---|---:|---:|---:|---:|---:|---:|---:|']
 for x in summary:
  if x['capacity_status']!='SCORED':report.append(f"| {x['control_id']} | UNSCORED | 0 | NA | NA | NA | NA | NA | NA |")
  else:report.append(f"| {x['control_id']} | SCORED | {x['eligible_events']} | {x['increments']['TOTAL_PAGE_LOCAL_GAIN']:+.4f} | {x['increments']['PAGE_HOST_GIVEN_CROSS_FOLIO_POSITION']:+.4f} | {x['increments']['PAGE_POSITION_GIVEN_PAGE_HOST']:+.4f} | {x['positive_pages']}/{x['pages']} | {x['local_p']} | {x['max_variable_family_p']} |")
 report+=['','All events on a physical line are scored before that line updates history. The alternative may use earlier lines from the held folio, so this is an online within-page adaptation test rather than a completely unseen-folio prediction.','','## Voynich prior sensitivities','']+[f"- prior {x['prior_mass']}: total {x['TOTAL_PAGE_LOCAL_GAIN']:+.6f}, page-host {x['PAGE_HOST_GIVEN_CROSS_FOLIO_POSITION']:+.6f}, page-position {x['PAGE_POSITION_GIVEN_PAGE_HOST']:+.6f} bits/event." for x in sens]+['','## Frozen gates','']+[f"- `{k}`: **{'PASS' if z else 'FAIL'}**" for k,z in gates.items()]+['','## Claim ceiling','','This can support only online page-local adaptation of a parser-defined renderer distribution. It cannot establish a page vocabulary meaning, lexical identity, code value, word, language, plaintext, or translation. No f84 row was opened, parsed, retained, joined, or scored.'];REPORT.write_text('\n'.join(report)+'\n')
 outputs=[PANEL,FOLIO,BREAK,NULL,SENS,COUNTER,REPORT];inputs=['gdt295_design.json','gdt295_design_validation.json','gdt295_capacity.tsv','gdt295_freeze_manifest.tsv','gdt278_native_event_inventory.tsv','gdt294_result.json','gdt293_result.json','gdt082_result.json','gdt288_result.json'];res={'schema':'GDT295_ONLINE_PAGE_LOCAL_RENDERER_RESULT_V1','status':status,'summary':summary,'voynich_summary':v,'voynich_sensitivities':sens,'frozen_gates':gates,'variable_null_panels':variable,'zero_null_variance_panels':fixed,'unscored_zero_capacity_panels':d['unscored_zero_capacity_panels'],'same_line_update_forbidden':True,'uses_earlier_held_folio_lines':True,'new_corpora':0,'new_architectures':0,'semantic_assignments':0,'page_host_substrings_mined':0,'claim_ceiling':d['claim_ceiling'],'f84':d['f84'],'inputs':{x:sha(R/x) for x in inputs},'documents':{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)},'implementation':{Path(__file__).name:sha(Path(__file__))},'outputs':{x.name:sha(x) for x in outputs}};res['content_sha256']=rcsha(res);RESULT.write_text(json.dumps(res,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':status,'voynich':v,'gates':gates},sort_keys=True))
if __name__=='__main__':main()
