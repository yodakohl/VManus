#!/usr/bin/env python3
"""Score one GDT396 blind decoder phase against direct synthetic truth."""

from __future__ import annotations

import argparse
import csv
import gzip
import json
import math
import statistics
from collections import Counter, defaultdict
from pathlib import Path

from metrics import binary_metrics, interval_iou, partition_metrics, ranked_target_metrics
from observation_api import load_seed
from phase_authority import content_hash as authority_content_hash, require_instrument


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
EXP = ROOT / "experiments/yolo/gdt396_repaired_synthetic_identifiability_voynich_surface"
G395 = ROOT / "experiments/yolo/gdt395_adversarial_synthetic_identifiability_benchmark"
CORPORA = EXP / ".work/corpora"
CLAIMS = EXP / ".work/claims"
OUT_FIELDS = (
    "phase", "decoder_id", "method_family", "world_id", "surface_id", "corpus_seed",
    "representation_id", "method_variant", "property_id", "endpoint", "status",
    "eligible_n", "prediction_n", "coverage", "primary_metric", "primary_value",
    "baseline_value", "gain", "pass", "metrics_json",
)
NONE = {"NONE", "", "NA", "N/A"}
WORLD_PANEL = json.loads((G395 / "artifacts/gdt395_world_panel_freeze.json").read_text(encoding="utf-8"))
WORLD_META = {row["world_id"]: row["meta"] for row in WORLD_PANEL["worlds"]}
TEMPORAL_CLASSES = {
    "TEMPORAL_SCOPE", "SIMULTANEOUS_SCOPE", "CONDITION_SCOPE", "TERMINAL_SCOPE",
    "COMPLETIVE", "SCOPE_OPERATOR", "STATE_OPERATOR", "TERMINATIVE",
    "CONDITION_OPEN", "CONDITION", "SCOPE_CLOSE", "ITERATIVE", "SCOPE_GATE",
    "SCOPE_CLOSER", "RECURRENCE_OPERATOR", "DISCOURSE", "SCOPE",
}
ALTERNATIVE_TYPES = {"ALTERNATIVE_TO", "ALTERNATIVE", "SUBSTITUTE"}
REFERENCE_TYPES = {
    "REFERS_TO", "COREFERENCE", "PREVIOUS_MENTION", "REFERS_BACK", "REF_EVENT",
    "REFERENCE", "INDEX_REFERENCE", "CROSS_REFERENCE", "continues_reference",
}
PARTITION_MAP = {
    "LEXICAL_IDENTITY": "lexical_id",
    "SEMANTIC_ENTITY_IDENTITY": "semantic_entity_id",
    "HISTORICAL_ANCESTRY": "historical_stem_id",
    "FOSSIL_COMPONENT": "fossilized_component_ids",
    "CURRENT_SHARED_MEANING": "current_component_semantics",
    "FUNCTION_OPERATOR_CLASS": "function_class",
    "CONSTRUCTION_CLASS": "construction_id",
    "REGISTER_REALIZATION": "register_realization_id",
    "SEMANTIC_CATEGORY": "semantic_category",
    "STATE_BEFORE_IDENTITY": "state_before",
    "STATE_AFTER_IDENTITY": "state_after",
}
RETAINED = {
    "FULL_GROUP": {"partition_claims": {"LEXICAL_IDENTITY"}},
    "HOST_LIKE": {"partition_claims": {"SEMANTIC_ENTITY_IDENTITY","HISTORICAL_ANCESTRY","CURRENT_SHARED_MEANING","REGISTER_REALIZATION"}},
    "COMPOSITE_STATE": {"partition_claims":{"CONSTRUCTION_CLASS","STATE_BEFORE_IDENTITY","STATE_AFTER_IDENTITY","STATE_TRANSITION_IDENTITY"},"binary_claims":{"TEMPORAL_STATE_GATE"}},
    "INFERRED_COMPONENTS": {"partition_claims":{"CURRENT_PRODUCTIVE_COMPONENT","FOSSIL_COMPONENT"},"binary_claims":{"PRODUCTIVE_MORPHOLOGY","FOSSILIZED_MORPHOLOGY"}},
    "CONSTRUCTION_SPAN": {"scope_claims":{"SCOPE"}},
    "RECORD_TOPOLOGY": {"binary_claims":{"ENTITY_REUSE_PRESENT"},"target_queries":{"GENERIC_RELATION","COORDINATOR_RELATION","ALTERNATIVE_RELATION","REFERENCE_ANAPHORA","ENTITY_REUSE_ANTECEDENT"},"record_partition_claims":{"RECORD_SCHEMA"}},
    "MULTI_RESOLUTION": {"partition_claims":{"FUNCTION_OPERATOR_CLASS","SEMANTIC_CATEGORY"},"architecture_binary_claims":{"LANGUAGE_LIKE","NOTATION_LIKE","CODEBOOK_LIKE","ORGANIC_EVOLUTION_LIKE","CLEAN_ENGINEERED_LIKE","SEMANTICS_LIGHT_LIKE"}},
}


