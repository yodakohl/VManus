#!/usr/bin/env python3
"""Independent integrity and exact-statistic validator for GDT012."""

from __future__ import annotations

import csv
import hashlib
import json
import math
from collections import defaultdict
from fractions import Fraction
from pathlib import Path

ROOT=Path(__file__).resolve().parent
RESULT=ROOT/"gdt012_result.json";VALIDATION=ROOT/"gdt012_validation.json"
PREFIXES=("che","ch","sh","t","s","d","q")


def read(name:str)->list[dict[str,str]]:
    with (ROOT/name).open(encoding="utf-8",newline="") as h:return list(csv.DictReader(h,delimiter="\t"))
def sha(path:Path)->str:return hashlib.sha256(path.read_bytes()).hexdigest()
def csha(value:object)->str:return hashlib.sha256(json.dumps(value,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def strip(token:str)->tuple[str,str,int]:
    prefix="NONE";host=token
    for x in PREFIXES:
        if host.startswith(x)and len(host)>len(x):prefix=x;host=host[len(x):];break
    dy=int(host.endswith("dy")and len(host)>2)
    if dy:host=host[:-2]
    return prefix,host,dy
def tags(row:dict[str,str],outcome:str)->bool:
    field="object_tags" if outcome in {"PLANT","FIGURE","WATER_OR_APPARATUS","STAR_OR_SKY","ROSETTE_OR_MAP"}else"relation_tags"
    return outcome in row[field].split(";")
def hpmf(n:int,k:int,m:int)->dict[int,Fraction]:
    den=math.comb(n,m);return{x:Fraction(math.comb(k,x)*math.comb(n-k,m-x),den)for x in range(max(0,m-(n-k)),min(m,k)+1)}
def test(rows:list[dict[str,str]],feature:set[int],outcome:str,allowed:set[int],stratum_field:str="page")->tuple[float,float,int,int,float]:
    pages=defaultdict(list)
    for i in allowed:pages[rows[i][stratum_field]].append(i)
    strata=[];obs=0;exp=Fraction();num=den=0.
    for indexes in pages.values():
        n=len(indexes);m=sum(i in feature for i in indexes);k=sum(tags(rows[i],outcome)for i in indexes)
        if not(0<m<n and 0<k<n):continue
        x=sum(i in feature and tags(rows[i],outcome)for i in indexes);w=m*(n-m)/n
        strata.append((n,m,k));obs+=x;exp+=Fraction(m*k,n);num+=w*(x/m-(k-x)/(n-m));den+=w
    pmf={0:Fraction(1)}
    for n,m,k in strata:
        nxt=defaultdict(Fraction)
        for a,pa in pmf.items():
            for b,pb in hpmf(n,k,m).items():nxt[a+b]+=pa*pb
        pmf=dict(nxt)
    d=abs(Fraction(obs)-exp);p=sum(v for x,v in pmf.items()if abs(Fraction(x)-exp)>=d)if strata else Fraction(1)
    return num/den if den else 0.,float(p),len(strata),obs,float(exp)


def main()->None:
    checks=[];result=json.loads(RESULT.read_text());copy=dict(result);recorded=copy.pop("result_content_sha256")
    checks.extend([("schema",result["schema"]=="GDT012_CORE_SEMANTIC_ATLAS_RESULT_V1"),("content_hash",recorded==csha(copy))])
    for part in("inputs","implementation","outputs"):
        for name,digest in result[part].items():checks.append((part+":"+name,sha(ROOT/name)==digest))
    rows=read("gdt012_annotated_core_inventory.tsv");atlas=read("gdt012_core_semantic_candidates.tsv");roles=read("gdt012_provisional_core_roles.tsv");counter=read("gdt012_core_semantic_counterexamples.tsv")
    checks.extend([("inventory_count",len(rows)==result["inventory_rows"]==671),("primary_count",sum(r["annotation_certainty"]=="UNHEDGED"for r in rows)==result["primary_unhedged_rows"]==394),("pages",len({r["page"]for r in rows})==result["pages"]==50),("f84_sealed",not any(r["locus"].startswith("f84r")for r in rows)and result["f84r"]=={"opened":False,"retained":False,"joined":False,"scored":False})])
    checks.append(("unique_groups",len({r["group_id"]for r in rows})==len(rows)))
    checks.append(("layer_projection",all(strip(r["token"])==(r["stripped_prefix"],r["residual_host"],int(r["dy_closure"]))for r in rows)))
    # Independently bind every inventory record to source-native consensus and human annotation.
    annotation={r["locus"]:r for r in read("experiments/semantic_assumptions/results/existing_human_exact_locus_annotations.tsv")}
    consensus={(r["locus"],r["consensus_group_index"]):r for r in read("experiments/semantic_assumptions/results/source_sta_family_consensus_groups.tsv")}
    align=defaultdict(list)
    for r in read("experiments/semantic_assumptions/results/source_sta_group_alignment.tsv"):align[(r["locus"],r["source_group_index"])].append(r)
    source_ok=True
    for row in rows:
        key=(row["locus"],str(int(row["group_index"])));a=annotation.get(row["locus"]);c=consensus.get(key);g=align.get(key,[])
        source_ok &= bool(a and c and c["strict_zero_alternative"]=="1"and c["grammar_scope"]=="DIAGNOSTIC_NONPROSE"and c["family_surface"]==row["family_surface"])
        source_ok &= {x["edition"]for x in g}=={"ZL3b","IT2a","RF1b"}and {x["nearest_basic_eva_primary"]for x in g}=={row["token"]}
        source_ok &= a["certainty"]==row["annotation_certainty"]and a["source_path"]==row["annotation_source"]
    checks.append(("source_join_exact",source_ok))
    checks.extend([("atlas_grid",len(atlas)==result["family_tests"]==1760 and len({r["candidate_id"]for r in atlas})==len(atlas)),("candidate_ids",all(r["candidate_id"]==hashlib.sha256((r["formal_feature"]+"|"+r["visual_outcome"]).encode()).hexdigest()[:12]for r in atlas)),("adjustments",all(abs(float(r["search_adjusted_p"])-min(1.,1760*float(r["exact_local_p"])))<2e-9 for r in atlas))])
    primary={i for i,r in enumerate(rows)if r["annotation_certainty"]=="UNHEDGED"}
    target_specs=[("HOST_LENGTH:1","REL_EXPLICIT_ATTACHMENT"),("HOST_CONTAINS:ar","REL_ENCLOSURE"),("HOST_EQ:o","REL_EXPLICIT_ATTACHMENT"),("HOST_CONTAINS:dal","REL_ARRAY_OR_GROUP"),("HOST_SUFFIX:dar","REL_PROXIMITY")]
    stored={(r["formal_feature"],r["visual_outcome"]):r for r in atlas}
    for feature,outcome in target_specs:
        if feature.startswith("HOST_LENGTH:"):value=int(feature.split(":",1)[1]);mask={i for i,r in enumerate(rows)if int(r["host_length"])==value}
        elif feature.startswith("HOST_CONTAINS:"):value=feature.split(":",1)[1];mask={i for i,r in enumerate(rows)if value in r["residual_host"]}
        elif feature.startswith("HOST_SUFFIX:"):value=feature.split(":",1)[1];mask={i for i,r in enumerate(rows)if r["residual_host"].endswith(value)}
        else:value=feature.split(":",1)[1];mask={i for i,r in enumerate(rows)if r["residual_host"]==value}
        effect,p,np,obs,exp=test(rows,mask,outcome,primary);row=stored[(feature,outcome)]
        checks.append(("exact:"+feature+":"+outcome,abs(effect-float(row["within_page_effect"]))<5e-13 and abs(p-float(row["exact_local_p"]))<5e-13 and np==int(row["informative_pages"])and obs==int(row["conditional_observed"])and abs(exp-float(row["conditional_expected"]))<5e-10))
        fe,fp,fn,_,_=test(rows,mask,outcome,primary,"physical_folio")
        checks.append(("folio:"+feature+":"+outcome,abs(fe-float(row["within_physical_folio_effect"]))<5e-13 and abs(fp-float(row["physical_folio_exact_p"]))<5e-13 and fn==int(row["informative_physical_folios"])))
    checks.extend([("top_candidate",result["strongest_candidate"]["candidate_id"]=="e26b8bd54faf"and result["strongest_reusable_module_candidate"]["candidate_id"]=="a9c4415fb9e1"),("roles",{r["formal_unit"]for r in roles}=={"AR","DAL","DAR","O_HOST","ONE_SIGN_HOST"}and all(r["candidate_id"]in {x["candidate_id"]for x in atlas}for r in roles)),("counterexamples",len(counter)>0 and all(r["counterexample_type"]in {"FEATURE_WITHOUT_OUTCOME","OUTCOME_WITHOUT_FEATURE"}for r in counter)),("ledger",(ROOT/"GDT002_YOLO_LEDGER.tsv").read_text().count("GDT012_CKPT001")==1)])
    report=(ROOT/"GDT012_CORE_SEMANTIC_ATLAS_REPORT.md").read_text().lower();checks.extend([("claim_ceiling",all(x in report for x in("post-hoc","no word","translation","f84r was not opened"))),("ar_caveat","bounded/local"in report and"adjustment is null"in report)])
    failures=[name for name,ok in checks if not ok];validation={"schema":"GDT012_CORE_SEMANTIC_ATLAS_VALIDATION_V1","status":"PASS"if not failures else"FAIL","checks":len(checks),"failures":failures,"result_sha256":sha(RESULT),"validator_sha256":sha(Path(__file__)),"scope":"Independent source-table binding, layer projection, candidate grid and adjustments, five exact page- and physical-folio-conditioned hypergeometric reconstructions, role/counterexample joins, f84 sealing, hashes, ledger, and claim ceiling."}
    VALIDATION.write_text(json.dumps(validation,indent=2,sort_keys=True)+"\n");print(json.dumps(validation,sort_keys=True))
    if failures:raise SystemExit(1)


if __name__=="__main__":main()
