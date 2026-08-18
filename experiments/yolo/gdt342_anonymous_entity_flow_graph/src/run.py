#!/usr/bin/env python3
"""Run GDT342 Stage A without opening any Voynich target."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import multiprocessing as mp
import os
import random
import re
import sys
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from pathlib import Path


def find_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("repository root not found")


ROOT = find_root(Path(__file__).resolve())
sys.path.insert(0, str(ROOT))
from tools.vmanus_experiment import canonical_json_bytes, sha256_file  # noqa: E402

EXP = ROOT / "experiments/yolo/gdt342_anonymous_entity_flow_graph"
ART = EXP / "artifacts"
METHOD = EXP / "METHOD.md"
AUDIT = EXP / "SOURCE_AUDIT.md"
DESIGN = ART / "gdt342_comparator_design.json"
SOURCE_FREEZE = ROOT / "gdt176_source_freeze.json"
MANIFEST = ROOT / "gdt176_corema_collection_manifest.tsv"
ORACLE = ROOT / "gdt176_corema_role_oracle.tsv"
CACHE = ROOT / ".gdt176/corema"
CENSUS = ART / "gdt342_entity_flow_census.tsv"
FOLDS = ART / "gdt342_comparator_folds.tsv"
RETRIEVAL = ART / "gdt342_comparator_retrieval.tsv"
MODELS = ART / "gdt342_comparator_models.tsv"
NULL = ART / "gdt342_comparator_null.tsv"
FREEZE = ART / "gdt342_entity_flow_freeze.json"
RESULT = ART / "gdt342_comparator_result.json"
COUNTER = ART / "gdt342_counterexamples.tsv"
REPORT = EXP / "COMPARATOR_REPORT.md"

NS = {"t": "http://www.tei-c.org/ns/1.0"}
XML_ID = "{http://www.w3.org/XML/1998/namespace}id"
ROLE_TAGS = {
    "opener", "instruction", "ingredient", "tool", "dish", "name",
    "closer", "kitchenTip", "householdTip", "servingTip", "time",
    "dietetics", "alternative", "ref", "unclear",
}

WORK_CANDIDATES: list[dict[str, object]] = []
WORK_WEIGHTS: dict[str, float] = {}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"empty table: {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def lname(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def normalized_text(node: ET.Element) -> str:
    return " ".join(" ".join(node.itertext()).lower().split())


def words(node: ET.Element) -> list[str]:
    return re.findall(r"[^\W_]+", normalized_text(node), flags=re.UNICODE)


def direct_words(node: ET.Element) -> list[str]:
    text = " ".join([node.text or ""] + [child.tail or "" for child in node]).lower()
    return re.findall(r"[^\W_]+", text, flags=re.UNICODE)


def opaque_word(value: str) -> str:
    return hashlib.sha256(("GDT342_RAW_WORD_CONTROL_V1\0" + value).encode()).hexdigest()[:20]


def norm_title(value: str) -> str:
    return re.sub(r"\W+", " ", value.lower()).strip()


def clip(value: int) -> int:
    return min(4, max(0, value))


def size_bucket(value: int) -> str:
    if value <= 8:
        return "01_08"
    if value <= 16:
        return "09_16"
    if value <= 32:
        return "17_32"
    return "33_PLUS"


def field_bucket(value: int) -> str:
    if value <= 4:
        return "01_04"
    if value <= 8:
        return "05_08"
    if value <= 16:
        return "09_16"
    return "17_PLUS"


def content_hash(document: dict[str, object]) -> str:
    copy = dict(document)
    copy.pop("content_sha256", None)
    return hashlib.sha256(canonical_json_bytes(copy)).hexdigest()


def multiset_jaccard(a: Counter, b: Counter) -> float:
    keys = set(a) | set(b)
    if not keys:
        return 1.0
    return sum(min(a[k], b[k]) for k in keys) / max(1, sum(max(a[k], b[k]) for k in keys))


def set_jaccard(a: set[str], b: set[str]) -> float:
    return len(a & b) / max(1, len(a | b))


def size_similarity(a: dict[str, object], b: dict[str, object]) -> float:
    du = abs(math.log2(1 + int(a["unit_count"])) - math.log2(1 + int(b["unit_count"])))
    df = abs(math.log2(1 + int(a["field_count"])) - math.log2(1 + int(b["field_count"])))
    return math.exp(-(du + df))


def tuple_similarity(a: tuple[int, ...], b: tuple[int, ...]) -> float:
    width = max(len(a), len(b))
    aa = a + (0,) * (width - len(a))
    bb = b + (0,) * (width - len(b))
    return max(0.0, 1.0 - sum(min(1.0, abs(x - y) / 4.0) for x, y in zip(aa, bb)) / width)


def ordered_alignment(a: list[tuple[int, ...]], b: list[tuple[int, ...]]) -> float:
    if not a or not b:
        return float(not a and not b)
    dp = [[0.0] * (len(b) + 1) for _ in range(len(a) + 1)]
    for i in range(1, len(a) + 1):
        for j in range(1, len(b) + 1):
            dp[i][j] = max(
                dp[i - 1][j],
                dp[i][j - 1],
                dp[i - 1][j - 1] + tuple_similarity(a[i - 1], b[j - 1]),
            )
    return dp[-1][-1] / max(len(a), len(b))


def build_graph(rows: list[dict[str, str]], raw_words: Counter[str]) -> dict[str, object]:
    rows = sorted(rows, key=lambda row: int(row["element_ordinal"]))
    instruction_counter = 0
    field_rows: dict[str, list[tuple[int, str]]] = defaultdict(list)
    field_first: dict[str, int] = {}
    global_concepts: set[str] = set()
    concept_rows = 0
    for row in rows:
        if row["role"] == "TITLE":
            continue
        ordinal = int(row["element_ordinal"])
        parent_instruction = int(row["parent_instruction_ordinal"])
        if row["role"] == "INSTRUCTION":
            instruction_counter += 1
            field = f"I{instruction_counter}"
        elif parent_instruction > 0:
            field = f"I{parent_instruction}"
        else:
            field = f"E{ordinal}"
        concept = row["concept_id"]
        if concept != "NONE":
            source_identity = "C:" + concept
            global_concepts.add(concept)
            concept_rows += 1
        else:
            source_identity = f"U:{ordinal}"
        field_rows[field].append((ordinal, source_identity))
        field_first[field] = min(field_first.get(field, ordinal), ordinal)

    field_order = sorted(field_rows, key=lambda field: (field_first[field], field))
    local_map: dict[str, str] = {}
    next_id = 1
    fields: list[list[str]] = []
    for field in field_order:
        values = []
        for _, source_identity in sorted(field_rows[field]):
            if source_identity not in local_map:
                local_map[source_identity] = f"E{next_id}"
                next_id += 1
            values.append(local_map[source_identity])
        fields.append(values)

    positions: dict[str, list[int]] = defaultdict(list)
    occurrence_counts: Counter[str] = Counter(identity for field in fields for identity in field)
    for index, values in enumerate(fields):
        for identity in set(values):
            positions[identity].append(index)
    n_fields = len(fields)
    field_signatures: list[tuple[int, ...]] = []
    order_only: list[tuple[int, ...]] = []
    transitions: list[tuple[int, ...]] = []
    flow_edges: Counter[tuple[int, ...]] = Counter()
    for index, values in enumerate(fields):
        current = set(values)
        previous = set(fields[index - 1]) if index else set()
        seen = set().union(*(set(field) for field in fields[:index])) if index else set()
        future = set().union(*(set(field) for field in fields[index + 1:])) if index + 1 < n_fields else set()
        immediate = current & previous
        returning = (current & seen) - previous
        reused_in_multiple_later = sum(sum(pos > index for pos in positions[identity]) >= 2 for identity in current)
        incoming = len(immediate | returning)
        field_signatures.append((
            clip(len(values)), clip(len(current)), clip(len(current - seen)),
            clip(len(immediate)), clip(len(returning)), clip(len(current & future)),
            int(incoming >= 2), clip(reused_in_multiple_later), int(index == n_fields - 1),
        ))
        order_only.append((clip(len(values)), int(index == n_fields - 1)))
        if index:
            source = set(fields[index - 1])
            shared = source & current
            ended = source - future - current
            transitions.append((
                clip(len(source)), clip(len(current)), clip(len(shared)),
                clip(len(current - seen)), clip(len(ended)), clip(len(returning)),
                int(incoming >= 2), clip(reused_in_multiple_later),
            ))
    entity_paths: Counter[tuple[int, ...]] = Counter()
    entity_degrees: Counter[tuple[int, ...]] = Counter()
    for field_positions in positions.values():
        gaps = [b - a for a, b in zip(field_positions, field_positions[1:])]
        path = (
            clip(len(field_positions)),
            min(3, 4 * field_positions[0] // max(1, n_fields)),
            min(3, 4 * field_positions[-1] // max(1, n_fields)),
            clip(max(gaps, default=0)),
            clip(sum(gap == 1 for gap in gaps)),
            int(any(gap > 1 for gap in gaps)),
            int(field_positions[-1] == n_fields - 1),
        )
        entity_paths[path] += 1
        entity_degrees[(clip(len(field_positions)),)] += 1
        for source, target in zip(field_positions, field_positions[1:]):
            flow_edges[(
                min(3, 4 * source // max(1, n_fields)),
                min(3, 4 * target // max(1, n_fields)),
                clip(target - source),
                clip(len(field_positions)),
            )] += 1
    return {
        "field_signatures": field_signatures,
        "transition_signatures": transitions,
        "order_only": order_only,
        "entity_paths": entity_paths,
        "flow_edges": flow_edges,
        "field_degrees": Counter((clip(len(set(field))),) for field in fields),
        "entity_degrees": entity_degrees,
        "unit_count": sum(len(field) for field in fields),
        "field_count": n_fields,
        "concept_rows": concept_rows,
        "global_concepts": global_concepts,
        "raw_words": raw_words,
        "record_local_identity_count": len(positions),
        "repeated_identity_count": sum(value >= 2 for value in occurrence_counts.values()),
        "cross_field_identity_count": sum(len(value) >= 2 for value in positions.values()),
    }


def parse_raw_sources(collections: list[str]) -> dict[tuple[str, str], dict[str, object]]:
    output: dict[tuple[str, str], dict[str, object]] = {}
    for collection in collections:
        root = ET.parse(CACHE / f"{collection}.recipes.xml").getroot()
        for ordinal, recipe in enumerate(root.findall('.//*[@type="recipe"]', NS), 1):
            record = recipe.get(XML_ID, f"{collection}.ordinal{ordinal}")
            raw = Counter()
            for node in recipe.iter():
                tag = lname(node.tag)
                if tag not in ROLE_TAGS or tag == "title":
                    continue
                # This control is deliberately diplomatic/source-form only.
                # Never substitute CoReMA's semantic `commodity=Q...` value:
                # doing so would duplicate the global-concept oracle ceiling.
                if tag in {"ingredient", "tool", "dish", "name"}:
                    source_tokens = words(node)
                else:
                    source_tokens = direct_words(node)
                if not source_tokens:
                    source_tokens = ["EMPTY"]
                for source_token in source_tokens:
                    raw[opaque_word(source_token)] += 1
            output[(collection, record)] = {
                "raw_words": raw,
                "surface_hash": hashlib.sha256(normalized_text(recipe).encode()).hexdigest(),
            }
    return output


def parse_records(collections: list[str], oracle_rows: list[dict[str, str]]) -> list[dict[str, object]]:
    raw_sources = parse_raw_sources(collections)
    by_record: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    titles: dict[tuple[str, str], list[str]] = defaultdict(list)
    truth_concepts: dict[tuple[str, str], set[str]] = defaultdict(set)
    for row in oracle_rows:
        key = (row["collection_id"], row["recipe_id"])
        by_record[key].append(row)
        if row["role"] == "TITLE" and row["editor_english_label"] != "NONE":
            titles[key].append(norm_title(row["editor_english_label"]))
        if row["concept_id"] != "NONE":
            truth_concepts[key].add(row["concept_id"])
    records = []
    for key in sorted(raw_sources):
        title_values = sorted(set(titles.get(key, ())))
        graph = build_graph(by_record[key], raw_sources[key]["raw_words"])
        records.append({
            "collection": key[0], "record": key[1],
            "title": title_values[0] if len(title_values) == 1 else "",
            "single_title": len(title_values) == 1,
            "truth_concepts": truth_concepts.get(key, set()),
            "surface_hash": raw_sources[key]["surface_hash"],
            "graph": graph,
        })
    return records


def score_components(a: dict[str, object], b: dict[str, object], weights: dict[str, float]) -> dict[str, float]:
    size = size_similarity(a, b)
    order = ordered_alignment(a["order_only"], b["order_only"])
    unordered = 0.45 * multiset_jaccard(a["field_degrees"], b["field_degrees"]) + 0.45 * multiset_jaccard(a["entity_degrees"], b["entity_degrees"]) + 0.10 * size
    raw = 0.85 * multiset_jaccard(a["raw_words"], b["raw_words"]) + 0.15 * size
    flow = (
        weights["ordered_fields"] * ordered_alignment(a["field_signatures"], b["field_signatures"])
        + weights["ordered_transitions"] * ordered_alignment(a["transition_signatures"], b["transition_signatures"])
        + weights["entity_paths"] * multiset_jaccard(a["entity_paths"], b["entity_paths"])
        + weights["flow_edges"] * multiset_jaccard(a["flow_edges"], b["flow_edges"])
        + weights["record_size"] * size
    )
    ceiling = 0.85 * set_jaccard(a["global_concepts"], b["global_concepts"]) + 0.15 * size
    return {
        "SIZE_ONLY": size,
        "ORDER_ONLY": 0.90 * order + 0.10 * size,
        "UNORDERED_INCIDENCE": unordered,
        "RAW_OPAQUE_WORD_IDENTITY": raw,
        "ANON_ENTITY_FLOW": flow,
        "GLOBAL_CONCEPT_ID_CEILING": ceiling,
    }


def init_score_worker(candidates: list[dict[str, object]], weights: dict[str, float]) -> None:
    global WORK_CANDIDATES, WORK_WEIGHTS
    WORK_CANDIDATES = candidates
    WORK_WEIGHTS = weights


def score_query_worker(query: dict[str, object]) -> list[dict[str, float]]:
    return [score_components(query["graph"], candidate["graph"], WORK_WEIGHTS) for candidate in WORK_CANDIDATES]


def correct(query: dict[str, object], candidate: dict[str, object]) -> bool:
    return bool(
        query["title"]
        and query["title"] == candidate["title"]
        and len(query["truth_concepts"] & candidate["truth_concepts"]) >= 2
        and query["surface_hash"] != candidate["surface_hash"]
    )


def main() -> int:
    design = json.loads(DESIGN.read_text())
    records = parse_records(design["collections"], read_tsv(ORACLE))
    singles = [record for record in records if record["single_title"]]
    eligible = [
        record for record in singles
        if any(other["collection"] != record["collection"] and correct(record, other) for other in singles)
    ]
    positive_pairs = [
        (a, b)
        for index, a in enumerate(eligible)
        for b in eligible[index + 1:]
        if a["collection"] != b["collection"] and correct(a, b)
    ]
    graphs = [record["graph"] for record in records]
    census_rows = [
        {"metric": "complete_records", "value": len(records), "global_ids_or_forms_exported": "NO"},
        {"metric": "single_title_records", "value": len(singles), "global_ids_or_forms_exported": "NO"},
        {"metric": "eligible_parallel_records", "value": len(eligible), "global_ids_or_forms_exported": "NO"},
        {"metric": "cross_collection_parallel_pairs", "value": len(positive_pairs), "global_ids_or_forms_exported": "NO"},
        {"metric": "parallel_pairs_with_identical_surface_hash", "value": sum(a["surface_hash"] == b["surface_hash"] for a, b in positive_pairs), "global_ids_or_forms_exported": "NO"},
        {"metric": "concept_linked_rows", "value": sum(int(graph["concept_rows"]) for graph in graphs), "global_ids_or_forms_exported": "NO"},
        {"metric": "records_with_concept_link", "value": sum(int(graph["concept_rows"]) > 0 for graph in graphs), "global_ids_or_forms_exported": "NO"},
        {"metric": "records_with_repeated_identity", "value": sum(int(graph["repeated_identity_count"]) > 0 for graph in graphs), "global_ids_or_forms_exported": "NO"},
        {"metric": "records_with_cross_field_identity", "value": sum(int(graph["cross_field_identity_count"]) > 0 for graph in graphs), "global_ids_or_forms_exported": "NO"},
    ]
    write_tsv(CENSUS, census_rows)

    models = design["models"]
    weights = {key: float(value) for key, value in design["entity_flow_weights"].items()}
    retrieval_rows: list[dict[str, object]] = []
    fold_rows: list[dict[str, object]] = []
    rankings: dict[tuple[str, str, str], list[dict[str, object]]] = {}
    for held in design["collections"]:
        queries = [record for record in eligible if record["collection"] == held]
        candidates = [record for record in singles if record["collection"] != held]
        accum = {model: {"top1": 0, "top5": 0, "rr": 0.0} for model in models}
        workers = min(32, max(1, os.cpu_count() or 1), max(1, len(queries)))
        context = mp.get_context("fork")
        with context.Pool(workers, initializer=init_score_worker, initargs=(candidates, weights)) as pool:
            scored_queries = pool.map(score_query_worker, queries, chunksize=1)
        for query, candidate_scores in zip(queries, scored_queries):
            for model in models:
                order = sorted(range(len(candidates)), key=lambda index: (-candidate_scores[index][model], str(candidates[index]["record"])))
                ranked = [candidates[index] for index in order]
                rank = next((index + 1 for index, candidate in enumerate(ranked) if correct(query, candidate)), 0)
                accum[model]["top1"] += int(rank == 1)
                accum[model]["top5"] += int(0 < rank <= 5)
                accum[model]["rr"] += (1 / rank) if 0 < rank <= int(design["retrieval"]["mrr_cutoff"]) else 0.0
                rankings[(str(query["collection"]), str(query["record"]), model)] = ranked[: int(design["retrieval"]["mrr_cutoff"])]
                retrieval_rows.append({
                    "held_collection": held,
                    "query_record": query["record"],
                    "model": model,
                    "candidate_count": len(ranked),
                    "first_correct_rank": rank,
                    "top1_correct": int(rank == 1),
                    "top5_correct": int(0 < rank <= 5),
                    "reciprocal_rank_100": f"{((1/rank) if 0 < rank <= 100 else 0):.9f}",
                    "top_candidate_record": ranked[0]["record"],
                    "concept_title_or_source_form_exported": "NO",
                })
        for model in models:
            count = len(queries)
            fold_rows.append({
                "held_collection": held,
                "model": model,
                "queries": count,
                "top1": int(accum[model]["top1"]),
                "top5": int(accum[model]["top5"]),
                "top1_rate": f"{int(accum[model]['top1'])/max(1,count):.9f}",
                "top5_rate": f"{int(accum[model]['top5'])/max(1,count):.9f}",
                "mrr100": f"{float(accum[model]['rr'])/max(1,count):.9f}",
            })
    write_tsv(RETRIEVAL, retrieval_rows)
    write_tsv(FOLDS, fold_rows)

    aggregates: list[dict[str, object]] = []
    mrr: dict[str, float] = {}
    for model in models:
        rows = [row for row in fold_rows if row["model"] == model]
        count = sum(int(row["queries"]) for row in rows)
        model_mrr = sum(float(row["mrr100"]) * int(row["queries"]) for row in rows) / count
        mrr[model] = model_mrr
        aggregates.append({
            "model": model,
            "selection_eligible": "YES" if model in design["selection_eligible"] else "NO",
            "queries": count,
            "top1": sum(int(row["top1"]) for row in rows),
            "top5": sum(int(row["top5"]) for row in rows),
            "top1_rate": f"{sum(int(row['top1']) for row in rows)/count:.9f}",
            "top5_rate": f"{sum(int(row['top5']) for row in rows)/count:.9f}",
            "mrr100": f"{model_mrr:.9f}",
            "positive_folds_vs_all_controls": "PENDING" if model == "ANON_ENTITY_FLOW" else "NA",
            "inclusive_p": "PENDING" if model == "ANON_ENTITY_FLOW" else "NA",
        })
    by_model = {row["model"]: row for row in aggregates}
    controls = tuple(design["required_controls"])
    observed_gain = mrr["ANON_ENTITY_FLOW"] - max(mrr[control] for control in controls)

    # Precompute reciprocal ranks for every allowed truth bundle in a query's
    # frozen null stratum. This is equivalent to rescanning fixed rankings.
    by_collection: dict[str, list[dict[str, object]]] = defaultdict(list)
    for record in eligible:
        by_collection[str(record["collection"])].append(record)
    possible_truth_rr: dict[tuple[str, str, str, str], float] = {}
    for collection, queries in by_collection.items():
        strata: dict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
        for query in queries:
            strata[(size_bucket(int(query["graph"]["unit_count"])), field_bucket(int(query["graph"]["field_count"])))].append(query)
        for values in strata.values():
            for query in values:
                for bundle in values:
                    for model in (*controls, "ANON_ENTITY_FLOW"):
                        rank = next((i + 1 for i, candidate in enumerate(rankings[(collection, str(query["record"]), model)]) if correct(bundle, candidate)), 0)
                        possible_truth_rr[(collection, str(query["record"]), str(bundle["record"]), model)] = (1 / rank) if rank else 0.0

    worlds = int(design["null"]["worlds"])
    rng = random.Random(int(design["null"]["seed"]))
    exceed = 0
    null_rows = []
    for world in range(worlds):
        assigned: dict[tuple[str, str], str] = {}
        for collection, queries in by_collection.items():
            strata: dict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
            for query in queries:
                strata[(size_bucket(int(query["graph"]["unit_count"])), field_bucket(int(query["graph"]["field_count"])))].append(query)
            for values in strata.values():
                bundles = values[:]
                rng.shuffle(bundles)
                for query, bundle in zip(values, bundles):
                    assigned[(collection, str(query["record"]))] = str(bundle["record"])
        world_mrr = {}
        for model in (*controls, "ANON_ENTITY_FLOW"):
            total = sum(
                possible_truth_rr[(str(query["collection"]), str(query["record"]), assigned[(str(query["collection"]), str(query["record"]))], model)]
                for query in eligible
            )
            world_mrr[model] = total / len(eligible)
        gain = world_mrr["ANON_ENTITY_FLOW"] - max(world_mrr[control] for control in controls)
        exceed += int(gain >= observed_gain - 1e-12)
        null_rows.append({"world": world, "entity_flow_mrr_gain_over_best_control": f"{gain:.9f}"})
    write_tsv(NULL, null_rows)

    positive_folds = 0
    for held in design["collections"]:
        flow = next(float(row["mrr100"]) for row in fold_rows if row["held_collection"] == held and row["model"] == "ANON_ENTITY_FLOW")
        best = max(float(row["mrr100"]) for row in fold_rows if row["held_collection"] == held and row["model"] in controls)
        positive_folds += int(flow > best)
    p_value = (exceed + 1) / (worlds + 1)
    by_model["ANON_ENTITY_FLOW"]["positive_folds_vs_all_controls"] = positive_folds
    by_model["ANON_ENTITY_FLOW"]["inclusive_p"] = f"{p_value:.9f}"
    write_tsv(MODELS, aggregates)

    flow = by_model["ANON_ENTITY_FLOW"]
    supported = (
        float(flow["mrr100"]) > max(float(by_model[name]["mrr100"]) for name in controls)
        and float(flow["top1_rate"]) > max(float(by_model[name]["top1_rate"]) for name in controls)
        and positive_folds >= int(design["gates"]["positive_folds_min"])
        and p_value <= float(design["gates"]["inclusive_p_max"])
    )
    status = "ANONYMOUS_ENTITY_FLOW_CALIBRATED" if supported else "ANONYMOUS_ENTITY_FLOW_NOT_CALIBRATED"
    counter_rows = [
        {"counterexample": "BEST_REQUIRED_CONTROL", "detail": max(controls, key=lambda name: mrr[name]), "effect": f"flow_mrr_gain={observed_gain:.9f}"},
        {"counterexample": "COLLECTION_INSTABILITY", "detail": f"positive_vs_all_controls={positive_folds}/6", "effect": "held-collection"},
        {"counterexample": "RAW_WORD_CONTROL", "detail": f"raw_mrr={mrr['RAW_OPAQUE_WORD_IDENTITY']:.9f}", "effect": "ordinary wording baseline"},
        {"counterexample": "GLOBAL_ID_CEILING", "detail": f"ceiling_mrr={mrr['GLOBAL_CONCEPT_ID_CEILING']:.9f}", "effect": "truth-proximal ineligible ceiling"},
        {"counterexample": "LOCAL_SINGLETONS", "detail": "conceptless elements cannot create recurrence", "effect": "conservative source normalization"},
        {"counterexample": "TARGET_ACCESS", "detail": "GDT327 values not opened or scored in Stage A", "effect": status},
    ]
    write_tsv(COUNTER, counter_rows)

    input_paths = (METHOD, AUDIT, DESIGN, SOURCE_FREEZE, MANIFEST, ORACLE, *(CACHE / f"{collection}.recipes.xml" for collection in design["collections"]))
    output_paths = (CENSUS, FOLDS, RETRIEVAL, MODELS, NULL, COUNTER)
    state = {
        "schema": "GDT342_ENTITY_FLOW_FREEZE_V1",
        "date": "2026-08-18",
        "status": status,
        "representation": "ANON_ENTITY_FLOW",
        "representation_supported": supported,
        "comparator": {"records": len(records), "eligible_records": len(eligible), "parallel_pairs": len(positive_pairs), "positive_folds": positive_folds, "inclusive_p": p_value},
        "target_gate": "OPEN_ONLY_AFTER_PUBLIC_COMPARATOR_PASS" if supported else "STOP_BEFORE_GDT327_ACCESS",
        "voynich_target_values_retained_or_scored": False,
        "global_concept_ids_or_source_forms_exported": False,
        "f84": {"opened": False, "parsed": False, "retained": False, "joined": False, "scored": False},
        "inputs": {str(path.relative_to(ROOT)): sha256_file(path) for path in input_paths},
        "outputs": {str(path.relative_to(ROOT)): sha256_file(path) for path in output_paths},
        "implementation": {str(Path(__file__).relative_to(ROOT)): sha256_file(Path(__file__))},
    }
    state["content_sha256"] = content_hash(state)
    FREEZE.write_bytes(canonical_json_bytes(state))
    result = {
        "schema": "GDT342_COMPARATOR_RESULT_V1",
        "status": status,
        "representation": "ANON_ENTITY_FLOW",
        "representation_supported": supported,
        "records": len(records),
        "eligible_records": len(eligible),
        "parallel_pairs": len(positive_pairs),
        "models": {row["model"]: {"top1": int(row["top1"]), "top5": int(row["top5"]), "mrr100": float(row["mrr100"])} for row in aggregates},
        "positive_folds_vs_all_controls": positive_folds,
        "inclusive_p": p_value,
        "voynich_target_values_retained_or_scored": False,
        "f84": state["f84"],
        "freeze_sha256": sha256_file(FREEZE),
        "inputs": state["inputs"],
        "outputs": {**state["outputs"], str(FREEZE.relative_to(ROOT)): sha256_file(FREEZE)},
        "implementation": state["implementation"],
    }
    result["content_sha256"] = content_hash(result)
    RESULT.write_bytes(canonical_json_bytes(result))

    lines = [
        "# GDT342 comparator report — anonymous entity-flow graphs", "",
        f"Status: **{status}**.", "",
        f"The comparator contains {len(eligible)} wording-distinct eligible records and {len(positive_pairs)} cross-collection parallel pairs. Every concept identity was restarted and renamed inside each record before graph construction.", "",
        "| model | top-1 | top-5 | MRR@100 | positive folds vs all controls | inclusive p |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for row in aggregates:
        lines.append(f"| {row['model']} | {int(row['top1'])}/{row['queries']} ({float(row['top1_rate']):.1%}) | {int(row['top5'])}/{row['queries']} ({float(row['top5_rate']):.1%}) | {float(row['mrr100']):.4f} | {row['positive_folds_vs_all_controls']} | {row['inclusive_p']} |")
    lines += [
        "", "The entity-flow model was frozen before these scores. It must beat size, order-only, unordered incidence, and raw opaque-word identity simultaneously.", "",
        ("The readable comparator passed. The exact representation may now be committed as a freeze before any target join." if supported else "The readable comparator failed its gate. GDT327 remains unopened and Stage B is not run."), "",
        "No concept name, concept ID, source form, semantic role, or word was exported as a graph feature. No Voynich role, meaning, language, plaintext, or translation follows. f84 was not accessed.", "",
    ]
    REPORT.write_text("\n".join(lines), encoding="utf-8")
    print(f"{status} eligible={len(eligible)} pairs={len(positive_pairs)} mrr={float(flow['mrr100']):.6f} best_control={max(mrr[name] for name in controls):.6f} p={p_value:.6f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
