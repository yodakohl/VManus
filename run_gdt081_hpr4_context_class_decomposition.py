#!/usr/bin/env python3
"""GDT081: decompose the frozen HPR4 class by held-register context ecology."""
from __future__ import annotations
import csv, hashlib, itertools, json, math, random
from collections import Counter, defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT/"gdt062_right_family_inventory.tsv";HPR4=ROOT/"gdt078_hpr4_model.json";METHOD=ROOT/"GDT081_HPR4_CONTEXT_CLASS_DECOMPOSITION_METHOD.md";REPORT=ROOT/"GDT081_HPR4_CONTEXT_CLASS_DECOMPOSITION_REPORT.md";SCORES=ROOT/"gdt081_context_class_scores.tsv";PAIRS=ROOT/"gdt081_pair_similarity.tsv";CELLS=ROOT/"gdt081_shared_context_cells.tsv";RESULT=ROOT/"gdt081_result.json"
VARIANTS={"FULL_NO_RIGHT":("wrapper","inner_d","local_frame","dy_closure","b3","position_quartile"),"WRAPPER_FRAME_POSITION":("wrapper","local_frame","position_quartile"),"WRAPPER_ONLY":("wrapper",),"POSITION_ONLY":("position_quartile",),"WITH_RIGHT_CIRCULAR":("wrapper","inner_d","local_frame","right_family","dy_closure","b3","position_quartile")}
def read(p):
 with Path(p).open(encoding="utf-8",newline="")as h:return list(csv.DictReader(h,delimiter="\t"))
def write(p,rows,fields):
 with Path(p).open("w",encoding="utf-8",newline="")as h:w=csv.DictWriter(h,fieldnames=fields,delimiter="\t",lineterminator="\n");w.writeheader();w.writerows(rows)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def cosine(a,b):
 den=math.sqrt(sum(x*x for x in a.values())*sum(x*x for x in b.values()));return sum(a[k]*b[k]for k in set(a)&set(b))/den if den else 0.0
