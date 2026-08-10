#!/usr/bin/env python3
"""Run target-free two-sided LRG006 calibration."""
from __future__ import annotations
import os
for v in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):os.environ[v]='32'
import hashlib,json
from pathlib import Path
import numpy as np
from lrg006_core import ah,coef,evaluate,load,random_labels
HERE=Path(__file__).resolve().parent;R=HERE/'results';P=R/'lrg006_a1_member_capacity.tsv';Q=R/'lrg006_a1_member_quotas.tsv';CAP=R/'lrg006_a1_member_capacity.json';CAPV=R/'lrg006_a1_member_capacity_validation.json';SPEC=HERE/'LRG006_TARGET_BLIND_CALIBRATION_SPEC.md';CORE=HERE/'lrg006_core.py';OUT=R/'lrg006_target_blind_calibration.json';REPORT=R/'lrg006_target_blind_calibration_report.md';KINDS=('NULL','POS_FULL','NEG_FULL','POS_REDUCED','NEG_REDUCED','ONE_FOLIO','ONE_SECTION','ONE_PARITY','FOLIO_RANDOM','CELL_CONSTANT')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def world(g,kind,i):
 rng=np.random.default_rng(6_000_000+1000*KINDS.index(kind)+i);y=random_labels(g,rng);priority=rng.standard_normal(len(y));orient=0.;mask=np.ones(len(y),dtype=bool)
 if kind=='POS_FULL':orient=3.
 elif kind=='NEG_FULL':orient=-3.
 elif kind=='POS_REDUCED':orient=1.8
 elif kind=='NEG_REDUCED':orient=-1.8
 elif kind=='ONE_FOLIO':orient=3.;mask=g.folio==g.folios[0]
 elif kind=='ONE_SECTION':orient=3.;mask=g.section=='B'
 elif kind=='ONE_PARITY':orient=3.;mask=np.asarray([int(f[1:])%2==0 for f in g.folio])
 elif kind=='FOLIO_RANDOM':
  signs={f:(1 if hashlib.sha256(f'{i}|{f}'.encode()).digest()[0]&1 else -1) for f in g.folios};priority+=3*(2*y-1)*np.asarray([signs[f] for f in g.folio])
 elif kind=='CELL_CONSTANT':
  return y,np.asarray([hashlib.sha256(f'{i}|{c}'.encode()).digest()[0]&1 for c in g.cell],dtype=np.float64)
 elif kind!='NULL':raise RuntimeError(kind)
 priority+=orient*(2*y-1)*mask;x=np.zeros(len(y))
 for c in g.cells:
  idx=np.flatnonzero(g.cell==c);k=max(1,min(len(idx)-1,int(round(.80*len(idx)))));x[idx[np.argpartition(priority[idx],-k)[-k:]]]=1
 return y,x
def main():
 if OUT.exists() or REPORT.exists():raise RuntimeError('output')
 g=load(P,Q);c=coef(g);worlds=[]
 for kind in KINDS:
  for i in range(64 if kind=='NULL' else 8):
   y,x=world(g,kind,i);worlds.append((kind,i,y,x))
 matrix=np.stack([x for _,_,_,x in worlds],axis=1);nulls=c@matrix;records=[]
 for j,(kind,i,y,x) in enumerate(worlds):records.append({'kind':kind,'world':i,'evaluation':evaluate(x,y,g,c,nulls[:,j])})
 counts={k:sum(r['evaluation']['passes'] for r in records if r['kind']==k) for k in KINDS};gates={'zero_null':counts['NULL']==0,'all_positive_full':counts['POS_FULL']==8,'all_negative_full':counts['NEG_FULL']==8,'all_positive_reduced':counts['POS_REDUCED']==8,'all_negative_reduced':counts['NEG_REDUCED']==8,'zero_adversaries':all(counts[k]==0 for k in KINDS[5:])};status='PASS_TARGET_BLIND_LRG006_CALIBRATION' if all(gates.values()) else 'STOP_TARGET_BLIND_LRG006_CALIBRATION';decision='GO_CLEAN_VALIDATION' if all(gates.values()) else 'DO_NOT_OPEN_TARGET';result={'status':status,'decision':decision,'claim_ceiling':'Calibration only; no real A1 feature role association member function meaning plaintext or translation.','inputs':{'panel':sha(P),'quotas':sha(Q),'capacity':sha(CAP),'capacity_validation':sha(CAPV)},'spec_sha256':sha(SPEC),'core_sha256':sha(CORE),'coefficient_sha256':ah(c),'counts':counts,'gates':gates,'records':records,'real_feature_accessed':False,'real_roles_accessed':False};text=json.dumps(result,indent=2,sort_keys=True)+'\n';OUT.write_text(text,encoding='utf8',newline='\n');report='\n'.join(['# LRG006 target-blind calibration','',f'Status: **{status}**.','',f"Passes: null **{counts['NULL']}/64**, positive full/reduced **{counts['POS_FULL']}/8 / {counts['POS_REDUCED']}/8**, negative full/reduced **{counts['NEG_FULL']}/8 / {counts['NEG_REDUCED']}/8**, adversaries "+', '.join(f"{k.lower()} **{counts[k]}/8**" for k in KINDS[5:])+'.','',f'Decision: **{decision}**.','','No real A1 feature or role association was opened. No function, meaning, plaintext, or translation follows.','']);REPORT.write_text(report,encoding='utf8',newline='\n');print(text,end='')
if __name__=='__main__':main()
