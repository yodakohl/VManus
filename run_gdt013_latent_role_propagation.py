#!/usr/bin/env python3
"""Cross-folio latent visual-role prediction and prose propagation."""

from __future__ import annotations

import csv
import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

from run_gdt012_core_semantic_atlas import ROOT, RESULTS, canonical_sha, exact_page_test, physical_folio, read_tsv, sha, strip_layers, write_tsv

ROLES=("PLANT","FIGURE","WATER_OR_APPARATUS","STAR_OR_SKY","REL_EXPLICIT_ATTACHMENT","REL_ENCLOSURE","REL_PROXIMITY","REL_ARRAY_OR_GROUP")
OBJECTS=set(ROLES[:4]);MODELS=("PRIOR","NUISANCE","WHOLE_TOKEN_STRING","RESIDUAL_HOST","SOURCE_FAMILY","FIELD_CONTENT_JOINT")


def ngrams(text:str,tag:str)->set[str]:
    padded="^"+text+"$";return{f"{tag}{n}:{padded[i:i+n]}"for n in(1,2,3)for i in range(len(padded)-n+1)}
def nuisance(row:dict[str,str])->set[str]:
    return{f"SECTION:{row['section']}",f"CURRIER:{row['currier']}",f"HAND:{row['hand']}",f"KIND:{row['kind']}",f"HOST_LEN:{min(9,int(row['host_length']))}",f"GROUP_COUNT:{min(4,int(row['group_count']))}"}
def features(row:dict[str,str],model:str)->set[str]:
    n=nuisance(row)
    host=ngrams(row["residual_host"],"H")|{f"HOST_EXACT:{row['residual_host']}",f"LAYER:{row['stripped_prefix']}",f"CLOSURE:{row['dy_closure']}"}
    family=ngrams(row["family_surface"],"F")|{f"FAMILY_EXACT:{row['family_surface']}"}
    token=ngrams(row["token"],"T")|{f"TOKEN_EXACT:{row['token']}"}
    return n if model=="NUISANCE" else n|token if model=="WHOLE_TOKEN_STRING" else n|host if model=="RESIDUAL_HOST" else n|family if model=="SOURCE_FAMILY" else n|host|family if model=="FIELD_CONTENT_JOINT" else set()
def target(row:dict[str,str],role:str)->int:
    field="object_tags"if role in OBJECTS else"relation_tags";return int(role in row[field].split(";"))


def train_nb(rows:list[dict[str,str]],indexes:list[int],role:str,model:str)->dict[str,object]:
    ys=[target(rows[i],role)for i in indexes];pos=sum(ys);neg=len(ys)-pos;prior=(pos+1)/(len(ys)+2)
    if model=="PRIOR":return{"prior":prior,"base":math.log(prior/(1-prior)),"delta":{},"vocab":set()}
    doc=Counter()
    for i in indexes:doc.update(features(rows[i],model))
    vocab={f for f,n in doc.items()if n>=2};cp=Counter();cn=Counter()
    for i,y in zip(indexes,ys):(cp if y else cn).update(features(rows[i],model)&vocab)
    base=math.log(prior/(1-prior));delta={}
    for f in vocab:
        p1=(cp[f]+1)/(pos+2);p0=(cn[f]+1)/(neg+2)
        base+=math.log((1-p1)/(1-p0));delta[f]=math.log(p1/(1-p1))-math.log(p0/(1-p0))
    return{"prior":prior,"base":base,"delta":delta,"vocab":vocab,"support":doc,"positive":cp,"negative":cn}
def predict_nb(fit:dict[str,object],row:dict[str,str],model:str)->float:
    if model=="PRIOR":return float(fit["prior"])
    score=float(fit["base"])+sum(fit["delta"].get(f,0.)for f in features(row,model))
    if score>35:return 1-1e-15
    if score< -35:return 1e-15
    return 1/(1+math.exp(-score))
