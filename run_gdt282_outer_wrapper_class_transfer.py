#!/usr/bin/env python3
"""Run the frozen GDT282 outer-wrapper class transfer."""
from __future__ import annotations
import csv, hashlib, json, math, statistics
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import run_gdt278_magnitude_calibration as g278
import run_gdt279_native_order_compiler_decomposition as g279
import run_gdt280_edge_compiler_fine_decomposition as g280

R=Path(__file__).resolve().parent
DESIGN=R/'gdt282_design.json';METHOD=R/'GDT282_OUTER_WRAPPER_CLASS_TRANSFER_METHOD.md';REPORT=R/'GDT282_OUTER_WRAPPER_CLASS_TRANSFER_REPORT.md';RESULT=R/'gdt282_result.json'
OUT_SCORE=R/'gdt282_model_scores.tsv';OUT_FOLD=R/'gdt282_transfer_folds.tsv';OUT_NULL=R/'gdt282_null_results.tsv';OUT_PROBE=R/'gdt282_wrapper_class_probes.tsv';OUT_COUNT=R/'gdt282_wrapper_counts.tsv';OUT_COUNTER=R/'gdt282_counterexamples.tsv'
PRIMARY_MODELS=('BASE_NO_WRAPPER','WRAPPER_PRESENCE','Q_BINARY','FULL_WRAPPER_IDENTITY','FULL_WRAPPER_PLUS_Q_REDUNDANCY')
CONTROLS=('LATIN_SCHOLASTIC_GRAPHEMATIC','LATIN_MEDICAL_GRAPHEMATIC','LATIN_15C_GRAPHEMATIC','VOYNICH_REFERENCE')
WRAPPERS=('NONE','q','ch','d','sh','che','t','s')

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
 with Path(p).open('w',encoding='utf8',newline='') as h:
  w=csv.DictWriter(h,ff,delimiter='\t',lineterminator='\n');w.writeheader();w.writerows([{k:r.get(k,'') for k in ff} for r in rr])

def state(row,model):
 w=row['wrapper'];q=int(row['q_flag'])
 if model=='BASE_NO_WRAPPER':return ()
 if model=='WRAPPER_PRESENCE':return (int(w!='NONE'),)
 if model=='Q_BINARY':return (int(w=='q'),)
 if model=='FULL_WRAPPER_IDENTITY':return (w,)
 if model=='FULL_WRAPPER_PLUS_Q_REDUNDANCY':return (w,q)
 if model.startswith('CLASS_BINARY_'):
  cut=model[13:];return (int(w==cut),)
 raise ValueError(model)

def context(row,model,state_row=None):
 return g280.fine_key(row,14)+state(row if state_row is None else state_row,model)

def summarize(events,observed,null=None):
 r={'events':len(events),'folds':len({x['physical_folio'] for x in events}),'observed_bits':f'{observed:.12f}'}
 if null is None:r.update({'null_worlds':0,'null_mean_bits':'NA','null_sd_bits':'NA','null_saving_bits_per_event':'NA','null_z':'NA'});return r
 m=statistics.mean(null);sd=statistics.pstdev(null);saving=m-observed
 r.update({'null_worlds':len(null),'null_mean_bits':f'{m:.12f}','null_sd_bits':f'{sd:.12f}','null_saving_bits_per_event':f'{saving/len(events):.12f}','null_z':f'{saving/sd:.12f}' if sd else 'NA'});return r

def published_job(item):
 control,events=item;observed={};folds={};maps={}
 for model in PRIMARY_MODELS:
  maps[model]=[context(x,model) for x in events];observed[model],folds[model]=g279.score_buckets(events,maps[model])
 null={m:[] for m in PRIMARY_MODELS};nr=[]
 for world in range(64):
  source=g279.permutation_indices(events,world)
  for model in PRIMARY_MODELS:
   keys=[context(row,model,events[source[i]]) for i,row in enumerate(events)]
   bits,_=g279.score_buckets(events,keys);null[model].append(bits);nr.append({'control_id':control,'regime':'PUBLISHED_HELD_FOLIO','model':model,'world_index':world,'held_bits':f'{bits:.12f}'})
 base=observed['BASE_NO_WRAPPER'];sr=[];fr=[]
 for model in PRIMARY_MODELS:
  q={'control_id':control,'regime':'PUBLISHED_HELD_FOLIO','model':model,'base_minus_model_bits_per_event':f'{(base-observed[model])/len(events):.12f}'};q.update(summarize(events,observed[model],null[model]));sr.append(q)
  for held,bits in sorted(folds[model].items()):fr.append({'control_id':control,'regime':'PUBLISHED_HELD_FOLIO','model':model,'held_stratum':held,'events':sum(x['physical_folio']==held for x in events),'held_bits':f'{bits:.12f}'})
 return sr,fr,nr

