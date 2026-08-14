#!/usr/bin/env python3
"""Analyze frozen O/OT/core ladders and record context."""

from __future__ import annotations
import json,random
from collections import Counter,defaultdict
from pathlib import Path
from run_gdt012_core_semantic_atlas import ROOT,canonical_sha,sha,write_tsv
from run_gdt013_latent_role_propagation import all_strict_groups

PERMUTATIONS=20000
VARIANTS=("ar","oar","otar","al","oal","otal","ol","ool","otol")
CONTRASTS=(("ar","oar"),("ar","otar"),("oar","otar"),("al","otal"),("ol","otol"))
def position(r:dict)->float:return (r["group_index"]-1)/(r["group_count"]-1)if r["group_count"]>1 else .5
def strata(rows:list[dict],a:str,b:str)->list[tuple[str,list[float],list[float]]]:
    by=defaultdict(lambda:[[],[]])
    for r in rows:
        if r["residual_host"]==a:by[r["page"]][0].append(position(r))
        if r["residual_host"]==b:by[r["page"]][1].append(position(r))
    return[(p,x,y)for p,(x,y)in sorted(by.items())if x and y]
def effect(parts:list[tuple[str,list[float],list[float]]])->float:
    num=den=0.
    for _,a,b in parts:
        w=len(a)*len(b)/(len(a)+len(b));num+=w*(sum(b)/len(b)-sum(a)/len(a));den+=w
    return num/den if den else 0.
def permutation(parts:list[tuple[str,list[float],list[float]]],observed:float,seed:int)->float:
    rng=random.Random(seed);extreme=0
    for _ in range(PERMUTATIONS):
        shuffled=[]
        for page,a,b in parts:
            values=a+b;rng.shuffle(values);shuffled.append((page,values[:len(a)],values[len(a):]))
        extreme+=abs(effect(shuffled))>=abs(observed)-1e-15
    return(extreme+1)/(PERMUTATIONS+1)


