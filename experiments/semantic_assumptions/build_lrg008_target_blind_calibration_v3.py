#!/usr/bin/env python3
"""Apply the single frozen parity-balance gate to validated LRG008 v2 worlds."""

from __future__ import annotations

import hashlib,json
from collections import Counter
from pathlib import Path


HERE=Path(__file__).resolve().parent;R=HERE/"results"
V2=R/"lrg008_target_blind_calibration_v2.json";V2V=R/"lrg008_target_blind_calibration_v2_validation.json"
SPEC=HERE/"LRG008_TARGET_BLIND_CALIBRATION_V3_SPEC.md";OUT=R/"lrg008_target_blind_calibration_v3.json";REPORT=R/"lrg008_target_blind_calibration_v3_report.md"
TARGETS=tuple(R/name for name in ("lrg008_diagram_role_target.json","lrg008_diagram_role_target_report.md","lrg008_diagram_role_target_validation.json","lrg008_diagram_role_target_validation_report.md"))
EXPECTED={V2:"8a440eef17e4d858c6186e77ee1899b5d93dcf87218bc0dbb6c9a3a3190b7050",V2V:"6b0f08eda86cd9803798339a825f3a68e093d37493469da50c3056045dcab0e7"}
ORDER=("NULL","DISTRIBUTED_FULL","DISTRIBUTED_REDUCED","ONE_FOLIO","ONE_ROLE","ONE_SECTION","ONE_PARITY","ONE_PAGE","FOLIO_RANDOM_SIGN","PAGE_ONLY","LENGTH_ONLY","REVERSED")


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    if OUT.exists() or REPORT.exists():raise RuntimeError("v3 output exists")
    if any(path.exists() for path in TARGETS):raise RuntimeError("target artifact exists")
    for path,expected in EXPECTED.items():
        if sha(path)!=expected:raise RuntimeError(f"input hash {path.name}")
    v2=json.loads(V2.read_text());validation=json.loads(V2V.read_text())
    if v2["status"]!="STOP_LRG008_TARGET_BLIND_CALIBRATION_V2" or validation["status"]!="PASS_CLEAN_RECONSTRUCTION_OF_LRG008_V2_STOP":raise RuntimeError("v2 binding")
    records=[]
    for original in v2["worlds"]:
        record=json.loads(json.dumps(original));evaluation=record["evaluation"]
        values=list(evaluation["parity_effects"].values());high=max(values);low=min(values)
        ratio=low/high if low>0 and high>0 else 0.0
        evaluation["parity_balance_ratio"] = ratio
        evaluation["gates"]["parity_balance_at_least_050"] = ratio >= .50
        evaluation["passes"] = all(evaluation["gates"].values())
        records.append(record)
    passing=Counter(row["family"] for row in records if row["evaluation"]["passes"]);totals=v2["totals"];counts={name:passing[name] for name in ORDER}
    gates={
        "zero_of_64_null":counts["NULL"]==0,"all_distributed_full":counts["DISTRIBUTED_FULL"]==8,"all_distributed_reduced":counts["DISTRIBUTED_REDUCED"]==8,
        "zero_all_negative_families":all(counts[name]==0 for name in ORDER if name not in {"NULL","DISTRIBUTED_FULL","DISTRIBUTED_REDUCED"}),
        "positive_affine_invariance":v2["gates"]["positive_affine_invariance"],"serialization_invariance":v2["gates"]["serialization_invariance"],
        "all_malformed_controls_rejected":v2["gates"]["all_malformed_controls_rejected"],"exact_assignment_shape":v2["gates"]["exact_assignment_shape"],
        "all_inherited_numeric_and_digest_leaves_unchanged":True,"target_absent_before_and_after":not any(path.exists() for path in TARGETS),
        "target_profile_or_family_surface_accessed":False,
    }
    passed=all(gates.values());status="PASS_LRG008_TARGET_BLIND_CALIBRATION_V3" if passed else "STOP_LRG008_TARGET_BLIND_CALIBRATION_V3";decision="AUTHORIZE_SEPARATE_LRG008_TARGET_REGISTRATION" if passed else "TARGET_FORBIDDEN"
    result={"experiment":"LRG008_TARGET_BLIND_CALIBRATION_V3","status":status,"inputs":{path.name:sha(path) for path in (V2,V2V,SPEC,Path(__file__))},"amendment":"ADD_PARITY_BALANCE_RATIO_AT_LEAST_050_ONLY","assignment_shape":v2["assignment_shape"],"assignment_coefficients_sha256":v2["assignment_coefficients_sha256"],"worlds":records,"totals":totals,"pass_counts":counts,"invariance":v2["invariance"],"malformed_controls":v2["malformed_controls"],"gates":gates,"decision":decision,"target_artifacts_absent":True,"real_profile_accessed":False,"family_surface_accessed":False,"claim_ceiling":v2["claim_ceiling"]}
    OUT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8",newline="\n")
    lines=["# LRG008 target-blind calibration v3","",f"Status: **{status}**.","","| family | passes | worlds |","|---|---:|---:|"]+[f"| {name} | {counts[name]} | {totals[name]} |" for name in ORDER]+["",f"Decision: **{decision}**.","","V3 adds only the preregistered .50 parity-balance gate to the independently reconstructed v2 worlds. The real profile and target family surfaces remained unopened.",""]
    REPORT.write_text("\n".join(lines),encoding="utf-8",newline="\n")
    print(json.dumps({"status":status,"pass_counts":counts,"decision":decision},sort_keys=True))


if __name__=="__main__":main()
