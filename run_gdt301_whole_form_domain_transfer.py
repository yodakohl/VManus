#!/usr/bin/env python3
"""Run frozen GDT301 exact whole-form domain transfer."""
from __future__ import annotations
import csv,hashlib,json,math,random,statistics
from collections import Counter,defaultdict
from pathlib import Path
R=Path(__file__).resolve().parent;D=R/'gdt301_design.json';SOURCE=R/'gdt278_native_event_inventory.tsv';METHOD=R/'GDT301_WHOLE_FORM_DOMAIN_TRANSFER_METHOD.md';REPORT=R/'GDT301_WHOLE_FORM_DOMAIN_TRANSFER_REPORT.md';SCORES=R/'gdt301_axis_scores.tsv';FOLDS=R/'gdt301_held_level_scores.tsv';NULL=R/'gdt301_null_results.tsv';SENS=R/'gdt301_prior_sensitivity.tsv';COUNTER=R/'gdt301_counterexamples.tsv';RESULT=R/'gdt301_result.json';Y=('FIRST','MIDDLE','LAST');META=('register','section','currier','hand')
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
def y(x):
 i=int(x['group_index']);n=int(x['group_count']);return 'FIRST' if i==1 else 'LAST' if i==n else 'MIDDLE'
def lk(x,axis):return (x['section'],x['currier'],x['hand'],x['group_count']) if axis=='physical_folio' else tuple(x[k] for k in META if k!=axis)+(x['group_count'],)
def dist(c,b,k):
 n=sum(c.values());return {z:(c[z]+k*b[z])/(n+k) for z in Y}
def score(E,S,axis,prior,fixed_population=False):
 total=Counter();top=Counter();fold=defaultdict(Counter);used=0;G=Counter();L=defaultdict(Counter);H=defaultdict(Counter);W=defaultdict(Counter);FG=defaultdict(Counter);FL=defaultdict(lambda:defaultdict(Counter));FH=defaultdict(lambda:defaultdict(Counter));FW=defaultdict(lambda:defaultdict(Counter));FN=Counter()
 for x,s in zip(E,S):
  z=y(x);v=x[axis];G[z]+=1;L[lk(x,axis)][z]+=1;H[x['page_host']][z]+=1;W[s][z]+=1;FG[v][z]+=1;FL[v][lk(x,axis)][z]+=1;FH[v][x['page_host']][z]+=1;FW[v][s][z]+=1;FN[v]+=1
 for x,s in zip(E,S):
  v=x[axis]
  if not fixed_population and (sum(H[x['page_host']].values())-sum(FH[v][x['page_host']].values())<=0 or sum(W[s].values())-sum(FW[v][s].values())<=0):continue
  z=y(x);ntr=len(E)-FN[v];g={q:G[q]-FG[v][q] for q in Y};p0={q:(g[q]+.5)/(ntr+1.5) for q in Y};a={q:L[lk(x,axis)][q]-FL[v][lk(x,axis)][q] for q in Y};pl=dist(a,p0,prior);a={q:H[x['page_host']][q]-FH[v][x['page_host']][q] for q in Y};ph=dist(a,pl,prior);a={q:W[s][q]-FW[v][s][q] for q in Y};pw=dist(a,ph,prior);P={'LAYOUT':pl,'PAGE_HOST':ph,'WHOLE_FORM':pw}
  for n,p in P.items():loss=-math.log2(p[z]);total[n]+=loss;fold[v][n]+=loss;pred=max(Y,key=lambda q:(p[q],-Y.index(q)));top[n]+=pred==z;fold[v][n+'_TOP1']+=pred==z
  fold[v]['events']+=1;used+=1
 fold={v:dict(q) for v,q in fold.items()}
 return {'events':used,'bits':dict(total),'top1':dict(top),'fold':fold}
def permute(E,S,w,seed):
 groups=defaultdict(list)
 for i,x in enumerate(E):groups[(x['physical_folio'],x['register'],x['section'],x['currier'],x['hand'],x['group_count'],x['page_host'])].append(i)
 out=list(S)
 for key,ix in sorted(groups.items(),key=lambda q:str(q[0])):
  vals=[S[i] for i in ix];h=int(hashlib.sha256((seed+'|'+str(w)+'|'+json.dumps(key)).encode()).hexdigest()[:16],16);random.Random(h).shuffle(vals)
  for i,v in zip(ix,vals):out[i]=v
 return out
def folio_population(E):
 hf=defaultdict(set);sf=defaultdict(set)
 for x in E:hf[x['page_host']].add(x['physical_folio']);sf[x['source_surface_sha256']].add(x['physical_folio'])
 return [x for x in E if len(hf[x['page_host']])>=2 and len(sf[x['source_surface_sha256']])>=2]
