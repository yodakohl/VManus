#!/usr/bin/env python3
"""Validate the pre-relation GDT384 freeze."""
import csv,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];BASE=ROOT/"experiments/yolo/gdt384_role_specific_relational_consequence";ART=BASE/"artifacts"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def content(d):q=dict(d);q.pop("content_hash",None);return hashlib.sha256(json.dumps(q,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def main():
 r=json.loads((ART/"gdt384_stage_a_freeze.json").read_text());checks={"content_hash":r["content_hash"]==content(r),"status":r["status"]=="FROZEN_BEFORE_RELATION_CONSTRUCTION_OR_SCORING","six_roles":len(r["roles"])==6,"priority":r["priority_role"]=="COORDINATOR","five_resolutions":len(r["resolutions"])==5,"seven_channels":len(r["grammar_channels"])==7,"three_treatments":len(r["channel_treatments"])==3,"worlds":r["null"]["worlds"]==2048,"full_gate":r["full_stage_gate"]["all_six_roles"] and r["full_stage_gate"]["priority_coordinator_required"],"stage_b_locked":not r["voynich_stage_b_authorized"],"gdt381_forbidden":not r["gdt381_target_artifacts_allowed"],"f84":not any(r["f84"].values())}
 for p,h in r["inputs"].items():checks["input:"+p]=(ROOT/p).is_file() and sha(ROOT/p)==h
 for p,h in r["documents"].items():checks["document:"+p]=(ROOT/p).is_file() and sha(ROOT/p)==h
 for p,h in r["implementation"].items():checks["implementation:"+p]=(ROOT/p).is_file() and sha(ROOT/p)==h
 rows=list(csv.DictReader((BASE/"gdt384_relation_manifest.tsv").open(),delimiter="\t"));checks["manifest_six"]=len(rows)==6 and {x["role"] for x in rows}==set(r["roles"]);checks["no_voynich_inputs"]=not any("gdt327" in p or "gdt381" in p for p in r["inputs"])
 out={"schema":"GDT384_STAGE_A_FREEZE_VALIDATION_V1","status":"PASS" if all(checks.values()) else "FAIL","checks":len(checks),"passed":sum(checks.values()),"details":checks,"freeze_hash":sha(ART/"gdt384_stage_a_freeze.json"),"validator_hash":sha(BASE/"src/validate_stage_a_freeze.py")};out["content_hash"]=content(out);(ART/"gdt384_stage_a_freeze_validation.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":out["status"],"passed":out["passed"],"checks":out["checks"]}));
 if out["status"]!="PASS":raise SystemExit(1)
if __name__=="__main__":main()
