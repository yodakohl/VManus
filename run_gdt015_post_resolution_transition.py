#!/usr/bin/env python3
"""Test adjacent q/DY states around frozen OT-versus-bare cores."""
from __future__ import annotations
import json,math
from collections import defaultdict
from fractions import Fraction
from pathlib import Path
from run_gdt012_core_semantic_atlas import ROOT,canonical_sha,sha,write_tsv
from run_gdt013_latent_role_propagation import all_strict_groups
PAIRS=(("ar","otar"),("al","otal"),("ol","otol"));OUTCOMES=("previous_dy","next_dy","previous_q","next_q")
def hp(n,k,m):
 d=math.comb(n,m);return{x:Fraction(math.comb(k,x)*math.comb(n-k,m-x),d)for x in range(max(0,m-(n-k)),min(m,k)+1)}
def exact(parts):
 dist={0:Fraction(1)};obs=0;exp=Fraction();num=den=0.
 for values in parts:
  n=len(values);m=sum(a for a,y in values);k=sum(y for a,y in values)
  if not(0<m<n and 0<k<n):continue
  x=sum(a and y for a,y in values);w=m*(n-m)/n;num+=w*(x/m-(k-x)/(n-m));den+=w;obs+=x;exp+=Fraction(m*k,n)
  nxt=defaultdict(Fraction)
  for i,pi in dist.items():
   for j,pj in hp(n,k,m).items():nxt[i+j]+=pi*pj
  dist=nxt
 d=abs(Fraction(obs)-exp);p=sum(v for x,v in dist.items()if abs(Fraction(x)-exp)>=d)if den else Fraction(1)
 return num/den if den else 0.,float(p),obs,float(exp),len([v for v in parts if 0<sum(a for a,y in v)<len(v)and 0<sum(y for a,y in v)<len(v)])
