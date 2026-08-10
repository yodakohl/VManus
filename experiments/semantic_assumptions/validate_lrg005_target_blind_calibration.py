#!/usr/bin/env python3
"""Clean-room reconstruction of the LRG005 target-blind calibration."""
from __future__ import annotations
import os
for v in ("OPENBLAS_NUM_THREADS","OMP_NUM_THREADS","MKL_NUM_THREADS","NUMEXPR_NUM_THREADS"):os.environ[v]="32"
import csv,hashlib,json
from collections import Counter
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent;R=HERE/"results";PANEL=R/"lrg005_d1_extension_capacity.tsv";QUOTAS=R/"lrg005_d1_extension_quotas.tsv";CAP=R/"lrg005_d1_extension_capacity.json";CAPVAL=R/"lrg005_d1_extension_capacity_validation.json";SPEC=HERE/"LRG005_TARGET_BLIND_CALIBRATION_SPEC.md";CORE=HERE/"lrg005_core.py";RUNNER=HERE/"run_lrg005_target_blind_calibration.py";PROD=R/"lrg005_target_blind_calibration.json";REPORT=R/"lrg005_target_blind_calibration_report.md";OUT=R/"lrg005_target_blind_calibration_validation.json";OUT_REPORT=R/"lrg005_target_blind_calibration_validation_report.md"
A=8192;SEED=510052026;KINDS=("NULL","DISTRIBUTED_FULL","DISTRIBUTED_REDUCED","ONE_FOLIO","ONE_SECTION","ONE_PARITY","FOLIO_RANDOM","ONE_CHANNEL","OPPOSITE_CHANNEL","CELL_CONSTANT");CHANNELS=("D1_BARE","D1_OTHER");checks=0
def need(x,m):
 global checks;checks+=1
 if not x:raise RuntimeError(m)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ah(a):return hashlib.sha256(np.ascontiguousarray(a).tobytes(order="C")).hexdigest()
def tab(p):
 with p.open(encoding="utf8",newline="") as h:return list(csv.DictReader(h,delimiter="\t"))
def geometry():
 p=tab(PANEL);q=tab(QUOTAS);need(len(p)==536 and len(q)==68,"counts");need(len({x['unit_id'] for x in p})==536,"units");quota={x['cell_id']:int(x['label_rows']) for x in q};total={x['cell_id']:int(x['total_rows']) for x in q};cells=tuple(sorted(quota));unit=np.asarray([x['unit_id'] for x in p]);cell=np.asarray([x['cell_id'] for x in p]);folio=np.asarray([x['physical_folio'] for x in p]);section=np.asarray([x['section'] for x in p]);folios=tuple(sorted(set(folio),key=lambda x:int(x[1:])));need(len(folios)==13,"folios")
 for c in cells:
  idx=np.flatnonzero(cell==c);need(len(idx)==total[c] and 0<quota[c]<len(idx),"quota");need(len(set(folio[idx]))==len(set(section[idx]))==1,"metadata")
 return unit,cell,folio,section,quota,cells,folios
def labels(cell,quota,cells,rng):
 y=np.zeros(len(cell),dtype=np.int8)
 for c in cells:
  idx=np.flatnonzero(cell==c);h=quota[c];chosen=idx[np.argpartition(rng.random(len(idx)),h-1)[:h]];y[chosen]=1
 return y
def coefficients(cell,folio,quota,cells,folios):
 out=np.zeros((A,len(cell)));rng=np.random.default_rng(SEED)
 for c in cells:
  idx=np.flatnonzero(cell==c);f=str(folio[idx[0]]);nc=len(set(cell[folio==f]));h=quota[c];lo=len(idx)-h;out[:,idx]=-1/(len(folios)*nc*lo);chosen=idx[np.argpartition(rng.random((A,len(idx))),h-1,axis=1)[:,:h]];out[np.arange(A)[:,None],chosen]=1/(len(folios)*nc*h)
 need(np.isfinite(out).all() and np.max(np.abs(out.sum(1)))<1e-12,"coefficients");return out