def retained(representation: str, table: str, prop: str) -> bool:
    plan = RETAINED[representation]
    return prop in plan.get(table, set())


def rows(path: Path) -> list[dict]:
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt", encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def sha256(path: Path) -> str:
    h = __import__("hashlib").sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def require_claim_freeze(phase: str, claims_dir: Path, manifest_path: Path) -> dict:
    if phase == "DEVELOPMENT":
        return {}
    require_instrument(EXP, phase)
    freeze_path = EXP / f"artifacts/gdt396_{phase.lower()}_claim_freeze.json"
    if not freeze_path.is_file():
        raise RuntimeError(f"{phase} blind claim freeze is absent")
    frozen = json.loads(freeze_path.read_text(encoding="utf-8"))
    if (frozen.get("schema") != "GDT396_BLIND_CLAIM_FREEZE_V1" or
            frozen.get("status") != "FROZEN_BEFORE_ORACLE_SCORING" or
            frozen.get("phase") != phase or
            frozen.get("content_sha256") != authority_content_hash(frozen) or
            frozen.get("claim_manifest_sha256") != sha256(manifest_path) or
            frozen.get("decoder_panel_freeze_sha256") != sha256(EXP / "artifacts/gdt396_decoder_panel_freeze.json")):
        raise RuntimeError(f"{phase} blind claim freeze is stale or invalid")
    bindings = frozen.get("claim_bindings", {})
    for relpath, expected in bindings.items():
        path = (claims_dir / relpath).resolve()
        if not path.is_relative_to(claims_dir.resolve()) or not path.is_file() or sha256(path) != expected:
            raise RuntimeError(f"post-freeze claim drift: {relpath}")
    return frozen


def signature(value: str) -> str:
    if value in NONE: return "NONE"
    return "|".join(sorted(set(value.split("|"))))


def corpus(block: str, world: str, seed: int, surface: str) -> tuple[list[dict], list[dict]]:
    # Use the same channel-specific observation materialization as the blind
    # runner.  The raw FREE TSV intentionally has no `visible_surface` field,
    # while morphology span diagnostics require the actual presented channel
    # length (which doubles under VOYNICH_SURFACE).
    obs = load_seed(block, world, seed, surface)
    oracle = rows(CORPORA / "sealed" / block / world / f"seed_{seed}_oracle.tsv.gz")
    if [r["event_id"] for r in obs] != [r["event_id"] for r in oracle]:
        raise RuntimeError("observation/oracle order mismatch")
    return obs, oracle


def partition_truth(prop: str, oracle: list[dict]) -> dict[str, str]:
    if prop == "CURRENT_PRODUCTIVE_COMPONENT":
        return {r["event_id"]: signature(r["current_morpheme_ids"]) for r in oracle if r["productive_morphology"] == "TRUE" and signature(r["current_morpheme_ids"]) != "NONE"}
    if prop == "STATE_TRANSITION_IDENTITY":
        return {r["event_id"]: signature(r["state_before"]) + "->" + signature(r["state_after"]) for r in oracle if r["state_before"] not in NONE and r["state_after"] not in NONE}
    field = PARTITION_MAP.get(prop)
    if not field: return {}
    return {r["event_id"]: signature(r[field]) for r in oracle if signature(r[field]) != "NONE"}


def binary_truth(prop: str, oracle: list[dict]) -> dict[str, bool]:
    if prop == "PRODUCTIVE_MORPHOLOGY": return {r["event_id"]: r["productive_morphology"] == "TRUE" for r in oracle}
    if prop == "FOSSILIZED_MORPHOLOGY": return {r["event_id"]: signature(r["fossilized_component_ids"]) != "NONE" for r in oracle}
    if prop == "TEMPORAL_STATE_GATE": return {r["event_id"]: r["function_class"] in TEMPORAL_CLASSES or r["relation_type"] == "CONDITION" for r in oracle}
    if prop == "ENTITY_REUSE_PRESENT":
        seen = set(); out = {}
        for r in oracle:
            value = signature(r["semantic_entity_id"])
            out[r["event_id"]] = value != "NONE" and value in seen
            if value != "NONE": seen.add(value)
        return out
    return {}


