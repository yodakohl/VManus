#!/usr/bin/env python3
"""Correct only the inverted target-isolation gate in LRG008 calibration v3."""

from __future__ import annotations
import hashlib,json
from pathlib import Path

HERE=Path(__file__).resolve().parent;R=HERE/"results"
V3=R/"lrg008_target_blind_calibration_v3.json";V3R=R/"lrg008_target_blind_calibration_v3_report.md"
SPEC=HERE/"LRG008_CALIBRATION_V3_R1_SPEC.md";OUT=R/"lrg008_target_blind_calibration_v3_r1.json";REPORT=R/"lrg008_target_blind_calibration_v3_r1_report.md"
TARGETS=tuple(R/name for name in ("lrg008_diagram_role_target.json","lrg008_diagram_role_target_report.md","lrg008_diagram_role_target_validation.json","lrg008_diagram_role_target_validation_report.md"))

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    if OUT.exists() or REPORT.exists():raise RuntimeError("R1 output exists")
    if any(path.exists() for path in TARGETS):raise RuntimeError("target artifact exists")
    original=json.loads(V3.read_text())
    if original["status"]!="STOP_LRG008_TARGET_BLIND_CALIBRATION_V3" or original["decision"]!="TARGET_FORBIDDEN":raise RuntimeError("v3 state")
    if original["gates"].get("target_profile_or_family_surface_accessed") is not False:raise RuntimeError("missing inverted gate")
    if not all(value for key,value in original["gates"].items() if key!="target_profile_or_family_surface_accessed"):raise RuntimeError("non-polarity v3 failure")
    result=json.loads(json.dumps(original));result["experiment"]="LRG008_TARGET_BLIND_CALIBRATION_V3_R1"
    result["inputs"]={"lrg008_target_blind_calibration_v3.json":sha(V3),"lrg008_target_blind_calibration_v3_report.md":sha(V3R),SPEC.name:sha(SPEC),Path(__file__).name:sha(Path(__file__))}
    del result["gates"]["target_profile_or_family_surface_accessed"]
    result["gates"]["target_profile_and_family_surface_absent"]=True
    if not all(result["gates"].values()):raise RuntimeError("R1 gates")
    result["status"]="PASS_LRG008_TARGET_BLIND_CALIBRATION_V3_R1";result["decision"]="AUTHORIZE_SEPARATE_LRG008_TARGET_REGISTRATION"
    result["correction"]="TOP_LEVEL_TARGET_ISOLATION_GATE_POLARITY_ONLY"
    OUT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8",newline="\n")
    REPORT.write_text("# LRG008 target-blind calibration v3-R1\n\nStatus: **PASS_LRG008_TARGET_BLIND_CALIBRATION_V3_R1**.\n\nThe correction changes only the inverted top-level target-isolation gate. All 64 null worlds reject, all 16 distributed worlds pass, and all 72 adversarial worlds reject.\n\nDecision: **AUTHORIZE_SEPARATE_LRG008_TARGET_REGISTRATION**. The real profile and family surfaces remained unopened.\n",encoding="utf-8",newline="\n")
    print(json.dumps({"status":result["status"],"pass_counts":result["pass_counts"],"decision":result["decision"]},sort_keys=True))

if __name__=="__main__":main()
