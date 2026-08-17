#!/usr/bin/env python3
"""Score the published GDT271 Q20 q outer-layer transfer."""
import csv,hashlib,itertools,json,math
from collections import Counter,defaultdict
from math import comb
from pathlib import Path
R=Path(__file__).resolve().parent;SRC="gdt127_q20_field_inventory.tsv";PRED="gdt271_frozen_prediction.json";METHOD="GDT271_Q20_Q_OUTER_LAYER_TRANSFER_METHOD.md";EDS=("ZL3b","IT2a","RF1b")
VARIANTS=[("PAGE_HOST_PAGE_OTHER_COMPILER",("page","page_host","other_compiler")),("PAGE_HOST_PAGE_OTHER_COMPILER_WITHIN_FIELD_POSITION",("page","page_host","other_compiler","within_field_position")),("PAGE_HOST_PAGE_OTHER_COMPILER_LOCAL_STRUCTURE",("page","page_host","other_compiler","local_structure"))]
def read(name):
 with (R/name).open(encoding="utf-8",newline="") as h:return list(csv.DictReader(h,delimiter="\t"))
def write(name,rows):
 with (R/name).open("w",encoding="utf-8",newline="") as h:w=csv.DictWriter(h,fieldnames=list(rows[0]),delimiter="\t",lineterminator="\n");w.writeheader();w.writerows(rows)