def main()->None:
    corpus=all_strict_groups();rows=[r for r in corpus if r["grammar_scope"]=="CONFIRMED_PROSE"]
    assert len(rows)==15592 and not any(r["locus"].startswith("f84r")for r in rows)
    counts=Counter(r["residual_host"]for r in rows)
    profiles=[];examples=[]
    for variant in VARIANTS:
        x=[r for r in rows if r["residual_host"]==variant];prefix=Counter(r["stripped_prefix"]for r in x)
        profiles.append({"variant":variant.upper(),"core":variant[-2:],"prose_groups":len(x),"physical_folios":len({r["physical_folio"]for r in x}),"pages":len({r["page"]for r in x}),"q_prefix":prefix["q"],"d_prefix":prefix["d"],"s_prefix":prefix["s"],"t_prefix":prefix["t"],"ch_sh_che_prefix":prefix["ch"]+prefix["sh"]+prefix["che"],"no_stripped_prefix":prefix["NONE"],"dy_closure":sum(int(r["dy_closure"])for r in x),"q_plus_dy":sum(r["stripped_prefix"]=="q"and int(r["dy_closure"])for r in x),"line_initial":sum(r["group_index"]==1 for r in x),"line_final":sum(r["group_index"]==r["group_count"]for r in x),"mean_normalized_position":f"{sum(map(position,x))/len(x):.12f}"if x else"0","sections":";".join(f"{k}:{v}"for k,v in sorted(Counter(r["section"]for r in x).items())),"currier":";".join(f"{k or 'UNKNOWN'}:{v}"for k,v in sorted(Counter(r["currier"]for r in x).items()))})
        for r in x[:10]:examples.append({"variant":variant.upper(),"locus":r["locus"],"page":r["page"],"group_index":r["group_index"],"group_count":r["group_count"],"token":r["token"],"stripped_prefix":r["stripped_prefix"],"residual_host":r["residual_host"],"dy_closure":r["dy_closure"],"family_surface":r["family_surface"],"normalized_position":f"{position(r):.12f}","claim_state":"FORMAL_CONTEXT_NOT_DECODED_PROSE"})
    write_tsv(ROOT/"gdt014_core_ladder_profiles.tsv",profiles);write_tsv(ROOT/"gdt014_context_examples.tsv",examples)

    tests=[]
    for i,(a,b)in enumerate(CONTRASTS,1):
        parts=strata(rows,a,b);observed=effect(parts);p=permutation(parts,observed,14000+i);positive=sum(sum(y)/len(y)>sum(x)/len(x)for _,x,y in parts);negative=sum(sum(y)/len(y)<sum(x)/len(x)for _,x,y in parts)
        tests.append({"contrast":a.upper()+"_TO_"+b.upper(),"form_a":a,"form_b":b,"shared_pages":len(parts),"a_groups":sum(len(x)for _,x,_ in parts),"b_groups":sum(len(y)for _,_,y in parts),"position_effect_b_minus_a":f"{observed:.12f}","positive_pages":positive,"negative_pages":negative,"ties":len(parts)-positive-negative,"permutations":PERMUTATIONS,"local_p":f"{p:.12f}","adjusted_p_5":f"{min(1.,5*p):.12f}","claim_state":"WITHIN_PAGE_POSITIONAL_FUNCTION_NOT_MEANING"})
    write_tsv(ROOT/"gdt014_position_tests.tsv",tests)

    bases=sorted((h for h in counts if"o"+h in counts and"ot"+h in counts),key=lambda h:(-(counts[h]+counts["o"+h]+counts["ot"+h]),h))
    ladders=[]
    for h in bases:ladders.append({"base_host":h,"base_n":counts[h],"o_host":"o"+h,"o_n":counts["o"+h],"ot_host":"ot"+h,"ot_n":counts["ot"+h],"total_n":counts[h]+counts["o"+h]+counts["ot"+h],"claim_state":"COMPLETE_FORMAL_LADDER_NOT_MORPHOLOGY"})
    write_tsv(ROOT/"gdt014_complete_ladders.tsv",ladders)
    pmap={r["contrast"]:r for r in tests};vmap={r["variant"]:r for r in profiles}
    qbare=int(vmap["AR"]["q_prefix"])+int(vmap["AL"]["q_prefix"]);qot=int(vmap["OTAR"]["q_prefix"])+int(vmap["OTAL"]["q_prefix"])
    status="LOCAL_REFERENCE_STATE_COMPILER_PROVISIONAL"
    report=f"""# GDT014 local-reference microgrammar

Status: **{status.replace('_',' ')}**

## A productive local-frame ladder

The strict prose corpus contains {len(ladders)} complete `H / oH / otH`
type ladders.  The visually motivated cores are not isolated accidents:

- `AR / OAR / OTAR`: {vmap['AR']['prose_groups']} / {vmap['OAR']['prose_groups']} / {vmap['OTAR']['prose_groups']} groups;
- `AL / OAL / OTAL`: {vmap['AL']['prose_groups']} / {vmap['OAL']['prose_groups']} / {vmap['OTAL']['prose_groups']} groups;
- `OL / OOL / OTOL`: {vmap['OL']['prose_groups']} / {vmap['OOL']['prose_groups']} / {vmap['OTOL']['prose_groups']} groups.

This does not overturn GDT003: local string statistics can generate such
ladders.  It does supply an explicit compiler for semantic theory generation.

## Record-position constraints

Within 45 shared pages, `OTAR` occurs {float(pmap['AR_TO_OTAR']['position_effect_b_minus_a']):+.3f}
normalized group positions later than `AR` (local permutation
p={float(pmap['AR_TO_OTAR']['local_p']):.5f}, five-test adjusted
p={float(pmap['AR_TO_OTAR']['adjusted_p_5']):.5f}).  `OTAL` is likewise
{float(pmap['AL_TO_OTAL']['position_effect_b_minus_a']):+.3f} later than `AL`
(adjusted p={float(pmap['AL_TO_OTAL']['adjusted_p_5']):.5f}).  `OTOL` has only
a weak {float(pmap['OL_TO_OTOL']['position_effect_b_minus_a']):+.3f} shift.

So `OT` is not a uniform lexical prefix.  The best provisional function is a
**later/local-qualified field state**, especially for AR/AL-like cores.

## Outer-state compatibility

Bare `AR` and `AL` have {qbare} q-prefixed occurrences in this projection;
`OTAR` and `OTAL` have {qot}.  The observed forms therefore support the stack

```text
[entry/carrier] [q outer state] [O/OT local frame] [AR/AL core] [DY state]
```

rather than unrestricted concatenation.  The q result is not independent
semantic evidence: it may be entirely explained by the familiar source
orthotactic preference for `qo`.  q and DY mostly behave as alternative states
inside these exact ladders, consistent with GDT011's rejection of whole-line
q...DY bracketing.

## Provisional meaning update

- `AR`: local referent/association nucleus;
- `AR+O/L` environments: adjacent or associated referent lead;
- `OT+AR`: bounded/interior or locally qualified referent lead;
- `OT+AL`: analogous later qualified state without a visual gloss yet;
- `q`: outer/current field state that prefers an O/OT-framed core;
- `DY`: alternative resolved/terminal field state, not a paired line bracket.

These functions explain visual `ARO/TAR` hints, productive prose ladders, and
record position at once.  They remain an abductive microgrammar, not word
translations.

f84r was not retained, joined, or scored.  No word, morpheme, POS, sound,
language, plaintext, or translation is confirmed.
"""
    (ROOT/"GDT014_LOCAL_REFERENCE_MICROGRAMMAR_REPORT.md").write_text(report)
    outputs=("gdt014_core_ladder_profiles.tsv","gdt014_position_tests.tsv","gdt014_complete_ladders.tsv","gdt014_context_examples.tsv","GDT014_LOCAL_REFERENCE_MICROGRAMMAR_REPORT.md")
    inputs=("gdt013_result.json","gdt013_relational_motif_leads.tsv","experiments/semantic_assumptions/results/source_sta_group_alignment.tsv","experiments/semantic_assumptions/results/source_sta_family_consensus_groups.tsv","GDT014_LOCAL_REFERENCE_MICROGRAMMAR_METHOD.md")
    result={"schema":"GDT014_LOCAL_REFERENCE_MICROGRAMMAR_RESULT_V1","status":status,"strict_prose_groups":len(rows),"complete_ladders":len(ladders),"variants":profiles,"position_tests":tests,"q_on_bare_ar_al":qbare,"q_on_otar_otal":qot,"f84r":{"retained":False,"joined":False,"scored":False},"claim_ceiling":"Provisional local-reference field compiler only; no confirmed word, morpheme, POS, sound, language, plaintext, or translation.","inputs":{x:sha(ROOT/x)for x in inputs},"implementation":{"run_gdt014_local_reference_microgrammar.py":sha(Path(__file__)),"run_gdt013_latent_role_propagation.py":sha(ROOT/"run_gdt013_latent_role_propagation.py")},"outputs":{x:sha(ROOT/x)for x in outputs}}
    result["result_content_sha256"]=canonical_sha(result);(ROOT/"gdt014_result.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":status,"groups":len(rows),"ladders":len(ladders),"tests":tests,"qbare":qbare,"qot":qot},sort_keys=True))
if __name__=="__main__":main()
