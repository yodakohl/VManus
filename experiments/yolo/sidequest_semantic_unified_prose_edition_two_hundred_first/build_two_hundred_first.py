#!/usr/bin/env python3
from __future__ import annotations
import csv,hashlib,json
from collections import Counter,defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent
R197=ROOT/"experiments/yolo/sidequest_semantic_normalized_h3_b3_edition_hundred_ninety_seventh"
R198=ROOT/"experiments/yolo/sidequest_semantic_normalized_h1_h2_b1_edition_hundred_ninety_eighth"
R199=ROOT/"experiments/yolo/sidequest_semantic_normalized_h4_h5_b2_edition_hundred_ninety_ninth"
R200=ROOT/"experiments/yolo/sidequest_semantic_normalized_b4_b5_b6_edition_two_hundredth"
DICTIONARY=ROOT/"experiments/yolo/sidequest_semantic_ten_page_master_edition_hundred_seventy_fifth/HUNDRED_SEVENTY_FIFTH_173_CARD_DICTIONARY.tsv"
COMPONENTS=ROOT/"experiments/yolo/sidequest_semantic_bound_carrier_closure/CLOSED_173_CARD_DICTIONARY.tsv"
NORMALIZATION=ROOT/"experiments/yolo/sidequest_semantic_reader_normalization_hundred_ninety_sixth/HUNDRED_NINETY_SIXTH_230_SURFACE_NORMALIZATION.tsv"
EVENT_FILES=[R197/"HUNDRED_NINETY_SEVENTH_103_EVENT_NORMALIZED_INTERLINEAR.tsv",R198/"HUNDRED_NINETY_EIGHTH_104_EVENT_NORMALIZED_INTERLINEAR.tsv",R199/"HUNDRED_NINETY_NINTH_107_EVENT_NORMALIZED_INTERLINEAR.tsv",R200/"TWO_HUNDREDTH_67_EVENT_NORMALIZED_INTERLINEAR.tsv"]
FIELD_FILES=[R197/"HUNDRED_NINETY_SEVENTH_42_FIELD_NORMALIZED_EDITION.tsv",R198/"HUNDRED_NINETY_EIGHTH_29_FIELD_NORMALIZED_EDITION.tsv",R199/"HUNDRED_NINETY_NINTH_37_FIELD_NORMALIZED_EDITION.tsv",R200/"TWO_HUNDREDTH_27_FIELD_NORMALIZED_EDITION.tsv"]
STATEMENT_FILES=[R197/"HUNDRED_NINETY_SEVENTH_38_STATEMENT_REVISED_EDITION.tsv",R198/"HUNDRED_NINETY_EIGHTH_26_STATEMENT_REVISED_EDITION.tsv",R199/"HUNDRED_NINETY_NINTH_32_STATEMENT_REVISED_EDITION.tsv",R200/"TWO_HUNDREDTH_20_STATEMENT_REVISED_EDITION.tsv"]
ORDER={"H1":0,"H2":1,"H3":2,"H4":3,"H5":4,"B1":5,"B2":6,"B3":7,"B4":8,"B5":9,"B6":10}
def read(p):
    with p.open(encoding="utf-8",newline="") as h:return list(csv.DictReader(h,delimiter="\t"))
def write(p,r):
    with p.open("w",encoding="utf-8",newline="") as h:w=csv.DictWriter(h,fieldnames=list(r[0]),delimiter="\t",lineterminator="\n",extrasaction="ignore");w.writeheader();w.writerows(r)
