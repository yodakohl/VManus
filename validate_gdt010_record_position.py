#!/usr/bin/env python3
"""Independent reconstruction and sensitivity validator for GDT010."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import random
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RESULT = ROOT / "gdt010_result.json"
VALIDATION = ROOT / "gdt010_validation.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()).hexdigest()


def read_tsv(name: str) -> list[dict[str, str]]:
    with (ROOT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def tagged(value: str, key: str) -> str:
    for part in value.split(";"):
        if part.startswith(key + ":"): return part.split(":", 1)[1]
    return ""


def reconstruct_groups(source: list[dict[str, str]]) -> list[dict[str, object]]:
    out = {}
    for row in source:
        key = (row["locus"], row["source_group_index"])
        if key in out or not row["ZL3b_token"] or not (row["ZL3b_token"] == row["IT2a_token"] == row["RF1b_token"]): continue
        n = int(tagged(row["source_group_count_by_reading"], "ZL3b")); i = int(row["source_group_index"])
        out[key] = {"token":row["ZL3b_token"],"normalized_position":(i-1)/(n-1) if n>1 else .5,"line_final":int(i==n),"line_initial":int(i==1),"nonprose":int(row["layout_role"]!="RUNNING_TEXT"),"page":row["page"],"folio":row["physical_folio"],"section":row["section"]}
    return list(out.values())


def maps(groups: list[dict[str, object]]) -> dict[str, tuple[dict, dict]]:
    tokens = defaultdict(list)
    for row in groups: tokens[row["token"]].append(row)
    bareq,q,s,d = (defaultdict(list) for _ in range(4)); suffix={x:defaultdict(list) for x in ("dy","dal","dar","sy")}; bare=defaultdict(list)
    for token,items in tokens.items():
        (q[token[1:]] if token.startswith("q") and len(token)>1 else bareq[token]).extend(items)
        if token.startswith("s") and len(token)>1:s[token[1:]].extend(items)
        if token.startswith("d") and len(token)>1:d[token[1:]].extend(items)
        hit=False
        for ending in ("dal","dar","sy","dy"):
            if token.endswith(ending) and len(token)>len(ending):suffix[ending][token[:-len(ending)]].extend(items);hit=True;break
        if not hit:bare[token].extend(items)
    return {"C01_BARE_TO_Q":(bareq,q),"C02_S_TO_D":(s,d),"C03_BARE_TO_DY":(bare,suffix["dy"]),"C04_BARE_TO_SY":(bare,suffix["sy"]),"C05_DAL_TO_DAR":(suffix["dal"],suffix["dar"])}


def strata(a: dict, b: dict, scope: str) -> list[tuple[list[dict],list[dict]]]:
    out=[]
    for host in sorted(set(a)&set(b)):
        if scope=="HOST_GLOBAL": buckets=[(a[host],b[host])]
        else:
            key="folio" if scope=="HOST_PHYSICAL_FOLIO" else "page";av,bv=defaultdict(list),defaultdict(list)
            for row in a[host]:av[row[key]].append(row)
            for row in b[host]:bv[row[key]].append(row)
            buckets=[(av[x],bv[x]) for x in sorted(set(av)&set(bv))]
        out.extend((aa,bb) for aa,bb in buckets if aa and bb)
    return out


def effect(parts: list[tuple[list[dict],list[dict]]], metric: str) -> tuple[float,int,int,int]:
    num=den=0.;na=nb=0
    for aa,bb in parts:
        ma=sum(float(x[metric]) for x in aa)/len(aa);mb=sum(float(x[metric]) for x in bb)/len(bb);w=len(aa)*len(bb)/(len(aa)+len(bb));num+=w*(mb-ma);den+=w;na+=len(aa);nb+=len(bb)
    return num/den,len(parts),na,nb


def independent_p(parts: list[tuple[list[dict],list[dict]]], metric: str, observed: float, seed: int, draws: int=2000) -> float:
    rng=random.Random(seed);pools=[]
    for aa,bb in parts:pools.append(([float(x[metric]) for x in aa+bb],len(aa),len(bb),len(aa)*len(bb)/(len(aa)+len(bb))))
    den=sum(x[3] for x in pools);extreme=0
    for _ in range(draws):
        total=0.
        for values,na,nb,w in pools:
            chosen=set(rng.sample(range(len(values)),nb));sb=sum(values[i] for i in chosen);sa=sum(values)-sb;total+=w*(sb/nb-sa/na)
        extreme += abs(total/den) >= abs(observed)-1e-15
    return (extreme+1)/(draws+1)


def main() -> None:
    checks=[];result=json.loads(RESULT.read_text());norm=dict(result);recorded=norm.pop("result_content_sha256")
    checks.append(("schema",result["schema"]=="GDT010_RECORD_POSITION_RESULT_V1"));checks.append(("content_hash",recorded==canonical_sha(norm)))
    for section in ("inputs","implementation","outputs"):
        for name,digest in result[section].items():checks.append((f"{section}:{name}",sha(ROOT/name)==digest))
    source=read_tsv("gdt002_morphology_occurrences.tsv");groups=reconstruct_groups(source);tests=read_tsv("gdt010_record_position_tests.tsv");constraints=read_tsv("gdt010_functional_constraints.tsv");model=json.loads((ROOT/"gdt010_ordered_record_model.json").read_text())
    checks.append(("no_f84",not any(r["locus"].startswith("f84r") for r in source)));checks.append(("group_count",len(groups)==result["group_universe"]==10890));checks.append(("test_grid",len(tests)==60 and len({(r["contrast_id"],r["match_scope"],r["metric"]) for r in tests})==60 and result["primary_scope"]=="HOST_PAGE"))
    fm=maps(groups);stored={(r["contrast_id"],r["match_scope"],r["metric"]):r for r in tests};scope="HOST_PAGE"
    keys=[("C01_BARE_TO_Q",scope,"normalized_position"),("C01_BARE_TO_Q",scope,"nonprose"),("C02_S_TO_D",scope,"normalized_position"),("C02_S_TO_D",scope,"line_initial"),("C03_BARE_TO_DY",scope,"normalized_position"),("C03_BARE_TO_DY",scope,"line_final"),("C04_BARE_TO_SY",scope,"line_final"),("C05_DAL_TO_DAR",scope,"normalized_position")]
    effects={}
    parts={contrast:strata(*fm[contrast],scope) for contrast in fm}
    for contrast,match_scope,metric in keys:
        value,nstrata,na,nb=effect(parts[contrast],metric);row=stored[(contrast,match_scope,metric)];effects[(contrast,match_scope,metric)]=value
        checks.append((f"effect:{contrast}:{metric}",abs(value-float(row["host_fixed_effect_B_minus_A"]))<5e-13 and nstrata==int(row["matched_strata"]) and na==int(row["form_a_groups"]) and nb==int(row["form_b_groups"])))
    # Fresh, lower-resolution null draws verify the decision directions without reusing producer randomness.
    fresh={key:independent_p(parts[key[0]],key[2],effects[key],101+i) for i,key in enumerate(keys)}
    checks.append(("q_signal",effects[("C01_BARE_TO_Q",scope,"normalized_position")]<-.04 and fresh[("C01_BARE_TO_Q",scope,"normalized_position")]<.01 and float(stored[("C01_BARE_TO_Q",scope,"normalized_position")]["search_adjusted_p_20_primary_tests"])<=.0011))
    checks.append(("d_s_confounded",effects[("C02_S_TO_D",scope,"normalized_position")]>0 and fresh[("C02_S_TO_D",scope,"normalized_position")]>.1))
    checks.append(("dy_signal",effects[("C03_BARE_TO_DY",scope,"normalized_position")]>.15 and effects[("C03_BARE_TO_DY",scope,"line_final")]>.20 and fresh[("C03_BARE_TO_DY",scope,"line_final")]<.01 and float(stored[("C03_BARE_TO_DY",scope,"line_final")]["search_adjusted_p_20_primary_tests"])<=.0011))
    checks.append(("sy_insufficient",effects[("C04_BARE_TO_SY",scope,"line_final")]>.40 and int(stored[("C04_BARE_TO_SY",scope,"line_final")]["matched_strata"])==2 and fresh[("C04_BARE_TO_SY",scope,"line_final")]>.1))
    checks.append(("dal_dar_lead_only",effects[("C05_DAL_TO_DAR",scope,"normalized_position")]>.15 and fresh[("C05_DAL_TO_DAR",scope,"normalized_position")]<.05 and float(stored[("C05_DAL_TO_DAR",scope,"normalized_position")]["search_adjusted_p_20_primary_tests"])>.5))
    checks.append(("lofo_directions",all(float(stored[key]["lofo_same_sign_fraction"])==1 for key in (keys[0],keys[4],keys[5]))))
    checks.append(("five_constraints",len(constraints)==5 and {r["constraint"] for r in constraints}=={"Q_EARLY_SCOPE","D_LATER_THAN_S","DY_COMPLETION","SY_MARKED_TERMINAL","DAR_LATER_CONFIGURATION"}))
    checks.append(("f84_sealed",model["f84r"]=={"opened":False,"joined":False,"scored":False}));checks.append(("ledger",(ROOT/"GDT002_YOLO_LEDGER.tsv").read_text().count("GDT010_CKPT001")==1))
    checks.append(("claim_ceiling",all(x in result["claim_ceiling"].lower() for x in ("module-selected","no sound","translation"))))
    failures=[name for name,ok in checks if not ok];validation={"schema":"GDT010_RECORD_POSITION_VALIDATION_V1","status":"PASS" if not failures else "FAIL","checks":len(checks),"failures":failures,"fresh_permutation_draws_per_key":2000,"fresh_p":{f"{a}:{b}:{c}":p for (a,b,c),p in fresh.items()},"result_sha256":sha(RESULT),"validator_sha256":sha(Path(__file__)),"scope":"Independent group deduplication, host-plus-page matching, eight key effects, lower-resolution fresh permutation checks, search-adjusted decisions, f84 sealing, hashes, and branch ledger. Does not confirm lexical meanings."}
    VALIDATION.write_text(json.dumps(validation,indent=2,sort_keys=True)+"\n");print(json.dumps(validation,sort_keys=True))
    if failures:raise SystemExit(1)


if __name__=="__main__":main()
