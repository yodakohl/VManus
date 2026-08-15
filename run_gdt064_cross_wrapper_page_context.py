#!/usr/bin/env python3
"""GDT064: compare page context for same PAGE_HOST across wrappers."""
from __future__ import annotations
import csv,hashlib,json,math
from collections import Counter,defaultdict
from itertools import combinations
from pathlib import Path
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT/"gdt062_right_family_inventory.tsv";METHOD=ROOT/"GDT064_CROSS_WRAPPER_PAGE_CONTEXT_METHOD.md";REPORT=ROOT/"GDT064_CROSS_WRAPPER_PAGE_CONTEXT_REPORT.md";CELLS=ROOT/"gdt064_cross_wrapper_context_cells.tsv";PAIRS=ROOT/"gdt064_cross_wrapper_context_pairs.tsv";VARIANTS=ROOT/"gdt064_variant_log.tsv";RESULT=ROOT/"gdt064_result.json"
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def read(p):
 with Path(p).open(encoding="utf-8",newline="")as h:return list(csv.DictReader(h,delimiter="\t"))
def write(p,rows,fields):
 with Path(p).open("w",encoding="utf-8",newline="")as h:w=csv.DictWriter(h,fieldnames=fields,delimiter="\t",lineterminator="\n");w.writeheader();w.writerows(rows)
def wj(a,b):
 k=set(a)|set(b);d=sum(max(a[x],b[x])for x in k);return sum(min(a[x],b[x])for x in k)/d if d else 0.
def binom_two(k,n):
 if not n:return 1.
 lo=sum(math.comb(n,i)for i in range(k+1))/2**n;hi=sum(math.comb(n,i)for i in range(k,n+1))/2**n;return min(1.,2*min(lo,hi))