def main():
 rows=[r for r in all_strict_groups()if r["grammar_scope"]=="CONFIRMED_PROSE"];by=defaultdict(list)
 for r in rows:by[r["locus"]].append(r)
 obs=[]
 for line in by.values():
  line.sort(key=lambda r:r["group_index"])
  for i,r in enumerate(line):
   p=(r["group_index"]-1)/(r["group_count"]-1)if r["group_count"]>1 else.5;z=dict(r);z["position_quartile"]=min(3,int(p*4));z["previous_dy"]=int(i>0 and line[i-1]["dy_closure"]);z["next_dy"]=int(i+1<len(line)and line[i+1]["dy_closure"]);z["previous_q"]=int(i>0 and line[i-1]["stripped_prefix"]=="q");z["next_q"]=int(i+1<len(line)and line[i+1]["stripped_prefix"]=="q");z["previous_token"]=line[i-1]["token"]if i else"LINE_START";z["next_token"]=line[i+1]["token"]if i+1<len(line)else"LINE_END";obs.append(z)
 tests=[]
 for a,b in PAIRS:
  for outcome in OUTCOMES:
   strata=defaultdict(list)
   for r in obs:
    if r["residual_host"]in(a,b):strata[(r["page"],r["position_quartile"])].append((r["residual_host"]==b,r[outcome]))
   effect,p,seen,expected,n=exact(list(strata.values()));tests.append({"test":a.upper()+"_TO_"+b.upper()+"__"+outcome.upper(),"scope":"CORE_SPECIFIC","bare_core":a,"ot_form":b,"outcome":outcome,"informative_strata":n,"observed_ot_outcomes":seen,"expected_ot_outcomes":f"{expected:.12f}","conditional_effect":f"{effect:.12f}","exact_p":f"{p:.12f}","adjusted_p_13":f"{min(1.,13*p):.12f}","claim_state":"ADJACENT_FIELD_STATE_NOT_SEMANTICS"})
 # Post-hoc pooled direction, still stratified by core.
 strata=defaultdict(list)
 for a,b in PAIRS:
  for r in obs:
   if r["residual_host"]in(a,b):strata[(a,r["page"],r["position_quartile"])].append((r["residual_host"]==b,r["previous_dy"]))
 effect,p,seen,expected,n=exact(list(strata.values()));tests.append({"test":"POOLED_OT_VS_BARE__PREVIOUS_DY","scope":"POSTHOC_POOLED_CORE_STRATIFIED","bare_core":"AR;AL;OL","ot_form":"OTAR;OTAL;OTOL","outcome":"previous_dy","informative_strata":n,"observed_ot_outcomes":seen,"expected_ot_outcomes":f"{expected:.12f}","conditional_effect":f"{effect:.12f}","exact_p":f"{p:.12f}","adjusted_p_13":f"{min(1.,13*p):.12f}","claim_state":"POSTHOC_ADJACENT_FIELD_STATE_NOT_SEMANTICS"})
 write_tsv(ROOT/"gdt015_adjacency_tests.tsv",tests)
 examples=[]
 for a,b in PAIRS:
  x=[r for r in obs if r["residual_host"]==b and r["previous_dy"]]
  for r in x[:15]:examples.append({"core_pair":a.upper()+"/"+b.upper(),"locus":r["locus"],"page":r["page"],"group_index":r["group_index"],"position_quartile":r["position_quartile"],"previous_token":r["previous_token"],"target_token":r["token"],"target_host":r["residual_host"],"next_token":r["next_token"],"claim_state":"SEQUENCE_EXAMPLE_NOT_DECODED_TEXT"})
 write_tsv(ROOT/"gdt015_sequence_examples.tsv",examples)
 pooled=tests[-1];specific={(r["bare_core"],r["outcome"]):r for r in tests[:-1]}
 status="POST_RESOLUTION_OT_TRANSITION_PROVISIONAL"
 report=f"""# GDT015 post-resolution transition

Status: **{status.replace('_',' ')}**

Across AR, AL, and OL, the OT-framed form is enriched immediately after a
group carrying terminal `DY`.  The core-, page-, and position-quartile-
conditioned pooled effect is {float(pooled['conditional_effect']):+.3f} over
{pooled['informative_strata']} informative strata: {pooled['observed_ot_outcomes']}
observed OT-after-DY cases versus {float(pooled['expected_ot_outcomes']):.3f}
expected (exact p={float(pooled['exact_p']):.8f}, 13-test adjusted
p={float(pooled['adjusted_p_13']):.8f}).  This pooled test is post-hoc and is
labelled accordingly.

The strongest core is AL→OTAL: previous-DY effect
{float(specific[('al','previous_dy')]['conditional_effect']):+.3f}, adjusted
p={float(specific[('al','previous_dy')]['adjusted_p_13']):.6f}.  AR→OTAR has
the same direction but does not survive family correction.  Next-DY and
adjacent-q controls do not form a comparably general pattern.

## Generative update

The best current sequence is:

```text
... HOST + DY       OT + LOCAL-REFERENCE/STATE ...
    resolved field  post-resolution local qualification
```

Thus `DY` is better treated as a state transition/closure and `OT` as a common
post-resolution local frame than as independent lexical suffix and prefix.
For the visually motivated AR core, `OTAR` remains the risky bounded/interior
reference candidate; the prose sequence result supplies a record function,
not the visual meaning itself.

Coarse position quartiles do not remove every record-position confound, and
the pooled test was discovered after the core-specific directions were seen.
No morpheme, sentence boundary, word, POS, sound, language, plaintext, or
translation is confirmed.  f84r was not retained, joined, or scored.
""";(ROOT/"GDT015_POST_RESOLUTION_TRANSITION_REPORT.md").write_text(report)
 outputs=("gdt015_adjacency_tests.tsv","gdt015_sequence_examples.tsv","GDT015_POST_RESOLUTION_TRANSITION_REPORT.md");inputs=("gdt014_result.json","gdt014_core_ladder_profiles.tsv","experiments/semantic_assumptions/results/source_sta_group_alignment.tsv","experiments/semantic_assumptions/results/source_sta_family_consensus_groups.tsv","GDT015_POST_RESOLUTION_TRANSITION_METHOD.md")
 result={"schema":"GDT015_POST_RESOLUTION_TRANSITION_RESULT_V1","status":status,"strict_prose_groups":len(rows),"tests":tests,"examples":len(examples),"f84r":{"retained":False,"joined":False,"scored":False},"claim_ceiling":"Provisional adjacent field-state transition only; no confirmed morpheme, sentence boundary, word, POS, sound, language, plaintext, or translation.","inputs":{x:sha(ROOT/x)for x in inputs},"implementation":{"run_gdt015_post_resolution_transition.py":sha(Path(__file__)),"run_gdt013_latent_role_propagation.py":sha(ROOT/"run_gdt013_latent_role_propagation.py")},"outputs":{x:sha(ROOT/x)for x in outputs}};result["result_content_sha256"]=canonical_sha(result);(ROOT/"gdt015_result.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":status,"pooled":pooled,"core_specific_tests":tests[:-1]},sort_keys=True))
if __name__=="__main__":main()
