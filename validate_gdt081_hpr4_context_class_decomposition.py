#!/usr/bin/env python3
"""Independent deterministic reconstruction for GDT081."""
from __future__ import annotations
import csv,hashlib,itertools,json,math
from collections import Counter,defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT/"gdt062_right_family_inventory.tsv";SCORES=ROOT/"gdt081_context_class_scores.tsv";PAIRS=ROOT/"gdt081_pair_similarity.tsv";CELLS=ROOT/"gdt081_shared_context_cells.tsv";RESULT=ROOT/"gdt081_result.json";LEDGER=ROOT/"GDT002_YOLO_LEDGER.tsv";OUT=ROOT/"gdt081_validation.json";FIELDS=("wrapper","inner_d","local_frame","dy_closure","b3","position_quartile")
def read(p):
 with p.open(encoding="utf-8",newline="")as h:return list(csv.DictReader(h,delimiter="\t"))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def cos(a,b):
 d=math.sqrt(sum(x*x for x in a.values())*sum(x*x for x in b.values()));return sum(a[k]*b[k]for k in set(a)&set(b))/d if d else 0
def main():
 rows=read(SOURCE);res=json.loads(RESULT.read_text());regs=sorted({r["register"]for r in rows});hs=["d","ok","yk","yt"];by=defaultdict(list)
 for r in rows:by[r["page_host"]].append(r)
 vec={(g,h):Counter(tuple(r[f]for f in FIELDS)for r in by[h]if r["register"]==g)for g in regs for h in hs}
 def score(ss):return sum(cos(vec[g,a],vec[g,b])for g in regs for a,b in itertools.combinations(ss,2))/(len(regs)*3)
 tri={drop:score([h for h in hs if h!=drop])for drop in hs};best=max(tri,key=tri.get);cell=defaultdict(set)
 for r in rows:
  if r["page_host"]in{"ok","yk","yt"}:cell[(r["register"],)+tuple(r[f]for f in FIELDS)].add(r["page_host"])
 checks={"source":len(rows)==15592 and not any(r["locus"].startswith("f84r")for r in rows),"primary":best==res["primary_dropped_host"]=="d"and abs(tri[best]-res["primary_similarity"])<1e-10,"ordering":tri["d"]>max(tri[x]for x in("ok","yk","yt")),"cells":sum(len(v)==3 for v in cell.values())==res["shared_all_three_cells"]==17 and sum(len(v)==2 for v in cell.values())==res["shared_two_host_cells"]==10,"tables":len(read(SCORES))==20 and len(read(PAIRS))==30 and len(read(CELLS))==27,"status":res["status"]=="HPR4_DECOMPOSES_INTO_OK_YK_YT_UNFRAMED_CONTEXT_CLASS_D_IS_OUTLIER","f84_seal":not any(res["f84r"].values())}
 body=dict(res);claimed=body.pop("result_content_sha256");checks["content_hash"]=csha(body)==claimed;checks["hashes"]=all(sha(ROOT/name)==d for fam in("inputs","outputs","documents","implementation")for name,d in res[fam].items());q=[r for r in read(LEDGER)if r["checkpoint_id"]=="GDT081_CKPT001"];checks["ledger"]=len(q)==1 and q[0]["status"]==res["status"]
 passed=all(checks.values());out={"schema":"GDT081_HPR4_CONTEXT_CLASS_DECOMPOSITION_VALIDATION_V1","status":"PASS_INDEPENDENT_CONTEXT_CLASS_RECONSTRUCTION"if passed else"FAIL","checks":checks,"checks_passed":sum(checks.values()),"checks_total":len(checks),"result_sha256":sha(RESULT),"validator_sha256":sha(Path(__file__)),"scope":"Independently reconstructs primary no-right-family trio similarities, ordering, shared cells, tables, seals, hashes and ledger; stored deterministic null p is bound but not rerun."};OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":out["status"],"checks":f"{out['checks_passed']}/{out['checks_total']}"},sort_keys=True));
 if not passed:raise SystemExit(1)
if __name__=="__main__":main()
