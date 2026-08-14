#!/usr/bin/env python3
"""Exact-host conditional control for the Q/L previous-DY association."""
from __future__ import annotations
import csv,hashlib,json,math
from collections import Counter,defaultdict
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def read(n):
 with (ROOT/n).open(encoding="utf-8",newline="")as h:return list(csv.DictReader(h,delimiter="\t"))
def write(n,rows):
 with (ROOT/n).open("w",encoding="utf-8",newline="")as h:w=csv.DictWriter(h,fieldnames=list(rows[0]),delimiter="\t",lineterminator="\n");w.writeheader();w.writerows(rows)
def branch(f):
 if"QJB"in f or"QKB"in f:return"Q"
 if"LJB"in f or"LKB"in f:return"L"
 return"OTHER"
def pmf(n,k,m):
 out=np.zeros(min(k,m)+1);den=math.comb(n,m)
 for x in range(max(0,m-(n-k)),min(m,k)+1):out[x]=math.comb(k,x)*math.comb(n-k,m-x)/den
 return out
def test(rows,level):
 strata=defaultdict(list)
 for x in rows:strata[(x[level],x["host"],x["state"],x["position_bin"])].append((x["branch"]=="Q",x["previous_dy"]))
 law=np.array([1.]);obs=0;exp=num=den=0.;informative=0
 for values in strata.values():
  n=len(values);m=sum(q for q,y in values);k=sum(y for q,y in values)
  if not(0<m<n and 0<k<n):continue
  informative+=1;o=sum(q and y for q,y in values);obs+=o;exp+=m*k/n;w=m*(n-m)/n;num+=w*(o/m-(k-o)/(n-m));den+=w;law=np.convolve(law,pmf(n,k,m))
 effect=num/den if den else 0.;p=1.
 if den:d=abs(obs-exp);p=min(1.,float(law[np.abs(np.arange(len(law))-exp)>=d-1e-12].sum()))
 return effect,p,informative,obs,exp
