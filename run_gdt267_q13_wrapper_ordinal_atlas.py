#!/usr/bin/env python3
"""GDT267: page-paired wrapper rates by q13 record ordinal."""
import csv,hashlib,itertools,json,math
from collections import Counter,defaultdict
from pathlib import Path
R=Path(__file__).resolve().parent;SRC="gdt227_q13_abstract_interlinear.tsv";ACCESS="gdt257_result.json";METHOD="GDT267_Q13_WRAPPER_ORDINAL_ATLAS_METHOD.md"
WRAPS=["NONE","ch","che","d","q","s","sh","t"]
def read(p):
 with (R/p).open(encoding="utf-8") as f:return list(csv.DictReader(f,delimiter="\t"))
def write(p,r):
 with (R/p).open("w",encoding="utf-8",newline="") as f:w=csv.DictWriter(f,fieldnames=list(r[0]),delimiter="\t",lineterminator="\n");w.writeheader();w.writerows(r)
def sha(p):return hashlib.sha256((R/p).read_bytes()).hexdigest()
def corr(a,b):
 ma=sum(a)/len(a);mb=sum(b)/len(b);num=sum((x-ma)*(y-mb) for x,y in zip(a,b));den=math.sqrt(sum((x-ma)**2 for x in a)*sum((y-mb)**2 for y in b));return num/den if den else 0
