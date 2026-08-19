#!/usr/bin/env python3
"""Freeze one Voynich-derived GDT346 graph before GDT278 control scoring."""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import math
from collections import Counter, defaultdict
from pathlib import Path


def root(start: Path) -> Path:
    for p in (start, *start.parents):
        if (p / "AGENTS.md").is_file() and (p / ".git").exists(): return p
    raise RuntimeError("root")


ROOT = root(Path(__file__).resolve()); EXP = ROOT / "experiments/yolo/gdt347_fixed_graph_control_transport"; ART = EXP / "artifacts"
DESIGN = ART / "gdt347_design.json"; FROZEN = ART / "gdt347_frozen_graph.json"; CAPACITY = ART / "gdt347_control_capacity.tsv"
G345 = ROOT / "experiments/yolo/gdt345_productive_operator_transfer/artifacts/gdt345_transition_inventory.tsv"
G346_EDGES = ROOT / "experiments/yolo/gdt346_compositional_operator_manifold/artifacts/gdt346_graph_edges.tsv"
G346_DESIGN = ROOT / "experiments/yolo/gdt346_compositional_operator_manifold/artifacts/gdt346_design.json"
G346_RESULT = ROOT / "experiments/yolo/gdt346_compositional_operator_manifold/artifacts/gdt346_result.json"
NATIVE = ROOT / "gdt278_native_event_inventory.tsv"; MATCHED = ROOT / "gdt278_matched_event_inventory.tsv"; MANIFEST = ROOT / "gdt278_control_manifest.tsv"


def sha(p: Path) -> str:
    h=hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda:f.read(1<<20),b""):h.update(b)
    return h.hexdigest()


def canonical(x: object) -> bytes: return (json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(",",":"))+"\n").encode()
def chash(x: dict) -> str:
    y=dict(x);y.pop("content_sha256",None);return hashlib.sha256(canonical(y)).hexdigest()


def load346():
    p=ROOT/"experiments/yolo/gdt346_compositional_operator_manifold/src/run.py"
    spec=importlib.util.spec_from_file_location("gdt346_freeze_dependency",p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    return m


def read(p: Path):
    with p.open(encoding="utf-8",newline="") as f:return list(csv.DictReader(f,delimiter="\t"))


def write_tsv(p: Path, rows: list[dict]):
    with p.open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,list(rows[0]),delimiter="\t",lineterminator="\n");w.writeheader();w.writerows(rows)


def main() -> int:
    ART.mkdir(parents=True,exist_ok=True); design=json.loads(DESIGN.read_text()); g=load346(); edges=g.load_edges()
    graph=read(G346_EDGES); primary=[r for r in graph if r["fold_tag"].startswith("PHYSICAL_FOLIO:")]
    folds=len({r["fold_tag"] for r in primary}); selected=Counter(r["pair_id"] for r in primary if r["selected"]=="1")
    eligible=[(pair,n) for pair,n in selected.items() if n/folds>=float(design["topology"]["minimum_fold_fraction"])]
    eligible.sort(key=lambda x:(-x[1],tuple(map(int,x[0].split("-")))))
    selected_pairs=[tuple(map(int,pair.split("-"))) for pair,_ in eligible[:int(design["topology"]["maximum_edges"])]]
    if selected_pairs != [(1,5),(3,5),(2,3)]: raise AssertionError(selected_pairs)

    folio_register={str(e["physical_folio"]):str(e["register"]) for e in edges}; held=[]
    for reg in sorted(set(folio_register.values())):
        fs=[f for f,v in folio_register.items() if v==reg]
        fs.sort(key=lambda f:hashlib.sha256((design["voynich_split"]["salt"]+"\0"+reg+"\0"+f).encode()).hexdigest())
        held.extend(fs[:max(1,round(float(design["voynich_split"]["held_fraction"])*len(fs)))])
    held=sorted(held); train=[e for e in edges if e["physical_folio"] not in held]; test=[e for e in edges if e["physical_folio"] in held]
    tables=g.build_tables(train,"INDEPENDENT_MARGINAL",json.loads(G346_DESIGN.read_text()))
    potentials={p:g.fit_potential(train,p,tables,json.loads(G346_DESIGN.read_text())) for p in selected_pairs}
    weight_rows=[]
    for pair in selected_pairs:
        for (scope,da,db),factor in sorted(potentials[pair].items()):
            weight_rows.append({"pair_id":f"{pair[0]}-{pair[1]}","coordinate_a":g.COMP[pair[0]],"coordinate_b":g.COMP[pair[1]],"scope":scope,"delta_a":da,"delta_b":db,"factor":format(factor,".17g")})

    capacities=[]
    labels={r["control_id"]:r for r in read(MANIFEST)}
    for view,path in (("NATIVE",NATIVE),("MATCHED",MATCHED)):
        rows=[r for r in read(path) if not r["page"].startswith("f84") and not r["locus"].startswith("f84")]
        grouped=defaultdict(list)
        for r in rows: grouped[(r["control_id"],r["page"],r["physical_folio"])].append(r)
        by=defaultdict(list)
        for r in rows:by[r["control_id"]].append(r)
        for cid,rs in sorted(by.items()):
            if cid.startswith("VOYNICH_"):continue
            units={(r["page"],r["physical_folio"]) for r in rs};transitions=sum(max(0,len(grouped[(cid,p,f)])-1) for p,f in units)
            meta=labels[cid]
            capacities.append({"view":view,"control_id":cid,"architecture_category":meta["architecture_category"],"groups":len(rs),"transitions":transitions,"folios":len({r["physical_folio"] for r in rs}),"pages":len({r["page"] for r in rs}),"wrapper_values":len({r["wrapper"] for r in rs}),"frame_values":len({r["local_frame"] for r in rs}),"right_values":len({r["right_family"] for r in rs}),"dy_values":len({r["dy_closure"] for r in rs}),"b3_values":len({r["b3"] for r in rs}),"dy_positive":sum(r["dy_closure"]=="1" for r in rs),"pre_score_state":"CAPACITY_ONLY"})
    write_tsv(CAPACITY,capacities)
    frozen={"schema":"GDT347_FROZEN_GRAPH_V1","date":"2026-08-19","status":"FROZEN_BEFORE_CONTROL_SCORING","coordinates":list(g.COMP),"topology":[{"pair_id":f"{a}-{b}","coordinate_a":g.COMP[a],"coordinate_b":g.COMP[b],"gdt346_selected_folds":selected[f"{a}-{b}"],"gdt346_total_folds":folds} for a,b in selected_pairs],"selector_bits_once":math.log2(math.comb(15,len(selected_pairs))),"voynich_partition":{"train_folios":sorted(set(folio_register)-set(held)),"held_folios":held,"train_edges":len(train),"held_edges":len(test),"method":design["voynich_split"]},"potential_weights":weight_rows,"unknown_cell_factor":1.0,"marginal_policy":"CONTROL_LOFO_WITH_FROZEN_GDT345_SMOOTHING","inputs":{str(p.relative_to(ROOT)):sha(p) for p in (DESIGN,G345,G346_EDGES,G346_DESIGN,G346_RESULT,NATIVE,MATCHED,MANIFEST)},"f84":{"opened":False,"parsed":False,"retained":False,"scored":False},"semantic_state":"UNASSIGNED"}
    frozen["content_sha256"]=chash(frozen);FROZEN.write_bytes(canonical(frozen));print(f"FROZEN edges={len(selected_pairs)} train={len(train)} held={len(test)} weights={len(weight_rows)} controls={len(capacities)}")
    return 0


if __name__=="__main__":raise SystemExit(main())
