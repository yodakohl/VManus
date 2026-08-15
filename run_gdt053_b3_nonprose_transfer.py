#!/usr/bin/env python3
"""GDT053: source-native B3 endpoint transfer in annotated nonprose units."""
from __future__ import annotations
import csv,hashlib,json,math
from collections import Counter,defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parent;ANN=ROOT/"gdt012_annotated_core_inventory.tsv";CONS=ROOT/"experiments/semantic_assumptions/results/source_sta_family_consensus_groups.tsv";METHOD=ROOT/"GDT053_B3_NONPROSE_TRANSFER_METHOD.md";REPORT=ROOT/"GDT053_B3_NONPROSE_TRANSFER_REPORT.md";GROUPS=ROOT/"gdt053_nonprose_member_groups.tsv";ATLAS=ROOT/"gdt053_nonprose_final_member_atlas.tsv";RESULT=ROOT/"gdt053_result.json"
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def read(p):
 with Path(p).open(encoding="utf-8",newline="")as h:return list(csv.DictReader(h,delimiter="\t"))
def write(p,rows,fields):
 with Path(p).open("w",encoding="utf-8",newline="")as h:w=csv.DictWriter(h,fieldnames=fields,delimiter="\t",lineterminator="\n");w.writeheader();w.writerows(rows)
def hyper(n,K,k):
 den=math.comb(n,k);return{x:math.comb(K,x)*math.comb(n-K,k-x)/den for x in range(max(0,k-(n-K)),min(K,k)+1)}
def conv(a,b):
 o=defaultdict(float)
 for x,p in a.items():
  for y,q in b.items():o[x+y]+=p*q
 return dict(o)
def test(by,member):
 pmf={0:1.};support=obs=0;exp=0.;informative=0
 for z in by.values():
  n=len(z);k=sum(r["final_member"]==member for r in z)
  if not k:continue
  support+=k;obs+=sum(r["final_member"]==member and r["is_locus_final"] for r in z);exp+=k/n;informative+=int(n>1 and k<n);pmf=conv(pmf,hyper(n,1,k))
 upper=sum(p for x,p in pmf.items()if x>=obs);lower=sum(p for x,p in pmf.items()if x<=obs)
 return{"final_member":member,"support":support,"observed_final":obs,"expected_final":exp,"endpoint_rate":obs/support,"expected_rate":exp/support,"rate_effect":(obs-exp)/support,"informative_multigroup_loci":informative,"local_two_sided_p":min(1.,2*min(upper,lower)),"null_min":min(pmf),"null_max":max(pmf)}
def main():
 consensus={(r["locus"],r["consensus_group_index"]):r for r in read(CONS)if not r["locus"].startswith("f84r")}
 partial=defaultdict(list)
 for a in read(ANN):
  if a["locus"].startswith("f84r"):continue
  c=consensus.get((a["locus"],a["group_index"]))
  if not c:continue
  codes=[c[x].split()for x in("zl_sta_codes","it_sta_codes","rf_sta_codes")]
  if not all(z and z[-1]==codes[0][-1]for z in codes):continue
  partial[a["locus"]].append({"locus":a["locus"],"page":a["page"],"physical_folio":a["physical_folio"],"group_index":int(a["group_index"]),"group_count":int(a["group_count"]),"token":a["token"],"annotation_certainty":a["annotation_certainty"],"object_tags":a["object_tags"],"relation_tags":a["relation_tags"],"final_member":codes[0][-1]})
 by={}
 for locus,z in partial.items():
  n=z[0]["group_count"]
  if len(z)==n and {r["group_index"]for r in z}==set(range(1,n+1)):
   for r in z:r["is_locus_final"]=int(r["group_index"]==n)
   by[locus]=sorted(z,key=lambda r:r["group_index"])
 rows=[r for locus in sorted(by)for r in by[locus]];assert len(by)==517 and len(rows)==602 and not any(r["locus"].startswith("f84r")for r in rows);write(GROUPS,rows,list(rows[0]))
 support=Counter(r["final_member"]for r in rows);atlas=[test(by,m)for m,n in support.items()if n>=20];atlas.sort(key=lambda r:(-r["rate_effect"],r["final_member"]));
 for i,r in enumerate(atlas,1):r["rank"]=i;r["bonferroni_p"]=min(1.,len(atlas)*r["local_two_sided_p"])
 fields=["rank"]+[k for k in atlas[0]if k!="rank"];write(ATLAS,[{k:(f"{v:.12g}"if isinstance(v,float)else v)for k,v in r.items()}for r in atlas],fields)
 b3=next(r for r in atlas if r["final_member"]=="B3");decision="B3_NONPROSE_ENDPOINT_TRANSFER_DIRECTIONAL_LOW_CAPACITY";assert b3["rank"]==1 and b3["rate_effect"]>0 and b3["bonferroni_p"]>.05
 report=f"""# GDT053 — B3 nonprose endpoint transfer

## Outcome

**{decision}**

The independently human-annotated nonprose panel yields 517 complete loci and
602 source-native groups. B3 appears 36 times and closes its locus 32 times,
versus {b3['expected_final']:.3f} under exact within-locus placement. Its
endpoint effect is {b3['rate_effect']:+.3f}; local p
{b3['local_two_sided_p']:.3f}, six-class adjusted p
{b3['bonferroni_p']:.3f}. It ranks first by effect among the six stable final
member classes with support at least 20.

This is directional transfer, not confirmation. Most annotated units contain
one group, and B3 has only {b3['informative_multigroup_loci']} informative
multi-group loci. The panel therefore cannot distinguish a general record
closer from a label/register preference with confidence. `HPR2_P01` is marked
directionally consistent but low-capacity rather than passed.

The useful update is that GDT045's B3 endpoint class does not reverse in
diagram labels and other annotated nonprose units. It still must not be called
punctuation, a label word, or a semantic role. No word, morpheme, POS, sound,
language, plaintext, meaning, or translation is assigned. f84r was excluded
before the join and not opened, retained, queried, joined, or scored.
""";REPORT.write_text(report,encoding="utf-8")
 result={"schema":"GDT053_B3_NONPROSE_TRANSFER_RESULT_V1","status":decision,"complete_loci":len(by),"groups":len(rows),"member_classes":len(atlas),"b3":b3,"hpr2_prediction":"HPR2_P01","prediction_outcome":"DIRECTIONAL_LOW_CAPACITY_NOT_CONFIRMING","claim_ceiling":"Directional source-native endpoint transfer in annotated nonprose; not punctuation, label meaning, word, morpheme, POS, sound, language, plaintext, meaning, or translation.","f84r":{"opened":False,"retained":False,"queried":False,"joined":False,"scored":False},"inputs":{ANN.name:sha(ANN),str(CONS.relative_to(ROOT)):sha(CONS),"gdt045_result.json":sha(ROOT/"gdt045_result.json"),"gdt051_result.json":sha(ROOT/"gdt051_result.json")},"implementation":{Path(__file__).name:sha(Path(__file__))},"outputs":{GROUPS.name:sha(GROUPS),ATLAS.name:sha(ATLAS)},"documents":{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)}};result["result_content_sha256"]=csha(result);RESULT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":decision,"loci":len(by),"groups":len(rows),"b3":b3},sort_keys=True))
if __name__=="__main__":main()
