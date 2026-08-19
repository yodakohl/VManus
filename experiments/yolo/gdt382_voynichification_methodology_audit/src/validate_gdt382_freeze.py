#!/usr/bin/env python3
"""Independent integrity validation of the GDT382 pre-outcome freeze."""
import csv,gzip,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];BASE=ROOT/"experiments/yolo/gdt382_voynichification_methodology_audit";ART=BASE/"artifacts"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def content(d):
 q=dict(d);q.pop("content_hash",None);return hashlib.sha256(json.dumps(q,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def main():
 checks=[]
 def ck(n,v):checks.append((n,bool(v)))
 e=json.loads((ART/"gdt382_encoder_freeze.json").read_text());d=json.loads((ART/"gdt382_recovery_design_freeze.json").read_text())
 ck("encoder_content_hash",e["content_hash"]==content(e));ck("design_content_hash",d["content_hash"]==content(d));ck("oracle_blind",not e["oracle_used_to_build_base_layer"]);ck("not_gdt381_tuned",not d["gdt381_outcome_used_to_design"]);ck("no_voynich",not d["voynich_scoring"]);ck("f84_false",not e["f84"]["opened"] and not d["f84_accessed"])
 p=ART/"gdt382_voynichified_observation_layer.tsv.gz";ck("encoded_hash",next(iter(e["encoded_output"].values()))==sha(p))
 n=0;recs=set();domains=set();oracle_flags=set();bad=[]
 with gzip.open(p,"rt",encoding="utf-8",newline="") as f:
  r=csv.DictReader(f,delimiter="\t")
  for x in r:
   n+=1;recs.add((x["domain"],x["collection_id"],x["record_id"]));domains.add(x["domain"]);oracle_flags.add(x["encoder_used_oracle"])
   # Hash/opaque codes can contain the hexadecimal substring f84 by chance.
   # Check only provenance-bearing identifiers, never arbitrary synthetic IDs.
   if "f84" in "\t".join(x[k] for k in ["domain","collection_id","record_id","element_key"]).lower():bad.append(n)
 ck("row_count",n==133183==e["rows"]);ck("record_count",len(recs)==3235==e["records"]);ck("five_domains",len(domains)==5);ck("oracle_flag_zero",oracle_flags=={"0"});ck("no_f84_payload",not bad)
 ck("six_endpoints",len(d["endpoints"])==6);ck("six_representations",len(d["representations"])==6);ck("eight_modes",len(d["encoding_modes"])==8);ck("eight_overcontrol_variables",len(d["overcontrol_variables"])==8)
 result={"schema":"GDT382_FREEZE_VALIDATION_V1","status":"PASS" if all(v for _,v in checks) else "FAIL","checks":len(checks),"passed":sum(v for _,v in checks),"details":{k:v for k,v in checks},"inputs":{"encoder_freeze":sha(ART/"gdt382_encoder_freeze.json"),"design_freeze":sha(ART/"gdt382_recovery_design_freeze.json"),"encoded_layer":sha(p)}}
 result["content_hash"]=content(result);(ART/"gdt382_freeze_validation.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":result["status"],"passed":result["passed"],"checks":result["checks"]}))
 if result["status"]!="PASS":raise SystemExit(1)
if __name__=="__main__":main()