def make_world(cell,folio,section,quota,cells,folios,kind,index):
 rng=np.random.default_rng(5_000_000+index+1000*KINDS.index(kind));y=labels(cell,quota,cells,rng);s=rng.standard_normal((len(y),2));signed=2*y.astype(float)-1;delta=.60 if kind=="DISTRIBUTED_FULL" else .36
 if kind in {"DISTRIBUTED_FULL","DISTRIBUTED_REDUCED"}:s+=delta*signed[:,None]
 elif kind=="ONE_FOLIO":
  m=folio==folios[0];s[m]+=.8*signed[m,None]
 elif kind=="ONE_SECTION":
  m=section=="B";s[m]+=.6*signed[m,None]
 elif kind=="ONE_PARITY":
  m=np.asarray([int(f[1:])%2==0 for f in folio]);s[m]+=.6*signed[m,None]
 elif kind=="FOLIO_RANDOM":
  signs={f:(1 if (hashlib.sha256(f"{index}|{f}".encode()).digest()[0]&1) else -1) for f in folios};s+=.55*signed[:,None]*np.asarray([signs[f] for f in folio])[:,None]
 elif kind=="ONE_CHANNEL":s[:,0]+=.55*signed
 elif kind=="OPPOSITE_CHANNEL":s[:,0]+=.55*signed;s[:,1]-=.55*signed
 elif kind=="CELL_CONSTANT":
  constants={c:rng.normal() for c in cells};s+=np.asarray([constants[c] for c in cell])[:,None]
 elif kind!="NULL":raise RuntimeError(kind)
 return y,s
def eval_world(s,y,cell,folio,section,folios,coef,null):
 fe=[]
 for f in folios:
  vals=[]
  for c in sorted(set(cell[folio==f])):
   idx=np.flatnonzero(cell==c);hi=idx[y[idx]==1];lo=idx[y[idx]==0];need(len(hi)>0 and len(lo)>0,"mixed");vals.append(s[hi].mean(0)-s[lo].mean(0))
  fe.append(np.stack(vals).mean(0))
 fe=np.stack(fe);obs=fe.mean(0);nums=np.asarray([int(f[1:]) for f in folios]);sf=np.asarray([str(section[np.flatnonzero(folio==f)[0]]) for f in folios]);metrics=[]
 for j,name in enumerate(CHANNELS):
  vals=fe[:,j];t=float(obs[j]);mu=float(null[:,j].mean());sd=float(null[:,j].std(ddof=0));p=(1+int(np.count_nonzero(null[:,j]>=t)))/(A+1);z=(t-mu)/sd if sd>0 else float('-inf');sec={x:float(vals[sf==x].mean()) for x in ('B','P')};par={'ODD':float(vals[nums%2==1].mean()),'EVEN':float(vals[nums%2==0].mean())};sb=min(sec.values())/max(sec.values()) if max(sec.values())>0 else float('-inf');pb=min(par.values())/max(par.values()) if max(par.values())>0 else float('-inf');d=[float(np.delete(vals,k).mean()) for k in range(len(vals))];den=float(np.abs(vals).sum());con=float(np.max(np.abs(vals))/den) if den else 1.;g={"p_at_most_001":p<=.01,"z_at_least_3":z>=3,"effect_at_least_010":t>=.10,"support_at_least_10":int(np.count_nonzero(vals>0))>=10,"both_sections_at_least_005":min(sec.values())>=.05,"section_balance_at_least_035":sb>=.35,"both_parities_at_least_005":min(par.values())>=.05,"parity_balance_at_least_035":pb>=.35,"all_deletions_at_least_005":min(d)>=.05,"concentration_at_most_030":con<=.30};metrics.append({"channel":name,"effect":t,"null_mean":mu,"null_sd":sd,"z":z,"p":p,"positive_folios":int(np.count_nonzero(vals>0)),"folio_effects":{f:float(v) for f,v in zip(folios,vals,strict=True)},"section_effects":sec,"section_balance_ratio":sb,"parity_effects":par,"parity_balance_ratio":pb,"minimum_deletion":min(d),"maximum_absolute_folio_concentration":con,"null_sha256":ah(null[:,j]),"gates":g,"passes":all(g.values())})
 return {"joint_pass":all(m['passes'] for m in metrics),"score_sha256":ah(s),"label_sha256":ah(y),"metrics":metrics}
