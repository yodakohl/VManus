#!/usr/bin/env python3
"""Freeze GDT138 line windows before visible-feature scoring."""
import csv,hashlib,json,re
from collections import defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT/"gdt062_right_family_inventory.tsv";PANEL=ROOT/"gdt137_herbal_visual_feature_inventory.tsv";METHOD=ROOT/"GDT138_HERBAL_ENTRY_LINE_CONTENT_LOCALIZATION_METHOD.md";WINDOWS=ROOT/"gdt138_line_window_inventory.tsv";PRED=ROOT/"gdt138_prediction.json"
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def order(locus):
 m=re.search(r"\.(\d+)$",locus);assert m,locus;return int(m.group(1))
with PANEL.open(encoding="utf8",newline="")as h:pages=list(csv.DictReader(h,delimiter="\t"))
wanted={r["page"]for r in pages};lines=defaultdict(lambda:defaultdict(int))
with SOURCE.open(encoding="utf8",newline="")as h:
 for row in csv.DictReader(h,delimiter="\t"):
  if row["page"].startswith("f84")or row["page"]not in wanted:continue
  lines[row["page"]][row["locus"]]+=1
out=[]
for row in pages:
 z=sorted(lines[row["page"]],key=order)
 if len(z)<2:continue
 out.append({"page":row["page"],"physical_folio":row["physical_folio"],"source_lines":len(z),"source_groups":sum(lines[row["page"]].values()),"first_locus":z[0],"first_groups":lines[row["page"]][z[0]],"body_after_first_lines":len(z)-1,"body_after_first_groups":sum(lines[row["page"]][x]for x in z[1:]),"last_locus":z[-1],"last_groups":lines[row["page"]][z[-1]],"selection":"MECHANICAL_NUMERIC_SOURCE_LOCUS_ORDER","semantic_role":"UNASSIGNED"})
assert len(out)==126 and len({r["physical_folio"]for r in out})==62 and {r["page"]for r in pages}-{r["page"]for r in out}=={"f57r"}
with WINDOWS.open("w",encoding="utf8",newline="")as h:w=csv.DictWriter(h,fieldnames=list(out[0]),delimiter="\t",lineterminator="\n");w.writeheader();w.writerows(out)
p={"schema":"GDT138_HERBAL_ENTRY_LINE_CONTENT_LOCALIZATION_PREDICTION_V1","status":"FROZEN_POST_GDT137_POSITIONAL_ABLATION_BEFORE_WINDOW_SCORING","chronology":"GDT137 whole-page outcome public; fixed first/body/last/all positional test frozen before window scores.","pages":126,"physical_folios":62,"excluded_one_line_page":"f57r","windows":["FIRST_LINE","BODY_AFTER_FIRST","LAST_LINE","ALL_PAGE"],"representations":["PAGE_HOST_IDENTITY","PAGE_HOST_CHAR3","RAW_CHAR3"],"primary_window":"FIRST_LINE","primary_features":json.load(open(ROOT/"gdt137_prediction.json"))["primary_capacity_features"],"cross_currier_features":json.load(open(ROOT/"gdt137_prediction.json"))["cross_currier_features"],"k":7,"shrink":8.0,"worlds":10000,"selector_models":12,"null":"CURRIER_HAND_ILLUSTRATION_PROFILE_COMPLETE_FEATURE_VECTOR","f84":{"all_rows_rejected_before_retention":True,"new_f84r_access":False},"claim_ceiling":"Entry-line visible-feature association only; no name field, semantic role, gloss, word, morpheme, POS, sound, language, plaintext, meaning, plant identity, or translation.","inputs":{x.name:sha(x)for x in(METHOD,SOURCE,PANEL,ROOT/"gdt137_prediction.json",ROOT/"gdt137_result.json")},"implementation":{Path(__file__).name:sha(Path(__file__))},"outputs":{WINDOWS.name:sha(WINDOWS)}};p["prediction_content_sha256"]=csha(p);PRED.write_text(json.dumps(p,indent=2,sort_keys=True)+"\n",encoding="utf8");print(json.dumps({"status":p["status"],"pages":len(out),"folios":62},sort_keys=True))
