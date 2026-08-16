#!/usr/bin/env python3
"""Freeze GDT174 metric/comparability rules before Voynich scoring."""
from __future__ import annotations
import hashlib,json
from pathlib import Path

R=Path(__file__).resolve().parent
OUT=R/"gdt174_design.json"
METHOD=R/"GDT174_VOYNICH_CALIBRATED_FINGERPRINT_METHOD.md"
FILES=[
 "gdt062_right_family_inventory.tsv","gdt046_line_frames.tsv",
 "gdt172_blind_parses.json.gz","gdt172_blind_diagnostics.tsv",
 "gdt172_recovery_levels.tsv","gdt172_component_recovery.tsv","gdt172_result.json",
 "gdt173_blind_parses.json.gz","gdt173_blind_diagnostics.tsv",
 "gdt173_recovery_levels.tsv","gdt173_component_recovery.tsv",
 "gdt173_three_system_fingerprint.tsv","gdt173_three_system_recovery.tsv","gdt173_result.json",
 "run_gdt170_blind_instrument.py","gdt167_alignment_scores.tsv","gdt167_result.json",
]
def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(x)->str:return hashlib.sha256(json.dumps(x,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def main():
    parent=json.loads((R/"gdt173_result.json").read_text())
    assert parent["status"]=="B2_DISTRIBUTED_IDENTITY_PARTIALLY_RECOVERED_WITHOUT_FACTORIAL_COMPATIBILITY"
    assert parent["system_a_frozen_unchanged"] and parent["factorial_b_frozen_unchanged"]
    design={
      "schema":"GDT174_VOYNICH_CALIBRATED_FINGERPRINT_DESIGN_V1",
      "status":"FROZEN_BEFORE_VOYNICH_FINGERPRINT_SCORING",
      "controls":["LEXICAL_A","HUMAN_GROWN_B2","FACTORIAL_B"],
      "controls_frozen_exactly_as_published":True,"build_b3":False,
      "voynich_representation":"FROZEN_GDT062_HPR2_ON_F84_FREE_COMPLETE_GDT046_LINES",
      "input_sha256":{name:sha(R/name) for name in FILES},
      "method_sha256":sha(METHOD),
      "operation_rules":{"lengths":[1,2,3],"minimum_distinct_hosts":8,"minimum_physical_folios":5,"maximum_per_side":12,"null_worlds":1024},
      "metrics":["HOST_RECOVERY_ACCURACY","HOST_RECURRENCE_PROXY","LEFT_RIGHT_COMPATIBILITY","SHORT_HOST_STRUCTURE","SAME_GROUP_SUBSTITUTION","EXTERNAL_SUBSTITUTION","NEXT_HOST","WHOLE_LINE","CLOSURE","REGISTER_ALIGNMENT"],
      "comparability":{"HOST_RECOVERY_ACCURACY":"NOT_COMPARABLE_NO_VOYNICH_ORACLE","HOST_RECURRENCE_PROXY":"DIRECT_PROXY_NOT_RECOVERY","LEFT_RIGHT_COMPATIBILITY":"DIRECT","SHORT_HOST_STRUCTURE":"DIRECT","SAME_GROUP_SUBSTITUTION":"STRUCTURALLY_ANALOGOUS_HPR2_SIGNATURE","EXTERNAL_SUBSTITUTION":"DIRECT","NEXT_HOST":"DIRECTION_ONLY_UNEQUAL_CORPUS","WHOLE_LINE":"DIRECTION_ONLY_UNEQUAL_CORPUS","CLOSURE":"STRUCTURALLY_ANALOGOUS_EDITORIAL_PARAGRAPH_END","REGISTER_ALIGNMENT":"NOT_DIRECTLY_COMPARABLE_NONPARALLEL_CONTENT"},
      "placement_rule":"UNSCALED_NEAREST_CONTROL_INSIDE_RANGE_ELSE_OUTSIDE; DIRECTION_ONLY_WHERE_DECLARED; NO_COMPOSITE",
      "f84_filter":"REJECT_PAGE_OR_LOCUS_PREFIX_F84_BEFORE_RETENTION",
      "f84r_access":False,"no_images":True,"no_new_parser":True,"no_threshold_tuning":True,"no_composite":True,
      "claim_ceiling":"Axis-wise synthetic calibration only; no Voynich encoder word code language morphology role meaning plaintext or translation.",
    }
    design["design_content_sha256"]=csha(design)
    OUT.write_text(json.dumps(design,indent=2,sort_keys=True)+"\n")
    print(design["status"])
if __name__=="__main__":main()
