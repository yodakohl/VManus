#!/usr/bin/env python3
"""GDT056: exact source-native A1Q2 insertion positional sensitivity."""
from __future__ import annotations
import csv,hashlib,json,random
from collections import defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT/"gdt016_group_state_inventory.tsv";CONS=ROOT/"experiments/semantic_assumptions/results/source_sta_family_consensus_groups.tsv";METHOD=ROOT/"GDT056_SOURCE_NATIVE_A1Q2_TRANSFER_METHOD.md";REPORT=ROOT/"GDT056_SOURCE_NATIVE_A1Q2_TRANSFER_REPORT.md";PAIRS=ROOT/"gdt056_source_native_a1q2_pairs.tsv";TESTS=ROOT/"gdt056_source_native_a1q2_tests.tsv";RESULT=ROOT/"gdt056_result.json";FEATURES=("normalized_field_index","normalized_within_field_position","after_dy");PERMS=20000
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def read(p):
 with Path(p).open(encoding="utf-8",newline="")as h:return list(csv.DictReader(h,delimiter="\t"))
def write(p,rows,fields):
 with Path(p).open("w",encoding="utf-8",newline="")as h:w=csv.DictWriter(h,fieldnames=fields,delimiter="\t",lineterminator="\n");w.writeheader();w.writerows(rows)
def contexts(source):
 by=defaultdict(list)
 for r in source:by[r["locus"]].append(r)
 out={}
 for locus,line in by.items():
  line.sort(key=lambda r:int(r["group_index"]));n=int(line[0]["group_count"])
  if len(line)!=n or {int(r["group_index"])for r in line}!=set(range(1,n+1)):continue
  fields=[];cur=[]
  for i,r in enumerate(line):
   cur.append((i,r))
   if r["record_state"]=="DY_RESOLUTION":fields.append(cur);cur=[]
  if cur:fields.append(cur)
  for fi,field in enumerate(fields):
   for j,(i,r)in enumerate(field):out[locus,str(i+1)]={"locus":locus,"page":r["page"],"physical_folio":r["physical_folio"],"group_index":i+1,"token":r["token"],"residual_host":r["residual_host"],"normalized_field_index":fi/(len(fields)-1)if len(fields)>1 else.5,"normalized_within_field_position":j/(len(field)-1)if len(field)>1 else.5,"after_dy":int(i>0 and line[i-1]["record_state"]=="DY_RESOLUTION")}
 return out
def parts(rows,feature):
 by=defaultdict(lambda:[[],[]])
 for r in rows:by[r["page"],r["base_skeleton"]][r["q2_present"]].append(float(r[feature]))
 return[(key,a,b)for key,(a,b)in by.items()if a and b]
def effect(z):
 num=den=0.
 for key,a,b in z:w=len(a)*len(b)/(len(a)+len(b));num+=w*(sum(b)/len(b)-sum(a)/len(a));den+=w
 return num/den if den else 0.
def perm(z,obs,seed):
 rng=random.Random(seed);ext=0
 for _ in range(PERMS):
  q=[]
  for key,a,b in z:v=a+b;rng.shuffle(v);q.append((key,v[:len(a)],v[len(a):]))
  ext+=abs(effect(q))>=abs(obs)-1e-15
 return(ext+1)/(PERMS+1)
def main():
 source=read(SOURCE);assert len(source)==15592 and not any(r["locus"].startswith("f84r")for r in source);ctx=contexts(source);rows=[]
 for c in read(CONS):
  if c["locus"].startswith("f84r"):continue
  key=(c["locus"],c["consensus_group_index"])
  if key not in ctx:continue
  codes=[c[x].split()for x in("zl_sta_codes","it_sta_codes","rf_sta_codes")]
  if not(codes[0]==codes[1]==codes[2]):continue
  z=codes[0];sites=[i for i in range(1,len(z))if z[i]=="Q2"and z[i-1]=="A1"]
  if len(sites)>1:continue
  if sites:i=sites[0];base=z[:i]+z[i+1:];present=1
  else:base=z;present=0
  rows.append({**ctx[key],"source_codes":" ".join(z),"base_skeleton":" ".join(base),"q2_present":present})
 tests=[];pair_keys=set()
 for i,f in enumerate(FEATURES):
  z=parts(rows,f);pair_keys|={x[0]for x in z};e=effect(z);tests.append({"feature":f,"exact_page_skeleton_strata":len(z),"base_occurrences":sum(len(x[1])for x in z),"a1q2_occurrences":sum(len(x[2])for x in z),"effect_q2_minus_base":e,"permutation_p":perm(z,e,56001+i)})
 for t in tests:t["bonferroni_3_p"]=min(1.,3*t["permutation_p"])
 paired=[r for r in rows if(r["page"],r["base_skeleton"])in pair_keys];paired.sort(key=lambda r:(r["base_skeleton"],r["page"],r["q2_present"],r["locus"],r["group_index"]));write(PAIRS,[{k:(f"{v:.12g}"if isinstance(v,float)else v)for k,v in r.items()}for r in paired],list(paired[0]));write(TESTS,[{k:(f"{v:.12g}"if isinstance(v,float)else v)for k,v in t.items()}for t in tests],list(tests[0]));field=tests[0];decision="SOURCE_NATIVE_A1Q2_LATER_FIELD_TRANSFER_DIRECTIONAL_LOW_CAPACITY";assert field["effect_q2_minus_base"]>0 and field["permutation_p"]<.05 and field["bonferroni_3_p"]>.05
 report=f"""# GDT056 — source-native A1Q2 transfer

## Outcome

**{decision}**

The exact source-native comparison finds only {field['exact_page_skeleton_strata']}
page×skeleton strata ({field['base_occurrences']} base and
{field['a1q2_occurrences']} A1Q2 occurrences). A1Q2 lies
{field['effect_q2_minus_base']:+.3f} normalized field indices later than its
exact Q2-deleted skeleton (local p {field['permutation_p']:.4f}, three-test
adjusted p {field['bonferroni_3_p']:.3f}). The direction agrees with GDT055,
but exact-skeleton capacity is too small for corrected confirmation.

This rules out the strongest version of an EVA-only artifact: the same later-
field direction appears when the operation is defined as a stable source-
native A1→Q2 insertion across all three readings. It does not independently
prove a Q2 meaning, and it does not make alternate transcriptions separate
samples.

No word, morpheme, POS, sound, language, plaintext, meaning, or translation is
assigned. f84r was skipped before formal parsing and not opened, retained,
queried, joined, or scored.
""";REPORT.write_text(report,encoding="utf-8")
 result={"schema":"GDT056_SOURCE_NATIVE_A1Q2_TRANSFER_RESULT_V1","status":decision,"stable_source_groups":len(rows),"paired_rows":len(paired),"tests":tests,"claim_ceiling":"Directional source-native sensitivity for later-field A1Q2 insertion; no Q2 meaning, word, morpheme, POS, sound, language, plaintext, meaning, or translation.","f84r":{"opened":False,"retained":False,"queried":False,"joined":False,"scored":False},"inputs":{SOURCE.name:sha(SOURCE),str(CONS.relative_to(ROOT)):sha(CONS),"gdt055_result.json":sha(ROOT/"gdt055_result.json")},"implementation":{Path(__file__).name:sha(Path(__file__))},"outputs":{PAIRS.name:sha(PAIRS),TESTS.name:sha(TESTS)},"documents":{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)}};result["result_content_sha256"]=csha(result);RESULT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":decision,"groups":len(rows),"paired":len(paired),"tests":tests},sort_keys=True))
if __name__=="__main__":main()
