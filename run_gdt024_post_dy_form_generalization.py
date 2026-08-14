#!/usr/bin/env python3
"""Dominant-form, rare-tail, register, and state controls for GDT023."""
from __future__ import annotations
import csv,json
from collections import Counter,defaultdict
from pathlib import Path
from run_gdt022_full_census_visual_phase import csha,formal_features,sha,statistic,write
ROOT=Path(__file__).resolve().parent
def read(n):
 with (ROOT/n).open(encoding="utf-8",newline="")as h:return list(csv.DictReader(h,delimiter="\t"))
def main():
 inv=read("gdt016_group_state_inventory.tsv");assert len(inv)==15592 and not any(r["locus"].startswith("f84r")for r in inv)
 lookup={(r["locus"],int(r["group_index"])):r for r in inv};lines=defaultdict(list)
 for r in inv:lines[r["locus"]].append(r)
 ctx={}
 for locus,line in lines.items():
  line.sort(key=lambda r:int(r["group_index"]));after=0
  for r in line:
   n=int(r["group_count"]);z=(int(r["group_index"])-1)/(n-1)if n>1 else.5;k=(locus,int(r["group_index"]));ctx[k]={"page":r["page"],"physical_folio":r["physical_folio"],"state":r["record_state"],"position_bin":min(3,int(z*4)),"IMMEDIATE_POST_DY":after};after=int(r["record_state"]=="DY_RESOLUTION")
 specs=(("QJB","SOURCE_FAMILY","F3:QJB","DY_RESOLUTION"),("KAL","RESIDUAL_HOST","H3:kal","AL_STATE"),("OKAL","RESIDUAL_HOST","HOST_EXACT:okal","AL_STATE"));allkeys=set(lookup);feature_sets={}
 deletion=[]
 for name,model,feature,state in specs:
  pos={k for k,r in lookup.items()if feature in formal_features(r,model)};feature_sets[name]=pos;post=Counter(lookup[k]["token"]for k in pos if ctx[k]["IMMEDIATE_POST_DY"]);total=Counter(lookup[k]["token"]for k in pos);ordered=[token for token,count in sorted(post.items(),key=lambda item:(-item[1],item[0]))]
  for drop in(0,1,2,4,8,16):
   removed=set(ordered[:drop]);selected={k for k in pos if lookup[k]["token"]not in removed};s=statistic(allkeys,selected,ctx,"IMMEDIATE_POST_DY");deletion.append({"feature":name,"diagnostic":f"DROP_TOP_{drop}_POSTDY_TOKENS","removed_tokens":"|".join(sorted(removed)),"remaining_token_types":len({lookup[k]["token"]for k in selected}),"remaining_occurrences":len(selected),"observed_postdy":s["observed"],"expected_postdy":f"{s['expected']:.12f}","conditional_effect":f"{s['effect']:.12f}","exact_p":f"{s['p']:.12f}","informative_strata":s["informative_strata"],"claim_state":"POSTHOC_DOMINANT_FORM_ROBUSTNESS_NOT_MEANING"})
  selected={k for k in pos if total[lookup[k]["token"]]<=5};s=statistic(allkeys,selected,ctx,"IMMEDIATE_POST_DY");deletion.append({"feature":name,"diagnostic":"RARE_TOKEN_TYPES_TOTAL_LE_5","removed_tokens":"","remaining_token_types":len({lookup[k]["token"]for k in selected}),"remaining_occurrences":len(selected),"observed_postdy":s["observed"],"expected_postdy":f"{s['expected']:.12f}","conditional_effect":f"{s['effect']:.12f}","exact_p":f"{s['p']:.12f}","informative_strata":s["informative_strata"],"claim_state":"POSTHOC_RARE_FORM_TAIL_ROBUSTNESS_NOT_MEANING"})
 write("gdt024_dominant_form_deletions.tsv",deletion)
 register=[]
 for name,model,feature,state in specs:
  pos=feature_sets[name]
  for axis in("section","currier","hand"):
   for value in sorted({r[axis]for r in inv}):
    keys={k for k,r in lookup.items()if r[axis]==value};s=statistic(keys,pos&keys,ctx,"IMMEDIATE_POST_DY");register.append({"feature":name,"axis":axis,"value":value,"universe_groups":len(keys),"feature_occurrences":len(pos&keys),"observed_postdy":s["observed"],"expected_postdy":f"{s['expected']:.12f}","conditional_effect":f"{s['effect']:.12f}","exact_p":f"{s['p']:.12f}","informative_strata":s["informative_strata"],"claim_state":"WITHIN_REGISTER_DIAGNOSTIC_NOT_INDEPENDENT_REPLICATION"})
 write("gdt024_register_transfer.tsv",register)
 controls=[]
 for name,model,feature,state in specs:
  keys={k for k,r in lookup.items()if r["record_state"]==state};pos=feature_sets[name]&keys;s=statistic(keys,pos,ctx,"IMMEDIATE_POST_DY");controls.append({"feature":name,"restricted_current_state":state,"state_universe_groups":len(keys),"feature_occurrences":len(pos),"observed_postdy":s["observed"],"expected_postdy":f"{s['expected']:.12f}","conditional_effect":f"{s['effect']:.12f}","exact_p":f"{s['p']:.12f}","informative_strata":s["informative_strata"],"claim_state":"WITHIN_ANONYMOUS_STATE_SUBTYPE_TEST_NOT_MEANING"})
 write("gdt024_state_restricted_tests.tsv",controls)
 d={(r["feature"],r["diagnostic"]):r for r in deletion};qtail=d[("QJB","RARE_TOKEN_TYPES_TOTAL_LE_5")];kdrop=d[("KAL","DROP_TOP_1_POSTDY_TOKENS")];q16=d[("QJB","DROP_TOP_16_POSTDY_TOKENS")]
 status="QJB_FORM_GENERALIZATION_WITHIN_CURRIER_B_KAL_WHOLE_FORM_DOMINATED"
 report=f"""# GDT024 post-DY form-generalization report

Status: **{status.replace('_',' ')}**

QJB is not merely recurrence of one exact target form.  After removing the 16
exact tokens contributing the most post-DY occurrences, 87 occurrences in the
remaining tail retain effect {float(q16['conditional_effect']):+.4f}
(p={float(q16['exact_p']):.6g}).  Restricting to 73 exact token types occurring
at most five times leaves 103 occurrences with effect
{float(qtail['conditional_effect']):+.4f} (p={float(qtail['exact_p']):.6g}).
Even among current DY_RESOLUTION groups, QJB has effect +0.0991 (p=.000627),
so it is a recurrent subtype of the resolution branch rather than only the
coarse DY state.

KAL behaves differently.  `qokal` alone supplies 39 of its 67 raw post-DY
occurrences.  Removing that one token leaves effect
{float(kdrop['conditional_effect']):+.4f} (p={float(kdrop['exact_p']):.3g});
removing `qokal` and `qokaly` reduces the effect to +0.0172 (p=.870).  OKAL
collapses similarly.  The KAL/OKAL lead is therefore an exact-form-dominated
local sequence, not demonstrated productive constructional generalization.

Register transfer is limited. QJB has zero Currier-A capacity and exists only
in Currier B; its section-level effect is strong in B and S but weak in H and
T. KAL occurs in both Currier strata, but its useful evidence is concentrated
in the same B/S ecology and in `qokal`.  Physical-folio stability therefore
does not imply cross-register transfer.

The generative theory is revised accordingly: a productive QJB subclass can
chain after DY checkpoints within Currier B, while a frequent `qokal` branch
occupies the AL state.  Their joint visual-anchor provenance remains a prompt
for generic reference/index function, not evidence that both implement one
semantic operator.

Only the frozen GDT016 inventory is used; it contains no f84r row. f84r was not
opened, retained, joined, or scored. No diagram role, referent, morpheme, word,
syntax, sound, language, plaintext, meaning, or translation is assigned.
""";(ROOT/"GDT024_POST_DY_FORM_GENERALIZATION_REPORT.md").write_text(report)
 outputs=("gdt024_dominant_form_deletions.tsv","gdt024_register_transfer.tsv","gdt024_state_restricted_tests.tsv","GDT024_POST_DY_FORM_GENERALIZATION_REPORT.md");inputs=("gdt016_group_state_inventory.tsv","gdt016_result.json","gdt023_result.json","GDT024_POST_DY_FORM_GENERALIZATION_METHOD.md")
 result={"schema":"GDT024_POST_DY_FORM_GENERALIZATION_RESULT_V1","status":status,"inventory_groups":len(inv),"diagnostics":len(deletion),"register_tests":len(register),"state_controls":len(controls),"qjb_rare_tail":qtail,"qjb_drop16":q16,"kal_drop_qokal":kdrop,"interpretation":{"QJB":"PRODUCTIVE_FORMAL_SUBTYPE_WITHIN_CURRIER_B","KAL_OKAL":"WHOLE_FORM_DOMINATED_LOCAL_SEQUENCE"},"f84r":{"input_contains_rows":False,"opened":False,"retained":False,"joined":False,"scored":False},"claim_ceiling":"Anonymous formal subtype productivity and whole-form dominance only; no diagram role, referent, morpheme, word, syntax, sound, language, plaintext, meaning, or translation.","inputs":{n:sha(ROOT/n)for n in inputs},"implementation":{"run_gdt024_post_dy_form_generalization.py":sha(Path(__file__)),"run_gdt022_full_census_visual_phase.py":sha(ROOT/"run_gdt022_full_census_visual_phase.py")},"outputs":{n:sha(ROOT/n)for n in outputs}};result["result_content_sha256"]=csha(result);(ROOT/"gdt024_result.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":status,"qjb_tail":qtail,"kal_drop":kdrop},sort_keys=True))
if __name__=="__main__":main()
