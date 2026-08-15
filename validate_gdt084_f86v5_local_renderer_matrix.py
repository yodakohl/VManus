#!/usr/bin/env python3
"""Independent matrix reconstruction for GDT084."""
from __future__ import annotations
import csv,hashlib,itertools,json,math
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT/"gdt062_right_family_inventory.tsv";RESULT=ROOT/"gdt084_result.json";MATRIX=ROOT/"gdt084_f86v5_matrix.tsv";RANKS=ROOT/"gdt084_page_matrix_ranks.tsv";NULL=ROOT/"gdt084_null_results.tsv";LEDGER=ROOT/"GDT002_YOLO_LEDGER.tsv";OUT=ROOT/"gdt084_validation.json";H=("ok","yk","yt");F=("aiin","air","ain","ar","al")
def read(p):
 with p.open(encoding="utf-8",newline="")as h:return list(csv.DictReader(h,delimiter="\t"))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def main():
 rows=[r for r in read(SOURCE)if r["page"]=="f86v5"and r["page_host"]in H and r["right_family"]in F];z=[(r["page_host"],r["right_family"])for r in rows];c=set(z);rect=sum(all((h,f)in c for h in hs for f in fs)for hs in itertools.combinations(H,2)for fs in itertools.combinations(F,2));a=Counter(h for h,f in z);b=Counter(f for h,f in z);cc=Counter(z);n=len(z);mi=sum(v/n*math.log2(v*n/(a[h]*b[f]))for(h,f),v in cc.items());r=json.loads(RESULT.read_text());checks={"matrix":len(rows)==20 and len(c)==12 and rect==r["f86v5_rectangles"]==12 and len(read(MATRIX))==15,"lines":len({x["locus"]for x in rows})==r["f86v5_physical_lines"]==14,"mi":abs(mi-r["f86v5_mutual_information_bits"])<1e-12,"ranks":read(RANKS)[0]["page"]=="f86v5"and int(read(RANKS)[1]["rectangles"])==r["next_best_rectangles"]==3,"tables":len(read(NULL))==3,"status":r["status"]=="F86V5_LOCAL_3X5_RENDERER_MATRIX_WEAK_POSTSELECTED_LEAD","f84_seal":not any(r["f84r"].values())};body=dict(r);claimed=body.pop("result_content_sha256");checks["content_hash"]=csha(body)==claimed;checks["hashes"]=all(sha(ROOT/name)==d for fam in("inputs","outputs","documents","implementation")for name,d in r[fam].items());q=[x for x in read(LEDGER)if x["checkpoint_id"]=="GDT084_CKPT001"];checks["ledger"]=len(q)==1 and q[0]["status"]==r["status"]
 passed=all(checks.values());out={"schema":"GDT084_F86V5_LOCAL_RENDERER_MATRIX_VALIDATION_V1","status":"PASS_INDEPENDENT_MATRIX_RECONSTRUCTION"if passed else"FAIL","checks":checks,"checks_passed":sum(checks.values()),"checks_total":len(checks),"result_sha256":sha(RESULT),"validator_sha256":sha(Path(__file__)),"scope":"Independently reconstructs f86v5 cells, rectangles, lines, MI, page ranks, hashes, seal and ledger; deterministic null is bound but not rerun."};OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":out["status"],"checks":f"{out['checks_passed']}/{out['checks_total']}"},sort_keys=True));
 if not passed:raise SystemExit(1)
if __name__=="__main__":main()
