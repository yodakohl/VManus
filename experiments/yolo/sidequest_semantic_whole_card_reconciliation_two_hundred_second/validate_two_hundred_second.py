#!/usr/bin/env python3
from __future__ import annotations
import csv,json
from pathlib import Path
OUT=Path(__file__).resolve().parent
def read(n):
    with (OUT/n).open(encoding="utf-8",newline="") as h:return list(csv.DictReader(h,delimiter="\t"))
def main():
    q=read("TWO_HUNDRED_SECOND_22_WHOLE_CARD_DECISIONS.tsv");d=read("TWO_HUNDRED_SECOND_173_CARD_RECONCILED_DICTIONARY.tsv");e=read("TWO_HUNDRED_SECOND_381_EVENT_RECONCILED_EDITION.tsv");s=read("TWO_HUNDRED_SECOND_116_STATEMENT_RECONCILED_EDITION.tsv");a=read("TWO_HUNDRED_SECOND_AFFECTED_STATEMENTS.tsv");z=json.loads((OUT/"BUILD_SUMMARY.json").read_text());sel={r["master_card_id"]:r["selected_value_de"] for r in q};c={"22_decisions":len(q)==22 and len(sel)==22,"28_occurrences":sum(int(r["occurrences"]) for r in q)==28,"11_7_4_split":z["decision_distribution"]=={"KEEP_CURRENT":11,"RESTORE_LEGACY":7,"REFINE":4},"173_cards":len(d)==173,"381_events":len(e)==381,"116_statements":len(s)==116,"event_values_match":all(r["master_card_id"] not in sel or r["portable_value_de"]==sel[r["master_card_id"]] for r in e),"dictionary_values_match":all(r["master_card_id"] not in sel or r["current_value_de"]==sel[r["master_card_id"]] for r in d),"nine_fluent_revisions":sum(r["fluent_changed"]=="YES" for r in a)==9,"all_values_short":all(0<len(r["selected_value_de"].split())<=4 for r in q),"sealed_absent":z["sealed_pages_accessed"] is False};result={"status":"PASS" if all(c.values()) else "FAIL","checks":c,"summary":z};(OUT/"VALIDATION.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n");print(json.dumps(result,ensure_ascii=False,indent=2));
    if result["status"]!="PASS":raise SystemExit(1)
if __name__=="__main__":main()
