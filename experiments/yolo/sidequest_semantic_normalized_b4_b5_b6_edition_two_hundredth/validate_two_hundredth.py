#!/usr/bin/env python3
from __future__ import annotations
import csv,json
from pathlib import Path
OUT=Path(__file__).resolve().parent
def read(n):
    with (OUT/n).open(encoding="utf-8",newline="") as h:return list(csv.DictReader(h,delimiter="\t"))
def main():
    e=read("TWO_HUNDREDTH_67_EVENT_NORMALIZED_INTERLINEAR.tsv");f=read("TWO_HUNDREDTH_27_FIELD_NORMALIZED_EDITION.tsv");s=read("TWO_HUNDREDTH_20_STATEMENT_REVISED_EDITION.tsv");z=json.loads((OUT/"BUILD_SUMMARY.json").read_text());c={"67_events":len(e)==67 and len({r["event_id"] for r in e})==67,"record_counts":sum(r["record_unit_id"]=="B4" for r in e)==47 and sum(r["record_unit_id"]=="B5" for r in e)==11 and sum(r["record_unit_id"]=="B6" for r in e)==9,"27_fields":len(f)==27 and len({r["field_id"] for r in f})==27,"20_statements":len(s)==20 and len({r["statement_id"] for r in s})==20,"event_accounting":sum(len(r["card_sequence"].split()) for r in f)==67,"all_normalized":all(r["normalized_master_form"] for r in e),"all_translated":all(r["revised_fluent_translation_de"] for r in s),"records_exact":{r["record_unit_id"] for r in e}=={"B4","B5","B6"},"sealed_absent":z["sealed_pages_accessed"] is False};result={"status":"PASS" if all(c.values()) else "FAIL","checks":c,"summary":z};(OUT/"VALIDATION.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n");print(json.dumps(result,ensure_ascii=False,indent=2));
    if result["status"]!="PASS":raise SystemExit(1)
if __name__=="__main__":main()
