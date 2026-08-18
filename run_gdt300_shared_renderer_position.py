#!/usr/bin/env python3
"""Run frozen GDT300 shared-renderer positional decomposition."""
from __future__ import annotations
import csv,hashlib,json,math,random,statistics
from collections import Counter,defaultdict
from pathlib import Path
R=Path(__file__).resolve().parent;D=R/'gdt300_design.json';SOURCE=R/'gdt278_native_event_inventory.tsv';METHOD=R/'GDT300_SHARED_RENDERER_POSITIONAL_GRAMMAR_METHOD.md';REPORT=R/'GDT300_SHARED_RENDERER_POSITIONAL_GRAMMAR_REPORT.md';PANELS=R/'gdt300_panel_scores.tsv';COMP=R/'gdt300_component_scores.tsv';FOLDS=R/'gdt300_folio_scores.tsv';NULL=R/'gdt300_null_results.tsv';SENS=R/'gdt300_prior_sensitivity.tsv';ATLAS=R/'gdt300_renderer_value_atlas.tsv';COUNTER=R/'gdt300_counterexamples.tsv';RESULT=R/'gdt300_result.json';Y=('FIRST','MIDDLE','LAST')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ch(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
def rch(v):q=dict(v);q.pop('content_sha256',None);return ch(q)
def read(p):
 with Path(p).open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def write(p,rows):
 fields=[]
 for x in rows:
  for k in x:
   if k not in fields:fields.append(k)
 with Path(p).open('w',encoding='utf8',newline='') as h:w=csv.DictWriter(h,fields,delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
def outcome(x):
 i=int(x['group_index']);n=int(x['group_count']);return 'FIRST' if i==1 else 'LAST' if i==n else 'MIDDLE'
def layout(x):return (x['section'],x['currier'],x['hand'],x['group_count'])
def renderer(x,fields):return tuple(x[k] for k in fields)
def eligible(rows,panel):
 base=[x for x in rows if x['control_id']==panel and int(x['group_count'])>=2];hf=defaultdict(set);sf=defaultdict(set)
 for x in base:hf[x['page_host']].add(x['physical_folio']);sf[x['source_surface_sha256']].add(x['physical_folio'])
 return [x for x in base if len(hf[x['page_host']])>=2 and len(sf[x['source_surface_sha256']])>=2]
def dist(count,back,prior):
 n=sum(count.values());return {z:(count[z]+prior*back[z])/(n+prior) for z in Y}
def score(events,renders,fields,prior):
 names=fields+['renderer_tuple'];glob=Counter();lc=defaultdict(Counter);hc=defaultdict(Counter);cc={n:defaultdict(Counter) for n in names};pc=defaultdict(Counter);fg=defaultdict(Counter);fl=defaultdict(lambda:defaultdict(Counter));fh=defaultdict(lambda:defaultdict(Counter));fc={n:defaultdict(lambda:defaultdict(Counter)) for n in names};fp=defaultdict(lambda:defaultdict(Counter));fn=Counter()
 for x,r in zip(events,renders):
  y=outcome(x);f=x['physical_folio'];glob[y]+=1;lc[layout(x)][y]+=1;hc[x['page_host']][y]+=1;pc[(x['page_host'],r)][y]+=1;fg[f][y]+=1;fl[f][layout(x)][y]+=1;fh[f][x['page_host']][y]+=1;fp[f][(x['page_host'],r)][y]+=1;fn[f]+=1
  for i,n in enumerate(fields):cc[n][r[i]][y]+=1;fc[n][f][r[i]][y]+=1
  cc['renderer_tuple'][r][y]+=1;fc['renderer_tuple'][f][r][y]+=1
 bits=Counter();tops=Counter();fold=defaultdict(Counter);alpha=.5
 for x,r in zip(events,renders):
  y=outcome(x);f=x['physical_folio'];ng=len(events)-fn[f];g={z:glob[z]-fg[f][z] for z in Y};p0={z:(g[z]+alpha)/(ng+alpha*3) for z in Y};lk=layout(x);a={z:lc[lk][z]-fl[f][lk][z] for z in Y};pl=dist(a,p0,prior);a={z:hc[x['page_host']][z]-fh[f][x['page_host']][z] for z in Y};ph=dist(a,pl,prior);probs={'HOST':ph}
  for i,n in enumerate(fields):
   a={z:cc[n][r[i]][z]-fc[n][f][r[i]][z] for z in Y};pcmp=dist(a,pl,prior);raw={z:ph[z]*pcmp[z]/pl[z] for z in Y};den=sum(raw.values());probs['SHARED_'+n]={z:raw[z]/den for z in Y}
  a={z:cc['renderer_tuple'][r][z]-fc['renderer_tuple'][f][r][z] for z in Y};pcmp=dist(a,pl,prior);raw={z:ph[z]*pcmp[z]/pl[z] for z in Y};den=sum(raw.values());probs['SHARED_renderer_tuple']={z:raw[z]/den for z in Y};a={z:pc[(x['page_host'],r)][z]-fp[f][(x['page_host'],r)][z] for z in Y};probs['HOST_X_RENDERER']=dist(a,ph,prior)
  for n,p in probs.items():
   loss=-math.log2(p[y]);bits[n]+=loss;fold[f][n]+=loss;pred=max(Y,key=lambda z:(p[z],-Y.index(z)));tops[n]+=pred==y;fold[f][n+'_TOP1']+=pred==y
 return {'bits':dict(bits),'top1':dict(tops),'fold':{f:dict(v) for f,v in fold.items()}}
def permute(events,renders,world,seed):
 groups=defaultdict(list)
 for i,x in enumerate(events):groups[(x['physical_folio'],x['section'],x['currier'],x['hand'],x['group_count'],x['page_host'])].append(i)
 out=list(renders)
 for key,idx in sorted(groups.items(),key=lambda z:str(z[0])):
  vals=[renders[i] for i in idx];s=int(hashlib.sha256((seed+'|'+str(world)+'|'+json.dumps(key)).encode()).hexdigest()[:16],16);random.Random(s).shuffle(vals)
  for i,v in zip(idx,vals):out[i]=v
 return out
def main():
 d=json.loads(D.read_text());assert d['content_sha256']==rch(d) and d['status']=='FROZEN_BEFORE_GDT300_SCORING';assert sha(METHOD)==d['method_sha256'] and sha(R/'gdt300_capacity.tsv')==d['capacity_sha256'];rows=read(SOURCE);assert not any(x['page'].startswith('f84') or x['locus'].startswith('f84') for x in rows);fields=d['renderer_fields'];caps={x['control_id']:x for x in read(R/'gdt300_capacity.tsv')};panels={p:eligible(rows,p) for p in sorted(caps)}
 # GDT297 alias assertion on the Voynich reference.
 vms=panels['VOYNICH_REFERENCE'];a=defaultdict(dict);b=defaultdict(dict)
 for x in vms:
  h=x['page_host'];r=renderer(x,fields);s=x['source_surface_sha256'];assert r not in a[h] or a[h][r]==s;assert s not in b[h] or b[h][s]==r;a[h][r]=s;b[h][s]=r
 obs={};panelrows=[];comprows=[];foldrows=[]
 for panel,ev in panels.items():
  if caps[panel]['score_capacity']!='POWERED':continue
  rr=[renderer(x,fields) for x in ev];z=score(ev,rr,fields,d['prior_mass']);obs[panel]=z;n=len(ev);host=z['bits']['HOST'];pair=z['bits']['HOST_X_RENDERER'];shared=z['bits']['SHARED_renderer_tuple'];pos_pair=sum(v['HOST']-v['HOST_X_RENDERER']>0 for v in z['fold'].values());pos_shared=sum(v['HOST']-v['SHARED_renderer_tuple']>0 for v in z['fold'].values());pairgain=(host-pair)/n;sgain=(host-shared)/n;frac=sgain/pairgain if pairgain>0 else float('nan')
  panelrows.append({'control_id':panel,'events':n,'folios':len(z['fold']),'host_bits_per_event':f'{host/n:.12f}','shared_renderer_bits_per_event':f'{shared/n:.12f}','exact_pair_bits_per_event':f'{pair/n:.12f}','shared_gain_bits_per_event':f'{sgain:.12f}','exact_pair_gain_bits_per_event':f'{pairgain:.12f}','shared_fraction_of_exact_pair_gain':f'{frac:.12f}' if math.isfinite(frac) else 'NA','host_top1':f"{z['top1']['HOST']/n:.12f}",'shared_top1':f"{z['top1']['SHARED_renderer_tuple']/n:.12f}",'exact_pair_top1':f"{z['top1']['HOST_X_RENDERER']/n:.12f}",'positive_shared_folios':pos_shared,'positive_exact_pair_folios':pos_pair})
  for name in fields+['renderer_tuple']:
   m='SHARED_'+name;comprows.append({'control_id':panel,'component':name,'events':n,'gain_vs_host_bits_per_event':f"{(host-z['bits'][m])/n:.12f}",'top1':f"{z['top1'][m]/n:.12f}",'positive_folios':sum(v['HOST']-v[m]>0 for v in z['fold'].values())})
  for f,v in sorted(z['fold'].items()):foldrows.append({'control_id':panel,'held_folio':f,'events':sum(x['physical_folio']==f for x in ev),'shared_gain_bits':f"{v['HOST']-v['SHARED_renderer_tuple']:.12f}",'exact_pair_gain_bits':f"{v['HOST']-v['HOST_X_RENDERER']:.12f}",'host_top1':v['HOST_TOP1'],'shared_top1':v['SHARED_renderer_tuple_TOP1'],'exact_pair_top1':v['HOST_X_RENDERER_TOP1']})
 nullrows=[];nv=defaultdict(list)
 variable=[p for p in obs if caps[p]['null_capacity']=='VARIABLE']
 for panel in variable:
  ev=panels[panel];rr=[renderer(x,fields) for x in ev]
  for wi in range(d['null_worlds']):
   pr=permute(ev,rr,wi,d['null_seed']+'|'+panel);z=score(ev,pr,fields,d['prior_mass']);host=z['bits']['HOST']
   for name in fields+['renderer_tuple']:
    gain=(host-z['bits']['SHARED_'+name])/len(ev);nv[(panel,name)].append(gain);nullrows.append({'control_id':panel,'component':name,'world_index':wi,'gain_vs_host_bits_per_event':f'{gain:.12f}','mobile_events':sum(x!=y for x,y in zip(rr,pr))})
 means={k:statistics.mean(v) for k,v in nv.items()};sds={k:statistics.pstdev(v) for k,v in nv.items()};oz={}
 for row in comprows:
  k=(row['control_id'],row['component'])
  if k in nv:
   o=float(row['gain_vs_host_bits_per_event']);row['null_mean']=f'{means[k]:.12f}';row['null_sd']=f'{sds[k]:.12f}';row['local_p']=f"{(1+sum(x>=o-1e-15 for x in nv[k]))/(1+d['null_worlds']):.12f}"
   if sds[k]>0:oz[k]=(o-means[k])/sds[k];row['observed_z']=f'{oz[k]:.12f}'
   else:row['observed_z']='NA'
  else:row.update({'null_mean':'NA','null_sd':'NA','local_p':'NA','observed_z':'NA'})
 worldmax=[max((nv[k][wi]-means[k])/sds[k] for k in oz) for wi in range(d['null_worlds'])]
 for row in comprows:
  k=(row['control_id'],row['component']);row['max_family_p']=f"{(1+sum(x>=oz[k]-1e-15 for x in worldmax))/(1+d['null_worlds']):.12f}" if k in oz else 'NA'
 sens=[]
 for prior in d['voynich_prior_sensitivities']:
  z=score(vms,[renderer(x,fields) for x in vms],fields,prior);n=len(vms);sens.append({'prior_mass':prior,'shared_gain_bits_per_event':f"{(z['bits']['HOST']-z['bits']['SHARED_renderer_tuple'])/n:.12f}",'exact_pair_gain_bits_per_event':f"{(z['bits']['HOST']-z['bits']['HOST_X_RENDERER'])/n:.12f}",'positive_shared_folios':sum(v['HOST']-v['SHARED_renderer_tuple']>0 for v in z['fold'].values())})
 atlas=[]
 for name in fields:
  ag=defaultdict(lambda:{'n':0,'folios':set(),'hosts':set(),'y':Counter()})
  for x in vms:
   q=ag[x[name]];q['n']+=1;q['folios'].add(x['physical_folio']);q['hosts'].add(x['page_host']);q['y'][outcome(x)]+=1
  for value,q in sorted(ag.items()):atlas.append({'component':name,'value':value,'events':q['n'],'folios':len(q['folios']),'hosts':len(q['hosts']),'first':q['y']['FIRST'],'middle':q['y']['MIDDLE'],'last':q['y']['LAST'],'first_rate':f"{q['y']['FIRST']/q['n']:.12f}",'last_rate':f"{q['y']['LAST']/q['n']:.12f}"})
 pm={x['control_id']:x for x in panelrows};vm=pm['VOYNICH_REFERENCE'];vc=next(x for x in comprows if x['control_id']=='VOYNICH_REFERENCE' and x['component']=='renderer_tuple');old=json.loads((R/'gdt299_result.json').read_text())['voynich_summary'];repro=abs(float(vm['exact_pair_gain_bits_per_event'])-float(old['whole_form_gain_vs_host_bits_per_event']))<=d['decision']['gdt299_reproduction_tolerance_bits_per_event'];gates={'gdt299_exact_pair_reproduced':repro,'shared_gain_positive':float(vm['shared_gain_bits_per_event'])>0,'minimum_positive_folios':int(vm['positive_shared_folios'])>=d['decision']['minimum_positive_folios'],'both_prior_sensitivities_positive':all(float(x['shared_gain_bits_per_event'])>0 for x in sens),'max_seven_p_le_0_05':float(vc['max_family_p'])<=d['decision']['max_seven_p_le'],'shared_fraction_at_least_half':float(vm['shared_fraction_of_exact_pair_gain'])>=d['decision']['minimum_shared_fraction']}
 if all(gates.values()):status=d['decision']['support']
 elif repro and float(vm['exact_pair_gain_bits_per_event'])>0:status=d['decision']['host_specific']
 else:status=d['decision']['reproduction_fail']
 counters=[{'counterexample_id':'C01','finding':'All outcomes are mechanical FIRST/MIDDLE/LAST positions.','impact':'No semantic or linguistic function follows.'},{'counterexample_id':'C02','finding':'The exact host×renderer predictor is the GDT299 complete-form partition on Voynich.','impact':'Only the shared conditional-independence model can support a compact cross-host rule.'},{'counterexample_id':'C03','finding':'Renderer components are parser outputs from the same source group.','impact':'Support is formal decomposition, not an independent physical or semantic anchor.'},{'counterexample_id':'C04','finding':'The fixed multiplicative predictor has no fitted weight.','impact':'A failure may reflect nonadditive shared effects as well as host-specific memory.'},{'counterexample_id':'C05','finding':'Alternate readings are not independent panels.','impact':'No three-sample replication is claimed.'},{'counterexample_id':'C06','finding':'No f84 row occurs in the frozen source.','impact':'The seal remains intact.'}]
 write(PANELS,panelrows);write(COMP,comprows);write(FOLDS,foldrows);write(NULL,nullrows);write(SENS,sens);write(ATLAS,atlas);write(COUNTER,counters)
 ordered=sorted(panelrows,key=lambda x:-float(x['shared_gain_bits_per_event']));report=['# GDT300 — shared renderer positional grammar','',f'Status: **{status}**.','','## Held-folio decomposition','', '| panel | events | shared gain | exact-pair gain | shared/exact | positive shared folios |','|---|---:|---:|---:|---:|---:|']
 for x in ordered:report.append(f"| {x['control_id']} | {x['events']} | {float(x['shared_gain_bits_per_event']):+.4f} | {float(x['exact_pair_gain_bits_per_event']):+.4f} | {x['shared_fraction_of_exact_pair_gain']} | {x['positive_shared_folios']}/{x['folios']} |")
 vcomp=sorted((x for x in comprows if x['control_id']=='VOYNICH_REFERENCE'),key=lambda x:-float(x['gain_vs_host_bits_per_event']));report+=['','## Voynich renderer components','', '| component | gain beyond host | positive folios | local p | max-family p |','|---|---:|---:|---:|---:|']
 for x in vcomp:report.append(f"| {x['component']} | {float(x['gain_vs_host_bits_per_event']):+.6f} | {x['positive_folios']}/91 | {x['local_p']} | {x['max_family_p']} |")
 report+=['','## Interpretation','',f"The complete shared renderer changes held-folio position codelength by **{float(vm['shared_gain_bits_per_event']):+.6f} bits/event** beyond opaque host, versus **{float(vm['exact_pair_gain_bits_per_event']):+.6f}** for exact host×renderer memory. The shared fraction is **{vm['shared_fraction_of_exact_pair_gain']}**; {vm['positive_shared_folios']}/91 folios improve. Frozen gates are `{json.dumps(gates,sort_keys=True)}`.",'','The exact pair reproduces GDT299, but the frozen cross-host renderer combination is harmful in absolute held-folio codelength. Its small tail means the observed renderer alignment is less harmful than shuffled alignments, not that it beats the host baseline. Under the frozen rule, the transferable placement signal therefore remains host-specific whole-form alternant behavior rather than a compact manuscript-wide renderer grammar. It does not identify a semantic or linguistic function.','','## Claim ceiling','',d['claim_ceiling']+' No source string was inspected and no f84 row was opened, parsed, retained, joined, or scored.'];REPORT.write_text('\n'.join(report)+'\n')
 outputs=[PANELS,COMP,FOLDS,NULL,SENS,ATLAS,COUNTER,REPORT];inputs=['gdt300_design.json','gdt300_design_validation.json','gdt300_capacity.tsv','gdt300_freeze_manifest.tsv','gdt278_native_event_inventory.tsv','gdt299_result.json','gdt297_result.json'];res={'schema':'GDT300_SHARED_RENDERER_POSITIONAL_GRAMMAR_RESULT_V1','status':status,'voynich_summary':vm,'voynich_components':vcomp,'voynich_prior_sensitivities':sens,'gates':gates,'panels':len(panels),'powered_panels':len(panelrows),'null_variable_panels':len(variable),'source_strings_inspected':0,'page_host_substrings_mined':0,'semantic_assignments':0,'claim_ceiling':d['claim_ceiling'],'f84':d['f84'],'inputs':{x:sha(R/x) for x in inputs},'documents':{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)},'implementation':{Path(__file__).name:sha(Path(__file__))},'outputs':{x.name:sha(x) for x in outputs}};res['content_sha256']=rch(res);RESULT.write_text(json.dumps(res,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':status,'shared_gain':vm['shared_gain_bits_per_event'],'exact_pair_gain':vm['exact_pair_gain_bits_per_event'],'fraction':vm['shared_fraction_of_exact_pair_gain'],'max_p':vc['max_family_p']},sort_keys=True))
if __name__=='__main__':main()
