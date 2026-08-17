#!/usr/bin/env python3
"""Integrity validator for the GDT272 density freeze."""
import csv,hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parent;PRED="gdt272_frozen_prediction.json";TABLE="gdt272_frozen_density_predictors.tsv";METHOD="GDT272_Q_DENSITY_MECHANISM_METHOD.md";FREEZER="freeze_gdt272_q_density_mechanism.py"
def sha(n):return hashlib.sha256((R/n).read_bytes()).hexdigest()
def main():
 checks=[]
 def ck(n,v):assert v,n;checks.append(n)
 with (R/TABLE).open(encoding="utf-8",newline="") as h:rows=list(csv.DictReader(h,delimiter="\t"));ck("thirteen_pages",len(rows)==13 and len({x["page"] for x in rows})==13);ck("no_f84",all(not x["page"].startswith("f84") for x in rows));ck("outcome_not_joined",all(x["outcome_access"]=="NOT_JOINED_AT_FREEZE" for x in rows));pred=json.loads((R/PRED).read_text());stored=pred.pop("content_hash");ck("content_hash",stored==hashlib.sha256(json.dumps(pred,sort_keys=True,separators=(",",":")).encode()).hexdigest());ck("table_hash",pred["outputs"][TABLE]==sha(TABLE));ck("inputs",all(sha(n)==v for n,v in pred["inputs"].items()));ck("method",pred["documents"][METHOD]==sha(METHOD));ck("freezer",pred["implementation"][FREEZER]==sha(FREEZER));ck("gate",pred["primary_gate"]=={"max_three_p_max":0.05,"pearson":"POSITIVE","positive_leave_one_page_min":11,"sign_agreement_min":9});ck("semantic_zero",pred["semantic_assignments"]==0);ck("f84_flags",not any(pred["f84r"].values()));val={"experiment":"GDT272_Q_DENSITY_MECHANISM_FREEZE","status":"PASS","checks_passed":len(checks),"checks":checks,"prediction_sha256":sha(PRED),"validator_sha256":sha(Path(__file__).name),"outcome_joined":False,"f84r_accessed":False};(R/"gdt272_freeze_validation.json").write_text(json.dumps(val,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":"PASS","checks":len(checks)},sort_keys=True))
if __name__=="__main__":main()
