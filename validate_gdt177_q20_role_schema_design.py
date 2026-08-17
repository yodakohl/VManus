#!/usr/bin/env python3
from __future__ import annotations
import csv, hashlib, json
from pathlib import Path

def sha(p: str) -> str: return hashlib.sha256(Path(p).read_bytes()).hexdigest()
d=json.loads(Path("gdt177_design.json").read_text())
checks=[]
checks.append(d["status"]=="FROZEN_BEFORE_UNUSED_Q20_FEATURE_SCORING")
checks.append(d["permutation_worlds"]==4096 and d["host_update_pseudocount"]==4)
checks.append(all(sha(p)==h for p,h in d["inputs"].items()))
with Path("gdt127_q20_field_inventory.tsv").open() as h:
    fields=list(csv.DictReader(h,delimiter="\t"))
checks.append(len(fields)==4443 and all(not r["page"].startswith("f84") and not r["locus"].startswith("f84") for r in fields))
with Path("gdt176_q20_role_like_projection.tsv").open() as h:
    proj=list(csv.DictReader(h,delimiter="\t"))
checks.append(len(proj)==4443 and all(not r["page"].startswith("f84") for r in proj))
clean=dict(d); expected=clean.pop("content_hash")
checks.append(hashlib.sha256(json.dumps(clean,sort_keys=True,separators=(",",":")).encode()).hexdigest()==expected)
checks.append(not d["f84r_accessed"] and "translation" in d["claim_ceiling"])
v={"experiment":d["experiment"],"status":"PASS" if all(checks) else "FAIL","checks_passed":sum(checks),"checks_total":len(checks),"design_sha256":sha("gdt177_design.json")}
Path("gdt177_design_validation.json").write_text(json.dumps(v,indent=2,sort_keys=True)+"\n")
print(v["status"],f"{v['checks_passed']}/{v['checks_total']}")
if not all(checks): raise SystemExit(1)
