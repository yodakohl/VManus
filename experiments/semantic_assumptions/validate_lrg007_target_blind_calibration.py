#!/usr/bin/env python3
"""Independent reconstruction of target-free LRG007 calibration."""
from __future__ import annotations
import os
for v in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):os.environ[v]='32'
import csv,hashlib,json
from pathlib import Path
import numpy as np
HERE=Path(__file__).resolve().parent;R=HERE/'results';P=R/'lrg007_ad_edge_capacity.tsv';M=R/'lrg007_ad_edge_margins.tsv';CAP=R/'lrg007_ad_edge_capacity.json';CAPV=R/'lrg007_ad_edge_capacity_validation.json';SPEC=HERE/'LRG007_TARGET_BLIND_CALIBRATION_SPEC.md';CORE=HERE/'lrg007_core.py';PROD=R/'lrg007_target_blind_calibration.json';REPORT=R/'lrg007_target_blind_calibration_report.md';OUT=R/'lrg007_target_blind_calibration_validation.json';OUTR=R/'lrg007_target_blind_calibration_validation_report.md';KINDS=('NULL','BOTH_FULL','BOTH_REDUCED','FIRST_ONLY','LAST_ONLY','ONE_FOLIO','ONE_SECTION','ONE_PARITY','FOLIO_RANDOM','OPPOSITE_EDGES','REVERSED');N=8192;checks=0
def need(x,m):
 global checks;checks+=1
 if not x:raise RuntimeError(m)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ah(a):return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()
def tab(p):
 with p.open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def geometry():
 p=tab(P);q=tab(M);need(len(p)==4911 and len(q)==132,'geometry');cell=np.asarray([r['cell_id'] for r in p]);folio=np.asarray([r['physical_folio'] for r in p]);section=np.asarray([r['section'] for r in p]);position=np.asarray([r['position'] for r in p]);cells=tuple(sorted(set(cell)));folios=tuple(sorted(set(folio),key=lambda z:int(z[1:])));m={r['cell_id']:(int(r['A_rows']),int(r['D_rows']),int(r['other_rows']),int(r['total_rows'])) for r in q};need(len(cells)==132 and len(folios)==16 and set(cells)==set(m),'counts');return cell,folio,section,position,cells,folios,m
def make_weights(cell,folio,position,cells,folios):
 w=np.zeros((len(cell),2));nf={f:len(set(cell[folio==f])) for f in folios}
 for c in cells:
  idx=np.flatnonzero(cell==c);f=str(folio[idx[0]]);base=1/(len(folios)*nf[f]);fi=idx[position[idx]=='FIRST'];co=idx[position[idx]=='CORE'];la=idx[position[idx]=='LAST'];w[fi,0]=base/len(fi);w[co,0]=-base/len(co);w[la,1]=base/len(la);w[co,1]=-base/len(co)
 return w
def make_null(cell,cells,m,w):
 rng=np.random.default_rng(70072026);out=np.zeros((N,2))
 for c in cells:
  idx=np.flatnonzero(cell==c);a,d,o,n=m[c];values=np.asarray([1]*a+[-1]*d+[0]*o,dtype=np.int8);order=np.argsort(rng.random((N,n)),axis=1);out+=values[order]@w[idx]
 return out
