#!/usr/bin/env python3
from __future__ import annotations
import csv,hashlib,json,re,urllib.request
from collections import defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]; BASE=ROOT/"experiments/semantic_assumptions"; RES=BASE/"results"
METHOD=BASE/"RFO001_RECURRENT_FIGURE_LABEL_OWNERSHIP_METHOD.md"
ROLES=RES/"existing_human_locus_roles.tsv"; ANN=RES/"existing_human_exact_locus_annotations.tsv"; GROUPS=RES/"source_sta_group_alignment.tsv"
OUT=RES/"rfo001_recurrent_figure_label_selection.json"; REPORT=RES/"rfo001_recurrent_figure_label_selection_report.md"
MANIFEST="https://collections.library.yale.edu/manifests/2002046"; MANIFEST_SHA="317d58fd9ea90392a83d9858a91eada3d0b41416a3c835857dc0154bd123a309"
EXPECTED={"f72v3.10":"1006204","f75v.37":"1006209","f84r.11":"1006226"}
def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def folio(page:str)->str:
 m=re.match(r"f\d+",page.lower());
 if not m:raise AssertionError(page)
 return m.group(0)
def main()->None:
 if OUT.exists() or REPORT.exists():raise SystemExit("refusing overwrite")
 roles={r["locus"]:r for r in csv.DictReader(ROLES.open(newline="",encoding="utf-8"),delimiter="\t") if r["kind"]=="L"}
 anns=defaultdict(list)
 for r in csv.DictReader(ANN.open(newline="",encoding="utf-8"),delimiter="\t"):anns[r["locus"]].append(r)
 readings=defaultdict(dict)
 for r in csv.DictReader(GROUPS.open(newline="",encoding="utf-8"),delimiter="\t"):
  if r["source_group_count"]=="1":readings[r["locus"]][r["edition"]]=r["nearest_basic_eva_primary"]
 by=defaultdict(list)
 for locus,role in roles.items():
  v=readings.get(locus,{})
  if set(v)=={"ZL3b","IT2a","RF1b"} and len(set(v.values()))==1 and len(v["ZL3b"])>=2:
   by[v["ZL3b"]].append((locus,role["page"]))
 selected={}
 for surface,occ in by.items():
  per=[]
  for locus,_ in occ:
   tags={t for a in anns.get(locus,[]) for t in a["object_tags"].split(";") if t and t!="LABEL"}
   per.append(tags)
  if len({folio(page) for _,page in occ})>=3 and per and all(per) and "FIGURE" in set.intersection(*per):
   selected[surface]=sorted(occ)
 if selected!={"otoly":[("f72v3.10","f72v3"),("f75v.37","f75v"),("f84r.11","f84r")]}:raise SystemExit(selected)
 raw=urllib.request.urlopen(MANIFEST,timeout=60).read()
 if hashlib.sha256(raw).hexdigest()!=MANIFEST_SHA:raise SystemExit("manifest hash")
 manifest=json.loads(raw); canvases={c["id"].rsplit("/",1)[-1]:c for c in manifest["items"]}
 targets=[]
 for locus,page in selected["otoly"]:
  cid=EXPECTED[locus]; c=canvases[cid]
  targets.append({"locus":locus,"page":page,"physical_folio":folio(page),"surface":"otoly","canvas_id":cid,"canvas_label":c["label"]["none"][0],"official_dimensions":[c["width"],c["height"]],"official_full_image_url":f"https://collections.library.yale.edu/iiif/2/{cid}/full/full/0/default.jpg","prior_full_canvas_exposure":True})
 result={"experiment":"RFO001_RECURRENT_FIGURE_LABEL_OWNERSHIP_SELECTION","schema":"RFO001_SELECTION_V1","status":"FROZEN_ONE_EXACT_THREE_FOLIO_FIGURE_TAG_RECURRENCE_BEFORE_TARGET_IMAGE_ACCESS","decision":"AUTHORIZE_THREE_SOURCE_BOUND_NATIVE_OWNERSHIP_INSPECTIONS","surface_selection_rule":"all editorial L exact one-group all-reading-agreement surfaces length>=2 recurring on >=3 physical folios with annotations at every occurrence and FIGURE in the all-occurrence non-LABEL tag intersection","targets":targets,"outcomes":["SINGULAR_FIGURE_OWNED","SLOT_OR_GROUP_ASSOCIATED","PROXIMITY_ONLY","LOCALIZATION_UNRESOLVED"],"gates":["target_inscription_securely_localized","exactly_one_plausible_human_figure_in_local_slot","author_visible_assignment_device","no_equal_competing_figure","assignment_independent_of_editorial_text_or_order"],"panel_rule":"PASS_ONLY_IF_ALL_THREE_TARGETS_ARE_SINGULAR_FIGURE_OWNED","inputs":{str(p.relative_to(ROOT)):sha(p) for p in (METHOD,ROLES,ANN,GROUPS)}|{"yale_manifest_2002046_sha256":MANIFEST_SHA},"access":{"target_image_bodies_opened":False,"parser_roots_or_roles_used":False,"alternate_readings_treated_as_replicates":False,"prior_full_canvas_exposure_disclosed":True},"claim_ceiling":"A pass can establish only one exact manual surface recurring at three singular figure-owned label positions. It cannot establish FIGURE WOMAN NYMPH a name POS sound language cipher plaintext meaning or translation; prose occurrence and productive composition remain explicit."}
 OUT.write_text(json.dumps(result,sort_keys=True,separators=(",",":"))+"\n")
 REPORT.write_text("# RFO001 recurrent figure-label ownership selection\n\nStatus: **FROZEN_ONE_EXACT_THREE_FOLIO_FIGURE_TAG_RECURRENCE_BEFORE_TARGET_IMAGE_ACCESS**.\n\nThe complete mechanical rule retains only `otoly`, at f72v3.10, f75v.37, and f84r.11 on three physical folios. All three official Yale canvases and five visual ownership gates are frozen before opening the target image bodies. Prior full-canvas exposure for unrelated layout work is disclosed.\n\nA pass requires singular visible ownership at all three loci. It would still not establish FIGURE, WOMAN, NYMPH, a name, POS, sound, language, cipher, plaintext, meaning, or translation.\n")
if __name__=="__main__":main()
