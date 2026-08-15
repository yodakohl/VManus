#!/usr/bin/env python3
"""Bound validator for GDT103."""
import csv,hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parent;RESULT=R/"gdt103_result.json";OUT=R/"gdt103_validation.json"
def read(p):
 with p.open(encoding="utf-8",newline="") as h:return list(csv.DictReader(h,delimiter="\t"))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(x):return hashlib.sha256(json.dumps(x,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def main():
 r=json.loads(RESULT.read_text());s=read(R/"gdt103_external_layer_scores.tsv");m=read(R/"gdt103_external_layer_summary.tsv");v=read(R/"gdt103_variant_log.tsv");b=dict(r);ch=b.pop("result_content_sha256");p={x["representation"]:x for x in m if x["encoding"]=="ACTIVE_ONLY"}
 checks={"panel":r["eligible_loci"]==332 and r["physical_folios"]==19,"matrix":len(s)==144 and len(m)==18 and len(v)==6,"host_raw":float(p["PAGE_HOST_CHAR3"]["summed_gain_vs_nuisance_bits"])>float(p["RAW_CHAR3"]["summed_gain_vs_nuisance_bits"]),"b3_neutral":abs(float(p["HOST_PLUS_B3"]["summed_increment_vs_page_host_bits"]))<1,"compiler_negative":float(p["COMPILER_ONLY"]["summed_gain_vs_nuisance_bits"])<0,"variant_disclosure":any(x["status"]=="SENSITIVITY_ARTIFACT" and "B3" in x["description"] for x in v),"roles":r["semantic_role"]=="UNASSIGNED" and all(x["semantic_role"]=="UNASSIGNED" for x in s+m),"seal":not any(r["f84r"].values()),"content_hash":csha(b)==ch,"hashes":all(sha(R/n)==z for fam in ("inputs","outputs","documents","implementation") for n,z in r[fam].items())};led=[x for x in read(R/"GDT002_YOLO_LEDGER.tsv") if x["checkpoint_id"]=="GDT103_CKPT001"];checks["ledger"]=len(led)==1 and led[0]["status"]==r["status"];ok=all(checks.values());o={"schema":"GDT103_HPR2_EXTERNAL_LAYER_ABLATION_VALIDATION_V1","status":"PASS_BOUND_LAYER_ABLATION" if ok else "FAIL","checks":checks,"checks_passed":sum(checks.values()),"checks_total":len(checks),"result_sha256":sha(RESULT),"validator_sha256":sha(Path(__file__)),"scope":"Checks panel/matrix/ordering/neutral-control/variant-disclosure/bindings/seal/ledger; does not independently replay the KNN score."};OUT.write_text(json.dumps(o,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":o["status"],"checks":f"{o['checks_passed']}/{o['checks_total']}"}));raise SystemExit(0 if ok else 1)
if __name__=="__main__":main()
