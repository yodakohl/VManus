#!/usr/bin/env python3
"""Independent bound validator for GDT101."""
import csv, hashlib, json
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path
ROOT=Path(__file__).resolve().parent; RESULT=ROOT/"gdt101_result.json"; OUT=ROOT/"gdt101_validation.json"
P=("","o","y");T=("","e","ed","ey","d","y")
def read(p):
 with p.open(encoding="utf-8",newline="") as h:return list(csv.DictReader(h,delimiter="\t"))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(x):return hashlib.sha256(json.dumps(x,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def main():
 r=json.loads(RESULT.read_text()); source=[x for x in read(ROOT/"gdt062_right_family_inventory.tsv") if not x["page"].startswith("f84r")]; cells=read(ROOT/"gdt101_pch_factor_cells.tsv"); ranking=read(ROOT/"gdt101_trigram_grid_ranking.tsv"); transfer=read(ROOT/"gdt101_pch_folio_transfer.tsv"); overlap=read(ROOT/"gdt101_pch_gdt003_overlap.tsv")
 by=defaultdict(list); allpch=[]
 for x in source:
  if "pch" in x["page_host"]:allpch.append(x)
  for p in P:
   for t in T:
    if x["page_host"]==p+"pch"+t:by[p,t].append(x)
 occ=set(by); rect=sum(all((p,t) in occ for p in pp for t in tt) for pp in combinations(P,2) for tt in combinations(T,2)); b=dict(r); ch=b.pop("result_content_sha256")
 novel=[x for x in transfer if x["novel_factor_only_prediction"]=="1"]
 checks={
  "seal":not any(r["f84r"].values()) and not any(x["page"].startswith("f84r") for x in source),
  "grid":len(cells)==18 and len(by)==18 and sum(len(v) for v in by.values())==181 and rect==45,
  "coverage":len(allpch)==331 and abs(r["grid_coverage"]-181/331)<1e-15,
  "cell_support":sum(len({x["physical_folio"] for x in z})>=2 for z in by.values())==17,
  "novel":len(novel)==1 and novel[0]["page_host"]=="ypched" and novel[0]["held_physical_folio"]=="f105",
  "ranking":len(ranking)==r["eligible_comparator_trigrams"] and next(x for x in ranking if x["core"]=="pch")["rank"]=="1",
  "overlap":sum(x["artifact"]=="gdt003_nested_correct_predictions.tsv" for x in overlap)==42 and sum(x["artifact"]=="gdt003_nested_top_predictions.tsv" for x in overlap)==146,
  "roles":r["semantic_role"]=="UNASSIGNED" and all(x["semantic_role"]=="UNASSIGNED" for x in cells+ranking+transfer+overlap),
  "content_hash":csha(b)==ch,
  "hashes":all(sha(ROOT/n)==v for fam in ("inputs","outputs","documents","implementation") for n,v in r[fam].items()),
 }
 led=[x for x in read(ROOT/"GDT002_YOLO_LEDGER.tsv") if x["checkpoint_id"]=="GDT101_CKPT001"]
 checks["ledger"]=len(led)==1 and led[0]["status"]==r["status"]
 ok=all(checks.values()); out={"schema":"GDT101_PCH_INTERNAL_FACTOR_GRID_VALIDATION_V1","status":"PASS_INDEPENDENT_BOUND_COUNTS" if ok else "FAIL","checks":checks,"checks_passed":sum(checks.values()),"checks_total":len(checks),"result_sha256":sha(RESULT),"validator_sha256":sha(Path(__file__)),"scope":"Independently reconstructs grid/cell/rectangle/coverage/folio-support/novel-cell and artifact-overlap counts plus bindings; deterministic permutation stream is bound, not independently replayed."};OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":out["status"],"checks":f"{out['checks_passed']}/{out['checks_total']}"}));raise SystemExit(0 if ok else 1)
if __name__=="__main__":main()
