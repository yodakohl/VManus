#!/usr/bin/env python3
"""Independent arithmetic validator for GDT353."""
from __future__ import annotations

import csv
import hashlib
import itertools
import json
import sys
from collections import defaultdict
from difflib import SequenceMatcher
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from tools.vmanus_experiment import GuardedTSV  # noqa: E402
EXP = ROOT / "experiments/yolo/gdt353_f68_nested_diagram_alignment"; ART = EXP / "artifacts"
A = [f"f68v1.{i}" for i in range(3, 11)]
B = ["f68v2.18", "f68v2.7", "f68v2.9", "f68v2.10", "f68v2.12", "f68v2.13", "f68v2.15", "f68v2.16"]

def read(path):
    with path.open(encoding="utf-8", newline="") as f: return list(csv.DictReader(f, delimiter="\t"))
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def stable(value): return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode()
def tri(s):
    s = "^" + s + "$"; return {s[i:i+3] for i in range(len(s)-2)}
def sim(a,b,m):
    if m == "EDIT": return SequenceMatcher(None,a,b).ratio()
    x,y=tri(a),tri(b); return len(x&y)/len(x|y) if x|y else 1.0
def dihedral(order):
    for rev in (0,1):
        q=list(reversed(order)) if rev else list(order)
        for k in range(8): yield rev,k,tuple(q[k:]+q[:k])

def main():
    result=json.loads((ART/"gdt353_result.json").read_text())
    scores=read(ART/"gdt353_scores.tsv"); arrays=read(ART/"gdt353_arrays.tsv")
    checks=[]
    def ck(n,o,d=""):checks.append({"name":n,"pass":bool(o),"detail":d})
    ck("array_rows",len(arrays)==16)
    ck("array_a_order",[r["locus"] for r in arrays if r["array"]=="F68V1_E1"]==A)
    ck("array_b_order",[r["locus"] for r in arrays if r["array"]=="F68V2_E1"]==B)
    guard=GuardedTSV(ROOT/"experiments/semantic_assumptions/results/source_sta_group_alignment.tsv",selector_column="locus",allowed_values=set(A+B))
    rows=list(guard); by=defaultdict(lambda:defaultdict(list))
    for r in rows:by[r["edition"]][r["locus"]].append(r)
    for row in [r for r in scores if r["analysis_role"]=="PREDECLARED"]:
        field="nearest_basic_eva_primary" if row["representation"]=="DIPLOMATIC_SURFACE" else "primary_sta_families"
        left=["|".join(x[field].replace(" ","") for x in by[row["edition"]][l]) for l in A]
        right=["|".join(x[field].replace(" ","") for x in by[row["edition"]][l]) for l in B]
        matrix=[[sim(x,y,row["metric"]) for y in right] for x in left]
        def sc(order):return sum(matrix[i][order[i]] for i in range(8))/8
        direct=sc(tuple(range(8))); best=max((sc(o),rv,k,o) for rv,k,o in dihedral(tuple(range(8))))
        null=[]
        for perm in itertools.permutations(range(8)):null.append(max(sc(o) for _,_,o in dihedral(perm)))
        p=sum(x>=best[0]-1e-15 for x in null)/len(null)
        tag=row["edition"]+":"+row["representation"]+":"+row["metric"]
        ck("direct:"+tag,abs(float(row["direct_score"])-direct)<1e-11)
        ck("best:"+tag,abs(float(row["best_score"])-best[0])<1e-11 and int(row["best_reflected"])==best[1] and int(row["best_rotation"])==best[2])
        ck("p:"+tag,abs(float(row["inclusive_p"])-p)<1e-11)
    ck("none_pass",not any(int(r["passes_0_05"]) for r in scores))
    ck("status",result["status"]=="NO_ORDERED_FORMAL_SUPPORT_FOR_F68V1_V2_NESTING")
    ck("no_f84",all("f84" not in "\t".join(r.values()).lower() for r in arrays+scores))
    ck("guard_skipped_f84",guard.stats.skipped_forbidden>0)
    for rel,h in result["outputs"].items():ck("output_hash:"+rel,sha(ROOT/rel)==h)
    for rel,h in result["documents"].items():ck("document_hash:"+rel,sha(ROOT/rel)==h)
    for rel,h in result["implementation"].items():ck("implementation_hash:"+rel,sha(ROOT/rel)==h)
    content=dict(result); claimed=content.pop("result_content_sha256");ck("content_hash",hashlib.sha256(stable(content)).hexdigest()==claimed)
    out={"experiment":"GDT353","schema":"GDT353_VALIDATION_V1","status":"PASS" if all(x["pass"] for x in checks) else "FAIL","scope":"Independent guarded reconstruction of all predeclared string/family circular scores and exact nulls, plus accounting and hashes; post-hoc length sensitivity is integrity-checked only.","checks_passed":sum(x["pass"] for x in checks),"checks_failed":sum(not x["pass"] for x in checks),"checks":checks,"result_sha256":sha(ART/"gdt353_result.json"),"implementation_sha256":sha(Path(__file__))}
    (ART/"gdt353_validation.json").write_bytes(stable(out));print(out["status"],out["checks_passed"],out["checks_failed"])
    if out["status"]!="PASS":raise SystemExit(1)
if __name__=="__main__":main()
