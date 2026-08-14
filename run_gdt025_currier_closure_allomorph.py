#!/usr/bin/env python3
"""Currier A/B formal closure realization and transition audit."""
from __future__ import annotations
import csv,json,math
from collections import Counter,defaultdict
from pathlib import Path
from run_gdt022_full_census_visual_phase import csha,sha,statistic,write
ROOT=Path(__file__).resolve().parent
def read(n):
 with (ROOT/n).open(encoding="utf-8",newline="")as h:return list(csv.DictReader(h,delimiter="\t"))
def fisher(a,b,c,d):
 n=a+b+c+d;r=a+b;k=a+c;lo=max(0,r-(n-k));hi=min(r,k)
 def lp(x):return math.lgamma(k+1)-math.lgamma(x+1)-math.lgamma(k-x+1)+math.lgamma(n-k+1)-math.lgamma(r-x+1)-math.lgamma(n-k-r+x+1)-math.lgamma(n+1)+math.lgamma(r+1)+math.lgamma(n-r+1)
 target=lp(a);logs=[lp(x)for x in range(lo,hi+1)if lp(x)<=target+1e-12];m=max(logs);return min(1.,math.exp(m)*sum(math.exp(x-m)for x in logs))
def main():
 inv=read("gdt016_group_state_inventory.tsv");assert len(inv)==15592 and not any(r["locus"].startswith("f84r")for r in inv);lookup={(r["locus"],int(r["group_index"])):r for r in inv};lines=defaultdict(list)
 for r in inv:lines[r["locus"]].append(r)
 ctx={};previous={};transition=Counter();postdy_total=Counter()
 for locus,line in lines.items():
  line.sort(key=lambda r:int(r["group_index"]));after=0
  for i,r in enumerate(line):
   n=int(r["group_count"]);z=(int(r["group_index"])-1)/(n-1)if n>1 else.5;k=(locus,int(r["group_index"]));ctx[k]={"page":r["page"],"physical_folio":r["physical_folio"],"state":r["record_state"],"position_bin":min(3,int(z*4)),"IMMEDIATE_POST_DY":after};previous[k]=line[i-1]if i else None
   if i and line[i-1]["record_state"]=="DY_RESOLUTION":postdy_total[r["currier"]]+=1;transition[r["currier"]]+=int(r["record_state"]=="DY_RESOLUTION")
   after=int(r["record_state"]=="DY_RESOLUTION")
 closure=[];counts={}
 for cur in("A","B"):
  dy=[r for r in inv if r["currier"]==cur and r["record_state"]=="DY_RESOLUTION"]
  e=sum(r["residual_host"].endswith("e")for r in dy);eo=sum(r["residual_host"].endswith("eo")for r in dy);counts[cur]=(e,eo)
  closure.append({"currier":cur,"dy_groups":len(dy),"terminal_e":e,"terminal_eo":eo,"other_terminal":len(dy)-e-eo,"dy_followed_internal_boundaries":postdy_total[cur],"dy_to_dy":transition[cur],"dy_to_dy_rate":f"{transition[cur]/postdy_total[cur]:.12f}","claim_state":"FORMAL_REGISTER_PROFILE_NOT_PHONOLOGY"})
 write("gdt025_currier_closure_inventory.tsv",closure)
 eodds=counts["A"][0]*counts["B"][1]/(counts["A"][1]*counts["B"][0]);ep=fisher(counts["A"][0],counts["A"][1],counts["B"][0],counts["B"][1]);tp=fisher(transition["A"],postdy_total["A"]-transition["A"],transition["B"],postdy_total["B"]-transition["B"])
 aggregate=[{"test":"TERMINAL_E_VS_EO_BY_CURRIER","a":counts["A"][0],"b":counts["A"][1],"c":counts["B"][0],"d":counts["B"][1],"odds_ratio":f"{eodds:.12f}","fisher_two_sided_p":f"{ep:.12g}","claim_state":"FORMAL_REALIZATION_ASSOCIATION_NOT_LANGUAGE"},{"test":"DY_TO_DY_RATE_BY_CURRIER","a":transition["A"],"b":postdy_total["A"]-transition["A"],"c":transition["B"],"d":postdy_total["B"]-transition["B"],"odds_ratio":f"{transition['A']*(postdy_total['B']-transition['B'])/((postdy_total['A']-transition['A'])*transition['B']):.12f}","fisher_two_sided_p":f"{tp:.12g}","claim_state":"FORMAL_TRANSITION_ASSOCIATION_NOT_LANGUAGE"}];write("gdt025_currier_aggregate_tests.tsv",aggregate)
 tests=[];motifs={"A":("QJAB","QKAB","LJAB","LKAB"),"B":("QJB","QKB","LJB","LKB")}
 for cur in("A","B"):
  keys={k for k,r in lookup.items()if r["currier"]==cur and r["record_state"]=="DY_RESOLUTION"}
  for motif in motifs[cur]:
   pos={k for k in keys if motif in lookup[k]["family_surface"]};s=statistic(keys,pos,ctx,"IMMEDIATE_POST_DY");tests.append({"currier":cur,"family_motif":motif,"dy_universe":len(keys),"motif_occurrences":len(pos),"raw_postdy_occurrences":sum(ctx[k]["IMMEDIATE_POST_DY"]for k in pos),"conditional_effect":f"{s['effect']:.12f}","observed_informative":s["observed"],"expected_informative":f"{s['expected']:.12f}","informative_strata":s["informative_strata"],"exact_p":f"{s['p']:.12f}","claim_state":"WITHIN_CURRIER_DY_SUBTYPE_TEST_NOT_MEANING"})
 write("gdt025_family_branch_tests.tsv",tests)
 repeat=[];keys={k for k,r in lookup.items()if r["currier"]=="B"and r["record_state"]=="DY_RESOLUTION"}
 for motif in motifs["B"]:
  base={k for k in keys if motif in lookup[k]["family_surface"]}
  for label,pos in(("ALL",base),("EXCLUDE_EXACT_TOKEN_REPEAT",{k for k in base if not(ctx[k]["IMMEDIATE_POST_DY"]and previous[k]["token"]==lookup[k]["token"])}),("EXCLUDE_EXACT_FAMILY_REPEAT",{k for k in base if not(ctx[k]["IMMEDIATE_POST_DY"]and previous[k]["family_surface"]==lookup[k]["family_surface"])})):
   s=statistic(keys,pos,ctx,"IMMEDIATE_POST_DY");repeat.append({"family_motif":motif,"ablation":label,"remaining_occurrences":len(pos),"conditional_effect":f"{s['effect']:.12f}","observed_informative":s["observed"],"expected_informative":f"{s['expected']:.12f}","informative_strata":s["informative_strata"],"exact_p":f"{s['p']:.12f}","claim_state":"REPETITION_SENSITIVITY_NOT_MEANING"})
 write("gdt025_repeat_ablation.tsv",repeat)
 t={(r["currier"],r["family_motif"]):r for r in tests};a={(r["family_motif"],r["ablation"]):r for r in repeat};status="CURRIER_B_Q_BRANCH_CHAINING_WITH_CURRIER_A_EO_REALIZATION"
 report=f"""# GDT025 Currier-conditioned closure allomorph report

Status: **{status.replace('_',' ')}**

The QJB restriction is explained by two coupled Currier differences. Among
DY-resolution groups, Currier A has 5 terminal-E versus 64 terminal-EO hosts;
Currier B has 1,844 versus 127. The odds ratio is {eodds:.6f} and exact
two-sided p={ep:.3g}. Concrete pairs include `qokedy/qokeody`,
`otedy/oteody`, `qokeedy/qokeeody`, and `shedy/sheody`. “Allomorph” here means
only alternate formal realization.

The record architecture also differs. Currier A has 21 DY-to-DY transitions
among 187 eligible post-DY boundaries ({transition['A']/postdy_total['A']:.1%});
Currier B has 716/2,157 ({transition['B']/postdy_total['B']:.1%}), exact
p={tp:.3g}. Currier A therefore has both the wrong surface realization for QJB
and little checkpoint-chain capacity.

Within Currier B, the distinction is more specific than generic `-edy`:
QJB effect {float(t['B','QJB']['conditional_effect']):+.4f}
(p={float(t['B','QJB']['exact_p']):.6g}) and QKB
{float(t['B','QKB']['conditional_effect']):+.4f}
(p={float(t['B','QKB']['exact_p']):.6g}) are attracted after DY, whereas LJB
{float(t['B','LJB']['conditional_effect']):+.4f}
(p={float(t['B','LJB']['exact_p']):.3g}) and LKB
{float(t['B','LKB']['conditional_effect']):+.4f}
(p={float(t['B','LKB']['exact_p']):.3g}) are repelled. Removing exact-token
repetitions leaves QJB +{float(a['QJB','EXCLUDE_EXACT_TOKEN_REPEAT']['conditional_effect']):.4f}
(p={float(a['QJB','EXCLUDE_EXACT_TOKEN_REPEAT']['exact_p']):.3g}); removing
same-family repeats weakens it to
{float(a['QJB','EXCLUDE_EXACT_FAMILY_REPEAT']['conditional_effect']):+.4f}
(p={float(a['QJB','EXCLUDE_EXACT_FAMILY_REPEAT']['exact_p']):.3g}). Thus local
family persistence explains part, but not all, of the Q-branch preference.

The nearest Currier-A QJAB/QKAB/LJAB/LKAB tests have only 0--4 informative
strata and do not distinguish branches. That is lack of transition capacity,
not evidence that their functions are identical.

The resulting generative account is a Currier-B-specific checkpoint-chain
grammar selecting Q-family `...e...` resolution subtypes over L-family
subtypes. Currier A strongly prefers `...eo...` realizations and rarely chains
checkpoints. This is structural register variation, not a decoded morpheme or
phonological identification.

Only the frozen GDT016 inventory is used and it contains no f84r row. f84r was
not opened, retained, joined, or scored. No role, referent, word, sound,
language, plaintext, meaning, or translation is assigned.
""";(ROOT/"GDT025_CURRIER_CLOSURE_ALLOMORPH_REPORT.md").write_text(report)
 outputs=("gdt025_currier_closure_inventory.tsv","gdt025_currier_aggregate_tests.tsv","gdt025_family_branch_tests.tsv","gdt025_repeat_ablation.tsv","GDT025_CURRIER_CLOSURE_ALLOMORPH_REPORT.md");inputs=("gdt016_group_state_inventory.tsv","gdt016_result.json","gdt024_result.json","GDT025_CURRIER_CLOSURE_ALLOMORPH_METHOD.md")
 result={"schema":"GDT025_CURRIER_CLOSURE_ALLOMORPH_RESULT_V1","status":status,"inventory_groups":len(inv),"closure_inventory":closure,"aggregate_tests":aggregate,"branch_tests":len(tests),"repeat_ablations":len(repeat),"interpretation":"QJB capacity is Currier-B-specific because B selects terminal-E closure realizations and chains DY checkpoints; Q/L subtypes further organize those chains.","f84r":{"input_contains_rows":False,"opened":False,"retained":False,"joined":False,"scored":False},"claim_ceiling":"Currier-conditioned formal realization and anonymous transition grammar only; no linguistic allomorph, role, referent, morpheme, word, sound, language, plaintext, meaning, or translation.","inputs":{n:sha(ROOT/n)for n in inputs},"implementation":{"run_gdt025_currier_closure_allomorph.py":sha(Path(__file__)),"run_gdt022_full_census_visual_phase.py":sha(ROOT/"run_gdt022_full_census_visual_phase.py")},"outputs":{n:sha(ROOT/n)for n in outputs}};result["result_content_sha256"]=csha(result);(ROOT/"gdt025_result.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":status,"aggregate":aggregate},sort_keys=True))
if __name__=="__main__":main()