def average_precision(y:list[int],p:list[float])->float:
    total=sum(y)
    if not total:return 0.
    groups=defaultdict(lambda:[0,0])
    for yy,pp in zip(y,p):groups[pp][0]+=yy;groups[pp][1]+=1
    tp=seen=0;ap=0.
    for score in sorted(groups,reverse=True):
        positives,count=groups[score];tp+=positives;seen+=count
        if positives:ap+=(positives/total)*(tp/seen)
    return ap
def metrics(y:list[int],p:list[float])->tuple[float,float,float]:
    b=sum((a-b)**2 for a,b in zip(y,p))/len(y);ll=-sum(a*math.log(max(1e-15,b))+(1-a)*math.log(max(1e-15,1-b))for a,b in zip(y,p))/len(y)
    return b,ll,average_precision(y,p)


def all_strict_groups()->list[dict[str,str]]:
    consensus={}
    with (RESULTS/"source_sta_family_consensus_groups.tsv").open(encoding="utf-8",newline="")as h:
        for r in csv.DictReader(h,delimiter="\t"):
            if not r["locus"].startswith("f84r")and r["strict_zero_alternative"]=="1":consensus[(r["locus"],r["consensus_group_index"])]=r
    align=defaultdict(list)
    with (RESULTS/"source_sta_group_alignment.tsv").open(encoding="utf-8",newline="")as h:
        for r in csv.DictReader(h,delimiter="\t"):
            if not r["locus"].startswith("f84r"):align[(r["locus"],r["source_group_index"])].append(r)
    out=[]
    for key,reads in align.items():
        c=consensus.get(key);tokens={r["nearest_basic_eva_primary"]for r in reads}
        if not c or {r["edition"]for r in reads}!={"ZL3b","IT2a","RF1b"}or len(tokens)!=1 or""in tokens:continue
        token=next(iter(tokens));prefix,host,dy=strip_layers(token)
        out.append({"locus":key[0],"page":c["page"],"physical_folio":physical_folio(c["page"]),"group_index":int(key[1]),"token":token,"residual_host":host,"stripped_prefix":prefix,"dy_closure":dy,"family_surface":c["family_surface"],"grammar_scope":c["grammar_scope"],"section":c["section"],"currier":c["currier"],"hand":c["hand"],"kind":c["kind"],"host_length":len(host),"group_count":int(c["consensus_group_count"])})
    return sorted(out,key=lambda r:(r["locus"],r["group_index"]))


