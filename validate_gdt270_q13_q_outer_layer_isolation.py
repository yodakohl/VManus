#!/usr/bin/env python3
"""Independent reconstruction validator for GDT270."""
import csv,hashlib,itertools,json,math
from collections import Counter,defaultdict
from math import comb
from pathlib import Path
R=Path(__file__).resolve().parent;SRC="gdt227_q13_abstract_interlinear.tsv";RESULT="gdt270_result.json";METHOD="GDT270_Q13_Q_OUTER_LAYER_ISOLATION_METHOD.md";RUNNER="run_gdt270_q13_q_outer_layer_isolation.py"
VARIANTS=[("PAGE_HOST_PAGE",("page","page_host")),("PAGE_HOST_PAGE_RIGHT",("page","page_host","right_family")),("PAGE_HOST_PAGE_DY",("page","page_host","dy")),("PAGE_HOST_PAGE_B3",("page","page_host","b3")),("PAGE_HOST_PAGE_FRAME",("page","page_host","frame")),("PAGE_HOST_PAGE_INNER_D",("page","page_host","inner_d")),("PAGE_HOST_PAGE_RIGHT_CLOSURE",("page","page_host","right_closure")),("PAGE_HOST_PAGE_OTHER_COMPILER",("page","page_host","other_compiler")),("PAGE_HOST_PAGE_OTHER_COMPILER_WITHIN_FIELD_POSITION",("page","page_host","other_compiler","within_field_position")),("PAGE_HOST_PAGE_RIGHT_CLOSURE_WITHIN_FIELD_POSITION",("page","page_host","right_closure","within_field_position")),("PAGE_HOST_PAGE_OTHER_COMPILER_FIELD_END",("page","page_host","other_compiler","field_end")),("PAGE_HOST_PAGE_OTHER_COMPILER_LOCAL_STRUCTURE",("page","page_host","other_compiler","local_structure")),("PAGE_HOST_PAGE_OTHER_COMPILER_RELATIVE_QUARTILE",("page","page_host","other_compiler","relative_quartile")),("PAGE_HOST_PAGE_OTHER_COMPILER_ROLE",("page","page_host","other_compiler","field_role"))]
def read(name):
 with (R/name).open(encoding="utf-8",newline="") as h:return list(csv.DictReader(h,delimiter="\t"))
def sha(name):return hashlib.sha256((R/name).read_bytes()).hexdigest()
def close(a,b,t=6e-10):return abs(float(a)-float(b))<=t
def rebuild():
 src=read(SRC);assert all(not x["page"].startswith("f84") for x in src);rec=defaultdict(list);loc=defaultdict(set)
 for x in src:rec[x["page"],x["record_id"]].append(x);loc[x["page"],x["record_id"]].add(x["locus"])
 bp=defaultdict(list)
 for (p,r),s in loc.items():
  if len(s)>=4:bp[p].append(r)
 panel={p:sorted(v) for p,v in bp.items() if len(v)==2};out=[]
 for p,rs in sorted(panel.items()):
  for y,rid in enumerate(rs):
   for f in rec[p,rid]:
    hs=f["page_hosts"].split("|");cs=f["compiler_cells"].split("|");ts=f["source_tokens"].split("|")
    for i,(h,c,tok) in enumerate(zip(hs,cs,ts)):
     w,frame,inner,right,dy,b3=c.split(":")
     if w not in {"q","NONE"}:continue
     pos="SINGLE" if len(hs)==1 else "FIRST" if i==0 else "LAST" if i==len(hs)-1 else "MIDDLE";end=f["line_field_end"]
     out.append({"page":p,"physical_folio":f["physical_folio"],"record_id":rid,"ordinal_class":"EARLIER" if y==0 else "LATER","ordinal_binary":str(y),"locus":f["locus"],"field_ordinal":f["field_ordinal"],"field_role":f["abstract_role_like"],"relative_quartile":str(min(3,int(float(f["relative_position"])*4))),"within_field_position":pos,"field_end":end,"local_structure":pos+":"+end,"page_host":h,"wrapper":w,"frame":frame,"inner_d":inner,"right_family":right,"dy":dy,"b3":b3,"right_closure":":".join((right,dy,b3)),"other_compiler":":".join((frame,inner,right,dy,b3)),"source_token":tok,"claim_state":"OPAQUE_COMPILER_CELL_NO_GLOSS"})
 return panel,out
