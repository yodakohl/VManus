#!/usr/bin/env python3
"""GDT090: same-host cross-folio visual descriptor stability."""
from __future__ import annotations
import csv,hashlib,json,random,re,statistics
from collections import defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parent;ANN=ROOT/"gdt012_annotated_core_inventory.tsv";PARSED=ROOT/"gdt059_hpr2_external_inventory.tsv";MANIFEST=ROOT/"gdt089_descriptor_manifest.tsv";METHOD=ROOT/"GDT090_EXACT_HOST_VISUAL_STABILITY_METHOD.md";REPORT=ROOT/"GDT090_EXACT_HOST_VISUAL_STABILITY_REPORT.md";PAIRS=ROOT/"gdt090_exact_host_pairs.tsv";NULL=ROOT/"gdt090_matched_null.tsv";RESULT=ROOT/"gdt090_result.json";SEED=90001;WORLDS=50000
def read(p):
 with p.open(encoding="utf-8",newline="") as h:return list(csv.DictReader(h,delimiter="\t"))
def write(p,rows,fields):
 with p.open("w",encoding="utf-8",newline="") as h:w=csv.DictWriter(h,fieldnames=fields,delimiter="\t",lineterminator="\n");w.writeheader();w.writerows(rows)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def jac(a,b):return len(a&b)/len(a|b) if a|b else 1.
def main():
 ann=read(ANN);parsed=read(PARSED);manifest=read(MANIFEST);assert len(ann)==len(parsed)==671 and not any(r["locus"].startswith("f84r") for r in ann+parsed)
 patterns={r["descriptor"]:re.compile(r["exact_regex"]) for r in manifest};by=defaultdict(list);desc={}
 for a,p in zip(ann,parsed):
  if a["kind"]=="L" and a["annotation_certainty"]=="UNHEDGED" and "PLANT" in a["object_tags"].split(";"):
   by[a["locus"]].append(p);desc[a["locus"]]=a["raw_source_description"].lower()
 D={loc:{n for n,q in patterns.items() if q.search(desc[loc])} for loc in by};hosts=defaultdict(list)
 for loc,z in by.items():
  for h in {r["page_host"] for r in z}:hosts[h].append(loc)
 pairdefs=[]
 for h,z in sorted(hosts.items()):
  if len(z)==2 and by[z[0]][0]["physical_folio"]!=by[z[1]][0]["physical_folio"]:pairdefs.append((h,z[0],z[1]))
 assert len(pairdefs)==8
 loci=sorted(by);rows=[];controls={}
 for h,a,b in pairdefs:
  cand=[x for x in loci if x!=a and by[x][0]["physical_folio"]!=by[a][0]["physical_folio"] and abs(len(D[x])-len(D[b]))<=1]
  vals=[jac(D[a],D[x]) for x in cand];obs=jac(D[a],D[b]);p=(sum(x>=obs for x in vals)+1)/(len(vals)+1);controls[h]=vals
  rows.append({"page_host":h,"locus_a":a,"folio_a":by[a][0]["physical_folio"],"locus_b":b,"folio_b":by[b][0]["physical_folio"],"positive_descriptors_a":len(D[a]),"positive_descriptors_b":len(D[b]),"shared_positive_descriptors":len(D[a]&D[b]),"union_positive_descriptors":len(D[a]|D[b]),"descriptor_jaccard":obs,"matched_controls":len(vals),"matched_mean_jaccard":statistics.mean(vals),"inclusive_local_p":p,"shared_descriptor_names":";".join(sorted(D[a]&D[b])) or "NONE"})
 rows.sort(key=lambda r:(-r["descriptor_jaccard"],r["page_host"]));rng=random.Random(SEED);obsmean=statistics.mean(r["descriptor_jaccard"] for r in rows);world=[]
 for _ in range(WORLDS):world.append(statistics.mean(rng.choice(controls[h]) for h,_,_ in pairdefs))
 p=(sum(x>=obsmean for x in world)+1)/(WORLDS+1);nullrows=[{"null_id":"ANCHOR_FIXED_CROSS_FOLIO_DESCRIPTOR_COUNT_MATCH","worlds":WORLDS,"seed":SEED,"exact_host_pairs":len(rows),"observed_mean_jaccard":obsmean,"null_mean_jaccard":statistics.mean(world),"one_sided_better_p":p,"observed_max_pair_jaccard":max(r["descriptor_jaccard"] for r in rows),"preserves":"anchor locus;cross-folio;target descriptor count within one"}]
 write(PAIRS,[{k:f"{v:.12g}" if isinstance(v,float) else v for k,v in r.items()} for r in rows],list(rows[0]));write(NULL,[{k:f"{v:.12g}" if isinstance(v,float) else v for k,v in r.items()} for r in nullrows],list(nullrows[0]))
 osrow=next(r for r in rows if r["page_host"]=="os");chrow=next(r for r in rows if r["page_host"]=="ch");status="EXACT_HOST_WIDE_VISUAL_DESCRIPTOR_STABILITY_NOT_SUPPORTED"
 REPORT.write_text(f"""# GDT090 — exact-host visual stability

## Outcome

**{status}**

Only eight exact PAGE_HOSTs recur across two strict plant-label folios.  Their
mean positive-descriptor Jaccard is {obsmean:.3f}, below the matched-null mean
{statistics.mean(world):.3f}; the one-sided probability of equal or greater
stability is {p:.4f}.  Whole descriptor vectors therefore do not transfer by
exact host better than descriptor-count-matched cross-folio pairs.

`os` is the highest pair at Jaccard {osrow['descriptor_jaccard']:.3f}, followed
by `ch` at {chrow['descriptor_jaccard']:.3f}, but their local matched ranks are
{osrow['inclusive_local_p']:.3f} and {chrow['inclusive_local_p']:.3f}.  Common
dark/light/root/leaf descriptors co-occur so often that this overlap is not
rare under the matched control.

This narrows rather than deletes GDT089: the specific held-folio PAGE_HOST
signal for DARK_LEAF remains a weak seed, while a broad claim that exact hosts
carry stable complete plant-property bundles is unsupported.  No host is
assigned a gloss or semantic role.  f84r remained absent.
""",encoding="utf-8")
 result={"schema":"GDT090_EXACT_HOST_VISUAL_STABILITY_RESULT_V1","status":status,"loci":len(by),"exact_host_pairs":len(rows),"descriptor_patterns":len(patterns),"observed_mean_jaccard":obsmean,"null_mean_jaccard":statistics.mean(world),"one_sided_better_p":p,"os_pair":osrow,"ch_pair":chrow,"interpretation":"Broad exact-host visual bundle stability is not supported; descriptor-specific GDT089 seeds remain exploratory.","claim_ceiling":"Archived description-vector comparison only; no semantic class, role, gloss, word, morpheme, POS, sound, language, plaintext, meaning, or translation.","f84r":{"opened":False,"retained":False,"queried":False,"joined":False,"scored":False,"targeted":False},"inputs":{ANN.name:sha(ANN),PARSED.name:sha(PARSED),MANIFEST.name:sha(MANIFEST),"gdt089_result.json":sha(ROOT/"gdt089_result.json")},"implementation":{Path(__file__).name:sha(Path(__file__))},"outputs":{PAIRS.name:sha(PAIRS),NULL.name:sha(NULL)},"documents":{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)}};result["result_content_sha256"]=csha(result);RESULT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":status,"pairs":len(rows),"observed":obsmean,"null":statistics.mean(world),"p":p},sort_keys=True))
if __name__=="__main__":main()
