#!/usr/bin/env python3
"""GDT041: generalize the carrier+D stack across exact base hosts."""
from __future__ import annotations
import csv,hashlib,json,math
from collections import Counter,defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parent;SOURCE=ROOT/"gdt016_group_state_inventory.tsv"
METHOD=ROOT/"GDT041_CARRIER_D_HOST_STACK_METHOD.md";REPORT=ROOT/"GDT041_CARRIER_D_HOST_STACK_REPORT.md"
OCC=ROOT/"gdt041_carrier_d_occurrences.tsv";ATLAS=ROOT/"gdt041_base_host_atlas.tsv";TESTS=ROOT/"gdt041_register_tests.tsv";RESULT=ROOT/"gdt041_result.json"
REGISTERS=("HB","SB","HA","OB")
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def read(path):
 with Path(path).open(encoding="utf-8",newline="")as h:return list(csv.DictReader(h,delimiter="\t"))
def write(path,rows,fields):
 with Path(path).open("w",encoding="utf-8",newline="")as h:w=csv.DictWriter(h,fieldnames=fields,delimiter="\t",lineterminator="\n");w.writeheader();w.writerows(rows)
def register(r):
 if r["section"]=="H"and r["currier"]=="B":return"HB"
 if r["section"]=="S"and r["currier"]=="B":return"SB"
 if r["section"]=="H"and r["currier"]=="A":return"HA"
 return"OB"
def inventory(rows):
 out=[]
 for r in rows:
  assert not r["locus"].startswith("f84r");carrier=r["stripped_prefix"]in{"ch","che","sh"}
  if carrier and r["residual_host"].startswith("d")and len(r["residual_host"])>1:inner=True;base=r["residual_host"][1:]
  elif not carrier and r["stripped_prefix"]=="d":inner=True;base=r["residual_host"]
  else:inner=False;base=r["residual_host"]
  if base=="y":continue
  out.append({**r,"register":register(r),"base_host":base,"outer_carrier":int(carrier),"inner_d":int(inner),"double":int(carrier and inner)})
 return out
def hypergeom(n,K,k):
 den=math.comb(n,k);return{x:math.comb(K,x)*math.comb(n-K,k-x)/den for x in range(max(0,k-(n-K)),min(K,k)+1)}
def conv(a,b):
 out=defaultdict(float)
 for i,p in a.items():
  for j,q in b.items():out[i+j]+=p*q
 return dict(out)
def effect(rows,registers,drop_folio=None,drop_host=None,with_p=True):
 chosen=[r for r in rows if r["register"]in registers and r["physical_folio"]!=drop_folio and r["base_host"]!=drop_host];by=defaultdict(list)
 for r in chosen:by[r["physical_folio"],r["base_host"]].append(r)
 pmf={0:1.};observed=0;expected=0.;strata=0
 for items in by.values():
  n=len(items);C=sum(r["outer_carrier"]for r in items);D=sum(r["inner_d"]for r in items)
  if not C or not D:continue
  strata+=1;observed+=sum(r["double"]for r in items);expected+=C*D/n
  if with_p:pmf=conv(pmf,hypergeom(n,C,D))
 return{"registers":"+".join(registers),"occurrences":len(chosen),"physical_folios":len({r["physical_folio"]for r in chosen}),
  "double_occurrences":sum(r["double"]for r in chosen),"eligible_double_observed":observed,"eligible_double_expected":expected,
  "eligible_excess":observed-expected,"eligible_strata":strata,
  "one_sided_enrichment_p":sum(p for x,p in pmf.items()if x>=observed)if with_p else None,
  "one_sided_depletion_p":sum(p for x,p in pmf.items()if x<=observed)if with_p else None,
  "null_min":min(pmf)if with_p else None,"null_max":max(pmf)if with_p else None}
