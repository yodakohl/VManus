#!/usr/bin/env python3
"""Independent non-importing validator for scored GDT271."""
import csv,hashlib,itertools,json,math
from collections import Counter,defaultdict
from math import comb
from pathlib import Path
R=Path(__file__).resolve().parent;SRC="gdt127_q20_field_inventory.tsv";PRED="gdt271_frozen_prediction.json";RESULT="gdt271_result.json";METHOD="GDT271_Q20_Q_OUTER_LAYER_TRANSFER_METHOD.md";RUNNER="run_gdt271_q20_q_outer_layer_transfer.py";EDS=("ZL3b","IT2a","RF1b")
VARIANTS=[("PAGE_HOST_PAGE_OTHER_COMPILER",("page","page_host","other_compiler")),("PAGE_HOST_PAGE_OTHER_COMPILER_WITHIN_FIELD_POSITION",("page","page_host","other_compiler","within_field_position")),("PAGE_HOST_PAGE_OTHER_COMPILER_LOCAL_STRUCTURE",("page","page_host","other_compiler","local_structure"))]
def read(name):
 with (R/name).open(encoding="utf-8",newline="") as h:return list(csv.DictReader(h,delimiter="\t"))
def sha(name):return hashlib.sha256((R/name).read_bytes()).hexdigest()
def close(a,b,t=8e-10):return abs(float(a)-float(b))<=t
def occ(rows,ed):
 pages=defaultdict(set)
 for x in rows:
  if x["edition"]==ed:pages[x["page"]].add(int(x["star_ordinal"]))
 sel={}
 for p,ss in pages.items():ss=sorted(ss);k=len(ss)//2;sel[p]={s:0 for s in ss[:k]};sel[p].update({s:1 for s in ss[-k:]})
 out=[]
 for x in rows:
  if x["edition"]!=ed or int(x["star_ordinal"]) not in sel[x["page"]]:continue
  hs=x["page_hosts"].split("|");cs=json.loads(x["compiler_skeleton"]);ts=x["group_tokens"].split("|")
  for i,(h,c,tok) in enumerate(zip(hs,cs,ts)):
   w,frame,right,inner,dy,b3=c
   if w not in {"q","NONE"}:continue
   pos="SINGLE" if len(hs)==1 else "FIRST" if i==0 else "LAST" if i==len(hs)-1 else "MIDDLE";end="DY" if int(x["ends_dy"]) else "B3" if int(x["ends_b3"]) else "OPEN"
   out.append({"edition":ed,"page":x["page"],"physical_folio":x["physical_folio"],"star_ordinal":str(int(x["star_ordinal"])),"stage":"EARLY" if sel[x["page"]][int(x["star_ordinal"])]==0 else "LATE","stage_binary":str(sel[x["page"]][int(x["star_ordinal"])]),"record_scope":x["record_scope"],"locus":x["locus"],"line_depth":x["line_depth"],"field_index":x["field_index"],"page_host":h,"wrapper":w,"frame":frame,"inner_d":str(inner),"right_family":right,"dy":str(dy),"b3":str(b3),"other_compiler":":".join(map(str,(frame,inner,right,dy,b3))),"within_field_position":pos,"field_end":end,"local_structure":pos+":"+end,"source_token":tok})
 return sorted(pages),out
def calc(keys,rows,pages):
 g=defaultdict(Counter)
 for x in rows:g[tuple(x[k] for k in keys)][x["wrapper"],int(x["stage_binary"])]+=1
 mob=[]
 for key,c in g.items():
  n=sum(c.values());q=c["q",0]+c["q",1];e=c["q",0]+c["NONE",0];lo=max(0,q-(n-e));hi=min(q,e)
  if hi>lo:mob.append((key,c,n,q,e,lo,hi))
 num=den=score=var=0.0;A=0;dist={0:1.0};ps=defaultdict(float)
 for key,c,n,q,e,lo,hi in mob:
  a,b,cc,d=c["q",0],c["q",1],c["NONE",0],c["NONE",1];num+=a*d/n;den+=b*cc/n;delta=a-q*e/n;score+=delta;ps[key[0]]+=delta;A+=a;var+=q*(n-q)*e*(n-e)/(n*n*(n-1));di={v:comb(e,v)*comb(n-e,q-v)/comb(n,q) for v in range(lo,hi+1)};new=defaultdict(float)
  for total,p0 in dist.items():
   for v,p1 in di.items():new[total+v]+=p0*p1
  dist=dict(new)
 mu=sum(v*p for v,p in dist.items());upper=sum(p for v,p in dist.items() if v>=A);two=sum(p for v,p in dist.items() if abs(v-mu)>=abs(A-mu)-1e-12);pv=[ps[p] for p in pages];norm=math.sqrt(sum(v*v for v in pv));stat=sum(pv)/norm if norm else 0
 return {"mov":len(mob),"occ":sum(x[2] for x in mob),"hosts":len({x[0][1] for x in mob}),"pages":len({x[0][0] for x in mob}),"u":score,"z":score/math.sqrt(var),"or":num/den,"upper":upper,"two":two,"pos":sum(v>0 for v in pv),"neg":sum(v<0 for v in pv),"tie":sum(v==0 for v in pv),"stat":stat,"pv":pv}
