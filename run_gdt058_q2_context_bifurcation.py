#!/usr/bin/env python3
"""GDT058: matched source-native Q2 context/record-coordinate test."""
from __future__ import annotations
import csv,hashlib,json,random
from collections import Counter,defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT/"gdt016_group_state_inventory.tsv";CONS=ROOT/"experiments/semantic_assumptions/results/source_sta_family_consensus_groups.tsv";METHOD=ROOT/"GDT058_Q2_CONTEXT_BIFURCATION_METHOD.md";REPORT=ROOT/"GDT058_Q2_CONTEXT_BIFURCATION_REPORT.md";OCC=ROOT/"gdt058_q2_context_inventory.tsv";TESTS=ROOT/"gdt058_q2_context_tests.tsv";RESULT=ROOT/"gdt058_result.json";FEATURES=("normalized_line_position","normalized_field_index","normalized_within_field_position","after_dy");PERMS=20000
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
  if len(line)!=n or{int(r["group_index"])for r in line}!=set(range(1,n+1)):continue
  fields=[];cur=[]
  for i,r in enumerate(line):
   cur.append((i,r))
   if r["record_state"]=="DY_RESOLUTION":fields.append(cur);cur=[]
  if cur:fields.append(cur)
  for fi,field in enumerate(fields):
   for j,(i,r)in enumerate(field):out[locus,str(i+1)]={"locus":locus,"page":r["page"],"physical_folio":r["physical_folio"],"register":r["section"]+"|"+r["currier"],"group_index":i+1,"group_count":n,"token":r["token"],"normalized_line_position":i/(n-1)if n>1 else.5,"normalized_field_index":fi/(len(fields)-1)if len(fields)>1 else.5,"normalized_within_field_position":j/(len(field)-1)if len(field)>1 else.5,"after_dy":int(i>0 and line[i-1]["record_state"]=="DY_RESOLUTION")}
 return out
def matched(rows,mode,feature):
 by=defaultdict(lambda:[[],[]])
 for r in rows:
  if mode=="GROUP_INITIAL_Q2":
   if r["group_initial_q2"]:y=1
   elif not r["contains_q2"]:y=0
   else:continue
  else:
   if r["internal_a1q2"]:y=1
   elif not r["contains_q2"]and r["contains_a1"]:y=0
   else:continue
  by[r["page"],r["source_member_count"],r["terminal_member"]][y].append((float(r[feature]),r["physical_folio"],r["locus"],r["group_index"]))
 return[(k,a,b)for k,(a,b)in by.items()if a and b]
def effect(z):
 num=den=0.
 for key,a,b in z:w=len(a)*len(b)/(len(a)+len(b));num+=w*(sum(x[0]for x in b)/len(b)-sum(x[0]for x in a)/len(a));den+=w
 return num/den if den else 0.
def perm(z,obs,seed):
 rng=random.Random(seed);ext=0
 for _ in range(PERMS):
  q=[]
  for key,a,b in z:v=a+b;rng.shuffle(v);q.append((key,v[:len(a)],v[len(a):]))
  ext+=abs(effect(q))>=abs(obs)-1e-15
 return(ext+1)/(PERMS+1)
def lofo(z):
 folios=sorted({x[1]for key,a,b in z for x in a+b});vals=[]
 for f in folios:
  q=[]
  for key,a,b in z:
   aa=[x for x in a if x[1]!=f];bb=[x for x in b if x[1]!=f]
   if aa and bb:q.append((key,aa,bb))
  if q:vals.append(effect(q))
 return folios,vals
def guarded_rows(ctx):
 out=[]
 with CONS.open(encoding="utf-8",newline="")as h:
  header=h.readline();fields=next(csv.reader([header],delimiter="\t"))
  for raw in h:
   if raw.startswith("f84r."):continue
   vals=next(csv.reader([raw],delimiter="\t"));c=dict(zip(fields,vals));key=(c["locus"],c["consensus_group_index"])
   if key not in ctx:continue
   codes=[c[x].split()for x in("zl_sta_codes","it_sta_codes","rf_sta_codes")]
   if not(codes[0]==codes[1]==codes[2]):continue
   z=codes[0];pred=Counter(z[i-1]for i in range(1,len(z))if z[i]=="Q2")
   out.append({**ctx[key],"source_codes":" ".join(z),"source_member_count":len(z),"terminal_member":z[-1],"group_initial_q2":int(z[0]=="Q2"),"internal_a1q2":int(pred["A1"]>0),"contains_q2":int("Q2"in z),"contains_a1":int("A1"in z),"q2_predecessors":";".join(f"{k}:{v}"for k,v in sorted(pred.items()))or"NONE"})
 return out
