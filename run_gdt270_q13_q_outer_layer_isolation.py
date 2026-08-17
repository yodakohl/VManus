#!/usr/bin/env python3
"""GDT270: isolate q from all other same-group compiler coordinates."""
import csv, hashlib, itertools, json, math
from collections import Counter, defaultdict
from math import comb
from pathlib import Path

R = Path(__file__).resolve().parent
SRC = "gdt227_q13_abstract_interlinear.tsv"
METHOD = "GDT270_Q13_Q_OUTER_LAYER_ISOLATION_METHOD.md"
CONTEXT = ["gdt036_result.json", "gdt062_result.json", "gdt086_result.json", "gdt267_result.json", "gdt268_result.json", "gdt269_result.json"]
VARIANTS = [
 ("PAGE_HOST_PAGE", ("page","page_host")),
 ("PAGE_HOST_PAGE_RIGHT", ("page","page_host","right_family")),
 ("PAGE_HOST_PAGE_DY", ("page","page_host","dy")),
 ("PAGE_HOST_PAGE_B3", ("page","page_host","b3")),
 ("PAGE_HOST_PAGE_FRAME", ("page","page_host","frame")),
 ("PAGE_HOST_PAGE_INNER_D", ("page","page_host","inner_d")),
 ("PAGE_HOST_PAGE_RIGHT_CLOSURE", ("page","page_host","right_closure")),
 ("PAGE_HOST_PAGE_OTHER_COMPILER", ("page","page_host","other_compiler")),
 ("PAGE_HOST_PAGE_OTHER_COMPILER_WITHIN_FIELD_POSITION", ("page","page_host","other_compiler","within_field_position")),
 ("PAGE_HOST_PAGE_RIGHT_CLOSURE_WITHIN_FIELD_POSITION", ("page","page_host","right_closure","within_field_position")),
 ("PAGE_HOST_PAGE_OTHER_COMPILER_FIELD_END", ("page","page_host","other_compiler","field_end")),
 ("PAGE_HOST_PAGE_OTHER_COMPILER_LOCAL_STRUCTURE", ("page","page_host","other_compiler","local_structure")),
 ("PAGE_HOST_PAGE_OTHER_COMPILER_RELATIVE_QUARTILE", ("page","page_host","other_compiler","relative_quartile")),
 ("PAGE_HOST_PAGE_OTHER_COMPILER_ROLE", ("page","page_host","other_compiler","field_role")),
]

def read(name):
 with (R/name).open(encoding="utf-8",newline="") as h:return list(csv.DictReader(h,delimiter="\t"))
def write(name,rows):
 with (R/name).open("w",encoding="utf-8",newline="") as h:
  w=csv.DictWriter(h,fieldnames=list(rows[0]),delimiter="\t",lineterminator="\n");w.writeheader();w.writerows(rows)
def sha(name):return hashlib.sha256((R/name).read_bytes()).hexdigest()
def chash(value):return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(",",":")).encode()).hexdigest()

def inventory():
 src=read(SRC);assert src and all(not x["page"].startswith("f84") for x in src)
 rec=defaultdict(list);loci=defaultdict(set)
 for x in src:rec[x["page"],x["record_id"]].append(x);loci[x["page"],x["record_id"]].add(x["locus"])
 bp=defaultdict(list)
 for (page,rid),values in loci.items():
  if len(values)>=4:bp[page].append(rid)
 panel={p:sorted(ids) for p,ids in bp.items() if len(ids)==2};assert len(panel)==9
 out=[]
 for page,ids in sorted(panel.items()):
  for ordinal,rid in enumerate(ids):
   for field in rec[page,rid]:
    hosts=field["page_hosts"].split("|");cells=field["compiler_cells"].split("|");tokens=field["source_tokens"].split("|");assert len(hosts)==len(cells)==len(tokens)
    for index,(host,cell,token) in enumerate(zip(hosts,cells,tokens)):
     wrapper,frame,inner,right,dy,b3=cell.split(":")
     if wrapper not in {"q","NONE"}:continue
     pos="SINGLE" if len(hosts)==1 else "FIRST" if index==0 else "LAST" if index==len(hosts)-1 else "MIDDLE"
     end=field["line_field_end"]
     out.append({"page":page,"physical_folio":field["physical_folio"],"record_id":rid,"ordinal_class":"EARLIER" if ordinal==0 else "LATER","ordinal_binary":ordinal,"locus":field["locus"],"field_ordinal":field["field_ordinal"],"field_role":field["abstract_role_like"],"relative_quartile":min(3,int(float(field["relative_position"])*4)),"within_field_position":pos,"field_end":end,"local_structure":pos+":"+end,"page_host":host,"wrapper":wrapper,"frame":frame,"inner_d":inner,"right_family":right,"dy":dy,"b3":b3,"right_closure":":".join((right,dy,b3)),"other_compiler":":".join((frame,inner,right,dy,b3)),"source_token":token,"claim_state":"OPAQUE_COMPILER_CELL_NO_GLOSS"})
 assert len(out)==632
 return panel,out

