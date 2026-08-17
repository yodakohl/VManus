#!/usr/bin/env python3
"""Independent retained-output and source-join checks for GDT177."""
from __future__ import annotations
import csv, hashlib, json, math
from collections import Counter, defaultdict
from pathlib import Path

def read(p):
    with Path(p).open(encoding="utf-8",newline="") as h:return list(csv.DictReader(h,delimiter="\t"))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def near(a,b,t=2e-7):return abs(a-b)<=t*max(1,abs(a),abs(b))
def mean(x):return sum(x)/len(x) if x else 0

def main():
    r=json.loads(Path("gdt177_result.json").read_text()); design=json.loads(Path("gdt177_design.json").read_text())
    inv=read("gdt177_field_inventory.tsv"); tests=read("gdt177_tests.tsv"); null=read("gdt177_null.tsv"); folds=read("gdt177_host_update_folds.tsv")
    source=read("gdt127_q20_field_inventory.tsv"); proj=read("gdt176_q20_role_like_projection.tsv")
    checks=[]
    checks.append(("status",r["status"]=="POSITION_LENGTH_ANALOGY_ONLY_NO_INDEPENDENT_Q20_ROLE_SUPPORT"))
    checks.append(("design",design["status"]=="FROZEN_BEFORE_UNUSED_Q20_FEATURE_SCORING" and design["permutation_worlds"]==4096))
    checks.append(("inventory",len(inv)==len(source)==len(proj)==4443 and len([x for x in inv if x["edition"]=="ZL3b"])==1483))
    checks.append(("no_f84",all(not x["page"].startswith("f84") and not x["field_id"].startswith("f84") for x in inv)))
    src={x["field_id"]:x for x in source}; pp={x["field_id"]:x for x in proj}
    checks.append(("exact_join",all(x["field_id"] in src and x["field_id"] in pp and x["abstract_role"]==pp[x["field_id"]]["supported_abstract_role_like"] for x in inv)))
    checks.append(("source_flags",all(int(x["ends_b3"])==int(src[x["field_id"]]["ends_b3"]) and int(x["ends_dy"])==int(src[x["field_id"]]["ends_dy"]) for x in inv)))
    zl=[x for x in inv if x["edition"]=="ZL3b"]
    final=[x for x in zl if x["is_record_final"]=="1" and x["abstract_role"]!="UNRESOLVED_EDGE_CLASS"]
    close=[x for x in final if x["abstract_role"]=="RECORD_CLOSER_LIKE"]; other=[x for x in final if x["abstract_role"]!="RECORD_CLOSER_LIKE"]
    b3=mean([int(x["ends_b3"]) for x in close])-mean([int(x["ends_b3"]) for x in other])
    dy=mean([int(x["ends_dy"]) for x in close])-mean([int(x["ends_dy"]) for x in other])
    pair=[x for x in zl if x["abstract_role"] in ("INSTRUCTION_CLAUSE_LIKE","SHORT_ARGUMENT_LIKE")]
    short=[x for x in pair if x["abstract_role"]=="SHORT_ARGUMENT_LIKE"]; instruction=[x for x in pair if x["abstract_role"]=="INSTRUCTION_CLAUSE_LIKE"]
    rec=mean([int(x["host_recurrent_other_2plus"]) for x in short])-mean([int(x["host_recurrent_other_2plus"]) for x in instruction])
    comp=mean([float(x["compiler_density"]) for x in instruction])-mean([float(x["compiler_density"]) for x in short])
    checks.append(("effects",near(b3,r["t1"]["b3_effect"]) and near(dy,r["t1"]["dy_effect"]) and near(rec,r["t2"]["effect"]) and near(comp,r["t3"]["effect"])))
    checks.append(("capacities",len(final)==170 and len(close)==121 and len(other)==49 and len(pair)==1323))
    bytest=defaultdict(list)
    for x in null:bytest[x["test_id"]].append(float(x["effect"]))
    checks.append(("null_worlds",set(bytest)=={"T1_FINAL_FIELD_B3","T2_CROSS_FOLIO_HOST_RECURRENCE","T3_COMPILER_STATE_DENSITY"} and all(len(v)==4096 for v in bytest.values())))
    primary={x["test_id"]:x for x in tests if x["edition"]=="ZL3b" and x["test_id"]!="T1_FINAL_FIELD_DY_SECONDARY"}
    effects={"T1_FINAL_FIELD_B3":b3,"T2_CROSS_FOLIO_HOST_RECURRENCE":rec,"T3_COMPILER_STATE_DENSITY":comp}
    checks.append(("local_p",all(near((1+sum(v>=effects[k]-6e-10 for v in bytest[k]))/4097,float(primary[k]["local_p"])) for k in effects)))
    checks.append(("host_fold_count",len(folds)==8 and {x["held_folio"] for x in folds}=={"f104","f105","f106","f107","f112","f113","f114","f115"}))
    checks.append(("host_totals",sum(int(x["n"]) for x in folds)==r["t4"]["n"] and sum(int(x["host_update_eligible"]) for x in folds)==r["t4"]["eligible"] and near(sum(float(x["gain_bits"]) for x in folds),r["t4"]["gain_bits"])))
    checks.append(("host_all_negative",r["t4"]["positive_folios"]==0 and all(float(x["gain_bits"])<0 for x in folds)))
    checks.append(("hashes",all(sha(p)==h for p,h in {**r["inputs"],**r["outputs"],**r["implementation"]}.items())))
    clean=dict(r); expected=clean.pop("content_hash"); checks.append(("content_hash",hashlib.sha256(json.dumps(clean,sort_keys=True,separators=(",",":")).encode()).hexdigest()==expected))
    checks.append(("claim",not r["f84r_accessed"] and "no ingredient" in r["claim_ceiling"]))
    failed=[n for n,ok in checks if not ok]
    v={"experiment":r["experiment"],"status":"PASS" if not failed else "FAIL","checks_passed":sum(ok for _,ok in checks),"checks_total":len(checks),"failed":failed,"result_sha256":sha("gdt177_result.json"),"report_sha256":sha("GDT177_Q20_ROLE_SCHEMA_VALIDATION_REPORT.md"),"counterexamples_sha256":sha("gdt177_counterexamples.tsv"),"scope":"independent joins, effect/null/fold arithmetic, hashes, f84 exclusion and claim validation; permutations are checked from retained worlds rather than regenerated"}
    Path("gdt177_validation.json").write_text(json.dumps(v,indent=2,sort_keys=True)+"\n")
    print(v["status"],f"{v['checks_passed']}/{v['checks_total']}",failed)
    if failed:raise SystemExit(1)
if __name__=="__main__":main()
