#!/usr/bin/env python3
"""Run the frozen one-shot LRG007 A/D edge-transfer target."""
from __future__ import annotations
import os
for v in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):os.environ[v]='32'
import csv,hashlib,json
from pathlib import Path
import numpy as np
from lrg007_core import ah,evaluate,load,null_orbit,weights
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];R=HERE/'results';FREEZE=HERE/'LRG007_TARGET_FREEZE.json';GROUPS=R/'source_sta_family_consensus_groups.tsv';PANEL=R/'lrg007_ad_edge_capacity.tsv';MARGINS=R/'lrg007_ad_edge_margins.tsv';CAP=R/'lrg007_ad_edge_capacity.json';CAL=R/'lrg007_target_blind_calibration.json';CALV=R/'lrg007_target_blind_calibration_validation.json';OUT=R/'lrg007_ad_edge_target.json';REPORT=R/'lrg007_ad_edge_target_report.md';VAL=R/'lrg007_ad_edge_target_validation.json';VALR=R/'lrg007_ad_edge_target_validation_report.md'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def tab(p):
 with p.open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def uid(x):return 'LRG007-U'+hashlib.sha256(('LRG007-AD|'+x).encode()).hexdigest()[:20]
def atomic(p,s):
 if p.exists():raise RuntimeError('output exists')
 q=p.with_suffix(p.suffix+'.tmp');q.write_text(s,encoding='utf8',newline='\n');os.link(q,p);q.unlink()
def main():
 outputs=(OUT,REPORT,VAL,VALR)
 if any(p.exists() for p in outputs):raise RuntimeError('target output exists')
 freeze=json.loads(FREEZE.read_text());expected=[str(p.relative_to(ROOT)) for p in outputs]
 if freeze['status']!='FROZEN_LRG007_AD_EDGE_TARGET' or freeze['result_paths']!=expected:raise RuntimeError('freeze contract')
 for rel,want in freeze['frozen_files'].items():
  if sha(ROOT/rel)!=want:raise RuntimeError(f'freeze drift {rel}')
 if json.loads(CAL.read_text())['status']!='PASS_TARGET_BLIND_LRG007_CALIBRATION' or json.loads(CALV.read_text())['status']!='PASS_CLEAN_LRG007_CALIBRATION_RECONSTRUCTION':raise RuntimeError('calibration')
 panel=tab(PANEL);groups=tab(GROUPS);lookup={uid(r['consensus_group_id']):r for r in groups}
 if len(panel)!=4911 or len(lookup)!=len(groups) or any(r['unit_id'] not in lookup for r in panel):raise RuntimeError('join')
 x=np.asarray([1 if lookup[p['unit_id']]['family_surface'][0]=='A' else -1 if lookup[p['unit_id']]['family_surface'][0]=='D' else 0 for p in panel],dtype=np.int8);capacity=json.loads(CAP.read_text())
 if ah(x)!=capacity['feature_matrix_sha256'] or (int(np.count_nonzero(x==1)),int(np.count_nonzero(x==-1)))!=(1118,1235):raise RuntimeError('feature drift')
 g=load(PANEL,MARGINS);w=weights(g);null=null_orbit(g,w);ev=evaluate(x,g,w,null);passed=bool(ev['joint_pass']);status='CONFIRMED_AD_OPPOSITION_AT_BOTH_PROSE_EDGES' if passed else 'FINAL_NONCONFIRMATION_LRG007_AD_EDGE_TRANSFER';decision='RETAIN_AD_AS_TRANSFERABLE_BOTH_EDGE_REGISTER' if passed else 'CLOSE_EXACT_AD_EDGE_TRANSFER'
 result={'status':status,'decision':decision,'claim_ceiling':'At most transfer of the structural A-over-D initial-family opposition to both corrected prose edges; FIRST LAST CORE are not semantic roles and no word function meaning plaintext or translation follows.','freeze_sha256':sha(FREEZE),'capacity_sha256':sha(CAP),'calibration_sha256':sha(CAL),'calibration_validation_sha256':sha(CALV),'counts':{'rows':len(x),'A':int(np.count_nonzero(x==1)),'D':int(np.count_nonzero(x==-1)),'other':int(np.count_nonzero(x==0)),'cells':len(g.cells),'folios':len(g.folios),'channels':2},'weight_sha256':ah(w),'null_sha256':ah(null),'feature_sha256':ah(x),'evaluation':ev,'individual_rows_emitted':False,'source_sequences_emitted':False,'position_family_counts_emitted':False};text=json.dumps(result,indent=2,sort_keys=True)+'\n';lines=['# LRG007 A/D edge-transfer target','',f'Status: **{status}**.','',f'Joint both-edge pass: **{passed}**.','','| channel | effect | FWER p | z | folios | A component | D component | B | P | odd | even | pass |','|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|',*[f"| {m['channel']} | {m['effect']:+.9f} | {m['fwer_p']:.9f} | {m['z']:+.4f} | {m['positive_folios']}/16 | {m['A_component']:+.9f} | {m['D_component']:+.9f} | {m['section_effects']['B']:+.9f} | {m['section_effects']['P']:+.9f} | {m['parity_effects']['ODD']:+.9f} | {m['parity_effects']['EVEN']:+.9f} | {m['passes']} |" for m in ev['metrics']],'',f'Decision: **{decision}**.','','No row, locus, page, source string, family sequence, semantic role, word, function, meaning, plaintext, or translation is emitted.',''];report='\n'.join(lines)
 if any(p.exists() for p in outputs):raise RuntimeError('concurrent output')
 atomic(OUT,text)
 try:atomic(REPORT,report)
 except Exception:OUT.unlink(missing_ok=True);raise
 print(text,end='')
if __name__=='__main__':main()