def make_world(cell,folio,section,position,cells,folios,m,kind,i):
 rng=np.random.default_rng(7_000_000+1000*KINDS.index(kind)+i);x=np.zeros(len(cell),dtype=np.int8)
 for c in cells:
  idx=np.flatnonzero(cell==c);a,d,_o,_n=m[c];pos=position[idx];u=np.zeros(len(idx));amp=0.
  if kind=='BOTH_FULL':u=np.where(pos=='CORE',-1.,1.);amp=3.
  elif kind=='BOTH_REDUCED':u=np.where(pos=='CORE',-1.,1.);amp=1.8
  elif kind=='FIRST_ONLY':u=(pos=='FIRST').astype(float);amp=3.
  elif kind=='LAST_ONLY':u=(pos=='LAST').astype(float);amp=3.
  elif kind=='ONE_FOLIO':u=np.where(pos=='CORE',-1.,1.);amp=3.;u*=folio[idx]==folios[0]
  elif kind=='ONE_SECTION':u=np.where(pos=='CORE',-1.,1.);amp=3.;u*=section[idx]=='B'
  elif kind=='ONE_PARITY':u=np.where(pos=='CORE',-1.,1.);amp=3.;u*=int(str(folio[idx[0]])[1:])%2==0
  elif kind=='FOLIO_RANDOM':
   sign=1 if hashlib.sha256(f'{i}|{folio[idx[0]]}'.encode()).digest()[0]&1 else -1;u=sign*np.where(pos=='CORE',-1.,1.);amp=3.
  elif kind=='OPPOSITE_EDGES':u=np.where(pos=='FIRST',1.,np.where(pos=='LAST',-1.,0.));amp=3.
  elif kind=='REVERSED':u=np.where(pos=='CORE',1.,-1.);amp=3.
  elif kind!='NULL':raise RuntimeError(kind)
  order=np.argsort(rng.standard_normal(len(idx))+amp*u)
  if d:x[idx[order[:d]]]=-1
  if a:x[idx[order[-a:]]]=1
 return x
def f_effect(x,cell,folio,position,cells,folios):
 out=[]
 for f in folios:
  values=[]
  for c in sorted(set(cell[folio==f])):
   idx=np.flatnonzero(cell==c);values.append((float(x[idx[position[idx]=='FIRST']].mean()-x[idx[position[idx]=='CORE']].mean()),float(x[idx[position[idx]=='LAST']].mean()-x[idx[position[idx]=='CORE']].mean())))
  out.append(np.asarray(values).mean(0))
 return np.stack(out)
def score(x,cell,folio,section,position,cells,folios,m,w,null):
 for c in cells:
  idx=np.flatnonzero(cell==c);a,d,o,_=m[c];need((int(np.count_nonzero(x[idx]==1)),int(np.count_nonzero(x[idx]==-1)),int(np.count_nonzero(x[idx]==0)))==(a,d,o),'margin')
 fe=f_effect(x,cell,folio,position,cells,folios);afe=f_effect((x==1).astype(float),cell,folio,position,cells,folios);dfe=-f_effect((x==-1).astype(float),cell,folio,position,cells,folios);t=fe.mean(0);mu=null.mean(0);sd=null.std(0,ddof=0);z=(t-mu)/sd;mx=((null-mu)/sd).max(1);nums=np.asarray([int(f[1:]) for f in folios]);sf=np.asarray([str(section[np.flatnonzero(folio==f)[0]]) for f in folios]);metrics=[]
 for j,name in enumerate(('FIRST_MINUS_CORE','LAST_MINUS_CORE')):
  vals=fe[:,j];p=(1+int(np.count_nonzero(mx>=z[j])))/(N+1);sec={s:float(vals[sf==s].mean()) for s in ('B','P')};par={'ODD':float(vals[nums%2==1].mean()),'EVEN':float(vals[nums%2==0].mean())};sb=min(sec.values())/max(sec.values()) if max(sec.values())>0 else float('-inf');pb=min(par.values())/max(par.values()) if max(par.values())>0 else float('-inf');dele=[float(np.delete(vals,k).mean()) for k in range(len(folios))];con=float(np.max(np.abs(vals))/np.abs(vals).sum()) if np.abs(vals).sum() else 1.;ac=float(afe[:,j].mean());dc=float(dfe[:,j].mean());g={'fwer_p_at_most_001':p<=.01,'z_at_least_3':z[j]>=3,'effect_at_least_008':t[j]>=.08,'positive_folios_at_least_12':int(np.count_nonzero(vals>0))>=12,'both_sections_at_least_004':min(sec.values())>=.04,'section_balance_at_least_025':sb>=.25,'both_parities_at_least_004':min(par.values())>=.04,'parity_balance_at_least_035':pb>=.35,'all_deletions_at_least_004':min(dele)>=.04,'concentration_at_most_030':con<=.30,'A_component_at_least_0015':ac>=.015,'D_component_at_least_0015':dc>=.015};g={k:bool(v) for k,v in g.items()};metrics.append({'channel':name,'effect':float(t[j]),'null_mean':float(mu[j]),'null_sd':float(sd[j]),'z':float(z[j]),'fwer_p':p,'positive_folios':int(np.count_nonzero(vals>0)),'folio_effects':{f:float(v) for f,v in zip(folios,vals,strict=True)},'section_effects':sec,'section_balance_ratio':sb,'parity_effects':par,'parity_balance_ratio':pb,'minimum_deletion':min(dele),'maximum_absolute_folio_concentration':con,'A_component':ac,'D_component':dc,'gates':g,'passes':all(g.values())})
 return {'metrics':metrics,'joint_pass':all(v['passes'] for v in metrics),'feature_sha256':ah(x),'null_sha256':ah(null),'weight_sha256':ah(w)}