def evaluate(name,keys,occ,pages):
 grouped=defaultdict(Counter)
 for x in occ:grouped[tuple(str(x[k]) for k in keys)][x["wrapper"],int(x["ordinal_binary"])]+=1
 mobile=[];strata=[]
 for key,c in sorted(grouped.items()):
  a,b,cc,d=c["q",0],c["q",1],c["NONE",0],c["NONE",1];n=a+b+cc+d;q=a+b;e=a+cc;lo=max(0,q-(n-e));hi=min(q,e);mov=int(hi>lo)
  strata.append({"variant":name,"stratum_key":json.dumps(dict(zip(keys,key)),sort_keys=True,separators=(",",":")),"q_early":a,"q_late":b,"none_early":cc,"none_late":d,"occurrences":n,"expected_q_early":f"{q*e/n:.12f}","score":f"{a-q*e/n:.12f}","movable":mov})
  if mov:mobile.append((key,c,n,q,e,lo,hi))
 num=den=score=var=0.0;observed=0;dist={0:1.0};ps=defaultdict(float)
 for key,c,n,q,e,lo,hi in mobile:
  a,b,cc,d=c["q",0],c["q",1],c["NONE",0],c["NONE",1];num+=a*d/n;den+=b*cc/n;delta=a-q*e/n;score+=delta;ps[key[0]]+=delta;observed+=a;var+=q*(n-q)*e*(n-e)/(n*n*(n-1))
  local={v:comb(e,v)*comb(n-e,q-v)/comb(n,q) for v in range(lo,hi+1)};new=defaultdict(float)
  for total,p0 in dist.items():
   for v,p1 in local.items():new[total+v]+=p0*p1
  dist=dict(new)
 mean=sum(v*p for v,p in dist.items());upper=sum(p for v,p in dist.items() if v>=observed);two=sum(p for v,p in dist.items() if abs(v-mean)>=abs(observed-mean)-1e-12)
 pv=[ps[p] for p in pages];norm=math.sqrt(sum(v*v for v in pv));stat=abs(sum(pv))/norm if norm else 0.0
 return {"variant":name,"stratification":"+".join(keys),"all_strata":len(grouped),"movable_strata":len(mobile),"mobile_occurrences":sum(x[2] for x in mobile),"mobile_hosts":len({x[0][1] for x in mobile}),"mobile_pages":len({x[0][0] for x in mobile}),"observed_q_early":observed,"expected_q_early":f"{mean:.12f}","conditional_u":f"{score:.12f}","conditional_z":f"{score/math.sqrt(var):.12f}","mh_odds_ratio":f"{num/den:.12f}" if den else "INF","exact_upper_p":f"{upper:.12f}","exact_two_sided_p":f"{two:.12f}","positive_pages":sum(v>0 for v in pv),"negative_pages":sum(v<0 for v in pv),"tied_pages":sum(v==0 for v in pv),"page_stat":f"{stat:.12f}","semantic_value":"UNASSIGNED"},strata,[{"variant":name,"page":p,"score":f"{ps[p]:.12f}","direction":"Q_EARLIER" if ps[p]>0 else "Q_LATER" if ps[p]<0 else "TIE"} for p in pages],pv

