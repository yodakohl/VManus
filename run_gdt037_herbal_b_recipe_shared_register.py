#!/usr/bin/env python3
"""GDT037: isolate formal constructions shared by Herbal-B and Stars/Recipe-S."""
from __future__ import annotations

import csv, hashlib, json, math
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "gdt016_group_state_inventory.tsv"
CANDIDATES = ROOT / "gdt037_bs_register_candidates.tsv"
CORES = ROOT / "gdt037_core_wrapper_atlas.tsv"
STRUCTURE = ROOT / "gdt037_field_transition_atlas.tsv"
COUNTER = ROOT / "gdt037_counterexamples.tsv"
RESULT = ROOT / "gdt037_result.json"
REPORT = ROOT / "GDT037_HERBAL_B_RECIPE_SHARED_REGISTER_REPORT.md"
METHOD = ROOT / "GDT037_HERBAL_B_RECIPE_SHARED_REGISTER_METHOD.md"

PRIMARY = ("HA", "HB", "SB", "OB")
ALL_STRATA = PRIMARY + ("SA", "OTHER")
TARGET = ("HB", "SB")
MIN_COUNT = 3
MIN_FOLIOS = 2


def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def csha(value): return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()).hexdigest()
def read(path):
    with Path(path).open(encoding="utf-8", newline="") as h: return list(csv.DictReader(h, delimiter="\t"))
def write(path, rows, fields):
    with Path(path).open("w", encoding="utf-8", newline="") as h:
        w=csv.DictWriter(h,fieldnames=fields,delimiter="\t",lineterminator="\n");w.writeheader();w.writerows(rows)


def stratum(row):
    if row["section"]=="H" and row["currier"]=="A": return "HA"
    if row["section"]=="H" and row["currier"]=="B": return "HB"
    if row["section"]=="S" and row["currier"]=="B": return "SB"
    if row["section"]=="S" and row["currier"]=="A": return "SA"
    if row["currier"]=="B": return "OB"
    return "OTHER"


def event(family, value, denominator, row, locus):
    return {"feature_family":family,"feature_value":value,"denominator":denominator,"stratum":stratum(row),
            "folio":row["physical_folio"],"page":row["page"],"hand":row["hand"],"locus":locus,
            "residual_host":row.get("residual_host","") ,"state":row.get("record_state","")}


def build_events(rows):
    lines=defaultdict(list)
    for r in rows:
        assert not r["locus"].startswith("f84r")
        lines[r["locus"]].append(r)
    for line in lines.values():line.sort(key=lambda r:int(r["group_index"]))
    events=[]; denominator=Counter(); core_state=Counter(); core_wrapper=Counter(); core_folios=defaultdict(set)
    for r in rows:
        s=stratum(r);denominator[("GROUP",s)]+=1
        events += [event("CORE",r["residual_host"],"GROUP",r,r["locus"]),
                   event("WRAPPER_CORE",f'{r["stripped_prefix"]}|{r["residual_host"]}',"GROUP",r,r["locus"]),
                   event("RECORD_STATE",r["record_state"],"GROUP",r,r["locus"])]
        core_state[(r["residual_host"],s,r["record_state"])]+=1
        core_wrapper[(r["residual_host"],s,r["stripped_prefix"])]+=1
        core_folios[(r["residual_host"],s)].add(r["physical_folio"])
    for locus,line in lines.items():
        s=stratum(line[0]); fol=line[0]["physical_folio"]
        for left,right in zip(line,line[1:]):
            denominator[("TRANSITION",s)]+=1
            events.append(event("STATE_TRANSITION",f'{left["record_state"]}>{right["record_state"]}',"TRANSITION",left,locus))
            events.append(event("WRAPPER_TRANSITION",f'{left["stripped_prefix"]}>{right["stripped_prefix"]}',"TRANSITION",left,locus))
        fields=[]; current=[]
        for r in line:
            current.append(r)
            if r["record_state"]=="DY_RESOLUTION": fields.append((current,True));current=[]
        if current:fields.append((current,False))
        for field,closed in fields:
            denominator[("FIELD",s)]+=1
            states=[r["record_state"]for r in field]
            exact=">".join(states)+("" if closed else ">OPEN")
            n=len(field);bucket=str(n)if n<=3 else"4PLUS"
            shape=f'{"CLOSED"if closed else"OPEN"}|LEN_{bucket}|{states[0]}>{states[-1]}'
            events.append(event("FIELD_TEMPLATE",exact,"FIELD",field[0],locus))
            events.append(event("FIELD_SHAPE",shape,"FIELD",field[0],locus))
            if closed:events.append(event("CLOSED_FIELD_CLOSER",field[-1]["residual_host"],"FIELD",field[-1],locus))
    return events,denominator,core_state,core_wrapper,core_folios