def main():
 rows=read(SOURCE);assert len(rows)==15592 and not any(r["locus"].startswith("f84r")for r in rows);hpr4=json.loads(HPR4.read_text())["stable_aiin_high_hosts"];assert hpr4==["d","ok","yk","yt"]
 regs=sorted({r["register"]for r in rows});by=defaultdict(list)
 for r in rows:by[r["page_host"]].append(r)
 eligible=[h for h,z in by.items()if len(z)>=20 and len({r["physical_folio"]for r in z})>=3 and all(sum(r["register"]==g for r in z)>=3 for g in regs)]
 freq=sorted((len(by[h]),h)for h in eligible);quart={h:min(3,4*i//len(freq))for i,(_,h)in enumerate(freq)};pools={i:[h for h in eligible if quart[h]==i]for i in range(4)};target=Counter(quart[h]for h in hpr4)
 score_rows=[];pair_rows=[];all_vectors={}
 for variant,fields in VARIANTS.items():
  vectors={}
  for reg in regs:
   for host in eligible:vectors[reg,host]=Counter(tuple(r[f]for f in fields)for r in by[host]if r["register"]==reg)
  all_vectors[variant]=vectors
  ps={}
  all_pair={}
  for a,b in itertools.combinations(eligible,2):
   all_pair[tuple(sorted((a,b)))]=sum(cosine(vectors[g,a],vectors[g,b])for g in regs)/len(regs)
  for a,b in itertools.combinations(hpr4,2):
   vals=[cosine(vectors[g,a],vectors[g,b])for g in regs];ps[a,b]=sum(vals)/len(vals);pair_rows.append({"variant":variant,"host_a":a,"host_b":b,**{g:vals[i]for i,g in enumerate(regs)},"mean_similarity":ps[a,b]})
  def trio_score(ss):return sum(all_pair[tuple(sorted((a,b)))]for a,b in itertools.combinations(ss,2))/3
  trios=[]
  for dropped in hpr4:
   ss=[h for h in hpr4 if h!=dropped];trios.append((trio_score(ss),dropped,ss))
  observed,dropped,best=max(trios)
  rng=random.Random(81081+list(VARIANTS).index(variant));null=[]
  for _ in range(50000):
   ss=[]
   for q,n in sorted(target.items()):ss+=rng.sample(pools[q],n)
   null.append(max(trio_score([h for h in ss if h!=d])for d in ss))
  p=(1+sum(x>=observed for x in null))/(len(null)+1)
  for value,drop,ss in sorted(trios,reverse=True):score_rows.append({"variant":variant,"dropped_host":drop,"retained_hosts":";".join(sorted(ss)),"trio_similarity":value,"selected_within_variant":int(value==observed),"frequency_matched_maxT_p":p if value==observed else "","null_mean_max_trio":sum(null)/len(null)if value==observed else"","null_draws":len(null)if value==observed else"","circular_right_family_variant":int("RIGHT"in variant)})
 primary=[r for r in score_rows if r["variant"]=="FULL_NO_RIGHT"and int(r["selected_within_variant"])][0];assert primary["dropped_host"]=="d"and primary["retained_hosts"]=="ok;yk;yt"
 fields=VARIANTS["FULL_NO_RIGHT"];cellmap=defaultdict(set);counts=Counter()
 for r in rows:
  if r["page_host"]in{"ok","yk","yt"}:
   k=(r["register"],)+tuple(r[f]for f in fields);cellmap[k].add(r["page_host"]);counts[k,r["page_host"]]+=1
 cell_rows=[]
 for k,hosts in sorted(cellmap.items(),key=lambda x:(-len(x[1]),x[0])):
  if len(hosts)>=2:cell_rows.append({"register":k[0],"wrapper":k[1],"inner_d":k[2],"local_frame":k[3],"dy_closure":k[4],"b3":k[5],"position_quartile":k[6],"hosts":";".join(sorted(hosts)),"host_count":len(hosts),"ok_occurrences":counts[k,"ok"],"yk_occurrences":counts[k,"yk"],"yt_occurrences":counts[k,"yt"]})
 status="HPR4_DECOMPOSES_INTO_OK_YK_YT_UNFRAMED_CONTEXT_CLASS_D_IS_OUTLIER"
 write(SCORES,[{k:f"{v:.12g}"if isinstance(v,float)else v for k,v in r.items()}for r in score_rows],list(score_rows[0]));write(PAIRS,[{k:f"{v:.12g}"if isinstance(v,float)else v for k,v in r.items()}for r in pair_rows],list(pair_rows[0]));write(CELLS,cell_rows,list(cell_rows[0]))
 REPORT.write_text(f"""# GDT081 — HPR4 context-class decomposition

## Outcome

**{status}**

After removing RIGHT_FAMILY from the context vector, the best of HPR4's four
leave-one-out trios is `ok/yk/yt`: mean pair similarity
{float(primary['trio_similarity']):.4f} across all five registers.  The
50,000-draw occurrence-frequency-quartile matched max-over-trios null gives
p={float(primary['frequency_matched_maxT_p']):.5f}.  Dropping `ok`, `yk`, or
`yt` instead gives {next(r['trio_similarity']for r in score_rows if r['variant']=='FULL_NO_RIGHT'and r['dropped_host']=='ok'):.4f},
{next(r['trio_similarity']for r in score_rows if r['variant']=='FULL_NO_RIGHT'and r['dropped_host']=='yk'):.4f}, and
{next(r['trio_similarity']for r in score_rows if r['variant']=='FULL_NO_RIGHT'and r['dropped_host']=='yt'):.4f}.
There are {sum(r['host_count']==3 for r in cell_rows)} exact register/compiler
cells containing all three hosts and {sum(r['host_count']==2 for r in cell_rows)}
containing two.

The interpretation is narrower than content: `ok/yk/yt` are an unframed
formal substitution class, while `d` is an O-framed, wrapper-rich outlier that
entered HPR4 through similar RIGHT_FAMILY propensity.  The result is
postselected, parser-dependent, and partly driven by shared absence of optional
layers; its null cannot reproduce the nearly unique HPR4 high-aiin selection
path.  It freezes a better HPR5 formal hypothesis but assigns no role or
meaning.  f84r was excluded and not opened or used.
""",encoding="utf-8")
 result={"schema":"GDT081_HPR4_CONTEXT_CLASS_DECOMPOSITION_RESULT_V1","status":status,"groups":len(rows),"eligible_hosts":len(eligible),"hpr4_hosts":hpr4,"primary_best_trio":["ok","yk","yt"],"primary_dropped_host":"d","primary_similarity":float(primary["trio_similarity"]),"primary_frequency_matched_maxT_p":float(primary["frequency_matched_maxT_p"]),"shared_all_three_cells":sum(r["host_count"]==3 for r in cell_rows),"shared_two_host_cells":sum(r["host_count"]==2 for r in cell_rows),"hpr5_formal_hypothesis":"ok/yk/yt are an unframed PAGE_HOST substitution class; d is a distinct O-framed wrapper-rich class.","limitations":["postselected among HPR4 leave-one-out trios","frequency null does not reproduce high-aiin selection path","shared absences inflate context similarity","source-only formal class; no external content"],"claim_ceiling":"No content, semantic class, role, gloss, word, morpheme, POS, sound, language, plaintext, meaning, or translation.","f84r":{"opened":False,"retained":False,"queried":False,"joined":False,"scored":False,"targeted":False},"inputs":{SOURCE.name:sha(SOURCE),HPR4.name:sha(HPR4),"gdt078_result.json":sha(ROOT/"gdt078_result.json"),"gdt080_result.json":sha(ROOT/"gdt080_result.json")},"implementation":{Path(__file__).name:sha(Path(__file__))},"outputs":{SCORES.name:sha(SCORES),PAIRS.name:sha(PAIRS),CELLS.name:sha(CELLS)},"documents":{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)}};result["result_content_sha256"]=csha(result);RESULT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":status,"trio":result["primary_best_trio"],"score":result["primary_similarity"],"p":result["primary_frequency_matched_maxT_p"]},sort_keys=True))
if __name__=="__main__":main()
