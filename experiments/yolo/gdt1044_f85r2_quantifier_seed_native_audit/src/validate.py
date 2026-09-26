#!/usr/bin/env python3
"""Validate fixed scope, receipts and complete records, not visual truth."""
from pathlib import Path
import hashlib,json,sys
B=Path(__file__).resolve().parents[1]
ROOT=B.parents[2]
sys.path.insert(0,str(B/"src"))
from run import collect
checks=[]
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def check(name,ok):
    if not ok: raise AssertionError(name)
    checks.append(name)
for lock in ["src/PREREG_LOCK.json","artifacts/ROOT_FREEZE.json","artifacts/B_FREEZE.json"]:
    j=json.loads((B/lock).read_text())
    for p,h in j["files"].items():
        source=ROOT/p if p.startswith("experiments/") else B/p
        check(lock+":"+p,sha(source)==(h["sha256"] if isinstance(h,dict) else h))
rows=json.loads((B/"src/REGISTERED_GROUPS.json").read_text())
check("39 registered groups across three readers",len(rows)==39)
check("exact two loci",{r["locus"] for r in rows}=={"f85r2.2","f85r2.20"})
expected={("f85r2.2",i) for i in range(1,6)}|{("f85r2.20",i) for i in range(1,9)}
for name in ["ROOT","B"]:
    j=json.loads((B/f"artifacts/OBSERVER_{name}.json").read_text())
    found=[(g["locus"],g["position"]) for g in j["groups"]]
    check(name+"13 unique complete positions",len(found)==13 and set(found)==expected)
for receipt in ["IMAGE_RECEIPTS.json","W_COMPLETE_RECEIPT.json"]:
    j=json.loads((B/"artifacts"/receipt).read_text())
    for r in j["images"]:
        x,y,w,h=r["rect"]
        check(r["block"]+"within existing admitted rectangle",x>=0 and y>=0 and x+w<=3000 and y+h<=3890)
        expected_url="https://collections.library.yale.edu/iiif/2/1006229/"+",".join(map(str,r["rect"]))+"/full/"+str(r["rotation"])+"/default.jpg"
        check(r["block"]+"exact IIIF receipt",r["url"]==expected_url)
        p=B/r["path"]
        check(r["block"]+"cached pixels hash",p.is_file() and sha(p)==r["sha256"] and p.stat().st_size==r["bytes"])
check("result inventory reproduces",json.loads((B/"artifacts/RESULT.json").read_text())==collect())
m=json.loads((B/"experiment.json").read_text())
check("both sealed selectors retained",m["sealed_data"]=={"f84":"FORBIDDEN","f84r":"FORBIDDEN"})
out={"status":"PASS","scope":"Hash, rectangle, inventory and frozen-record integrity only; not visual judgment or meaning truth","checks":checks}
(B/"artifacts/VALIDATION.json").write_text(json.dumps(out,indent=2)+"\n")
print(json.dumps(out,indent=2))
