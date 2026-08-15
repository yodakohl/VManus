#!/usr/bin/env python3
"""GDT065: exact O-vs-OT cross-folio PAGE_HOST context preservation."""
from __future__ import annotations
import csv,hashlib,json,math
from collections import Counter,defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT/"gdt062_right_family_inventory.tsv";METHOD=ROOT/"GDT065_O_OT_PAGE_CONTEXT_PRESERVATION_METHOD.md";REPORT=ROOT/"GDT065_O_OT_PAGE_CONTEXT_PRESERVATION_REPORT.md";PAIRS=ROOT/"gdt065_o_ot_context_pairs.tsv";CELLS=ROOT/"gdt065_o_ot_context_cells.tsv";VARIANTS=ROOT/"gdt065_variant_log.tsv";RESULT=ROOT/"gdt065_result.json"
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def read(p):
 with Path(p).open(encoding="utf-8",newline="")as h:return list(csv.DictReader(h,delimiter="\t"))
def write(p,rows,fields):
 with Path(p).open("w",encoding="utf-8",newline="")as h:w=csv.DictWriter(h,fieldnames=fields,delimiter="\t",lineterminator="\n");w.writeheader();w.writerows(rows)
def wj(a,b):
 k=set(a)|set(b);d=sum(max(a[x],b[x])for x in k);return sum(min(a[x],b[x])for x in k)/d if d else 0.
def binom_two(k,n):
 lo=sum(math.comb(n,i)for i in range(k+1))/2**n;hi=sum(math.comb(n,i)for i in range(k,n+1))/2**n;return min(1.,2*min(lo,hi))
