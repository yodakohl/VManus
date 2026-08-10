#!/usr/bin/env python3
"""Freeze the registered LRG006 target before execution."""
from __future__ import annotations
import hashlib,json,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];R=HERE/'results';OUT=HERE/'LRG006_TARGET_FREEZE.json';RESULTS=(R/'lrg006_a1_member_target.json',R/'lrg006_a1_member_target_report.md',R/'lrg006_a1_member_target_validation.json',R/'lrg006_a1_member_target_validation_report.md');FILES=(HERE/'LRG006_TARGET_METHOD.md',HERE/'LRG006_A1_MEMBER_CAPACITY_SPEC.md',HERE/'build_lrg006_a1_member_capacity.py',HERE/'validate_lrg006_a1_member_capacity.py',R/'source_sta_family_consensus_groups.tsv',R/'lrg001_label_register_capacity.tsv',R/'lrg006_a1_member_capacity.tsv',R/'lrg006_a1_member_quotas.tsv',R/'lrg006_a1_member_capacity.json',R/'lrg006_a1_member_capacity_validation.json',HERE/'LRG006_TARGET_BLIND_CALIBRATION_SPEC.md',HERE/'lrg006_core.py',HERE/'run_lrg006_target_blind_calibration.py',HERE/'validate_lrg006_target_blind_calibration.py',R/'lrg006_target_blind_calibration.json',R/'lrg006_target_blind_calibration_report.md',R/'lrg006_target_blind_calibration_validation.json',R/'lrg006_target_blind_calibration_validation_report.md',HERE/'run_lrg006_a1_member_target.py',HERE/'validate_lrg006_a1_member_target.py',HERE/'freeze_lrg006_target.py')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 if OUT.exists() or any(p.exists() for p in RESULTS):raise RuntimeError('freeze/result exists')
 if json.loads((R/'lrg006_target_blind_calibration.json').read_text())['status']!='PASS_TARGET_BLIND_LRG006_CALIBRATION':raise RuntimeError('calibration')
 if json.loads((R/'lrg006_target_blind_calibration_validation.json').read_text())['status']!='PASS_CLEAN_LRG006_CALIBRATION_RECONSTRUCTION':raise RuntimeError('calibration validation')
 commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip();result={'status':'FROZEN_LRG006_A1_MEMBER_TARGET','code_commit':commit,'frozen_files':{str(p.relative_to(ROOT)):sha(p) for p in FILES},'result_paths':[str(p.relative_to(ROOT)) for p in RESULTS],'all_results_absent':True,'claim_ceiling':'One aggregate two-sided A1-versus-other-A target and one clean reconstruction only; no row output sound word function meaning plaintext or translation.'};OUT.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf8',newline='\n');print(json.dumps(result,indent=2,sort_keys=True))
if __name__=='__main__':main()
