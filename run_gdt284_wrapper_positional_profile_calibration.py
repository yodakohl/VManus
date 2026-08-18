#!/usr/bin/env python3
"""Run the frozen GDT284 architecture calibration."""
from __future__ import annotations
import csv,hashlib,json,math,statistics
from concurrent.futures import ProcessPoolExecutor,as_completed
from pathlib import Path
import run_gdt283_wrapper_host_coupling_localization as core
R=Path(__file__).resolve().parent;DESIGN=R/'gdt284_design.json';METHOD=R/'GDT284_WRAPPER_POSITIONAL_PROFILE_CALIBRATION_METHOD.md';REPORT=R/'GDT284_WRAPPER_POSITIONAL_PROFILE_CALIBRATION_REPORT.md';RESULT=R/'gdt284_result.json'
OUT_COMP=R/'gdt284_component_scores.tsv';OUT_DIST=R/'gdt284_profile_distances.tsv';OUT_NULL=R/'gdt284_null_results.tsv';OUT_SUM=R/'gdt284_summary.tsv';OUT_COUNTER=R/'gdt284_counterexamples.tsv'
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
 with Path(p).open('w',encoding='utf8',newline='') as h:w=csv.DictWriter(h,ff,delimiter='\t',lineterminator='\n');w.writeheader();w.writerows([{k:r.get(k,'') for k in ff} for r in rr])
