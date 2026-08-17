#!/usr/bin/env python3
"""Independent reconstruction of GDT273 from the frozen field inventory."""
import csv,hashlib,json,math,random,statistics
from collections import Counter,defaultdict
from pathlib import Path

R=Path(__file__).resolve().parent
SRC="gdt227_q13_abstract_interlinear.tsv"
REPS=("SIZE2","SIZE4","END2","JOINT4")
WORLDS=4096
ALPHA=.5

def rows(name):
 with (R/name).open(encoding="utf-8",newline="") as h:return list(csv.DictReader(h,delimiter="\t"))
def sha(name):return hashlib.sha256((R/name).read_bytes()).hexdigest()
def content_hash(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def close(a,b,tol=1e-9):return abs(float(a)-float(b))<=tol
def st(row,rep):
 n=int(row["field_group_count"]);s2="S12" if n<=2 else "L3P";e=row["line_field_end"]
 if rep=="SIZE2":return s2
 if rep=="SIZE4":return "G1" if n==1 else "G2" if n==2 else "G3_5" if n<=5 else "G6P"
 if rep=="END2":return e
 return s2+"|"+e
def rb(n):return "R1_10" if n<=10 else "R11_20" if n<=20 else "R21P"
def values(seq,rep,perm=None):
 out={}
 for rid,rr in seq.items():
  vv=[st(x,rep) for x in rr]
  if perm is not None:vv=[vv[i] for i in perm[rid]]
  out[rid]=vv
 return out
def score(seq,vv,states):
 out={}
 for held in sorted({rr[0]["physical_folio"] for rr in seq.values()}):
  b=defaultdict(Counter);m=defaultdict(Counter)
  for rid,rr in seq.items():
   if rr[0]["physical_folio"]==held:continue
   n=len(rr);x=vv[rid]
   for i in range(1,n):
    q=min(3,int(((i+1)/n)*4));c=(rb(n),q);b[c][x[i]]+=1;m[c+(x[i-1],)][x[i]]+=1
  g=0.0
  for rid,rr in seq.items():
   if rr[0]["physical_folio"]!=held:continue
   n=len(rr);x=vv[rid]
   for i in range(1,n):
    q=min(3,int(((i+1)/n)*4));c=(rb(n),q);bc=b[c];mc=m[c+(x[i-1],)]
    pb=(bc[x[i]]+ALPHA)/(sum(bc.values())+ALPHA*len(states));pm=(mc[x[i]]+ALPHA)/(sum(mc.values())+ALPHA*len(states));g+=math.log2(pm/pb)
  out[held]=g
 return sum(out.values()),out
def repeats(vv):return sum(sum(a==b for a,b in zip(x,x[1:])) for x in vv.values())

def main():
 checks=[]
 def ck(name,ok):
  checks.append({"check":name,"pass":bool(ok)})
  if not ok:raise AssertionError(name)
 src=rows(SRC);ck("source_701",len(src)==701);ck("source_no_f84",all(not x["page"].startswith("f84") for x in src))
 seq=defaultdict(list)
 for x in src:seq[x["record_id"]].append(x)
 for rid in seq:seq[rid].sort(key=lambda x:int(x["field_ordinal"]));ck("ordinals_"+rid,[int(x["field_ordinal"]) for x in seq[rid]]==list(range(1,len(seq[rid])+1)))
 ck("records_33",len(seq)==33);ck("folios_9",len({x["physical_folio"] for x in src})==9)
 tests={x["representation"]:x for x in rows("gdt273_tests.tsv")};folds=rows("gdt273_lofo_folds.tsv");trans=rows("gdt273_transition_counts.tsv")
 ck("four_test_rows",set(tests)==set(REPS));ck("fold_rows_36",len(folds)==36)
 states={r:sorted({st(x,r) for x in src}) for r in REPS};obs={}
 for rep in REPS:
  vv=values(seq,rep);gain,ff=score(seq,vv,states[rep]);obs[rep]=(gain,ff,repeats(vv))
  ck(rep+"_gain",close(gain,tests[rep]["held_gain_bits"]));ck(rep+"_repeat",obs[rep][2]==int(tests[rep]["same_state_adjacencies"]))
  exported={x["held_folio"]:float(x["gain_bits"]) for x in folds if x["representation"]==rep};ck(rep+"_folds",set(exported)==set(ff) and all(close(exported[k],v) for k,v in ff.items()))
  cc=Counter()
  for x in vv.values():cc.update(zip(x,x[1:]))
  ex={(x["left_state"],x["right_state"]):int(x["count"]) for x in trans if x["representation"]==rep};ck(rep+"_transitions",cc==ex)
 ng={r:[] for r in REPS};nr={r:[] for r in REPS}
 for world in range(WORLDS):
  rng=random.Random(int(hashlib.sha256(f"GDT273_Q13_FIELD_SEQUENCE_NULL_V1|{world}".encode()).hexdigest()[:16],16));perm={}
  for rid,rr in sorted(seq.items()):
   ix=list(range(len(rr)));rng.shuffle(ix);perm[rid]=ix
  for rep in REPS:
   vv=values(seq,rep,perm);ng[rep].append(score(seq,vv,states[rep])[0]);nr[rep].append(repeats(vv))
 gm={r:statistics.mean(ng[r]) for r in REPS};gs={r:statistics.pstdev(ng[r]) for r in REPS};rm={r:statistics.mean(nr[r]) for r in REPS};rs={r:statistics.pstdev(nr[r]) for r in REPS}
 gz={r:(obs[r][0]-gm[r])/gs[r] for r in REPS};rz={r:(obs[r][2]-rm[r])/rs[r] for r in REPS};mxg=[max((ng[r][i]-gm[r])/gs[r] for r in REPS) for i in range(WORLDS)];mxr=[max(abs((nr[r][i]-rm[r])/rs[r]) for r in REPS) for i in range(WORLDS)]
 for rep in REPS:
  mg=(1+sum(x>=gz[rep]-1e-12 for x in mxg))/(WORLDS+1);mr=(1+sum(x>=abs(rz[rep])-1e-12 for x in mxr))/(WORLDS+1);x=tests[rep]
  ck(rep+"_null_gain",close(gm[rep],x["null_gain_mean"]));ck(rep+"_gain_z",close(gz[rep],x["gain_z"]));ck(rep+"_gain_max4",close(mg,x["gain_max_four_p"]));ck(rep+"_null_repeat",close(rm[rep],x["null_repeat_mean"]));ck(rep+"_repeat_z",close(rz[rep],x["repeat_z"]));ck(rep+"_repeat_max4",close(mr,x["repeat_max_four_p"]))
 result=json.loads((R/"gdt273_result.json").read_text());stored=result.pop("content_hash");ck("result_content_hash",stored==content_hash(result));result["content_hash"]=stored
 ck("result_status",result["status"]=="Q13_FIELD_ORDER_NOT_PREDICTIVE_BEYOND_POSITION_AND_RECORD_SIZE" and result["gate_pass"] is False)
 ck("result_counts",(result["records"],result["fields"],result["transitions"],result["folios"],result["worlds"])==(33,701,668,9,4096))
 ck("input_hashes",all(sha(k)==v for k,v in result["inputs"].items()));ck("document_hashes",all(sha(k)==v for k,v in result["documents"].items()));ck("implementation_hash",all(sha(k)==v for k,v in result["implementation"].items()));ck("output_hashes",all(sha(k)==v for k,v in result["outputs"].items()))
 ck("semantic_none",result["semantic_assignments"]==0);ck("f84_flags",all(v is False for v in result["f84r"].values()))
 payload={"experiment":"GDT273_Q13_FIELD_SEQUENCE_GRAMMAR_VALIDATION","status":"PASS","checks_passed":len(checks),"checks_total":len(checks),"result_sha256":sha("gdt273_result.json"),"validator_sha256":sha(Path(__file__).name),"checks":checks};payload["content_hash"]=content_hash(payload);(R/"gdt273_validation.json").write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":"PASS","checks":len(checks)},sort_keys=True))
if __name__=="__main__":main()
