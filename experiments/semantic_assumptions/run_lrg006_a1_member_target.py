#!/usr/bin/env python3
"""Run the frozen one-shot LRG006 A1-member target."""
from __future__ import annotations
import os
for v in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):os.environ[v]='32'
import csv,hashlib,json
from pathlib import Path
import numpy as np
from lrg006_core import ah,coef,evaluate,load
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];R=HERE/'results';FREEZE=HERE/'LRG006_TARGET_FREEZE.json';GROUPS=R/'source_sta_family_consensus_groups.tsv';PANEL=R/'lrg006_a1_member_capacity.tsv';QUOTAS=R/'lrg006_a1_member_quotas.tsv';CAP=R/'lrg006_a1_member_capacity.json';CAL=R/'lrg006_target_blind_calibration.json';CALV=R/'lrg006_target_blind_calibration_validation.json';OUT=R/'lrg006_a1_member_target.json';REPORT=R/'lrg006_a1_member_target_report.md';VAL=R/'lrg006_a1_member_target_validation.json';VALR=R/'lrg006_a1_member_target_validation_report.md';F=('zl_sta_codes','it_sta_codes','rf_sta_codes')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def tab(p):
 with p.open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def uid(x):return 'LRG006-U'+hashlib.sha256(('LRG006-A1|'+x).encode()).hexdigest()[:20]
def atomic(p,s):
 if p.exists():raise RuntimeError('output exists')
 q=p.with_suffix(p.suffix+'.tmp');q.write_text(s,encoding='utf8',newline='\n');os.link(q,p);q.unlink()
def main():
 outputs=(OUT,REPORT,VAL,VALR)
 if any(p.exists() for p in outputs):raise RuntimeError('target output exists')
 freeze=json.loads(FREEZE.read_text());expected=[str(p.relative_to(ROOT)) for p in outputs]
 if freeze['status']!='FROZEN_LRG006_A1_MEMBER_TARGET' or freeze['result_paths']!=expected:raise RuntimeError('freeze contract')
 for rel,want in freeze['frozen_files'].items():
  if sha(ROOT/rel)!=want:raise RuntimeError(f'freeze drift {rel}')
 if json.loads(CAL.read_text())['status']!='PASS_TARGET_BLIND_LRG006_CALIBRATION' or json.loads(CALV.read_text())['status']!='PASS_CLEAN_LRG006_CALIBRATION_RECONSTRUCTION':raise RuntimeError('calibration')
 groups=tab(GROUPS);panel=tab(PANEL);lookup={uid(r['consensus_group_id']):r for r in groups}
 if len(panel)!=677 or len(lookup)!=len(groups) or any(r['unit_id'] not in lookup for r in panel):raise RuntimeError('join')
 x=[];y=[]
 for p in panel:
  r=lookup[p['unit_id']];parts=[r[f].split() for f in F]
  if any(not z or z[0][0]!='A' for z in parts):raise RuntimeError('A universe')
  x.append(all(z[0]=='A1' for z in parts))
  if r['kind']=='L':y.append(1)
  elif r['kind']=='P' and r['grammar_scope']=='CONFIRMED_PROSE':y.append(0)
  else:raise RuntimeError('role')
 x=np.asarray(x,dtype=np.int8);y=np.asarray(y,dtype=np.int8);capacity=json.loads(CAP.read_text())
 if ah(x)!=capacity['feature_vector_sha256'] or int(x.sum())!=543 or int(y.sum())!=163:raise RuntimeError('target vector drift')
 g=load(PANEL,QUOTAS)
 for c,h in g.quota.items():
  if int(y[g.cell==c].sum())!=h:raise RuntimeError('quota drift')
 coefficient=coef(g);ev=evaluate(x,y,g,coefficient);passed=bool(ev['passes'])
 if passed and ev['direction']=='A1_POSITIVE':status='CONFIRMED_A1_SPECIFIC_LABEL_REGISTER_SUBSTATE';decision='RETAIN_A1_AS_LOCALIZED_A_FAMILY_REGISTER_STATE'
 elif passed:status='CONFIRMED_OTHER_A_LABEL_REGISTER_SUBSTATE';decision='RETAIN_OTHER_A_AS_LOCALIZED_A_FAMILY_REGISTER_STATE'
 else:status='FINAL_NONCONFIRMATION_LRG006_A1_MEMBER_SPECIFICITY';decision='RETAIN_BROAD_A_FAMILY_REGISTER_ONLY'
 result={'status':status,'decision':decision,'claim_ceiling':'At most an exact A1-versus-other-A member substate association inside the conditioned structural A family; no sound spelling word POS function language cipher meaning plaintext or translation.','freeze_sha256':sha(FREEZE),'capacity_sha256':sha(CAP),'calibration_sha256':sha(CAL),'calibration_validation_sha256':sha(CALV),'counts':{'rows':len(y),'labels':int(y.sum()),'prose':int(len(y)-y.sum()),'cells':len(g.cells),'folios':len(g.folios),'A1':int(x.sum()),'other_A':int(len(x)-x.sum())},'coefficient_sha256':ah(coefficient),'feature_sha256':ah(x),'label_sha256':ah(y),'evaluation':ev,'individual_rows_emitted':False,'member_triplets_emitted':False,'source_surfaces_emitted':False}
 text=json.dumps(result,indent=2,sort_keys=True)+'\n';sec=ev['signed_section_effects'];par=ev['signed_parity_effects'];lines=['# LRG006 A1-member target','',f'Status: **{status}**.','',f"Direction: **{ev['direction']}**; label-minus-prose A1 effect **{ev['effect']:+.9f}**, two-sided p **{ev['p']:.9f}**, z **{ev['z']:+.4f}**, directional folios **{ev['positive_direction_folios']}/13**.",'',f"Signed robustness: B **{sec['B']:+.9f}**, P **{sec['P']:+.9f}**, odd **{par['ODD']:+.9f}**, even **{par['EVEN']:+.9f}**, section balance **{ev['section_balance_ratio']:.4f}**, parity balance **{ev['parity_balance_ratio']:.4f}**, minimum deletion **{ev['minimum_signed_deletion']:+.9f}**, concentration **{ev['maximum_absolute_folio_concentration']:.4f}**.",'',f"All gates pass: **{passed}**. Decision: **{decision}**.",'','No row, locus, page, surface, member triplet, sound, word, function, meaning, plaintext, or translation is emitted.',''];report='\n'.join(lines)
 if any(p.exists() for p in outputs):raise RuntimeError('concurrent output')
 atomic(OUT,text)
 try:atomic(REPORT,report)
 except Exception:OUT.unlink(missing_ok=True);raise
 print(text,end='')
if __name__=='__main__':main()
