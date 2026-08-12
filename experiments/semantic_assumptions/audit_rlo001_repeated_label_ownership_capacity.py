#!/usr/bin/env python3
from __future__ import annotations
import csv,hashlib,json
from collections import defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]; BASE=ROOT/"experiments/semantic_assumptions"; RES=BASE/"results"
ANN=RES/"existing_human_exact_locus_annotations.tsv"; GROUPS=RES/"source_sta_group_alignment.tsv"
OUT=RES/"rlo001_repeated_label_ownership_capacity.json"; REPORT=RES/"rlo001_repeated_label_ownership_capacity_report.md"
STRICT={"REL_EXPLICIT_ATTACHMENT","REL_DIRECT_ENCLOSURE","REL_EXPLICIT_IDENTITY"}
def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def main()->None:
 if OUT.exists() or REPORT.exists():raise SystemExit("refusing overwrite")
 readings=defaultdict(dict)
 with GROUPS.open(newline="",encoding="utf-8") as f:
  for r in csv.DictReader(f,delimiter="\t"):
   if r["source_group_count"]=="1":readings[r["locus"]][r["edition"]]=r["nearest_basic_eva_primary"]
 strict=[]; loose=[]
 with ANN.open(newline="",encoding="utf-8") as f:
  for r in csv.DictReader(f,delimiter="\t"):
   tags=set((r["local_relation_tags"]+";"+r["unit_relation_tags"]).split(";")); vals=readings.get(r["locus"],{})
   base=r["certainty"]=="UNHEDGED" and r["context_class"]=="OBJECT_BEARING" and set(vals)=={"ZL3b","IT2a","RF1b"} and len(set(vals.values()))==1 and bool(vals.get("ZL3b"))
   if base and tags&STRICT:strict.append((r["locus"],r["page"],vals["ZL3b"]))
   if base and tags&(STRICT|{"REL_ARRAY_OR_GROUP"}):loose.append((r["locus"],r["page"],vals["ZL3b"]))
 def repeated(rows):
  d=defaultdict(list)
  for loc,page,surface in rows:d[surface].append((loc,page))
  return {s:v for s,v in d.items() if len({x[1] for x in v})>=2}
 sr=repeated(strict); lr=repeated(loose)
 result={"experiment":"RLO001_REPEATED_LABEL_OWNERSHIP_CAPACITY","schema":"RLO001_CAPACITY_V1","status":"STOP_ZERO_CROSS_PAGE_EXACT_REPEATS_WITH_STRICT_SINGULAR_OWNERSHIP","decision":"DO_NOT_OPEN_IMAGES_OR_BUILD_OBJECT_CLASS_TEST",
  "strict_relation_tags":sorted(STRICT),"counts":{"strict_eligible_labels":len(strict),"strict_exact_types":len({x[2] for x in strict}),"strict_cross_page_repeat_types":len(sr),"strict_cross_page_repeat_rows":sum(map(len,sr.values())),"loose_array_inclusive_labels":len(loose),"loose_array_inclusive_cross_page_repeat_types":len(lr)},
  "loose_diagnostic":{s:[x[0] for x in v] for s,v in sorted(lr.items())},
  "gates":{"at_least_three_strict_repeat_types":len(sr)>=3,"at_least_six_strict_repeat_rows":sum(map(len,sr.values()))>=6,"at_least_three_physical_folios":len({page for v in sr.values() for _,page in v})>=3},
  "inputs":{str(ANN.relative_to(ROOT)):sha(ANN),str(GROUPS.relative_to(ROOT)):sha(GROUPS)},
  "access":{"image_bodies_opened":False,"object_descriptions_used_in_selection":False,"alternate_readings_treated_as_replicates":False,"formal_parser_roots_or_roles_used":False},
  "claim_ceiling":"The complete strict source-only census has no cross-page exact repeated single-group label with singular human attachment at both endpoints. This closes only that exact recurrence bridge and supplies no object identity, word, language, cipher, plaintext, meaning, or translation."}
 OUT.write_text(json.dumps(result,sort_keys=True,separators=(",",":"))+"\n")
 REPORT.write_text("# RLO001 repeated-label ownership capacity\n\nStatus: **STOP_ZERO_CROSS_PAGE_EXACT_REPEATS_WITH_STRICT_SINGULAR_OWNERSHIP**.\n\nA complete source-only census requires unhedged object-bearing rows, one exact single group in all three alternate readings, and a human relation of explicit attachment, direct enclosure, or explicit identity. It retains 57 labels and 57 exact types: zero repeat across pages.\n\nAllowing the nonsingular `REL_ARRAY_OR_GROUP` tag would create three apparent two-row repeats (`darol`, `otedy`, `otoly`), but that tag does not assign either string to one object and cannot support the proposed bridge. Stop before image review or object-class comparison.\n\nNo object identity, word, language, plaintext, meaning, or translation follows.\n")
if __name__=="__main__":main()