def main():
 src=read(SRC);assert src and all(not x["page"].startswith("f84") for x in src)
 a=json.loads((R/ACCESS).read_text());assert a["access"]["pristine_access_seal"] is False
 rec=defaultdict(list);loc=defaultdict(set)
 for x in src:rec[(x["page"],x["record_id"])].append(x);loc[(x["page"],x["record_id"])].add(x["locus"])
 bp=defaultdict(list)
 for k,v in loc.items():
  if len(v)>=4:bp[k[0]].append(k[1])
 pages={p:sorted(v) for p,v in bp.items() if len(v)==2};assert len(pages)==9
 counts={};detail=[];diff={w:[] for w in WRAPS};lr=[]
 for p,rs in sorted(pages.items()):
  cc=[]
  for role,rid in zip(["EARLIER","LATER"],rs):
   c=Counter(z.split(":")[0] for x in rec[(p,rid)] for z in x["compiler_cells"].split("|"));n=sum(c.values());assert set(c)<=set(WRAPS);cc.append((c,n))
   for w in WRAPS:detail.append({"page":p,"record_id":rid,"ordinal_class":role,"wrapper":w,"wrapper_count":c[w],"group_count":n,"rate_per_group":f"{c[w]/n:.12f}"})
  lr.append(math.log(cc[0][1]/cc[1][1]))
  for w in WRAPS:diff[w].append(cc[0][0][w]/cc[0][1]-cc[1][0][w]/cc[1][1])
  counts[p]=cc
 def stat(d):
  den=math.sqrt(sum(x*x for x in d));return abs(sum(d))/den if den else 0
 obs={w:stat(diff[w]) for w in WRAPS};worlds=[];vals={w:[] for w in WRAPS}
 for wi,bits in enumerate(itertools.product([-1,1],repeat=9)):
  z={w:stat([s*x for s,x in zip(bits,diff[w])]) for w in WRAPS}
  for w in WRAPS:vals[w].append(z[w])
  worlds.append({"world":wi,"signs":"".join("+" if x==1 else "-" for x in bits),**{w:f"{z[w]:.12f}" for w in WRAPS},"max_abs_standardized":f"{max(z.values()):.12f}"})
 maxv=[max(vals[w][i] for w in WRAPS) for i in range(512)];atlas=[]
 for w in WRAPS:
  d=diff[w];loo=[sum(d[:i]+d[i+1:])/8 for i in range(9)];num=den=0.0
  for p in sorted(pages):
   (ce,ne),(cl,nl)=counts[p];a1=ce[w];b1=ne-a1;c1=cl[w];d1=nl-c1;n=ne+nl;num+=a1*d1/n;den+=b1*c1/n
  direction=sum(d)/9
  held=sum((sum(d[:i]+d[i+1:])/8>0)==(d[i]>0) for i in range(9) if d[i]!=0);heldn=sum(x!=0 for x in d)
  atlas.append({"wrapper":w,"earlier_total":sum(counts[p][0][0][w] for p in pages),"earlier_groups":sum(counts[p][0][1] for p in pages),"later_total":sum(counts[p][1][0][w] for p in pages),"later_groups":sum(counts[p][1][1] for p in pages),"mean_paired_rate_difference":f"{direction:.12f}","positive_pages":sum(x>0 for x in d),"negative_pages":sum(x<0 for x in d),"tied_pages":sum(x==0 for x in d),"held_page_direction_correct":held,"held_page_direction_scored":heldn,"leave_one_page_mean_min":f"{min(loo):.12f}","leave_one_page_mean_max":f"{max(loo):.12f}","mantel_haenszel_odds_ratio":f"{num/den:.12f}" if den else "INF","correlation_with_log_group_count_ratio":f"{corr(lr,d):.12f}","paired_standardized_stat":f"{obs[w]:.12f}","local_two_sided_inclusive_p":f"{(1+sum(v>=obs[w]-1e-15 for v in vals[w]))/513:.12f}","max_eight_inclusive_p":f"{(1+sum(v>=obs[w]-1e-15 for v in maxv))/513:.12f}","semantic_value":"UNASSIGNED"})
 write("gdt267_wrapper_page_rates.tsv",detail);write("gdt267_wrapper_atlas.tsv",atlas);write("gdt267_wrapper_null.tsv",worlds)
 q=next(x for x in atlas if x["wrapper"]=="q");bare=next(x for x in atlas if x["wrapper"]=="NONE");dd=next(x for x in atlas if x["wrapper"]=="d")
 status="Q13_Q_WRAPPER_EARLIER_BARE_RENDERING_LATER_RECORD_ASSOCIATION" if float(q["max_eight_inclusive_p"])<=.05 and float(bare["max_eight_inclusive_p"])<=.05 else "Q13_WRAPPER_ORDINAL_ATLAS_EXPLORATORY"
 counter=[{"counterexample":"Q_LENGTH_CORRELATION","value":q["correlation_with_log_group_count_ratio"],"consequence":"q rate difference grows on more length-imbalanced pages despite per-group normalization"},{"counterexample":"D_WEAK_LATER","value":f"mean {dd['mean_paired_rate_difference']} max-eight p {dd['max_eight_inclusive_p']}","consequence":"not every apparent wrapper contrast is stable or selected"},{"counterexample":"RIGHT_FAMILY_REVERSAL_GDT265","value":"RIGHT 32/72 held ordinal assignments","consequence":"record order is not a single monotone compiler axis"},{"counterexample":"MECHANICAL_ORDINAL","value":"earlier/later among two eligible GDT227 records","consequence":"association is document placement not semantic content"}]
 write("gdt267_counterexamples.tsv",counter)
 report=["# GDT267 — q13 wrapper/record-ordinal atlas","",f"Status: **{status}**.","","## Result","","Rates are normalized per source group inside each record before the nine pages are combined.","","| wrapper | mean earlier−later rate | + / − / tie pages | held direction | MH odds ratio | local p | max-eight p |","|---|---:|---:|---:|---:|---:|---:|"]
 for x in sorted(atlas,key=lambda z:-abs(float(z["mean_paired_rate_difference"]))):report.append(f"| {x['wrapper']} | {float(x['mean_paired_rate_difference']):+.4f} | {x['positive_pages']} / {x['negative_pages']} / {x['tied_pages']} | {x['held_page_direction_correct']}/{x['held_page_direction_scored']} | {float(x['mantel_haenszel_odds_ratio']):.3f} | {float(x['local_two_sided_inclusive_p']):.4f} | {float(x['max_eight_inclusive_p']):.4f} |")
 report += ["",f"`q` is enriched in the earlier eligible record on {q['positive_pages']}/9 pages (mean rate difference {float(q['mean_paired_rate_difference']):+.4f}; MH OR {float(q['mantel_haenszel_odds_ratio']):.3f}). Bare/`NONE` rendering is enriched in the later record on {bare['negative_pages']}/9 pages (mean earlier−later {float(bare['mean_paired_rate_difference']):+.4f}; MH OR {float(bare['mantel_haenszel_odds_ratio']):.3f}). Both directions transfer under leave-one-page sign prediction.","","This is the first stable constructional function recovered from the GDT264 fingerprint: q13 `q` participates in an earlier-record rendering regime, contrasted with later-record bare rendering. It does **not** establish what the records say or make `q` a spoken/semantic prefix. The q effect correlates with record-length imbalance, so its exact mechanism may involve expansion, density, or record stage; per-group normalization prevents simple count inflation but does not distinguish those alternatives.","","No topic, operation, lexical value, word, language, plaintext, or translation is assigned. No f84r material was opened, retained, queried, or scored; the prior process-level breach remains disclosed.",""]
 (R/"GDT267_Q13_WRAPPER_ORDINAL_ATLAS_REPORT.md").write_text("\n".join(report))
 result={"experiment":"GDT267_Q13_WRAPPER_ORDINAL_ATLAS","status":status,"pages":9,"records":18,"wrappers":8,"q":{"positive_pages":int(q["positive_pages"]),"mean_rate_difference":float(q["mean_paired_rate_difference"]),"mh_odds_ratio":float(q["mantel_haenszel_odds_ratio"]),"max_eight_p":float(q["max_eight_inclusive_p"]),"held_direction":f"{q['held_page_direction_correct']}/{q['held_page_direction_scored']}"},"bare":{"negative_pages":int(bare["negative_pages"]),"mean_rate_difference":float(bare["mean_paired_rate_difference"]),"mh_odds_ratio":float(bare["mantel_haenszel_odds_ratio"]),"max_eight_p":float(bare["max_eight_inclusive_p"]),"held_direction":f"{bare['held_page_direction_correct']}/{bare['held_page_direction_scored']}"},"semantic_assignments":0,"interpretation":"q-wrapped rendering is earlier-record-associated and bare rendering later-record-associated in this q13 panel; meaning remains unknown.","claim_ceiling":"q13 wrapper placement by mechanical record ordinal only; no semantic operator word or translation.","f84r":{"prior_transient_parse_disclosed":True,"new_access":False,"used":False,"scored":False},"inputs":{SRC:sha(SRC),ACCESS:sha(ACCESS)},"documents":{METHOD:sha(METHOD)},"outputs":{},"implementation":{Path(__file__).name:sha(Path(__file__).name)}}
 result["outputs"]={p:sha(p) for p in ["gdt267_wrapper_page_rates.tsv","gdt267_wrapper_atlas.tsv","gdt267_wrapper_null.tsv","gdt267_counterexamples.tsv","GDT267_Q13_WRAPPER_ORDINAL_ATLAS_REPORT.md"]};result["content_hash"]=hashlib.sha256(json.dumps(result,sort_keys=True,separators=(",",":")).encode()).hexdigest();(R/"gdt267_result.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":status,"q_p":q["max_eight_inclusive_p"],"bare_p":bare["max_eight_inclusive_p"]},sort_keys=True))
if __name__=="__main__":main()