def rate(count,total):return(count+.5)/(total+1.0)
def lrr(a,b):return math.log2(a/b)


def held_minimum(feature_events, denominator, counts, folios, compare):
    vals=[]
    target_folios=sorted(folios[("HB")]|folios[("SB")])
    by=Counter((e["stratum"],e["folio"])for e in feature_events)
    den_by=Counter((e["stratum"],e["folio"])for e in ALL_DENOM_EVENTS[feature_events[0]["denominator"]])
    for held in target_folios:
        rs={}
        for s in PRIMARY:
            c=counts[s]-by[(s,held)];n=denominator[(feature_events[0]["denominator"],s)]-den_by[(s,held)]
            rs[s]=rate(c,n)
        base="HA"if compare=="A"else"OB"
        vals.append(min(lrr(rs["HB"],rs[base]),lrr(rs["SB"],rs[base])))
    return min(vals)if vals else float("nan")


def classify(row):
    if row["shared_a_enrichment_log2"]>=1 and row["shared_other_b_specificity_log2"]>=.5 and row["lofo_min_a_enrichment_log2"]>0 and row["lofo_min_other_b_specificity_log2"]>0:
        if row["same_hand3_support"]=="YES":return"B_S_REGISTER_CANDIDATE"
        return"B_S_ENRICHED_HAND_CONFOUNDED"
    if row["shared_a_enrichment_log2"]>=1 and row["shared_other_b_specificity_log2"]<=0:return"GENERIC_CURRIER_B_NOT_BS_SPECIFIC"
    if row["shared_a_enrichment_log2"]>=1:return"A_RARE_BS_SHARED_WEAK_SPECIFICITY"
    return"SHARED_NOT_ENRICHED"


def formal_hint(host, core_state):
    counts=Counter();total=0
    for s in TARGET:
        for (h,st,state),n in core_state.items():
            if h==host and st==s:counts[state]+=n;total+=n
    if not total:return"UNRESOLVED"
    state,n=counts.most_common(1)[0];frac=n/total;dy=counts["DY_RESOLUTION"]/total
    if dy>=.67:return"PREDOMINANT_CLOSURE_HOST"
    if frac>=.67:return f"PREDOMINANT_{state}"
    if dy<=.25:return"MIXED_NONCLOSURE_HOST_CANDIDATE"
    return"MIXED_STATE_HOST"


