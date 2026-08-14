#!/usr/bin/env python3
"""Independent nonimporting validation of GDT029."""
from __future__ import annotations
import csv,hashlib,json,math,random
from collections import Counter,defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parent;RES=ROOT/"gdt029_result.json";VAL=ROOT/"gdt029_validation.json";A=.5;TRIALS=200000
MODELS=("PRIOR","CONTEXT","HISTORY","EXACT_HOST","EXACT_HOST_HISTORY","HOST_NGRAM","HOST_NGRAM_HISTORY","HOST_NGRAM_INTERACTION")
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def read(n):
 with (ROOT/n).open(encoding="utf-8",newline="")as h:return list(csv.DictReader(h,delimiter="\t"))
def branch(f):
 if"QJB"in f or"QKB"in f:return 1
 if"LJB"in f or"LKB"in f:return 0
 return None
def grams(s):
 p="^"+s+"$";return sorted({p[i:i+n]for n in(1,2,3)for i in range(len(p)-n+1)})
def feats(x,m):
 out=[]
 if m!="PRIOR":out +=["STATE="+x["state"],"POSITION="+str(x["position_bin"])]
 if m in("HISTORY","EXACT_HOST_HISTORY","HOST_NGRAM_HISTORY","HOST_NGRAM_INTERACTION"):out +=["PREVIOUS_DY="+str(x["previous_dy"])]
 if m in("EXACT_HOST","EXACT_HOST_HISTORY"):out +=["HOST="+x["host"]]
 if m in("HOST_NGRAM","HOST_NGRAM_HISTORY","HOST_NGRAM_INTERACTION"):
  g=grams(x["host"]);out +=["GRAM="+z for z in g]
  if m=="HOST_NGRAM_INTERACTION":out +=["HISTGRAM="+str(x["previous_dy"])+":"+z for z in g]
 return out
def score(data,train,test,m):
 nc=[0,0];counts=[Counter(),Counter()];tot=[0,0];vocab=set()
 for i in train:
  x=data[i];f=feats(x,m);nc[x["y"]]+=1;counts[x["y"]].update(f);tot[x["y"]]+=len(f);vocab.update(f)
 bits=0.;correct=0;v=max(1,len(vocab))
 for i in test:
  x=data[i];s=[math.log((nc[y]+A)/(len(train)+2*A))+sum(math.log((counts[y][f]+A)/(tot[y]+A*v))for f in feats(x,m))for y in(0,1)];peak=max(s);p=math.exp(s[1]-peak)/(math.exp(s[0]-peak)+math.exp(s[1]-peak));bits-=math.log2(p if x["y"]else 1-p);correct+=int((p>=.5)==bool(x["y"]))
 return bits,correct
