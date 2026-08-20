#!/usr/bin/env python3
"""Freeze GDT396 decoder-route eligibility from blind qualification metrics."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import statistics
from collections import defaultdict
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
EXP = ROOT / "experiments/yolo/gdt396_repaired_synthetic_identifiability_voynich_surface"
DEFAULT_METRICS = EXP / ".work/claims/gdt396_qualification_metrics.tsv"
DEFAULT_OUTPUT = EXP / "artifacts/gdt396_decoder_qualification.json"
REPRESENTATION_ORDER = (
    "FULL_GROUP", "HOST_LIKE", "COMPOSITE_STATE", "INFERRED_COMPONENTS",
    "CONSTRUCTION_SPAN", "RECORD_TOPOLOGY", "MULTI_RESOLUTION",
)
ARCHITECTURE_DIRECT = {
    "ORGANIC_EVOLUTION_LIKE", "CLEAN_ENGINEERED_LIKE", "SEMANTICS_LIGHT_LIKE",
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def rows(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def metrics(row: dict) -> dict:
    return json.loads(row["metrics_json"])


SEMANTIC_PROPERTIES = {
    "SEMANTIC_ENTITY_IDENTITY", "CURRENT_PRODUCTIVE_COMPONENT",
    "CURRENT_SHARED_MEANING", "FUNCTION_OPERATOR_CLASS", "SEMANTIC_CATEGORY",
    "PRODUCTIVE_MORPHOLOGY", "TEMPORAL_STATE_GATE", "GENERIC_RELATION",
    "COORDINATOR_RELATION", "ALTERNATIVE_RELATION", "REFERENCE_ANAPHORA",
    "ENTITY_REUSE_ANTECEDENT",
}


def semantic_w10_false_rates(
    data: list[dict], decoder: str, prop: str, representation: str, surface: str,
) -> list[float]:
    """Return the complete five-seed W10 guard or fail closed."""
    if prop not in SEMANTIC_PROPERTIES:
        return []
    selected = [
        row for row in data
        if row["decoder_id"] == decoder and row["property_id"] == prop
        and row["representation_id"] == representation
        and row["surface_id"] == surface and row["world_id"] == "W10"
        and row["method_variant"] == "PRIMARY"
    ]
    if len(selected) != 5 or len({int(row["corpus_seed"]) for row in selected}) != 5:
        raise ValueError(f"incomplete W10 five-seed guard for {decoder}/{prop}/{representation}/{surface}")
    rates = []
    for source in selected:
        detail = metrics(source)
        rate = detail.get("resolved_without_truth_rate", detail.get("positive_prediction_rate"))
        if rate is None:
            raise ValueError(f"missing W10 false-positive rate for {decoder}/{prop}/{representation}/{surface}")
        rates.append(float(rate))
    return rates


def strict_seed_pass(row: dict) -> tuple[bool, float]:
    if row["status"] != "SCORED":
        return False, -math.inf
    value = metrics(row)
    endpoint = row["endpoint"]
    coverage = float(row["coverage"])
    if endpoint in {"PARTITION", "RECORD_PARTITION"}:
        margins = (
            coverage - .80,
            value["nonsingleton_clusters"] - 3,
            .60 - value["singleton_fraction"],
            .75 - value["largest_cluster_fraction"],
            value["cocluster_pair_ratio"] - .25,
            4.0 - value["cocluster_pair_ratio"],
            value["nmi"] - .50,
            value["ari"] - .30,
            value["pair_f1"] - .40,
        )
    elif endpoint == "BINARY":
        # Event status qualification is deliberately stricter than the final
        # confirmation floor and rejects selective one-class solutions.
        margins = (
            coverage - .60,
            value["balanced_accuracy"] - .70,
            value["mcc"] - .30,
            .30 - value["fdr"],
        )
    elif endpoint == "RANKED_TARGET":
        margins = (
            int(row["eligible_n"]) - 30,
            coverage - .60,
            value["mrr"] - .35,
            value["hits1"] - .20,
            value["ndcg5"] - .45,
            value["mrr_gain"] - .10,
        )
        if row["property_id"] == "GENERIC_RELATION":
            margins += (value.get("relation_type_count", 0) - 3,)
    elif endpoint == "SCOPE":
        margins = (
            coverage - .60,
            value["median_iou"] - .50,
            value["exact_rate"] - .25,
            float(row["gain"]) - .10,
        )
    elif endpoint == "MORPHOLOGY":
        margins=(coverage-.60,value["macro_f1"]-.60,value["mean_ap"]-.50,.10-value["current_false_discovery_rate"],value["recurrent_component_count"]-1,float(value["productive_fossil_component_ids_disjoint"])-1,value["proper_substring_fraction"]-.50)
    else:
        return False, -math.inf
    return all(value >= -1e-12 for value in margins), min(margins)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--metrics", type=Path, default=DEFAULT_METRICS)
    ap.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = ap.parse_args()
    data = rows(args.metrics)
    if not data or {row["phase"] for row in data} != {"QUALIFICATION"}:
        raise ValueError("qualification metrics are absent or mixed")

    # route -> world -> seed outcomes
    grouped: dict[tuple, dict[str, list[tuple[bool, float]]]] = defaultdict(lambda: defaultdict(list))
    decoder_family: dict[str, str] = {}
    for row in data:
        if row["endpoint"] == "ARCHITECTURE_BINARY" or row["method_variant"] != "PRIMARY":
            continue
        key = (row["decoder_id"], row["property_id"], row["representation_id"], row["surface_id"])
        grouped[key][row["world_id"]].append(strict_seed_pass(row))
        decoder_family[row["decoder_id"]] = row["method_family"]

    route_rows = []
    route_by_rep: dict[tuple[str, str, str], list[dict]] = defaultdict(list)
    for (decoder, prop, representation, surface), worlds in sorted(grouped.items()):
        world_passes = []
        margins = []
        for world, values in sorted(worlds.items()):
            if len(values) != 5:
                raise ValueError(f"incomplete five-seed route {decoder}/{prop}/{representation}/{surface}/{world}")
            pass_count = sum(flag for flag, _ in values)
            world_pass = pass_count >= 4
            if world != "W10" and world_pass:
                world_passes.append(world)
            margins.extend(margin for flag, margin in values if flag and math.isfinite(margin))
        w10_false_rates=semantic_w10_false_rates(data,decoder,prop,representation,surface)
        w10_ok=not w10_false_rates or max(w10_false_rates)<=.10
        row = {
            "decoder_id": decoder,
            "method_family": decoder_family[decoder],
            "property_id": prop,
            "representation_id": representation,
            "surface_id": surface,
            "meaningful_worlds_passing": world_passes,
            "meaningful_world_pass_count": len(world_passes),
            "median_positive_margin": statistics.median(margins) if margins else None,
            "w10_false_positive_rates": w10_false_rates,
            "w10_veto_pass": w10_ok,
            "route_qualifies_before_representation_freeze": len(world_passes) >= 2 and w10_ok,
        }
        route_rows.append(row)
        route_by_rep[(prop, surface, representation)].append(row)

    # One representation per property and surface, selected without confirmation.
    selections = []
    selected_rep: dict[tuple[str, str], str] = {}
    for prop, surface in sorted({(row["property_id"], row["surface_id"]) for row in route_rows}):
        candidates = []
        for index, representation in enumerate(REPRESENTATION_ORDER):
            entries = route_by_rep.get((prop, surface, representation), [])
            qualifying = [row for row in entries if row["route_qualifies_before_representation_freeze"]]
            margins = [row["median_positive_margin"] for row in qualifying if row["median_positive_margin"] is not None]
            candidates.append((len(qualifying), statistics.median(margins) if margins else -math.inf, -index, representation))
        best = max(candidates)
        selected_rep[(prop, surface)] = best[3]
        selections.append({
            "property_id": prop, "surface_id": surface,
            "representation_id": best[3], "qualified_decoder_count": best[0],
            "selection_margin": None if not math.isfinite(best[1]) else best[1],
        })

    # Decoder-wide qualification suite: easy equality plus at least one
    # recurrent relation route must survive on both surfaces before any of the
    # decoder's property routes can enter confirmation.
    suite={}
    for decoder in sorted({r["decoder_id"] for r in route_rows}):
        lexical=all(any(r["decoder_id"]==decoder and r["property_id"]=="LEXICAL_IDENTITY" and r["surface_id"]==surface and r["route_qualifies_before_representation_freeze"] for r in route_rows) for surface in ("FREE_SURFACE","VOYNICH_SURFACE"))
        relation=all(any(r["decoder_id"]==decoder and r["property_id"] in {"GENERIC_RELATION","ENTITY_REUSE_ANTECEDENT"} and r["surface_id"]==surface and r["route_qualifies_before_representation_freeze"] for r in route_rows) for surface in ("FREE_SURFACE","VOYNICH_SURFACE"))
        suite[decoder]={"easy_equality":lexical,"simple_recurrent_relation":relation,"schema_and_determinism":True,"qualified":lexical and relation}
    qualified_routes = []
    for row in route_rows:
        selected = selected_rep[(row["property_id"], row["surface_id"])] == row["representation_id"]
        row["selected_representation"] = selected
        row["decoder_suite_pass"] = suite[row["decoder_id"]]["qualified"]
        row["qualified"] = bool(selected and row["route_qualifies_before_representation_freeze"] and row["decoder_suite_pass"])
        if row["qualified"]:
            qualified_routes.append({key: row[key] for key in (
                "decoder_id", "method_family", "property_id", "representation_id",
                "surface_id", "meaningful_worlds_passing",
            )})

    panels = []
    for prop, surface in sorted(selected_rep):
        routes = [r for r in qualified_routes if r["property_id"] == prop and r["surface_id"] == surface]
        families = sorted({r["method_family"] for r in routes})
        panels.append({
            "property_id": prop, "surface_id": surface,
            "representation_id": selected_rep[(prop, surface)],
            "qualified_decoders": sorted(r["decoder_id"] for r in routes),
            "method_families": families,
            "confirmation_eligible": len(routes) >= 3 and len(families) >= 2,
        })

    # Direct architecture qualification is cross-world by seed. It remains a
    # panel diagnostic and never substitutes for property-route qualification.
    architecture = []
    arch_groups = defaultdict(list)
    for row in data:
        if row["endpoint"] == "ARCHITECTURE_BINARY" and row["property_id"] in ARCHITECTURE_DIRECT and row["status"]=="SCORED":
            key = (row["decoder_id"], row["method_family"], row["property_id"], row["surface_id"], row["representation_id"], row["method_variant"], int(row["corpus_seed"]))
            arch_groups[key].append(row)
    for key, values in sorted(arch_groups.items()):
        decoder, family, prop, surface, representation, variant, seed = key
        if len(values) != 10:
            raise ValueError(f"incomplete architecture world panel: {key}")
        truth = [json.loads(r["metrics_json"])["truth_bool"] for r in values]
        pred = [json.loads(r["metrics_json"])["predicted_bool"] for r in values]
        tp=sum(t and p for t,p in zip(truth,pred));tn=sum((not t) and (not p) for t,p in zip(truth,pred));fp=sum((not t) and p for t,p in zip(truth,pred));fn=sum(t and (not p) for t,p in zip(truth,pred))
        tpr=tp/(tp+fn) if tp+fn else 0.0;tnr=tn/(tn+fp) if tn+fp else 0.0
        denom=math.sqrt((tp+fp)*(tp+fn)*(tn+fp)*(tn+fn));mcc=(tp*tn-fp*fn)/denom if denom else 0.0
        architecture.append({
            "decoder_id":decoder,"method_family":family,"property_id":prop,"surface_id":surface,
            "representation_id":representation,"method_variant":variant,"corpus_seed":seed,
            "balanced_accuracy":.5*(tpr+tnr),"mcc":mcc,"false_positive_rate":fp/(fp+tn) if fp+tn else 0.0,
        })
    arch_index={(r["decoder_id"],r["surface_id"],r["representation_id"],r["property_id"],r["corpus_seed"],r["method_variant"]):r for r in architecture}
    architecture_qualification=[]
    for decoder,surface,representation in sorted({(r["decoder_id"],r["surface_id"],r["representation_id"]) for r in architecture if r["property_id"]=="SEMANTICS_LIGHT_LIKE"}):
        seed_rows=[]
        for seed in sorted({r["corpus_seed"] for r in architecture}):
            multi=arch_index.get((decoder,surface,representation,"SEMANTICS_LIGHT_LIKE",seed,"MULTI_CONSTRAINT"));scalar=arch_index.get((decoder,surface,representation,"SEMANTICS_LIGHT_LIKE",seed,"SCALAR_BOTTLENECK"))
            if not multi or not scalar:continue
            lead=multi["balanced_accuracy"]-scalar["balanced_accuracy"];passed=multi["balanced_accuracy"]>=.70 and multi["mcc"]>=.35 and multi["false_positive_rate"]<=.10 and lead>=.10
            seed_rows.append({"corpus_seed":seed,"multi_balanced_accuracy":multi["balanced_accuracy"],"multi_mcc":multi["mcc"],"multi_false_positive_rate":multi["false_positive_rate"],"scalar_balanced_accuracy":scalar["balanced_accuracy"],"balanced_accuracy_lead":lead,"pass":passed})
        architecture_qualification.append({"decoder_id":decoder,"surface_id":surface,"representation_id":representation,"seed_rows":seed_rows,"qualified":len(seed_rows)==5 and sum(r["pass"] for r in seed_rows)>=4})

    # Matched event-level multi-constraint versus scalar function partition.
    variant_cells=defaultdict(dict)
    for row in data:
        if row["property_id"]=="FUNCTION_OPERATOR_CLASS" and row["representation_id"]=="MULTI_RESOLUTION" and row["method_variant"] in {"MULTI_CONSTRAINT","SCALAR_BOTTLENECK"}:
            variant_cells[(row["decoder_id"],row["method_family"],row["world_id"],row["surface_id"],int(row["corpus_seed"]))][row["method_variant"]]=row
    function_multiconstraint=[];by_decoder_surface=defaultdict(lambda:defaultdict(list))
    for key,cell in sorted(variant_cells.items()):
        decoder,family,world,surface,seed=key
        if set(cell)!={"MULTI_CONSTRAINT","SCALAR_BOTTLENECK"}:continue
        multi=cell["MULTI_CONSTRAINT"];scalar=cell["SCALAR_BOTTLENECK"];m_pass,m_margin=strict_seed_pass(multi);lead=(float(multi["primary_value"])-float(scalar["primary_value"])) if multi["primary_value"]!="NA" and scalar["primary_value"]!="NA" else -math.inf
        row={"decoder_id":decoder,"method_family":family,"world_id":world,"surface_id":surface,"corpus_seed":seed,"multi_strict_pass":m_pass,"pair_f1_lead":None if not math.isfinite(lead) else lead,"seed_pass":m_pass and lead>=.10}
        function_multiconstraint.append(row);by_decoder_surface[(decoder,surface)][world].append(row["seed_pass"])
    multiconstraint_routes=[]
    for (decoder,surface),worlds in sorted(by_decoder_surface.items()):
        passing=[world for world,flags in worlds.items() if world!="W10" and len(flags)==5 and sum(flags)>=4]
        multiconstraint_routes.append({"decoder_id":decoder,"surface_id":surface,"worlds_passing":passing,"qualified":len(passing)>=2})

    output = {
        "schema": "GDT396_DECODER_QUALIFICATION_V1",
        "status": "PASS" if any(row["confirmation_eligible"] for row in panels if row["surface_id"] == "VOYNICH_SURFACE") else "NO_CONFIRMATION_ELIGIBLE_PROPERTY",
        "metrics_sha256": sha256(args.metrics),
        "seed_count": 5,
        "route_rows": route_rows,
        "representation_selections": selections,
        "qualified_routes": qualified_routes,
        "confirmation_panels": panels,
        "architecture_diagnostics": architecture,
        "architecture_qualification": architecture_qualification,
        "function_multiconstraint_seed_diagnostics": function_multiconstraint,
        "function_multiconstraint_routes": multiconstraint_routes,
        "decoder_wide_suite": suite,
        "f84": {"accessed": False, "rows": 0},
        "f84r": {"accessed": False, "rows": 0},
    }
    content = dict(output); content.pop("content_sha256", None)
    output["content_sha256"] = hashlib.sha256(json.dumps(content, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    args.output.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(args.output, output["status"], len(qualified_routes), sha256(args.output))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
