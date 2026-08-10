#!/usr/bin/env python3
"""Freeze the one-shot LRG008 target with all outputs absent."""

from __future__ import annotations
import hashlib,json,subprocess
from pathlib import Path

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];R=HERE/"results";OUT=HERE/"LRG008_TARGET_FREEZE.json"
FILES=(
    HERE/"LRG008_TARGET_METHOD.md",HERE/"run_lrg008_diagram_role_target.py",HERE/"validate_lrg008_diagram_role_target.py",HERE/"freeze_lrg008_target.py",
    HERE/"lrg001_core.py",HERE/"lrg008_core.py",R/"source_sta_family_consensus_groups.tsv",R/"source_sta_family_consensus_validation.json",
    R/"lrg001_label_register_capacity.tsv",R/"lrg001_label_register_target_recovered.json",R/"lrg001_label_register_target_recovered_validation.json",
    HERE/"LRG008_DIAGRAM_ROLE_CAPACITY_SPEC.md",HERE/"build_lrg008_diagram_role_capacity.py",HERE/"validate_lrg008_diagram_role_capacity.py",
    R/"lrg008_diagram_role_capacity.tsv",R/"lrg008_diagram_role_capacity.json",R/"lrg008_diagram_role_capacity_validation.json",
    HERE/"LRG008_TARGET_BLIND_CALIBRATION_SPEC.md",HERE/"LRG008_TARGET_BLIND_CALIBRATION_V2_SPEC.md",HERE/"LRG008_TARGET_BLIND_CALIBRATION_V3_SPEC.md",HERE/"LRG008_CALIBRATION_V3_R1_SPEC.md",
    HERE/"run_lrg008_target_blind_calibration.py",HERE/"run_lrg008_target_blind_calibration_v2.py",HERE/"build_lrg008_target_blind_calibration_v3.py",HERE/"build_lrg008_target_blind_calibration_v3_r1.py",
    HERE/"validate_lrg008_target_blind_calibration.py",HERE/"validate_lrg008_target_blind_calibration_v2.py",HERE/"validate_lrg008_target_blind_calibration_v3_r1.py",
    R/"lrg008_target_blind_calibration.json",R/"lrg008_target_blind_calibration_validation.json",R/"lrg008_target_blind_calibration_v2.json",R/"lrg008_target_blind_calibration_v2_validation.json",
    R/"lrg008_target_blind_calibration_v3.json",R/"lrg008_target_blind_calibration_v3_r1.json",R/"lrg008_target_blind_calibration_v3_r1_validation.json",
)
RESULTS=(R/"lrg008_diagram_role_target.json",R/"lrg008_diagram_role_target_report.md",R/"lrg008_diagram_role_target_validation.json",R/"lrg008_diagram_role_target_validation_report.md")

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    if OUT.exists():raise RuntimeError("freeze exists")
    if any(path.exists() for path in RESULTS):raise RuntimeError("result path exists")
    if subprocess.check_output(["git","status","--porcelain"],cwd=ROOT,text=True).strip():raise RuntimeError("worktree must be clean")
    calibration=json.loads((R/"lrg008_target_blind_calibration_v3_r1.json").read_text());validation=json.loads((R/"lrg008_target_blind_calibration_v3_r1_validation.json").read_text())
    if calibration["status"]!="PASS_LRG008_TARGET_BLIND_CALIBRATION_V3_R1" or validation["status"]!="PASS_EXACT_LRG008_V3_R1_POLARITY_CORRECTION":raise RuntimeError("calibration not validated")
    result={"status":"FROZEN_LRG008_SINGLE_TARGET","code_commit":subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip(),"frozen_files":{str(path.relative_to(ROOT)):sha(path) for path in FILES},"result_paths":[str(path.relative_to(ROOT)) for path in RESULTS],"result_paths_absent":True,"authorized_invocations":{"target":1,"production_free_validation":1},"claim_ceiling":"A pass establishes only a held-profile distinction between manual L and pooled C/R diagram text on the fixed panel; no identifier, name, noun, owner, object, word, sound, language, meaning, plaintext, or translation."}
    OUT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8",newline="\n")
    print(json.dumps({"status":result["status"],"code_commit":result["code_commit"],"files":len(FILES),"outputs_absent":True},sort_keys=True))

if __name__=="__main__":main()
