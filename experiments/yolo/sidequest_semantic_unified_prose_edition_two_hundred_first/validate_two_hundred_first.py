#!/usr/bin/env python3
from __future__ import annotations
import csv,json
from pathlib import Path
OUT=Path(__file__).resolve().parent
def read(n):
    with (OUT/n).open(encoding="utf-8",newline="") as h:return list(csv.DictReader(h,delimiter="\t"))
def main():
    e=read("TWO_HUNDRED_FIRST_381_EVENT_CURRENT_EDITION.tsv");f=read("TWO_HUNDRED_FIRST_135_FIELD_CURRENT_EDITION.tsv");s=read("TWO_HUNDRED_FIRST_116_STATEMENT_CURRENT_EDITION.tsv");d=read("TWO_HUNDRED_FIRST_173_CARD_CURRENT_DICTIONARY.tsv");r=read("TWO_HUNDRED_FIRST_11_RECORD_CURRENT_EDITION.tsv");z=json.loads((OUT/"BUILD_SUMMARY.json").read_text());c={"381_events":len(e)==381 and [int(x["event_id"][1:]) for x in e]==list(range(1,382)),"380_logical":z["logical_source_tokens"]==380 and sum(x["source_token_correction"]!="NONE" for x in s)==1,"135_fields":len(f)==135 and [int(x["field_id"][1:]) for x in f]==list(range(1,136)),"116_statements":len(s)==116 and len({x["statement_id"] for x in s})==116,"173_cards":len(d)==173 and len({x["master_card_id"] for x in d})==173,"230_surfaces":sum(int(x["surface_count"]) for x in d)==230,"151_productive_22_whole":sum(x["component_class"]=="PRODUCTIVE_COMPOSITION" for x in d)==151 and sum(x["component_class"]=="MEMORIZED_WHOLE_CARD" for x in d)==22,"353_productive_28_whole_events":z["productive_events"]==353 and z["memorized_events"]==28,"11_records":len(r)==11 and sum(int(x["events"]) for x in r)==381 and sum(int(x["fields"]) for x in r)==135 and sum(int(x["statements"]) for x in r)==116,"all_normalized":all(x["normalized_master_form"] for x in e),"all_translated":all(x["revised_fluent_translation_de"] for x in s),"sealed_absent":z["sealed_pages_accessed"] is False};result={"status":"PASS" if all(c.values()) else "FAIL","checks":c,"summary":z};(OUT/"VALIDATION.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n");print(json.dumps(result,ensure_ascii=False,indent=2));
    if result["status"]!="PASS":raise SystemExit(1)
if __name__=="__main__":main()
