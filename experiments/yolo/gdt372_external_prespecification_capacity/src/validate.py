#!/usr/bin/env python3
"""Nonimporting aggregate validator for GDT372."""
import csv,hashlib,json,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]; BASE=ROOT/"experiments/yolo/gdt372_external_prespecification_capacity"; ART=BASE/"artifacts"
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):
 with open(p,newline="") as f:return list(csv.DictReader(f))
def main():
 c=[]
 def ck(n,o,d=""):
  c.append({"check":n,"passed":bool(o),"detail":d})
  if not o:raise AssertionError(f"{n}: {d}")
 rp=ART/"gdt372_result.json"; r=json.loads(rp.read_text()); g=read(ART/"gdt372_power_grid.tsv"); s=read(ART/"gdt372_design_thresholds.tsv"); m=read(ART/"gdt372_minimum_designs.tsv")
 ck("schema",r["schema"]=="GDT372_RESULT_V1");ck("grid",len(g)==540,str(len(g)));ck("summary",len(s)==180,str(len(s)));ck("minima",len(m)==5,str(len(m)))
 ck("trials",all(int(x["trials"])==256 for x in g));ck("partition",all(abs(float(x["any_pass_rate"])-float(x["successful_detection_rate"])-float(x["wrong_predicate_pass_rate"]))<1e-12 for x in g))
 by={(int(x["candidate_library"]),int(x["discovery_folios"]),int(x["held_folios"]),int(x["arrays_per_folio"]),int(x["cells_per_array"]),x["effect"],x["direction_mode"]):x for x in g}
 adequate={L:[] for L in (1,3,9,27,81)}
 for x in s:
  key=(int(x["candidate_library"]),int(x["discovery_folios"]),int(x["held_folios"]),int(x["arrays_per_folio"]),int(x["cells_per_array"]));L,d,h,a,z=key
  st=by[key+("MEDIUM","STABLE")];nu=by[key+("NULL","STABLE")];rv=by[key+("MEDIUM","REVERSING")]
  ok=float(st["successful_detection_rate"])>=.8 and float(nu["any_pass_rate"])<=.05 and float(rv["any_pass_rate"])<=.10
  ck("gate_"+"_".join(map(str,key)),(x["adequate"]=="True")==ok)
  if ok:adequate[L].append((int(x["total_cells"]),d+h,int(x["held_cells"]),a,z,x))
 for x in m:
  L=int(x["candidate_library"]); adequate[L].sort()
  if adequate[L]:ck(f"minimum_{L}",x["adequate"]=="True" and int(x["total_cells"])==adequate[L][0][0])
  else:ck(f"minimum_none_{L}",x["adequate"]=="False" and x["total_cells"]=="")
 for rel,d in r["inputs"].items():ck("input_"+rel,sha(ROOT/rel)==d)
 for rel,d in r["outputs"].items():ck("output_"+rel,sha(ROOT/rel)==d)
 for rel,d in r["implementation"].items():ck("implementation_"+rel,sha(ROOT/rel)==d)
 p=dict(r);stored=p.pop("content_hash");ck("content_hash",hashlib.sha256(json.dumps(p,sort_keys=True,separators=(",",":")).encode()).hexdigest()==stored)
 ck("no_voynich",r["new_voynich_rows_loaded"]==0);ck("no_images",r["new_images_accessed"]==0);ck("f84",r["f84_accessed"] is False)
 v={"schema":"GDT372_VALIDATION_V1","status":"PASS","scope":"INTEGRITY_AND_INDEPENDENT_AGGREGATE_GATE_RECONSTRUCTION; STOCHASTIC_KERNEL_NOT_INDEPENDENTLY_REIMPLEMENTED","checks_passed":len(c),"checks_total":len(c),"checks":c,"result_sha256":sha(rp),"validator_sha256":sha(BASE/'src/validate.py'),"f84_accessed":False}
 (ART/"gdt372_validation.json").write_text(json.dumps(v,indent=2,sort_keys=True)+"\n");print(f"PASS {len(c)}/{len(c)}")
if __name__=="__main__":main()