def main():
 panel,occ=inventory();pages=sorted(panel);tests=[];strata=[];page_rows=[];vectors=[]
 for name,keys in VARIANTS:
  summary,srows,prows,pv=evaluate(name,keys,occ,pages);tests.append(summary);strata.extend(srows);page_rows.extend(prows);vectors.append(pv)
 null=[];world_stats=[]
 for world,signs in enumerate(itertools.product((-1,1),repeat=9)):
  vals=[]
  for pv in vectors:
   norm=math.sqrt(sum(v*v for v in pv));vals.append(abs(sum(s*v for s,v in zip(signs,pv)))/norm if norm else 0.0)
  world_stats.append(vals);null.append({"world":world,"signs":"".join("+" if s==1 else "-" for s in signs),**{name:f"{v:.12f}" for (name,_),v in zip(VARIANTS,vals)},"max_fourteen":f"{max(vals):.12f}"})
 maxima=[max(v) for v in world_stats]
 for index,row in enumerate(tests):
  obs=float(row["page_stat"]);local=(1+sum(v[index]>=obs-1e-12 for v in world_stats))/513;maxp=(1+sum(v>=obs-1e-12 for v in maxima))/513;row["page_sign_local_p"]=f"{local:.12f}";row["page_sign_max_fourteen_p"]=f"{maxp:.12f}"
 write("gdt270_occurrences.tsv",occ);write("gdt270_tests.tsv",tests);write("gdt270_strata.tsv",strata);write("gdt270_page_scores.tsv",page_rows);write("gdt270_page_sign_null.tsv",null)
 primary=next(x for x in tests if x["variant"]=="PAGE_HOST_PAGE_OTHER_COMPILER");position=next(x for x in tests if x["variant"]=="PAGE_HOST_PAGE_OTHER_COMPILER_WITHIN_FIELD_POSITION");fine=next(x for x in tests if x["variant"]=="PAGE_HOST_PAGE_OTHER_COMPILER_LOCAL_STRUCTURE")
 counter=[{"counterexample":"FINE_LOCAL_STRUCTURE_CAPACITY","value":f"{fine['movable_strata']} strata {fine['mobile_occurrences']} occurrences p {fine['exact_two_sided_p']}","consequence":"joint position and endpoint matching is underpowered and nonconfirming"},{"counterexample":"POSTHOC_FOURTEEN_VARIANTS","value":"all reported with shared max-fourteen page null","consequence":"this local isolation is hypothesis generation rather than prospective confirmation"},{"counterexample":"Q20_GDT268_WEAK","value":"q max-two p .172464","consequence":"no universal record-stage function is established"},{"counterexample":"PARSER_DEPENDENCE","value":"PAGE_HOST and OTHER_COMPILER use HPR2 parsing","consequence":"separability is formal under the frozen parser, not independent linguistic segmentation"},{"counterexample":"GROUP_DEPENDENCE","value":"occurrences share fields records and pages","consequence":"page clustered max-family null is primary for search calibration"}];write("gdt270_counterexamples.tsv",counter)
 status="Q13_Q_SEPARABLE_OUTER_RECORD_STAGE_RENDERER_COMPILER_MATCHED_EXPLORATORY"
 report=["# GDT270 — q13 q outer-layer isolation","",f"Status: **{status}**.","","## Result","",f"After fixing exact page, PAGE_HOST, O/OT frame, inner-D, right family, DY, and B3, {primary['movable_strata']} strata with {primary['mobile_occurrences']} occurrences across {primary['mobile_hosts']} hosts and all nine pages remain movable. `q` is still earlier-record associated: MH OR {float(primary['mh_odds_ratio']):.3f}, exact two-sided diagnostic p={float(primary['exact_two_sided_p']):.4f}, and shared max-fourteen page p={float(primary['page_sign_max_fourteen_p']):.4f}.","",f"Adding within-field position still leaves {position['mobile_occurrences']} occurrences and OR {float(position['mh_odds_ratio']):.3f}; its exact diagnostic is p={float(position['exact_two_sided_p']):.4f} and max-fourteen page p={float(position['page_sign_max_fourteen_p']):.4f}. The finest joint position+endpoint match falls to {fine['mobile_occurrences']} occurrences and is nonconfirming (exact p={float(fine['exact_two_sided_p']):.4f}).","","## Complete conditioning atlas","","| conditioning | movable | occurrences | hosts | OR | exact p | local page p | max-14 page p |","|---|---:|---:|---:|---:|---:|---:|---:|"]
 for x in tests:report.append(f"| {x['variant']} | {x['movable_strata']} | {x['mobile_occurrences']} | {x['mobile_hosts']} | {float(x['mh_odds_ratio']):.3f} | {float(x['exact_two_sided_p']):.4f} | {float(x['page_sign_local_p']):.4f} | {float(x['page_sign_max_fourteen_p']):.4f} |")
 report += ["","## Interpretation","","Within this q13 panel, q is empirically separable from the opaque PAGE_HOST and the other same-group renderer coordinates. It behaves like an outer constructional choice associated with record stage, not merely a spelling selected by a different host/right/closure combination. Its exact mechanism can still be line-entry layout, expansion, or record-template organization, and the weak GDT268 transfer prevents a manuscript-wide claim.","","This is an exposed exploratory decomposition. It assigns no word, sound, morpheme, semantic operator, topic, language, plaintext, or translation. No f84r material was opened, retained, queried, joined, or scored.",""]
 (R/"GDT270_Q13_Q_OUTER_LAYER_ISOLATION_REPORT.md").write_text("\n".join(report),encoding="utf-8")
 outputs=["gdt270_occurrences.tsv","gdt270_tests.tsv","gdt270_strata.tsv","gdt270_page_scores.tsv","gdt270_page_sign_null.tsv","gdt270_counterexamples.tsv","GDT270_Q13_Q_OUTER_LAYER_ISOLATION_REPORT.md"]
 result={"experiment":"GDT270_Q13_Q_OUTER_LAYER_ISOLATION","status":status,"analysis_state":"EXPLORATORY_POSTHOC_FOURTEEN_VARIANT_COMPILER_ISOLATION","pages":9,"records":18,"q_or_bare_occurrences":632,"variants":14,"primary":{"movable_strata":int(primary["movable_strata"]),"mobile_occurrences":int(primary["mobile_occurrences"]),"mobile_hosts":int(primary["mobile_hosts"]),"mh_odds_ratio":float(primary["mh_odds_ratio"]),"exact_two_sided_p":float(primary["exact_two_sided_p"]),"page_sign_max_fourteen_p":float(primary["page_sign_max_fourteen_p"])},"position_sensitivity":{"mobile_occurrences":int(position["mobile_occurrences"]),"mh_odds_ratio":float(position["mh_odds_ratio"]),"exact_two_sided_p":float(position["exact_two_sided_p"]),"page_sign_max_fourteen_p":float(position["page_sign_max_fourteen_p"])},"fine_local_structure":{"mobile_occurrences":int(fine["mobile_occurrences"]),"exact_two_sided_p":float(fine["exact_two_sided_p"])},"interpretation":"q is separable from exact PAGE_HOST and all other same-group compiler coordinates in the q13 record-stage association, with fine-position capacity limits.","claim_ceiling":"Opaque q13 outer renderer separability under HPR2 only; no semantic operator word morpheme meaning plaintext or translation.","semantic_assignments":0,"f84r":{"new_access":False,"used":False,"scored":False,"prior_process_breach_disclosed":True},"inputs":{SRC:sha(SRC),**{x:sha(x) for x in CONTEXT}},"documents":{METHOD:sha(METHOD)},"implementation":{Path(__file__).name:sha(Path(__file__).name)},"outputs":{x:sha(x) for x in outputs}};result["content_hash"]=chash(result);(R/"gdt270_result.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8");print(json.dumps({"status":status,"primary":result["primary"],"position":result["position_sensitivity"],"fine":result["fine_local_structure"]},sort_keys=True))
if __name__=="__main__":main()