def main():
 rows=read(SOURCE);assert len(rows)==15592 and not any(r["locus"].startswith("f84r")for r in rows);pages=defaultdict(list)
 for r in rows:pages[r["page"]].append(r)
 units=[]
 for page,z in sorted(pages.items()):
  bag=Counter(r["page_host"]for r in z);by=defaultdict(list)
  for r in z:by[r["page_host"],r["wrapper"]].append(r)
  for (host,wrapper),q in sorted(by.items()):
   ctx=Counter(bag);del ctx[host];units.append({"unit_id":page+"|"+host+"|"+wrapper,"page":page,"physical_folio":q[0]["physical_folio"],"register":q[0]["register"],"host":host,"wrapper":wrapper,"occurrences":len(q),"host_len_bucket":len(host)//2,"page_size_bucket":len(z)//25,"context":ctx})
 pool=defaultdict(list)
 for u in units:pool[u["register"],u["host_len_bucket"],u["page_size_bucket"]].append(u)
 pairrows=[];cell=defaultdict(lambda:{"diff":[],"same":[],"control":[]});control_cache={}
 byhr=defaultdict(list)
 for u in units:byhr[u["host"],u["register"]].append(u)
 for (host,reg),z in sorted(byhr.items()):
  cand=defaultdict(list)
  for a,b in combinations(z,2):
   if a["physical_folio"]==b["physical_folio"]:continue
   typ="same"if a["wrapper"]==b["wrapper"]else"diff";key=hashlib.sha256((a["unit_id"]+"|"+b["unit_id"]).encode()).hexdigest();cand[typ].append((key,a,b))
  for typ in("diff","same"):
   for _,a,b in sorted(cand[typ])[:200]:
    sim=wj(a["context"],b["context"]);ck=(a["unit_id"],typ,b["page_size_bucket"])
    if ck not in control_cache:
     controls=[q for q in pool[a["register"],a["host_len_bucket"],b["page_size_bucket"]]if q["physical_folio"]!=a["physical_folio"]and q["host"]!=host and((q["wrapper"]==a["wrapper"])==(typ=="same"))];control_cache[ck]=(sum(wj(a["context"],q["context"])for q in controls)/len(controls)if controls else 0.,len(controls))
    cs,nc=control_cache[ck];pairrows.append({"host":host,"register":reg,"pair_type":typ.upper()+"_WRAPPER","left_unit":a["unit_id"],"right_unit":b["unit_id"],"context_similarity":sim,"matched_control_similarity":cs,"gain_vs_control":sim-cs,"control_units":nc});cell[host,reg][typ].append(sim);cell[host,reg]["control"].append(cs)
 cells=[]
 for (host,reg),v in sorted(cell.items()):
  if not v["diff"]:continue
  d=sum(v["diff"])/len(v["diff"]);s=sum(v["same"])/len(v["same"])if v["same"]else 0.;c=sum(v["control"])/len(v["control"]);cells.append({"host":host,"register":reg,"physical_folios":len({u["physical_folio"]for u in byhr[host,reg]}),"wrappers":len({u["wrapper"]for u in byhr[host,reg]}),"different_wrapper_pairs":len(v["diff"]),"same_wrapper_pairs":len(v["same"]),"different_wrapper_mean_similarity":d,"same_wrapper_mean_similarity":s,"matched_control_mean_similarity":c,"different_minus_control":d-c,"different_minus_same":d-s if v["same"]else 0.,"same_wrapper_available":int(bool(v["same"]))})
 cells.sort(key=lambda r:(-r["different_minus_control"],r["host"],r["register"]));write(PAIRS,[{k:f"{v:.12g}"if isinstance(v,float)else v for k,v in r.items()}for r in pairrows],list(pairrows[0]));write(CELLS,[{k:f"{v:.12g}"if isinstance(v,float)else v for k,v in r.items()}for r in cells],list(cells[0]));n=len(cells);pos=sum(r["different_minus_control"]>0 for r in cells);both=[r for r in cells if r["same_wrapper_available"]];mean_diff=sum(r["different_wrapper_mean_similarity"]for r in cells)/n;mean_ctrl=sum(r["matched_control_mean_similarity"]for r in cells)/n;mean_same=sum(r["same_wrapper_mean_similarity"]for r in both)/len(both);lead={h:[r for r in cells if r["host"]==h]for h in("d","ok")}
 variants=[{"variant_id":"V00","status":"PRIMARY","description":"Host×register-balanced exact-host cross-wrapper page-context similarity; 200 SHA256-smallest pairs per cell/type."},{"variant_id":"V01","status":"RUN_CONTROL","description":"Different-host match on register, host length, page size, and wrapper contrast."},{"variant_id":"V02","status":"RUN_SENSITIVITY","description":"Same-host same-wrapper comparison where capacity exists."},{"variant_id":"V03","status":"POSTSELECTED_DISPLAY","description":"GDT063 d and ok cells displayed but not selected for the manuscript-wide score."},{"variant_id":"V04","status":"NOT_RUN","description":"No external annotation score, semantic role, alternative parser, or f84r."}];write(VARIANTS,variants,list(variants[0]));p=binom_two(pos,n);status="CROSS_WRAPPER_PAGE_CONTEXT_PRESERVATION_SUPPORTED"if mean_diff>mean_ctrl and p<.05 else"CROSS_WRAPPER_PAGE_CONTEXT_PRESERVATION_WEAK_OR_UNSTABLE"
 gain=mean_diff-mean_ctrl;relative=gain/mean_ctrl if mean_ctrl else 0.;same_delta=mean_diff-mean_same;lead_pos={h:sum(r["different_minus_control"]>0 for r in z)for h,z in lead.items()};report=f"""# GDT064 — cross-wrapper PAGE_HOST page-context preservation

## Outcome

**{status}**

The inventory yields {len(units):,} page×host×wrapper units and
{len(pairrows):,} cross-folio exact-host pairs.  Across {n} host×register cells,
different-wrapper exact-host context similarity averages {mean_diff:.5f}
versus {mean_ctrl:.5f} for matched different-host controls; {pos}/{n} cells
are positive (descriptive exact sign p={p:.6g}).  The absolute gain is
{gain:+.5f}, or {100*relative:+.2f}% of the matched-control similarity.  In the
{len(both)} cells with both pair types, same-wrapper exact-host similarity
averages {mean_same:.5f}; different-wrapper minus same-wrapper is
{same_delta:+.5f}.

GDT063's `d` and `ok` cells are retained explicitly but are not allowed to set
the manuscript-wide statistic.  `ok` is positive against its matched control
in {lead_pos['ok']}/{len(lead['ok'])} register cells; `d` in
{lead_pos['d']}/{len(lead['d'])}.  Pair observations share pages and the sign
test treats host×register cells as exchangeable, so its p-value is a ranking
diagnostic rather than independent confirmation.  This is an internal page-inventory result;
it can support renderer invariance but cannot validate the archived external
annotation leads.  No role, gloss, word, morpheme, POS, sound, language,
plaintext, meaning, or translation is assigned.  f84r was excluded before
aggregation and not opened, retained, queried, joined, or scored.
""";REPORT.write_text(report,encoding="utf-8")
 result={"schema":"GDT064_CROSS_WRAPPER_PAGE_CONTEXT_RESULT_V1","status":status,"groups":len(rows),"units":len(units),"cross_folio_pairs":len(pairrows),"pair_cap_per_host_register_type":200,"host_register_cells":n,"positive_cells":pos,"sign_test_p":p,"mean_different_wrapper_similarity":mean_diff,"mean_matched_control_similarity":mean_ctrl,"different_minus_control":gain,"relative_gain_vs_control":relative,"same_wrapper_cells":len(both),"mean_same_wrapper_similarity":mean_same,"different_minus_same":same_delta,"postselected_leads":lead,"postselected_lead_positive_cells":lead_pos,"interpretation":"Internal page-context preservation only; external semantic preservation remains unconfirmed. Pair-sharing and exchangeable-cell caveats make the sign p descriptive.","claim_ceiling":"No role, gloss, word, morpheme, POS, sound, language, plaintext, meaning, or translation.","f84r":{"opened":False,"retained":False,"queried":False,"joined":False,"scored":False},"inputs":{SOURCE.name:sha(SOURCE),"gdt062_result.json":sha(ROOT/"gdt062_result.json"),"gdt063_result.json":sha(ROOT/"gdt063_result.json")},"implementation":{Path(__file__).name:sha(Path(__file__))},"outputs":{CELLS.name:sha(CELLS),PAIRS.name:sha(PAIRS),VARIANTS.name:sha(VARIANTS)},"documents":{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)}};result["result_content_sha256"]=csha(result);RESULT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":status,"cells":n,"positive":pos,"p":p,"diff":mean_diff,"control":mean_ctrl,"same":mean_same,"lead_cells":{h:len(z)for h,z in lead.items()}},sort_keys=True))
if __name__=="__main__":main()
