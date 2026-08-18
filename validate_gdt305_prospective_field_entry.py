#!/usr/bin/env python3
"""Independently reconstruct retained GDT305 endpoints and decisions."""
import csv, hashlib, json, statistics
from collections import defaultdict
from pathlib import Path

R = Path(__file__).resolve().parent
SOURCE = R / "gdt278_native_event_inventory.tsv"; FROZEN = R / "gdt305_frozen_pairs.tsv"
PAIR = R / "gdt305_pair_endpoint_deltas.tsv"; OPS = R / "gdt305_operation_endpoint_scores.tsv"
PRED = R / "gdt305_prediction_results.tsv"; RESULT = R / "gdt305_result.json"; OUT = R / "gdt305_validation.json"
ENDPOINTS = {"FIELD_FIRST": lambda x: x["within_field_position"] == "FIRST", "FIELD_LAST": lambda x: x["within_field_position"] == "LAST", "LINE_FIRST": lambda x: int(x["group_index"]) == 1, "LINE_LAST": lambda x: int(x["group_index"]) == int(x["group_count"]), "RECORD_ORDINAL_1": lambda x: int(x["record_ordinal"]) == 1}

def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def canon(value): return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()).hexdigest()
def read(path):
    with Path(path).open(encoding="utf8", newline="") as handle: return list(csv.DictReader(handle, delimiter="\t"))
checks=[]
def check(name, condition):
    if not condition: raise AssertionError(name)
    checks.append(name)
def close(a,b): return abs(float(a)-float(b)) < 5e-12

def main():
    frozen=read(FROZEN); wanted={(x["page_host"],x["source_surface_sha256"]) for x in frozen}|{(x["page_host"],x["target_surface_sha256"]) for x in frozen}; events=defaultdict(list); f84=False
    with SOURCE.open(encoding="utf8",newline="") as handle:
        for row in csv.DictReader(handle,delimiter="\t"):
            if row["control_id"]!="VOYNICH_REFERENCE" or int(row["group_count"])<2: continue
            f84 |= row["page"].startswith("f84") or row["locus"].startswith("f84")
            key=(row["page_host"],row["source_surface_sha256"])
            if key in wanted: events[key].append(row)
    check("source_f84_free",not f84); actual={x["pair_id"]:x for x in read(PAIR)}; host=defaultdict(lambda:defaultdict(list))
    for item in frozen:
        a=events[(item["page_host"],item["source_surface_sha256"])]; b=events[(item["page_host"],item["target_surface_sha256"])]; check("pair_support",len(a)==int(item["source_events"]) and len(b)==int(item["target_events"])); row=actual[item["pair_id"]]
        for endpoint,predicate in ENDPOINTS.items():
            sr=sum(predicate(x) for x in a)/len(a); tr=sum(predicate(x) for x in b)/len(b); delta=tr-sr
            check("pair_endpoint",close(row[f"source_{endpoint.lower()}_rate"],sr) and close(row[f"target_{endpoint.lower()}_rate"],tr) and close(row[f"delta_{endpoint.lower()}"],delta)); host[(item["operation"],item["page_host"])][endpoint].append(delta)
    check("pair_inventory",set(actual)=={x["pair_id"] for x in frozen})
    op_actual={x["operation"]:x for x in read(OPS)}
    for operation,row in op_actual.items():
        hosts=sorted(h for op,h in host if op==operation); check("operation_host_count",len(hosts)==int(row["hosts"]))
        for endpoint in ENDPOINTS:
            vals=[statistics.mean(host[(operation,h)][endpoint]) for h in hosts]; check("operation_endpoint",close(row[f"mean_delta_{endpoint.lower()}"],statistics.mean(vals)))
    q=op_actual["wrapper:NONE>q"]; ch=op_actual["wrapper:ch>s"]; ds=op_actual["wrapper:d>s"]
    expected={"P1":float(q["mean_delta_field_first"])>0 and float(q["mean_delta_field_last"])<0,"P2":float(ch["mean_delta_field_first"])>0,"P3":float(ds["mean_delta_field_first"])>0,"P4":all(abs(float(op_actual[o]["mean_delta_record_ordinal_1"]))<.1 for o in op_actual)}
    pred={x["prediction_id"]:x["passed"]=="true" for x in read(PRED)}; check("prediction_decisions",pred==expected); passed=sum(expected.values()); status="ALL_FROZEN_DIRECTIONS_TRANSFER" if passed==4 else "FROZEN_DIRECTIONS_FAIL" if passed==0 else "MIXED_FROZEN_DIRECTIONS"
    result=json.loads(RESULT.read_text()); stored=result.pop("content_sha256"); check("result_content_hash",stored==canon(result)); check("result_status",result["status"]==status and result["summary"]["prediction_passes"]==passed); check("result_inputs",all(result["inputs"][name]==sha(R/name) for name in result["inputs"])); check("result_outputs",all(result["outputs"][name]==sha(R/name) for name in result["outputs"])); check("result_documents",all(result["documents"][name]==sha(R/name) for name in result["documents"])); check("implementation_hash",all(result["implementation"][name]==sha(R/name) for name in result["implementation"])); check("f84_flags",not any(result["f84"].values()))
    out={"schema":"GDT305_PROSPECTIVE_FIELD_ENTRY_VALIDATION_V1","status":"PASS","checks_passed":len(checks),"checks":checks,"result_sha256":sha(RESULT),"reconstructed_status":status,"f84_rows":0}; out["content_sha256"]=canon(out); OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n"); print(json.dumps({"status":"PASS","checks":len(checks),"reconstructed_status":status},sort_keys=True))

if __name__=="__main__": main()
