#!/usr/bin/env python3
"""Independent reconstruction of the frozen LRG006 A1-member target."""
from __future__ import annotations
import os
for v in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):os.environ[v]='32'
import csv,hashlib,json
from pathlib import Path
import numpy as np
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];R=HERE/'results';FREEZE=HERE/'LRG006_TARGET_FREEZE.json';G=R/'source_sta_family_consensus_groups.tsv';P=R/'lrg006_a1_member_capacity.tsv';Q=R/'lrg006_a1_member_quotas.tsv';CAP=R/'lrg006_a1_member_capacity.json';CAL=R/'lrg006_target_blind_calibration.json';CALV=R/'lrg006_target_blind_calibration_validation.json';PROD=R/'lrg006_a1_member_target.json';REPORT=R/'lrg006_a1_member_target_report.md';OUT=R/'lrg006_a1_member_target_validation.json';OUTR=R/'lrg006_a1_member_target_validation_report.md';F=('zl_sta_codes','it_sta_codes','rf_sta_codes');A=8192;SEED=60062026;checks=0
def need(x,m):
 global checks;checks+=1
 if not x:raise RuntimeError(m)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ah(a):return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()
def tab(p):
 with p.open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def uid(x):return 'LRG006-U'+hashlib.sha256(('LRG006-A1|'+x).encode()).hexdigest()[:20]