def main():
 source=read(SOURCE);assert len(source)==15592 and not any(r["locus"].startswith("f84r")for r in source);ctx=contexts(source);rows=guarded_rows(ctx);assert len(rows)==7974
 relevant=[r for r in rows if r["contains_q2"]];relevant.sort(key=lambda r:(r["physical_folio"],r["locus"],r["group_index"]));fields=list(relevant[0]);write(OCC,[{k:f"{v:.12g}"if isinstance(v,float)else v for k,v in r.items()}for r in relevant],fields)
 tests=[]
 for mi,mode in enumerate(("GROUP_INITIAL_Q2","INTERNAL_A1Q2")):
  for fi,feature in enumerate(FEATURES):
   z=matched(rows,mode,feature);obs=effect(z);folios,lvals=lofo(z);tests.append({"context":mode,"feature":feature,"matched_strata":len(z),"control_groups":sum(len(x[1])for x in z),"target_groups":sum(len(x[2])for x in z),"effect_target_minus_control":obs,"permutation_p":perm(z,obs,58000+mi*10+fi),"physical_folios":len(folios),"lofo_min_effect":min(lvals),"lofo_max_effect":max(lvals)})
 for t in tests:t["bonferroni_8_p"]=min(1.,8*t["permutation_p"])
 write(TESTS,[{k:f"{v:.12g}"if isinstance(v,float)else v for k,v in t.items()}for t in tests],list(tests[0]));get=lambda c,f:next(t for t in tests if t["context"]==c and t["feature"]==f);il=get("GROUP_INITIAL_Q2","normalized_line_position");iff=get("GROUP_INITIAL_Q2","normalized_field_index");af=get("INTERNAL_A1Q2","normalized_field_index");al=get("INTERNAL_A1Q2","normalized_line_position");decision="Q2_HAS_CONTEXT_CONDITIONED_EARLY_INITIAL_VS_LATER_INTERNAL_PLACEMENT"
 assert il["effect_target_minus_control"]<0 and il["bonferroni_8_p"]<.05 and il["lofo_max_effect"]<0 and iff["effect_target_minus_control"]<0 and af["effect_target_minus_control"]>0 and af["bonferroni_8_p"]<.05 and af["lofo_min_effect"]>0
 pred=Counter()
 for r in relevant:
  for x in r["q2_predecessors"].split(";"):
   if x!="NONE":
    k,n=x.split(":");pred[k]+=int(n)
 q2_members=sum(r["source_codes"].split().count("Q2")for r in relevant)
 report=f"""# GDT058 — Q2 source-context coordinate bifurcation

## Outcome

**{decision}**

The stable complete-line panel contains {len(rows):,} groups; {len(relevant):,}
contain {q2_members:,} Q2 members. Group-initial Q2 is matched against Q2-absent groups on page,
source-member count, and terminal member. It lies
{il['effect_target_minus_control']:+.3f} normalized physical-line positions
earlier ({il['matched_strata']} strata, {il['target_groups']} targets,
eight-test adjusted p {il['bonferroni_8_p']:.4g}, leave-folio maximum
{il['lofo_max_effect']:+.3f}) and {iff['effect_target_minus_control']:+.3f}
field indices earlier.

Internal A1→Q2 is compared with Q2-absent A1-containing groups under the same
matching. It lies {af['effect_target_minus_control']:+.3f} normalized field
indices later ({af['matched_strata']} strata, {af['target_groups']} targets,
adjusted p {af['bonferroni_8_p']:.4g}, leave-folio minimum
{af['lofo_min_effect']:+.3f}); its physical-line shift is
{al['effect_target_minus_control']:+.3f}. The opposite directions survive
major page, length, and right-edge controls.

## Generative consequence

Q2 should not be modeled as one invariant display-t operation. A compact
source-native generator conditions it on its local state: group-initial Q2
(display `t` entry) is licensed strongly at the early/line-entry coordinate,
while A1-preceded Q2 (the source pattern behind internal `ot`) is licensed
later between fields. Q2 is distinct from the display-q/Q1 relation. No single
lexical or phonological function is required.

The comparison is post-GDT057 exploratory and matched rather than exact-whole-
skeleton for every group. It establishes a context-conditioned record
coordinate, not an operator meaning, word, morpheme, POS, sound, language,
plaintext, or translation. f84r was skipped before parsing and was not opened,
retained, queried, joined, or scored.
""";REPORT.write_text(report,encoding="utf-8")
 result={"schema":"GDT058_Q2_CONTEXT_BIFURCATION_RESULT_V1","status":decision,"stable_complete_line_groups":len(rows),"q2_groups":len(relevant),"q2_member_occurrences":q2_members,"q2_predecessor_counts":dict(sorted(pred.items())),"tests":tests,"headline":{"group_initial_line_position":il,"group_initial_field_index":iff,"internal_a1q2_field_index":af,"internal_a1q2_line_position":al},"generative_update":"Q2 is context-licensed: group-initial Q2/display-t entry is early/line-entry; A1-preceded Q2 behind internal display-ot is later-field. Q2 is distinct from the display-q/Q1 relation; do not collapse these into one invariant display-t function.","claim_ceiling":"Context-conditioned source-native record coordinate only; no operator meaning, word, morpheme, POS, sound, language, plaintext, meaning, or translation.","f84r":{"opened":False,"parsed":False,"retained":False,"queried":False,"joined":False,"scored":False},"inputs":{SOURCE.name:sha(SOURCE),str(CONS.relative_to(ROOT)):sha(CONS),"gdt055_result.json":sha(ROOT/"gdt055_result.json"),"gdt056_result.json":sha(ROOT/"gdt056_result.json"),"gdt057_result.json":sha(ROOT/"gdt057_result.json")},"implementation":{Path(__file__).name:sha(Path(__file__))},"outputs":{OCC.name:sha(OCC),TESTS.name:sha(TESTS)},"documents":{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)}};result["result_content_sha256"]=csha(result);RESULT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":decision,"groups":len(rows),"q2_groups":len(relevant),"q2_members":q2_members,"tests":tests},sort_keys=True))
if __name__=="__main__":main()