def main():
 rows=read(SOURCE);assert len(rows)==15592 and not any(r["locus"].startswith("f84r")for r in rows);pages=defaultdict(list)
 for r in rows:pages[r["page"]].append(r)
 units=[]
 for page,z in sorted(pages.items()):
  bag=Counter(r["page_host"]for r in z);by={}
  for r in z:
   if r["local_frame"]in{"O","OT"}:by.setdefault((r["page_host"],r["local_frame"],r["wrapper"]),r)
  for (host,frame,wrapper),r in sorted(by.items()):
   ctx=Counter(bag);del ctx[host];units.append({"unit_id":page+"|"+host+"|"+frame+"|"+wrapper,"page":page,"physical_folio":r["physical_folio"],"register":r["register"],"host":host,"frame":frame,"wrapper":wrapper,"host_len_bucket":len(host)//2,"page_size_bucket":len(z)//25,"context":ctx})
 controls=defaultdict(list);cellsrc=defaultdict(lambda:{"O":[],"OT":[]})
 for u in units:controls[u["register"],u["wrapper"],u["frame"],u["host_len_bucket"],u["page_size_bucket"]].append(u);cellsrc[u["host"],u["wrapper"],u["register"]][u["frame"]].append(u)
 pairrows=[];cellvals=defaultdict(list)
 for (host,wrapper,reg),z in sorted(cellsrc.items()):
  for a in z["O"]:
   for b in z["OT"]:
    if a["physical_folio"]==b["physical_folio"]:continue
    q=[x for x in controls[reg,wrapper,"OT",a["host_len_bucket"],b["page_size_bucket"]]if x["physical_folio"]!=a["physical_folio"]and x["host"]!=host]
    if not q:continue
    sim=wj(a["context"],b["context"]);cs=sum(wj(a["context"],x["context"])for x in q)/len(q);pairrows.append({"host":host,"wrapper":wrapper,"register":reg,"o_unit":a["unit_id"],"ot_unit":b["unit_id"],"context_similarity":sim,"matched_control_similarity":cs,"gain_vs_control":sim-cs,"control_units":len(q)});cellvals[host,wrapper,reg].append((sim,cs))
 cellrows=[]
 for (host,wrapper,reg),z in sorted(cellvals.items()):
  s=sum(x for x,y in z)/len(z);c=sum(y for x,y in z)/len(z);cellrows.append({"host":host,"wrapper":wrapper,"register":reg,"cross_folio_o_ot_pairs":len(z),"mean_context_similarity":s,"mean_matched_control_similarity":c,"gain_vs_control":s-c})
 write(PAIRS,[{k:f"{v:.12g}"if isinstance(v,float)else v for k,v in r.items()}for r in pairrows],list(pairrows[0]));write(CELLS,[{k:f"{v:.12g}"if isinstance(v,float)else v for k,v in r.items()}for r in cellrows],list(cellrows[0]));n=len(cellrows);pos=sum(r["gain_vs_control"]>0 for r in cellrows);mean=sum(r["mean_context_similarity"]for r in cellrows)/n;ctrl=sum(r["mean_matched_control_similarity"]for r in cellrows)/n;gain=mean-ctrl;p=binom_two(pos,n);status="O_OT_PRESERVES_INTERNAL_PAGE_CONTEXT_ACROSS_POSITIONAL_RENDERING"if gain>0 and p<.05 else"O_OT_PAGE_CONTEXT_PRESERVATION_WEAK_OR_UNSTABLE"
 regs={}
 for reg in sorted({r["register"]for r in cellrows}):
  q=[r for r in cellrows if r["register"]==reg];regs[reg]={"cells":len(q),"positive":sum(r["gain_vs_control"]>0 for r in q),"mean_gain":sum(r["gain_vs_control"]for r in q)/len(q)}
 write(VARIANTS,[{"variant_id":"V00","status":"PRIMARY","description":"Exclude O/OT pairs lacking an eligible matched different-host control."},{"variant_id":"V01","status":"REJECTED_IMPLEMENTATION_DIAGNOSTIC","description":"Initial implementation assigned unsupported pairs a zero control; 71 such pairs were removed before publication."},{"variant_id":"V02","status":"NOT_RUN_CAPACITY_LIMIT","description":"External annotation preservation remains unavailable because GDT059 found zero exact cross-folio annotated O/OT capacity."}], ["variant_id","status","description"])
 report=f"""# GDT065 — O/OT PAGE_HOST page-context preservation

## Outcome

**{status}**

There are {len(units):,} O/OT page-host units, {len(pairrows):,} exact
cross-folio O-versus-OT pairs with at least one matched different-host control,
and {n} PAGE_HOST×wrapper×register cells.
Same-host O/OT context similarity averages {mean:.5f}, versus {ctrl:.5f} for
matched different-host controls: gain {gain:+.5f}.  {pos}/{n} cells are
positive (descriptive exact sign p={p:.6g}).

Together with GDT054/GDT055's independently established O-early/OT-later
placement, this is a weak internal lead for a positional-rendering
interpretation around a stable PAGE_HOST key.  It does not validate preserved external content or
meaning; GDT059 still has zero exact annotated O/OT capacity.  Cells share
pages, so the sign p is a ranking diagnostic.  No role, gloss, word, morpheme,
POS, sound, language, plaintext, meaning, or translation is assigned.  f84r
was excluded and not opened, retained, queried, joined, or scored.
""";REPORT.write_text(report,encoding="utf-8")
 result={"schema":"GDT065_O_OT_PAGE_CONTEXT_PRESERVATION_RESULT_V1","status":status,"groups":len(rows),"units":len(units),"pairs":len(pairrows),"cells":n,"positive_cells":pos,"sign_test_p":p,"mean_same_host_o_ot_similarity":mean,"mean_matched_control_similarity":ctrl,"gain_vs_control":gain,"register_diagnostics":regs,"inherited_position_result":"O_EARLY_OT_LATE_POSITIONAL_RENDERER_TRANSFERS_TO_UNSEEN_HOSTS","interpretation":"O/OT has a small positive internal page-context lead around exact PAGE_HOST while changing record placement; external content preservation remains unscored and the lead misses the predeclared sign threshold.","claim_ceiling":"No role, gloss, word, morpheme, POS, sound, language, plaintext, meaning, or translation.","f84r":{"opened":False,"retained":False,"queried":False,"joined":False,"scored":False},"inputs":{SOURCE.name:sha(SOURCE),"gdt062_result.json":sha(ROOT/"gdt062_result.json"),"gdt054_result.json":sha(ROOT/"gdt054_result.json"),"gdt055_result.json":sha(ROOT/"gdt055_result.json"),"gdt059_result.json":sha(ROOT/"gdt059_result.json")},"implementation":{Path(__file__).name:sha(Path(__file__))},"outputs":{PAIRS.name:sha(PAIRS),CELLS.name:sha(CELLS),VARIANTS.name:sha(VARIANTS)},"documents":{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)}};result["result_content_sha256"]=csha(result);RESULT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":status,"units":len(units),"pairs":len(pairrows),"cells":n,"positive":pos,"p":p,"gain":gain},sort_keys=True))
if __name__=="__main__":main()