def main():
    global ALL_DENOM_EVENTS
    rows=read(SOURCE);events,denominator,core_state,core_wrapper,core_folios=build_events(rows)
    ALL_DENOM_EVENTS=defaultdict(list)
    # one denominator event per physical unit, reconstructed without feature multiplication
    for r in rows:ALL_DENOM_EVENTS["GROUP"].append(event("_","_","GROUP",r,r["locus"]))
    lines=defaultdict(list)
    for r in rows:lines[r["locus"]].append(r)
    for locus,line in lines.items():
        line.sort(key=lambda r:int(r["group_index"]))
        for left,_ in zip(line,line[1:]):ALL_DENOM_EVENTS["TRANSITION"].append(event("_","_","TRANSITION",left,locus))
        current=[]
        for r in line:
            current.append(r)
            if r["record_state"]=="DY_RESOLUTION":ALL_DENOM_EVENTS["FIELD"].append(event("_","_","FIELD",current[0],locus));current=[]
        if current:ALL_DENOM_EVENTS["FIELD"].append(event("_","_","FIELD",current[0],locus))
    grouped=defaultdict(list)
    for e in events:grouped[(e["feature_family"],e["feature_value"],e["denominator"])].append(e)
    family_eligible=Counter();raw=[]
    for (family,value,denom),es in grouped.items():
        counts=Counter(e["stratum"]for e in es);folios=defaultdict(set);hands=defaultdict(set)
        for e in es:folios[e["stratum"]].add(e["folio"]);hands[e["stratum"]].add(e["hand"])
        if counts["HB"]<MIN_COUNT or counts["SB"]<MIN_COUNT or len(folios["HB"])<MIN_FOLIOS or len(folios["SB"])<MIN_FOLIOS:continue
        family_eligible[family]+=1
        rates={s:rate(counts[s],denominator[(denom,s)])for s in ALL_STRATA}
        ea=min(lrr(rates["HB"],rates["HA"]),lrr(rates["SB"],rates["HA"]))
        eo=min(lrr(rates["HB"],rates["OB"]),lrr(rates["SB"],rates["OB"]))
        balance=abs(lrr(rates["HB"],rates["SB"]));rec=min(len(folios["HB"]),len(folios["SB"]))
        same_h3=sum(1 for e in es if e["stratum"]=="HB"and e["hand"]=="3")>0 and sum(1 for e in es if e["stratum"]=="SB"and e["hand"]=="3")>0
        hb_h3=[e for e in es if e["stratum"]=="HB"and e["hand"]=="3"]
        sb_h3=[e for e in es if e["stratum"]=="SB"and e["hand"]=="3"]
        hb_non3=[e for e in es if e["stratum"]=="HB"and e["hand"]!="3"]
        cross_hand=len(hands["HB"]|hands["SB"])>=2
        rank=min(4,ea)+max(-3,min(3,eo))+math.log2(1+rec)-.5*balance
        raw.append({"feature_family":family,"feature_value":value,"denominator":denom,
                    **{f"{s.lower()}_count":counts[s]for s in ALL_STRATA},
                    **{f"{s.lower()}_folios":len(folios[s])for s in ALL_STRATA},
                    **{f"{s.lower()}_rate_per_1000":rates[s]*1000 for s in ALL_STRATA},
                    "shared_a_enrichment_log2":ea,"shared_other_b_specificity_log2":eo,"hb_sb_abs_log2_rate_difference":balance,
                    "minimum_target_folio_support":rec,"same_hand3_support":"YES"if same_h3 else"NO",
                    "hb_hand3_count":len(hb_h3),"hb_hand3_folios":len({e['folio']for e in hb_h3}),
                    "sb_hand3_count":len(sb_h3),"sb_hand3_folios":len({e['folio']for e in sb_h3}),
                    "hb_nonhand3_count":len(hb_non3),"hb_nonhand3_folios":len({e['folio']for e in hb_non3}),
                    "cross_hand_target_support":"YES"if cross_hand else"NO","sa_cross_currier_sensitivity":"PRESENT"if counts["SA"]else"ABSENT",
                    "lofo_min_a_enrichment_log2":held_minimum(es,denominator,counts,folios,"A"),
                    "lofo_min_other_b_specificity_log2":held_minimum(es,denominator,counts,folios,"OB"),"rank_score":rank,
                    "formal_function_hint":formal_hint(value,core_state)if family=="CORE"else"FORMAL_PATTERN"})
    for r in raw:
        r["family_selector_bits"]=math.log2(family_eligible[r["feature_family"]])if family_eligible[r["feature_family"]]>1 else 0.
        r["classification"]=classify(r)
    raw.sort(key=lambda r:(-r["rank_score"],r["feature_family"],r["feature_value"]))
    for i,r in enumerate(raw,1):r["rank"]=i
    fields=["rank","feature_family","feature_value","denominator"]
    for s in ALL_STRATA:fields +=[f"{s.lower()}_count",f"{s.lower()}_folios",f"{s.lower()}_rate_per_1000"]
    fields +=["shared_a_enrichment_log2","shared_other_b_specificity_log2","hb_sb_abs_log2_rate_difference","minimum_target_folio_support","same_hand3_support","hb_hand3_count","hb_hand3_folios","sb_hand3_count","sb_hand3_folios","hb_nonhand3_count","hb_nonhand3_folios","cross_hand_target_support","sa_cross_currier_sensitivity","lofo_min_a_enrichment_log2","lofo_min_other_b_specificity_log2","family_selector_bits","rank_score","formal_function_hint","classification"]
    formatted=[]
    for r in raw:formatted.append({k:(f"{r[k]:.9f}"if isinstance(r[k],float)else r[k])for k in fields})
    write(CANDIDATES,formatted,fields)
    rank_lookup={(r["feature_family"],r["feature_value"]):r for r in raw}
    core_rows=[]
    for host in sorted({r["feature_value"]for r in raw if r["feature_family"]=="CORE"},key=lambda h:rank_lookup[("CORE",h)]["rank"]):
        base=rank_lookup[("CORE",host)];x={"core":host,"global_rank":base["rank"],"rank_score":f'{base["rank_score"]:.9f}',"classification":base["classification"],"formal_function_hint":base["formal_function_hint"]}
        for s in ALL_STRATA:
            wc=Counter({w:n for (h,st,w),n in core_wrapper.items()if h==host and st==s})
            sc=Counter({state:n for(h,st,state),n in core_state.items()if h==host and st==s})
            x[f"{s.lower()}_count"]=sum(wc.values());x[f"{s.lower()}_folios"]=len(core_folios[(host,s)])
            x[f"{s.lower()}_wrapper_forms"]=";".join(f"{w}:{n}"for w,n in sorted(wc.items(),key=lambda z:(-z[1],z[0])))
            x[f"{s.lower()}_states"]=";".join(f"{state}:{n}"for state,n in sorted(sc.items(),key=lambda z:(-z[1],z[0])))
        target_wrappers={w for(h,st,w),n in core_wrapper.items()if h==host and st in TARGET and n}
        x["target_wrapper_variety"]=len(target_wrappers);x["target_wrappers"]=";".join(sorted(target_wrappers))
        core_rows.append(x)
    core_fields=list(core_rows[0])if core_rows else["core"]
    write(CORES,core_rows,core_fields)
    struct=[r for r in formatted if r["feature_family"]in{"RECORD_STATE","FIELD_TEMPLATE","FIELD_SHAPE","CLOSED_FIELD_CLOSER","STATE_TRANSITION","WRAPPER_TRANSITION"}]
    write(STRUCTURE,struct,fields)
    counter=[r for r in formatted if r["classification"]in{"GENERIC_CURRIER_B_NOT_BS_SPECIFIC","B_S_ENRICHED_HAND_CONFOUNDED"}]
    write(COUNTER,counter[:100],fields)
    bs_candidates=[r for r in raw if r["classification"]=="B_S_REGISTER_CANDIDATE"]
    top_by_family={}
    for family in sorted({r["feature_family"]for r in raw}):top_by_family[family]=[r["feature_value"]for r in raw if r["feature_family"]==family][:5]
    result={"schema":"GDT037_HERBAL_B_RECIPE_SHARED_REGISTER_RESULT_V1","status":"B_S_SHARED_REGISTER_CANDIDATES_ISOLATED_CURRIER_HAND_CONFOUNDED",
            "scope":"Exploratory formal inventory of constructions shared by Herbal Currier B and Currier-B Stars/Recipe S but rare in Herbal A; no semantics.",
            "strata":{"HA":"section H Currier A","HB":"section H Currier B","SB":"section S Currier B primary target","OB":"other Currier B sections B/C/T","SA":"section S Currier A one-folio sensitivity"},
            "denominators":{f"{d}_{s}":n for(d,s),n in sorted(denominator.items())if s in ALL_STRATA},
            "capacity":{"eligible_features":len(raw),"bs_register_candidates":len(bs_candidates),"feature_family_eligible_counts":dict(sorted(family_eligible.items())),"minimum_count_each_target":MIN_COUNT,"minimum_folios_each_target":MIN_FOLIOS},
            "top_by_family":top_by_family,"top_register_candidates":[{"rank":r["rank"],"family":r["feature_family"],"value":r["feature_value"],"score":r["rank_score"],"formal_hint":r["formal_function_hint"]}for r in bs_candidates[:20]],
            "controls":{"currier":"Primary H-B and S comparison fixes Currier B; other Currier-B sections test generic B prevalence.","hand":"Hand 3 overlap is recorded per feature; H-B hands 2/3/5 and S-B hand 3/@ prevent complete hand balance.","cross_currier":"One S-A folio is sensitivity only, never replication.","robustness":"Minimum enrichment is recomputed after deleting every target folio in turn."},
            "claim_ceiling":"Identifies candidate shared formal register features and formal content/closure tendencies only. No word, morpheme, POS, function name, referent, sound, language, plaintext, meaning, or translation.",
            "f84r":{"opened":False,"retained":False,"queried":False,"joined":False,"scored":False},
            "inputs":{"gdt016_group_state_inventory.tsv":sha(SOURCE),"gdt016_result.json":sha(ROOT/"gdt016_result.json"),"gdt025_result.json":sha(ROOT/"gdt025_result.json"),"gdt033_result.json":sha(ROOT/"gdt033_result.json"),"gdt036_result.json":sha(ROOT/"gdt036_result.json")},
            "implementation":{Path(__file__).name:sha(Path(__file__))},"outputs":{CANDIDATES.name:sha(CANDIDATES),CORES.name:sha(CORES),STRUCTURE.name:sha(STRUCTURE),COUNTER.name:sha(COUNTER)}}
    # Report is generated before the result so its digest can be bound without a cycle.
    top=raw[:20];formal=bs_candidates[:20]
    core_shortlist=[x for x in core_rows if x["classification"]=="B_S_REGISTER_CANDIDATE"]
    report=f"""# GDT037 — Herbal-B / Stars-Recipe shared formal register

## Outcome

**B_S_SHARED_REGISTER_CANDIDATES_ISOLATED_CURRIER_HAND_CONFOUNDED**

This pass does not re-test whether Herbal-B and Stars/Recipe are globally similar. It isolates exact features that recur in both targets, subtracts Herbal-A prevalence, and then asks whether they are also more specific than **other Currier-B sections**. The primary inventories contain {denominator[('GROUP','HB')]:,} Herbal-B groups on 16 folios, {denominator[('GROUP','SB')]:,} Currier-B S groups on 13 folios, {denominator[('GROUP','HA')]:,} Herbal-A groups on 47 folios, and {denominator[('GROUP','OB')]:,} other Currier-B groups.

The scan retains **{len(raw):,}** cross-folio recurring formal features; **{len(bs_candidates)}** meet the stricter exploratory B↔S-register classification after requiring positive leave-one-target-folio enrichment over both Herbal-A and other Currier-B. These are candidate register markers, not meanings.

## Highest-ranked overall patterns

| Rank | Family | Pattern | HB/S/A/other-B counts | min log2 enrichment vs A | min log2 specificity vs other-B | target folios | hand-3 overlap | Classification |
|---:|---|---|---|---:|---:|---:|---|---|
"""
    for r in top:
        report+=f"| {r['rank']} | {r['feature_family']} | `{r['feature_value']}` | {r['hb_count']}/{r['sb_count']}/{r['ha_count']}/{r['ob_count']} | {r['shared_a_enrichment_log2']:.3f} | {r['shared_other_b_specificity_log2']:.3f} | {r['minimum_target_folio_support']} | {r['same_hand3_support']} | {r['classification']} |\n"
    report+="\n## Strongest B↔S-specific candidates\n\n| Rank | Family | Pattern | HB/S/A/other-B | LOFO min vs A / other-B | Formal reading |\n|---:|---|---|---|---:|---|\n"
    for r in formal[:20]:
        report+=f"| {r['rank']} | {r['feature_family']} | `{r['feature_value']}` | {r['hb_count']}/{r['sb_count']}/{r['ha_count']}/{r['ob_count']} | {r['lofo_min_a_enrichment_log2']:.3f} / {r['lofo_min_other_b_specificity_log2']:.3f} | {r['formal_function_hint']} |\n"
    report+="\n## Candidate residual cores, separated by formal behavior\n\n| Core | HB/S/A/other-B | Target wrapper variants | Anonymous-state tendency | Reading |\n|---|---:|---|---|---|\n"
    for x in core_shortlist:
        report+=f"| `{x['core']}` | {x['hb_count']}/{x['sb_count']}/{x['ha_count']}/{x['ob_count']} | {x['target_wrappers']} | {x['hb_states']} ; {x['sb_states']} | {x['formal_function_hint']} |\n"
    report+="""

`DAIIN` is the cleanest carrier-associated residual host: it recurs under `ch`, `che`, and `sh`, with 6/17 target occurrences versus 1 Herbal-A and 4 other-B. `OKAM` and `ODAIN` are the clearest mixed nonclosure candidates, but are weaker. `OPCH` and `OTCH` are not content leads: every target occurrence is a DY-resolution closer, making them candidate shared **field-closing templates**. Bare `AR` and bare `AIIN` are constructional selection effects; their underlying cores are much broader than the bare forms.

The earlier CKHY lead is an important counterexample to a simple practical-register vocabulary: CKHY occurs 23 times in Herbal-B and 33 in S, but also 17 in Herbal-A and 52 in other Currier-B; its target-versus-other-B specificity is negative. It is not a B↔S register marker here.

## Interpretation

The leading vocabulary candidates must be read through `gdt037_core_wrapper_atlas.tsv`, which keeps every observed wrapper distribution and anonymous-state distribution separate. A core recurrent under several wrappers is evidence for a stable residual host, not for a lexeme. `MIXED_NONCLOSURE_HOST_CANDIDATE` means only that the core is not normally the DY-resolution closer in this formal parser; it is the appropriate pool for later independent grounding.

The structural atlas separately ranks anonymous states, exact state-field templates, compact field shapes, closer hosts, state transitions, and wrapper transitions. This prevents a frequent closure renderer from being mistaken for content vocabulary. Generic Currier-B patterns are retained as counterexamples rather than promoted as B↔S-specific.

## Hand and Currier limits

The primary target comparison fixes Currier B. Other Currier-B sections are the strongest available control against simply rediscovering the B renderer. Hand 3 occurs in both Herbal-B and S, and every candidate records whether it recurs there. But Herbal-B also uses hands 2 and 5, S is overwhelmingly hand 3, and Herbal-A is hand 1/Currier A. Consequently A-rarity can never be fully separated from Currier/hand with this manuscript. The single Currier-A S folio is reported only as sensitivity.

No candidate receives a semantic function, object, medical operation, ingredient, word, morpheme, POS, sound, language, plaintext, or translation. f84r was not opened, retained, queried, joined, or scored.
"""
    REPORT.write_text(report,encoding="utf-8")
    result["documents"]={METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)}
    body=dict(result);result["result_content_sha256"]=csha(body);RESULT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"status":result["status"],"eligible":len(raw),"candidates":len(bs_candidates)},sort_keys=True))


if __name__=="__main__":main()