def target_truth(prop: str, obs: list[dict], oracle: list[dict]) -> dict[str, set[str]]:
    by = {r["event_id"]: r for r in obs}; rank = {r["event_id"]: i for i, r in enumerate(obs)}
    result: dict[str, set[str]] = {}
    if prop == "ENTITY_REUSE_ANTECEDENT":
        seen: dict[str, list[str]] = defaultdict(list)
        for truth in oracle:
            value = signature(truth["semantic_entity_id"]); eid = truth["event_id"]
            if value != "NONE" and seen[value]: result[eid] = set(seen[value])
            if value != "NONE": seen[value].append(eid)
        return result
    for truth in oracle:
        if truth["relation_target_event_id"] in NONE: continue
        types = truth["relation_type"].split("|")
        targets = {value for value in truth["relation_target_event_id"].split("|") if value in by}
        if prop == "COORDINATOR_RELATION" and truth["function_class"] != "COORDINATOR": continue
        if prop == "ALTERNATIVE_RELATION" and not (len(types) == 1 and types[0] in ALTERNATIVE_TYPES): continue
        if prop == "REFERENCE_ANAPHORA" and not (len(types) == 1 and types[0] in REFERENCE_TYPES): continue
        if prop not in {"GENERIC_RELATION", "COORDINATOR_RELATION", "ALTERNATIVE_RELATION", "REFERENCE_ANAPHORA"}: continue
        source = by[truth["event_id"]]
        if prop in {"GENERIC_RELATION", "COORDINATOR_RELATION", "ALTERNATIVE_RELATION"}:
            targets = {value for value in targets if by[value]["record_id"] == source["record_id"] and value != source["event_id"]}
        else:
            targets = {value for value in targets if rank[value] < rank[source["event_id"]]}
        if targets: result[source["event_id"]] = targets
    return result


def relation_type_count(prop: str, obs: list[dict], oracle: list[dict]) -> int:
    by={r["event_id"]:r for r in obs};rank={r["event_id"]:i for i,r in enumerate(obs)};types=set()
    for truth in oracle:
        targets={value for value in truth["relation_target_event_id"].split("|") if value in by and value not in NONE}
        if not targets:continue
        raw=truth["relation_type"].split("|")
        if prop=="COORDINATOR_RELATION" and truth["function_class"]!="COORDINATOR":continue
        if prop=="ALTERNATIVE_RELATION" and not(len(raw)==1 and raw[0] in ALTERNATIVE_TYPES):continue
        if prop=="REFERENCE_ANAPHORA" and not(len(raw)==1 and raw[0] in REFERENCE_TYPES):continue
        if prop=="ENTITY_REUSE_ANTECEDENT":continue
        source=truth["event_id"]
        if prop in {"GENERIC_RELATION","COORDINATOR_RELATION","ALTERNATIVE_RELATION"}:
            targets={value for value in targets if by[value]["record_id"]==by[source]["record_id"] and value!=source}
        else:targets={value for value in targets if rank[value]<rank[source]}
        if targets:types.update(raw)
    return len(types)


def average_precision(truth:list[bool],scores:list[float])->float:
    positives=sum(truth)
    if not positives:return math.nan
    order=sorted(range(len(truth)),key=lambda i:(-scores[i],i));hits=0;total=0.0
    for rank,index in enumerate(order,1):
        if truth[index]:hits+=1;total+=hits/rank
    return total/positives


def scope_truth(obs: list[dict], oracle: list[dict]) -> dict[str, tuple[int, int]]:
    by = {r["event_id"]: r for r in obs}; record_ord = {}; counts = defaultdict(int)
    for row in obs:
        record_ord[row["event_id"]] = counts[row["record_id"]]; counts[row["record_id"]] += 1
    out = {}
    for truth in oracle:
        a = truth["scope_start_event_id"]; b = truth["scope_end_event_id"]; source = truth["event_id"]
        if a in NONE or b in NONE or a not in by or b not in by: continue
        if by[a]["record_id"] == by[source]["record_id"] == by[b]["record_id"]:
            out[source] = (record_ord[a], record_ord[b])
    return out


def resolved_partition(claims: list[dict], prop: str) -> dict[str, str]:
    return {r["unit_id"]: r["cluster_id"] for r in claims if r["property_id"] == prop and r["unit_type"] == "EVENT" and r["claim_status"] == "RESOLVED"}


def make_row(context: dict, prop: str, endpoint: str, status: str, eligible: int, prediction: int, coverage: float, primary: str, value: float, baseline: float, gain: float, passed: bool, metrics: dict) -> dict:
    return {**context, "property_id": prop, "endpoint": endpoint, "status": status,
            "eligible_n": eligible, "prediction_n": prediction, "coverage": f"{coverage:.12g}",
            "primary_metric": primary, "primary_value": f"{value:.12g}" if math.isfinite(value) else "NA",
            "baseline_value": f"{baseline:.12g}" if math.isfinite(baseline) else "NA",
            "gain": f"{gain:.12g}" if math.isfinite(gain) else "NA", "pass": "TRUE" if passed else "FALSE",
            "metrics_json": json.dumps(metrics, sort_keys=True, separators=(",", ":"))}


