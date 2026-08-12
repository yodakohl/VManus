#!/usr/bin/env python3
from __future__ import annotations
import csv,hashlib,json,re,urllib.request
from collections import defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/"experiments/semantic_assumptions";RES=BASE/"results"
METHOD=BASE/"RRA001_RECURRENT_LABEL_OWNER_ATLAS_METHOD.md";ROLES=RES/"existing_human_locus_roles.tsv";ANN=RES/"existing_human_exact_locus_annotations.tsv";GROUPS=RES/"source_sta_group_alignment.tsv";RFO=RES/"rfo001_recurrent_figure_label_ownership_result.json";OUT=RES/"rra001_recurrent_label_owner_atlas_selection.json";REPORT=RES/"rra001_recurrent_label_owner_atlas_selection_report.md"
MANIFEST="https://collections.library.yale.edu/manifests/2002046";MSHA="317d58fd9ea90392a83d9858a91eada3d0b41416a3c835857dc0154bd123a309";CLASSES={"PLANT","FIGURE","WATER_OR_APPARATUS","STAR_OR_SKY"}
CANVAS={"f70v2":"1006200","f70v1":"1006201","f72r2":"1006203","f72r3":"1006203","f72v3":"1006204","f72v1":"1006205","f75v":"1006209","f80r":"1006218","f82r":"1006222","f84r":"1006226","f88r":"1037112","f89r1":"1006233","f99v":"1006247"}
FIXED={"f75v.21":"PROXIMITY_OR_GROUP_ONLY","f82r.35":"PROXIMITY_OR_GROUP_ONLY","f72v3.10":"OTHER_CLASS_OR_SLOT_ASSOCIATED","f75v.37":"SINGULAR_COMMON_CLASS_OWNED","f84r.11":"SINGULAR_COMMON_CLASS_OWNED"}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def folio(p):m=re.match(r"f\d+",p.lower());assert m;return m.group()
def panel():
 roles={r["locus"]:r for r in csv.DictReader(ROLES.open(),delimiter="\t") if r["kind"]=="L"};anns=defaultdict(list);rd=defaultdict(dict)
 for r in csv.DictReader(ANN.open(),delimiter="\t"):anns[r["locus"]].append(r)
 for r in csv.DictReader(GROUPS.open(),delimiter="\t"):
  if r["source_group_count"]=="1":rd[r["locus"]][r["edition"]]=r["nearest_basic_eva_primary"]
 by=defaultdict(list)
 for loc,m in roles.items():
  v=rd.get(loc,{})
  if set(v)=={"ZL3b","IT2a","RF1b"} and len(set(v.values()))==1 and len(v["ZL3b"])>=2:by[v["ZL3b"]].append((loc,m["page"]))
 out={}
 for s,occ in by.items():
  if len({folio(p) for _,p in occ})<2:continue
  tags=[{t for a in anns.get(l,[]) for t in a["object_tags"].split(";") if t in CLASSES} for l,_ in occ]
  common=set.intersection(*tags) if tags and all(tags) else set()
  if common:out[s]={"shared_classes":sorted(common),"occurrences":sorted(occ)}
 return dict(sorted(out.items()))
def main():
 if OUT.exists() or REPORT.exists():raise SystemExit("refusing overwrite")
 p=panel();assert len(p)==9 and sum(len(x["occurrences"]) for x in p.values())==21
 raw=urllib.request.urlopen(MANIFEST,timeout=60).read();assert hashlib.sha256(raw).hexdigest()==MSHA;m=json.loads(raw);cm={c["id"].rsplit("/",1)[-1]:c for c in m["items"]}
 rows=[]
 for s,x in p.items():
  for loc,page in x["occurrences"]:
   cid=CANVAS[page];c=cm[cid];rows.append({"surface":s,"shared_classes":x["shared_classes"],"locus":loc,"page":page,"physical_folio":folio(page),"canvas_id":cid,"official_dimensions":[c["width"],c["height"]],"official_full_image_url":f"https://collections.library.yale.edu/iiif/2/{cid}/full/full/0/default.jpg","exposure":"FIXED_PRIOR" if loc in FIXED else "SEALED_TARGET_JUDGMENT","fixed_outcome":FIXED.get(loc)})
 assert len(rows)==21 and sum(r["exposure"]=="SEALED_TARGET_JUDGMENT" for r in rows)==16
 result={"experiment":"RRA001_RECURRENT_LABEL_OWNER_ATLAS_SELECTION","schema":"RRA001_SELECTION_V1","status":"FROZEN_COMPLETE_NINE_TYPE_TWENTY_ONE_LOCUS_ATLAS_FIVE_FIXED_SIXTEEN_SEALED","decision":"AUTHORIZE_SIXTEEN_BOUNDED_SOURCE_NATIVE_OWNERSHIP_JUDGMENTS","selection_rule":"kind L; exact one source group and same length>=2 literal in all readings; >=2 physical folios; annotations at every occurrence; nonempty all-occurrence intersection over four frozen coarse tags","counts":{"types":len(p),"loci":len(rows),"physical_folios":len({r["physical_folio"] for r in rows}),"fixed_prior_outcomes":sum(r["exposure"]=="FIXED_PRIOR" for r in rows),"sealed_target_judgments":sum(r["exposure"]=="SEALED_TARGET_JUDGMENT" for r in rows)},"rows":rows,"type_rule":"PASS_ONLY_IF_EVERY_OCCURRENCE_IS_SINGULAR_COMMON_CLASS_OWNED","inputs":{str(q.relative_to(ROOT)):sha(q) for q in (METHOD,ROLES,ANN,GROUPS,RFO)}|{"yale_manifest_2002046_sha256":MSHA},"access":{"sixteen_target_specific_ownership_judgments_opened":False,"prior_full_canvas_exposure_disclosed":True,"ocr_clip_embedding_or_automated_vision_used":False,"parser_roots_or_roles_used":False},"claim_ceiling":"This freezes a descriptive owner-acquisition census. A passing type could establish repeated exact label use in visibly owned same-class positions only; it cannot name that class or establish a word POS sound language cipher plaintext meaning or translation."}
 OUT.write_text(json.dumps(result,sort_keys=True,separators=(",",":"))+"\n");REPORT.write_text("# RRA001 recurrent-label owner atlas selection\n\nStatus: **FROZEN_COMPLETE_NINE_TYPE_TWENTY_ONE_LOCUS_ATLAS_FIVE_FIXED_SIXTEEN_SEALED**.\n\nThe complete mechanical census retains nine exact cross-folio label types, 21 loci, and nine physical folios. Five ownership outcomes are fixed from published `darol`/RFO001 work; sixteen target-specific judgments remain sealed. A type qualifies only if every occurrence is singularly owned by its frozen shared coarse class.\n\nThis is descriptive acquisition, not semantic confirmation. No class name, word, POS, sound, language, cipher, plaintext, meaning, or translation follows.\n")
if __name__=="__main__":main()