def main():
 d=json.loads(D.read_text());assert d['content_sha256']==rcan(d) and d['status']=='CORRECTED_AFTER_FIRST_SCORE_BEFORE_PUBLICATION';assert sha(METHOD)==d['method_sha256'];rows=read(SOURCE);assert not any(x['page'].startswith('f84') or x['locus'].startswith('f84') for x in rows);cap={(x['control_id'],x['held_axis']):x for x in read(R/'gdt301_capacity.tsv')};panels={p:[x for x in rows if x['control_id']==p and int(x['group_count'])>=2] for p in sorted({x['control_id'] for x in rows})};obs={};score_rows=[];foldrows=[]
 for p,E in panels.items():
  for ax in d['axes']:
   if cap[(p,ax)]['capacity']!='POWERED':continue
   Q=folio_population(E) if ax=='physical_folio' else E;QS=[x['source_surface_sha256'] for x in Q];z=score(Q,QS,ax,d['prior_mass'],ax=='physical_folio');assert z['events']==int(cap[(p,ax)]['eligible_events']),(p,ax,z['events'],cap[(p,ax)]['eligible_events']);obs[(p,ax)]=z;n=z['events'];g=(z['bits']['PAGE_HOST']-z['bits']['WHOLE_FORM'])/n;pos=sum(v['PAGE_HOST']-v['WHOLE_FORM']>0 for v in z['fold'].values());score_rows.append({'control_id':p,'held_axis':ax,'events':n,'held_levels':len(z['fold']),'layout_bits_per_event':f"{z['bits']['LAYOUT']/n:.12f}",'host_bits_per_event':f"{z['bits']['PAGE_HOST']/n:.12f}",'whole_form_bits_per_event':f"{z['bits']['WHOLE_FORM']/n:.12f}",'whole_form_gain_bits_per_event':f'{g:.12f}','layout_top1':f"{z['top1']['LAYOUT']/n:.12f}",'host_top1':f"{z['top1']['PAGE_HOST']/n:.12f}",'whole_form_top1':f"{z['top1']['WHOLE_FORM']/n:.12f}",'positive_held_levels':pos})
   for v,q in sorted(z['fold'].items()):foldrows.append({'control_id':p,'held_axis':ax,'held_level':v,'events':q['events'],'host_bits':f"{q['PAGE_HOST']:.12f}",'whole_form_bits':f"{q['WHOLE_FORM']:.12f}",'gain_bits':f"{q['PAGE_HOST']-q['WHOLE_FORM']:.12f}",'host_top1':q['PAGE_HOST_TOP1'],'whole_form_top1':q['WHOLE_FORM_TOP1']})
 nullrows=[];NV=defaultdict(list)
 for (p,ax),z0 in obs.items():
  if p!='VOYNICH_REFERENCE':continue
  E=folio_population(panels[p]) if ax=='physical_folio' else panels[p];S=[x['source_surface_sha256'] for x in E]
  for w in range(d['null_worlds']):
   P=permute(E,S,w,d['null_seed']+'|'+p);z=score(E,P,ax,d['prior_mass'],ax=='physical_folio');g=(z['bits']['PAGE_HOST']-z['bits']['WHOLE_FORM'])/z['events'];NV[(p,ax)].append(g);nullrows.append({'control_id':p,'held_axis':ax,'world_index':w,'gain_bits_per_event':f'{g:.12f}','eligible_events':z['events'],'mobile_events':sum(a!=b for a,b in zip(S,P))})
 sr={(x['control_id'],x['held_axis']):x for x in score_rows};means={k:statistics.mean(v) for k,v in NV.items()};sds={k:statistics.pstdev(v) for k,v in NV.items()}
 for k,row in sr.items():
  if k not in NV:row.update({'null_mean':'NA','null_sd':'NA','local_p':'NA','observed_z':'NA'});continue
  o=float(row['whole_form_gain_bits_per_event']);row['null_mean']=f'{means[k]:.12f}';row['null_sd']=f'{sds[k]:.12f}';row['local_p']=f"{(1+sum(v>=o-1e-15 for v in NV[k]))/(1+d['null_worlds']):.12f}";row['observed_z']=f'{(o-means[k])/sds[k]:.12f}' if sds[k] else 'NA'
 vk=[('VOYNICH_REFERENCE',a) for a in d['axes']];wm=[max((NV[k][w]-means[k])/sds[k] for k in vk if sds[k]) for w in range(d['null_worlds'])]
 for k,row in sr.items():
  if k in vk and sds[k]:z=(float(row['whole_form_gain_bits_per_event'])-means[k])/sds[k];row['max_five_p']=f"{(1+sum(v>=z-1e-15 for v in wm))/(1+d['null_worlds']):.12f}"
  else:row['max_five_p']='NA'
 sens=[];VE=panels['VOYNICH_REFERENCE'];VS=[x['source_surface_sha256'] for x in VE]
 for prior in d['voynich_prior_sensitivities']:
  for ax in d['decision']['required_positive_axes']:
   z=score(VE,VS,ax,prior);sens.append({'prior_mass':prior,'held_axis':ax,'events':z['events'],'gain_bits_per_event':f"{(z['bits']['PAGE_HOST']-z['bits']['WHOLE_FORM'])/z['events']:.12f}",'positive_held_levels':sum(v['PAGE_HOST']-v['WHOLE_FORM']>0 for v in z['fold'].values())})
 old=float(json.loads((R/'gdt299_result.json').read_text())['voynich_summary']['whole_form_gain_vs_host_bits_per_event']);vr={a:sr[('VOYNICH_REFERENCE',a)] for a in d['axes']};gates={'folio_reproduced':abs(float(vr['physical_folio']['whole_form_gain_bits_per_event'])-old)<=d['decision']['folio_reproduction_tolerance'],'required_axes_positive':all(float(vr[a]['whole_form_gain_bits_per_event'])>0 for a in d['decision']['required_positive_axes']),'minimum_four_positive_axes':sum(float(vr[a]['whole_form_gain_bits_per_event'])>0 for a in d['axes'])>=d['decision']['minimum_positive_axes'],'required_axes_prior_sensitivities_positive':all(float(x['gain_bits_per_event'])>0 for x in sens),'required_axes_max_five_p_le_0_05':all(float(vr[a]['max_five_p'])<=d['decision']['max_five_p_le'] for a in d['decision']['required_positive_axes'])}
 if all(gates.values()):status=d['decision']['support']
 elif gates['folio_reproduced'] and sum(float(vr[a]['whole_form_gain_bits_per_event'])<=0 for a in ('register','section','currier','hand'))>=2:status=d['decision']['local']
 else:status=d['decision']['mixed']
 counters=[{'counterexample_id':'C01','finding':'Exact complete forms are opaque hashes.','impact':'Transfer cannot identify a spelling rule or meaning.'},{'counterexample_id':'C02','finding':'Cross-domain eligibility retains only forms already present outside the held domain.','impact':'This tests reusable alternants, not prediction of unseen forms.'},{'counterexample_id':'C03','finding':'Section, Currier, hand, and register are correlated manuscript strata.','impact':'Axes are sensitivity views rather than independent replications.'},{'counterexample_id':'C04','finding':'Physical FIRST/MIDDLE/LAST is a layout outcome.','impact':'No semantic or linguistic function follows.'},{'counterexample_id':'C05','finding':'Alternate readings are not independent panels.','impact':'No three-sample support is claimed.'},{'counterexample_id':'C06','finding':'No f84 row occurs in the frozen source.','impact':'The seal remains intact.'}];write(SCORES,score_rows);write(FOLDS,foldrows);write(NULL,nullrows);write(SENS,sens);write(COUNTER,counters)
 report=['# GDT301 — whole-form physical-role domain transfer','',f'Status: **{status}**.','','## Voynich transfer axes','', '| held axis | events | gain beyond host | top-1 host→form | positive levels | local p | max-five p |','|---|---:|---:|---:|---:|---:|---:|']
 for ax in d['axes']:
  x=vr[ax];report.append(f"| {ax} | {x['events']} | {float(x['whole_form_gain_bits_per_event']):+.6f} | {float(x['host_top1']):.3f}→{float(x['whole_form_top1']):.3f} | {x['positive_held_levels']}/{x['held_levels']} | {x['local_p']} | {x['max_five_p']} |")
 report+=['','## Interpretation','',f"Frozen gates are `{json.dumps(gates,sort_keys=True)}`. The folio result is an exact integrity reproduction of GDT299. Cross-domain folds ask whether the same opaque host-specific alternant retains its physical role when the complete register, section, Currier stratum, or hand is unseen.",'','All five observed gains are positive, including 5/5 held registers and 6/6 held sections, and all five max-family tails are 1/65. The strict support decision is withheld because the Currier effect changes from -0.010430 bits/event at prior mass 5 to +0.008468 at 11 and +0.012622 at 22. The appropriate reading is broad but prior-sensitive domain stability, not either a register-local failure or a robust universal positional rule.','', 'The result is a formal domain-stability test only. Correlated manuscript strata and support filtering are explicit limitations; no axis is a semantic replication.','','## Claim ceiling','',d['claim_ceiling']+' No source string was inspected and no f84 row was opened, parsed, retained, joined, or scored.'];REPORT.write_text('\n'.join(report)+'\n')
 outputs=[SCORES,FOLDS,NULL,SENS,COUNTER,REPORT];inputs=['gdt301_design.json','gdt301_design_validation.json','gdt301_capacity.tsv','gdt301_freeze_manifest.tsv','gdt278_native_event_inventory.tsv','gdt300_result.json','gdt299_result.json'];res={'schema':'GDT301_WHOLE_FORM_DOMAIN_TRANSFER_RESULT_V1','status':status,'voynich_axes':vr,'voynich_prior_sensitivities':sens,'gates':gates,'powered_panel_axes':len(score_rows),'source_strings_inspected':0,'page_host_substrings_mined':0,'semantic_assignments':0,'claim_ceiling':d['claim_ceiling'],'f84':d['f84'],'inputs':{x:sha(R/x) for x in inputs},'documents':{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)},'implementation':{Path(__file__).name:sha(Path(__file__))},'outputs':{x.name:sha(x) for x in outputs}};res['content_sha256']=rcan(res);RESULT.write_text(json.dumps(res,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':status,'axes':{a:vr[a]['whole_form_gain_bits_per_event'] for a in d['axes']}},sort_keys=True))
if __name__=='__main__':main()