def main():
 need(PROD.exists() and REPORT.exists() and not OUT.exists() and not OUTR.exists(),'paths');cell,folio,section,position,cells,folios,m=geometry();w=make_weights(cell,folio,position,cells,folios);null=make_null(cell,cells,m,w);records=[]
 for kind in KINDS:
  for i in range(64 if kind=='NULL' else 8):records.append({'kind':kind,'world':i,'evaluation':score(make_world(cell,folio,section,position,cells,folios,m,kind,i),cell,folio,section,position,cells,folios,m,w,null)})
 counts={k:sum(r['evaluation']['joint_pass'] for r in records if r['kind']==k) for k in KINDS};gates={'zero_null':counts['NULL']==0,'all_full':counts['BOTH_FULL']==8,'all_reduced':counts['BOTH_REDUCED']==8,'zero_controls':all(counts[k]==0 for k in KINDS[3:])};passed=all(gates.values());status='PASS_TARGET_BLIND_LRG007_CALIBRATION' if passed else 'STOP_TARGET_BLIND_LRG007_CALIBRATION';decision='GO_CLEAN_VALIDATION' if passed else 'DO_NOT_OPEN_TARGET';expected={'status':status,'decision':decision,'claim_ceiling':'Calibration only; no real family-position association opening closing word function meaning plaintext or translation.','inputs':{'panel':sha(P),'margins':sha(M),'capacity':sha(CAP),'capacity_validation':sha(CAPV)},'spec_sha256':sha(SPEC),'core_sha256':sha(CORE),'weight_sha256':ah(w),'null_sha256':ah(null),'counts':counts,'gates':gates,'records':records,'real_family_positions_accessed':False};need(json.loads(PROD.read_text())==expected,'full result');report='\n'.join(['# LRG007 target-blind calibration','',f'Status: **{status}**.','',f"Passes: null **{counts['NULL']}/64**, full/reduced **{counts['BOTH_FULL']}/8 / {counts['BOTH_REDUCED']}/8**, controls "+', '.join(f"{k.lower()} **{counts[k]}/8**" for k in KINDS[3:])+'.','',f'Decision: **{decision}**.','','No real family-position association was accessed. No opening, closing, word, function, meaning, plaintext, or translation follows.','']);need(REPORT.read_text()==report,'report');result={'status':'PASS_CLEAN_LRG007_CALIBRATION_RECONSTRUCTION','checks':checks,'discrepancies':0,'production_sha256':sha(PROD),'report_sha256':sha(REPORT),'counts':counts,'decision':decision};OUT.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf8',newline='\n');OUTR.write_text('\n'.join(['# LRG007 calibration validation','',f"Status: **{result['status']}**.",'',f"Independent code reconstructs all worlds, exact-margin assignments, both channels, robustness gates, decision, and report in **{checks}** checks with zero discrepancies.",'','No real family-position association was accessed.','']),encoding='utf8',newline='\n');print(json.dumps(result,indent=2,sort_keys=True))
if __name__=='__main__':main()
