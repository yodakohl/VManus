#!/usr/bin/env python3
"""Independent pre-control validation of GDT175 design."""
from __future__ import annotations
import hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parent;D=R/"gdt175_design.json";OUT=R/"gdt175_design_validation.json"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(x):return hashlib.sha256(json.dumps(x,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def main():
 d=json.loads(D.read_text());checks=[]
 def ck(v,n):assert v,n;checks.append(n)
 ck(d["status"]=="DIAGNOSTIC_FROZEN_BEFORE_CONTROL_CALIBRATION","status");ck(d["controls"]==["LEXICAL_A","HUMAN_GROWN_B2","FACTORIAL_B"] and d["controls_frozen_exactly_as_published"],"controls");ck(d["control_level"]=="SURFACE_ONLY" and not d["build_b3"],"level_no_b3");ck(d["occurrence_bins"]=={"N2_4":[2,4],"N5_15":[5,15],"N16_63":[16,63],"N64_PLUS":[64,None]},"bins");ck(d["sampling_null"]["worlds"]==256 and d["sampling_null"]["shuffle"]=="PARTNER_ASSIGNMENT_ONLY","null");ck(d["held_model"]=={"alpha":16.0,"beta":8.0,"fold":"PHYSICAL_FOLIO","nuisance":["GROUP_INDEX","LINE_ORDINAL_MOD3","GROUP_COUNT"]},"held_model");ck(d["powered_scope"]=={"minimum_eligible_hosts":3,"minimum_folios":3,"minimum_next_events":20} and d["powered_bin_minimum_hosts"]==5,"power");ck(all(sha(R/k)==v for k,v in d["control_inputs"].items()),"hashes");stored=d.pop("design_content_sha256");ck(csha(d)==stored,"content_hash");ck(d["no_rescaling"] and d["no_tuning"] and d["no_new_architecture"],"prohibitions");ck(not d["f84r_access"],"f84r")
 out={"schema":"GDT175_DESIGN_VALIDATION_V1","status":"PASS_INDEPENDENT_PRECONTROL_FREEZE","checks_passed":len(checks),"checks_failed":0,"checks":checks,"design_sha256":sha(D),"validator_sha256":sha(Path(__file__)),"f84r_access":False};out["validation_content_sha256"]=csha(out);OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print(f"PASS {len(checks)}/{len(checks)}")
if __name__=="__main__":main()
