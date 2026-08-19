#!/usr/bin/env python3
"""Freeze the final CoReMA structural model before Voynich scoring."""
from __future__ import annotations
import csv,hashlib,importlib.util,json
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[4];BASE=ROOT/'experiments/yolo/gdt377_local_head_signature_transfer';ART=BASE/'artifacts'
G376=ROOT/'experiments/yolo/gdt376_corema_hidden_function_oracle';OBS=G376/'artifacts/gdt376_observation_layer.tsv';ORACLE=ROOT/'gdt176_corema_role_oracle.tsv';RESULT=G376/'artifacts/gdt376_result.json';TARGET=ROOT/'gdt327_joint_tuple_interlinear.tsv'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):
 with p.open(encoding='utf-8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def loadmod():
 s=importlib.util.spec_from_file_location('gdt376_frozen',G376/'src/run.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def content(d):
 x=dict(d);x.pop('content_hash',None);return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def main():
 ART.mkdir(parents=True,exist_ok=True);r=json.loads(RESULT.read_text());assert r['promoted_endpoints']==['PREDICATE_HEAD_WITH_DEPENDENTS'];m=loadmod();obs=read(OBS);oracle=read(ORACLE);Y=m.labels(oracle)['PREDICATE_HEAD_WITH_DEPENDENTS'];static,_=m.static_features(obs);valid=[i for i,x in enumerate(obs) if x['observable_surface']=='1'];learned,_=m.learned_form_features(obs,valid,valid)
 Xn=[static[i][0] for i in valid];Xs=[static[i][0]+static[i][1]+learned[i] for i in valid];yn=Y[valid]
 nuisance=m.fit_logistic(Xn,yn);structure=m.fit_logistic(Xs,yn)
 def pack(model):
  b,mu,sd=model;return {'beta':[float(x) for x in b],'mean':[float(x) for x in mu],'sd':[float(x) for x in sd]}
 model={'schema':'GDT377_COMPARATOR_MODEL_V1','status':'FROZEN_BEFORE_VOYNICH_SCORE','endpoint':'PREDICATE_HEAD_WITH_DEPENDENTS','semantic_state':'UNASSIGNED','training_rows':len(valid),'positive_rows':int(yn.sum()),'nuisance_model':pack(nuisance),'structure_model':pack(structure),'feature_mapping':{'voynich_collection_id':'page','voynich_recipe_id':'page plus record_ordinal','voynich_recipe_ordinal':'record_ordinal','voynich_element':'atomic GDT327 event in stored physical order','opaque_form_id':'joint_tuple_id','direct_token_count':1,'record_element_count':'groups in page-record','relative_position':'event ordinal divided by record elements'},'candidate_gate':{'minimum_events':12,'minimum_physical_folios':3,'minimum_mean_structure_probability':0.5,'minimum_folio_fraction_mean_ge_0_5':0.75,'minimum_mean_structure_minus_nuisance':0.0},'null':{'worlds':4096,'shuffle':'joint_tuple IDs within section x register x hand x record-length bucket x within-record-position quartile','statistic':'maximum powered tuple mean structural-minus-nuisance score','inclusive_plus_one':True},'claim_ceiling':'ANONYMOUS_COMPARATOR_SIGNATURE_NOMINATION_ONLY','f84_accessed':False,'voynich_scored':False,'inputs':{str(p.relative_to(ROOT)):sha(p) for p in [OBS,ORACLE,RESULT,TARGET,G376/'src/run.py']}}
 model['content_hash']=content(model);(ART/'gdt377_comparator_model_freeze.json').write_text(json.dumps(model,indent=2,sort_keys=True)+'\n');print(json.dumps({'rows':len(valid),'positive':int(yn.sum()),'status':model['status']}))
if __name__=='__main__':main()
