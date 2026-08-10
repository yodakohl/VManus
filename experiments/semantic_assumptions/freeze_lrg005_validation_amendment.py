#!/usr/bin/env python3
"""Freeze the validator-only LRG005 arithmetic-order amendment."""
from __future__ import annotations
import hashlib,json,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];R=HERE/'results';OUT=HERE/'LRG005_TARGET_VALIDATION_AMENDMENT.json';ORIGINAL=HERE/'validate_lrg005_d1_extension_target.py';CORRECTED=HERE/'validate_lrg005_d1_extension_target_v2.py';TARGET=R/'lrg005_d1_extension_target.json';REPORT=R/'lrg005_d1_extension_target_report.md';VALIDATION=R/'lrg005_d1_extension_target_validation.json';VALIDATION_REPORT=R/'lrg005_d1_extension_target_validation_report.md'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 if OUT.exists() or VALIDATION.exists() or VALIDATION_REPORT.exists():raise RuntimeError('amendment/output exists')
 result={'status':'FROZEN_LRG005_VALIDATOR_ARITHMETIC_ORDER_CORRECTION','code_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'hashes':{'original_validator':sha(ORIGINAL),'target':sha(TARGET),'report':sha(REPORT),'corrected_validator':sha(CORRECTED)},'correction':'Use the production vectorized two-column folio-effect mean before selecting each channel; change no other arithmetic, gate, result, or report.','production_rerun_authorized':False,'validation_outputs_absent':True};OUT.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf8',newline='\n');print(json.dumps(result,indent=2,sort_keys=True))
if __name__=='__main__':main()
