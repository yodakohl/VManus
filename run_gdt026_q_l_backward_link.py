#!/usr/bin/env python3
"""Direction and repetition audit for Currier-B Q/L DY subtypes."""
from __future__ import annotations
import csv,json
from collections import Counter,defaultdict
from pathlib import Path
from run_gdt022_full_census_visual_phase import csha,sha,statistic,write
ROOT=Path(__file__).resolve().parent
def read(n):
 with (ROOT/n).open(encoding="utf-8",newline="")as h:return list(csv.DictReader(h,delimiter="\t"))
def branch(r):
 f=r["family_surface"]
 if "QJB"in f or"QKB"in f:return"Q_FAMILY"
 if "LJB"in f or"LKB"in f:return"L_FAMILY"
 return"OTHER"
def main():
 inv=read("gdt016_group_state_inventory.tsv");assert len(inv)==15592 and not any(r["locus"].startswith("f84r")for r in inv);lines=defaultdict(list)
 for r in inv:lines[r["locus"]].append(r)
 lookup={};ctx={};previous={};keys=set();positive=set();phase=Counter()
 for locus,line in lines.items():
  line.sort(key=lambda r:int(r["group_index"]))
  for i,r in enumerate(line):
   b=branch(r)
   if r["currier"]!="B"or r["record_state"]!="DY_RESOLUTION"or b=="OTHER":continue
   n=int(r["group_count"]);z=(int(r["group_index"])-1)/(n-1)if n>1 else.5;k=(locus,int(r["group_index"]));pd=int(i>0 and line[i-1]["record_state"]=="DY_RESOLUTION");nd=int(i+1<len(line)and line[i+1]["record_state"]=="DY_RESOLUTION");p="ISOLATED"if not pd and not nd else"CHAIN_START"if not pd and nd else"CHAIN_END"if pd and not nd else"CHAIN_INTERNAL";phase[b,p]+=1;keys.add(k);lookup[k]=r;previous[k]=line[i-1]if i else None
   if b=="Q_FAMILY":positive.add(k)
   ctx[k]={"page":r["page"],"physical_folio":r["physical_folio"],"state":r["record_state"],"position_bin":min(3,int(z*4)),"PREVIOUS_DY":pd,"NEXT_DY":nd,"LINE_START":int(i==0),"LINE_END":int(i==len(line)-1),"CHAIN_ENTRY":int(not pd and nd)}
 invrows=[]
 for b in("Q_FAMILY","L_FAMILY"):
  invrows.append({"branch":b,"isolated":phase[b,"ISOLATED"],"chain_start":phase[b,"CHAIN_START"],"chain_internal":phase[b,"CHAIN_INTERNAL"],"chain_end":phase[b,"CHAIN_END"],"total":sum(phase[b,p]for p in("ISOLATED","CHAIN_START","CHAIN_INTERNAL","CHAIN_END")),"claim_state":"ANONYMOUS_DY_CHAIN_POSITION_NOT_MEANING"})
 write("gdt026_chain_phase_inventory.tsv",invrows)
 tests=[];outcomes=("PREVIOUS_DY","NEXT_DY","LINE_START","LINE_END","CHAIN_ENTRY")
 for outcome in outcomes:
  s=statistic(keys,positive,ctx,outcome);folios=sorted({ctx[k]["physical_folio"]for k in keys});lo=[statistic(keys,positive,ctx,outcome,f,False)["effect"]for f in folios];tests.append({"test_id":outcome,"universe":len(keys),"q_family":len(positive),"conditional_effect":f"{s['effect']:.12f}","observed_q_outcomes":s["observed"],"expected_q_outcomes":f"{s['expected']:.12f}","informative_strata":s["informative_strata"],"exact_p":f"{s['p']:.12g}","search_adjusted_p_5":f"{min(1.,float(s['p'])*5):.12g}","lofo_folios":len(lo),"lofo_positive_effects":sum(x>0 for x in lo),"lofo_min_effect":f"{min(lo):.12f}","lofo_max_effect":f"{max(lo):.12f}","claim_state":"DIRECTIONAL_FORMAL_STATE_TEST_NOT_MEANING"})
 write("gdt026_direction_tests.tsv",tests)
 ab=[]
 cases=[("ALL",lambda k:True),("EXCLUDE_EXACT_TOKEN_REPEAT",lambda k:not(ctx[k]["PREVIOUS_DY"]and previous[k]["token"]==lookup[k]["token"])),("EXCLUDE_EXACT_FAMILY_REPEAT",lambda k:not(ctx[k]["PREVIOUS_DY"]and previous[k]["family_surface"]==lookup[k]["family_surface"])),("EXCLUDE_IDENTICAL_HOST_REPEAT",lambda k:not(ctx[k]["PREVIOUS_DY"]and previous[k]["residual_host"]==lookup[k]["residual_host"]))]
 for name,keep in cases:
  k2={k for k in keys if keep(k)};p2=positive&k2;s=statistic(k2,p2,ctx,"PREVIOUS_DY");ab.append({"ablation":name,"remaining_groups":len(k2),"q_family_groups":len(p2),"conditional_effect":f"{s['effect']:.12f}","observed_q_previous_dy":s["observed"],"expected_q_previous_dy":f"{s['expected']:.12f}","informative_strata":s["informative_strata"],"exact_p":f"{s['p']:.12g}","claim_state":"REPETITION_CONTROLLED_BACKWARD_LINK_NOT_MEANING"})
 write("gdt026_backward_link_ablations.tsv",ab)
 t={r["test_id"]:r for r in tests};a={r["ablation"]:r for r in ab};status="CURRIER_B_Q_FAMILY_BACKWARD_LINK_STATE_PROVISIONAL"
 report=f"""# GDT026 Currier-B Q/L backward-link report

Status: **{status.replace('_',' ')}**

Q-family and L-family closures differ primarily in what came before, not in
what comes next. Against L-family within the same page, DY state, and position
quartile, Q-family has previous-DY effect
{float(t['PREVIOUS_DY']['conditional_effect']):+.4f}
(exact p={float(t['PREVIOUS_DY']['exact_p']):.3g}; five-test adjusted
p={float(t['PREVIOUS_DY']['search_adjusted_p_5']):.3g}). The direction remains
positive in {t['PREVIOUS_DY']['lofo_positive_effects']}/{t['PREVIOUS_DY']['lofo_folios']}
leave-one-folio deletions. By contrast, next-DY is only
{float(t['NEXT_DY']['conditional_effect']):+.4f} (p={float(t['NEXT_DY']['exact_p']):.3g});
line start, line end, and chain entry are also nonconfirming after adjustment.

The backward effect is not literal copying. Removing exact repeated tokens
leaves {float(a['EXCLUDE_EXACT_TOKEN_REPEAT']['conditional_effect']):+.4f}
(p={float(a['EXCLUDE_EXACT_TOKEN_REPEAT']['exact_p']):.3g}); removing identical
families leaves {float(a['EXCLUDE_EXACT_FAMILY_REPEAT']['conditional_effect']):+.4f}
(p={float(a['EXCLUDE_EXACT_FAMILY_REPEAT']['exact_p']):.3g}); and removing
identical residual hosts leaves
{float(a['EXCLUDE_IDENTICAL_HOST_REPEAT']['conditional_effect']):+.4f}
(p={float(a['EXCLUDE_IDENTICAL_HOST_REPEAT']['exact_p']):.3g}).

The best generative rule is therefore:

```
if previous group closed a field with DY:
    next DY-bearing group preferentially selects QJB/QKB realization
else:
    LJB/LKB remains comparatively available
```

This is a one-bit local history flag. It does not tell us that another field
will follow, and it does not yet say what the field contains. It is compatible
with continuation/agreement-like notation, but those linguistic or semantic
labels are not established.

Only the frozen GDT016 inventory is used and it contains no f84r row. f84r was
not opened, retained, joined, or scored. No role, referent, morpheme, word,
sound, language, plaintext, meaning, or translation is assigned.
""";(ROOT/"GDT026_Q_L_BACKWARD_LINK_REPORT.md").write_text(report)
 outputs=("gdt026_chain_phase_inventory.tsv","gdt026_direction_tests.tsv","gdt026_backward_link_ablations.tsv","GDT026_Q_L_BACKWARD_LINK_REPORT.md");inputs=("gdt016_group_state_inventory.tsv","gdt016_result.json","gdt025_result.json","GDT026_Q_L_BACKWARD_LINK_METHOD.md")
 result={"schema":"GDT026_Q_L_BACKWARD_LINK_RESULT_V1","status":status,"inventory_groups":len(inv),"ql_universe":len(keys),"q_family_groups":len(positive),"phase_inventory":invrows,"direction_tests":len(tests),"ablations":len(ab),"primary":t["PREVIOUS_DY"],"next_control":t["NEXT_DY"],"rule":"Previous DY preferentially selects a QJB/QKB realization among the next Currier-B DY group; it does not materially predict another following DY.","f84r":{"input_contains_rows":False,"opened":False,"retained":False,"joined":False,"scored":False},"claim_ceiling":"One-bit local formal-history dependence only; no role, referent, morpheme, word, syntax, sound, language, plaintext, meaning, or translation.","inputs":{n:sha(ROOT/n)for n in inputs},"implementation":{"run_gdt026_q_l_backward_link.py":sha(Path(__file__)),"run_gdt022_full_census_visual_phase.py":sha(ROOT/"run_gdt022_full_census_visual_phase.py")},"outputs":{n:sha(ROOT/n)for n in outputs}};result["result_content_sha256"]=csha(result);(ROOT/"gdt026_result.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":status,"primary":t['PREVIOUS_DY'],"next":t['NEXT_DY']},sort_keys=True))
if __name__=="__main__":main()