def main():
 inv=read("gdt016_group_state_inventory.tsv");assert len(inv)==15592 and not any(r["locus"].startswith("f84r")for r in inv);lines=defaultdict(list)
 for r in inv:lines[r["locus"]].append(r)
 data=[]
 for locus,line in lines.items():
  line.sort(key=lambda r:int(r["group_index"]))
  for i,r in enumerate(line):
   b=branch(r["family_surface"])
   if r["currier"]!="B"or b=="OTHER":continue
   n=int(r["group_count"]);z=(int(r["group_index"])-1)/(n-1)if n>1 else.5;data.append({"branch":b,"host":r["residual_host"],"state":r["record_state"],"page":r["page"],"folio":r["physical_folio"],"section":r["section"],"position_bin":min(3,int(z*4)),"previous_dy":int(i>0 and line[i-1]["record_state"]=="DY_RESOLUTION"),"token":r["token"]})
 seen=defaultdict(set)
 for x in data:seen[x["host"],x["state"]].add(x["branch"])
 eligible={k for k,v in seen.items()if v=={"Q","L"}};panel=[x for x in data if(x["host"],x["state"])in eligible]
 inventory=[]
 for host,state in sorted(eligible):
  x=[r for r in panel if r["host"]==host and r["state"]==state];c=Counter((r["branch"],r["previous_dy"])for r in x);inventory.append({"residual_host":host,"state":state,"groups":len(x),"q_postdy":c["Q",1],"q_not_postdy":c["Q",0],"l_postdy":c["L",1],"l_not_postdy":c["L",0],"q_tokens":"|".join(sorted({r["token"]for r in x if r["branch"]=="Q"})),"l_tokens":"|".join(sorted({r["token"]for r in x if r["branch"]=="L"})),"claim_state":"EXACT_HOST_BRANCH_CAPACITY_NOT_MEANING"})
 write("gdt030_exact_host_overlap_inventory.tsv",inventory);tests=[]
 for partition,rows in[("ALL",panel)]+[(s,[x for x in panel if x["state"]==s])for s in sorted({x["state"]for x in panel})]:
  for level in("page","folio","section"):
   e,p,n,o,z=test(rows,level);tests.append({"partition":partition,"matching_level":level.upper(),"groups":len(rows),"effect":f"{e:.12f}","exact_p":f"{p:.12g}","informative_strata":n,"observed_q_postdy":o,"expected_q_postdy":f"{z:.12f}","claim_state":"EXACT_HOST_CONTROL_NOT_MEANING"})
 write("gdt030_exact_host_history_tests.tsv",tests);primary=next(r for r in tests if r["partition"]=="ALL"and r["matching_level"]=="PAGE");folio=next(r for r in tests if r["partition"]=="ALL"and r["matching_level"]=="FOLIO");section=next(r for r in tests if r["partition"]=="ALL"and r["matching_level"]=="SECTION");status="EXACT_HOST_CONTROLLED_HISTORY_OPERATOR_NOT_CONFIRMED"
 report=f"""# GDT030 exact-host Q/L history control

Status: **{status.replace('_',' ')}**

Only eight residual-host × state cells admit both Q and L, yielding {len(panel)}
groups. They include exact formal pairs `tedy/shedy`, `teedy/sheedy`,
`tchdy/shchdy`, `ted/shed`, `tedal/shedal`, `tedain/shedain`,
`tedaiin/shedaiin`, and `tedam/shedam`.

After fixing exact host, state, position, and page, previous-DY has effect
{float(primary['effect']):+.4f}, p={float(primary['exact_p']):.3f}, with only
{primary['informative_strata']} informative strata. Folio matching gives
{float(folio['effect']):+.4f}, p={float(folio['exact_p']):.3f}. Section pooling
is positive ({float(section['effect']):+.4f}, p={float(section['exact_p']):.4f})
but is too coarse to distinguish local history from register ecology.

Therefore the strong GDT026 association does not establish a separable Q/L
history operator. The better model is host-licensed construction choice with
history/register-correlated ecology. This exact-host panel is small, so it
does not prove history irrelevant; it removes the claimed independent bit.
Only the frozen GDT016 inventory is used and contains no f84r row. f84r was
not opened, retained, joined, or scored. No role, morpheme, word, sound,
language, plaintext, meaning, or translation is assigned.
""";(ROOT/"GDT030_EXACT_HOST_HISTORY_CONTROL_REPORT.md").write_text(report)
 outputs=("gdt030_exact_host_overlap_inventory.tsv","gdt030_exact_host_history_tests.tsv","GDT030_EXACT_HOST_HISTORY_CONTROL_REPORT.md");inputs=("gdt016_group_state_inventory.tsv","gdt016_result.json","gdt026_result.json","gdt029_result.json","GDT030_EXACT_HOST_HISTORY_CONTROL_METHOD.md")
 result={"schema":"GDT030_EXACT_HOST_HISTORY_CONTROL_RESULT_V1","status":status,"groups":len(panel),"eligible_host_state_cells":len(eligible),"tests":len(tests),"primary":primary,"folio":folio,"section":section,"interpretation":"Q/L history association is not confirmed as a separable operator after exact-host local control.","f84r":{"input_contains_rows":False,"opened":False,"retained":False,"joined":False,"scored":False},"claim_ceiling":"Exact-host formal association control only; no independently identified operator, role, morpheme, word, sound, language, plaintext, meaning, or translation.","inputs":{n:sha(ROOT/n)for n in inputs},"implementation":{"run_gdt030_exact_host_history_control.py":sha(Path(__file__))},"outputs":{n:sha(ROOT/n)for n in outputs}};result["result_content_sha256"]=csha(result);(ROOT/"gdt030_result.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":status,"groups":len(panel),"cells":len(eligible),"primary":primary,"folio":folio,"section":section},sort_keys=True))
if __name__=="__main__":main()
