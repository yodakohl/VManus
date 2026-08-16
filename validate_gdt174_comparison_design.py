#!/usr/bin/env python3
"""Independent pre-score validation of the GDT174 freeze."""
from __future__ import annotations
import csv,hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parent
D=R/"gdt174_design.json";OUT=R/"gdt174_design_validation.json"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(x):return hashlib.sha256(json.dumps(x,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def main():
 d=json.loads(D.read_text());checks=[]
 def ck(x,n):
  assert x,n;checks.append(n)
 ck(d["status"]=="FROZEN_BEFORE_VOYNICH_FINGERPRINT_SCORING","status")
 ck(d["controls"]==["LEXICAL_A","HUMAN_GROWN_B2","FACTORIAL_B"] and d["controls_frozen_exactly_as_published"],"controls")
 ck(not d["build_b3"] and d["no_threshold_tuning"] and d["no_composite"],"prohibitions")
 ck(all(sha(R/k)==v for k,v in d["input_sha256"].items()),"input_hashes")
 stored=d.pop("design_content_sha256");ck(csha(d)==stored,"content_hash")
 frames=set();f84_frames=0
 with (R/"gdt046_line_frames.tsv").open(newline="",encoding="utf8") as h:
  for r in csv.DictReader(h,delimiter="\t"):
   if r["page"].startswith("f84") or r["locus"].startswith("f84"):f84_frames+=1;continue
   frames.add(r["locus"])
 n=kept=f84=f84r=0;by={}
 with (R/"gdt062_right_family_inventory.tsv").open(newline="",encoding="utf8") as h:
  for r in csv.DictReader(h,delimiter="\t"):
   n+=1
   if r["page"].startswith("f84r") or r["locus"].startswith("f84r"):f84r+=1
   if r["page"].startswith("f84") or r["locus"].startswith("f84"):f84+=1;continue
   if r["locus"] not in frames:continue
   kept+=1;by.setdefault(r["locus"],[]).append(r)
 ck(f84r==0 and f84>0 and f84_frames>0,"f84r_absent_f84_guard_required")
 ck(kept>0 and by,"eligible_capacity")
 ck(all(len(v)==int(v[0]["group_count"]) and sorted(int(x["group_index"]) for x in v)==list(range(1,int(v[0]["group_count"])+1)) for v in by.values()),"complete_lines")
 ck(d["comparability"]["HOST_RECOVERY_ACCURACY"].startswith("NOT_COMPARABLE"),"host_recovery_unresolved")
 ck(d["comparability"]["REGISTER_ALIGNMENT"].startswith("NOT_DIRECTLY_COMPARABLE"),"alignment_unresolved")
 ck(d["placement_rule"].endswith("NO_COMPOSITE"),"rank_only")
 out={"schema":"GDT174_DESIGN_VALIDATION_V1","status":"PASS_INDEPENDENT_PRESCORE_FREEZE","checks_passed":len(checks),"checks_failed":0,"checks":checks,"source_rows":n,"eligible_groups":kept,"eligible_lines":len(by),"f84_rows_rejected":f84,"f84r_rows_in_source":f84r,"design_sha256":sha(D),"validator_sha256":sha(Path(__file__)),"f84r_access":False}
 out["validation_content_sha256"]=csha(out);OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print(f"PASS {len(checks)}/{len(checks)}")
if __name__=="__main__":main()
