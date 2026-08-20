#!/usr/bin/env python3
"""Validate immutable GDT373 bytes while allowing two named live-state advances."""
from __future__ import annotations
import hashlib,json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4]
BASE=ROOT/"experiments/yolo/gdt373_functional_operator_roadmap"
RESULT=BASE/"artifacts/gdt373_result.json"
HISTORICAL=BASE/"artifacts/gdt373_validation.json"
ALLOWED={"VOYNICH_ACTIVE_STATE.md","experiments/semantic_assumptions/ACTIVE_EXPERIMENT_LEDGER.tsv"}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
checks=[]
def ck(n,x):assert x,n;checks.append(n)
r=json.loads(RESULT.read_text());q=dict(r);h=q.pop("content_hash")
ck("content_hash",h==hashlib.sha256(json.dumps(q,sort_keys=True,separators=(",",":")).encode()).hexdigest())
for rel,digest in r["inputs"].items():
 path=ROOT/rel
 if rel in ALLOWED:ck("advanced_live_input:"+rel,path.is_file() and sha(path)!=digest)
 else:ck("immutable_input:"+rel,sha(path)==digest)
for rel,digest in r["outputs"].items():ck("output:"+rel,sha(ROOT/rel)==digest)
for rel,digest in r["implementation"].items():ck("implementation:"+rel,sha(ROOT/rel)==digest)
old=json.loads(HISTORICAL.read_text());ck("historical_validation",old["status"]=="PASS")
ck("status",r["status"]=="FUNCTIONAL_OPERATOR_HYPOTHESES_REGISTERED_BEFORE_SEARCH")
ck("no_f84",r["f84_accessed"] is False)
print(f"ADMINISTRATIVE_MANIFEST_PASS {len(checks)}/{len(checks)}")
