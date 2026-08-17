#!/usr/bin/env python3
"""Validate the GDT276 pre-score design without loading a Voynich row source."""
import hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256((R/p).read_bytes()).hexdigest()
def ch(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def main():
 d=json.loads((R/"gdt276_design.json").read_text());checks=[]
 def ck(n,v):
  checks.append({"check":n,"pass":bool(v)})
  if not v:raise AssertionError(n)
 ck("status",d["status"]=="FROZEN_BEFORE_GDT276_SCORING");ck("five_models",d["models"]==["COMPRESSED_NATURAL_LANGUAGE","ABBREVIATION_HEAVY_LANGUAGE","LOCAL_CODEBOOK","TECHNICAL_NOTATION","HYBRID"]);ck("opaque_target",d["primary_target"]=="OPAQUE_PAGE_HOST");ck("no_semantics",d["semantic_assignments"]==0);ck("folio_fold",d["fold"]=="LEAVE_ONE_PHYSICAL_FOLIO_OUT");ck("page_past_only",d["page_conditioning"]=="HELD_PAGE_PREQUENTIAL_PAST_ONLY");ck("f84_guard",d["source_guard"]=="REJECT_ALL_F84_PREFIX_ROWS_BEFORE_FORMAL_COLUMN_PARSE");ck("buckets_256",d["capacity"]["context_buckets"]==256);ck("worlds_64",d["matched_control_worlds"]==64);ck("alphabet_22",len(d["alphabet"])==22 and d["alphabet"][-1]=="<EOS>");ck("compiler_complete",set(["register","record_ordinal","within_field_position","wrapper","q_flag","local_frame","inner_d","right_family","dy_closure","b3","line_close","paragraph_close","known_label_renderer"]).issubset(d["compiler_nuisance"]));ck("method_exists",(R/"GDT276_RESIDUAL_CHANNEL_WORLD_COMPARISON_METHOD.md").is_file())
 p={"experiment":"GDT276_DESIGN_VALIDATION","status":"PASS","checks_passed":len(checks),"checks_total":len(checks),"design_sha256":sha("gdt276_design.json"),"method_sha256":sha("GDT276_RESIDUAL_CHANNEL_WORLD_COMPARISON_METHOD.md"),"validator_sha256":sha(Path(__file__).name),"checks":checks};p["content_hash"]=ch(p);(R/"gdt276_design_validation.json").write_text(json.dumps(p,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":"PASS","checks":len(checks)},sort_keys=True))
if __name__=="__main__":main()
