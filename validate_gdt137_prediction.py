#!/usr/bin/env python3
"""Validate the GDT137 pre-score page/feature freeze."""
import csv,hashlib,json
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parent
P=ROOT/"gdt137_prediction.json";I=ROOT/"gdt137_herbal_visual_feature_inventory.tsv";OUT=ROOT/"gdt137_prediction_validation.json"
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
with I.open(encoding="utf8",newline="")as h:rows=list(csv.DictReader(h,delimiter="\t"))
p=json.loads(P.read_text());checks=[]
def check(n,v):checks.append({"check":n,"pass":bool(v)});assert v,n
check("status",p["status"]=="FROZEN_ARCHIVE_WIDE_PAGE_TEST_BEFORE_FORMAL_SCORING")
check("panel",len(rows)==127 and len({r["physical_folio"]for r in rows})==63 and Counter(r["currier"]for r in rows)==Counter({"A":95,"B":32}))
check("unique_pages",len({r["page"]for r in rows})==127)
check("f84",not any(r["page"].startswith("f84")for r in rows))
counts={name:sum(int(r[name])for r in rows)for name in p["features"]}
check("counts",counts==p["feature_positive_pages"])
check("primary",p["primary_capacity_features"]==[name for name in p["features"]if 8<=counts[name]<=119])
check("cross",p["cross_currier_features"]==[name for name in p["features"]if all(sum(int(r[name])for r in rows if r["currier"]==c)>=2 for c in("A","B"))])
check("representations",p["representations"]==["PAGE_HOST_IDENTITY","PAGE_HOST_CHAR3","RAW_CHAR3","COMPILER_SIGNATURE"])
check("hashes",all(sha(ROOT/name)==digest for name,digest in p["inputs"].items())and all(sha(ROOT/name)==digest for name,digest in p["implementation"].items())and all(sha(ROOT/name)==digest for name,digest in p["outputs"].items()))
content=dict(p);digest=content.pop("prediction_content_sha256");check("content",csha(content)==digest)
v={"schema":"GDT137_PREDICTION_VALIDATION_V1","status":"PASS_PRESCORE_FREEZE","checks":len(checks),"passed":sum(x["pass"]for x in checks),"prediction_sha256":sha(P),"validator_sha256":sha(Path(__file__)),"check_rows":checks}
OUT.write_text(json.dumps(v,indent=2,sort_keys=True)+"\n",encoding="utf8")
print(json.dumps({"status":v["status"],"checks":v["checks"]},sort_keys=True))