def main():
 checks=[]
 def ck(n,v):assert v,n;checks.append(n)
 src=read(SRC);ck("source_no_f84",all(not x["page"].startswith("f84") for x in src));reb=[];values={};tests={(x["edition"],x["variant"]):x for x in read("gdt271_tests.tsv")}
 for ed in EDS:
  pages,rows=occ(src,ed);reb.extend(rows);vals=[]
  for name,keys in VARIANTS:
   v=calc(keys,rows,pages);vals.append(v);values[ed,name]=v;x=tests[ed,name];ck(ed+name+"_capacity",int(x["movable_strata"])==v["mov"] and int(x["mobile_occurrences"])==v["occ"] and int(x["mobile_hosts"])==v["hosts"] and int(x["mobile_pages"])==v["pages"]);ck(ed+name+"_effect",close(x["conditional_u"],v["u"]) and close(x["conditional_z"],v["z"]) and close(x["mh_odds_ratio"],v["or"]) and close(x["exact_directional_upper_p"],v["upper"]) and close(x["exact_two_sided_p"],v["two"]));ck(ed+name+"_directions",int(x["positive_pages"])==v["pos"] and int(x["negative_pages"])==v["neg"] and int(x["tied_pages"])==v["tie"])
  worlds=[]
  for signs in itertools.product((-1,1),repeat=13):
   worlds.append([sum(s*y for s,y in zip(signs,v["pv"]))/math.sqrt(sum(y*y for y in v["pv"])) for v in vals])
  maxima=[max(w) for w in worlds]
  for i,(name,_) in enumerate(VARIANTS):
   local=(1+sum(w[i]>=vals[i]["stat"]-1e-12 for w in worlds))/8193;maxp=(1+sum(w>=vals[i]["stat"]-1e-12 for w in maxima))/8193;ck(ed+name+"_null",close(tests[ed,name]["page_sign_directional_p"],local) and close(tests[ed,name]["page_sign_max_three_p"],maxp))
 ck("inventory_counts",len(reb)==3735+3626+3676);pred=json.loads((R/PRED).read_text());ck("freeze_hash",sha(PRED)==json.loads((R/RESULT).read_text())["freeze_prediction_sha256"]);res=json.loads((R/RESULT).read_text());stored=res.pop("content_hash");ck("result_content",stored==hashlib.sha256(json.dumps(res,sort_keys=True,separators=(",",":")).encode()).hexdigest());ck("inputs",all(sha(n)==v for n,v in res["inputs"].items()));ck("outputs",all(sha(n)==v for n,v in res["outputs"].items()));ck("method",res["documents"][METHOD]==sha(METHOD));ck("runner",res["implementation"][RUNNER]==sha(RUNNER));p=values["ZL3b","PAGE_HOST_PAGE_OTHER_COMPILER"];gate=p["u"]>0 and p["pos"]>=pred["primary_gate"]["positive_pages_min"] and float(tests["ZL3b","PAGE_HOST_PAGE_OTHER_COMPILER"]["page_sign_max_three_p"])<=pred["primary_gate"]["page_sign_max_three_p_max"];ck("gate",res["gate_pass"]==gate);ck("status",res["status"]==("Q13_Q_OUTER_STAGE_TRANSFERS_TO_Q20_COMPILER_MATCHED" if gate else "Q13_Q_OUTER_STAGE_Q20_COMPILER_MATCHED_TRANSFER_NONCONFIRMING"));ck("claim_flags",res["semantic_assignments"]==0 and not res["f84r"]["new_access"] and not res["f84r"]["used"] and not res["f84r"]["scored"])
 val={"experiment":"GDT271_Q20_Q_OUTER_LAYER_TRANSFER","status":"PASS","checks_passed":len(checks),"checks":checks,"independent_reconstruction":True,"result_sha256":sha(RESULT),"validator_sha256":sha(Path(__file__).name),"f84r_accessed":False};(R/"gdt271_validation.json").write_text(json.dumps(val,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":"PASS","checks":len(checks),"gate":gate,"primary":{"u":p["u"],"or":p["or"],"positive_pages":p["pos"],"max3":float(tests["ZL3b","PAGE_HOST_PAGE_OTHER_COMPILER"]["page_sign_max_three_p"])}},sort_keys=True))
if __name__=="__main__":main()
