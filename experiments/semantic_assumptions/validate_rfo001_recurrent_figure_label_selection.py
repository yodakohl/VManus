#!/usr/bin/env python3
from __future__ import annotations
import csv,hashlib,json,re,urllib.request
from collections import defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/"experiments/semantic_assumptions";RES=BASE/"results"
METHOD=BASE/"RFO001_RECURRENT_FIGURE_LABEL_OWNERSHIP_METHOD.md";ROLES=RES/"existing_human_locus_roles.tsv";ANN=RES/"existing_human_exact_locus_annotations.tsv";GROUPS=RES/"source_sta_group_alignment.tsv";RESULT=RES/"rfo001_recurrent_figure_label_selection.json";OUT=RES/"rfo001_recurrent_figure_label_selection_validation.json";REPORT=RES/"rfo001_recurrent_figure_label_selection_validation_report.md"
MANIFEST="https://collections.library.yale.edu/manifests/2002046";MSHA="317d58fd9ea90392a83d9858a91eada3d0b41416a3c835857dc0154bd123a309"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def folio(s):
 m=re.match(r"f\d+",s.lower());assert m;return m.group()
def main():
 if OUT.exists() or REPORT.exists():raise SystemExit("refusing overwrite")
 roles={r["locus"]:r for r in csv.DictReader(ROLES.open(),delimiter="\t") if r["kind"]=="L"};anns=defaultdict(list);rd=defaultdict(dict)
 for r in csv.DictReader(ANN.open(),delimiter="\t"):anns[r["locus"]].append(r)
 for r in csv.DictReader(GROUPS.open(),delimiter="\t"):
  if r["source_group_count"]=="1":rd[r["locus"]][r["edition"]]=r["nearest_basic_eva_primary"]
 by=defaultdict(list)
 for loc,r in roles.items():
  v=rd.get(loc,{})
  if set(v)=={"ZL3b","IT2a","RF1b"} and len(set(v.values()))==1 and len(v["ZL3b"])>=2:by[v["ZL3b"]].append((loc,r["page"]))
 sel={}
 for s,occ in by.items():
  tags=[{t for a in anns.get(l,[]) for t in a["object_tags"].split(";") if t and t!="LABEL"} for l,_ in occ]
  if len({folio(p) for _,p in occ})>=3 and tags and all(tags) and "FIGURE" in set.intersection(*tags):sel[s]=sorted(occ)
 raw=urllib.request.urlopen(MANIFEST,timeout=60).read();assert hashlib.sha256(raw).hexdigest()==MSHA;m=json.loads(raw);cm={c["id"].rsplit("/",1)[-1]:(c["width"],c["height"]) for c in m["items"]}
 r=json.loads(RESULT.read_text()); checks={"canonical":RESULT.read_bytes()==(json.dumps(r,sort_keys=True,separators=(",",":"))+"\n").encode(),"complete_selection":sel=={"otoly":[("f72v3.10","f72v3"),("f75v.37","f75v"),("f84r.11","f84r")]},"three_physical_folios":{x["physical_folio"] for x in r["targets"]}=={"f72","f75","f84"},"exact_canvas_bindings":[(x["canvas_id"],x["official_dimensions"]) for x in r["targets"]]==[("1006204",list(cm["1006204"])),("1006209",list(cm["1006209"])),("1006226",list(cm["1006226"]))],"input_hashes":r["inputs"]=={str(p.relative_to(ROOT)):sha(p) for p in (METHOD,ROLES,ANN,GROUPS)}|{"yale_manifest_2002046_sha256":MSHA},"sealed_target_access":r["access"]["target_image_bodies_opened"] is False,"prior_exposure_disclosed":r["access"]["prior_full_canvas_exposure_disclosed"] is True,"panel_rule":r["panel_rule"]=="PASS_ONLY_IF_ALL_THREE_TARGETS_ARE_SINGULAR_FIGURE_OWNED","claim_ceiling":all(x in r["claim_ceiling"] for x in ("prose occurrence","translation"))}
 if not all(checks.values()):raise SystemExit([k for k,v in checks.items() if not v])
 v={"experiment":"RFO001_SELECTION_VALIDATION","schema":"RFO001_SELECTION_VALIDATION_V1","status":"PASS_9_CHECK_INDEPENDENT_SOURCE_AND_MANIFEST_RECONSTRUCTION","source_result_sha256":sha(RESULT),"check_count":len(checks),"checks":checks,"claim_ceiling":r["claim_ceiling"]};OUT.write_text(json.dumps(v,sort_keys=True,separators=(",",":"))+"\n");REPORT.write_text("# RFO001 selection validation\n\nStatus: **PASS_9_CHECK_INDEPENDENT_SOURCE_AND_MANIFEST_RECONSTRUCTION**.\n\nIndependent code reconstructs the unique three-folio type, exact loci, physical folios, official canvas bindings, hashes, sealed target access, prior exposure disclosure, panel rule, and claim ceiling.\n")
if __name__=="__main__":main()
