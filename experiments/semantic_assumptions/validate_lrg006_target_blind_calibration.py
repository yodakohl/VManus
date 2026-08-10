#!/usr/bin/env python3
"""Independent reconstruction of LRG006 target-blind calibration."""
from __future__ import annotations
import os
for v in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):os.environ[v]='32'
import csv,hashlib,json
from pathlib import Path
import numpy as np
HERE=Path(__file__).resolve().parent;R=HERE/'results';P=R/'lrg006_a1_member_capacity.tsv';Q=R/'lrg006_a1_member_quotas.tsv';CAP=R/'lrg006_a1_member_capacity.json';CAPV=R/'lrg006_a1_member_capacity_validation.json';SPEC=HERE/'LRG006_TARGET_BLIND_CALIBRATION_SPEC.md';CORE=HERE/'lrg006_core.py';PROD=R/'lrg006_target_blind_calibration.json';REPORT=R/'lrg006_target_blind_calibration_report.md';OUT=R/'lrg006_target_blind_calibration_validation.json';OUTR=R/'lrg006_target_blind_calibration_validation_report.md';KINDS=('NULL','POS_FULL','NEG_FULL','POS_REDUCED','NEG_REDUCED','ONE_FOLIO','ONE_SECTION','ONE_PARITY','FOLIO_RANDOM','CELL_CONSTANT');A=8192;SEED=60062026;checks=0
def need(x,m):
 global checks;checks+=1
 if not x:raise RuntimeError(m)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ah(x):return hashlib.sha256(np.ascontiguousarray(x).tobytes()).hexdigest()
def tab(p):
 with p.open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def geom():
 p=tab(P);q=tab(Q);need(len(p)==677 and len(q)==69,'geometry');cell=np.asarray([r['cell_id'] for r in p]);folio=np.asarray([r['physical_folio'] for r in p]);section=np.asarray([r['section'] for r in p]);quota={r['cell_id']:int(r['label_rows']) for r in q};cells=tuple(sorted(quota));folios=tuple(sorted(set(folio),key=lambda x:int(x[1:])));need(len(folios)==13,'folios');return cell,folio,section,quota,cells,folios
def labels(cell,quota,cells,rng):
 y=np.zeros(len(cell),dtype=np.int8)
 for c in cells:
  idx=np.flatnonzero(cell==c);h=quota[c];y[idx[np.argpartition(rng.random(len(idx)),h-1)[:h]]]=1
 return y
def coefficient(cell,folio,quota,cells,folios):
 out=np.zeros((A,len(cell)));rng=np.random.default_rng(SEED)
 for c in cells:
  idx=np.flatnonzero(cell==c);f=str(folio[idx[0]]);nc=len(set(cell[folio==f]));h=quota[c];lo=len(idx)-h;out[:,idx]=-1/(len(folios)*nc*lo);chosen=idx[np.argpartition(rng.random((A,len(idx))),h-1,axis=1)[:,:h]];out[np.arange(A)[:,None],chosen]=1/(len(folios)*nc*h)
 need(np.max(np.abs(out.sum(1)))<1e-12,'coefficient');return out
def world(cell,folio,section,quota,cells,folios,kind,i):
 rng=np.random.default_rng(6_000_000+1000*KINDS.index(kind)+i);y=labels(cell,quota,cells,rng);priority=rng.standard_normal(len(y));orient=0.;mask=np.ones(len(y),dtype=bool)
 if kind=='POS_FULL':orient=3.
 elif kind=='NEG_FULL':orient=-3.
 elif kind=='POS_REDUCED':orient=1.8
 elif kind=='NEG_REDUCED':orient=-1.8
 elif kind=='ONE_FOLIO':orient=3.;mask=folio==folios[0]
 elif kind=='ONE_SECTION':orient=3.;mask=section=='B'
 elif kind=='ONE_PARITY':orient=3.;mask=np.asarray([int(f[1:])%2==0 for f in folio])
 elif kind=='FOLIO_RANDOM':
  signs={f:(1 if hashlib.sha256(f'{i}|{f}'.encode()).digest()[0]&1 else -1) for f in folios};priority+=3*(2*y-1)*np.asarray([signs[f] for f in folio])
 elif kind=='CELL_CONSTANT':return y,np.asarray([hashlib.sha256(f'{i}|{c}'.encode()).digest()[0]&1 for c in cell],dtype=float)
 elif kind!='NULL':raise RuntimeError(kind)
 priority+=orient*(2*y-1)*mask;x=np.zeros(len(y))
 for c in cells:
  idx=np.flatnonzero(cell==c);k=max(1,min(len(idx)-1,int(round(.8*len(idx)))));x[idx[np.argpartition(priority[idx],-k)[-k:]]]=1
 return y,x
