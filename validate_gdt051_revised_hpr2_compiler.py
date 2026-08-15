#!/usr/bin/env python3
"""Validator for GDT051 synthesis bindings and claim discipline."""
import csv,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent;RESULT=ROOT/"gdt051_result.json";OUT=ROOT/"gdt051_validation.json"
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):
 with Path(p).open(encoding="utf-8",newline="")as h:return list(csv.DictReader(h,delimiter="\t"))
def main():
 r=json.loads(RESULT.read_text());m=json.loads((ROOT/"gdt051_hpr2_model.json").read_text());c=read(ROOT/"gdt051_component_status.tsv");p=read(ROOT/"gdt051_representative_parses.tsv");q=read(ROOT/"gdt051_novel_predictions.tsv");checks=[]
 def ck(n,x):checks.append({"name":n,"pass":bool(x)})
 ck("component_count",len(c)==r["component_count"]==14);ck("parse_count",len(p)==r["representative_parse_count"]==6);ck("prediction_count",len(q)==r["prediction_count"]==6);ck("roles_unassigned",all(x["semantic_reading"]=="UNASSIGNED"for x in p));ck("predictions_frozen",all(x["status"]=="FROZEN_NOT_RUN"for x in q));ck("model_name",m["name"]=="HPR-2_LAYERED_TECHNICAL_RECORD_COMPILER");ck("b3_close",m["generator"]["record_close"].startswith("source-native final B3"));ck("dy_internal","internal"in m["rejected_or_downgraded"]["DY_as_line_closer"]);ck("semantic_ceiling",m["provisional_semantic_layer"]["all_other_components"]=="UNASSIGNED"and"concrete meaning"in r["claim_ceiling"]);ck("f84",not any(r["f84r"].values())and all(not x["locus"].startswith("f84r")for x in p)and all(not x["target"].lower().startswith("f84")for x in q))
 for bucket in("inputs","outputs","documents","implementation"):
  for name,d in r[bucket].items():ck(bucket+":"+name,sha(ROOT/name)==d)
 ck("decision",r["status"]=="HPR2_LAYERED_TECHNICAL_RECORD_COMPILER_SELECTED_WITH_CONTENT_UNGROUNDED")
 status="PASS_SYNTHESIS_BINDINGS"if all(x["pass"]for x in checks)else"FAIL";o={"schema":"GDT051_VALIDATION_V1","status":status,"checks_passed":sum(x["pass"]for x in checks),"checks_total":len(checks),"checks":checks,"result_sha256":sha(RESULT)};OUT.write_text(json.dumps(o,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":status,"checks":f'{o["checks_passed"]}/{o["checks_total"]}'},sort_keys=True));raise SystemExit(0 if status.startswith("PASS")else 1)
if __name__=="__main__":main()