def sha(name):return hashlib.sha256((R/name).read_bytes()).hexdigest()
def chash(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def occurrences(rows,ed):
 pages=defaultdict(set)
 for x in rows:
  if x["edition"]==ed:pages[x["page"]].add(int(x["star_ordinal"]))
 selected={}
 for page,values in pages.items():
  stars=sorted(values);k=len(stars)//2;selected[page]={s:0 for s in stars[:k]};selected[page].update({s:1 for s in stars[-k:]})
 out=[]
 for x in rows:
  if x["edition"]!=ed:continue
  page=x["page"];star=int(x["star_ordinal"])
  if star not in selected[page]:continue
  hosts=x["page_hosts"].split("|");cells=json.loads(x["compiler_skeleton"]);tokens=x["group_tokens"].split("|");assert len(hosts)==len(cells)==len(tokens)
  for index,(host,cell,token) in enumerate(zip(hosts,cells,tokens)):
   wrapper,frame,right,inner,dy,b3=cell
   if wrapper not in {"q","NONE"}:continue
   pos="SINGLE" if len(hosts)==1 else "FIRST" if index==0 else "LAST" if index==len(hosts)-1 else "MIDDLE";end="DY" if int(x["ends_dy"]) else "B3" if int(x["ends_b3"]) else "OPEN"
   out.append({"edition":ed,"page":page,"physical_folio":x["physical_folio"],"star_ordinal":star,"stage":"EARLY" if selected[page][star]==0 else "LATE","stage_binary":selected[page][star],"record_scope":x["record_scope"],"locus":x["locus"],"line_depth":x["line_depth"],"field_index":x["field_index"],"page_host":host,"wrapper":wrapper,"frame":frame,"inner_d":str(inner),"right_family":right,"dy":str(dy),"b3":str(b3),"other_compiler":":".join(map(str,(frame,inner,right,dy,b3))),"within_field_position":pos,"field_end":end,"local_structure":pos+":"+end,"source_token":token})
 return sorted(pages),selected,out
def evaluate(ed,name,keys,occ,pages):
 grouped=defaultdict(Counter)
 for x in occ:grouped[tuple(str(x[k]) for k in keys)][x["wrapper"],int(x["stage_binary"])]+=1
 mobile=[];rows=[]
 for key,c in sorted(grouped.items()):
  a,b,cc,d=c["q",0],c["q",1],c["NONE",0],c["NONE",1];n=a+b+cc+d;q=a+b;e=a+cc;lo=max(0,q-(n-e));hi=min(q,e)
  if hi>lo:
   mobile.append((key,c,n,q,e,lo,hi));rows.append({"edition":ed,"variant":name,"stratum_key":json.dumps(dict(zip(keys,key)),sort_keys=True,separators=(",",":")),"q_early":a,"q_late":b,"none_early":cc,"none_late":d,"occurrences":n,"expected_q_early":f"{q*e/n:.12f}","score":f"{a-q*e/n:.12f}"})
 num=den=score=var=0.0;A=0;dist={0:1.0};ps=defaultdict(float)
 for key,c,n,q,e,lo,hi in mobile:
  a,b,cc,d=c["q",0],c["q",1],c["NONE",0],c["NONE",1];num+=a*d/n;den+=b*cc/n;delta=a-q*e/n;score+=delta;ps[key[0]]+=delta;A+=a;var+=q*(n-q)*e*(n-e)/(n*n*(n-1));local={v:comb(e,v)*comb(n-e,q-v)/comb(n,q) for v in range(lo,hi+1)};new=defaultdict(float)
  for total,p0 in dist.items():
   for v,p1 in local.items():new[total+v]+=p0*p1
  dist=dict(new)
 mean=sum(v*p for v,p in dist.items());upper=sum(p for v,p in dist.items() if v>=A);two=sum(p for v,p in dist.items() if abs(v-mean)>=abs(A-mean)-1e-12);pv=[ps[p] for p in pages];norm=math.sqrt(sum(v*v for v in pv));stat=sum(pv)/norm if norm else 0
 return {"edition":ed,"variant":name,"movable_strata":len(mobile),"mobile_occurrences":sum(x[2] for x in mobile),"mobile_hosts":len({x[0][1] for x in mobile}),"mobile_pages":len({x[0][0] for x in mobile}),"observed_q_early":A,"expected_q_early":f"{mean:.12f}","conditional_u":f"{score:.12f}","conditional_z":f"{score/math.sqrt(var):.12f}","mh_odds_ratio":f"{num/den:.12f}" if den else "INF","exact_directional_upper_p":f"{upper:.12f}","exact_two_sided_p":f"{two:.12f}","positive_pages":sum(v>0 for v in pv),"negative_pages":sum(v<0 for v in pv),"tied_pages":sum(v==0 for v in pv),"directional_page_stat":f"{stat:.12f}","semantic_value":"UNASSIGNED"},rows,[{"edition":ed,"variant":name,"page":p,"conditional_score":f"{ps[p]:.12f}","direction":"Q_EARLIER" if ps[p]>0 else "Q_LATER" if ps[p]<0 else "TIE"} for p in pages],pv
def main():
 pred=json.loads((R/PRED).read_text());stored=pred.pop("content_hash");assert stored==chash(pred) and pred["freeze_status"]=="FROZEN_BEFORE_GDT271_CONDITIONAL_ASSOCIATION_SCORING";rows=read(SRC);assert rows and all(not x["page"].startswith("f84") for x in rows)
 tests=[];strata=[];page_rows=[];null_rows=[];all_occ=[]
 for ed in EDS:
  pages,selected,occ=occurrences(rows,ed);all_occ.extend(occ);vectors=[];edtests=[]
  for name,keys in VARIANTS:
   result,srows,prows,pv=evaluate(ed,name,keys,occ,pages);edtests.append(result);strata.extend(srows);page_rows.extend(prows);vectors.append(pv)
  worlds=[]
  for world,signs in enumerate(itertools.product((-1,1),repeat=13)):
   vals=[]
   for pv in vectors:
    norm=math.sqrt(sum(v*v for v in pv));vals.append(sum(s*v for s,v in zip(signs,pv))/norm if norm else 0)
   worlds.append(vals)
   if ed=="ZL3b":null_rows.append({"world":world,"signs":"".join("+" if s==1 else "-" for s in signs),**{name:f"{value:.12f}" for (name,_),value in zip(VARIANTS,vals)},"max_three":f"{max(vals):.12f}"})
  maxima=[max(v) for v in worlds]
  for index,result in enumerate(edtests):
   obs=float(result["directional_page_stat"]);result["page_sign_directional_p"]=f"{(1+sum(v[index]>=obs-1e-12 for v in worlds))/8193:.12f}";result["page_sign_max_three_p"]=f"{(1+sum(v>=obs-1e-12 for v in maxima))/8193:.12f}";tests.append(result)
 write("gdt271_mobile_strata.tsv",strata);write("gdt271_tests.tsv",tests);write("gdt271_page_scores.tsv",page_rows);write("gdt271_zl_page_sign_null.tsv",null_rows)
 primary=next(x for x in tests if x["edition"]=="ZL3b" and x["variant"]==pred["primary_variant"]);gate=float(primary["conditional_u"])>0 and int(primary["positive_pages"])>=pred["primary_gate"]["positive_pages_min"] and float(primary["page_sign_max_three_p"])<=pred["primary_gate"]["page_sign_max_three_p_max"]
 status="Q13_Q_OUTER_STAGE_TRANSFERS_TO_Q20_COMPILER_MATCHED" if gate else "Q13_Q_OUTER_STAGE_Q20_COMPILER_MATCHED_TRANSFER_NONCONFIRMING"
 counter=[{"counterexample":"PRIMARY_GATE","value":f"U {primary['conditional_u']} positive pages {primary['positive_pages']} max3 p {primary['page_sign_max_three_p']}","consequence":"status follows the published ZL page-cluster gate"},{"counterexample":"PANEL_PREEXPOSURE","value":"GDT268 exposed marginal Q20 q/bare directions","consequence":"metric was frozen prospectively but source panel is not observer-blind"},{"counterexample":"READINGS_NOT_REPLICATIONS","value":"ZL3b IT2a RF1b","consequence":"alternate readings are sensitivity analyses only"},{"counterexample":"PARSER_DEPENDENCE","value":"exact PAGE_HOST and compiler tuple","consequence":"transfer is conditional on HPR2 parsing and is not linguistic segmentation proof"},{"counterexample":"NO_SEMANTIC_ENDPOINT","value":"record ordinal only","consequence":"even a pass gives no q meaning or translation"}];write("gdt271_counterexamples.tsv",counter)
 report=["# GDT271 — frozen Q20 transfer of q outer-layer stage","",f"Status: **{status}**.","","## Frozen transfer result","",f"The ZL primary exact page/PAGE_HOST/non-wrapper-compiler match retains {primary['mobile_occurrences']} mobile occurrences in {primary['movable_strata']} strata across {primary['mobile_hosts']} hosts and all thirteen pages. Conditional U is {float(primary['conditional_u']):+.3f}, MH OR {float(primary['mh_odds_ratio']):.3f}, with {primary['positive_pages']}/13 positive page scores, exact directional p={float(primary['exact_directional_upper_p']):.4f}, and max-three page p={float(primary['page_sign_max_three_p']):.4f}.","","| reading | conditioning | occurrences | hosts | U | OR | +/−/tie pages | exact directional p | max-3 page p |","|---|---|---:|---:|---:|---:|---:|---:|---:|"]
 for x in tests:report.append(f"| {x['edition']} | {x['variant']} | {x['mobile_occurrences']} | {x['mobile_hosts']} | {float(x['conditional_u']):+.3f} | {float(x['mh_odds_ratio']):.3f} | {x['positive_pages']}/{x['negative_pages']}/{x['tied_pages']} | {float(x['exact_directional_upper_p']):.4f} | {float(x['page_sign_max_three_p']):.4f} |")
 report += ["","## Interpretation","",("The frozen q13 direction passes the Q20 primary gate. This supports a cross-register outer-renderer stage tendency under exact HPR2 host/compiler matching." if gate else "The frozen q13 direction does not pass the Q20 primary gate. GDT270 remains a q13-local constructional result."),"The outcome concerns formal record placement only; alternate readings do not multiply the evidence.","","No word, spoken prefix, morpheme, semantic operator, language, plaintext, meaning, or translation is assigned. No f84r material was opened, retained, queried, joined, or scored.",""];(R/"GDT271_Q20_Q_OUTER_LAYER_TRANSFER_REPORT.md").write_text("\n".join(report),encoding="utf-8")
 outputs=["gdt271_mobile_strata.tsv","gdt271_tests.tsv","gdt271_page_scores.tsv","gdt271_zl_page_sign_null.tsv","gdt271_counterexamples.tsv","GDT271_Q20_Q_OUTER_LAYER_TRANSFER_REPORT.md"]
 result={"experiment":"GDT271_Q20_Q_OUTER_LAYER_TRANSFER","status":status,"freeze_prediction_sha256":sha(PRED),"gate_pass":gate,"primary":{k:(int(primary[k]) if k in {"movable_strata","mobile_occurrences","mobile_hosts","mobile_pages","positive_pages","negative_pages","tied_pages"} else float(primary[k])) for k in ("movable_strata","mobile_occurrences","mobile_hosts","mobile_pages","conditional_u","mh_odds_ratio","positive_pages","negative_pages","tied_pages","exact_directional_upper_p","page_sign_max_three_p")},"alternate_readings":{ed:{"conditional_u":float(next(x for x in tests if x["edition"]==ed and x["variant"]==pred["primary_variant"])["conditional_u"]),"positive_pages":int(next(x for x in tests if x["edition"]==ed and x["variant"]==pred["primary_variant"])["positive_pages"]),"page_sign_max_three_p":float(next(x for x in tests if x["edition"]==ed and x["variant"]==pred["primary_variant"])["page_sign_max_three_p"])} for ed in ("IT2a","RF1b")},"interpretation":"Frozen q13 q-EARLY outer-renderer direction scored on Q20 under exact page PAGE_HOST and non-wrapper compiler matching.","claim_ceiling":"Cross-register opaque outer-renderer stage transfer only; no semantic prefix word meaning plaintext or translation.","semantic_assignments":0,"f84r":{"new_access":False,"used":False,"scored":False},"inputs":{SRC:sha(SRC),PRED:sha(PRED)},"documents":{METHOD:sha(METHOD)},"implementation":{Path(__file__).name:sha(Path(__file__).name)},"outputs":{x:sha(x) for x in outputs}};result["content_hash"]=chash(result);(R/"gdt271_result.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":status,"gate":gate,"primary":result["primary"],"alternate":result["alternate_readings"]},sort_keys=True))
if __name__=="__main__":main()
