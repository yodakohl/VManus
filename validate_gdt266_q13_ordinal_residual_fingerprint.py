#!/usr/bin/env python3
"""Integrity/arithmetic and identifiability validation for stopped GDT266."""
import csv,hashlib,json,random
from collections import Counter,defaultdict
from pathlib import Path
R=Path(__file__).resolve().parent;RES="gdt266_result.json";SRC="gdt227_q13_abstract_interlinear.tsv"
MODES=["STRUCTURE_ONLY","WRAPPER","RIGHT","COMPILER","RAW_EXACT","PAGE_HOST_EXACT","RAW_CHAR3","PAGE_HOST_CHAR3"]
def read(p):
 with (R/p).open(encoding="utf-8") as f:return list(csv.DictReader(f,delimiter="\t"))
def sha(p):return hashlib.sha256((R/p).read_bytes()).hexdigest()
def main():
 c=[]
 def ck(n,v):assert v,n;c.append(n)
 z=json.loads((R/RES).read_text())
 for g in ["inputs","documents","outputs","implementation"]:
  for p,h in z[g].items():ck("hash:"+p,sha(p)==h)
 q=dict(z);h=q.pop("content_hash");ck("content_hash",hashlib.sha256(json.dumps(q,sort_keys=True,separators=(",",":")).encode()).hexdigest()==h)
 src=read(SRC);ck("source_f84_free",src and all(not x["page"].startswith("f84") for x in src))
 loc=defaultdict(set)
 for x in src:loc[(x["page"],x["record_id"])].add(x["locus"])
 bp=defaultdict(list)
 for k,v in loc.items():
  if len(v)>=4:bp[k[0]].append(k[1])
 pages={p:sorted(v) for p,v in bp.items() if len(v)==2};ck("binary_panel",len(pages)==9 and all(len(v)==2 for v in pages.values()))
 ck("zero_same_ordinal_decoys",all(len({"EARLIER" if r==rs[0] else "LATER" for r in rs})==2 for rs in pages.values()))
 pred=read("gdt266_residual_predictions.tsv");ck("predictions",len(pred)==1152)
 block={m:defaultdict(int) for m in MODES};seen=set();agg=Counter();pp=defaultdict(Counter)
 for x in pred:
  k=(x["representation"],x["held_page"],x["record_id"],int(x["split_index"]),x["direction"]);ck("unique:"+"|".join(map(str,k)),k not in seen);seen.add(k)
  ck("page",x["held_page"] in pages);rs=pages[x["held_page"]];ck("ordinal",x["record_ordinal_class"]==("EARLIER" if x["record_id"]==rs[0] else "LATER"));ck("held_out",x["held_page"] not in x["train_pages"].split(";") and len(x["train_pages"].split(";"))==8)
  good=int(x["top1"]);ck("rank",int(x["rank"])==(1 if good else 2));block[x["representation"]][(x["held_page"],int(x["split_index"]))]+=good;agg[x["representation"]]+=good;pp[x["representation"]][x["held_page"]]+=good
 scores={x["representation"]:x for x in read("gdt266_residual_scores.tsv")};rng=random.Random(26620260817);vals={m:[] for m in MODES};maxv=[]
 for _ in range(4096):
  flips={(p,si):rng.randrange(2) for p in pages for si in range(4)};w={m:sum((4-block[m][k]) if flips[k] else block[m][k] for k in block[m]) for m in MODES}
  for m in MODES:vals[m].append(w[m])
  maxv.append(max(w.values()))
 for m in MODES:
  x=scores[m];o=agg[m];lp=(1+sum(v>=o for v in vals[m]))/4097;mp=(1+sum(v>=o for v in maxv))/4097
  ck("score:"+m,int(x["correct"])==o and int(x["positive_held_pages"])==sum(v>8 for v in pp[m].values()) and abs(float(x["local_inclusive_p"])-lp)<5e-10 and abs(float(x["max_eight_inclusive_p"])-mp)<5e-10)
 ck("stopped",z["status"]=="ORDINAL_RESIDUAL_MATE_TEST_UNIDENTIFIABLE_NO_SAME_ORDINAL_CONTROL" and z["valid_primary_score"] is False and z["semantic_assignments"]==0)
 v={"experiment":"GDT266_Q13_ORDINAL_RESIDUAL_FINGERPRINT","status":"PASS_STOP_AND_DIAGNOSTIC_ARITHMETIC","checks_passed":len(c),"checks_failed":0,"result_sha256":sha(RES),"result_content_hash":z["content_hash"],"scope":"Validates the fatal same-ordinal/decoy confound, hashes, retained diagnostic predictions, and null arithmetic; it does not promote a scientific score.","f84r":{"new_access":False,"used":False,"scored":False},"checks":c};v["content_hash"]=hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":")).encode()).hexdigest();(R/"gdt266_validation.json").write_text(json.dumps(v,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":v["status"],"checks":len(c)},sort_keys=True))
if __name__=="__main__":main()