def main():
    events=sorted([r for p in EVENT_FILES for r in read(p)],key=lambda r:int(r["event_id"][1:]));fields=sorted([r for p in FIELD_FILES for r in read(p)],key=lambda r:int(r["field_id"][1:]));statements=[r for p in STATEMENT_FILES for r in read(p)];statements.sort(key=lambda r:(ORDER[r["record_unit_id"]],int(r["statement_id"].split("S")[1])))
    for r in statements:r["source_token_correction"]=r.get("source_token_correction","NONE")
    write(OUT/"TWO_HUNDRED_FIRST_381_EVENT_CURRENT_EDITION.tsv",events);write(OUT/"TWO_HUNDRED_FIRST_135_FIELD_CURRENT_EDITION.tsv",fields);write(OUT/"TWO_HUNDRED_FIRST_116_STATEMENT_CURRENT_EDITION.tsv",statements)
    base=read(DICTIONARY);comp={r["surface_family"]:r for r in read(COMPONENTS)};norm=read(NORMALIZATION);rules=defaultdict(set)
    for r in norm:
        if r["normalization_rule"]!="MASTER_FORM":rules[r["master_card_id"]].add(r["normalization_rule"])
    dr=[]
    for r in base:
        c=comp[r["registered_surfaces"]];formula=c["closed_parse"].replace("Y_OPEN","Y_CURRENT_ITEM")
        dr.append({"master_card_id":r["master_card_id"],"master_form":r["master_form"],"registered_surfaces":r["registered_surfaces"],"surface_count":len(r["registered_surfaces"].split("|")),"current_value_de":r["portable_card_value_de"],"syntactic_type":r["syntactic_type"],"event_count":r["event_count"],"records":r["records"],"component_class":c["closed_architecture"],"component_formula":formula,"component_reading_snapshot_de":c["closed_reading_de"],"teaching_symbol":c["teaching_symbol"],"reader_normalization_families":"|".join(sorted(rules[r["master_card_id"]])) or "MASTER_ONLY"})
    write(OUT/"TWO_HUNDRED_FIRST_173_CARD_CURRENT_DICTIONARY.tsv",dr)
    rr=[]
    for rec in ORDER:
        ss=[r for r in statements if r["record_unit_id"]==rec];ee=[r for r in events if r["record_unit_id"]==rec];ff=[r for r in fields if r["record_unit_id"]==rec]
        rr.append({"record_unit_id":rec,"page":ee[0]["page"],"events":len(ee),"logical_source_tokens":len(ee)-sum(r["source_token_correction"]!="NONE" for r in ss),"fields":len(ff),"statements":len(ss),"visible_owner_sequence":"|".join(dict.fromkeys(r["visible_owner"] for r in ss)),"fluent_record_reading_de":" ".join(r["revised_fluent_translation_de"] for r in ss)})
    write(OUT/"TWO_HUNDRED_FIRST_11_RECORD_CURRENT_EDITION.tsv",rr)
    lines=["# Aktuelle normalisierte Prosaausgabe",""]
    for rec in ORDER:
        row=next(x for x in rr if x["record_unit_id"]==rec);lines.extend([f"## {rec} / {row['page']}","",f"**Besitzer:** {row['visible_owner_sequence']}",""])
        for s in [x for x in statements if x["record_unit_id"]==rec]:lines.extend([f"- **{s['statement_id']}** `{s['visible_sequence']}`",f"  - Normalisiert: `{s['normalized_sequence']}`",f"  - {s['revised_fluent_translation_de']}"])
        lines.append("")
    (OUT/"TWO_HUNDRED_FIRST_COMPLETE_PROSE_READER.md").write_text("\n".join(lines),encoding="utf-8")
    event_class=Counter(next(x for x in dr if x["master_card_id"]==r["master_card_id"])["component_class"] for r in events)
    summary={"source_hashes":{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in EVENT_FILES+FIELD_FILES+STATEMENT_FILES+[DICTIONARY,COMPONENTS,NORMALIZATION]},"events":len(events),"logical_source_tokens":len(events)-1,"fields":len(fields),"statements":len(statements),"records":len(rr),"cards":len(dr),"registered_surfaces":sum(int(r["surface_count"]) for r in dr),"productive_card_types":sum(r["component_class"]=="PRODUCTIVE_COMPOSITION" for r in dr),"memorized_card_types":sum(r["component_class"]=="MEMORIZED_WHOLE_CARD" for r in dr),"productive_events":event_class["PRODUCTIVE_COMPOSITION"],"memorized_events":event_class["MEMORIZED_WHOLE_CARD"],"all_events_normalized":all(r["normalized_master_form"] for r in events),"all_statements_translated":all(r["revised_fluent_translation_de"] for r in statements),"sealed_pages_accessed":False}
    (OUT/"BUILD_SUMMARY.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
if __name__=="__main__":main()