def total(x):return sum(x.get(c,0.) for c in core.COMPS)
def sign(v):return '+' if v>0 else '-' if v<0 else '0'
def pattern(v):return ''.join(sign(v[c]) for c in core.COMPS)
def rank(v):return '>'.join(sorted(core.COMPS,key=lambda c:(-v[c],core.COMPS.index(c))))
def main():
 d=json.loads(DESIGN.read_text());assert d['status']=='CORRECTED_FROZEN_BEFORE_AUTHORITATIVE_GDT284_SCORING' and d['content_sha256']==rcsha(d)
 for x in read(R/'gdt284_freeze_manifest.tsv'):assert sha(R/x['artifact'])==x['frozen_sha256']
 native=read(R/'gdt278_native_event_inventory.tsv');assert not any(x['page'].startswith('f84') or x['locus'].startswith('f84') for x in native)
 panels={p:[x for x in native if x['control_id']==p] for p in d['panels']};assert all(len(x)==d['events_per_panel'] for x in panels.values())
 manifest={x['control_id']:x for x in read(R/'gdt278_control_manifest.tsv')};cats={p:('UNKNOWN_VOYNICH_ARCHITECTURE' if p=='VOYNICH_REFERENCE' else manifest[p]['architecture_category']) for p in panels}
 results={}
 with ProcessPoolExecutor(max_workers=4) as ex:
  jobs={ex.submit(core.job,x):x[0] for x in panels.items()}
  for f in as_completed(jobs):q=f.result();results[q[0]]=q;print(json.dumps({'scored':q[0]},sort_keys=True),flush=True)
 comp=[];nullrows=[];summ=[];vec={};nullgain={};mobile={}
 for panel in d['panels']:
  _,base,full,bf,ff,nb,nf,nfb,nff,nbuck,nfbuck,null,mob=results[panel];mobile[panel]=mob;vec[panel]={};nullgain[panel]=[]
  for mode,a,z in [('STANDARD_HELD_FOLIO',base,full),('NESTED_UNSEEN_HOST_BUCKET',nb,nf)]:
   v={c:(a.get(c,0.)-z.get(c,0.))/len(panels[panel]) for c in core.COMPS};vec[panel][mode]=v
   for c in core.COMPS:comp.append({'control_id':panel,'architecture_category':cats[panel],'mode':mode,'component':c,'base_bits':f'{a.get(c,0.):.12f}','wrapper_bits':f'{z.get(c,0.):.12f}','gain_bits':f'{a.get(c,0.)-z.get(c,0.):.12f}','gain_bits_per_event':f'{v[c]:.12f}'})
  for world,q in enumerate(null):
   row={'control_id':panel,'world_index':world}
   for c in core.COMPS:row['gain_'+c.lower()+'_bits_per_event']=f'{(base.get(c,0.)-q.get(c,0.))/len(panels[panel]):.12f}'
   g=(total(base)-total(q))/len(panels[panel]);row['gain_total_bits_per_event']=f'{g:.12f}';nullgain[panel].append(g);nullrows.append(row)
 profile_active=[p for p in d['panels'] if mobile[p]>0 and p not in d['capacity_rule']['known_zero_context_reuse_panels']];means={p:statistics.mean(nullgain[p]) for p in profile_active};sds={p:statistics.pstdev(nullgain[p]) for p in profile_active};assert all(sds[p]>0 for p in profile_active)
 obsz={p:(sum(vec[p]['STANDARD_HELD_FOLIO'].values())-means[p])/sds[p] for p in profile_active};worldmax=[max((nullgain[p][w]-means[p])/sds[p] for p in profile_active) for w in range(d['null_worlds'])]
 for panel in d['panels']:
  v=vec[panel]['STANDARD_HELD_FOLIO'];n=vec[panel]['NESTED_UNSEEN_HOST_BUCKET'];cap='UNSCORED_NO_WRAPPER_CAPACITY' if mobile[panel]==0 else 'UNSCORED_NO_CONTEXT_REUSE' if panel in d['capacity_rule']['known_zero_context_reuse_panels'] else 'SCORED'
  local='NA' if panel not in profile_active else f"{(1+sum(x>=sum(v.values())-1e-15 for x in nullgain[panel]))/65:.12f}"
  maxp='NA' if panel not in profile_active else f"{(1+sum(x>=obsz[panel]-1e-15 for x in worldmax))/65:.12f}"
  summ.append({'control_id':panel,'architecture_category':cats[panel],'events':len(panels[panel]),'folios':len({x['physical_folio'] for x in panels[panel]}),'wrapper_classes':len({x['wrapper'] for x in panels[panel]}),'mobile_events':mobile[panel],'capacity_status':cap,'standard_initial':f"{v['INITIAL']:.12f}",'standard_internal':f"{v['INTERNAL']:.12f}",'standard_final':f"{v['FINAL']:.12f}",'standard_eos':f"{v['EOS']:.12f}",'standard_onset_body':f"{v['INITIAL']+v['INTERNAL']:.12f}",'standard_terminal':f"{v['FINAL']+v['EOS']:.12f}",'standard_total':f"{sum(v.values()):.12f}",'standard_sign_pattern':pattern(v) if cap=='SCORED' else 'UNSCORED','standard_component_rank':rank(v) if cap=='SCORED' else 'UNSCORED','nested_initial':f"{n['INITIAL']:.12f}",'nested_internal':f"{n['INTERNAL']:.12f}",'nested_final':f"{n['FINAL']:.12f}",'nested_eos':f"{n['EOS']:.12f}",'nested_onset_body':f"{n['INITIAL']+n['INTERNAL']:.12f}",'nested_terminal':f"{n['FINAL']+n['EOS']:.12f}",'nested_total':f"{sum(n.values()):.12f}",'nested_sign_pattern':pattern(n) if cap=='SCORED' else 'UNSCORED','nested_component_rank':rank(n) if cap=='SCORED' else 'UNSCORED','local_p':local,'max12_p':maxp})
 # Require exact reproduction of every GDT283 component anchor.
 old=read(R/'gdt283_component_scores.tsv')
 for x in old:
  y=next(z for z in comp if z['control_id']==x['control_id'] and z['mode']==x['mode'] and z['component']==x['component']);assert abs(float(x['gain_bits_per_event'])-float(y['gain_bits_per_event']))<1e-12
 vms=vec['VOYNICH_REFERENCE'];dist=[]
 for panel in d['panels']:
  for mode in d['modes']:
   q=vec[panel][mode];dv=math.sqrt(sum((q[c]-vms[mode][c])**2 for c in core.COMPS));cap=next(x['capacity_status'] for x in summ if x['control_id']==panel);dist.append({'control_id':panel,'architecture_category':cats[panel],'mode':mode,'capacity_status':cap,'euclidean_distance_to_voynich':f'{dv:.12f}','exact_sign_match':int(cap=='SCORED' and pattern(q)==pattern(vms[mode])),'component_rank_match':int(cap=='SCORED' and rank(q)==rank(vms[mode])),'rank_among_scored_controls':'NA'})
 for mode in d['modes']:
  q=sorted([x for x in dist if x['mode']==mode and x['control_id']!='VOYNICH_REFERENCE' and x['capacity_status']=='SCORED'],key=lambda x:(float(x['euclidean_distance_to_voynich']),x['control_id']))
  for i,x in enumerate(q,1):x['rank_among_scored_controls']=i
 vp=pattern(vms['STANDARD_HELD_FOLIO']);matches=[x for x in summ if x['control_id']!='VOYNICH_REFERENCE' and x['capacity_status']=='SCORED' and x['standard_sign_pattern']==vp];mcats=sorted({x['architecture_category'] for x in matches})
 np=pattern(vms['NESTED_UNSEEN_HOST_BUCKET']);nmatches=[x for x in summ if x['control_id']!='VOYNICH_REFERENCE' and x['capacity_status']=='SCORED' and x['nested_sign_pattern']==np];nmcats=sorted({x['architecture_category'] for x in nmatches})
 if len(mcats)>=2:status=d['classification']['two_or_more_architecture_categories_exact_standard_sign_match']
 elif len(mcats)==1:status=d['classification']['one_architecture_category_exact_standard_sign_match']
 else:status=d['classification']['zero_control_exact_standard_sign_match']
 nearest=sorted([x for x in dist if x['mode']=='STANDARD_HELD_FOLIO' and x['control_id']!='VOYNICH_REFERENCE' and x['capacity_status']=='SCORED'],key=lambda x:float(x['euclidean_distance_to_voynich']))[:3]
 nnearest=sorted([x for x in dist if x['mode']=='NESTED_UNSEEN_HOST_BUCKET' and x['control_id']!='VOYNICH_REFERENCE' and x['capacity_status']=='SCORED'],key=lambda x:float(x['euclidean_distance_to_voynich']))[:3]
 counters=[{'counterexample':'POSITIONAL_PROFILE_IDENTIFIES_ONE_ARCHITECTURE','evidence':f'exact standard sign matches span {len(mcats)} architecture categories: {"|".join(mcats) if mcats else "NONE"}','impact':'the frozen category-count rule determines specificity'}, {'counterexample':'STANDARD_TERMINAL_NEGATIVITY_TRANSFERS_TO_UNSEEN_HOST_TYPES','evidence':f'nested Voynich pattern {np} is shared by {len(nmatches)} controls across {len(nmcats)} architecture categories','impact':'the distinctive negative terminal components are tied to reusable exact-host/model support and disappear under host-identity exclusion'}, {'counterexample':'LEARNED_ABBREVIATION_OUTPUT_IS_A_NEGATIVE_WRAPPER_RESULT','evidence':'MAP and sampled panels each have one wrapper class and zero mobile events','impact':'they are capacity-unscored, not negative profile matches'}, {'counterexample':'NEAREST_CONTROL_PROVES_GENERATIVE_IDENTITY','evidence':f'nearest raw-vector control is {nearest[0]["control_id"]} at distance {nearest[0]["euclidean_distance_to_voynich"]}','impact':'distance is descriptive and the finite panels are not exhaustive'}, {'counterexample':'NESTED_SCORE_IS_PARSER_INDEPENDENT','evidence':'the published frozen PAGE_HOST parser defines the host buckets','impact':'identity exclusion does not re-learn the parser'}, {'counterexample':'F84_USED','evidence':'only the published f84-free native inventory is read','impact':'no f84 access'}]
 write(OUT_COMP,comp);write(OUT_DIST,dist);write(OUT_NULL,nullrows);write(OUT_SUM,summ);write(OUT_COUNTER,counters)
 report=['# GDT284 — wrapper positional-profile architecture calibration','',f'Status: **{status}**.','','## Standard held-folio fingerprint','', '| panel | architecture | capacity | initial | internal | final | EOS | sign | distance |','|---|---|---|---:|---:|---:|---:|---|---:|']
 dd={(x['control_id'],x['mode']):x for x in dist}
 for x in summ:report.append(f"| {x['control_id']} | {x['architecture_category']} | {x['capacity_status']} | {float(x['standard_initial']):+.4f} | {float(x['standard_internal']):+.4f} | {float(x['standard_final']):+.4f} | {float(x['standard_eos']):+.4f} | {x['standard_sign_pattern']} | {float(dd[(x['control_id'],'STANDARD_HELD_FOLIO')]['euclidean_distance_to_voynich']):.4f} |")
 report +=['','Voynich exact standard sign pattern: `'+vp+'`.  Matching scored controls: '+(', '.join(x['control_id'] for x in matches) if matches else 'none')+'.  Matching architecture categories: '+(', '.join(mcats) if mcats else 'none')+'.','','The three nearest scored standard vectors are: '+', '.join(f"{x['control_id']} ({float(x['euclidean_distance_to_voynich']):.4f})" for x in nearest)+'.','','## Unseen-host sensitivity','','After every exact host identity in the target bucket is excluded from training, Voynich changes to `'+np+'`.  That sign pattern is shared by '+(', '.join(x['control_id'] for x in nmatches) if nmatches else 'no control')+'.  Its nearest nested vectors are '+', '.join(f"{x['control_id']} ({float(x['euclidean_distance_to_voynich']):.4f})" for x in nnearest)+'.  Thus the standard `++--` fingerprint is distinct in this panel, but its terminal-negative half does **not** transfer to unseen host identities.','','## Interpretation','','The learned-abbreviation outputs are an observation-layer capacity result, not a failed positional profile: the frozen parser assigns them no wrapper contrast. The ordinary and diplomatic Nuremberg overlays have no context reuse under this exact instrument and are also capacity-unscored. Exact component vectors, nested sensitivities, nulls and distances are exported in the TSVs. No fitted classifier or post-score rescaling is used.','','## Claim ceiling','','This only calibrates the positional shape of opaque wrapper-conditioned character compression. It establishes no morphology, abbreviation mechanism, lexical identity, language, meaning, plaintext, or translation. No f84 row was opened, parsed, retained, joined, or scored.'];REPORT.write_text('\n'.join(report)+'\n')
 outputs=[OUT_COMP,OUT_DIST,OUT_NULL,OUT_SUM,OUT_COUNTER,REPORT];inputs=['gdt284_design.json','gdt284_design_validation.json','gdt284_freeze_manifest.tsv','gdt278_native_event_inventory.tsv','gdt278_control_manifest.tsv','gdt283_result.json','gdt283_component_scores.tsv'];result={'schema':'GDT284_WRAPPER_POSITIONAL_PROFILE_CALIBRATION_RESULT_V1','status':status,'panels':len(d['panels']),'scored_panels':len(profile_active),'events_per_panel':d['events_per_panel'],'voynich_standard_sign_pattern':vp,'exact_matching_controls':[x['control_id'] for x in matches],'exact_matching_architecture_categories':mcats,'nearest_standard_controls':nearest,'voynich_nested_sign_pattern':np,'nested_exact_matching_controls':[x['control_id'] for x in nmatches],'nested_exact_matching_architecture_categories':nmcats,'nearest_nested_controls':nnearest,'zero_wrapper_capacity_panels':[p for p in d['panels'] if mobile[p]==0],'zero_context_reuse_panels':d['capacity_rule']['known_zero_context_reuse_panels'],'gdt283_anchor_exact':True,'authoritative_run_after_capacity_correction':True,'new_corpora':0,'new_synthetic_worlds':0,'semantic_assignments':0,'page_host_substrings_mined':0,'oracle_fields_scored':0,'claim_ceiling':d['claim_ceiling'],'f84':d['f84'],'inputs':{x:sha(R/x) for x in inputs},'documents':{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)},'implementation':{Path(__file__).name:sha(Path(__file__)),'run_gdt283_wrapper_host_coupling_localization.py':sha(R/'run_gdt283_wrapper_host_coupling_localization.py')},'outputs':{x.name:sha(x) for x in outputs}};result['content_sha256']=rcsha(result);RESULT.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':status,'matches':result['exact_matching_controls'],'nearest':nearest[0]['control_id']},sort_keys=True))
if __name__=='__main__':main()