def score_context(context: dict, tables: dict[str, list[dict]], obs: list[dict], oracle: list[dict]) -> list[dict]:
    out = []
    partition_claims = [r for r in tables["partition_claims"] if r["method_variant"] == "PRIMARY"]
    binary_claims = [r for r in tables["binary_claims"] if r["method_variant"] == "PRIMARY"]
    partition_props = sorted(set(PARTITION_MAP) | {"CURRENT_PRODUCTIVE_COMPONENT", "STATE_TRANSITION_IDENTITY"})
    for prop in partition_props:
        if not retained(context["representation_id"], "partition_claims", prop):
            out.append(make_row(context, prop, "PARTITION", "UNSUPPORTED", 0, 0, 0, "pair_f1", math.nan, math.nan, math.nan, False, {})); continue
        truth = partition_truth(prop, oracle); pred = resolved_partition(partition_claims, prop); eligible = len(truth)
        if eligible < 2:
            absent=[row["event_id"] for row in obs if row["event_id"] not in truth]
            fp_rate=sum(eid in pred for eid in absent)/len(absent) if absent else 0.0
            out.append(make_row(context, prop, "PARTITION", "NO_CAPACITY", eligible, len(pred), 0, "pair_f1", math.nan, math.nan, math.nan, False, {"resolved_without_truth_rate":fp_rate})); continue
        ids = sorted(truth); resolved = sum(eid in pred for eid in ids); coverage = resolved / eligible
        predicted = [pred.get(eid, f"ABSTAIN:{eid}") for eid in ids]
        metrics = partition_metrics([truth[eid] for eid in ids], predicted)
        absent=[row["event_id"] for row in obs if row["event_id"] not in truth]
        metrics["resolved_without_truth_rate"]=sum(eid in pred for eid in absent)/len(absent) if absent else 0.0
        gate = coverage >= .25 and metrics["nmi"] >= .35 and metrics["ari"] >= .20 and metrics["pair_f1"] >= .35
        metrics["coverage"] = coverage
        out.append(make_row(context, prop, "PARTITION", "SCORED", eligible, resolved, coverage, "pair_f1", metrics["pair_f1"], 0, metrics["pair_f1"], gate, metrics))
    if context["representation_id"] == "MULTI_RESOLUTION":
        truth=partition_truth("FUNCTION_OPERATOR_CLASS",oracle)
        for variant in ("MULTI_CONSTRAINT","SCALAR_BOTTLENECK"):
            variant_context=dict(context);variant_context["method_variant"]=variant
            claims=[r for r in tables["partition_claims"] if r["method_variant"]==variant]
            pred=resolved_partition(claims,"FUNCTION_OPERATOR_CLASS");eligible=len(truth)
            if eligible<2:
                absent=[row["event_id"] for row in obs if row["event_id"] not in truth];rate=sum(eid in pred for eid in absent)/len(absent) if absent else 0.0
                out.append(make_row(variant_context,"FUNCTION_OPERATOR_CLASS","PARTITION", "NO_CAPACITY",eligible,len(pred),0,"pair_f1",math.nan,math.nan,math.nan,False,{"resolved_without_truth_rate":rate}));continue
            ids=sorted(truth);resolved=sum(eid in pred for eid in ids);coverage=resolved/eligible;predicted=[pred.get(eid,f"ABSTAIN:{eid}") for eid in ids];detail=partition_metrics([truth[eid] for eid in ids],predicted);detail["coverage"]=coverage;absent=[row["event_id"] for row in obs if row["event_id"] not in truth];detail["resolved_without_truth_rate"]=sum(eid in pred for eid in absent)/len(absent) if absent else 0.0;gate=coverage>=.25 and detail["nmi"]>=.35 and detail["ari"]>=.20 and detail["pair_f1"]>=.35
            out.append(make_row(variant_context,"FUNCTION_OPERATOR_CLASS","PARTITION","SCORED",eligible,resolved,coverage,"pair_f1",detail["pair_f1"],0,detail["pair_f1"],gate,detail))
    for prop in ("PRODUCTIVE_MORPHOLOGY", "FOSSILIZED_MORPHOLOGY", "TEMPORAL_STATE_GATE", "ENTITY_REUSE_PRESENT"):
        if not retained(context["representation_id"], "binary_claims", prop):
            out.append(make_row(context, prop, "BINARY", "UNSUPPORTED", 0, 0, 0, "mcc", math.nan, math.nan, math.nan, False, {})); continue
        truth = binary_truth(prop, oracle); resolved_rows = {r["unit_id"]: r for r in binary_claims if r["property_id"] == prop and r["unit_type"] == "EVENT" and r["claim_status"] == "RESOLVED"}
        ids = sorted(truth); resolved_ids = [eid for eid in ids if eid in resolved_rows]; coverage = len(resolved_ids) / len(ids) if ids else 0
        if not ids or len({truth[eid] for eid in ids}) < 2:
            positives=sum(row["predicted_bool"]=="TRUE" for row in resolved_rows.values())
            out.append(make_row(context, prop, "BINARY", "NO_CAPACITY", len(ids), len(resolved_ids), coverage, "mcc", math.nan, math.nan, math.nan, False, {"positive_prediction_rate":positives/len(ids) if ids else (positives/len(obs) if obs else 0.0)})); continue
        # Complete abstentions adversarially so selective coverage cannot inflate accuracy.
        predictions = [
            (resolved_rows[eid]["predicted_bool"] == "TRUE") if eid in resolved_rows else (not truth[eid])
            for eid in ids
        ]
        metrics = binary_metrics([truth[eid] for eid in ids], predictions); metrics["coverage"] = coverage
        metrics["positive_prediction_rate"]=sum(bool(value) for value in predictions)/len(predictions) if predictions else 0.0
        gate = coverage >= .25 and metrics["balanced_accuracy"] >= .65 and metrics["mcc"] >= .20 and metrics["fdr"] <= .40
        out.append(make_row(context, prop, "BINARY", "SCORED", len(ids), len(resolved_ids), coverage, "mcc", metrics["mcc"], 0, metrics["mcc"], gate, metrics))

    if context["representation_id"]!="INFERRED_COMPONENTS":
        out.append(make_row(context,"MORPHOLOGY_ANALYSIS","MORPHOLOGY","UNSUPPORTED",0,0,0,"macro_f1",math.nan,math.nan,math.nan,False,{}))
    else:
        by_event={r["event_id"]:r for r in obs};truth_by={r["event_id"]:r for r in oracle};claims=[r for r in tables["morphology_claims"] if r["method_variant"]=="PRIMARY" and r["claim_status"]=="RESOLVED" and r["morphology_status"] in {"CURRENTLY_PRODUCTIVE","FOSSILIZED"}]
        claimed=defaultdict(list)
        for row in claims:claimed[row["event_id"]].append(row)
        ids=list(by_event);status_metrics={};f1s=[];aps=[]
        for status in ("CURRENTLY_PRODUCTIVE","FOSSILIZED"):
            truth=[truth_by[eid]["productive_morphology"]=="TRUE" if status=="CURRENTLY_PRODUCTIVE" else signature(truth_by[eid]["fossilized_component_ids"])!="NONE" for eid in ids]
            pred=[any(r["morphology_status"]==status for r in claimed[eid]) for eid in ids]
            score=[max((float(r["confidence"]) for r in claimed[eid] if r["morphology_status"]==status),default=0.0) for eid in ids]
            bm=binary_metrics(truth,pred);precision=bm["tp"]/(bm["tp"]+bm["fp"]) if bm["tp"]+bm["fp"] else 0.0;recall=bm["tp"]/(bm["tp"]+bm["fn"]) if bm["tp"]+bm["fn"] else 0.0;f1=2*precision*recall/(precision+recall) if precision+recall else 0.0;ap=average_precision(truth,score)
            status_metrics[status]={**bm,"precision":precision,"recall":recall,"f1":f1,"ap":ap};f1s.append(f1)
            if math.isfinite(ap):aps.append(ap)
        proper=sum(0<=int(r["start_offset"])<int(r["end_offset"])<=len(by_event[r["event_id"]]["visible_surface"]) and (int(r["start_offset"])>0 or int(r["end_offset"])<len(by_event[r["event_id"]]["visible_surface"])) for r in claims)/len(claims) if claims else 0.0
        supports=defaultdict(lambda:{"types":set(),"records":set(),"statuses":set()})
        for r in claims:
            item=supports[r["component_id"]];item["types"].add(tuple(by_event[r["event_id"]]["visible_surface"]));item["records"].add(by_event[r["event_id"]]["record_id"]);item["statuses"].add(r["morphology_status"])
        recurrent=sum(len(v["types"])>=3 and len(v["records"])>=2 for v in supports.values());disjoint=all(len(v["statuses"])==1 for v in supports.values());coverage=len(claimed)/len(ids) if ids else 0.0;macro=sum(f1s)/2;mean_ap=sum(aps)/len(aps) if aps else math.nan;current_fdr=status_metrics["CURRENTLY_PRODUCTIVE"]["fdr"]
        detail={"coverage":coverage,"macro_f1":macro,"mean_ap":mean_ap,"proper_substring_fraction":proper,"recurrent_component_count":recurrent,"productive_fossil_component_ids_disjoint":disjoint,"current_false_discovery_rate":current_fdr,"status_metrics":status_metrics}
        gate=coverage>=.60 and macro>=.60 and (mean_ap>=.50 if math.isfinite(mean_ap) else False) and current_fdr<=.10 and recurrent>=1 and disjoint and proper>=.50
        out.append(make_row(context,"MORPHOLOGY_ANALYSIS","MORPHOLOGY","SCORED",len(ids),len(claimed),coverage,"macro_f1",macro,0,macro,gate,detail))

    query_rows = [r for r in tables["target_queries"] if r["method_variant"] == "PRIMARY"]
    rank_rows = [r for r in tables["target_ranks"] if r["method_variant"] == "PRIMARY"]
    for prop in ("GENERIC_RELATION", "COORDINATOR_RELATION", "ALTERNATIVE_RELATION", "REFERENCE_ANAPHORA", "ENTITY_REUSE_ANTECEDENT"):
        if not retained(context["representation_id"], "target_queries", prop):
            out.append(make_row(context, prop, "RANKED_TARGET", "UNSUPPORTED", 0, 0, 0, "mrr", math.nan, math.nan, math.nan, False, {})); continue
        truth = target_truth(prop, obs, oracle); eligible = len(truth)
        queries = {r["source_event_id"]: r for r in query_rows if r["property_id"] == prop}
        rankings = defaultdict(list)
        for row in sorted((r for r in rank_rows if r["property_id"] == prop), key=lambda r: (r["source_event_id"], int(r["target_rank"]))): rankings[row["source_event_id"]].append(row["target_event_id"])
        resolved = sum(source in queries and queries[source]["claim_status"] == "RESOLVED" for source in truth); coverage = resolved / eligible if eligible else 0
        if not truth:
            resolved_queries=sum(r["claim_status"]=="RESOLVED" for r in query_rows if r["property_id"]==prop)
            out.append(make_row(context, prop, "RANKED_TARGET", "NO_CAPACITY", 0, resolved_queries, 0, "mrr", math.nan, math.nan, math.nan, False, {"resolved_without_truth_rate":resolved_queries/len(obs) if obs else 0.0})); continue
        metrics = ranked_target_metrics(truth, rankings)
        absent=[row["event_id"] for row in obs if row["event_id"] not in truth]
        metrics["resolved_without_truth_rate"]=sum(eid in queries and queries[eid]["claim_status"]=="RESOLVED" for eid in absent)/len(absent) if absent else 0.0
        by = {r["event_id"]: r for r in obs}; pos = {r["event_id"]: i for i, r in enumerate(obs)}
        baseline_rank = {}
        for source in truth:
            if prop in {"REFERENCE_ANAPHORA", "ENTITY_REUSE_ANTECEDENT"}:
                candidates = [eid for eid in by if pos[eid] < pos[source]]
                baseline_rank[source] = [max(candidates, key=lambda eid: pos[eid])] if candidates else []
            else:
                candidates = [eid for eid, row in by.items() if row["record_id"] == by[source]["record_id"] and eid != source]
                baseline_rank[source] = sorted(candidates, key=lambda eid: (abs(pos[eid] - pos[source]), pos[eid]))[:1]
        baseline = ranked_target_metrics(truth, baseline_rank)["mrr"]
        gain = metrics["mrr"] - baseline; metrics.update(coverage=coverage, baseline_mrr=baseline, mrr_gain=gain, relation_type_count=relation_type_count(prop,obs,oracle))
        gate = coverage >= .25 and metrics["hits1"] >= .15 and gain >= .05
        out.append(make_row(context, prop, "RANKED_TARGET", "SCORED", eligible, resolved, coverage, "mrr", metrics["mrr"], baseline, gain, gate, metrics))

    truth_scope = scope_truth(obs, oracle); scope_rows = {r["source_event_id"]: r for r in tables["scope_claims"] if r["method_variant"] == "PRIMARY" and r["claim_status"] == "RESOLVED" and r["scope_present"] == "TRUE"}
    if not retained(context["representation_id"], "scope_claims", "SCOPE"):
        out.append(make_row(context,"SCOPE","SCOPE","UNSUPPORTED",0,0,0,"mean_iou",math.nan,math.nan,math.nan,False,{}))
    elif truth_scope:
        record_ord = {}; counts = defaultdict(int); record_sizes = Counter(r["record_id"] for r in obs); by = {r["event_id"]: r for r in obs}
        for row in obs: record_ord[row["event_id"]] = counts[row["record_id"]]; counts[row["record_id"]] += 1
        ious=[]; exact=0; endpoint=0; baseline=[]
        for source, target in truth_scope.items():
            row=scope_rows.get(source); predicted=None
            if row and row["predicted_start_event_id"] in record_ord and row["predicted_end_event_id"] in record_ord:
                predicted=(record_ord[row["predicted_start_event_id"]],record_ord[row["predicted_end_event_id"]])
            ious.append(interval_iou(target,predicted) if predicted else 0.0); exact += predicted==target
            endpoint += bool(predicted and (predicted[0]==target[0] or predicted[1]==target[1]))
            anchor=record_ord[source]; size=record_sizes[by[source]["record_id"]]
            candidates=[(0,size-1),(anchor,anchor),(max(0,anchor-2),min(size-1,anchor+2))]
            baseline.append(max(interval_iou(target,c) for c in candidates))
        coverage=sum(source in scope_rows for source in truth_scope)/len(truth_scope); mean=sum(ious)/len(ious); base=sum(baseline)/len(baseline)
        metrics={"mean_iou":mean,"median_iou":statistics.median(ious),"exact_rate":exact/len(ious),"endpoint_rate":endpoint/len(ious),"coverage":coverage,"baseline_iou":base}
        gate=coverage>=.25 and mean>=.35
        out.append(make_row(context,"SCOPE","SCOPE","SCORED",len(truth_scope),len(scope_rows),coverage,"mean_iou",mean,base,mean-base,gate,metrics))
    else:
        out.append(make_row(context,"SCOPE","SCOPE","NO_CAPACITY",0,0,0,"mean_iou",math.nan,math.nan,math.nan,False,{}))

    schemas=defaultdict(set)
    for o,t in zip(obs,oracle,strict=True): schemas[o["record_id"]].add(t["record_schema_id"])
    truth_records={rid:next(iter(values)) for rid,values in schemas.items() if len(values)==1 and next(iter(values)) not in NONE}
    claim_records={r["record_id"]:r["record_schema_cluster_id"] for r in tables["record_partition_claims"] if r["method_variant"] == "PRIMARY" and r["claim_status"]=="RESOLVED"}
    if not retained(context["representation_id"], "record_partition_claims", "RECORD_SCHEMA"):
        out.append(make_row(context,"RECORD_SCHEMA","RECORD_PARTITION","UNSUPPORTED",0,0,0,"pair_f1",math.nan,math.nan,math.nan,False,{}))
    elif len(truth_records)>=2:
        ids=sorted(truth_records);resolved=sum(rid in claim_records for rid in ids);coverage=resolved/len(ids);pred=[claim_records.get(rid,f"ABSTAIN:{rid}") for rid in ids];metrics=partition_metrics([truth_records[rid] for rid in ids],pred);metrics["coverage"]=coverage
        gate=coverage>=.25 and metrics["nmi"]>=.35 and metrics["ari"]>=.20 and metrics["pair_f1"]>=.35
        out.append(make_row(context,"RECORD_SCHEMA","RECORD_PARTITION","SCORED",len(ids),resolved,coverage,"pair_f1",metrics["pair_f1"],0,metrics["pair_f1"],gate,metrics))
    else:
        out.append(make_row(context,"RECORD_SCHEMA","RECORD_PARTITION","NO_CAPACITY",len(truth_records),0,0,"pair_f1",math.nan,math.nan,math.nan,False,{}))

    # World-level architecture rows are retained as seed-level direct-truth
    # diagnostics. Cross-world BA/MCC is computed by the qualification/result
    # aggregator, never from one world in isolation.
    architecture_truth = {
        "ORGANIC_EVOLUTION_LIKE": bool(WORLD_META[context["world_id"]]["organic_evolution"]),
        "CLEAN_ENGINEERED_LIKE": bool(WORLD_META[context["world_id"]]["clean_engineered_control"]),
        "SEMANTICS_LIGHT_LIKE": bool(WORLD_META[context["world_id"]]["semantics_light"]),
    }
    for variant in ("PRIMARY", "MULTI_CONSTRAINT", "SCALAR_BOTTLENECK"):
        for prop in ("LANGUAGE_LIKE", "NOTATION_LIKE", "CODEBOOK_LIKE", "ORGANIC_EVOLUTION_LIKE", "CLEAN_ENGINEERED_LIKE", "SEMANTICS_LIGHT_LIKE"):
            matches = [r for r in tables["architecture_binary_claims"] if r["method_variant"] == variant and r["property_id"] == prop and r["claim_status"] == "RESOLVED"]
            arch_context = dict(context); arch_context["method_variant"] = variant
            if context["representation_id"] != "MULTI_RESOLUTION":
                out.append(make_row(arch_context, prop, "ARCHITECTURE_BINARY", "UNSUPPORTED", 0, 0, 0, "accuracy", math.nan, math.nan, math.nan, False, {})); continue
            if prop not in architecture_truth:
                out.append(make_row(arch_context, prop, "ARCHITECTURE_BINARY", "UNSUPPORTED_DIRECT_TRUTH", 0, len(matches), 0, "accuracy", math.nan, math.nan, math.nan, False, {}))
                continue
            if len(matches) != 1:
                out.append(make_row(arch_context, prop, "ARCHITECTURE_BINARY", "NO_PREDICTION", 1, len(matches), float(bool(matches)), "accuracy", 0.0, 0.0, 0.0, False, {}))
                continue
            predicted = matches[0]["predicted_bool"] == "TRUE"; truth_value = architecture_truth[prop]
            value = float(predicted == truth_value)
            out.append(make_row(arch_context, prop, "ARCHITECTURE_BINARY", "SCORED", 1, 1, 1.0, "accuracy", value, 0.5, value - 0.5, bool(value), {"truth_bool": truth_value, "predicted_bool": predicted}))
    return out


