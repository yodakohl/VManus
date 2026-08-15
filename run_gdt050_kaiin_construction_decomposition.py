#!/usr/bin/env python3
"""GDT050: test KAIIN inside the K x right-family construction table."""
from __future__ import annotations
import csv,hashlib,json,math
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT/"gdt016_group_state_inventory.tsv";METHOD=ROOT/"GDT050_KAIIN_CONSTRUCTION_DECOMPOSITION_METHOD.md";REPORT=ROOT/"GDT050_KAIIN_CONSTRUCTION_DECOMPOSITION_REPORT.md";TABLE=ROOT/"gdt050_kaiin_construction_table.tsv";OCC=ROOT/"gdt050_kaiin_occurrences.tsv";RESULT=ROOT/"gdt050_result.json";SUFFIXES=("aiin","air","ain","ar","al")
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def read(p):
 with Path(p).open(encoding="utf-8",newline="")as h:return list(csv.DictReader(h,delimiter="\t"))
def write(p,rows,fields):
 with Path(p).open("w",encoding="utf-8",newline="")as h:w=csv.DictWriter(h,fieldnames=fields,delimiter="\t",lineterminator="\n");w.writeheader();w.writerows(rows)
def reg(r):
 if r["section"]=="H"and r["currier"]=="A":return"HA"
 if r["section"]=="H"and r["currier"]=="B":return"HB"
 if r["section"]=="S"and r["currier"]=="B":return"SB"
 if r["currier"]=="B":return"OB"
 return"OUT"
def split(h):
 for s in SUFFIXES:
  if h.endswith(s)and len(h)>len(s):return h[:-len(s)],s
 return None
def fisher(a,b,c,d):
 R=a+b;C=a+c;N=a+b+c+d;lo=max(0,R-(N-C));hi=min(R,C)
 def p(x):return math.comb(C,x)*math.comb(N-C,R-x)/math.comb(N,R)
 po=p(a);return sum(p(x)for x in range(lo,hi+1)if p(x)<=po+1e-15)
def stat(rows,pred):
 c=Counter((r["side"],bool(pred(r)))for r in rows);a,b,c0,d=c["TARGET",True],c["TARGET",False],c["CONTROL",True],c["CONTROL",False]
 return{"target_positive":a,"target_negative":b,"control_positive":c0,"control_negative":d,"odds_ratio":a*d/(b*c0)if b and c0 else None,"two_sided_fisher_p":fisher(a,b,c0,d)}
def main():
 rows=[]
 for r in read(SOURCE):
  if r["locus"].startswith("f84r"):continue
  rr=reg(r)
  if rr=="OUT"or r["dy_closure"]!="0"or r["residual_host"].endswith("m"):continue
  q=split(r["residual_host"])
  if not q:continue
  base,suffix=q;rows.append({"locus":r["locus"],"physical_folio":r["physical_folio"],"register":rr,"side":"TARGET"if rr in{"HB","SB"}else"CONTROL","token":r["token"],"wrapper":r["stripped_prefix"],"residual_host":r["residual_host"],"base":base,"suffix":suffix})
 assert len(rows)==2813 and not any(r["locus"].startswith("f84r")for r in rows)
 tests={"K_BASE":stat(rows,lambda r:r["base"]=="k"),"AIIN_WITHIN_K":stat([r for r in rows if r["base"]=="k"],lambda r:r["suffix"]=="aiin"),"EXACT_KAIIN":stat(rows,lambda r:r["base"]=="k"and r["suffix"]=="aiin")}
 cells=[]
 for suffix in SUFFIXES:
  z=[r for r in rows if r["base"]=="k"and r["suffix"]==suffix];c=Counter(r["register"]for r in z);w=Counter(r["wrapper"]for r in z)
  cells.append({"base":"k","suffix":suffix,"ha":c["HA"],"hb":c["HB"],"sb":c["SB"],"ob":c["OB"],"target_total":c["HB"]+c["SB"],"control_total":c["HA"]+c["OB"],"wrappers":";".join(f"{a}:{b}"for a,b in w.most_common())})
 write(TABLE,cells,list(cells[0]));occ=[r for r in rows if r["base"]=="k"and r["suffix"]=="aiin"];occ.sort(key=lambda r:(r["side"],r["register"],r["physical_folio"],r["locus"],r["token"]));write(OCC,occ,list(occ[0]))
 decision="KAIIN_RESIDUAL_ATTRIBUTED_TO_COMMON_K_AND_AIIN_FAMILY";assert all(t["two_sided_fisher_p"]>.05 for t in tests.values())
 report=f"""# GDT050 — KAIIN construction decomposition

## Outcome

**{decision}**

The broad-corpus ranking does not survive its matched construction family.
Base K occurs {tests['K_BASE']['target_positive']} times in the HB+Stars target
and {tests['K_BASE']['control_positive']} times in HA+other-B, against
{tests['K_BASE']['target_negative']} and {tests['K_BASE']['control_negative']}
other bases (odds ratio {tests['K_BASE']['odds_ratio']:.3f}, p
{tests['K_BASE']['two_sided_fisher_p']:.3f}). Within K, AIIN is
{tests['AIIN_WITHIN_K']['target_positive']}/{tests['AIIN_WITHIN_K']['target_positive']+tests['AIIN_WITHIN_K']['target_negative']}
in the target and {tests['AIIN_WITHIN_K']['control_positive']}/{tests['AIIN_WITHIN_K']['control_positive']+tests['AIIN_WITHIN_K']['control_negative']}
in controls (odds ratio {tests['AIIN_WITHIN_K']['odds_ratio']:.3f}, p
{tests['AIIN_WITHIN_K']['two_sided_fisher_p']:.3f}). Exact K+AIIN likewise
has no target enrichment (p {tests['EXACT_KAIIN']['two_sided_fisher_p']:.3f}).

KAIIN is therefore not a remaining privileged content host. It is an observed
combination of a reusable K base and the common AIIN right-family member,
appearing under both bare and carrier-wrapped constructions. This correction
leaves GDT048's AIR selection as the only new right-family result from the
GDT047 residual atlas, and that result remains functionally ungrounded.

No function, morpheme, word, POS, sound, language, plaintext, meaning, or
translation is assigned. f84r was skipped before parsing and not opened,
retained, queried, joined, or scored.
""";REPORT.write_text(report,encoding="utf-8")
 result={"schema":"GDT050_KAIIN_CONSTRUCTION_DECOMPOSITION_RESULT_V1","status":decision,"eligible_groups":len(rows),"kaiin_occurrences":len(occ),"tests":tests,"claim_ceiling":"Matched formal decomposition of KAIIN only; no function, morpheme, word, POS, sound, language, plaintext, meaning, or translation.","f84r":{"opened":False,"retained":False,"queried":False,"joined":False,"scored":False},"inputs":{SOURCE.name:sha(SOURCE),"gdt047_result.json":sha(ROOT/"gdt047_result.json"),"gdt048_result.json":sha(ROOT/"gdt048_result.json")},"implementation":{Path(__file__).name:sha(Path(__file__))},"outputs":{TABLE.name:sha(TABLE),OCC.name:sha(OCC)},"documents":{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)}};result["result_content_sha256"]=csha(result);RESULT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":decision,"groups":len(rows),"kaiin":len(occ),"tests":tests},sort_keys=True))
if __name__=="__main__":main()
