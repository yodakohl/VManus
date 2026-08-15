#!/usr/bin/env python3
"""Independent arithmetic validator for GDT104."""
import csv,hashlib,itertools,json
from pathlib import Path
R=Path(__file__).resolve().parent;RESULT=R/"gdt104_result.json";OUT=R/"gdt104_validation.json";OBJ={"STAR_OR_SKY","FIGURE","PLANT","WATER_OR_APPARATUS"}
def read(p):
 with p.open(encoding="utf-8",newline="") as h:return list(csv.DictReader(h,delimiter="\t"))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(x):return hashlib.sha256(json.dumps(x,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def main():
 r=json.loads(RESULT.read_text());a=read(R/"gdt104_axis_contributions.tsv");c=read(R/"gdt104_channel_decomposition.tsv");n=read(R/"gdt104_partition_null.tsv");p=read(R/"gdt104_frozen_predictions.tsv");b=dict(r);ch=b.pop("result_content_sha256");by={x["layer"]:x for x in c};fixed=next(x for x in n if x["is_preexisting_object_partition"]=="1")
 checks={"matrix":len(a)==48 and len(c)==6,"partition":len(n)==70 and fixed["rank"]=="3" and abs(r["partition_diagnostic_p"]-3/70)<1e-15,"decomposition":float(by["PAGE_HOST_CHAR3"]["object_axis_bits"])>0>float(by["PAGE_HOST_CHAR3"]["relation_axis_bits"]) and float(by["HOST_PLUS_DY"]["relation_axis_bits"])>float(by["HOST_PLUS_DY"]["object_axis_bits"]),"predictions":len(p)==4 and all(x["status"]=="FROZEN_NOT_RUN" for x in p),"roles":r["semantic_role"]=="UNASSIGNED" and all(x["semantic_role"]=="UNASSIGNED" for x in a+c+p),"seal":not any(r["f84r"].values()),"content_hash":csha(b)==ch,"hashes":all(sha(R/k)==v for fam in ("inputs","outputs","documents","implementation") for k,v in r[fam].items())};led=[x for x in read(R/"GDT002_YOLO_LEDGER.tsv") if x["checkpoint_id"]=="GDT104_CKPT001"];checks["ledger"]=len(led)==1 and led[0]["status"]==r["status"];ok=all(checks.values());o={"schema":"GDT104_HPR2_TWO_CHANNEL_DECOMPOSITION_VALIDATION_V1","status":"PASS_INDEPENDENT_ARITHMETIC" if ok else "FAIL","checks":checks,"checks_passed":sum(checks.values()),"checks_total":len(checks),"result_sha256":sha(RESULT),"validator_sha256":sha(Path(__file__)),"scope":"Checks decomposition signs, exact 70-world rank, predictions, roles, bindings, seal, and ledger."};OUT.write_text(json.dumps(o,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":o["status"],"checks":f"{o['checks_passed']}/{o['checks_total']}"}));raise SystemExit(0 if ok else 1)
if __name__=="__main__":main()
