#!/usr/bin/env python3
"""Freeze the registered LRG005 target before execution."""
from __future__ import annotations
import hashlib,json,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];R=HERE/'results';OUT=HERE/'LRG005_TARGET_FREEZE.json';RESULTS=(R/'lrg005_d1_extension_target.json',R/'lrg005_d1_extension_target_report.md',R/'lrg005_d1_extension_target_validation.json',R/'lrg005_d1_extension_target_validation_report.md')
FILES=(HERE/'LRG005_TARGET_METHOD.md',HERE/'LRG005_D1_EXTENSION_CAPACITY_SPEC.md',HERE/'build_lrg005_d1_extension_capacity.py',HERE/'validate_lrg005_d1_extension_capacity.py',R/'source_sta_family_consensus_groups.tsv',R/'lrg005_d1_extension_capacity.tsv',R/'lrg005_d1_extension_quotas.tsv',R/'lrg005_d1_extension_capacity.json',R/'lrg005_d1_extension_capacity_validation.json',HERE/'audit_lrg005_d1_specificity_capacity.py',HERE/'validate_lrg005_d1_specificity_capacity.py',R/'lrg005_d1_specificity_capacity.json',R/'lrg005_d1_specificity_capacity_report.md',R/'lrg005_d1_specificity_capacity_validation.json',R/'lrg005_d1_specificity_capacity_validation_report.md',HERE/'LRG005_TARGET_BLIND_CALIBRATION_SPEC.md',HERE/'lrg005_core.py',HERE/'run_lrg005_target_blind_calibration.py',HERE/'validate_lrg005_target_blind_calibration.py',R/'lrg005_target_blind_calibration.json',R/'lrg005_target_blind_calibration_report.md',R/'lrg005_target_blind_calibration_validation.json',R/'lrg005_target_blind_calibration_validation_report.md',HERE/'run_lrg005_d1_extension_target.py',HERE/'validate_lrg005_d1_extension_target.py',HERE/'freeze_lrg005_target.py')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 if OUT.exists() or any(p.exists() for p in RESULTS):raise RuntimeError('freeze/result exists')
 if json.loads((R/'lrg005_target_blind_calibration.json').read_text())['status']!='PASS_TARGET_BLIND_LRG005_CALIBRATION':raise RuntimeError('calibration')
 if json.loads((R/'lrg005_target_blind_calibration_validation.json').read_text())['status']!='PASS_CLEAN_LRG005_CALIBRATION_RECONSTRUCTION':raise RuntimeError('calibration validation')
 commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip();result={'status':'FROZEN_LRG005_D1_EXTENSION_TARGET','code_commit':commit,'frozen_files':{str(p.relative_to(ROOT)):sha(p) for p in FILES},'result_paths':[str(p.relative_to(ROOT)) for p in RESULTS],'all_results_absent':True,'claim_ceiling':'One aggregate two-channel target and one clean reconstruction only; no row output prefix function meaning plaintext or translation.'};OUT.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf8',newline='\n');print(json.dumps(result,indent=2,sort_keys=True))
if __name__=='__main__':main()