def main():
 need(PROD.is_file() and REPORT.is_file(),"production absent");unit,cell,folio,section,quota,cells,folios=geometry();coef=coefficients(cell,folio,quota,cells,folios);worlds=[]
 for kind in KINDS:
  for i in range(64 if kind=="NULL" else 8):
   y,s=make_world(cell,folio,section,quota,cells,folios,kind,i);worlds.append((kind,i,y,s))
 stacked=np.concatenate([s for _,_,_,s in worlds],axis=1);nulls=coef@stacked;records=[]
 for w,(kind,i,y,s) in enumerate(worlds):records.append({"kind":kind,"world":i,"evaluation":eval_world(s,y,cell,folio,section,folios,coef,nulls[:,2*w:2*w+2])})
 counts={k:sum(r['evaluation']['joint_pass'] for r in records if r['kind']==k) for k in KINDS};gates={"zero_of_64_null":counts['NULL']==0,"all_full_plants":counts['DISTRIBUTED_FULL']==8,"all_reduced_plants":counts['DISTRIBUTED_REDUCED']==8,"zero_all_adversaries":all(counts[k]==0 for k in KINDS[3:])};status="PASS_TARGET_BLIND_LRG005_CALIBRATION" if all(gates.values()) else "STOP_TARGET_BLIND_LRG005_CALIBRATION";decision="GO_CLEAN_VALIDATION" if all(gates.values()) else "DO_NOT_OPEN_TARGET";expected={"status":status,"decision":decision,"claim_ceiling":"Calibration only; no source member sequence row role target score prefix classifier morpheme word POS sound meaning plaintext or translation.","inputs":{"panel":sha(PANEL),"quotas":sha(QUOTAS),"capacity":sha(CAP)},"capacity_validation_sha256":sha(CAPVAL),"spec_sha256":sha(SPEC),"core_sha256":sha(CORE),"coefficient_sha256":ah(coef),"counts":counts,"gates":gates,"records":records,"target_accessed":False,"source_groups_accessed":False,"row_roles_accessed":False,"member_sequences_accessed":False}
 need(json.loads(PROD.read_text())==expected,"full result reconstruction");report="\n".join(["# LRG005 target-blind calibration","",f"Status: **{status}**.","",f"Passes: null **{counts['NULL']}/64**, full **{counts['DISTRIBUTED_FULL']}/8**, reduced **{counts['DISTRIBUTED_REDUCED']}/8**, "+", ".join(f"{k.lower()} **{counts[k]}/8**" for k in KINDS[3:])+".","",f"Decision: **{decision}**.","","No manuscript role association or target score was opened. Calibration supplies no prefix, classifier, morpheme, word, POS, sound, meaning, plaintext, or translation.",""]);need(REPORT.read_text()==report,"report reconstruction")
 result={"status":"PASS_CLEAN_RECONSTRUCTION_OF_LRG005_CALIBRATION_STOP","checks":checks,"discrepancies":0,"production_sha256":sha(PROD),"report_sha256":sha(REPORT),"validator_sha256":sha(Path(__file__)),"counts":counts,"decision":decision,"target_accessed":False};OUT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf8",newline="\n");OUT_REPORT.write_text("\n".join(["# LRG005 calibration validation","",f"Status: **{result['status']}**.","",f"Independent code reconstructs all 136 worlds, the 8,192-assignment matrix, every statistic, gate, digest, decision, and exact report in **{checks}** checks with zero discrepancies.","",f"The frozen decision remains **{decision}**; no target or source member sequence was accessed.",""]),encoding="utf8",newline="\n");print(json.dumps(result,indent=2,sort_keys=True))
if __name__=="__main__":main()