def main() -> int:
    ap=argparse.ArgumentParser();ap.add_argument("--phase",choices=("DEVELOPMENT","QUALIFICATION","CONFIRMATION"),required=True);ap.add_argument("--claims-dir",type=Path,default=CLAIMS);ap.add_argument("--output",type=Path,default=None);args=ap.parse_args()
    block=args.phase.lower(); manifest_path=args.claims_dir/f"gdt396_{block}_claim_manifest.tsv"; manifest=rows(manifest_path)
    claim_freeze=require_claim_freeze(args.phase,args.claims_dir,manifest_path)
    if claim_freeze:
        manifest_bindings={row["relpath"]:row["sha256"] for row in manifest}
        if (len(manifest_bindings)!=len(manifest) or manifest_bindings!=claim_freeze.get("claim_bindings") or
                sum(int(row["rows"]) for row in manifest)!=int(claim_freeze.get("claim_rows",-1))):
            raise RuntimeError("claim manifest no longer reconstructs the exact frozen panel")
    panel_path = EXP / "artifacts/gdt396_decoder_panel_freeze.json"
    panel_hashes = {}
    if panel_path.is_file():
        panel_hashes = {row["decoder_id"]: row["decoder_sha256"] for row in json.loads(panel_path.read_text())["decoders"]}
    groups=defaultdict(dict);meta={}; model_hashes={}
    for row in manifest:
        key=(row["decoder_id"],row["world_id"],row["surface_id"],int(row["corpus_seed"]),row["representation_id"])
        table=row["table_name"]
        if table in groups[key]: raise ValueError(f"duplicate table manifest row {key}/{table}")
        path=(args.claims_dir/row["relpath"]).resolve()
        if not path.is_relative_to(args.claims_dir.resolve()) or not path.is_file() or sha256(path)!=row["sha256"]:
            raise ValueError(f"claim path/hash invalid {row['relpath']}")
        if panel_hashes and panel_hashes.get(row["decoder_id"]) != row["decoder_sha256"]:
            raise ValueError("claim decoder hash differs from panel freeze")
        expected_training={"DEVELOPMENT":"legacy","QUALIFICATION":"legacy;development","CONFIRMATION":"legacy;development;qualification"}[args.phase]
        if row["phase"]!=args.phase or row["training_blocks"]!=expected_training: raise ValueError("claim phase/training binding invalid")
        model_key=(row["decoder_id"],row["world_id"],row["surface_id"])
        if model_key in model_hashes and model_hashes[model_key]!=row["model_sha256"]: raise ValueError("model hash changed within phase")
        model_hashes[model_key]=row["model_sha256"]
        groups[key][table]=(path,int(row["rows"]));meta[key]=row
    required={"partition_claims","binary_claims","target_queries","target_ranks","scope_claims","morphology_claims","record_partition_claims","architecture_partition_claims","architecture_binary_claims"}
    if any(set(tables)!=required for tables in groups.values()): raise ValueError("incomplete context table set")
    by_corpus=defaultdict(list)
    for key in groups: by_corpus[(key[1],key[3])].append(key)
    result=[]; corpus_cache={}
    for (world,seed),keys in sorted(by_corpus.items()):
        for key in sorted(keys):
            decoder,_,surface,_,representation=key; tables={}
            corpus_key=(world,seed,surface)
            if corpus_key not in corpus_cache:
                corpus_cache[corpus_key]=corpus(block,world,seed,surface)
            obs,oracle=corpus_cache[corpus_key]
            for table,(path,expected_rows) in groups[key].items():
                data=rows(path)
                if len(data)!=expected_rows: raise ValueError(f"claim row count mismatch {path}")
                tables[table]=data
            context={"phase":args.phase,"decoder_id":decoder,"method_family":meta[key]["method_family"],"world_id":world,"surface_id":surface,"corpus_seed":seed,"representation_id":representation,"method_variant":"PRIMARY"}
            result.extend(score_context(context,tables,obs,oracle))
    output=args.output or args.claims_dir/f"gdt396_{block}_metrics.tsv"
    if output.exists(): raise RuntimeError(f"refusing to overwrite scored metrics {output}")
    with output.open("w",encoding="utf-8",newline="") as fh:
        writer=csv.DictWriter(fh,fieldnames=OUT_FIELDS,delimiter="\t",lineterminator="\n");writer.writeheader();writer.writerows(result)
    print(output,len(result));return 0


if __name__=="__main__":raise SystemExit(main())
