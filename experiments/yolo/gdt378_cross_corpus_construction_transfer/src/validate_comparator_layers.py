#!/usr/bin/env python3
"""Validate the frozen form-blind GDT378 comparator layers."""
from __future__ import annotations
import csv, gzip, hashlib, json, re
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4]
BASE=ROOT/"experiments/yolo/gdt378_cross_corpus_construction_transfer";ART=BASE/"artifacts"
def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def rows(p:Path):
    opener=gzip.open if p.suffix==".gz" else open
    with opener(p,"rt",encoding="utf-8",newline="") as h:return list(csv.DictReader(h,delimiter="\t"))
def main():
    design_path=ART/"gdt378_comparator_design_freeze.json";d=json.loads(design_path.read_text())
    obs=rows(ART/"gdt378_comparator_observation_layer.tsv.gz");oracle=rows(ART/"gdt378_hidden_oracle.tsv.gz");coverage=rows(ART/"gdt378_endpoint_coverage.tsv")
    domains=Counter(r["domain"] for r in obs);records={(r["domain"],r["collection_id"],r["record_id"]) for r in obs}
    forbidden={"surface","word","translation","pos","parse","role","concept_id","function_label","parent_link","host_id","page_host"}
    expected={"COREMA":27349,"PCEEC2":27518,"CURIOUS_CURES":21817,"HARLEIAN_COOKERY":40826,"QUINTE_ESSENCE":15673}
    head=Counter()
    for r in oracle:head[r["domain"]]+=int(r["HEAD_WITH_DEPENDENTS"])
    payload=dict(d);expected_hash=payload.pop("content_hash")
    checks={
      "status":d["status"]=="FORM_BLIND_LAYERS_FROZEN_BEFORE_SCORING",
      "rows":len(obs)==len(oracle)==d["rows"]==133183,
      "records":len(records)==d["records"]==3235,
      "domain_counts":dict(domains)==expected,
      "key_alignment":[r["element_key"] for r in obs]==[r["element_key"] for r in oracle],
      "unique_keys":len({r["element_key"] for r in obs})==len(obs),
      "blind_schema":not(forbidden&set(obs[0])),
      "opaque_ids":all(re.fullmatch(r"[0-9a-f]{24}",r["opaque_form_id"]) is not None for r in obs),
      "positions":all(0<float(r["relative_position"])<=1 for r in obs),
      "boundaries":all(r["boundary_before"] in {"0","1"} and r["boundary_after"] in {"0","1"} for r in obs),
      "curious_pages":len({r["physical_page"] for r in obs if r["domain"]=="CURIOUS_CURES"})==183,
      "pceec_collections":len({r["collection_id"] for r in obs if r["domain"]=="PCEEC2"})==84,
      "harleian_books":{r["collection_id"] for r in obs if r["domain"]=="HARLEIAN_COOKERY"}=={"HARL279","HARL4016"},
      "head_counts":dict(head)=={"COREMA":7315,"PCEEC2":3225,"CURIOUS_CURES":1139,"HARLEIAN_COOKERY":4472,"QUINTE_ESSENCE":438},
      "coverage_rows":len(coverage)==5*13,
      "corema_gold":all(r["oracle_strength"]=="GOLD" for r in coverage if r["domain"]=="COREMA"),
      "procedural_oracle_disclosed":all(r["oracle_strength"]=="HIGH_PRECISION_LEXICAL" for r in coverage if r["domain"] in {"CURIOUS_CURES","HARLEIAN_COOKERY","QUINTE_ESSENCE"}),
      "output_hashes":all(sha(ROOT/p)==v for p,v in d["outputs"].items()),
      "implementation_hash":all(sha(ROOT/p)==v for p,v in d["implementation"].items()),
      "content_hash":hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(",",":")).encode()).hexdigest()==expected_hash,
      "no_voynich":not d["voynich_scored"] and d["voynich_rows_read"]==0,
      "f84_sealed":not any(d["f84"].values()) and not any("f84" in r["element_key"].lower() for r in obs),
    }
    out={"schema":"GDT378_COMPARATOR_LAYER_VALIDATION_V1","status":"PASS" if all(checks.values()) else "FAIL","checks":checks,"checks_passed":sum(checks.values()),"checks_total":len(checks),"design_sha256":sha(design_path)}
    (ART/"gdt378_comparator_design_validation.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(out["status"],f'{out["checks_passed"]}/{out["checks_total"]}')
    if out["status"]!="PASS":raise SystemExit(1)
if __name__=="__main__":main()
