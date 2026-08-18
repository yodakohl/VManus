#!/usr/bin/env python3
"""Score frozen GDT299 opaque whole-form physical-role transfer."""
from __future__ import annotations
import csv,hashlib,json,math,random,statistics
from collections import Counter,defaultdict
from pathlib import Path
R=Path(__file__).resolve().parent;D=R/'gdt299_design.json';SOURCE=R/'gdt278_native_event_inventory.tsv';METHOD=R/'GDT299_WHOLE_FORM_PHYSICAL_ROLE_TRANSFER_METHOD.md';REPORT=R/'GDT299_WHOLE_FORM_PHYSICAL_ROLE_TRANSFER_REPORT.md';SCORES=R/'gdt299_panel_scores.tsv';FOLDS=R/'gdt299_folio_scores.tsv';NULL=R/'gdt299_null_results.tsv';SENS=R/'gdt299_prior_sensitivity.tsv';COUNTER=R/'gdt299_counterexamples.tsv';RESULT=R/'gdt299_result.json';Y=('FIRST','MIDDLE','LAST')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ch(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
def rch(v):q=dict(v);q.pop('content_sha256',None);return ch(q)
def read(p):
 with Path(p).open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def write(p,rows):
 fields=[]
 for row in rows:
  for k in row:
   if k not in fields:fields.append(k)
 with Path(p).open('w',encoding='utf8',newline='') as h:w=csv.DictWriter(h,fields,delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
def outcome(x):
 i=int(x['group_index']);n=int(x['group_count']);return 'FIRST' if i==1 else 'LAST' if i==n else 'MIDDLE'
def layout(x):return (x['section'],x['currier'],x['hand'],x['group_count'])
def eligible(panel):
 base=[x for x in panel if int(x['group_count'])>=2];hf=defaultdict(set);sf=defaultdict(set)
 for x in base:hf[x['page_host']].add(x['physical_folio']);sf[x['source_surface_sha256']].add(x['physical_folio'])
 return [x for x in base if len(hf[x['page_host']])>=2 and len(sf[x['source_surface_sha256']])>=2]
def score(events,surface_ids,prior):
 glob=Counter();lc=defaultdict(Counter);hc=defaultdict(Counter);sc=defaultdict(Counter);fg=defaultdict(Counter);fl=defaultdict(lambda:defaultdict(Counter));fh=defaultdict(lambda:defaultdict(Counter));fs=defaultdict(lambda:defaultdict(Counter));fn=Counter()
 for x,sid in zip(events,surface_ids):
  y=outcome(x);f=x['physical_folio'];glob[y]+=1;lc[layout(x)][y]+=1;hc[x['page_host']][y]+=1;sc[sid][y]+=1;fg[f][y]+=1;fl[f][layout(x)][y]+=1;fh[f][x['page_host']][y]+=1;fs[f][sid][y]+=1;fn[f]+=1
 bits=Counter();tops=Counter();fold=defaultdict(Counter);alpha=.5
 for x,sid in zip(events,surface_ids):
  y=outcome(x);f=x['physical_folio'];ng=len(events)-fn[f];g={z:glob[z]-fg[f][z] for z in Y};p0={z:(g[z]+alpha)/(ng+alpha*len(Y)) for z in Y};lk=layout(x);l={z:lc[lk][z]-fl[f][lk][z] for z in Y};nl=sum(l.values());pl={z:(l[z]+prior*p0[z])/(nl+prior) for z in Y};h={z:hc[x['page_host']][z]-fh[f][x['page_host']][z] for z in Y};nh=sum(h.values());ph={z:(h[z]+prior*pl[z])/(nh+prior) for z in Y};s={z:sc[sid][z]-fs[f][sid][z] for z in Y};ns=sum(s.values());ps={z:(s[z]+prior*ph[z])/(ns+prior) for z in Y}
  for name,p in [('LAYOUT',pl),('PAGE_HOST',ph),('WHOLE_FORM',ps)]:
   loss=-math.log2(p[y]);bits[name]+=loss;fold[f][name]+=loss;pred=max(Y,key=lambda z:(p[z],-Y.index(z)));tops[name]+=pred==y;fold[f][name+'_TOP1']+=pred==y
 return {'bits':dict(bits),'top1':dict(tops),'fold':{f:dict(v) for f,v in fold.items()},'gain':bits['PAGE_HOST']-bits['WHOLE_FORM']}
def permuted(events,world,seed):
 ids=[x['source_surface_sha256'] for x in events];groups=defaultdict(list)
 for i,x in enumerate(events):groups[(x['physical_folio'],x['section'],x['currier'],x['hand'],x['group_count'],x['page_host'])].append(i)
 out=list(ids)
 for key,idx in sorted(groups.items(),key=lambda z:str(z[0])):
  vals=[ids[i] for i in idx];h=int(hashlib.sha256((seed+'|'+str(world)+'|'+json.dumps(key)).encode()).hexdigest()[:16],16);random.Random(h).shuffle(vals)
  for i,v in zip(idx,vals):out[i]=v
 return out
def main():
 d=json.loads(D.read_text());assert d['status']=='FROZEN_BEFORE_GDT299_SCORING' and d['content_sha256']==rch(d);assert sha(R/'gdt299_capacity.tsv')==d['capacity_sha256'] and sha(METHOD)==d['method_sha256'];rows=read(SOURCE);assert not any(x['page'].startswith('f84') or x['locus'].startswith('f84') for x in rows);cap={x['control_id']:x for x in read(R/'gdt299_capacity.tsv')};panels={p:eligible([x for x in rows if x['control_id']==p]) for p in sorted(cap)};obs={};foldrows=[];score_rows=[]
 for panel,ev in panels.items():
  if cap[panel]['score_capacity']!='POWERED':continue
  s=score(ev,[x['source_surface_sha256'] for x in ev],d['prior_mass']);obs[panel]=s;n=len(ev);pos=0
  for folio,z in sorted(s['fold'].items()):
   gain=z['PAGE_HOST']-z['WHOLE_FORM'];pos+=gain>0;foldrows.append({'control_id':panel,'held_folio':folio,'events':sum(x['physical_folio']==folio for x in ev),'layout_bits':f"{z['LAYOUT']:.12f}",'host_bits':f"{z['PAGE_HOST']:.12f}",'whole_form_bits':f"{z['WHOLE_FORM']:.12f}",'whole_form_gain_bits':f'{gain:.12f}','layout_top1':z['LAYOUT_TOP1'],'host_top1':z['PAGE_HOST_TOP1'],'whole_form_top1':z['WHOLE_FORM_TOP1']})
  score_rows.append({'control_id':panel,'capacity_status':cap[panel]['score_capacity'],'null_capacity':cap[panel]['null_capacity'],'events':n,'folios':len(s['fold']),'layout_bits_per_event':f"{s['bits']['LAYOUT']/n:.12f}",'host_bits_per_event':f"{s['bits']['PAGE_HOST']/n:.12f}",'whole_form_bits_per_event':f"{s['bits']['WHOLE_FORM']/n:.12f}",'host_gain_vs_layout_bits_per_event':f"{(s['bits']['LAYOUT']-s['bits']['PAGE_HOST'])/n:.12f}",'whole_form_gain_vs_host_bits_per_event':f"{s['gain']/n:.12f}",'layout_top1':f"{s['top1']['LAYOUT']/n:.12f}",'host_top1':f"{s['top1']['PAGE_HOST']/n:.12f}",'whole_form_top1':f"{s['top1']['WHOLE_FORM']/n:.12f}",'positive_folios':pos})
 nullrows=[];nullvals=defaultdict(list);mobile0={}
 for panel,ev in panels.items():
  if cap[panel]['score_capacity']!='POWERED':continue
  original=[x['source_surface_sha256'] for x in ev]
  for wi in range(d['null_worlds']):
   ids=permuted(ev,wi,d['null_seed']+'|'+panel);s=score(ev,ids,d['prior_mass']);gain=s['gain']/len(ev);nullvals[panel].append(gain);mobile=sum(a!=b for a,b in zip(original,ids));
   if wi==0:mobile0[panel]=mobile
   nullrows.append({'control_id':panel,'world_index':wi,'whole_form_gain_vs_host_bits_per_event':f'{gain:.12f}','mobile_events':mobile})
 variable=[p for p in obs if cap[p]['null_capacity']=='VARIABLE'];means={p:statistics.mean(nullvals[p]) for p in variable};sds={p:statistics.pstdev(nullvals[p]) for p in variable};zobs={p:(obs[p]['gain']/len(panels[p])-means[p])/sds[p] for p in variable if sds[p]>0};worldmax=[]
 for wi in range(d['null_worlds']):worldmax.append(max((nullvals[p][wi]-means[p])/sds[p] for p in zobs))
 for row in score_rows:
  p=row['control_id'];o=obs[p]['gain']/len(panels[p]);row['null_mean_gain']=f"{statistics.mean(nullvals[p]):.12f}";row['null_sd_gain']=f"{statistics.pstdev(nullvals[p]):.12f}";row['observed_z']=f"{zobs[p]:.12f}" if p in zobs else 'NA';row['local_p']=f"{(1+sum(v>=o-1e-15 for v in nullvals[p]))/(1+d['null_worlds']):.12f}" if p in variable else 'NA';row['max_family_p']=f"{(1+sum(v>=zobs[p]-1e-15 for v in worldmax))/(1+d['null_worlds']):.12f}" if p in zobs else 'NA';row['null_mobile_events_world0']=mobile0[p]
 sens=[];vms=panels['VOYNICH_REFERENCE']
 for prior in d['voynich_prior_sensitivities']:
  z=score(vms,[x['source_surface_sha256'] for x in vms],prior);sens.append({'control_id':'VOYNICH_REFERENCE','prior_mass':prior,'events':len(vms),'whole_form_gain_vs_host_bits_per_event':f"{z['gain']/len(vms):.12f}",'positive_folios':sum(x['PAGE_HOST']-x['WHOLE_FORM']>0 for x in z['fold'].values())})
 sm={x['control_id']:x for x in score_rows};v=sm['VOYNICH_REFERENCE'];gates={'gain_positive':float(v['whole_form_gain_vs_host_bits_per_event'])>0,'positive_folios_at_least_60':int(v['positive_folios'])>=60,'both_prior_sensitivities_positive':all(float(x['whole_form_gain_vs_host_bits_per_event'])>0 for x in sens),'max_family_p_le_0_05':float(v['max_family_p'])<=.05};status=d['decision']['support'] if all(gates.values()) else d['decision']['fail'];score_rows+= [{'control_id':p,'capacity_status':cap[p]['score_capacity'],'null_capacity':cap[p]['null_capacity'],'events':cap[p]['eligible_events'],'folios':cap[p]['eligible_folios'],'layout_bits_per_event':'NA','host_bits_per_event':'NA','whole_form_bits_per_event':'NA','host_gain_vs_layout_bits_per_event':'NA','whole_form_gain_vs_host_bits_per_event':'NA','layout_top1':'NA','host_top1':'NA','whole_form_top1':'NA','positive_folios':'NA','null_mean_gain':'NA','null_sd_gain':'NA','observed_z':'NA','local_p':'NA','max_family_p':'NA','null_mobile_events_world0':0} for p in panels if cap[p]['score_capacity']!='POWERED'];score_rows.sort(key=lambda x:x['control_id']);write(SCORES,score_rows);write(FOLDS,foldrows);write(NULL,nullrows);write(SENS,sens)
 counters=[{'counterexample_id':'C01','finding':'Whole-form identities are hashes; no spelling or substring enters the model.','impact':'Any effect is exact-form memory, not inferred morphology.'},{'counterexample_id':'C02','finding':f"Voynich host gain beyond layout is {float(v['host_gain_vs_layout_bits_per_event']):+.6f} bits/event.",'impact':'The incremental whole-form result is conditional on a possibly weak or strong host baseline.'},{'counterexample_id':'C03','finding':f"Only {v['null_mobile_events_world0']}/{v['events']} Voynich rows move in null world zero.",'impact':'Inference is limited to within-folio exact-host/layout alternant mobility.'},{'counterexample_id':'C04','finding':'Physical FIRST/MIDDLE/LAST is layout, not semantic role.','impact':'Support cannot name a grammatical or technical function.'},{'counterexample_id':'C05','finding':'Alternate readings are not independent panels.','impact':'This GDT278 native view supplies no three-sample replication.'},{'counterexample_id':'C06','finding':'No f84 row is present in the frozen source.','impact':'The seal remains intact.'}];write(COUNTER,counters)
 powered=sorted((x for x in score_rows if x['capacity_status']=='POWERED'),key=lambda x:-float(x['whole_form_gain_vs_host_bits_per_event']));report=['# GDT299 — opaque whole-form physical-role transfer','',f'Status: **{status}**.','','## Held-folio results','', '| panel | events | host gain vs layout | whole-form gain vs host | top-1 host→form | positive folios | local p | max-family p |','|---|---:|---:|---:|---:|---:|---:|---:|']
 for x in powered:report.append(f"| {x['control_id']} | {x['events']} | {float(x['host_gain_vs_layout_bits_per_event']):+.4f} | {float(x['whole_form_gain_vs_host_bits_per_event']):+.4f} | {float(x['host_top1']):.3f}→{float(x['whole_form_top1']):.3f} | {x['positive_folios']}/{x['folios']} | {x['local_p']} | {x['max_family_p']} |")
 report+=['','## Voynich interpretation','',f"On {v['events']} held-folio events, opaque whole-form identity changes physical-position codelength by **{float(v['whole_form_gain_vs_host_bits_per_event']):+.6f} bits/event** beyond PAGE_HOST. Top-1 changes from {float(v['host_top1']):.3f} to {float(v['whole_form_top1']):.3f}; {v['positive_folios']}/91 folios improve. The prior-5/prior-22 sensitivities are {float(sens[0]['whole_form_gain_vs_host_bits_per_event']):+.6f} and {float(sens[1]['whole_form_gain_vs_host_bits_per_event']):+.6f}. Frozen gates are `{json.dumps(gates,sort_keys=True)}`.",'', 'This is the direct functional test of GDT298 joint-form alternants. A positive result means complete opaque forms carry reusable physical line-placement information beyond stripped hosts; a negative result means the high-capacity alternants remain memory without this external structural role. Controls calibrate whether the same property is ordinary in readable or synthetic systems.','','## Claim ceiling','',d['claim_ceiling']+' No source string was inspected and no f84 row was opened, parsed, retained, joined, or scored.'];REPORT.write_text('\n'.join(report)+'\n')
 outputs=[SCORES,FOLDS,NULL,SENS,COUNTER,REPORT];inputs=['gdt299_design.json','gdt299_design_validation.json','gdt299_capacity.tsv','gdt299_freeze_manifest.tsv','gdt278_native_event_inventory.tsv','gdt298_result.json','gdt297_result.json'];res={'schema':'GDT299_WHOLE_FORM_PHYSICAL_ROLE_TRANSFER_RESULT_V1','status':status,'panels':len(panels),'powered_panels':len(powered),'null_variable_panels':len(variable),'voynich_summary':v,'voynich_prior_sensitivities':sens,'gates':gates,'source_strings_inspected':0,'page_host_substrings_mined':0,'semantic_assignments':0,'claim_ceiling':d['claim_ceiling'],'f84':d['f84'],'inputs':{x:sha(R/x) for x in inputs},'documents':{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)},'implementation':{Path(__file__).name:sha(Path(__file__))},'outputs':{x.name:sha(x) for x in outputs}};res['content_sha256']=rch(res);RESULT.write_text(json.dumps(res,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':status,'voynich_gain':v['whole_form_gain_vs_host_bits_per_event'],'positive_folios':v['positive_folios'],'max_p':v['max_family_p']},sort_keys=True))
if __name__=='__main__':main()