def evaluate(x,y,cell,folio,section,quota,cells,folios,coef,null):
 fe=[]
 for f in folios:
  vals=[]
  for c in sorted(set(cell[folio==f])):
   idx=np.flatnonzero(cell==c);vals.append(float(x[idx[y[idx]==1]].mean()-x[idx[y[idx]==0]].mean()))
  fe.append(float(np.mean(vals)))
 fe=np.asarray(fe);t=float(fe.mean());mu=float(null.mean());sd=float(null.std(ddof=0));z=(t-mu)/sd if sd>0 else 0.;p=(1+int(np.count_nonzero(np.abs(null)>=abs(t))))/(A+1);sign=1 if t>=0 else -1;nums=np.asarray([int(f[1:]) for f in folios]);sf=np.asarray([str(section[np.flatnonzero(folio==f)[0]]) for f in folios]);sec={s:sign*float(fe[sf==s].mean()) for s in ('B','P')};par={'ODD':sign*float(fe[nums%2==1].mean()),'EVEN':sign*float(fe[nums%2==0].mean())};sb=min(sec.values())/max(sec.values()) if max(sec.values())>0 else float('-inf');pb=min(par.values())/max(par.values()) if max(par.values())>0 else float('-inf');dele=[sign*float(np.delete(fe,k).mean()) for k in range(13)];con=float(np.max(np.abs(fe))/np.abs(fe).sum()) if np.abs(fe).sum() else 1.;g={'p_at_most_001':p<=.01,'absolute_z_at_least_3':abs(z)>=3,'absolute_effect_at_least_008':abs(t)>=.08,'directional_support_at_least_10':int(np.count_nonzero(sign*fe>0))>=10,'both_sections_signed_at_least_004':min(sec.values())>=.04,'section_balance_at_least_035':sb>=.35,'both_parities_signed_at_least_004':min(par.values())>=.04,'parity_balance_at_least_035':pb>=.35,'all_deletions_signed_at_least_004':min(dele)>=.04,'concentration_at_most_030':con<=.30};return {'effect':t,'direction':'A1_POSITIVE' if sign>0 else 'A1_NEGATIVE','null_mean':mu,'null_sd':sd,'z':z,'p':p,'positive_direction_folios':int(np.count_nonzero(sign*fe>0)),'folio_effects':{f:float(v) for f,v in zip(folios,fe,strict=True)},'signed_section_effects':sec,'section_balance_ratio':sb,'signed_parity_effects':par,'parity_balance_ratio':pb,'minimum_signed_deletion':min(dele),'maximum_absolute_folio_concentration':con,'null_sha256':ah(null),'feature_sha256':ah(x),'label_sha256':ah(y),'gates':g,'passes':all(g.values())}
def main():
 cell,folio,section,quota,cells,folios=geom();coef=coefficient(cell,folio,quota,cells,folios);worlds=[]
 for kind in KINDS:
  for i in range(64 if kind=='NULL' else 8):
   y,x=world(cell,folio,section,quota,cells,folios,kind,i);worlds.append((kind,i,y,x))
 matrix=np.stack([x for _,_,_,x in worlds],1);nulls=coef@matrix;records=[{'kind':kind,'world':i,'evaluation':evaluate(x,y,cell,folio,section,quota,cells,folios,coef,nulls[:,j])} for j,(kind,i,y,x) in enumerate(worlds)];counts={k:sum(r['evaluation']['passes'] for r in records if r['kind']==k) for k in KINDS};gates={'zero_null':counts['NULL']==0,'all_positive_full':counts['POS_FULL']==8,'all_negative_full':counts['NEG_FULL']==8,'all_positive_reduced':counts['POS_REDUCED']==8,'all_negative_reduced':counts['NEG_REDUCED']==8,'zero_adversaries':all(counts[k]==0 for k in KINDS[5:])};status='PASS_TARGET_BLIND_LRG006_CALIBRATION' if all(gates.values()) else 'STOP_TARGET_BLIND_LRG006_CALIBRATION';decision='GO_CLEAN_VALIDATION' if all(gates.values()) else 'DO_NOT_OPEN_TARGET';expected={'status':status,'decision':decision,'claim_ceiling':'Calibration only; no real A1 feature role association member function meaning plaintext or translation.','inputs':{'panel':sha(P),'quotas':sha(Q),'capacity':sha(CAP),'capacity_validation':sha(CAPV)},'spec_sha256':sha(SPEC),'core_sha256':sha(CORE),'coefficient_sha256':ah(coef),'counts':counts,'gates':gates,'records':records,'real_feature_accessed':False,'real_roles_accessed':False};need(json.loads(PROD.read_text())==expected,'full result');report='\n'.join(['# LRG006 target-blind calibration','',f'Status: **{status}**.','',f"Passes: null **{counts['NULL']}/64**, positive full/reduced **{counts['POS_FULL']}/8 / {counts['POS_REDUCED']}/8**, negative full/reduced **{counts['NEG_FULL']}/8 / {counts['NEG_REDUCED']}/8**, adversaries "+', '.join(f"{k.lower()} **{counts[k]}/8**" for k in KINDS[5:])+'.','',f'Decision: **{decision}**.','','No real A1 feature or role association was opened. No function, meaning, plaintext, or translation follows.','']);need(REPORT.read_text()==report,'report');result={'status':'PASS_CLEAN_RECONSTRUCTION_OF_LRG006_CALIBRATION_STOP' if decision=='DO_NOT_OPEN_TARGET' else 'PASS_CLEAN_LRG006_CALIBRATION_RECONSTRUCTION','checks':checks,'discrepancies':0,'production_sha256':sha(PROD),'report_sha256':sha(REPORT),'counts':counts,'decision':decision,'target_accessed':False};OUT.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf8',newline='\n');OUTR.write_text('\n'.join(['# LRG006 calibration validation','',f"Status: **{result['status']}**.",'',f"Independent code reconstructs all worlds, the assignment matrix, statistics, gates, decision, and report in **{checks}** checks with zero discrepancies.",'','No real A1 association was accessed.','']),encoding='utf8',newline='\n');print(json.dumps(result,indent=2,sort_keys=True))
if __name__=='__main__':main()
