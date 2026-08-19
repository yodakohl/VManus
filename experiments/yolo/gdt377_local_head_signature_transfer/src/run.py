#!/usr/bin/env python3
"""Apply the frozen CoReMA local-head signature once to f84-free GDT327."""
from __future__ import annotations
import csv,hashlib,importlib.util,json,math,random
from collections import Counter,defaultdict
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[4];BASE=ROOT/'experiments/yolo/gdt377_local_head_signature_transfer';ART=BASE/'artifacts';FREEZE=ART/'gdt377_comparator_model_freeze.json';SOURCE=ROOT/'gdt327_joint_tuple_interlinear.tsv';G376=ROOT/'experiments/yolo/gdt376_corema_hidden_function_oracle'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):
 with p.open(encoding='utf-8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def write(p,rows):
 with p.open('w',encoding='utf-8',newline='') as h:w=csv.DictWriter(h,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
def loadmod():
 s=importlib.util.spec_from_file_location('gdt376_frozen',G376/'src/run.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def unpack(x):return np.array(x['beta']),np.array(x['mean']),np.array(x['sd'])
def bucket(n):return 'A' if n<=8 else 'B' if n<=16 else 'C' if n<=32 else 'D'
def content(d):
 x=dict(d);x.pop('content_hash',None);return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def main():
 f=json.loads(FREEZE.read_text());assert f['status']=='FROZEN_BEFORE_VOYNICH_SCORE' and not f['voynich_scored'];src=read(SOURCE);assert len(src)==8448 and not any(r['page'].startswith('f84') or r['locus'].startswith('f84') for r in src)
 byrec=defaultdict(list)
 for i,r in enumerate(src):byrec[(r['page'],int(r['record_ordinal']))].append((i,r))
 obs=[];meta=[];recipe_order=defaultdict(list)
 for page,record in byrec:recipe_order[page].append(record)
 for page in recipe_order:recipe_order[page]=sorted(set(recipe_order[page]))
 ordered=[]
 for page in sorted(recipe_order):
  for record in recipe_order[page]:
   vals=byrec[(page,record)];n=len(vals)
   for j,(source_index,r) in enumerate(vals,1):
    obs.append({'collection_id':page,'recipe_id':f'{page}:R{record}','recipe_ordinal':str(record),'element_ordinal':str(j),'opaque_form_id':r['joint_tuple_id'],'direct_token_count':'1','observable_surface':'1','record_element_count':str(n),'relative_position':f'{j/max(1,n):.9f}'})
    meta.append(r);ordered.append(source_index)
 m=loadmod();static,_=m.static_features(obs);default=[0.,0.,0.,0.,.5,0.];Xn=[x[0] for x in static];Xs=[x[0]+x[1]+default for x in static];pn=m.predict(unpack(f['nuisance_model']),Xn);ps=m.predict(unpack(f['structure_model']),Xs)
 events=[]
 for i,(r,a,b) in enumerate(zip(meta,pn,ps)):
  events.append({'event_id_sha256':r['event_id_sha256'],'page':r['page'],'physical_folio':r['physical_folio'],'locus':r['locus'],'record_ordinal':r['record_ordinal'],'field_ordinal':r['field_ordinal'],'within_field_position':r['within_field_position'],'joint_tuple_id':r['joint_tuple_id'],'section':r['section'],'register':r['register'],'currier':r['currier'],'hand':r['hand'],'nuisance_probability':f'{a:.12f}','cmp_local_head_signature_probability':f'{b:.12f}','structure_minus_nuisance':f'{b-a:.12f}','semantic_state':'UNASSIGNED'})
 bytuple=defaultdict(list)
 for i,r in enumerate(events):bytuple[r['joint_tuple_id']].append(i)
 atlas=[]
 gate=f['candidate_gate']
 for tid,ids in bytuple.items():
  fol=defaultdict(list)
  for i in ids:fol[events[i]['physical_folio']].append(float(events[i]['cmp_local_head_signature_probability']))
  fm={k:sum(v)/len(v) for k,v in fol.items()};mean=sum(float(events[i]['cmp_local_head_signature_probability']) for i in ids)/len(ids);delta=sum(float(events[i]['structure_minus_nuisance']) for i in ids)/len(ids);frac=sum(v>=.5 for v in fm.values())/len(fm)
  promoted=len(ids)>=gate['minimum_events'] and len(fol)>=gate['minimum_physical_folios'] and mean>=gate['minimum_mean_structure_probability'] and frac>=gate['minimum_folio_fraction_mean_ge_0_5'] and delta>=gate['minimum_mean_structure_minus_nuisance']
  atlas.append({'joint_tuple_id':tid,'events':len(ids),'physical_folios':len(fol),'sections':len({events[i]['section'] for i in ids}),'registers':len({events[i]['register'] for i in ids}),'mean_signature_probability':f'{mean:.12f}','mean_structure_minus_nuisance':f'{delta:.12f}','min_folio_mean':f'{min(fm.values()):.12f}','max_folio_mean':f'{max(fm.values()):.12f}','folio_fraction_mean_ge_0_5':f'{frac:.12f}','candidate_gate':'PASS' if promoted else 'FAIL','anonymous_class':'CMP_LOCAL_HEAD_SIGNATURE' if promoted else 'UNASSIGNED','semantic_state':'UNASSIGNED'})
 atlas.sort(key=lambda r:(r['candidate_gate']!='PASS',-float(r['mean_structure_minus_nuisance']),-int(r['physical_folios']),r['joint_tuple_id']))
 # Placement-preserving ID randomization; score values stay fixed.
 strata=defaultdict(list)
 for i,(r,o) in enumerate(zip(meta,obs)):
  q=min(3,int(float(o['relative_position'])*4));strata[(r['section'],r['register'],r['hand'],bucket(int(o['record_element_count'])),q)].append(i)
 observed=max((float(r['mean_structure_minus_nuisance']) for r in atlas if int(r['events'])>=12 and int(r['physical_folios'])>=3),default=-1)
 null=[]
 original=[r['joint_tuple_id'] for r in events]
 for world in range(4096):
  rng=random.Random(377000+world);assigned=original[:]
  for ids in strata.values():
   vals=[assigned[i] for i in ids];rng.shuffle(vals)
   for i,v in zip(ids,vals):assigned[i]=v
  groups=defaultdict(list)
  for i,t in enumerate(assigned):groups[t].append(i)
  best=-1
  for ids in groups.values():
   if len(ids)<12 or len({events[i]['physical_folio'] for i in ids})<3:continue
   best=max(best,sum(float(events[i]['structure_minus_nuisance']) for i in ids)/len(ids))
  null.append(best)
 p=(1+sum(x>=observed for x in null))/4097
 write(ART/'gdt377_event_scores.tsv',events);write(ART/'gdt377_tuple_candidate_atlas.tsv',atlas);write(ART/'gdt377_null.tsv',[{'observed_max_mean_delta':f'{observed:.12f}','null_worlds':4096,'null_mean':f'{np.mean(null):.12f}','null_sd':f'{np.std(null):.12f}','inclusive_p':f'{p:.12f}'}])
 passed=[r for r in atlas if r['candidate_gate']=='PASS'];outputs=[ART/'gdt377_event_scores.tsv',ART/'gdt377_tuple_candidate_atlas.tsv',ART/'gdt377_null.tsv']
 result={'schema':'GDT377_RESULT_V1','status':'ANONYMOUS_LOCAL_HEAD_SIGNATURE_CANDIDATES_NOMINATED' if passed else 'NO_STABLE_VOYNICH_TRANSFER_CANDIDATE','events':len(events),'records':len(byrec),'tuples':len(atlas),'candidate_tuples':len(passed),'max_null_p':p,'semantic_assignments':0,'f84':{'opened':False,'parsed':False,'retained':False,'scored':False},'inputs':{str(p.relative_to(ROOT)):sha(p) for p in [FREEZE,SOURCE,G376/'src/run.py']},'outputs':{str(p.relative_to(ROOT)):sha(p) for p in outputs},'implementation':{str((BASE/'src/run.py').relative_to(ROOT)):sha(BASE/'src/run.py')},'claim_ceiling':'ANONYMOUS_COMPARATOR_SIGNATURE_NOMINATION_ONLY'};result['content_hash']=content(result);(ART/'gdt377_result.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':result['status'],'candidates':len(passed),'p':p}))
if __name__=='__main__':main()