def safe_job(item):
 control,events,target=item;models=PRIMARY_MODELS+tuple('CLASS_BINARY_'+x for x in WRAPPERS);obs={m:0. for m in models};fr=[];changed=0
 for held in sorted({x['physical_folio'] for x in events}):
  safe=g278.safe_reparse(events,control,held,target);changed+=sum(a['page_host']!=b['page_host'] or g280.fine_key(a,14)!=g280.fine_key(b,14) for a,b in zip(safe,events));train=[x for x in safe if x['physical_folio']!=held];test=[x for x in safe if x['physical_folio']==held]
  heldbits={}
  for model in models:
   bm={x['observation_id']:context(x,model) for x in safe};bits=g278.fold_char(train,test,bm);obs[model]+=bits;heldbits[model]=bits
  for model in models:fr.append({'control_id':control,'regime':'LOFO_SAFE_HELD_FOLIO','model':model,'held_stratum':held,'events':len(test),'held_bits':f'{heldbits[model]:.12f}'})
 base=obs['BASE_NO_WRAPPER'];sr=[]
 for model in PRIMARY_MODELS:
  q={'control_id':control,'regime':'LOFO_SAFE_HELD_FOLIO','model':model,'base_minus_model_bits_per_event':f'{(base-obs[model])/len(events):.12f}','representation_changes_across_folds':changed};q.update(summarize(events,obs[model]));sr.append(q)
 return sr,fr,obs

def external_split(events,field,allowed,models):
 obs={m:0. for m in models};fr=[]
 for held in allowed:
  train=[x for x in events if x[field]!=held];test=[x for x in events if x[field]==held];assert test
  vals={}
  for model in models:
   bm={x['observation_id']:context(x,model) for x in events};vals[model]=g278.fold_char(train,test,bm);obs[model]+=vals[model]
  for model in models:fr.append({'control_id':'VOYNICH_REFERENCE','regime':'HELD_'+field.upper()+'_PUBLISHED','model':model,'held_stratum':held,'events':len(test),'held_bits':f'{vals[model]:.12f}'})
 return obs,fr

def add_fold_gains(folds):
 base={(x['control_id'],x['regime'],x['held_stratum']):float(x['held_bits']) for x in folds if x['model']=='BASE_NO_WRAPPER'}
 for x in folds:x['base_minus_model_bits']=f"{base[(x['control_id'],x['regime'],x['held_stratum'])]-float(x['held_bits']):.12f}"

