#!/usr/bin/env python3
"""Run target-free LRG007 calibration."""
from __future__ import annotations
import os
for v in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):os.environ[v]='32'
import hashlib,json
from pathlib import Path
import numpy as np
from lrg007_core import ah,evaluate,load,null_orbit,synthetic,weights
HERE=Path(__file__).resolve().parent;R=HERE/'results';P=R/'lrg007_ad_edge_capacity.tsv';M=R/'lrg007_ad_edge_margins.tsv';CAP=R/'lrg007_ad_edge_capacity.json';CAPV=R/'lrg007_ad_edge_capacity_validation.json';SPEC=HERE/'LRG007_TARGET_BLIND_CALIBRATION_SPEC.md';CORE=HERE/'lrg007_core.py';OUT=R/'lrg007_target_blind_calibration.json';REPORT=R/'lrg007_target_blind_calibration_report.md';KINDS=('NULL','BOTH_FULL','BOTH_REDUCED','FIRST_ONLY','LAST_ONLY','ONE_FOLIO','ONE_SECTION','ONE_PARITY','FOLIO_RANDOM','OPPOSITE_EDGES','REVERSED')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 if OUT.exists() or REPORT.exists():raise RuntimeError('output exists')
 g=load(P,M);w=weights(g);null=null_orbit(g,w);records=[]
 for kind in KINDS:
  for i in range(64 if kind=='NULL' else 8):
   x=synthetic(g,kind,i,KINDS);records.append({'kind':kind,'world':i,'evaluation':evaluate(x,g,w,null)})
 counts={k:sum(r['evaluation']['joint_pass'] for r in records if r['kind']==k) for k in KINDS};gates={'zero_null':counts['NULL']==0,'all_full':counts['BOTH_FULL']==8,'all_reduced':counts['BOTH_REDUCED']==8,'zero_controls':all(counts[k]==0 for k in KINDS[3:])};passed=all(gates.values());status='PASS_TARGET_BLIND_LRG007_CALIBRATION' if passed else 'STOP_TARGET_BLIND_LRG007_CALIBRATION';decision='GO_CLEAN_VALIDATION' if passed else 'DO_NOT_OPEN_TARGET';result={'status':status,'decision':decision,'claim_ceiling':'Calibration only; no real family-position association opening closing word function meaning plaintext or translation.','inputs':{'panel':sha(P),'margins':sha(M),'capacity':sha(CAP),'capacity_validation':sha(CAPV)},'spec_sha256':sha(SPEC),'core_sha256':sha(CORE),'weight_sha256':ah(w),'null_sha256':ah(null),'counts':counts,'gates':gates,'records':records,'real_family_positions_accessed':False};text=json.dumps(result,indent=2,sort_keys=True)+'\n';OUT.write_text(text,encoding='utf8',newline='\n');report='\n'.join(['# LRG007 target-blind calibration','',f'Status: **{status}**.','',f"Passes: null **{counts['NULL']}/64**, full/reduced **{counts['BOTH_FULL']}/8 / {counts['BOTH_REDUCED']}/8**, controls "+', '.join(f"{k.lower()} **{counts[k]}/8**" for k in KINDS[3:])+'.','',f'Decision: **{decision}**.','','No real family-position association was accessed. No opening, closing, word, function, meaning, plaintext, or translation follows.','']);REPORT.write_text(report,encoding='utf8',newline='\n');print(text,end='')
if __name__=='__main__':main()
