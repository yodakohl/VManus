#!/usr/bin/env python3
"""Nonimporting panel, hash, prediction, and exact-null validation for GDT265."""
import csv,hashlib,json,math
from collections import Counter,defaultdict
from pathlib import Path
R=Path(__file__).resolve().parent;RES="gdt265_result.json";SRC="gdt227_q13_abstract_interlinear.tsv"
MODES=["STRUCTURE_ONLY","WRAPPER","RIGHT","COMPILER","RAW_EXACT","PAGE_HOST_EXACT","RAW_CHAR3","PAGE_HOST_CHAR3"]
def read(p):
 with (R/p).open(encoding="utf-8") as f:return list(csv.DictReader(f,delimiter="\t"))
def sha(p):return hashlib.sha256((R/p).read_bytes()).hexdigest()
def main():
 c=[]
 def ck(n,v):assert v,n;c.append(n)
 z=json.loads((R/RES).read_text())
 for group in ["inputs","documents","outputs","implementation"]:
  for p,h in z[group].items():ck("hash:"+p,sha(p)==h)
 q=dict(z);h=q.pop("content_hash");ck("content_hash",hashlib.sha256(json.dumps(q,sort_keys=True,separators=(",",":")).encode()).hexdigest()==h)
 src=read(SRC);ck("source_f84_free",src and all(not x["page"].startswith("f84") for x in src))
 loc=defaultdict(set)
 for x in src:loc[(x["page"],x["record_id"])].add(x["locus"])
 bp=defaultdict(list)
 for k,v in loc.items():
  if len(v)>=4:bp[k[0]].append(k[1])
 pages={p:sorted(v) for p,v in bp.items() if len(v)==2};ck("panel_9x2",len(pages)==9 and sum(map(len,pages.values()))==18)
 for p,rs in pages.items():ck("ordered:"+p,int(rs[0].rsplit("R",1)[-1])<int(rs[1].rsplit("R",1)[-1]))
 pred=read("gdt265_record_ordinal_predictions.tsv");ck("predictions_576",len(pred)==576)
 seen=set();agg=Counter();pp=defaultdict(Counter)
 for x in pred:
  k=(x["representation"],x["held_page"],int(x["split_index"]),x["view"]);ck("pred_unique:"+"|".join(map(str,k)),k not in seen);seen.add(k)
  ck("mode",x["representation"] in MODES);ck("held_page",x["held_page"] in pages);ck("records",[x["held_record_earlier"],x["held_record_later"]]==pages[x["held_page"]]);ck("fold_excludes_held",x["held_page"] not in x["train_pages"].split(";") and len(x["train_pages"].split(";"))==8)
  direct=float(x["direct_orientation_score"]);swap=float(x["swapped_orientation_score"]);good=int(x["correct"]);ck("orientation",good==int(direct>=swap) and x["predicted_orientation"]==("DIRECT" if good else "SWAPPED"))
  agg[x["representation"]]+=good;pp[x["representation"]][x["held_page"]]+=good
 scores={x["representation"]:x for x in read("gdt265_record_ordinal_scores.tsv")};ck("score_modes",set(scores)==set(MODES))
 null=read("gdt265_record_ordinal_null.tsv");ck("null_512",len(null)==512 and len({x["flip_bits"] for x in null})==512)
 maxcount=[max(int(x[m]) for m in MODES) for x in null]
 for m in MODES:
  x=scores[m];o=agg[m];ck("aggregate:"+m,int(x["correct"])==o and int(x["positive_held_pages"])==sum(v>4 for v in pp[m].values()))
  vals=[int(y[m]) for y in null];lp=(1+sum(v>=o for v in vals))/513;mp=(1+sum(v>=o for v in maxcount))/513
  ck("null_p:"+m,abs(float(x["local_inclusive_p"])-lp)<5e-10 and abs(float(x["max_eight_inclusive_p"])-mp)<5e-10 and abs(float(x["null_mean_correct"])-sum(vals)/512)<5e-10)
 ck("headline",z["status"]=="WRAPPER_RECORD_ORDINAL_TRANSFER_BORDERLINE" and z["best_representation"]=="WRAPPER" and z["wrapper_correct"]==62 and abs(z["wrapper_max_eight_p"]-0.101364522417)<1e-12)
 v={"experiment":"GDT265_Q13_RECORD_ORDINAL_TRANSFER","status":"PASS_PANEL_PREDICTION_NULL_ARITHMETIC","checks_passed":len(c),"checks_failed":0,"result_sha256":sha(RES),"result_content_hash":z["content_hash"],"scope":"Does not independently refit TF-IDF centroids; validates source panel, held-page separation, retained scores, complete exact null, hashes, and claims.","f84r":{"new_access":False,"used":False,"scored":False},"checks":c};v["content_hash"]=hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":")).encode()).hexdigest();(R/"gdt265_validation.json").write_text(json.dumps(v,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":v["status"],"checks":len(c)},sort_keys=True))
if __name__=="__main__":main()
