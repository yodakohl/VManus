#!/usr/bin/env python3
from __future__ import annotations
import csv, json
from pathlib import Path
OUT = Path(__file__).resolve().parent
def read(name: str):
    with (OUT / name).open(encoding="utf-8", newline="") as handle: return list(csv.DictReader(handle, delimiter="\t"))
def main():
    events=read("HUNDRED_NINETY_EIGHTH_104_EVENT_NORMALIZED_INTERLINEAR.tsv"); fields=read("HUNDRED_NINETY_EIGHTH_29_FIELD_NORMALIZED_EDITION.tsv"); statements=read("HUNDRED_NINETY_EIGHTH_26_STATEMENT_REVISED_EDITION.tsv"); summary=json.loads((OUT/"BUILD_SUMMARY.json").read_text())
    checks={
        "104_events":len(events)==104 and len({r["event_id"] for r in events})==104,
        "record_counts":sum(r["record_unit_id"]=="H1" for r in events)==14 and sum(r["record_unit_id"]=="H2" for r in events)==24 and sum(r["record_unit_id"]=="B1" for r in events)==66,
        "29_fields":len(fields)==29 and len({r["field_id"] for r in fields})==29,
        "26_statements":len(statements)==26 and len({r["statement_id"] for r in statements})==26,
        "event_accounting":sum(len(r["card_sequence"].split()) for r in fields)==104,
        "all_normalized":all(r["normalized_master_form"] for r in events), "all_translated":all(r["revised_fluent_translation_de"] for r in statements),
        "records_exact":{r["record_unit_id"] for r in events}=={"H1","H2","B1"}, "sealed_absent":summary["sealed_pages_accessed"] is False,
    }
    result={"status":"PASS" if all(checks.values()) else "FAIL","checks":checks,"summary":summary};(OUT/"VALIDATION.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n");print(json.dumps(result,ensure_ascii=False,indent=2));
    if result["status"]!="PASS":raise SystemExit(1)
if __name__=="__main__":main()