def calc(keys,occ,pages):
 g=defaultdict(Counter)
 for x in occ:g[tuple(x[k] for k in keys)][x["wrapper"],int(x["ordinal_binary"])]+=1
 mob=[]
 for key,c in g.items():
  n=sum(c.values());q=c["q",0]+c["q",1];e=c["q",0]+c["NONE",0];lo=max(0,q-(n-e));hi=min(q,e)
  if hi>lo:mob.append((key,c,n,q,e,lo,hi))
 num=den=score=var=0.0;A=0;dist={0:1.0};ps=defaultdict(float)
 for key,c,n,q,e,lo,hi in mob:
  a,b,cc,d=c["q",0],c["q",1],c["NONE",0],c["NONE",1];num+=a*d/n;den+=b*cc/n;delta=a-q*e/n;score+=delta;ps[key[0]]+=delta;A+=a;var+=q*(n-q)*e*(n-e)/(n*n*(n-1));di={v:comb(e,v)*comb(n-e,q-v)/comb(n,q) for v in range(lo,hi+1)};new=defaultdict(float)
  for s,p0 in dist.items():
   for v,p1 in di.items():new[s+v]+=p0*p1
  dist=dict(new)
 mu=sum(v*p for v,p in dist.items());two=sum(p for v,p in dist.items() if abs(v-mu)>=abs(A-mu)-1e-12);pv=[ps[p] for p in pages];norm=math.sqrt(sum(v*v for v in pv));stat=abs(sum(pv))/norm if norm else 0
 return {"all":len(g),"mov":len(mob),"occ":sum(x[2] for x in mob),"hosts":len({x[0][1] for x in mob}),"pages":len({x[0][0] for x in mob}),"or":num/den,"u":score,"z":score/math.sqrt(var),"two":two,"pv":pv,"stat":stat,"pos":sum(v>0 for v in pv),"neg":sum(v<0 for v in pv),"tie":sum(v==0 for v in pv)}
def main():
 checks=[]
 def ck(n,v):assert v,n;checks.append(n)
 panel,occ=rebuild();exp=read("gdt270_occurrences.tsv");ck("panel_9_18",len(panel)==9 and sum(map(len,panel.values()))==18);ck("occ_632",len(occ)==len(exp)==632);ck("inventory_exact",occ==exp);ck("f84_absent",all(not x["page"].startswith("f84") for x in occ));pages=sorted(panel);tests={x["variant"]:x for x in read("gdt270_tests.tsv")};values=[]
 for name,keys in VARIANTS:
  v=calc(keys,occ,pages);values.append(v);x=tests[name];ck(name+"_capacity",int(x["all_strata"])==v["all"] and int(x["movable_strata"])==v["mov"] and int(x["mobile_occurrences"])==v["occ"] and int(x["mobile_hosts"])==v["hosts"] and int(x["mobile_pages"])==v["pages"]);ck(name+"_effect",close(x["mh_odds_ratio"],v["or"]) and close(x["conditional_u"],v["u"]) and close(x["conditional_z"],v["z"]) and close(x["exact_two_sided_p"],v["two"]) and close(x["page_stat"],v["stat"]));ck(name+"_directions",int(x["positive_pages"])==v["pos"] and int(x["negative_pages"])==v["neg"] and int(x["tied_pages"])==v["tie"])
 worlds=[]
 for signs in itertools.product((-1,1),repeat=9):
  vals=[]
  for v in values:
   norm=math.sqrt(sum(x*x for x in v["pv"]));vals.append(abs(sum(s*x for s,x in zip(signs,v["pv"])))/norm if norm else 0)
  worlds.append(vals)
 maxima=[max(x) for x in worlds]
 for i,(name,_) in enumerate(VARIANTS):
  local=(1+sum(w[i]>=values[i]["stat"]-1e-12 for w in worlds))/513;maxp=(1+sum(w>=values[i]["stat"]-1e-12 for w in maxima))/513;ck(name+"_search_p",close(tests[name]["page_sign_local_p"],local) and close(tests[name]["page_sign_max_fourteen_p"],maxp))
 res=json.loads((R/RESULT).read_text());stored=res.pop("content_hash");ck("content_hash",stored==hashlib.sha256(json.dumps(res,sort_keys=True,separators=(",",":")).encode()).hexdigest());ck("input_hashes",all(sha(n)==h for n,h in res["inputs"].items()));ck("output_hashes",all(sha(n)==h for n,h in res["outputs"].items()));ck("method_hash",res["documents"][METHOD]==sha(METHOD));ck("runner_hash",res["implementation"][RUNNER]==sha(RUNNER));primary=values[7];position=values[8];fine=values[11];ck("primary_exact",close(res["primary"]["mh_odds_ratio"],primary["or"]) and close(res["primary"]["exact_two_sided_p"],primary["two"]));ck("position_exact",close(res["position_sensitivity"]["mh_odds_ratio"],position["or"]) and close(res["position_sensitivity"]["exact_two_sided_p"],position["two"]));ck("fine_exact",int(res["fine_local_structure"]["mobile_occurrences"])==fine["occ"] and close(res["fine_local_structure"]["exact_two_sided_p"],fine["two"]));ck("claim_flags",res["semantic_assignments"]==0 and not res["f84r"]["new_access"] and not res["f84r"]["used"] and not res["f84r"]["scored"])
 val={"experiment":"GDT270_Q13_Q_OUTER_LAYER_ISOLATION","status":"PASS","checks_passed":len(checks),"checks":checks,"independent_reconstruction":True,"result_sha256":sha(RESULT),"validator_sha256":sha(Path(__file__).name),"f84r_accessed":False};(R/"gdt270_validation.json").write_text(json.dumps(val,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":"PASS","checks":len(checks),"primary_or":primary["or"],"primary_p":primary["two"],"position_p":position["two"],"fine_p":fine["two"]},sort_keys=True))
if __name__=="__main__":main()
