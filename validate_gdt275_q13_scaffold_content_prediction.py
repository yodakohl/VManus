#!/usr/bin/env python3
"""Independent reconstruction of the completed GDT275 terminal scaffold test."""
import csv,hashlib,json,math,random,statistics
from collections import Counter,defaultdict
from pathlib import Path
R=Path(__file__).resolve().parent;W=2048;BP=8.0;SP=512.0;TS=("PAGE_HOST","RAW")
def read(n):
 with (R/n).open(encoding="utf-8",newline="") as h:return list(csv.DictReader(h,delimiter="\t"))
def sha(n):return hashlib.sha256((R/n).read_bytes()).hexdigest()
def ch(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def build():
 r=read("gdt227_q13_abstract_interlinear.tsv");by=defaultdict(list)
 for x in r:by[(x["record_id"],x["locus"])].append(x)
 out=[]
 for k,a in sorted(by.items()):
  a.sort(key=lambda x:int(x["field_ordinal"]));t=tuple(("S12" if int(x["field_group_count"])<=2 else "L3P",x["line_field_end"]) for x in a);rn=int(a[0]["record_field_count"])
  for slot,x in enumerate(a):
   n=int(x["field_group_count"]);q=min(3,int((int(x["field_ordinal"])/rn)*4));p="ONLY" if len(a)==1 else "FIRST" if slot==0 else "LAST" if slot==len(a)-1 else "MIDDLE";base=(n,x["line_field_end"],len(a),p,q)
   aa=x["source_tokens"].split("|");bb=x["page_hosts"].split("|")
   for raw,host in zip(aa,bb):out.append({"folio":x["physical_folio"],"base":base,"context":(t,slot),"RAW":raw,"PAGE_HOST":host})
 return r,out
def score(ev,t):
 ff={}
 for held in sorted({x["folio"] for x in ev}):
  tr=[x for x in ev if x["folio"]!=held];te=[x for x in ev if x["folio"]==held];g=Counter(x[t] for x in tr);b=defaultdict(Counter);m=defaultdict(Counter)
  for x in tr:b[x["base"]][x[t]]+=1;m[x["context"]][x[t]]+=1
  V=len(g);N=sum(g.values());z=0.0
  for x in te:
   y=x[t];bc=b[x["base"]];pg=(g[y]+.5)/(N+.5*V);pb=(bc[y]+BP*pg)/(sum(bc.values())+BP);mc=m[x["context"]];pm=(mc[y]+SP*pb)/(sum(mc.values())+SP);z+=math.log2(pm/pb)
  ff[held]=z
 return sum(ff.values()),ff
def main():
 c=[]
 def ck(n,v):
  c.append({"check":n,"pass":bool(v)})
  if not v:raise AssertionError(n)
 src,ev=build();ck("source_701",len(src)==701);ck("source_no_f84",all(not x["page"].startswith("f84") for x in src));ck("events_1896",len(ev)==1896);ck("folios_9",len({x["folio"] for x in ev})==9)
 tests={x["target"]:x for x in read("gdt275_tests.tsv")};folds=read("gdt275_lofo_folds.tsv");obs={}
 for t in TS:
  g,f=score(ev,t);obs[t]=(g,f);ck(t+"_gain",abs(g-float(tests[t]["held_gain_bits"]))<1e-9);ex={x["held_folio"]:float(x["gain_bits"]) for x in folds if x["target"]==t};ck(t+"_folds",set(ex)==set(f) and all(abs(ex[k]-v)<1e-9 for k,v in f.items()))
 s=defaultdict(list)
 for i,x in enumerate(ev):s[(x["folio"],x["base"])].append(i)
 ck("strata_564",len(s)==564);ck("mobile_1737",sum(len(v) for v in s.values() if len(v)>1)==1737);orig=[(x["RAW"],x["PAGE_HOST"]) for x in ev];null={t:[] for t in TS}
 for world in range(W):
  rng=random.Random(int(hashlib.sha256(f"GDT275_SCAFFOLD_CONTENT_NULL_V1|{world}".encode()).hexdigest()[:16],16))
  for ids in s.values():
   vals=[orig[i] for i in ids];rng.shuffle(vals)
   for i,(a,b) in zip(ids,vals):ev[i]["RAW"]=a;ev[i]["PAGE_HOST"]=b
  for t in TS:null[t].append(score(ev,t)[0])
 for i,(a,b) in enumerate(orig):ev[i]["RAW"]=a;ev[i]["PAGE_HOST"]=b
 means={t:statistics.mean(null[t]) for t in TS};sd={t:statistics.pstdev(null[t]) for t in TS};z={t:(obs[t][0]-means[t])/sd[t] for t in TS};mx=[max((null[t][i]-means[t])/sd[t] for t in TS) for i in range(W)]
 for t in TS:
  mp=(1+sum(v>=z[t]-1e-12 for v in mx))/(W+1);x=tests[t];ck(t+"_mean",abs(means[t]-float(x["null_mean"]))<1e-9);ck(t+"_z",abs(z[t]-float(x["z"]))<1e-9);ck(t+"_max2",abs(mp-float(x["max_two_p"]))<1e-12)
 result=json.loads((R/"gdt275_result.json").read_text());h=result.pop("content_hash");ck("result_hash",h==ch(result));result["content_hash"]=h;ck("status",result["status"]=="Q13_REUSABLE_SCAFFOLD_DOES_NOT_PREDICT_EXACT_CONTENT_IDENTITY" and result["gate_pass"] is False);ck("counts",(result["events"],result["folios"],result["nuisance_strata"],result["movable_events"],result["worlds"])==(1896,9,564,1737,2048));ck("hashes",all(sha(k)==v for group in (result["inputs"],result["documents"],result["implementation"],result["outputs"]) for k,v in group.items()));ck("no_semantics",result["semantic_assignments"]==0);ck("no_f84",all(v is False for v in result["f84r"].values()))
 p={"experiment":"GDT275_Q13_SCAFFOLD_CONTENT_PREDICTION_VALIDATION","status":"PASS","checks_passed":len(c),"checks_total":len(c),"result_sha256":sha("gdt275_result.json"),"validator_sha256":sha(Path(__file__).name),"checks":c};p["content_hash"]=ch(p);(R/"gdt275_validation.json").write_text(json.dumps(p,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":"PASS","checks":len(c)},sort_keys=True))
if __name__=="__main__":main()
