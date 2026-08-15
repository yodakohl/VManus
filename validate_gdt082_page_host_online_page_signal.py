#!/usr/bin/env python3
"""Independent retained-model reconstruction for GDT082."""
from __future__ import annotations
import csv,hashlib,json,math,re
from collections import Counter,defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT/"gdt062_right_family_inventory.tsv";RESULT=ROOT/"gdt082_result.json";PAGES=ROOT/"gdt082_page_contributions.tsv";SCORES=ROOT/"gdt082_page_shrinkage_scores.tsv";REG=ROOT/"gdt082_register_scores.tsv";NULL=ROOT/"gdt082_null_results.tsv";LEDGER=ROOT/"GDT002_YOLO_LEDGER.tsv";OUT=ROOT/"gdt082_validation.json";Y=("ok","yk","yt");WA=4;PA=32
def read(p):
 with p.open(encoding="utf-8",newline="")as h:return list(csv.DictReader(h,delimiter="\t"))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def main():
 rows=[r for r in read(SOURCE)if r["page_host"]in Y];rows.sort(key=lambda r:(r["page"],int(re.search(r"\.(\d+)",r["locus"]).group(1)),int(r["group_index"])));folios=sorted({r["physical_folio"]for r in rows});total=0;pg=defaultdict(float);rg=defaultdict(float)
 for fol in folios:
  tr=[r for r in rows if r["physical_folio"]!=fol];te=[r for r in rows if r["physical_folio"]==fol];rc=defaultdict(Counter);wc=defaultdict(Counter)
  for r in tr:rc[r["register"]][r["page_host"]]+=1;wc[r["register"],r["wrapper"]][r["page_host"]]+=1
  pc=defaultdict(Counter);i=0
  while i<len(te):
   locus=te[i]["locus"];batch=[]
   while i<len(te)and te[i]["locus"]==locus:batch.append(te[i]);i+=1
   for r in batch:
    base={y:(rc[r["register"]][y]+.5)/(sum(rc[r["register"]].values())+1.5)for y in Y};c=wc[r["register"],r["wrapper"]];wp={y:(c[y]+WA*base[y])/(sum(c.values())+WA)for y in Y};p=pc[r["page"]];pr={y:(p[y]+PA*wp[y])/(sum(p.values())+PA)for y in Y};g=math.log2(pr[r["page_host"]]/wp[r["page_host"]]);total+=g;pg[r["page"]]+=g;rg[r["register"]]+=g
   for r in batch:pc[r["page"]][r["page_host"]]+=1
 res=json.loads(RESULT.read_text());page=read(PAGES);reg=read(REG);checks={"inventory":len(rows)==958 and not any(r["locus"].startswith("f84r")for r in rows),"selected":res["selected_page_alpha"]==32 and abs(total-res["page_gain_vs_wrapper_bits"])<1e-9,"top_page":max(pg,key=pg.get)==res["top_page"]["page"]=="f86v5"and abs(pg["f86v5"]-float(res["top_page"]["page_gain_vs_wrapper"]))<1e-9,"registers":all(abs(rg[r["register"]]-float(r["page_gain_vs_wrapper"]))<1e-9 for r in reg),"tables":len(page)==res["pages"]==127 and len(read(SCORES))==7 and len(reg)==5 and len(read(NULL))==1,"status":res["status"]=="PAGE_HOST_IDENTITY_HAS_PAGE_LOCAL_SIGNAL_BEYOND_WRAPPER_BUT_F86V5_DOMINATES","f84_seal":not any(res["f84r"].values())}
 body=dict(res);claimed=body.pop("result_content_sha256");checks["content_hash"]=csha(body)==claimed;checks["hashes"]=all(sha(ROOT/name)==d for fam in("inputs","outputs","documents","implementation")for name,d in res[fam].items());q=[r for r in read(LEDGER)if r["checkpoint_id"]=="GDT082_CKPT001"];checks["ledger"]=len(q)==1 and q[0]["status"]==res["status"]
 passed=all(checks.values());out={"schema":"GDT082_PAGE_HOST_ONLINE_PAGE_SIGNAL_VALIDATION_V1","status":"PASS_INDEPENDENT_RETAINED_MODEL_RECONSTRUCTION"if passed else"FAIL","checks":checks,"checks_passed":sum(checks.values()),"checks_total":len(checks),"result_sha256":sha(RESULT),"validator_sha256":sha(Path(__file__)),"scope":"Independently reconstructs line-batched held-folio selected model, page/register contributions, tables, hashes, seal and ledger; deterministic 5000-draw null is bound but not rerun."};OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":out["status"],"checks":f"{out['checks_passed']}/{out['checks_total']}"},sort_keys=True));
 if not passed:raise SystemExit(1)
if __name__=="__main__":main()
