#!/usr/bin/env python3
"""Independent reconstruction/validation for GDT264; does not import scorer."""
import csv,hashlib,json,math,random
from collections import Counter,defaultdict
from pathlib import Path
R=Path(__file__).resolve().parent
SRC="gdt227_q13_abstract_interlinear.tsv"; RES="gdt264_result.json"
REPS=["STRUCTURE_ONLY","COMPILER_COARSE","RAW_EXACT","PAGE_HOST_EXACT","RAW_CHAR3","PAGE_HOST_CHAR3"]
BLOCKS=["WRAPPER","FRAME_INNERD","RIGHT","CLOSURE","JOINT_CELL"]
SEEDS=["GDT264-S0","GDT264-S1","GDT264-S2","GDT264-S3"]
def rows(p):
 with (R/p).open(encoding="utf-8") as f:return list(csv.DictReader(f,delimiter="\t"))
def sha(p):return hashlib.sha256((R/p).read_bytes()).hexdigest()
def tri(s):
 z="^"+s+"$";return [z[i:i+3] for i in range(max(0,len(z)-2))]
def feat(rr,mode):
 o=Counter()
 for x in rr:
  ts=x["source_tokens"].split("|");hs=x["page_hosts"].split("|");cs=x["compiler_cells"].split("|")
  assert len(ts)==len(hs)==len(cs)==int(x["field_group_count"])
  if mode=="STRUCTURE_ONLY":
   n=int(x["field_group_count"]);o["SIZE:"+(str(n) if n<=4 else "5+")]+=1;o["END:"+x["line_field_end"]]+=1;o["CLASS:"+x["abstract_role_like"]]+=1
  elif mode=="COMPILER_COARSE":
   for c in cs:
    p=c.split(":")
    for k,v in zip(["WRAP","FRAME","INNERD","RIGHT","DY","B3"],p):o[k+":"+v]+=1
    o["CELL:"+c]+=1
  elif mode=="RAW_EXACT":
   for t in ts:o["RAW:"+t]+=1
  elif mode=="PAGE_HOST_EXACT":
   for h in hs:o["HOST:"+h]+=1
  elif mode=="RAW_CHAR3":
   for t in ts:
    for q in tri(t):o["R3:"+q]+=1
  elif mode=="PAGE_HOST_CHAR3":
   for h in hs:
    for q in tri(h):o["H3:"+q]+=1
  elif mode in BLOCKS:
   for c in cs:
    w,fr,ind,ri,dy,b3=c.split(":")
    if mode=="WRAPPER":o["WRAP:"+w]+=1
    elif mode=="FRAME_INNERD":o["FRAME:"+fr]+=1;o["INNERD:"+ind]+=1
    elif mode=="RIGHT":o["RIGHT:"+ri]+=1
    elif mode=="CLOSURE":o["DY:"+dy]+=1;o["B3:"+b3]+=1
    else:o["CELL:"+c]+=1
  else:raise AssertionError(mode)
 return o
def cos(a,b,idf):
 dot=aa=bb=0.0
 for k in set(a)|set(b):
  x=a.get(k,0)*idf.get(k,0);y=b.get(k,0)*idf.get(k,0);dot+=x*y;aa+=x*x;bb+=y*y
 return dot/math.sqrt(aa*bb) if aa and bb else 0.0
