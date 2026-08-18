#!/usr/bin/env python3
"""Independently reconstruct the GDT322 lexicon, fit, coverage, and bindings."""
import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

R=Path(__file__).resolve().parent; SOURCE=R/'gdt278_native_event_inventory.tsv'; PANEL=R/'gdt318_frozen_panel.tsv'; LEXICON=R/'gdt322_opaque_cell_lexicon.tsv'; MODEL=R/'gdt322_renderer_model.json'; RESULT=R/'gdt322_result.json'; OUT=R/'gdt322_validation.json'
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def can(v): return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
def read(p):
 with Path(p).open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def softmax(a):
 z=a-a.max(axis=1,keepdims=True);e=np.exp(z);return e/e.sum(axis=1,keepdims=True)
def fit(offsets,truth,line,prev,si,qi,ridge):
 b=np.zeros(2)
 for _ in range(60):
  scores=offsets.copy();scores[:,si]+=b[0]*line;scores[:,qi]+=b[1]*prev;p=softmax(scores);ys=truth==si;yq=truth==qi;g=np.array([np.sum((p[:,si]-ys)*line)+ridge*b[0],np.sum((p[:,qi]-yq)*prev)+ridge*b[1]]);H=np.array([[np.sum(p[:,si]*(1-p[:,si])*line*line)+ridge,np.sum(-p[:,si]*p[:,qi]*line*prev)],[np.sum(-p[:,si]*p[:,qi]*line*prev),np.sum(p[:,qi]*(1-p[:,qi])*prev*prev)+ridge]]);step=np.linalg.pinv(H)@g;b-=step
  if abs(step).max()<1e-10:break
 return b
def main():
 checks=[]
 def ck(n,v):
  if not v:raise AssertionError(n)
  checks.append(n)
 classes=['NONE','ch','che','d','q','s','sh','t'];ci={v:i for i,v in enumerate(classes)};source=[r for r in read(SOURCE) if r['control_id']=='VOYNICH_REFERENCE'];panel=read(PANEL);source_map={hashlib.sha256(r['observation_id'].encode()).hexdigest()[:20]:r for r in source};ck('join',all(r['event_id_sha256'] in source_map for r in panel));groups=defaultdict(list)
 for r in panel:groups[r['cell_id']].append((r,source_map[r['event_id_sha256']]))
 stored={r['cell_id']:r for r in read(LEXICON)};ck('cells',len(groups)==len(stored)==126)
 for cell,members in groups.items():
  counts=Counter(x['wrapper'] for _,x in members);row=stored[cell];ck('lexicon',int(row['events'])==len(members) and int(row['folios'])==len({r['physical_folio'] for r,_ in members}) and json.loads(row['wrapper_counts_json'])=={w:counts[w] for w in classes} and int(row['line_start_events'])==sum(int(r['line_first']) for r,_ in members) and int(row['prev_dy_events'])==sum(int(r['prev_dy']) for r,_ in members))
 cell_index={cell:i for i,cell in enumerate(sorted(groups))};counts=np.full((len(groups),len(classes)),.5);truth=[]
 for r in panel:
  y=ci[source_map[r['event_id_sha256']]['wrapper']];truth.append(y);counts[cell_index[r['cell_id']],y]+=1
 offsets=np.array([np.log(counts[cell_index[r['cell_id']]]) for r in panel]);truth=np.array(truth);line=np.array([float(r['line_first']) for r in panel]);prev=np.array([float(r['prev_dy']) for r in panel]);beta=fit(offsets,truth,line,prev,ci['s'],ci['q'],10.0);model=json.loads(MODEL.read_text());stored_hash=model.pop('content_sha256');ck('model_content',stored_hash==can(model));ck('beta',abs(model['beta_s_line_first']-beta[0])<5e-12 and abs(model['beta_q_prev_dy']-beta[1])<5e-12);total_cells=len({(r['page_host'],r['local_frame'],r['inner_d'],r['right_family'],r['dy_closure'],r['b3']) for r in source});ck('coverage',model['coverage']['events']==5607 and model['coverage']['total_voynich_reference_events']==8448 and model['coverage']['cells']==126 and model['coverage']['total_observed_cells']==total_cells);ck('model_hashes',all(model['inputs'][n]==sha(R/n) for n in model['inputs']) and all(model['outputs'][n]==sha(R/n) for n in model['outputs']) and all(model['implementation'][n]==sha(R/n) for n in model['implementation']));result=json.loads(RESULT.read_text());result_hash=result.pop('content_sha256');ck('result_content',result_hash==can(result));ck('result',result['status']=='EXECUTABLE_TWO_RULE_RENDERER' and abs(result['summary']['beta_s_line_first']-beta[0])<5e-12 and abs(result['summary']['beta_q_prev_dy']-beta[1])<5e-12);ck('result_hashes',all(result['inputs'][n]==sha(R/n) for n in result['inputs']) and all(result['outputs'][n]==sha(R/n) for n in result['outputs']) and all(result['documents'][n]==sha(R/n) for n in result['documents']) and all(result['implementation'][n]==sha(R/n) for n in result['implementation']));ck('f84',not any(model['f84'].values()) and not any(result['f84'].values()) and not any(r['page'].startswith('f84') or r['locus'].startswith('f84') for r in source));v={'schema':'GDT322_EXECUTABLE_RENDERER_VALIDATION_V1','status':'PASS','checks_passed':len(checks),'checks':checks,'result_sha256':sha(RESULT),'model_sha256':sha(MODEL),'f84_rows':0,'scope':'INDEPENDENT_LEXICON_FULL_FIT_COVERAGE_AND_BINDING_RECONSTRUCTION'};v['content_sha256']=can(v);OUT.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':'PASS','checks':len(checks)},sort_keys=True))
if __name__=='__main__':main()
