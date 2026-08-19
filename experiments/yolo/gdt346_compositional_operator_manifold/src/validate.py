#!/usr/bin/env python3
"""Independent source/accounting validator for GDT346; does not import scorer."""

from __future__ import annotations

import csv
import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path


def find_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists(): return candidate
    raise RuntimeError("repository root not found")


ROOT = find_root(Path(__file__).resolve())
import sys
sys.path.insert(0, str(ROOT))
from tools.vmanus_experiment import GuardedTSV  # noqa: E402

EXP = ROOT / "experiments/yolo/gdt346_compositional_operator_manifold"; ART = EXP / "artifacts"
G345 = ROOT / "experiments/yolo/gdt345_productive_operator_transfer/artifacts/gdt345_transition_inventory.tsv"
DESIGN = ART / "gdt346_design.json"; GRAPH = ART / "gdt346_graph_edges.tsv"; FOLDS = ART / "gdt346_folds.tsv"; TRANSFER = ART / "gdt346_transfer.tsv"; PRED = ART / "gdt346_predictions.tsv"; MODELS = ART / "gdt346_models.tsv"; NULL = ART / "gdt346_null.tsv"; HERBAL = ART / "gdt346_herbal_a.tsv"; RESULT = ART / "gdt346_result.json"; VALIDATION = ART / "gdt346_validation.json"
MODEL_NAMES = ("PLACEMENT","EXACT_PREDECESSOR","SOURCE_STATE_TABLE","INDEPENDENT_MARGINAL","PAIR_GRAPH_NONWRAPPER","PAIR_GRAPH_FULL","EXACT_OPERATOR_LEXICON")


def read(path: Path) -> list[dict[str,str]]:
    with path.open(encoding="utf-8",newline="") as h: return list(csv.DictReader(h,delimiter="\t"))


def sha(path: Path) -> str:
    d=hashlib.sha256()
    with path.open("rb") as h:
        for chunk in iter(lambda:h.read(1<<20),b""): d.update(chunk)
    return d.hexdigest()


def canonical(x: object) -> bytes: return (json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(",",":"))+"\n").encode()
def content_hash(x: dict[str,object]) -> str:
    y=dict(x);y.pop("content_sha256",None);return hashlib.sha256(canonical(y)).hexdigest()