def main():
 checks=[]
 def ck(n,v):
  assert v,n;checks.append(n)
 result=json.loads((R/RES).read_text())
 for group in ["inputs","documents","outputs","implementation"]:
  for p,h in result[group].items():ck("hash:"+p,sha(p)==h)
 q=dict(result);h=q.pop("content_hash");ck("content_hash",hashlib.sha256(json.dumps(q,sort_keys=True,separators=(",",":")).encode()).hexdigest()==h)
 src=rows(SRC);ck("source_nonempty",bool(src));ck("source_f84_free",all(not x["page"].startswith("f84") for x in src))
 rec=defaultdict(list);loc=defaultdict(set)
 for x in src:rec[(x["page"],x["record_id"])].append(x);loc[(x["page"],x["record_id"])].add(x["locus"])
 bp=defaultdict(list)
 for k,v in loc.items():
  if len(v)>=4:bp[k[0]].append(k[1])
 pages={p:sorted(v) for p,v in bp.items() if len(v)==2}
 ck("nine_pages",len(pages)==9);ck("eighteen_records",sum(map(len,pages.values()))==18)
 views={}
 for p,rs in pages.items():
  for rid in rs:
   for si,seed in enumerate(SEEDS):
    ls=sorted(loc[(p,rid)],key=lambda z:hashlib.sha256((seed+"|"+z).encode()).hexdigest());cut=len(ls)//2
    ck("split_capacity:"+p+":"+rid+":"+str(si),cut>=2 and len(ls)-cut>=2)
    for vn,keep in [("A",set(ls[:cut])),("B",set(ls[cut:]))]:
     rr=[x for x in rec[(p,rid)] if x["locus"] in keep]
     for m in REPS+BLOCKS:views[(m,p,rid,si,vn)]=feat(rr,m)
 idfs={}
 for m in REPS+BLOCKS:
  vs=[v for k,v in views.items() if k[0]==m];df=Counter();n=len(vs)
  for v in vs:
   for z in v:df[z]+=1
  idfs[m]={z:math.log((1+n)/(1+d))+1 for z,d in df.items()}
 pred=rows("gdt264_record_fingerprint_predictions.tsv");ck("prediction_rows",len(pred)==864)
 pmap={(x["representation"],x["page"],x["record_id"],int(x["split_index"]),x["direction"]):x for x in pred};ck("prediction_unique",len(pmap)==864)
 block_counts={m:defaultdict(int) for m in REPS+BLOCKS};block_margin={m:defaultdict(float) for m in REPS+BLOCKS}
 top={m:0 for m in REPS+BLOCKS};marg={m:0.0 for m in REPS+BLOCKS}
 for m in REPS+BLOCKS:
  for p,rs in pages.items():
   for si in range(4):
    for sv,dv in [("A","B"),("B","A")]:
     for rid in rs:
      sc={c:cos(views[(m,p,rid,si,sv)],views[(m,p,c,si,dv)],idfs[m]) for c in rs};rank=sorted(rs,key=lambda c:(-sc[c],c));good=int(rank[0]==rid);other=[c for c in rs if c!=rid][0]
      top[m]+=good;marg[m]+=sc[rid]-sc[other];block_counts[m][(p,si)]+=good;block_margin[m][p]+=sc[rid]-sc[other]
      if m in REPS:
       x=pmap[(m,p,rid,si,sv+"_TO_"+dv)];ck("score:"+m+":"+p+":"+rid+":"+str(si)+":"+sv,abs(float(x["true_score"])-sc[rid])<5e-10 and abs(float(x["competitor_score"])-sc[other])<5e-10 and int(x["top1"])==good)
 scores={x["representation"]:x for x in rows("gdt264_record_fingerprint_scores.tsv")};comps={x["component"]:x for x in rows("gdt264_compiler_component_scores.tsv")}
 for m in REPS:
  x=scores[m];ck("aggregate:"+m,int(x["top1_correct"])==top[m] and abs(float(x["mean_true_minus_competitor"])-marg[m]/144)<5e-10 and int(x["positive_aggregate_pages"])==sum(v>0 for v in block_margin[m].values()))
 for m in BLOCKS:
  x=comps[m];ck("component:"+m,int(x["top1_correct"])==top[m] and abs(float(x["mean_true_minus_competitor"])-marg[m]/144)<5e-10)
 # Independent replay of shared-label null from reconstructed block counts.
 rng=random.Random(26420260817); vals={m:[] for m in REPS+BLOCKS};max6=[];max5=[]
 for _ in range(4096):
  flips={(p,si):rng.randrange(2) for p in pages for si in range(4)}
  w={}
  for m in REPS+BLOCKS:
   w[m]=sum((4-block_counts[m][k]) if flips[k] else block_counts[m][k] for k in block_counts[m]);vals[m].append(w[m])
  max6.append(max((w[m]-72)/6 for m in REPS));max5.append(max((w[m]-72)/6 for m in BLOCKS))
 for m in REPS:
  x=scores[m];o=top[m];lp=(1+sum(v>=o for v in vals[m]))/4097;mp=(1+sum(v>=(o-72)/6 for v in max6))/4097
  ck("null:"+m,abs(float(x["local_inclusive_p"])-lp)<5e-10 and abs(float(x["max_six_inclusive_p"])-mp)<5e-10)
 for m in BLOCKS:
  x=comps[m];o=top[m];lp=(1+sum(v>=o for v in vals[m]))/4097;mp=(1+sum(v>=(o-72)/6 for v in max5))/4097
  ck("component_null:"+m,abs(float(x["local_inclusive_p"])-lp)<5e-10 and abs(float(x["max_five_inclusive_p"])-mp)<5e-10)
 ck("headline",result["best_representation"]=="COMPILER_COARSE" and result["best_top1"]==90 and result["posthoc_compiler_decomposition"]["best_component"]=="WRAPPER" and result["posthoc_compiler_decomposition"]["top1"]==97)
 validation={"experiment":"GDT264_Q13_RECORD_FINGERPRINT","status":"PASS_INDEPENDENT_RECONSTRUCTION","checks_passed":len(checks),"checks_failed":0,"result_sha256":sha(RES),"result_content_hash":result["content_hash"],"f84r":{"new_access":False,"used":False,"scored":False},"checks":checks}
 validation["content_hash"]=hashlib.sha256(json.dumps(validation,sort_keys=True,separators=(",",":")).encode()).hexdigest();(R/"gdt264_validation.json").write_text(json.dumps(validation,indent=2,sort_keys=True)+"\n")
 print(json.dumps({"status":validation["status"],"checks":len(checks)},sort_keys=True))
if __name__=="__main__":main()
