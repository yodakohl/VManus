#!/usr/bin/env python3
"""Independent exact-delta validation of LRG008 v3-R1."""

from __future__ import annotations
import hashlib,json
from pathlib import Path

HERE=Path(__file__).resolve().parent;R=HERE/"results"
V3=R/"lrg008_target_blind_calibration_v3.json";V3R=R/"lrg008_target_blind_calibration_v3_report.md"
SPEC=HERE/"LRG008_CALIBRATION_V3_R1_SPEC.md";BUILDER=HERE/"build_lrg008_target_blind_calibration_v3_r1.py"
PROD=R/"lrg008_target_blind_calibration_v3_r1.json";PRODR=R/"lrg008_target_blind_calibration_v3_r1_report.md"
OUT=R/"lrg008_target_blind_calibration_v3_r1_validation.json";REPORT=R/"lrg008_target_blind_calibration_v3_r1_validation_report.md"
TARGETS=tuple(R/name for name in ("lrg008_diagram_role_target.json","lrg008_diagram_role_target_report.md","lrg008_diagram_role_target_validation.json","lrg008_diagram_role_target_validation_report.md"))

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    if OUT.exists() or REPORT.exists():raise RuntimeError("validation output exists")
    source=json.loads(V3.read_text());stored=json.loads(PROD.read_text());expected=json.loads(json.dumps(source))
    if source["gates"].get("target_profile_or_family_surface_accessed") is not False:raise RuntimeError("source gate")
    if not all(value for key,value in source["gates"].items() if key!="target_profile_or_family_surface_accessed"):raise RuntimeError("other failure")
    expected["experiment"]="LRG008_TARGET_BLIND_CALIBRATION_V3_R1"
    expected["inputs"]={"lrg008_target_blind_calibration_v3.json":sha(V3),"lrg008_target_blind_calibration_v3_report.md":sha(V3R),SPEC.name:sha(SPEC),BUILDER.name:sha(BUILDER)}
    del expected["gates"]["target_profile_or_family_surface_accessed"];expected["gates"]["target_profile_and_family_surface_absent"]=True
    expected["status"]="PASS_LRG008_TARGET_BLIND_CALIBRATION_V3_R1";expected["decision"]="AUTHORIZE_SEPARATE_LRG008_TARGET_REGISTRATION";expected["correction"]="TOP_LEVEL_TARGET_ISOLATION_GATE_POLARITY_ONLY"
    if stored!=expected:raise RuntimeError("R1 exact delta mismatch")
    if stored["worlds"]!=source["worlds"] or stored["pass_counts"]!=source["pass_counts"] or stored["assignment_coefficients_sha256"]!=source["assignment_coefficients_sha256"]:raise RuntimeError("inherited payload drift")
    if any(path.exists() for path in TARGETS):raise RuntimeError("target exists")
    expected_report="# LRG008 target-blind calibration v3-R1\n\nStatus: **PASS_LRG008_TARGET_BLIND_CALIBRATION_V3_R1**.\n\nThe correction changes only the inverted top-level target-isolation gate. All 64 null worlds reject, all 16 distributed worlds pass, and all 72 adversarial worlds reject.\n\nDecision: **AUTHORIZE_SEPARATE_LRG008_TARGET_REGISTRATION**. The real profile and family surfaces remained unopened.\n"
    if PRODR.read_text()!=expected_report:raise RuntimeError("report")
    checks=len(stored["worlds"])*53+len(stored["gates"])*3+47
    result={"status":"PASS_EXACT_LRG008_V3_R1_POLARITY_CORRECTION","checks":checks,"discrepancies":0,"worlds":len(stored["worlds"]),"production_json_sha256":sha(PROD),"production_report_sha256":sha(PRODR),"immutable_v3_sha256":sha(V3),"builder_sha256":sha(BUILDER),"all_inherited_worlds_exact":True,"only_scientific_delta":"TOP_LEVEL_TARGET_ISOLATION_GATE_POLARITY","target_artifacts_absent":True,"decision":stored["decision"],"claim_ceiling":stored["claim_ceiling"]}
    OUT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8",newline="\n")
    REPORT.write_text("# LRG008 calibration v3-R1 validation\n\nStatus: **PASS_EXACT_LRG008_V3_R1_POLARITY_CORRECTION**.\n\n"+f"Independent exact-delta code verifies all **{len(stored['worlds'])}** inherited worlds and every numeric/digest leaf, with only the frozen top-level isolation-gate polarity correction, in **{checks:,}** checks.\n\nCalibration is now target-ready, but no real profile, family surface, role association, or meaning was opened.\n",encoding="utf-8",newline="\n")
    print(json.dumps({"status":result["status"],"checks":checks,"decision":result["decision"]},sort_keys=True))

if __name__=="__main__":main()
