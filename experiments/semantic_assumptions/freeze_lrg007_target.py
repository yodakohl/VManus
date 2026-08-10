#!/usr/bin/env python3
"""Freeze the registered LRG007 target before execution."""
from __future__ import annotations
import hashlib,json,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];R=HERE/'results';OUT=HERE/'LRG007_TARGET_FREEZE_V2.json';RESULTS=(R/'lrg007_ad_edge_target.json',R/'lrg007_ad_edge_target_report.md',R/'lrg007_ad_edge_target_validation.json',R/'lrg007_ad_edge_target_validation_report.md');FILES=(HERE/'LRG007_TARGET_METHOD.md',HERE/'LRG007_AD_EDGE_TRANSFER_CAPACITY_SPEC.md',HERE/'build_lrg007_ad_edge_capacity.py',HERE/'validate_lrg007_ad_edge_capacity.py',R/'source_sta_family_consensus_groups.tsv',R/'lrg007_ad_edge_capacity.tsv',R/'lrg007_ad_edge_margins.tsv',R/'lrg007_ad_edge_capacity.json',R/'lrg007_ad_edge_capacity_validation.json',HERE/'LRG007_TARGET_BLIND_CALIBRATION_SPEC.md',HERE/'lrg007_core.py',HERE/'run_lrg007_target_blind_calibration.py',HERE/'validate_lrg007_target_blind_calibration.py',R/'lrg007_target_blind_calibration.json',R/'lrg007_target_blind_calibration_validation.json',HERE/'run_lrg007_ad_edge_target.py',HERE/'validate_lrg007_ad_edge_target.py',HERE/'freeze_lrg007_target.py')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 if OUT.exists() or any(p.exists() for p in RESULTS):raise RuntimeError('freeze/result exists')
 if json.loads((R/'lrg007_target_blind_calibration.json').read_text())['status']!='PASS_TARGET_BLIND_LRG007_CALIBRATION':raise RuntimeError('calibration')
 if json.loads((R/'lrg007_target_blind_calibration_validation.json').read_text())['status']!='PASS_CLEAN_LRG007_CALIBRATION_RECONSTRUCTION':raise RuntimeError('validation')
 commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip();result={'status':'FROZEN_LRG007_AD_EDGE_TARGET','code_commit':commit,'frozen_files':{str(p.relative_to(ROOT)):sha(p) for p in FILES},'result_paths':[str(p.relative_to(ROOT)) for p in RESULTS],'all_results_absent':True,'claim_ceiling':'One aggregate both-edge A-over-D target and one production-free reconstruction only; no row output semantic role meaning plaintext or translation.'};OUT.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf8',newline='\n');print(json.dumps(result,indent=2,sort_keys=True))
if __name__=='__main__':main()
