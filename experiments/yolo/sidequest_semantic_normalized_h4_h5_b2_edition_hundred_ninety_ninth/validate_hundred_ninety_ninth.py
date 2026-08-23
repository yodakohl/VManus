#!/usr/bin/env python3
from __future__ import annotations
import csv,json
from pathlib import Path
OUT=Path(__file__).resolve().parent
def read(n):
    with (OUT/n).open(encoding="utf-8",newline="") as h:return list(csv.DictReader(h,delimiter="\t"))
def main():
    e=read("HUNDRED_NINETY_NINTH_107_EVENT_NORMALIZED_INTERLINEAR.tsv");f=read("HUNDRED_NINETY_NINTH_37_FIELD_NORMALIZED_EDITION.tsv");s=read("HUNDRED_NINETY_NINTH_32_STATEMENT_REVISED_EDITION.tsv");z=json.loads((OUT/"BUILD_SUMMARY.json").read_text())
    c={"107_events":len(e)==107 and len({r["event_id"] for r in e})==107,"106_logical_tokens":z["logical_source_tokens"]==106,"single_carry_correction":sum(r["source_token_correction"]!="NONE" for r in s)==1 and next(r for r in s if r["statement_id"]=="B2-S005")["source_token_correction"]=="E180_E181_TWO_VISIBLE_ONE_LOGICAL_MEASURE","record_counts":sum(r["record_unit_id"]=="H4" for r in e)==18 and sum(r["record_unit_id"]=="H5" for r in e)==27 and sum(r["record_unit_id"]=="B2" for r in e)==62,"37_fields":len(f)==37 and len({r["field_id"] for r in f})==37,"32_statements":len(s)==32 and len({r["statement_id"] for r in s})==32,"event_accounting":sum(len(r["card_sequence"].split()) for r in f)==107,"all_normalized":all(r["normalized_master_form"] for r in e),"all_translated":all(r["revised_fluent_translation_de"] for r in s),"records_exact":{r["record_unit_id"] for r in e}=={"H4","H5","B2"},"sealed_absent":z["sealed_pages_accessed"] is False}
    result={"status":"PASS" if all(c.values()) else "FAIL","checks":c,"summary":z};(OUT/"VALIDATION.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n");print(json.dumps(result,ensure_ascii=False,indent=2));
    if result["status"]!="PASS":raise SystemExit(1)
if __name__=="__main__":main()
