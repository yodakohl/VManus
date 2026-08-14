#!/usr/bin/env python3
"""Independent reconstruction validator for GDT011 field layers."""

from __future__ import annotations

import csv
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parent;RESULT=ROOT/"gdt011_result.json";VALIDATION=ROOT/"gdt011_validation.json"
PREFIXES=("t","s","d","q","ch","sh","che","o","ot")


def sha(path:Path)->str:return hashlib.sha256(path.read_bytes()).hexdigest()
def canonical_sha(value:object)->str:return hashlib.sha256(json.dumps(value,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def read_tsv(name:str)->list[dict[str,str]]:
    with (ROOT/name).open(encoding="utf-8",newline="") as h:return list(csv.DictReader(h,delimiter="\t"))
def tagged(value:str,key:str)->str:
    for part in value.split(";"):
        if part.startswith(key+":"):return part.split(":",1)[1]
    return ""


def groups(source:list[dict[str,str]])->list[dict[str,object]]:
    out={}
    for row in source:
        key=(row["locus"],row["source_group_index"])
        if key in out or not row["ZL3b_token"] or not(row["ZL3b_token"]==row["IT2a_token"]==row["RF1b_token"]):continue
        n=int(tagged(row["source_group_count_by_reading"],"ZL3b"));i=int(row["source_group_index"])
        out[key]={"token":row["ZL3b_token"],"position":(i-1)/(n-1)if n>1 else .5,"initial":int(i==1),"final":int(i==n),"nonprose":int(row["layout_role"]!="RUNNING_TEXT"),"page":row["page"],"locus":row["locus"],"index":i}
    return list(out.values())


def operation_maps(items:list[dict[str,object]])->dict[str,tuple[dict,dict]]:
    tokens=defaultdict(list)
    for row in items:tokens[row["token"]].append(row)
    out={}
    for prefix in PREFIXES:
        a,b=defaultdict(list),defaultdict(list)
        for token,rows in tokens.items():(b[token[len(prefix):]] if token.startswith(prefix)and len(token)>len(prefix) else a[token]).extend(rows)
        out[prefix.upper()+"_PREPEND"]=(a,b)
    suffix,bare=defaultdict(list),defaultdict(list)
    for token,rows in tokens.items():
        if token.endswith("dy")and len(token)>2:suffix[token[:-2]].extend(rows)
        elif not any(token.endswith(x)and len(token)>len(x)for x in ("dal","dar","sy")):bare[token].extend(rows)
    out["DY_APPEND"]=(bare,suffix);return out


def page_strata(a:dict,b:dict)->list[tuple[list[dict],list[dict]]]:
    out=[]
    for host in set(a)&set(b):
        av,bv=defaultdict(list),defaultdict(list)
        for row in a[host]:av[row["page"]].append(row)
        for row in b[host]:bv[row["page"]].append(row)
        out.extend((av[p],bv[p])for p in set(av)&set(bv))
    return out


def effect(parts:list[tuple[list[dict],list[dict]]],metric:str)->float:
    num=den=0.
    for a,b in parts:
        w=len(a)*len(b)/(len(a)+len(b));num+=w*(sum(float(x[metric])for x in b)/len(b)-sum(float(x[metric])for x in a)/len(a));den+=w
    return num/den


def exact_binomial(success:int,total:int)->float:
    d=abs(success-total/2);return sum(math.comb(total,k)for k in range(total+1)if abs(k-total/2)>=d-1e-12)/(2**total)


def main()->None:
    checks=[];result=json.loads(RESULT.read_text());norm=dict(result);recorded=norm.pop("result_content_sha256")
    checks.extend([("schema",result["schema"]=="GDT011_FIELD_LAYER_RESULT_V1"),("content_hash",recorded==canonical_sha(norm))])
    for section in("inputs","implementation","outputs"):
        for name,digest in result[section].items():checks.append((f"{section}:{name}",sha(ROOT/name)==digest))
    source=read_tsv("gdt002_morphology_occurrences.tsv");items=groups(source);tests=read_tsv("gdt011_operation_position_tests.tsv");layers=read_tsv("gdt011_recovered_layers.tsv");rects=read_tsv("gdt011_q_dy_rectangles.tsv");interaction=json.loads((ROOT/"gdt011_q_dy_interaction.json").read_text());model=json.loads((ROOT/"gdt011_field_layer_model.json").read_text())
    checks.extend([("no_f84",not any(r["locus"].startswith("f84r")for r in source)),("group_count",len(items)==result["groups"]==10890),("test_grid",len(tests)==40 and len({(r["operation"],r["metric"])for r in tests})==40)])
    stored={(r["operation"],r["metric"]):r for r in tests};maps=operation_maps(items);metric_map={"normalized_position":"position","line_initial":"initial","line_final":"final","nonprose":"nonprose"}
    for operation,(a,b) in maps.items():
        parts=page_strata(a,b)
        for external,internal in metric_map.items():
            value=effect(parts,internal);row=stored[(operation,external)]
            checks.append((f"effect:{operation}:{external}",abs(value-float(row["effect_marked_minus_bare"]))<5e-13 and len(parts)==int(row["host_page_strata"])))
            checks.append((f"adjustment:{operation}:{external}",abs(float(row["search_adjusted_p_40"])-min(1.,40*float(row["local_p"])))<5e-7))
    layer_map={r["operation"]:r["recovered_layer"]for r in layers};expected={"T_PREPEND":"ENTRY","S_PREPEND":"ENTRY","D_PREPEND":"ENTRY","Q_PREPEND":"EARLY_CARRIER","CH_PREPEND":"EARLY_CARRIER","SH_PREPEND":"EARLY_CARRIER","CHE_PREPEND":"EARLY_CARRIER","O_PREPEND":"LOCAL_OR_UNRESOLVED","OT_PREPEND":"LOCAL_OR_UNRESOLVED","DY_APPEND":"CLOSURE"}
    checks.extend([("layers",layer_map==expected==result["layers"]),("model_layers",model["recovered_layers"]==expected),("f84_sealed",model["f84r"]=={"opened":False,"joined":False,"scored":False})])
    by_token=defaultdict(list)
    for row in items:by_token[row["token"]].append(row)
    hosts=[h for h in by_token if not h.startswith("q")and not h.endswith("dy")and all(x in by_token for x in(h,"q"+h,h+"dy","q"+h+"dy"))]
    checks.append(("global_rectangles",len(hosts)==len(rects)==interaction["global_complete_hosts"]==6));checks.append(("zero_page_rectangles",sum(int(r["same_page_complete"])for r in rects)==interaction["same_page_complete_rectangles"]==0))
    byline=defaultdict(list)
    for row in items:byline[row["locus"]].append(row)
    earlier=later=tie=eligible=0
    for rows in byline.values():
        q=[r for r in rows if r["token"].startswith("q")and not r["token"].endswith("dy")];d=[r for r in rows if r["token"].endswith("dy")and not r["token"].startswith("q")]
        if not q or not d:continue
        eligible+=1;mq=sum(r["position"]for r in q)/len(q);md=sum(r["position"]for r in d)/len(d);earlier+=mq<md;later+=mq>md;tie+=mq==md
    checks.append(("line_order",(eligible,earlier,later,tie)==(419,200,201,18)and abs(exact_binomial(earlier,earlier+later)-interaction["two_sided_line_binomial_p"])<1e-15))
    checks.append(("field_not_line",interaction["decision"]==result["interaction_decision"]=="FIELD_EDGE_AXES_NOT_WHOLE_LINE_BRACKETS"));checks.append(("ledger",(ROOT/"GDT002_YOLO_LEDGER.tsv").read_text().count("GDT011_CKPT001")==1));checks.append(("claim_ceiling",all(x in result["claim_ceiling"].lower()for x in("distributional","no confirmed language","translation"))))
    failures=[name for name,ok in checks if not ok];validation={"schema":"GDT011_FIELD_LAYER_VALIDATION_V1","status":"PASS"if not failures else"FAIL","checks":len(checks),"failures":failures,"result_sha256":sha(RESULT),"validator_sha256":sha(Path(__file__)),"scope":"Independent exact-group reconstruction, 40 host-page effects and search adjustments, recovered layers, q/DY rectangles, line-order falsifier, f84 sealing, hashes, and ledger. Does not confirm lexical meanings."}
    VALIDATION.write_text(json.dumps(validation,indent=2,sort_keys=True)+"\n");print(json.dumps(validation,sort_keys=True))
    if failures:raise SystemExit(1)


if __name__=="__main__":main()
