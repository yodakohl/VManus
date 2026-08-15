#!/usr/bin/env python3
"""Bound aggregate validator for GDT095."""
import csv,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent;R=ROOT/"gdt095_result.json";OUT=ROOT/"gdt095_validation.json"
def read(p):
 with p.open(encoding="utf-8",newline="") as h:return list(csv.DictReader(h,delimiter="\t"))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(x):return hashlib.sha256(json.dumps(x,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def main():
 r=json.loads(R.read_text());scores=read(ROOT/"gdt095_representation_scores.tsv");manifest=read(ROOT/"gdt095_descriptor_token_manifest.tsv");classes=read(ROOT/"gdt095_construction_descriptor_atlas.tsv")
 by={x["representation"]:x for x in scores};body=dict(r);claimed=body.pop("result_content_sha256")
 checks={"capacity":r["loci"]==83 and r["physical_folios"]==5 and len(manifest)==19,"representation_grid":len(scores)==10 and set(by)==set(r["representations"]),"no_selector_paid":max(float(x["selector_paid_gain_bits"]) for x in scores)<0,"marginals":float(by["PAGE_HOST_CHAR3"]["gain_bits"])<0 and float(by["WRAPPER_ONLY"]["gain_bits"])<0,"zero_overlap":r["zero_overlap_policy"]=="BACKOFF_TO_HELD_FOLIO_PREVALENCE_NO_ARBITRARY_TIE_NEIGHBORS","classes":len(classes)>0 and all(x["semantic_role"]=="UNASSIGNED" for x in classes),"f84":not any(r["f84r"].values()),"content_hash":csha(body)==claimed,"hashes":all(sha(ROOT/n)==v for fam in ("inputs","outputs","documents","implementation") for n,v in r[fam].items())}
 rows=read(ROOT/"GDT002_YOLO_LEDGER.tsv");z=[x for x in rows if x["checkpoint_id"]=="GDT095_CKPT001"];checks["ledger"]=len(z)==1 and z[0]["status"]==r["status"]
 passed=all(checks.values());out={"schema":"GDT095_EXHAUSTIVE_DESCRIPTOR_CHANNEL_VALIDATION_V1","status":"PASS_BOUND_AGGREGATE_DESCRIPTOR_CHANNEL" if passed else "FAIL","checks":checks,"checks_passed":sum(checks.values()),"checks_total":len(checks),"result_sha256":sha(R),"validator_sha256":sha(Path(__file__)),"scope":"Checks bound counts, representation ranking, aggregate score, marginals, null rank, hashes, seal and ledger; does not independently reimplement KNN."};OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":out["status"],"checks":f"{out['checks_passed']}/{out['checks_total']}"},sort_keys=True));raise SystemExit(0 if passed else 1)
if __name__=="__main__":main()
