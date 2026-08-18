#!/usr/bin/env python3
"""Build frozen GDT302 host-specific positional alternant atlas."""
import csv,hashlib,json,math
from collections import Counter,defaultdict
from pathlib import Path
R=Path(__file__).resolve().parent;D=R/'gdt302_design.json';NATIVE=R/'gdt278_native_event_inventory.tsv';RAW=R/'gdt276_event_inventory.tsv';METHOD=R/'GDT302_HOST_POSITIONAL_ALTERNANT_ATLAS_METHOD.md';REPORT=R/'GDT302_HOST_POSITIONAL_ALTERNANT_ATLAS_REPORT.md';ATLAS=R/'gdt302_positional_alternants.tsv';PAIRS=R/'gdt302_contrast_pairs.tsv';CONC=R/'gdt302_gain_concentration.tsv';COUNTER=R/'gdt302_counterexamples.tsv';RESULT=R/'gdt302_result.json';Y=('FIRST','MIDDLE','LAST')
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
def layout(x):return x['section'],x['currier'],x['hand'],x['group_count']
def dist(c,b,k):
 n=sum(c.values());return {z:(c[z]+k*b[z])/(n+k) for z in Y}
def population(rows):
 base=[x for x in rows if x['control_id']=='VOYNICH_REFERENCE' and int(x['group_count'])>=2];hf=defaultdict(set);sf=defaultdict(set)
 for x in base:hf[x['page_host']].add(x['physical_folio']);sf[x['source_surface_sha256']].add(x['physical_folio'])
 return [x for x in base if len(hf[x['page_host']])>=2 and len(sf[x['source_surface_sha256']])>=2]
def contributions(E):
 G=Counter();L=defaultdict(Counter);H=defaultdict(Counter);W=defaultdict(Counter);FG=defaultdict(Counter);FL=defaultdict(lambda:defaultdict(Counter));FH=defaultdict(lambda:defaultdict(Counter));FW=defaultdict(lambda:defaultdict(Counter));FN=Counter();ans=[]
 for x in E:
  z=out(x);f=x['physical_folio'];G[z]+=1;L[layout(x)][z]+=1;H[x['page_host']][z]+=1;W[x['source_surface_sha256']][z]+=1;FG[f][z]+=1;FL[f][layout(x)][z]+=1;FH[f][x['page_host']][z]+=1;FW[f][x['source_surface_sha256']][z]+=1;FN[f]+=1
 for x in E:
  z=out(x);f=x['physical_folio'];n=len(E)-FN[f];g={q:G[q]-FG[f][q] for q in Y};p0={q:(g[q]+.5)/(n+1.5) for q in Y};a={q:L[layout(x)][q]-FL[f][layout(x)][q] for q in Y};pl=dist(a,p0,11);a={q:H[x['page_host']][q]-FH[f][x['page_host']][q] for q in Y};ph=dist(a,pl,11);a={q:W[x['source_surface_sha256']][q]-FW[f][x['source_surface_sha256']][q] for q in Y};pw=dist(a,ph,11);ans.append(math.log2(pw[z]/ph[z]))
 return ans
