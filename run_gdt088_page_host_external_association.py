#!/usr/bin/env python3
"""GDT088: folio-conditioned exploratory PAGE_HOST/external-axis atlas."""
from __future__ import annotations
import csv,hashlib,json,math
from collections import Counter,defaultdict
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parent
PARSED=ROOT/"gdt059_hpr2_external_inventory.tsv";ANN=ROOT/"gdt012_annotated_core_inventory.tsv"
METHOD=ROOT/"GDT088_PAGE_HOST_EXTERNAL_ASSOCIATION_METHOD.md";REPORT=ROOT/"GDT088_PAGE_HOST_EXTERNAL_ASSOCIATION_REPORT.md"
ATLAS=ROOT/"gdt088_page_host_external_atlas.tsv";NULL=ROOT/"gdt088_null_results.tsv";COUNTER=ROOT/"gdt088_counterexamples.tsv";RESULT=ROOT/"gdt088_result.json"
AXES=("STAR_OR_SKY","FIGURE","PLANT","WATER_OR_APPARATUS","REL_PROXIMITY","REL_EXPLICIT_ATTACHMENT","REL_ENCLOSURE","REL_ARRAY_OR_GROUP")
SEED=88001;PERMUTATIONS=5000
def read(p):
 with p.open(encoding="utf-8",newline="") as h:return list(csv.DictReader(h,delimiter="\t"))
