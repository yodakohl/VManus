#!/usr/bin/env python3
"""Freeze the GDT137 page panel and visible-feature endpoints before scoring."""
from __future__ import annotations
import csv,hashlib,json,re
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parent
ARCH=ROOT/"gdt031_herbal_page_architecture.tsv"
ANNOT=ROOT/"experiments/semantic_assumptions/results/existing_human_page_annotations.tsv"
METHOD=ROOT/"GDT137_HERBAL_PAGE_VISUAL_FEATURE_TRANSFER_METHOD.md"
INVENTORY=ROOT/"gdt137_herbal_visual_feature_inventory.tsv"
PREDICTION=ROOT/"gdt137_prediction.json"

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def read(p):
 with Path(p).open(encoding="utf8",newline="")as h:return list(csv.DictReader(h,delimiter="\t"))
def rules():return {
 "DAISY_CUP":lambda s:"β: 'daisy in a cup'"in s,
 "BROAD_CALYX":lambda s:"β: broad many-fingered calyx"in s,
 "GRASS":lambda s:"β: 'grass'"in s,
 "ROOT_PLATFORM":lambda s:"β: root platform"in s,
 "LEAVES_ONE_SIDE":lambda s:"β: all leaves point to one side"in s,
 "FUSED_PARALLEL_LEAVES":lambda s:"β: leaves parallel and fused together on one stalk"in s,
 "BULB_OR_TUBER_ROOT":lambda s:bool(re.search(r"\bbulb|\btuber",s,re.I)),
 "LARGE_OR_EXTENSIVE_ROOT":lambda s:bool(re.search(r"large root|large roots|extensive roots|huge[^.]{0,40}root",s,re.I)),
 "MULTIPLE_PLANTS":lambda s:bool(re.search(r"two plants|two different plants|two of the same plants|row of plants|many plants",s,re.I)),
 "BLUE_FLOWERS_OR_BUDS":lambda s:"blue"in s.lower()and bool(re.search(r"flower|bud",s,re.I)),
 "FINGERED_OR_FRILLED_LEAVES":lambda s:bool(re.search(r"fingered leaves|frilled fingered leaves|leaves (?:ending in|with)[^.]{0,20}(?:finger|figer)|leaves are similar, with many fingers",s,re.I)),
 "MULTIPLE_STEMS_OR_STALKS":lambda s:bool(re.search(r"(two|three|four|several) (stems|stalks)",s,re.I)),
}

arch=[r for r in read(ARCH)if not r["page"].startswith("f84")]
assert len(arch)==127 and len({r["physical_folio"]for r in arch})==63
assert Counter(r["currier"]for r in arch)==Counter({"A":95,"B":32})
wanted={r["page"]for r in arch};annotations={}
with ANNOT.open(encoding="utf8",newline="")as h:
 for row in csv.DictReader(h,delimiter="\t"):
  if row["page"]in wanted:annotations[row["page"]]=row
assert set(annotations)==wanted and not any(p.startswith("f84")for p in annotations)
rule=rules();feature_names=list(rule);out=[]
for a in sorted(arch,key=lambda r:r["page"]):
 ann=annotations[a["page"]];values={name:int(fn(ann["illustrations"]))for name,fn in rule.items()}
 out.append({"page":a["page"],"physical_folio":a["physical_folio"],"currier":a["currier"],"hand":a["hand"],"illustration_profile":a["illustration_profile"],"catalogue_prose_lines":a["catalogue_prose_lines"],"paragraph_starts":a["paragraph_starts"],"catalogue_label_presence":a["catalogue_label_presence"],"formal_lines":a["LINES"],"formal_groups":a["GROUPS"],**values,"illustrations_sha256":hashlib.sha256(ann["illustrations"].encode()).hexdigest(),"source_url":ann["source_url"],"provenance":"EXISTING_HUMAN_ANNOTATION","semantic_role":"UNASSIGNED"})
with INVENTORY.open("w",encoding="utf8",newline="")as h:
 w=csv.DictWriter(h,fieldnames=list(out[0]),delimiter="\t",lineterminator="\n");w.writeheader();w.writerows(out)
counts={name:sum(int(r[name])for r in out)for name in feature_names}
primary=[name for name in feature_names if 8<=counts[name]<=119]
cross=[name for name in feature_names if all(sum(int(r[name])for r in out if r["currier"]==currier)>=2 for currier in("A","B"))]
assert len(primary)==8 and len(cross)==6
prediction={"schema":"GDT137_HERBAL_PAGE_VISUAL_FEATURE_TRANSFER_PREDICTION_V1","status":"FROZEN_ARCHIVE_WIDE_PAGE_TEST_BEFORE_FORMAL_SCORING","chronology":"The 12 human feature rules are inherited/public; the complete page panel and endpoint sets were frozen before whole-page formal predictions were computed.","panel":{"pages":127,"physical_folios":63,"currier_A_pages":95,"currier_B_pages":32},"features":feature_names,"feature_positive_pages":counts,"primary_capacity_features":primary,"cross_currier_features":cross,"representations":["PAGE_HOST_IDENTITY","PAGE_HOST_CHAR3","RAW_CHAR3","COMPILER_SIGNATURE"],"primary_representation_family":["PAGE_HOST_IDENTITY","PAGE_HOST_CHAR3"],"k":7,"shrink":8.0,"worlds":10000,"null":"CURRIER_HAND_ILLUSTRATION_PROFILE_COMPLETE_12_FEATURE_VECTOR","gates":{"page_host_selector_paid_gain_positive":True,"page_host_beats_raw_and_compiler":True,"positive_at_least_6_of_8_features":True,"positive_at_least_35_of_63_folios":True,"cross_currier_panel_positive":True,"max_four_p_le_005":True},"outcome_access":"ARCHIVED_HUMAN_DESCRIPTIONS_ALREADY_PUBLIC;NO_FORMAL_MODEL_SCORES_COMPUTED_AT_FREEZE","f84":{"all_pages_excluded_before_annotation_retention":True,"new_f84r_access":False},"claim_ceiling":"Page-level visible-feature association only; no semantic role, gloss, word, morpheme, POS, sound, language, plaintext, meaning, plant identity, or translation.","inputs":{p.name if p.parent==ROOT else str(p.relative_to(ROOT)):sha(p)for p in(METHOD,ARCH,ANNOT,ROOT/"gdt031_result.json",ROOT/"gdt033_result.json",ROOT/"gdt016_group_state_inventory.tsv")},"implementation":{Path(__file__).name:sha(Path(__file__))},"outputs":{INVENTORY.name:sha(INVENTORY)}}
prediction["prediction_content_sha256"]=csha(prediction);PREDICTION.write_text(json.dumps(prediction,indent=2,sort_keys=True)+"\n",encoding="utf8")
print(json.dumps({"status":prediction["status"],"panel":prediction["panel"],"counts":counts,"primary":primary,"cross":cross},sort_keys=True))