def main():
 need(PROD.is_file() and REPORT.is_file(),'target absent');freeze=json.loads(FREEZE.read_text());need(freeze['status']=='FROZEN_LRG006_A1_MEMBER_TARGET','freeze');need(freeze['result_paths']==[str(p.relative_to(ROOT)) for p in (PROD,REPORT,OUT,OUTR)],'paths')
 for rel,want in freeze['frozen_files'].items():need(sha(ROOT/rel)==want,'freeze drift')
 groups=tab(G);panel=tab(P);quotas=tab(Q);lookup={uid(r['consensus_group_id']):r for r in groups};need(len(panel)==677 and len(quotas)==69 and len(lookup)==len(groups) and all(r['unit_id'] in lookup for r in panel),'join')
 x=[];y=[]
 for p in panel:
  r=lookup[p['unit_id']];parts=[r[f].split() for f in F];need(all(z and z[0][0]=='A' for z in parts),'A universe');x.append(all(z[0]=='A1' for z in parts));y.append(1 if r['kind']=='L' else 0 if r['kind']=='P' and r['grammar_scope']=='CONFIRMED_PROSE' else -1)
 x=np.asarray(x,dtype=np.int8);y=np.asarray(y,dtype=np.int8);need(-1 not in y and int(x.sum())==543 and int(y.sum())==163,'vectors');need(ah(x)==json.loads(CAP.read_text())['feature_vector_sha256'],'feature hash')
 cell=np.asarray([r['cell_id'] for r in panel]);folio=np.asarray([r['physical_folio'] for r in panel]);section=np.asarray([r['section'] for r in panel]);quota={r['cell_id']:int(r['label_rows']) for r in quotas};cells=tuple(sorted(quota));folios=tuple(sorted(set(folio),key=lambda z:int(z[1:])));need(len(folios)==13,'folios')
 for c in cells:need(int(y[cell==c].sum())==quota[c],'quota')
 coefficient=np.zeros((A,len(y)));rng=np.random.default_rng(SEED)
 for c in cells:
  idx=np.flatnonzero(cell==c);f=str(folio[idx[0]]);nc=len(set(cell[folio==f]));h=quota[c];lo=len(idx)-h;coefficient[:,idx]=-1/(len(folios)*nc*lo);chosen=idx[np.argpartition(rng.random((A,len(idx))),h-1,axis=1)[:,:h]];coefficient[np.arange(A)[:,None],chosen]=1/(len(folios)*nc*h)
 null=coefficient@x;fe=[]
 for f in folios:
  values=[]
  for c in sorted(set(cell[folio==f])):
   idx=np.flatnonzero(cell==c);values.append(float(x[idx[y[idx]==1]].mean()-x[idx[y[idx]==0]].mean()))
  fe.append(float(np.mean(values)))
 fe=np.asarray(fe);t=float(fe.mean());mu=float(null.mean());sd=float(null.std(ddof=0));z=(t-mu)/sd if sd>0 else 0.;pval=(1+int(np.count_nonzero(np.abs(null)>=abs(t))))/(A+1);sign=1 if t>=0 else -1;nums=np.asarray([int(f[1:]) for f in folios]);sf=np.asarray([str(section[np.flatnonzero(folio==f)[0]]) for f in folios]);sec={s:sign*float(fe[sf==s].mean()) for s in ('B','P')};par={'ODD':sign*float(fe[nums%2==1].mean()),'EVEN':sign*float(fe[nums%2==0].mean())};sb=min(sec.values())/max(sec.values()) if max(sec.values())>0 else float('-inf');pb=min(par.values())/max(par.values()) if max(par.values())>0 else float('-inf');dele=[sign*float(np.delete(fe,k).mean()) for k in range(13)];con=float(np.max(np.abs(fe))/np.abs(fe).sum()) if np.abs(fe).sum() else 1.;gates={'p_at_most_001':pval<=.01,'absolute_z_at_least_3':abs(z)>=3,'absolute_effect_at_least_008':abs(t)>=.08,'directional_support_at_least_10':int(np.count_nonzero(sign*fe>0))>=10,'both_sections_signed_at_least_020':min(sec.values())>=.20,'section_balance_at_least_035':sb>=.35,'both_parities_signed_at_least_004':min(par.values())>=.04,'parity_balance_at_least_035':pb>=.35,'all_deletions_signed_at_least_004':min(dele)>=.04,'concentration_at_most_030':con<=.30};ev={'effect':t,'direction':'A1_POSITIVE' if sign>0 else 'A1_NEGATIVE','null_mean':mu,'null_sd':sd,'z':z,'p':pval,'positive_direction_folios':int(np.count_nonzero(sign*fe>0)),'folio_effects':{f:float(v) for f,v in zip(folios,fe,strict=True)},'signed_section_effects':sec,'section_balance_ratio':sb,'signed_parity_effects':par,'parity_balance_ratio':pb,'minimum_signed_deletion':min(dele),'maximum_absolute_folio_concentration':con,'null_sha256':ah(null),'feature_sha256':ah(x),'label_sha256':ah(y),'gates':gates,'passes':all(gates.values())};passed=ev['passes']
 if passed and ev['direction']=='A1_POSITIVE':status='CONFIRMED_A1_SPECIFIC_LABEL_REGISTER_SUBSTATE';decision='RETAIN_A1_AS_LOCALIZED_A_FAMILY_REGISTER_STATE'
 elif passed:status='CONFIRMED_OTHER_A_LABEL_REGISTER_SUBSTATE';decision='RETAIN_OTHER_A_AS_LOCALIZED_A_FAMILY_REGISTER_STATE'
 else:status='FINAL_NONCONFIRMATION_LRG006_A1_MEMBER_SPECIFICITY';decision='RETAIN_BROAD_A_FAMILY_REGISTER_ONLY'
 expected={'status':status,'decision':decision,'claim_ceiling':'At most an exact A1-versus-other-A member substate association inside the conditioned structural A family; no sound spelling word POS function language cipher meaning plaintext or translation.','freeze_sha256':sha(FREEZE),'capacity_sha256':sha(CAP),'calibration_sha256':sha(CAL),'calibration_validation_sha256':sha(CALV),'counts':{'rows':len(y),'labels':int(y.sum()),'prose':int(len(y)-y.sum()),'cells':len(cells),'folios':len(folios),'A1':int(x.sum()),'other_A':int(len(x)-x.sum())},'coefficient_sha256':ah(coefficient),'feature_sha256':ah(x),'label_sha256':ah(y),'evaluation':ev,'individual_rows_emitted':False,'member_triplets_emitted':False,'source_surfaces_emitted':False};need(json.loads(PROD.read_text())==expected,'full result')
 lines=['# LRG006 A1-member target','',f'Status: **{status}**.','',f"Direction: **{ev['direction']}**; label-minus-prose A1 effect **{ev['effect']:+.9f}**, two-sided p **{ev['p']:.9f}**, z **{ev['z']:+.4f}**, directional folios **{ev['positive_direction_folios']}/13**.",'',f"Signed robustness: B **{sec['B']:+.9f}**, P **{sec['P']:+.9f}**, odd **{par['ODD']:+.9f}**, even **{par['EVEN']:+.9f}**, section balance **{ev['section_balance_ratio']:.4f}**, parity balance **{ev['parity_balance_ratio']:.4f}**, minimum deletion **{ev['minimum_signed_deletion']:+.9f}**, concentration **{ev['maximum_absolute_folio_concentration']:.4f}**.",'',f"All gates pass: **{passed}**. Decision: **{decision}**.",'','No row, locus, page, surface, member triplet, sound, word, function, meaning, plaintext, or translation is emitted.',''];need(REPORT.read_text()=='\n'.join(lines),'report')
 result={'status':'PASS_CLEAN_LRG006_TARGET_RECONSTRUCTION','checks':checks,'discrepancies':0,'production_sha256':sha(PROD),'report_sha256':sha(REPORT),'target_status':status,'decision':decision};OUT.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf8',newline='\n');OUTR.write_text('\n'.join(['# LRG006 target validation','',f"Status: **{result['status']}**.",'',f"Independent code reconstructs the real A1 and role vectors, all quotas, the statistic, null, robustness gates, decision, and exact report in **{checks}** checks with zero discrepancies.",'','The result remains structural only; no member function or meaning follows.','']),encoding='utf8',newline='\n');print(json.dumps(result,indent=2,sort_keys=True))
if __name__=='__main__':main()