def close(a,b):return abs(float(a)-float(b))<7e-10
def main():
 checks=[];result=json.loads(RES.read_text());body=dict(result);digest=body.pop("result_content_sha256");checks +=[("schema",result["schema"]=="GDT029_HOST_LICENSED_Q_L_GRAMMAR_RESULT_V1"),("content_hash",digest==csha(body)),("status",result["status"]=="HOST_LICENSED_Q_L_BRANCHING_SUPPORTED_HISTORY_INCREMENT_WEAK")]
 for section in("inputs","implementation","outputs"):
  for name,digest in result[section].items():checks.append((f"hash:{section}:{name}",sha(ROOT/name)==digest))
 inv=read("gdt016_group_state_inventory.tsv");checks +=[("inventory",len(inv)==15592),("f84r_absent",not any(r["locus"].startswith("f84r")for r in inv))];lines=defaultdict(list)
 for r in inv:lines[r["locus"]].append(r)
 data=[]
 for locus,line in lines.items():
  line.sort(key=lambda r:int(r["group_index"]))
  for i,r in enumerate(line):
   y=branch(r["family_surface"])
   if r["currier"]!="B"or y is None:continue
   n=int(r["group_count"]);z=(int(r["group_index"])-1)/(n-1)if n>1 else.5;data.append({"y":y,"folio":r["physical_folio"],"host":r["residual_host"],"state":r["record_state"],"position_bin":min(3,int(z*4)),"previous_dy":int(i>0 and line[i-1]["record_state"]=="DY_RESOLUTION")})
 stored={(r["protocol"],r["model"]):r for r in read("gdt029_heldout_model_comparison.tsv")};expected_folios=[]
 for protocol,field in(("LEAVE_ONE_PHYSICAL_FOLIO_OUT","folio"),("LEAVE_ONE_RESIDUAL_HOST_OUT","host")):
  vals=sorted({x[field]for x in data});sums={m:[0.,0]for m in MODELS}
  for value in vals:
   train=[i for i,x in enumerate(data)if x[field]!=value];test=[i for i,x in enumerate(data)if x[field]==value];fold={}
   for m in MODELS:
    bits,correct=score(data,train,test,m);sums[m][0]+=bits;sums[m][1]+=correct;fold[m]=bits
   if field=="folio":expected_folios.append({"held_folio":str(value),"groups":str(len(test)),"host_ngram_bits":f"{fold['HOST_NGRAM']:.12f}","host_ngram_history_bits":f"{fold['HOST_NGRAM_HISTORY']:.12f}","history_increment_gain_bits":f"{fold['HOST_NGRAM']-fold['HOST_NGRAM_HISTORY']:.12f}","exact_host_increment_gain_bits":f"{fold['EXACT_HOST']-fold['EXACT_HOST_HISTORY']:.12f}","claim_state":"HELD_FOLIO_FORMAL_PREDICTION_NOT_MEANING"})
  for m in MODELS:
   row=stored[(protocol,m)];checks.append((f"model:{protocol}:{m}",int(row["folds"])==len(vals)and int(row["groups"])==len(data)and close(row["heldout_bits"],sums[m][0])and close(row["bits_per_group"],sums[m][0]/len(data))and close(row["accuracy"],sums[m][1]/len(data))))
 folios=read("gdt029_folio_history_increment.tsv");checks.append(("folio_details",folios==expected_folios));gains=[float(r["history_increment_gain_bits"])for r in folios];observed=sum(gains);rng=random.Random(290029);extreme=sum(sum(x if rng.getrandbits(1)else-x for x in gains)>=observed-1e-15 for _ in range(TRIALS));p=(extreme+1)/(TRIALS+1);rng=random.Random(290030);boots=sorted(sum(rng.choice(gains)for _ in gains)for _ in range(TRIALS));lo,hi=boots[int(.025*TRIALS)],boots[int(.975*TRIALS)-1]
 fcounts=defaultdict(lambda:Counter());ffolios=defaultdict(lambda:defaultdict(set));total=Counter(x["y"]for x in data)
 for x in data:
  for g in grams(x["host"]):fcounts[g][x["y"]]+=1;ffolios[g][x["y"]].add(x["folio"])
 atlas=[]
 for g,c in fcounts.items():
  if sum(c.values())<10 or len(ffolios[g][0]|ffolios[g][1])<3:continue
  log=math.log2(((c[1]+.5)/(total[1]+.5))/((c[0]+.5)/(total[0]+.5)));atlas.append({"host_feature":g,"q_groups":str(c[1]),"l_groups":str(c[0]),"q_folios":str(len(ffolios[g][1])),"l_folios":str(len(ffolios[g][0])),"log2_q_vs_l_enrichment":f"{log:.12f}","direction":"Q"if log>0 else"L","claim_state":"ORTHOGRAPHIC_HOST_COMPATIBILITY_NOT_MEANING"})
 atlas.sort(key=lambda r:(-abs(float(r["log2_q_vs_l_enrichment"])),r["host_feature"]));checks.append(("atlas_exact",atlas==read("gdt029_host_compatibility_atlas.tsv")))
 checks +=[("counts",result["groups"]==len(data)==1633 and result["folios"]==len({x["folio"]for x in data})==40 and result["residual_hosts"]==len({x["host"]for x in data})==198 and result["models"]==len(MODELS)==8),("history",close(result["folio_history_increment_bits"],observed)and result["folio_history_positive"]==sum(x>0 for x in gains)==23 and close(result["folio_history_signflip_p"],p)and close(result["folio_history_bootstrap_95"][0],lo)and close(result["folio_history_bootstrap_95"][1],hi)),("snapshots",close(result["folio_context_bits"],stored[("LEAVE_ONE_PHYSICAL_FOLIO_OUT","CONTEXT")]["heldout_bits"])and close(result["folio_exact_host_bits"],stored[("LEAVE_ONE_PHYSICAL_FOLIO_OUT","EXACT_HOST")]["heldout_bits"])and close(result["folio_host_ngram_bits"],stored[("LEAVE_ONE_PHYSICAL_FOLIO_OUT","HOST_NGRAM")]["heldout_bits"])and close(result["host_holdout_ngram_bits"],stored[("LEAVE_ONE_RESIDUAL_HOST_OUT","HOST_NGRAM")]["heldout_bits"])),("flags",result["f84r"]=={"input_contains_rows":False,"opened":False,"retained":False,"joined":False,"scored":False})]
 report=" ".join((ROOT/"GDT029_HOST_LICENSED_Q_L_GRAMMAR_REPORT.md").read_text().lower().split());ledger=(ROOT/"GDT002_YOLO_LEDGER.tsv").read_text();checks +=[("claims",all(x in report for x in("host-conditioned construction lexicon","too small and unstable","not identified independently of host selection","f84r was not opened","no role"))),("ledger",ledger.count("GDT029_CKPT001")==1)]
 failures=[n for n,ok in checks if not ok];validation={"schema":"GDT029_HOST_LICENSED_Q_L_GRAMMAR_VALIDATION_V1","status":"PASS"if not failures else"FAIL","checks":len(checks),"failures":failures,"result_sha256":sha(RES),"validator_sha256":sha(Path(__file__)),"scope":"Independent reconstruction of all folio- and host-held naive-Bayes models, folio increments, sign-flip and bootstrap controls, compatibility atlas, hashes, f84r exclusion, ledger, and claims."};VAL.write_text(json.dumps(validation,indent=2,sort_keys=True)+"\n");print(json.dumps(validation,sort_keys=True));
 if failures:raise SystemExit(1)
if __name__=="__main__":main()