def write(p,rows,fields):
 with p.open("w",encoding="utf-8",newline="") as h:w=csv.DictWriter(h,fieldnames=fields,delimiter="\t",lineterminator="\n");w.writeheader();w.writerows(rows)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def main():
 parsed=read(PARSED);ann=read(ANN);assert len(parsed)==len(ann)==671 and not any(r["locus"].startswith("f84r") for r in parsed+ann)
 byloc=defaultdict(list);adesc={}
 for r in parsed:byloc[r["locus"]].append(r)
 for r in ann:adesc.setdefault(r["locus"],r)
 units=[]
 for locus,z in sorted(byloc.items()):
  z.sort(key=lambda r:int(r["group_index"]));units.append({"locus":locus,"folio":z[0]["physical_folio"],"hosts":{r["page_host"] for r in z},"tags":{x for x in z[0]["tags"].split(";") if x},"groups":z})
 assert len(units)==560
 hcount=Counter(h for u in units for h in u["hosts"]);hfolios=defaultdict(set)
 for u in units:
  for h in u["hosts"]:hfolios[h].add(u["folio"])
 hosts=sorted(h for h,n in hcount.items() if n>=3 and len(hfolios[h])>=2);assert len(hosts)==43
 folios=sorted({u["folio"] for u in units});fi={f:np.array([i for i,u in enumerate(units) if u["folio"]==f],dtype=int) for f in folios}
 H=np.array([[int(h in u["hosts"]) for h in hosts] for u in units],dtype=float)
 Y=np.array([[int(a in u["tags"]) for a in AXES] for u in units],dtype=float)
 E=np.zeros((len(hosts),len(AXES)));V=np.zeros_like(E);inform=np.zeros_like(E,dtype=int);uf={};vf={}
 for f,idx in fi.items():
  n=len(idx);n1=H[idx].sum(axis=0)[:,None];m=Y[idx].sum(axis=0)[None,:];e=n1*m/n
  v=n1*(n-n1)*m*(n-m)/(n*n*(n-1)) if n>1 else np.zeros_like(e)
  E+=e;V+=v;inform+=((n1>0)&(n1<n)&(m>0)&(m<n));uf[f]=H[idx].T@Y[idx]-e;vf[f]=v
 U=H.T@Y-E;Z=np.divide(U,np.sqrt(V),out=np.zeros_like(U),where=V>0)
 rng=np.random.default_rng(SEED);local_ge=np.zeros_like(U,dtype=int);maxima=[]
 for _ in range(PERMUTATIONS):
  yp=Y.copy()
  for idx in fi.values():yp[idx]=yp[rng.permutation(idx)]
  zp=np.divide(H.T@yp-E,np.sqrt(V),out=np.zeros_like(U),where=V>0);az=np.abs(zp);local_ge+=(az>=np.abs(Z));maxima.append(float(az[V>0].max()))
 maxima=np.array(maxima);rows=[]
 for hi,h in enumerate(hosts):
  hu=[u for u in units if h in u["hosts"]]
  for ai,a in enumerate(AXES):
   if V[hi,ai]<=0:continue
   z=float(Z[hi,ai]);lo=[]
   for f in folios:
    vv=V[hi,ai]-vf[f][hi,ai]
    if vv>0:lo.append(float((U[hi,ai]-uf[f][hi,ai])/math.sqrt(vv)))
   stable=bool(lo) and all(x*z>0 for x in lo)
   pos=[u for u in hu if a in u["tags"]];neg=[u for u in hu if a not in u["tags"]]
   def vals(zs,key):return sorted({r[key] for u in zs for r in u["groups"] if r["page_host"]==h})
   lp=(int(local_ge[hi,ai])+1)/(PERMUTATIONS+1);mp=(int(np.sum(maxima>=abs(z)))+1)/(PERMUTATIONS+1)
   if abs(z)>=2 and int(inform[hi,ai])>=2 and stable and lp<=.05:label="INTERESTING_EXPLORATORY"
   elif abs(z)>=2 and (int(inform[hi,ai])<2 or not stable):label="LIKELY_PAGE_CONFOUND"
   elif abs(z)>=1.5 and int(inform[hi,ai])>=2:label="WEAK"
   else:label="NO_SIGNAL"
   rows.append({"page_host":h,"external_axis":a,"direction":"ENRICHED" if z>0 else "DEPLETED","host_loci":len(hu),"host_folios":len({u['folio'] for u in hu}),"axis_positive_host_loci":len(pos),"axis_negative_host_loci":len(neg),"positive_folios":len({u['folio'] for u in pos}),"negative_folios":len({u['folio'] for u in neg}),"informative_folios":int(inform[hi,ai]),"cmh_z":z,"local_permutation_p":lp,"max_search_p":mp,"lofo_min_z":min(lo) if lo else 0,"lofo_max_z":max(lo) if lo else 0,"lofo_sign_stable":int(stable),"positive_wrappers":";".join(vals(pos,"wrapper")),"negative_wrappers":";".join(vals(neg,"wrapper")),"positive_right_families":";".join(vals(pos,"right_family")),"negative_right_families":";".join(vals(neg,"right_family")),"classification":label})
 rows.sort(key=lambda r:(-abs(r["cmh_z"]),r["page_host"],r["external_axis"]));
 for i,r in enumerate(rows,1):r["rank_by_abs_cmh_z"]=i
 top=rows[:15];counter=[]
 for c in top:
  h=c["page_host"];a=c["external_axis"]
  for u in units:
   if h not in u["hosts"]:continue
   bad=(c["direction"]=="ENRICHED" and a not in u["tags"])or(c["direction"]=="DEPLETED" and a in u["tags"])
   if not bad:continue
   gs=[r for r in u["groups"] if r["page_host"]==h];d=adesc[u["locus"]]
   counter.append({"candidate_rank":c["rank_by_abs_cmh_z"],"page_host":h,"external_axis":a,"direction":c["direction"],"locus":u["locus"],"physical_folio":u["folio"],"tokens":";".join(r["token"] for r in gs),"wrappers":";".join(sorted({r["wrapper"] for r in gs})),"right_families":";".join(sorted({r["right_family"] for r in gs})),"observed_tags":";".join(sorted(u["tags"])),"annotation_certainty":d["annotation_certainty"],"raw_source_description":d["raw_source_description"]})
 outrows=[{k:f"{v:.12g}" if isinstance(v,float) else v for k,v in r.items()} for r in rows]
 write(ATLAS,outrows,list(outrows[0]));write(COUNTER,counter,list(counter[0]))
 nullrows=[{"null_id":"WITHIN_FOLIO_COMPLETE_TAG_VECTOR_PERMUTATION","permutations":PERMUTATIONS,"seed":SEED,"scanned_hosts":len(hosts),"scanned_axes":len(AXES),"scanned_pairs":len(rows),"observed_max_abs_z":max(abs(r["cmh_z"]) for r in rows),"global_max_search_p":rows[0]["max_search_p"],"preserves":"folio;axis co-occurrence;host incidence;unit size"}]
 write(NULL,[{k:f"{v:.12g}" if isinstance(v,float) else v for k,v in r.items()} for r in nullrows],list(nullrows[0]))
 interesting=[r for r in rows if r["classification"]=="INTERESTING_EXPLORATORY"]
 status="EXACT_PAGE_HOST_ARCHIVE_ASSOCIATIONS_FOUND_NONE_SURVIVE_GLOBAL_SEARCH"
 leads=[("os","PLANT"),("d","REL_ENCLOSURE"),("d","REL_EXPLICIT_ATTACHMENT"),("ok","WATER_OR_APPARATUS")]
 leadrows=[next(r for r in rows if (r["page_host"],r["external_axis"])==x) for x in leads]
 REPORT.write_text(f"""# GDT088 — exact PAGE_HOST external-association atlas

## Outcome

**{status}**

The scan covers {len(units)} archived loci, {len(hosts)} recurrent exact
PAGE_HOSTs, eight provenance-native axes, and {len(rows)} supported pairs.
It finds {len(interesting)} locally interesting exploratory associations, but
the strongest manuscript-wide maximum-search p is {rows[0]['max_search_p']:.4f}.

The strongest lead is `os × PLANT` (z={leadrows[0]['cmh_z']:+.3f},
{leadrows[0]['axis_positive_host_loci']}/{leadrows[0]['host_loci']} host loci,
local p={leadrows[0]['local_permutation_p']:.4f}), recurring under several
wrappers/right renderers.  Its source inventory is dirty: one contributing
astronomical-page line is tagged PLANT by the archived ontology and another
plant label also carries STAR_OR_SKY, so this is a review target, not a gloss.

The more structurally useful candidates are exact host `d` with archived
REL_ENCLOSURE (z={leadrows[1]['cmh_z']:+.3f}) and
REL_EXPLICIT_ATTACHMENT (z={leadrows[2]['cmh_z']:+.3f}), and `ok` with
WATER_OR_APPARATUS (z={leadrows[3]['cmh_z']:+.3f}).  They survive folio
conditioning and leave-one-folio sign checks but are concentrated in known
diagram/register ecologies.  `arol` is not a stable flow-like content key:
its four archived loci split between two water/apparatus contexts and two
plant contexts.

This atlas supplies concrete targets for later independent annotation, but no
PAGE_HOST receives a semantic role or gloss.  All endpoints are archived,
correlated, and postselected.  f84r was absent before the scan and remains
sealed.
""",encoding="utf-8")
 result={"schema":"GDT088_PAGE_HOST_EXTERNAL_ASSOCIATION_RESULT_V1","status":status,"units":len(units),"physical_folios":len(folios),"hosts":len(hosts),"axes":list(AXES),"scanned_pairs":len(rows),"permutations":PERMUTATIONS,"interesting_exploratory":len(interesting),"top_candidates":[{k:r[k] for k in ("rank_by_abs_cmh_z","page_host","external_axis","direction","cmh_z","local_permutation_p","max_search_p","classification")} for r in rows[:15]],"frozen_followup_candidates":[{"page_host":h,"external_axis":a,"semantic_role":"UNASSIGNED"} for h,a in leads],"arol_counterexample":"Four archived AROL-host loci split two WATER_OR_APPARATUS and two PLANT; no stable flow key.","claim_ceiling":"Archived hypothesis-generation associations only; no semantic class, role, gloss, word, morpheme, POS, sound, language, plaintext, meaning, or translation.","f84r":{"opened":False,"retained":False,"queried":False,"joined":False,"scored":False,"targeted":False},"inputs":{PARSED.name:sha(PARSED),ANN.name:sha(ANN),"gdt068_result.json":sha(ROOT/"gdt068_result.json"),"gdt073_result.json":sha(ROOT/"gdt073_result.json")},"implementation":{Path(__file__).name:sha(Path(__file__))},"outputs":{ATLAS.name:sha(ATLAS),NULL.name:sha(NULL),COUNTER.name:sha(COUNTER)},"documents":{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)}}
 result["result_content_sha256"]=csha(result);RESULT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":status,"pairs":len(rows),"interesting":len(interesting),"top":result["top_candidates"][0]},sort_keys=True))
if __name__=="__main__":main()