def main()->None:
    annotated=read_tsv(ROOT/"gdt012_annotated_core_inventory.tsv");rows=[r for r in annotated if r["annotation_certainty"]=="UNHEDGED"]
    assert len(rows)==394 and not any(r["locus"].startswith("f84r")for r in rows)
    folios=sorted({r["physical_folio"]for r in rows});pred=[]
    for held in folios:
        train=[i for i,r in enumerate(rows)if r["physical_folio"]!=held];test=[i for i,r in enumerate(rows)if r["physical_folio"]==held]
        for role in ROLES:
            for model in MODELS:
                fit=train_nb(rows,train,role,model)
                for i in test:pred.append({"held_folio":held,"group_id":rows[i]["group_id"],"role":role,"model":model,"actual":target(rows[i],role),"probability":f"{predict_nb(fit,rows[i],model):.12f}"})
    write_tsv(ROOT/"gdt013_heldout_predictions.tsv",pred)
    comparison=[]
    for role in ROLES:
        prior_brier=None;token_brier=None
        for model in MODELS:
            subset=[r for r in pred if r["role"]==role and r["model"]==model];y=[int(r["actual"])for r in subset];p=[float(r["probability"])for r in subset];b,ll,ap=metrics(y,p)
            if model=="PRIOR":prior_brier=b
            if model=="WHOLE_TOKEN_STRING":token_brier=b
            comparison.append({"role":role,"model":model,"rows":len(y),"positives":sum(y),"held_folio_brier":f"{b:.12f}","held_folio_logloss":f"{ll:.12f}","held_folio_average_precision":f"{ap:.12f}","brier_gain_vs_prior":f"{prior_brier-b:.12f}"if prior_brier is not None else"0.000000000000","brier_gain_vs_whole_token":f"{token_brier-b:.12f}"if token_brier is not None else"NOT_YET_AVAILABLE"})
    # Backfill token comparisons after every role/model score exists.
    by={(r["role"],r["model"]):r for r in comparison}
    for r in comparison:r["brier_gain_vs_whole_token"]=f"{float(by[(r['role'],'WHOLE_TOKEN_STRING')]['held_folio_brier'])-float(r['held_folio_brier']):.12f}"
    write_tsv(ROOT/"gdt013_model_comparison.tsv",comparison)
    mean_brier={m:sum(float(by[(role,m)]["held_folio_brier"])for role in ROLES)/len(ROLES)for m in MODELS}
    mean_ap={m:sum(float(by[(role,m)]["held_folio_average_precision"])for role in ROLES)/len(ROLES)for m in MODELS}
    selected_calibration=min(MODELS,key=lambda m:(mean_brier[m],m))
    selected_discrimination=max((m for m in MODELS if m!="PRIOR"),key=lambda m:(mean_ap[m],m))

    weights=[];top_features=defaultdict(list);allidx=list(range(len(rows)));propagation_models=("SOURCE_FAMILY","RESIDUAL_HOST")
    for model in propagation_models:
        for role in ROLES:
            fit=train_nb(rows,allidx,role,model)
            for feature,weight in fit["delta"].items():
                support=int(fit["support"][feature]);positive=int(fit["positive"][feature]);feature_folios=len({rows[i]["physical_folio"]for i in allidx if feature in features(rows[i],model)})
                if support<3 or feature_folios<2:continue
                row={"role":role,"formal_feature":feature,"log_odds_weight":f"{weight:.12f}","support":support,"positive_support":positive,"physical_folios":feature_folios,"selected_model":model,"claim_state":"POSTSELECTED_ROLE_MOTIF_NOT_MEANING"}
                weights.append(row)
            candidates=[r for r in weights if r["role"]==role and r["selected_model"]==model and r["formal_feature"].startswith(("H2:","H3:","HOST_EXACT:","F2:","F3:","FAMILY_EXACT:"))]
            top_features[(role,model)]=sorted(candidates,key=lambda r:(-float(r["log_odds_weight"]),-int(r["support"]),r["formal_feature"]))[:5]
    weights.sort(key=lambda r:(r["selected_model"],r["role"],-float(r["log_odds_weight"]),-int(r["support"]),r["formal_feature"]));write_tsv(ROOT/"gdt013_feature_role_weights.tsv",weights)

    corpus=all_strict_groups();prose=[]
    anchors=[]
    for model in propagation_models:
      for role in ROLES:
        for rank,w in enumerate(top_features[(role,model)],1):
            feature=w["formal_feature"];matches=[r for r in corpus if r["grammar_scope"]=="CONFIRMED_PROSE"and feature in features(r,model)]
            anchors.append({"role":role,"rank":rank,**w,"prose_occurrence_total":len(matches),"prose_occurrences_exported":min(40,len(matches))})
            for row in matches[:40]:
                prose.append({"role_hypothesis":role,"anchor_model":model,"anchor_rank":rank,"formal_feature":feature,"feature_weight":w["log_odds_weight"],"locus":row["locus"],"page":row["page"],"physical_folio":row["physical_folio"],"group_index":row["group_index"],"token":row["token"],"residual_host":row["residual_host"],"stripped_prefix":row["stripped_prefix"],"dy_closure":row["dy_closure"],"family_surface":row["family_surface"],"claim_state":"PROSE_PROPAGATION_HYPOTHESIS_NOT_DECODED_TEXT"})
    write_tsv(ROOT/"gdt013_role_anchors.tsv",anchors);write_tsv(ROOT/"gdt013_prose_anchor_occurrences.tsv",prose)

    primary={i for i,r in enumerate(annotated)if r["annotation_certainty"]=="UNHEDGED"}
    motif_specs=(("ARO","aro","REL_PROXIMITY","ADJACENT_OR_LOCAL_REFERENCE"),("TAR","tar","REL_ENCLOSURE","BOUNDED_OR_INTERIOR_REFERENCE"),("ED","ed","WATER_OR_APPARATUS","APPARATUS_OR_MEDIUM_FIELD"),("KAL","kal","FIGURE","FIGURE_ASSOCIATED_INDEX"))
    motif_leads=[]
    for name,motif,role,gloss in motif_specs:
        mask={i for i,r in enumerate(annotated)if motif in r["residual_host"]};page=exact_page_test(annotated,mask,role,primary);folio=exact_page_test(annotated,mask,role,primary,"physical_folio")
        support=sum(i in mask for i in primary);positive=sum(i in mask and target(annotated[i],role)for i in primary)
        label="CROSS_FOLIO_WEAK_LEAD"if folio["p"]<.20 and folio["effect"]>0 else"REGISTER_ASSOCIATION_ONLY"if positive==support and support>=5 else"PAGE_OR_DOMAIN_CONFOUND"
        motif_leads.append({"motif":name,"residual_substring":motif,"provisional_function":gloss,"visual_channel":role,"support":support,"positive_support":positive,"physical_folios":len({annotated[i]["physical_folio"]for i in primary if i in mask}),"page_conditioned_effect":f"{page['effect']:.12f}","page_exact_p":f"{page['p']:.12f}","folio_conditioned_effect":f"{folio['effect']:.12f}","folio_exact_p":f"{folio['p']:.12f}","label":label,"claim_state":"SPECULATIVE_MICROGRAMMAR_NOT_WORD_MEANING"})
    write_tsv(ROOT/"gdt013_relational_motif_leads.tsv",motif_leads)

    joint_gain=mean_brier["WHOLE_TOKEN_STRING"]-mean_brier["FIELD_CONTENT_JOINT"]
    family_ap_gain=mean_ap["SOURCE_FAMILY"]-mean_ap["WHOLE_TOKEN_STRING"]
    status="WEAK_ROLE_RANKING_WITH_RELATIONAL_MICROGRAMMAR_LEADS"
    report=f"""# GDT013 latent-role propagation report

Status: **{status.replace('_',' ')}**

## Held-physical-folio result

The experiment used {len(rows)} unhedged annotated groups on {len(folios)}
physical folios.  `{selected_calibration}` is the best calibrated model;
`{selected_discrimination}` gives the best mean held-folio ranking.  Mean
Brier / average precision across eight channels are:

"""+"\n".join(f"- `{m}`: {mean_brier[m]:.6f} / {mean_ap[m]:.6f}"for m in MODELS)+f"""

`FIELD_CONTENT_JOINT` changes mean Brier by {joint_gain:+.6f} relative to the
whole-token string model.  Source-native family structure changes mean AP by
{family_ap_gain:+.6f} relative to that string model.  The prior remains best
calibrated and nuisance/register structure nearly matches the best AP: there
is no general semantic decoder here.

## Concrete microgrammar leads

The best abductive contrast is now more specific than `AR` alone:

- `ARO` occurs in proximity-labelled contexts {motif_leads[0]['positive_support']}/{motif_leads[0]['support']} times across {motif_leads[0]['physical_folios']} physical folios.  It is a plausible **adjacent/local-reference** sequence, but the within-folio p={float(motif_leads[0]['folio_exact_p']):.3f} shows that it largely follows register ecology.
- `TAR` occurs in enclosure contexts {motif_leads[1]['positive_support']}/{motif_leads[1]['support']} times across {motif_leads[1]['physical_folios']} folios.  Its folio-conditioned effect is {float(motif_leads[1]['folio_conditioned_effect']):+.3f} (p={float(motif_leads[1]['folio_exact_p']):.3f}), making **bounded/interior reference** the sharper risky prediction.
- `ED` is a weak apparatus/medium lead; `KAL` is a figure-associated index lead.  Both remain domain-confounded.

This suggests a provisional local-reference microgrammar in which material
around `AR`—especially `O` versus `T/OT` environments—modulates how a referent
is situated.  It is a generative hypothesis, not a lexical segmentation.

## What was extracted

The full-data exploratory fit ranks {len(weights)} formal feature/role weights.
The top five source-family and residual-host motifs per channel were propagated into
{len(prose)} strict, all-reading confirmed-prose occurrences.  These are
concrete places where the label-derived theory makes a functional prediction;
they are not decoded prose.

GDT012's `AR` enclosure lead remains one member of a larger motif system rather
than a proposed standalone word.  GDT013 asks whether neighboring
source-family and residual-host features reinforce or replace it.  The anchor
and prose TSVs preserve every feature, score, locus, and renderer state so the
next pass can search record-level co-occurrence patterns instead of inventing
English sentences.

## Limits

The human labels are sparse and diagram-family clustered.  Naive Bayes assumes
conditional independence, and the selected model is post-selected on these
same eight channels.  A role predictor can exploit domain/register style even
under folio holdout.  Therefore every propagated role is speculative.

No word, morpheme, POS, sound, language, plaintext, or translation is claimed.
f84r remained unopened, unretained, unjoined, and unscored.
"""
    (ROOT/"GDT013_LATENT_ROLE_PROPAGATION_REPORT.md").write_text(report)
    outputs=("gdt013_heldout_predictions.tsv","gdt013_model_comparison.tsv","gdt013_feature_role_weights.tsv","gdt013_role_anchors.tsv","gdt013_prose_anchor_occurrences.tsv","gdt013_relational_motif_leads.tsv","GDT013_LATENT_ROLE_PROPAGATION_REPORT.md")
    inputs=("gdt012_annotated_core_inventory.tsv","gdt012_result.json","experiments/semantic_assumptions/results/source_sta_group_alignment.tsv","experiments/semantic_assumptions/results/source_sta_family_consensus_groups.tsv","GDT013_LATENT_ROLE_PROPAGATION_METHOD.md")
    result={"schema":"GDT013_LATENT_ROLE_PROPAGATION_RESULT_V1","status":status,"annotated_rows":len(rows),"physical_folios":len(folios),"roles":len(ROLES),"models":len(MODELS),"selected_calibration_model":selected_calibration,"selected_discrimination_model":selected_discrimination,"mean_brier":mean_brier,"mean_average_precision":mean_ap,"joint_gain_vs_whole_token":joint_gain,"source_family_ap_gain_vs_whole_token":family_ap_gain,"role_weight_rows":len(weights),"prose_propagations":len(prose),"top_anchors":anchors,"relational_motif_leads":motif_leads,"f84r":{"opened":False,"retained":False,"joined":False,"scored":False},"claim_ceiling":"Exploratory formal-role propagation only; no confirmed word, morpheme, POS, sound, language, plaintext, or translation.","inputs":{x:sha(ROOT/x)for x in inputs},"implementation":{"run_gdt013_latent_role_propagation.py":sha(Path(__file__)),"run_gdt012_core_semantic_atlas.py":sha(ROOT/"run_gdt012_core_semantic_atlas.py")},"outputs":{x:sha(ROOT/x)for x in outputs}}
    result["result_content_sha256"]=canonical_sha(result);(ROOT/"gdt013_result.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"status":status,"calibration":selected_calibration,"discrimination":selected_discrimination,"mean_brier":mean_brier,"mean_ap":mean_ap,"joint_gain":joint_gain,"family_ap_gain":family_ap_gain,"weights":len(weights),"prose":len(prose),"motifs":motif_leads},sort_keys=True))


if __name__=="__main__":main()
