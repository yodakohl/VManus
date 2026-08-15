#!/usr/bin/env python3
"""Integrity and arithmetic validator for GDT049."""
import csv,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent;RESULT=ROOT/"gdt049_result.json";OCC=ROOT/"gdt049_air_family_contexts.tsv";TESTS=ROOT/"gdt049_air_context_tests.tsv";OUT=ROOT/"gdt049_validation.json"
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):
 with Path(p).open(encoding="utf-8",newline="")as h:return list(csv.DictReader(h,delimiter="\t"))
def main():
 r=json.loads(RESULT.read_text());o=read(OCC);t=read(TESTS);checks=[]
 def ck(n,v):checks.append({"name":n,"pass":bool(v)})
 ck("occurrence_count",len(o)==r["family_groups"]==614);ck("air_count",sum(x["is_air"]=="1"for x in o)==r["air_occurrences"]==22);ck("test_count",len(t)==len(r["tests"])==18)
 for stored,row in zip(r["tests"],t):
  ck("test_identity:"+row["registers"]+":"+row["feature"],stored["registers"]==row["registers"]and stored["feature"]==row["feature"]and abs(stored["observed_hits"]-float(row["observed_hits"]))<1e-12 and abs(stored["expected_hits"]-float(row["expected_hits"]))<1e-9)
 ck("no_pass",not r["passing_features"]);ck("f84_absent",not any(x["locus"].startswith("f84r")for x in o)and not any(r["f84r"].values()))
 for bucket in("inputs","outputs","documents","implementation"):
  for name,digest in r[bucket].items():ck(bucket+":"+name,sha(ROOT/name)==digest)
 ck("decision",r["status"]=="AIR_HAS_REGISTER_SELECTION_BUT_NO_STABLE_COARSE_LOCAL_FUNCTION");ck("ceiling","no morpheme"in r["claim_ceiling"]and"meaning"in r["claim_ceiling"])
 status="PASS_ARITHMETIC_AND_HASH_BINDINGS"if all(x["pass"]for x in checks)else"FAIL";payload={"schema":"GDT049_VALIDATION_V1","status":status,"checks_passed":sum(x["pass"]for x in checks),"checks_total":len(checks),"checks":checks,"result_sha256":sha(RESULT)};OUT.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":status,"checks":f'{payload["checks_passed"]}/{payload["checks_total"]}'},sort_keys=True));raise SystemExit(0 if status.startswith("PASS")else 1)
if __name__=="__main__":main()
