#!/usr/bin/env python3
"""Integrity and source-capacity validator for the GDT271 freeze."""
import csv,hashlib,json
from collections import Counter,defaultdict
from pathlib import Path
R=Path(__file__).resolve().parent;SRC="gdt127_q20_field_inventory.tsv";PRED="gdt271_frozen_prediction.json";METHOD="GDT271_Q20_Q_OUTER_LAYER_TRANSFER_METHOD.md";FREEZER="freeze_gdt271_q20_q_outer_layer_transfer.py"
def sha(n):return hashlib.sha256((R/n).read_bytes()).hexdigest()
def main():
 checks=[]
 def ck(n,v):assert v,n;checks.append(n)
 with (R/SRC).open(encoding="utf-8",newline="") as h:rows=list(csv.DictReader(h,delimiter="\t"))
 ck("source_nonempty",bool(rows));ck("source_no_f84",all(not x["page"].startswith("f84") for x in rows));pred=json.loads((R/PRED).read_text());stored=pred.pop("content_hash");ck("content_hash",stored==hashlib.sha256(json.dumps(pred,sort_keys=True,separators=(",",":")).encode()).hexdigest());ck("source_hash",pred["inputs"][SRC]==sha(SRC));ck("method_hash",pred["documents"][METHOD]==sha(METHOD));ck("freezer_hash",pred["implementation"][FREEZER]==sha(FREEZER));ck("other_input_hashes",all(sha(n)==v for n,v in pred["inputs"].items()));ck("freeze_status",pred["freeze_status"]=="FROZEN_BEFORE_GDT271_CONDITIONAL_ASSOCIATION_SCORING");ck("direction",pred["prediction"].startswith("q has positive EARLY"));ck("primary_gate",pred["primary_gate"]=={"conditional_score":"POSITIVE","page_sign_max_three_p_max":0.05,"positive_pages_min":9});ck("readings",pred["primary_reading"]=="ZL3b" and pred["alternate_readings"]==["IT2a","RF1b"]);ck("capacity_primary",pred["capacity"]["ZL3b"]["variants"]["PAGE_HOST_PAGE_OTHER_COMPILER"]=={"all_strata":2369,"mobile_hosts":33,"mobile_occurrences":668,"mobile_pages":13,"movable_strata":128});ck("selected_records",all(pred["capacity"][ed]["selected_records"]==162 for ed in ("ZL3b","IT2a","RF1b")));ck("f84_flags",not pred["f84r"]["new_access"] and not pred["f84r"]["used"] and not pred["f84r"]["scored"]);ck("semantic_zero",pred["semantic_assignments"]==0)
 val={"experiment":"GDT271_Q20_Q_OUTER_LAYER_TRANSFER_FREEZE","status":"PASS","checks_passed":len(checks),"checks":checks,"prediction_sha256":sha(PRED),"validator_sha256":sha(Path(__file__).name),"association_scored":False,"f84r_accessed":False};(R/"gdt271_freeze_validation.json").write_text(json.dumps(val,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":"PASS","checks":len(checks)},sort_keys=True))
if __name__=="__main__":main()
