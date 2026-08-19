#!/usr/bin/env python3
"""Nonimporting integrity and gate validator for GDT371."""

import csv, hashlib, json, math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / "experiments/yolo/gdt371_validation_capacity_extension"
ART = BASE / "artifacts"

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rows(p):
    with open(p, newline="") as f: return list(csv.DictReader(f))

def main():
    checks=[]
    def ck(name, ok, detail=""):
        checks.append({"check":name,"passed":bool(ok),"detail":detail})
        if not ok: raise AssertionError(f"{name}: {detail}")
    rp=ART/"gdt371_result.json"; r=json.loads(rp.read_text())
    g=rows(ART/"gdt371_power_grid.tsv"); d=rows(ART/"gdt371_design_thresholds.tsv")
    ck("schema",r["schema"]=="GDT371_RESULT_V1")
    ck("grid_rows",len(g)==600,str(len(g))); ck("design_rows",len(d)==150,str(len(d)))
    ck("trials",all(int(x["trials"])==256 for x in g))
    ck("selector",abs(r["simulation"]["selector_cost_bits"]-math.log2(81))<1e-12)
    ck("rates",all(0<=float(x[k])<=1 for x in g for k in ("selected_true_rate","any_pass_rate","successful_detection_rate","wrong_predicate_pass_rate","held_transfer_rate")))
    ck("partition",all(abs(float(x["any_pass_rate"])-float(x["successful_detection_rate"])-float(x["wrong_predicate_pass_rate"]))<1e-12 for x in g))
    by={(int(x["discovery_folios"]),int(x["held_folios"]),int(x["arrays_per_folio"]),int(x["cells_per_array"]),x["effect"],x["direction_mode"]):x for x in g}
    adequate=[]
    for x in d:
        key=(int(x["discovery_folios"]),int(x["held_folios"]),int(x["arrays_per_folio"]),int(x["cells_per_array"]))
        s=by[key+("MEDIUM","STABLE")]; n=by[key+("NULL","STABLE")]; v=by[key+("MEDIUM","REVERSING")]
        ok=float(s["successful_detection_rate"])>=.8 and float(n["any_pass_rate"])<=.05 and float(v["any_pass_rate"])<=.10
        ck(f"gate_{key}",(x["adequate"]=="True")==ok)
        if ok: adequate.append((int(x["total_cells"]),int(x["total_folios"]),int(x["held_cells"]),key,x))
    adequate.sort()
    ck("adequate_count",len(adequate)==r["adequate_design_count"])
    if adequate:
        rec=r["recommended_design"]; x=adequate[0][4]
        ck("recommendation",all(int(rec[k])==int(x[k]) for k in ("discovery_folios","held_folios","arrays_per_folio","cells_per_array")))
    else: ck("recommendation_none",r["recommended_design"] is None)
    for rel,digest in r["inputs"].items(): ck("input_"+rel,sha(ROOT/rel)==digest)
    for rel,digest in r["outputs"].items(): ck("output_"+rel,sha(ROOT/rel)==digest)
    for rel,digest in r["implementation"].items(): ck("implementation_"+rel,sha(ROOT/rel)==digest)
    payload=dict(r); stored=payload.pop("content_hash")
    ck("content_hash",hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(",",":")).encode()).hexdigest()==stored)
    ck("no_voynich",r["new_voynich_rows_loaded"]==0); ck("no_images",r["new_images_accessed"]==0); ck("f84",r["f84_accessed"] is False)
    v={"schema":"GDT371_VALIDATION_V1","status":"PASS","scope":"INTEGRITY_AND_INDEPENDENT_AGGREGATE_GATE_RECONSTRUCTION; STOCHASTIC_KERNEL_NOT_INDEPENDENTLY_REIMPLEMENTED","checks_passed":len(checks),"checks_total":len(checks),"checks":checks,"result_sha256":sha(rp),"validator_sha256":sha(BASE/'src/validate.py'),"f84_accessed":False}
    (ART/"gdt371_validation.json").write_text(json.dumps(v,indent=2,sort_keys=True)+"\n")
    print(f"PASS {len(checks)}/{len(checks)}")

if __name__=="__main__": main()
