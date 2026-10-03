#!/usr/bin/env python3
"""Validate complete census and fixed inputs, not native-vision truth."""
from pathlib import Path
import json, hashlib, csv
from run import BASE,build
ROOT=BASE.parents[2]
rows,result=build()
assert json.loads((BASE/"artifacts/RESULT.json").read_text())==result
with (BASE/"artifacts/CASES.tsv").open() as f:
    observed=list(csv.DictReader(f,delimiter="\t"))
assert observed==[{k:str(v) for k,v in r.items()} for r in rows]
m=json.loads((BASE/"experiment.json").read_text())
for b in m["inputs"]:
    assert hashlib.sha256((ROOT/b["path"]).read_bytes()).hexdigest()==b["sha256"],b["path"]
assert m["sealed_data"]=={"f84":"FORBIDDEN","f84r":"FORBIDDEN"}
s=json.loads((BASE/"artifacts/SOURCE.json").read_text())
assert s["sha256"]=="2bf46dbeaaaab4a97075f46f503582da0eef2b352eb92277d7a3b6db1a3a0b8c"
v=dict(status="PASS",scope="8-case completeness, two manual inventories, deterministic summary, input hashes and seals; no palaeographic or semantic validation")
(BASE/"artifacts/VALIDATION.json").write_text(json.dumps(v,indent=2)+"\n")
print(json.dumps(v))