def main():
 d=json.loads(DESIGN.read_text());assert d['status']=='FROZEN_BEFORE_GDT282_SCORING' and d['content_sha256']==rcsha(d)
 for x in read(R/'gdt282_gdt281_freeze_manifest.tsv'):assert sha(R/x['artifact'])==x['frozen_sha256']
 panels,_inter,target=g279.build_panels();native={c:panels[(c,'NATIVE_ORDER')] for c in CONTROLS};vms=native['VOYNICH_REFERENCE']
 assert len(vms)==8448 and all(not x['page'].startswith('f84') and not x['locus'].startswith('f84') for rr in native.values() for x in rr)
 assert {x['wrapper'] for x in vms}==set(WRAPPERS) and all(int(x['q_flag'])==int(x['wrapper']=='q') for x in vms)
 scores=[];folds=[];nulls=[];safe_obs={}
 with ProcessPoolExecutor(max_workers=4) as ex:
  jobs={ex.submit(published_job,(c,native[c])):c for c in CONTROLS}
  for f in as_completed(jobs):a,b,c=f.result();scores+=a;folds+=b;nulls+=c;print(json.dumps({'published':jobs[f]},sort_keys=True),flush=True)
 with ProcessPoolExecutor(max_workers=4) as ex:
  jobs={ex.submit(safe_job,(c,native[c],target)):c for c in CONTROLS}
  for f in as_completed(jobs):a,b,c=f.result();control=jobs[f];scores+=a;folds+=b;safe_obs[control]=c;print(json.dumps({'safe':control},sort_keys=True),flush=True)
 all_models=PRIMARY_MODELS+tuple('CLASS_BINARY_'+x for x in WRAPPERS)
 section_obs,section_folds=external_split(vms,'section',d['powered_sections'],all_models);hand_obs,hand_folds=external_split(vms,'hand',d['powered_hands']+d['descriptive_hands'],all_models);folds+=section_folds+hand_folds
 for regime,obs,allowed in [('HELD_SECTION_PUBLISHED',section_obs,d['powered_sections']),('HELD_HAND_PUBLISHED',hand_obs,d['powered_hands']+d['descriptive_hands'])]:
  base=obs['BASE_NO_WRAPPER']
  for model in PRIMARY_MODELS:
   q={'control_id':'VOYNICH_REFERENCE','regime':regime,'model':model,'base_minus_model_bits_per_event':f'{(base-obs[model])/len(vms):.12f}'};q.update(summarize(vms,obs[model]));scores.append(q)
 add_fold_gains(folds)

 # Exhaustive one-vs-rest class probes under every Voynich transfer regime.
 probes=[];reg_obs={'LOFO_SAFE_HELD_FOLIO':safe_obs['VOYNICH_REFERENCE'],'HELD_SECTION_PUBLISHED':section_obs,'HELD_HAND_PUBLISHED':hand_obs}
 pub_obs={x['model']:float(x['observed_bits']) for x in scores if x['control_id']=='VOYNICH_REFERENCE' and x['regime']=='PUBLISHED_HELD_FOLIO'}
 # Score the eight published class probes once; no post-selected null.
 for cut in WRAPPERS:
  model='CLASS_BINARY_'+cut;keys=[context(x,model) for x in vms];bits,_=g279.score_buckets(vms,keys);pub_obs[model]=bits
 reg_obs['PUBLISHED_HELD_FOLIO']=pub_obs
 for regime,obs in reg_obs.items():
  base=obs['BASE_NO_WRAPPER']
  for cut in WRAPPERS:probes.append({'regime':regime,'wrapper_class':cut,'occurrences':sum(x['wrapper']==cut for x in vms),'class_binary_bits':f"{obs['CLASS_BINARY_'+cut]:.12f}",'base_minus_class_binary_bits_per_event':f"{(base-obs['CLASS_BINARY_'+cut])/len(vms):.12f}"})
 counts=[]
 for w in WRAPPERS:
  rr=[x for x in vms if x['wrapper']==w];counts.append({'wrapper_class':w,'events':len(rr),'folios':len({x['physical_folio'] for x in rr}),'sections':len({x['section'] for x in rr}),'hands':len({x['hand'] for x in rr}),'registers':len({x['register'] for x in rr})})
 scores.sort(key=lambda x:(x['control_id'],x['regime'],PRIMARY_MODELS.index(x['model'])));folds.sort(key=lambda x:(x['control_id'],x['regime'],x['held_stratum'],x['model']));nulls.sort(key=lambda x:(x['control_id'],x['model'],int(x['world_index'])));probes.sort(key=lambda x:(x['regime'],WRAPPERS.index(x['wrapper_class'])))

 def score_row(regime,model):return next(x for x in scores if x['control_id']=='VOYNICH_REFERENCE' and x['regime']==regime and x['model']==model)
 regime_checks={}
 for regime in ('LOFO_SAFE_HELD_FOLIO','HELD_SECTION_PUBLISHED','HELD_HAND_PUBLISHED'):
  full=float(score_row(regime,'FULL_WRAPPER_IDENTITY')['base_minus_model_bits_per_event']);presence=float(score_row(regime,'WRAPPER_PRESENCE')['base_minus_model_bits_per_event']);regime_checks[regime]={'full_positive':full>0,'identity_beyond_presence_positive':full>presence,'full_gain':full,'presence_gain':presence}
 section_full=[x for x in folds if x['control_id']=='VOYNICH_REFERENCE' and x['regime']=='HELD_SECTION_PUBLISHED' and x['model']=='FULL_WRAPPER_IDENTITY' and x['held_stratum'] in d['powered_sections']];hand_full=[x for x in folds if x['control_id']=='VOYNICH_REFERENCE' and x['regime']=='HELD_HAND_PUBLISHED' and x['model']=='FULL_WRAPPER_IDENTITY' and x['held_stratum'] in d['powered_hands']]
 section_positive=sum(float(x['base_minus_model_bits'])>0 for x in section_full);hand_positive=sum(float(x['base_minus_model_bits'])>0 for x in hand_full)
 redundant=True
 for control in CONTROLS:
  for regime in ('PUBLISHED_HELD_FOLIO','LOFO_SAFE_HELD_FOLIO'):
   by={(x['held_stratum'],x['model']):float(x['held_bits']) for x in folds if x['control_id']==control and x['regime']==regime}
   for held in {k[0] for k in by}:redundant &= abs(by[(held,'FULL_WRAPPER_IDENTITY')]-by[(held,'FULL_WRAPPER_PLUS_Q_REDUNDANCY')])<=d['redundancy_tolerance_bits']
 gates={'all_three_total_positive':all(x['full_positive'] for x in regime_checks.values()),'identity_beyond_presence_all_three':all(x['identity_beyond_presence_positive'] for x in regime_checks.values()),'sections_positive_at_least_4_of_6':section_positive>=4,'hands_positive_at_least_3_of_4':hand_positive>=3,'q_redundancy_exact':bool(redundant)}
 status='OUTER_WRAPPER_IDENTITY_TRANSFERS_ACROSS_REGISTERS' if all(gates.values()) else 'OUTER_WRAPPER_SIGNAL_REGISTER_LOCAL_OR_NONIDENTIFIABLE'
 counters=[{'counterexample':'Q_IS_AN_INDEPENDENT_OUTER_DIMENSION','evidence':'q_flag equals wrapper=q on all 8448 events and FULL_PLUS_Q exactly equals FULL_IDENTITY','impact':'q receives no independent dimensional credit'}, {'counterexample':'WRAPPER_PRESENCE_EXPLAINS_FULL_SIGNAL','evidence':'nested presence and identity gains are reported separately in all transfer regimes','impact':'failure of identity beyond presence blocks the transfer claim'}, {'counterexample':'ONE_REGISTER_DRIVES_WRAPPER_SIGNAL','evidence':f'{section_positive}/6 held sections and {hand_positive}/4 powered held hands are positive','impact':'all fold signs remain public'}, {'counterexample':'SUPERSEDED_UNIQUE_RENAME_WAS_A_REAL_ABLATION','evidence':'renaming one class to a new unique label preserved the context partition and forced eight zero losses','impact':'discarded before publication and replaced with exhaustive one-vs-rest probes'}, {'counterexample':'WRAPPER_CLASS_EQUALS_PREFIX_MORPHOLOGY','evidence':'classes are source-form compiler partitions only','impact':'no linguistic function or meaning follows'}, {'counterexample':'F84_USED','evidence':'the sole Voynich panel is the frozen f84-free GDT278 native inventory','impact':'no f84 access'}]
 write(OUT_SCORE,scores);write(OUT_FOLD,folds);write(OUT_NULL,nulls);write(OUT_PROBE,probes);write(OUT_COUNT,counts);write(OUT_COUNTER,counters)
 report=['# GDT282 — outer-wrapper class transfer','',f'Status: **{status}**.','','The collision-free GDT281 wrapper direction is decomposed without inspecting PAGE_HOST substrings. Scores below are base-minus-model bits/event; positive is better.','','## Voynich transfer','', '| regime | presence | q binary | full identity | identity beyond presence |','|---|---:|---:|---:|---:|']
 for regime in ('PUBLISHED_HELD_FOLIO','LOFO_SAFE_HELD_FOLIO','HELD_SECTION_PUBLISHED','HELD_HAND_PUBLISHED'):
  p=float(score_row(regime,'WRAPPER_PRESENCE')['base_minus_model_bits_per_event']);q=float(score_row(regime,'Q_BINARY')['base_minus_model_bits_per_event']);f=float(score_row(regime,'FULL_WRAPPER_IDENTITY')['base_minus_model_bits_per_event']);report.append(f'| {regime} | {p:+.4f} | {q:+.4f} | {f:+.4f} | {f-p:+.4f} |')
 report +=['',f'Full wrapper identity is positive in **{section_positive}/6** held sections and **{hand_positive}/4** powered held hands. Hand `@` is descriptive only.','','## Native Latin calibration','','| panel | published presence | published full | safe presence | safe full |','|---|---:|---:|---:|---:|']
 for c in CONTROLS[:3]:report.append(f"| {c} | {float(next(x for x in scores if x['control_id']==c and x['regime']=='PUBLISHED_HELD_FOLIO' and x['model']=='WRAPPER_PRESENCE')['base_minus_model_bits_per_event']):+.4f} | {float(next(x for x in scores if x['control_id']==c and x['regime']=='PUBLISHED_HELD_FOLIO' and x['model']=='FULL_WRAPPER_IDENTITY')['base_minus_model_bits_per_event']):+.4f} | {float(next(x for x in scores if x['control_id']==c and x['regime']=='LOFO_SAFE_HELD_FOLIO' and x['model']=='WRAPPER_PRESENCE')['base_minus_model_bits_per_event']):+.4f} | {float(next(x for x in scores if x['control_id']==c and x['regime']=='LOFO_SAFE_HELD_FOLIO' and x['model']=='FULL_WRAPPER_IDENTITY')['base_minus_model_bits_per_event']):+.4f} |")
 report +=['','## One-vs-rest class probes','', '| class | published | safe folio | held section | held hand |','|---|---:|---:|---:|---:|']
 for w in WRAPPERS:
  vals={x['regime']:float(x['base_minus_class_binary_bits_per_event']) for x in probes if x['wrapper_class']==w};report.append(f"| {w} | {vals['PUBLISHED_HELD_FOLIO']:+.4f} | {vals['LOFO_SAFE_HELD_FOLIO']:+.4f} | {vals['HELD_SECTION_PUBLISHED']:+.4f} | {vals['HELD_HAND_PUBLISHED']:+.4f} |")
 report +=['','These eight probes are exhaustive but nonadditive. The initial unique-rename diagnostic was a bijection and is explicitly discarded in the method and counterexamples.','','## Frozen gates','']+[f"- `{k}`: **{'PASS' if v else 'FAIL'}**" for k,v in gates.items()]+['','`q_flag` is a deterministic duplicate of `wrapper=q`; the exact full-plus-q model equals full wrapper identity and is not evidence for a separate q dimension.','','## Claim ceiling','','At most this establishes a transferable opaque wrapper-class character channel. It does not identify prefix morphology, abbreviation, a linguistic function, sound, language, code, notation, meaning, plaintext, or translation. No f84 row was opened, parsed, retained, joined, or scored.']
 REPORT.write_text('\n'.join(report)+'\n')
 outputs=[OUT_SCORE,OUT_FOLD,OUT_NULL,OUT_PROBE,OUT_COUNT,OUT_COUNTER,REPORT];inputs=['gdt282_design.json','gdt282_design_validation.json','gdt282_gdt281_freeze_manifest.tsv','gdt281_result.json','gdt278_native_event_inventory.tsv']
 result={'schema':'GDT282_OUTER_WRAPPER_CLASS_TRANSFER_RESULT_V1','status':status,'events':len(vms),'folios':len({x['physical_folio'] for x in vms}),'models':list(PRIMARY_MODELS),'wrapper_classes':list(WRAPPERS),'class_probe_rule':d['class_probe_rule'],'superseded_invalid_probe':d['superseded_invalid_probe'],'regime_checks':regime_checks,'positive_sections':section_positive,'powered_sections':6,'positive_hands':hand_positive,'powered_hands':4,'frozen_gates':gates,'q_flag_redundant_with_wrapper_q':True,'new_corpora':0,'semantic_assignments':0,'hpr1_semantics_used':0,'page_host_substrings_mined':0,'claim_ceiling':'Transfer of an opaque wrapper-class character-prediction channel only; no function morphology language meaning plaintext or translation.','f84':{'input_files':0,'opened':False,'parsed':False,'retained':False,'joined':False,'scored':False},'gdt281_immutable':all(sha(R/x['artifact'])==x['frozen_sha256'] for x in read(R/'gdt282_gdt281_freeze_manifest.tsv')),'inputs':{x:sha(R/x) for x in inputs},'documents':{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)},'implementation':{Path(__file__).name:sha(Path(__file__))},'outputs':{x.name:sha(x) for x in outputs}}
 result['content_sha256']=rcsha(result);RESULT.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':status,'gates':gates},sort_keys=True))
if __name__=='__main__':main()