def main() -> int:
    checks=[]
    def check(name,ok,detail=""):
        checks.append({"check":name,"pass":bool(ok),"detail":str(detail)})
        if not ok: raise AssertionError(f"{name}: {detail}")
    design=json.loads(DESIGN.read_text());result=json.loads(RESULT.read_text())
    reader=GuardedTSV(G345,selector_column="page",forbidden_prefixes=("f84",),forbidden_action="error"); source=list(reader)
    check("source_events",len(source)==8268,len(source));check("source_folios",len({r['physical_folio'] for r in source})==91);check("source_pages",len({r['page'] for r in source})==180);check("source_no_f84",not any(r['page'].startswith('f84') for r in source))
    parsed=[];bad_apply=0
    for r in source:
        s=tuple(json.loads(r['source_state_json']));t=tuple(json.loads(r['target_state_json']));d=tuple(json.loads(r['delta_json']));bad_apply+=int(tuple(a if x=='KEEP' else x[4:] for a,x in zip(s,d))!=t);parsed.append({"folio":r['physical_folio'],"state":r['source_state_id'],"op":r['operator_id'],"s":s,"d":d})
    check("all_deltas_apply",bad_apply==0,bad_apply);check("state_width",all(len(r['s'])==len(r['d'])==6 for r in parsed))
    decisive=0
    for hold in sorted({r['folio'] for r in parsed}):
        tr=[r for r in parsed if r['folio']!=hold];te=[r for r in parsed if r['folio']==hold];states={r['state'] for r in tr};ops={r['op'] for r in tr};combos={(r['state'],r['op']) for r in tr};component=[{(r['s'][i],r['d'][i]) for r in tr} for i in range(6)]
        decisive+=sum(r['state'] in states and r['op'] in ops and (r['state'],r['op']) not in combos and all((r['s'][i],r['d'][i]) in component[i] for i in range(6)) for r in te)
    check("decisive_capacity",decisive==1027,decisive)

    graph=read(GRAPH);folds=read(FOLDS);transfer=read(TRANSFER);pred=read(PRED);models=read(MODELS);null=read(NULL);herbal=read(HERBAL)
    check("graph_pairs",all(0<=int(r['pair_id'].split('-')[0])<int(r['pair_id'].split('-')[1])<6 for r in graph));check("graph_unassigned",all(r['semantic_state']=='UNASSIGNED' for r in graph))
    for tag in sorted({r['fold_tag'] for r in graph}): check(f"graph_max3:{tag}",sum(int(r['selected']) for r in graph if r['fold_tag']==tag)<=3)
    check("fold_rows",len(folds)==91*len(MODEL_NAMES),len(folds));check("fold_models",{r['model'] for r in folds}==set(MODEL_NAMES));check("model_rows",{r['model'] for r in models}==set(MODEL_NAMES))
    by={r['model']:r for r in models}
    for model in MODEL_NAMES:
        rows=[r for r in folds if r['model']==model];check(f"folds:{model}",len(rows)==91);check(f"n:{model}",sum(int(r['decisive_events']) for r in rows)==int(by[model]['decisive_events']));check(f"bits:{model}",math.isclose(sum(float(r['decisive_bits']) for r in rows),float(by[model]['decisive_bits']),abs_tol=3e-6));check(f"paid:{model}",math.isclose(sum(float(r['decisive_selector_paid_bits']) for r in rows),float(by[model]['decisive_selector_paid_bits']),abs_tol=3e-6));check(f"rank:{model}",math.isclose(sum(int(r['rank_sum']) for r in rows)/max(1,int(by[model]['decisive_events'])),float(by[model]['mean_rank']),abs_tol=2e-9));check(f"top:{model}",sum(int(r['top1']) for r in rows)==int(by[model]['top1']) and sum(int(r['top5']) for r in rows)==int(by[model]['top5']))
    check("prediction_rows",len(pred)==1027*len(MODEL_NAMES),len(pred));check("prediction_models",Counter(r['model'] for r in pred)==Counter({m:1027 for m in MODEL_NAMES}));check("prediction_rank",all(int(r['true_operator_rank'])>=1 and int(r['top1'])==int(int(r['true_operator_rank'])==1) and int(r['top5'])==int(int(r['true_operator_rank'])<=5) for r in pred))
    check("transfer_split_models",all({r['model'] for r in transfer if r['split']==s}==set(MODEL_NAMES) for s in ('SECTION','REGISTER','HAND')))
    check("null_worlds",len(null)==int(design['null']['worlds']))
    full=by['PAIR_GRAPH_FULL'];non=by['PAIR_GRAPH_NONWRAPPER'];base=by['INDEPENDENT_MARGINAL'];obsfull=float(base['decisive_bits'])-float(full['decisive_bits']);obsnon=float(base['decisive_bits'])-float(non['decisive_bits'])
    # TSV values are rounded to nine decimals; 1e-10 retains the scorer's
    # inclusive comparison without admitting a distinct value 4e-9 below it.
    pfull=(1+sum(float(r['full_gain'])>=obsfull-1e-10 for r in null))/(1+len(null));pnon=(1+sum(float(r['nonwrapper_gain'])>=obsnon-1e-10 for r in null))/(1+len(null));pmax=(1+sum(float(r['max_two_gain'])>=max(obsfull,obsnon)-1e-10 for r in null))/(1+len(null))
    check("null_p_full",math.isclose(pfull,float(full['inclusive_p']),abs_tol=5e-10),(pfull,full['inclusive_p']));check("null_p_non",math.isclose(pnon,float(non['inclusive_p']),abs_tol=5e-10));check("null_p_max",math.isclose(pmax,float(full['max_two_p']),abs_tol=5e-10))
    check("herbal_rows",len(herbal)>0 and {r['model'] for r in herbal}=={'INDEPENDENT','FOREIGN_GRAPH','LOCAL_GRAPH'});check("result_source",result['source']=={'events':8268,'folios':91,'pages':180});check("zero_semantics",result['semantic_alignments']==result['tuple_merges']==result['page_host_factorizations']==0);check("f84_flags",all(v is False for v in result['f84'].values()))
    for p,d in result['inputs'].items():check(f"input_hash:{p}",sha(ROOT/p)==d)
    for p,d in result['outputs'].items():check(f"output_hash:{p}",sha(ROOT/p)==d)
    for p,d in result['implementation'].items():check(f"implementation_hash:{p}",sha(ROOT/p)==d)
    check("result_content_hash",content_hash(result)==result['content_sha256'])
    validation={"schema":"GDT346_VALIDATION_V1","status":"PASS","checks_passed":len(checks),"checks_failed":0,"result_sha256":sha(RESULT),"source_reconstruction":{"events":len(source),"folios":91,"pages":180,"decisive":decisive},"scope":"Independent guarded GDT345 source/delta/capacity reconstruction; graph sparsity, fold/aggregate/rank/null/Herbal/accounting, semantic-zero, f84 and hashes. Marginal fits, pair potentials and nested edge-selection gains are not independently refit.","checks":checks};validation['content_sha256']=content_hash(validation);VALIDATION.write_bytes(canonical(validation));print(f"PASS {len(checks)}/{len(checks)} {result['status']}");return 0


if __name__=='__main__':raise SystemExit(main())