def main():
 d=json.loads(D.read_text());assert d['content_sha256']==rcan(d) and d['status']=='FROZEN_BEFORE_GDT302_ROLE_SCORING';nr=read(NATIVE);rr=read(RAW);assert not any(x['page'].startswith('f84') or x['locus'].startswith('f84') for x in nr+rr);raw={x['observation_id']:x for x in rr};E=population(nr);assert len(E)==6844 and all(x['observation_id'] in raw for x in E)
 for x in E:assert sha256_text(raw[x['observation_id']]['raw_token'])==x['source_surface_sha256']
 gains=contributions(E);hc=Counter(x['page_host'] for x in E);fc=Counter((x['page_host'],x['source_surface_sha256']) for x in E);ff=defaultdict(set);forms=defaultdict(list);hosts=defaultdict(list)
 for i,x in enumerate(E):q=(x['page_host'],x['source_surface_sha256']);ff[q].add(x['physical_folio']);forms[q].append((i,x));hosts[x['page_host']].append((i,x))
 eligible={(h,s) for (h,s),n in fc.items() if n>=d['form_min_events'] and len(ff[(h,s)])>=d['form_min_folios'] and hc[h]>=d['host_min_events']};bc=Counter(h for h,s in eligible);eligible={q for q in eligible if bc[q[0]]>=d['host_min_scored_forms']};atlas=[]
 for h,s in sorted(eligible):
  F=forms[(h,s)];O=[q for q in hosts[h] if q not in F];cy=Counter(out(x) for i,x in F);hy=Counter(out(x) for i,x in hosts[h]);rat={z:((cy[z]+.5)/(len(F)+1.5))/((hy[z]+.5)/(len(hosts[h])+1.5)) for z in Y};role=max(Y,key=lambda z:(rat[z],-Y.index(z)));powered=positive=0
  for axis in ('section','hand'):
   for v in sorted({x[axis] for i,x in F}):
    a=[x for i,x in F if x[axis]==v];b=[x for i,x in O if x[axis]==v]
    if len(a)>=d['stratum_min_form_events'] and len(b)>=d['stratum_min_other_host_events']:
     powered+=1;positive+=sum(out(x)==role for x in a)/len(a)>sum(out(x)==role for x in b)/len(b)
  gain=sum(gains[i] for i,x in F);mx=rat[role]
  if gain>0 and mx>=d['role_ratio_threshold'] and powered>=d['stable_min_powered_strata'] and positive==powered:cl='STABLE_POSITIONAL_ALTERNANT'
  elif gain>0 and mx>=1.25:cl='PROVISIONAL'
  elif gain>0:cl='WEAK'
  else:cl='COUNTEREXAMPLE'
  z=raw[F[0][1]['observation_id']];tuplev='|'.join(z[k] for k in ('wrapper','local_frame','inner_d','right_family','dy_closure','b3'));atlas.append({'page_host':h,'raw_token':z['raw_token'],'surface_sha256':s,'renderer_tuple':tuplev,'events':len(F),'folios':len(ff[(h,s)]),'sections':len({x['section'] for i,x in F}),'hands':len({x['hand'] for i,x in F}),'registers':len({x['register'] for i,x in F}),'first':cy['FIRST'],'middle':cy['MIDDLE'],'last':cy['LAST'],'preferred_physical_role':role,'role_likelihood_ratio':f'{mx:.12f}','lofo_gain_bits':f'{gain:.12f}','lofo_gain_bits_per_event':f'{gain/len(F):.12f}','powered_section_hand_strata':powered,'positive_role_strata':positive,'classification':cl})
 by=defaultdict(list)
 for x in atlas:by[x['page_host']].append(x)
 pairs=[]
 for h,A in sorted(by.items()):
  for i,a in enumerate(A):
   for b in A[i+1:]:
    if a['preferred_physical_role']==b['preferred_physical_role']:continue
    cl='STABLE_CONTRAST' if a['classification']==b['classification']=='STABLE_POSITIONAL_ALTERNANT' else 'PROVISIONAL_CONTRAST';pairs.append({'page_host':h,'form_a':a['raw_token'],'role_a':a['preferred_physical_role'],'events_a':a['events'],'gain_a':a['lofo_gain_bits'],'form_b':b['raw_token'],'role_b':b['preferred_physical_role'],'events_b':b['events'],'gain_b':b['lofo_gain_bits'],'classification':cl})
 pos=sorted((float(x['lofo_gain_bits']) for x in atlas if float(x['lofo_gain_bits'])>0),reverse=True);tot=sum(pos);conc=[{'rank_cutoff':k,'positive_gain_bits':f'{sum(pos[:k]):.12f}','share_of_positive_gain':f'{sum(pos[:k])/tot:.12f}' if tot else 'NA','positive_forms':len(pos),'all_scored_forms':len(atlas)} for k in (10,20,len(pos))];counter=[{'counterexample_id':'C01','finding':'Atlas selection is post-GDT299 and descriptive.','impact':'Classes are normalization candidates, not independent confirmation.'},{'counterexample_id':'C02','finding':'Complete forms and PAGE_HOST are parser-coupled.','impact':'A positional alternant is not necessarily a linguistic allomorph.'},{'counterexample_id':'C03','finding':'Physical roles are FIRST/MIDDLE/LAST only.','impact':'No grammatical or semantic gloss follows.'},{'counterexample_id':'C04','finding':'Only forms with >=8 events on >=4 folios are scored.','impact':'Rare alternants remain unclassified.'},{'counterexample_id':'C05','finding':'Section and hand stability uses observational strata.','impact':'Correlated strata are not independent replications.'},{'counterexample_id':'C06','finding':'No f84 row occurs in either joined source.','impact':'The seal remains intact.'}];write(ATLAS,atlas);write(PAIRS,pairs);write(CONC,conc);write(COUNTER,counter)
 cc=Counter(x['classification'] for x in atlas);pc=Counter(x['classification'] for x in pairs);top=sorted(atlas,key=lambda x:-float(x['lofo_gain_bits']))[:15];report=['# GDT302 — host-specific positional alternant atlas','',f"Status: **POSITIONAL_ALTERNANT_ATLAS_BUILT**.",'',f"The frozen atlas contains {len(atlas)} complete forms under {len(by)} opaque hosts. Class counts are `{json.dumps(cc,sort_keys=True)}`. It contains {len(pairs)} within-host different-role pairs, including {pc['STABLE_CONTRAST']} stable contrasts.",'',f"The top 10 and 20 positive forms carry {float(conc[0]['share_of_positive_gain']):.3f} and {float(conc[1]['share_of_positive_gain']):.3f} of positive scored-form gain.",'','## Highest held-folio contributors','', '| host | complete form | role | events/folios | gain bits | class |','|---|---|---|---:|---:|---|']
 for x in top:report.append(f"| {x['page_host']} | `{x['raw_token']}` | {x['preferred_physical_role']} | {x['events']}/{x['folios']} | {float(x['lofo_gain_bits']):+.3f} | {x['classification']} |")
 report+=['','## Interpretation','', 'This is the usable normalization layer implied by GDT299--301: some exact host-specific complete forms carry stable physical placement, while counterexamples and weak forms remain explicit. Whole forms are shown only as exact joined source groups; no substring was selected or assigned a function.','','## Claim ceiling','',d['claim_ceiling']+' No f84 row was opened, parsed, retained, joined, or scored.'];REPORT.write_text('\n'.join(report)+'\n');outputs=[ATLAS,PAIRS,CONC,COUNTER,REPORT];inputs=['gdt302_design.json','gdt302_design_validation.json','gdt302_capacity.tsv','gdt302_freeze_manifest.tsv','gdt278_native_event_inventory.tsv','gdt276_event_inventory.tsv','gdt301_result.json','gdt299_result.json'];res={'schema':'GDT302_HOST_POSITIONAL_ALTERNANT_ATLAS_RESULT_V1','status':'POSITIONAL_ALTERNANT_ATLAS_BUILT','summary':{'forms':len(atlas),'hosts':len(by),'class_counts':dict(cc),'contrast_pairs':len(pairs),'stable_contrasts':pc['STABLE_CONTRAST'],'top10_positive_gain_share':conc[0]['share_of_positive_gain'],'top20_positive_gain_share':conc[1]['share_of_positive_gain']},'substrings_mined':0,'semantic_assignments':0,'claim_ceiling':d['claim_ceiling'],'f84':d['f84'],'inputs':{x:sha(R/x) for x in inputs},'documents':{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)},'implementation':{Path(__file__).name:sha(Path(__file__))},'outputs':{x.name:sha(x) for x in outputs}};res['content_sha256']=rcan(res);RESULT.write_text(json.dumps(res,indent=2,sort_keys=True)+'\n');print(json.dumps(res['summary'],sort_keys=True))
def sha256_text(s):return hashlib.sha256(s.encode()).hexdigest()
if __name__=='__main__':main()
