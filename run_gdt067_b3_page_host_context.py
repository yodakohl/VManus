#!/usr/bin/env python3
"""GDT067: same PAGE_HOST page context with versus without B3."""
from __future__ import annotations
import csv,hashlib,json,math
from collections import Counter,defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT/"gdt062_right_family_inventory.tsv";METHOD=ROOT/"GDT067_B3_PAGE_HOST_CONTEXT_METHOD.md";REPORT=ROOT/"GDT067_B3_PAGE_HOST_CONTEXT_REPORT.md";PAIRS=ROOT/"gdt067_b3_context_pairs.tsv";CELLS=ROOT/"gdt067_b3_context_cells.tsv";VARIANTS=ROOT/"gdt067_variant_log.tsv";RESULT=ROOT/"gdt067_result.json"
def read(p):
 with Path(p).open(encoding="utf-8",newline="")as h:return list(csv.DictReader(h,delimiter="\t"))
def write(p,rows,fields):
 with Path(p).open("w",encoding="utf-8",newline="")as h:w=csv.DictWriter(h,fieldnames=fields,delimiter="\t",lineterminator="\n");w.writeheader();w.writerows(rows)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
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
  for r in z:by.setdefault((r["page_host"],r["b3"],r["wrapper"],r["local_frame"],r["right_family"]),r)
  for (host,b3,wrapper,frame,right),r in sorted(by.items()):
   ctx=Counter(bag);del ctx[host];units.append({"unit_id":"|".join((page,host,b3,wrapper,frame,right)),"page":page,"physical_folio":r["physical_folio"],"register":r["register"],"host":host,"b3":b3,"wrapper":wrapper,"frame":frame,"right_family":right,"host_len_bucket":len(host)//2,"page_size_bucket":len(z)//25,"context":ctx})
 pool=defaultdict(list);cellsrc=defaultdict(lambda:{"0":[],"1":[]})
 for u in units:
  pool[u["register"],u["wrapper"],u["frame"],u["right_family"],u["b3"],u["host_len_bucket"],u["page_size_bucket"]].append(u);cellsrc[u["host"],u["register"],u["wrapper"],u["frame"],u["right_family"]][u["b3"]].append(u)
 pairrows=[];cellvals=defaultdict(list)
 for cell,z in sorted(cellsrc.items()):
  host,reg,wrapper,frame,right=cell
  for a in z["0"]:
   for b in z["1"]:
    if a["physical_folio"]==b["physical_folio"]:continue
    controls=[q for q in pool[reg,wrapper,frame,right,"1",a["host_len_bucket"],b["page_size_bucket"]]if q["physical_folio"]!=a["physical_folio"]and q["host"]!=host]
    if not controls:continue
    sim=wj(a["context"],b["context"]);control=sum(wj(a["context"],q["context"])for q in controls)/len(controls);pairrows.append({"host":host,"register":reg,"wrapper":wrapper,"frame":frame,"right_family":right,"b3_absent_unit":a["unit_id"],"b3_present_unit":b["unit_id"],"context_similarity":sim,"matched_control_similarity":control,"gain_vs_control":sim-control,"control_units":len(controls)});cellvals[cell].append((sim,control))
 cells=[]
 for (host,reg,wrapper,frame,right),z in sorted(cellvals.items()):
  sim=sum(x for x,_ in z)/len(z);ctrl=sum(y for _,y in z)/len(z);cells.append({"host":host,"register":reg,"wrapper":wrapper,"frame":frame,"right_family":right,"supported_pairs":len(z),"mean_context_similarity":sim,"mean_matched_control_similarity":ctrl,"gain_vs_control":sim-ctrl})
 write(PAIRS,[{k:f"{v:.12g}"if isinstance(v,float)else v for k,v in r.items()}for r in pairrows],list(pairrows[0]));write(CELLS,[{k:f"{v:.12g}"if isinstance(v,float)else v for k,v in r.items()}for r in cells],list(cells[0]));n=len(cells);pos=sum(r["gain_vs_control"]>0 for r in cells);sim=sum(r["mean_context_similarity"]for r in cells)/n;ctrl=sum(r["mean_matched_control_similarity"]for r in cells)/n;gain=sim-ctrl;p=binom_two(pos,n);status="B3_INTERNAL_HOST_CONTEXT_PRESERVATION_SUPPORTED"if gain>0 and p<.05 else"B3_CONTENT_NEUTRALITY_NOT_SUPPORTED_BY_INTERNAL_CONTEXT"
 regs={}
 for reg in sorted({r["register"]for r in cells}):
  q=[r for r in cells if r["register"]==reg];regs[reg]={"cells":len(q),"positive":sum(r["gain_vs_control"]>0 for r in q),"mean_gain":sum(r["gain_vs_control"]for r in q)/len(q)}
 variants=[{"variant_id":"V00","status":"PRIMARY","description":"Exact PAGE_HOST B3-absent versus B3-present, same register/wrapper/frame/right family, cross-folio."},{"variant_id":"V01","status":"RUN_CONTROL","description":"Different host with B3 present and matched compiler, host length and page size; unsupported pairs dropped."},{"variant_id":"V02","status":"INHERITED_FORMAL","description":"GDT045 terminal transfer and GDT052 DY-profile null are hash-bound, not rerun."},{"variant_id":"V03","status":"NOT_RUN","description":"No external semantic score, alternate parser, or f84r."}];write(VARIANTS,variants,list(variants[0]))
 report=f"""# GDT067 — B3 PAGE_HOST context preservation

## Outcome

**{status}**

There are {len(units):,} page-level host/compiler/B3 units, {len(pairrows):,}
supported B3-absent versus B3-present cross-folio pairs, and {n} balanced
host×register×wrapper×frame×RIGHT_FAMILY cells.  Exact-host page-context
similarity is {sim:.5f}, versus {ctrl:.5f} for matched different-host controls:
gain {gain:+.5f}.  {pos}/{n} cells are positive (descriptive sign p={p:.6g}).
Register diagnostics are {json.dumps(regs,sort_keys=True)}.

GDT045's line-closer result and GDT052's internal-DY null remain intact.  This
test asks only whether the host's internal page ecology survives B3 selection.
GDT059's external-content warning remains active regardless.  No role, gloss,
word, morpheme, POS, sound, language, plaintext, meaning, or translation is
assigned.  f84r was excluded and not opened, retained, queried, joined, or
scored.
""";REPORT.write_text(report,encoding="utf-8")
 result={"schema":"GDT067_B3_PAGE_HOST_CONTEXT_RESULT_V1","status":status,"groups":len(rows),"units":len(units),"supported_pairs":len(pairrows),"cells":n,"positive_cells":pos,"sign_test_p":p,"mean_exact_host_similarity":sim,"mean_matched_control_similarity":ctrl,"gain_vs_control":gain,"register_diagnostics":regs,"interpretation":"B3 is a confirmed probabilistic line closer; this result tests only internal PAGE_HOST ecology, while external content neutrality remains unconfirmed.","claim_ceiling":"No role, gloss, word, morpheme, POS, sound, language, plaintext, meaning, or translation.","f84r":{"opened":False,"retained":False,"queried":False,"joined":False,"scored":False},"inputs":{SOURCE.name:sha(SOURCE),"gdt045_result.json":sha(ROOT/"gdt045_result.json"),"gdt052_result.json":sha(ROOT/"gdt052_result.json"),"gdt059_result.json":sha(ROOT/"gdt059_result.json")},"implementation":{Path(__file__).name:sha(Path(__file__))},"outputs":{PAIRS.name:sha(PAIRS),CELLS.name:sha(CELLS),VARIANTS.name:sha(VARIANTS)},"documents":{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)}};result["result_content_sha256"]=csha(result);RESULT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":status,"units":len(units),"pairs":len(pairrows),"cells":n,"positive":pos,"p":p,"gain":gain},sort_keys=True))
if __name__=="__main__":main()
