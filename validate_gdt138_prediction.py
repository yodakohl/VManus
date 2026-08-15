#!/usr/bin/env python3
"""Validate GDT138 pre-score positional freeze."""
import csv,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent;P=ROOT/"gdt138_prediction.json";W=ROOT/"gdt138_line_window_inventory.tsv";OUT=ROOT/"gdt138_prediction_validation.json"
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
p=json.loads(P.read_text());
with W.open(encoding="utf8",newline="")as h:rows=list(csv.DictReader(h,delimiter="\t"))
checks=[]
def check(n,v):checks.append({"check":n,"pass":bool(v)});assert v,n
check("status",p["status"]=="FROZEN_POST_GDT137_POSITIONAL_ABLATION_BEFORE_WINDOW_SCORING");check("panel",len(rows)==126 and len({r["physical_folio"]for r in rows})==62 and len({r["page"]for r in rows})==126);check("windows",p["windows"]==["FIRST_LINE","BODY_AFTER_FIRST","LAST_LINE","ALL_PAGE"]and p["representations"]==["PAGE_HOST_IDENTITY","PAGE_HOST_CHAR3","RAW_CHAR3"]);check("positive_counts",all(int(r["source_lines"])>=2 and int(r["first_groups"])>=1 and int(r["body_after_first_groups"])>=1 and int(r["last_groups"])>=1 for r in rows));check("f84",not any(r["page"].startswith("f84")or r["first_locus"].startswith("f84")or r["last_locus"].startswith("f84")for r in rows));check("hashes",all(sha(ROOT/n)==d for n,d in p["inputs"].items())and all(sha(ROOT/n)==d for n,d in p["implementation"].items())and all(sha(ROOT/n)==d for n,d in p["outputs"].items()));x=dict(p);d=x.pop("prediction_content_sha256");check("content",csha(x)==d);v={"schema":"GDT138_PREDICTION_VALIDATION_V1","status":"PASS_PREWINDOW_SCORE_FREEZE","checks":len(checks),"passed":sum(x["pass"]for x in checks),"prediction_sha256":sha(P),"validator_sha256":sha(Path(__file__)),"check_rows":checks};OUT.write_text(json.dumps(v,indent=2,sort_keys=True)+"\n",encoding="utf8");print(json.dumps({"status":v["status"],"checks":v["checks"]},sort_keys=True))