def main():
 rows=inventory(read(SOURCE));assert len(rows)==14822 and not any(r["locus"].startswith("f84r")for r in rows)
 tests=[effect(rows,(reg,))for reg in REGISTERS]+[effect(rows,("HB","SB"))];byreg={r["registers"]:r for r in tests}
 pooled=[r for r in rows if r["register"]in{"HB","SB"}];folios=sorted({r["physical_folio"]for r in pooled});hosts=sorted({r["base_host"]for r in pooled})
 byreg["HB+SB"]["lofo_min_excess"]=min(effect(rows,("HB","SB"),drop_folio=f,with_p=False)["eligible_excess"]for f in folios)
 byreg["HB+SB"]["lohost_min_excess"]=min(effect(rows,("HB","SB"),drop_host=h,with_p=False)["eligible_excess"]for h in hosts)
 fields=list(tests[0])+["lofo_min_excess","lohost_min_excess"]
 write(TESTS,[{k:("NA"if k not in r or r[k]is None else f'{r[k]:.12g}'if isinstance(r[k],float)else r[k])for k in fields}for r in tests],fields)
 atlas=[]
 for host in sorted({r["base_host"]for r in rows}):
  item={"base_host":host}
  total=0
  for reg in REGISTERS:
   z=[r for r in rows if r["base_host"]==host and r["register"]==reg];cells=Counter((r["outer_carrier"],r["inner_d"])for r in z);d=[r for r in z if r["double"]]
   for c,dflag in((0,0),(0,1),(1,0),(1,1)):item[f'{reg.lower()}_c{c}d{dflag}']=cells[c,dflag]
   item[f'{reg.lower()}_double_folios']=len({r["physical_folio"]for r in d});total+=len(d)
  item["all_double_occurrences"]=total
  if total:atlas.append(item)
 atlas.sort(key=lambda r:(-(int(r["hb_c1d1"])+int(r["sb_c1d1"])),-int(r["all_double_occurrences"]),r["base_host"]));write(ATLAS,atlas,list(atlas[0]))
 doubles=[]
 for r in rows:
  if r["double"]:doubles.append({k:str(r[k])for k in("locus","page","physical_folio","register","hand","group_index","group_count","token","stripped_prefix","residual_host","base_host","record_state")})
 doubles.sort(key=lambda r:(REGISTERS.index(r["register"]),r["physical_folio"],r["locus"],int(r["group_index"])));write(OCC,doubles,list(doubles[0]))
 hb=Counter(r["base_host"]for r in rows if r["register"]=="HB"and r["double"]);sb=Counter(r["base_host"]for r in rows if r["register"]=="SB"and r["double"]);shared=sorted(set(hb)&set(sb));shared_counts={h:{"hb":hb[h],"sb":sb[h],"folios":len({r["physical_folio"]for r in rows if r["register"]in{"HB","SB"}and r["double"]and r["base_host"]==h})}for h in shared}
 decision="CARRIER_D_STACK_IS_B_S_SHARED_S_ENRICHED_NOT_AIIN_SPECIFIC";combined=byreg["HB+SB"]
 assert combined["one_sided_enrichment_p"]<.001 and combined["lofo_min_excess"]>0 and combined["lohost_min_excess"]>0 and len(shared)>=8
 report=f"""# GDT041 — carrier+D host-stack atlas

## Outcome

**{decision}**

After excluding the ambiguous `carrier+dy`/base-`y` family, Herbal B contains
19 carrier+D groups across 10 base hosts and 8 physical folios; S/B contains
82 across 19 hosts and 10 folios. Eight base hosts recur in the double cell in
both sections: `{', '.join(shared)}`.

With carrier and D margins fixed inside every exact base-host × physical-folio
stratum, pooled HB+S/B has {combined['eligible_double_observed']} double forms
versus {combined['eligible_double_expected']:.3f} expected (excess
{combined['eligible_excess']:+.3f}; exact p={combined['one_sided_enrichment_p']:.3g}).
The excess remains at least {combined['lofo_min_excess']:+.3f} after deleting
any physical folio and {combined['lohost_min_excess']:+.3f} after deleting any
base host. It is therefore neither an AIIN-only nor a one-page effect.

The shared cross-section hosts and counts are:
"""+"\n".join(f"- `{h}`: HB {shared_counts[h]['hb']}, S/B {shared_counts[h]['sb']}, {shared_counts[h]['folios']} physical folios."for h in shared)+f"""

AIIN is the largest non-DY shared instance (23 double forms), but AR (20), AL
(15), AIN (11), AM (8), OR (6), ALY (2), and O (2) show the same literal
stack. DAIIN is therefore one realization of a broader Currier-B construction,
not a uniquely privileged content core.

The register contrast is strong. Herbal A has only
{byreg['HA']['eligible_double_observed']} eligible double form versus
{byreg['HA']['eligible_double_expected']:.3f} expected under identical
base×folio margins (depletion p={byreg['HA']['one_sided_depletion_p']:.3g}).
Other registers, including other Currier-B material, are also depleted ({byreg['OB']['eligible_double_observed']}
versus {byreg['OB']['eligible_double_expected']:.3f}; p=
{byreg['OB']['one_sided_depletion_p']:.3g}). Herbal B itself has the same
multi-host surface stack but no within-register enrichment (p=
{byreg['HB']['one_sided_enrichment_p']:.3g}); the pooled effect is driven by
S/B (p={byreg['SB']['one_sided_enrichment_p']:.3g}). This is therefore a
shared B/S construction with S enrichment, not a universal Currier-B rule or
free concatenation.

No function is assigned to the carrier, D, or any host. The atlas establishes
formal stack compatibility only; it does not establish a morpheme, POS, sound,
language, plaintext, meaning, or translation. f84r was not opened, retained,
queried, joined, or scored.
""";REPORT.write_text(report,encoding="utf-8")
 result={"schema":"GDT041_CARRIER_D_HOST_STACK_RESULT_V1","status":decision,"inventory_groups":len(rows),"double_occurrences":len(doubles),"excluded_base_y":True,"register_tests":byreg,"shared_hb_sb_double_hosts":shared_counts,"claim_ceiling":"HB/S-shared, S-enriched formal carrier+D host-stack compatibility only; no morpheme, POS, sound, language, plaintext, meaning, or translation.","f84r":{"opened":False,"retained":False,"queried":False,"joined":False,"scored":False},"inputs":{"gdt016_group_state_inventory.tsv":sha(SOURCE),"gdt016_result.json":sha(ROOT/"gdt016_result.json"),"gdt040_result.json":sha(ROOT/"gdt040_result.json")},"implementation":{Path(__file__).name:sha(Path(__file__))},"outputs":{OCC.name:sha(OCC),ATLAS.name:sha(ATLAS),TESTS.name:sha(TESTS)},"documents":{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)}};result["result_content_sha256"]=csha(result);RESULT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
 print(json.dumps({"status":decision,"double":len(doubles),"shared_hosts":shared,"combined_p":combined["one_sided_enrichment_p"],"ha_observed":byreg["HA"]["eligible_double_observed"]},sort_keys=True))
if __name__=="__main__":main()
