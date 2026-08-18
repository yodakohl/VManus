#!/usr/bin/env python3
"""Calibrate and freeze GDT341 ordered form-blind event graphs."""

from __future__ import annotations

import csv
import hashlib
import json
import math
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

EXP = ROOT / "experiments/yolo/gdt341_ordered_recipe_event_graph"
ART = EXP / "artifacts"
METHOD = EXP / "METHOD.md"
AUDIT = EXP / "SOURCE_AUDIT.md"
DESIGN = ART / "gdt341_comparator_design.json"
SOURCE_FREEZE = ROOT / "gdt176_source_freeze.json"
MANIFEST = ROOT / "gdt176_corema_collection_manifest.tsv"
ORACLE = ROOT / "gdt176_corema_role_oracle.tsv"
CACHE = ROOT / ".gdt176/corema"
PARALLELS = ART / "gdt341_parallel_recipe_census.tsv"
FOLDS = ART / "gdt341_comparator_folds.tsv"
RETRIEVAL = ART / "gdt341_comparator_retrieval.tsv"
MODELS = ART / "gdt341_comparator_models.tsv"
NULL = ART / "gdt341_comparator_null.tsv"
FREEZE = ART / "gdt341_graph_freeze.json"
RESULT = ART / "gdt341_comparator_result.json"
REPORT = EXP / "COMPARATOR_REPORT.md"

NS = {"t": "http://www.tei-c.org/ns/1.0"}
XML_ID = "{http://www.w3.org/XML/1998/namespace}id"
ROLE_TAGS = {"opener", "instruction", "ingredient", "tool", "dish", "name", "closer", "kitchenTip", "householdTip", "servingTip", "time", "dietetics", "alternative", "ref", "unclear"}
ROLE_MAP = {
    "ingredient": "MATERIAL", "dish": "MATERIAL", "name": "MATERIAL",
    "instruction": "OPERATION", "time": "INTERMEDIATE_STATE",
    "servingTip": "APPLICATION", "householdTip": "APPLICATION", "kitchenTip": "APPLICATION",
    "closer": "RESULT_CONDITION", "dietetics": "RESULT_CONDITION",
    "tool": "TOOL", "alternative": "BRANCH", "ref": "BRANCH",
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"empty table {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)


def lname(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def normalized_text(node: ET.Element) -> str:
    return " ".join(" ".join(node.itertext()).lower().split())


def words(node: ET.Element) -> list[str]:
    return re.findall(r"[^\W_]+", normalized_text(node), flags=re.UNICODE)


def direct_words(node: ET.Element) -> list[str]:
    text = " ".join([node.text or ""] + [child.tail or "" for child in node]).lower()
    return re.findall(r"[^\W_]+", text, flags=re.UNICODE)


def opaque(value: str) -> str:
    return hashlib.sha256(("GDT341_OPAQUE_UNIT_V1\0" + value).encode()).hexdigest()[:20]


def norm_title(value: str) -> str:
    return re.sub(r"\W+", " ", value.lower()).strip()


def bucket(value: int) -> int:
    return min(4, max(1, value))


def size_bucket(value: int) -> str:
    if value <= 8: return "01_08"
    if value <= 16: return "09_16"
    if value <= 32: return "17_32"
    return "33_PLUS"


def field_bucket(value: int) -> str:
    if value <= 4: return "01_04"
    if value <= 8: return "05_08"
    if value <= 16: return "09_16"
    return "17_PLUS"


def content_hash(document: dict[str, object]) -> str:
    copy = dict(document); copy.pop("content_sha256", None)
    return hashlib.sha256(canonical_json_bytes(copy)).hexdigest()


def build_graph(units: list[dict[str, str]]) -> dict[str, object]:
    by_field: dict[str, list[str]] = defaultdict(list)
    field_order = []
    roles = []
    for unit in units:
        field = unit["field"]
        if field not in by_field:
            field_order.append(field)
        by_field[field].append(unit["identity"])
        roles.append(unit["oracle_role"])
    identity_fields: dict[str, list[int]] = defaultdict(list)
    for index, field in enumerate(field_order):
        for identity in set(by_field[field]):
            identity_fields[identity].append(index)
    signatures = []
    n_fields = len(field_order)
    for index, field in enumerate(field_order):
        ids = by_field[field]
        unique = set(ids)
        new = sum(min(identity_fields[ident]) == index for ident in unique)
        returning = sum(min(identity_fields[ident]) < index for ident in unique)
        continuing = sum(max(identity_fields[ident]) > index for ident in unique)
        branching = sum(len([x for x in identity_fields[ident] if x > index]) >= 2 for ident in unique)
        signatures.append((bucket(len(ids)), bucket(new), bucket(returning), bucket(continuing), bucket(branching), int(index == n_fields - 1)))
    edges = []
    for fields in identity_fields.values():
        if len(fields) < 2:
            continue
        for source, target in zip(fields, fields[1:]):
            edges.append((min(3, 4 * source // max(1, n_fields)), min(3, 4 * target // max(1, n_fields)), bucket(len(fields))))
    transitions = Counter(zip(roles, roles[1:]))
    return {
        "field_signatures": signatures, "repeat_edges": Counter(edges),
        "unit_count": len(units), "field_count": n_fields,
        "identities": set(unit["identity"] for unit in units),
        "oracle_transitions": transitions,
    }


def parse_records(collections: list[str], oracle_rows: list[dict[str, str]]) -> list[dict[str, object]]:
    title_map: dict[tuple[str, str], list[str]] = defaultdict(list)
    concept_map: dict[tuple[str, str], set[str]] = defaultdict(set)
    for row in oracle_rows:
        key = (row["collection_id"], row["recipe_id"])
        if row["role"] == "TITLE" and row["editor_english_label"] != "NONE":
            title_map[key].append(norm_title(row["editor_english_label"]))
        if row["concept_id"] != "NONE":
            concept_map[key].add(row["concept_id"])
    output = []
    for collection in collections:
        root = ET.parse(CACHE / f"{collection}.recipes.xml").getroot()
        for ordinal, recipe in enumerate(root.findall('.//*[@type="recipe"]', NS), 1):
            recipe_id = recipe.get(XML_ID, f"{collection}.ordinal{ordinal}")
            key = (collection, recipe_id)
            titles = sorted(set(title_map.get(key, ())))
            instructions = recipe.findall(".//t:instruction", NS)
            instruction_index = {id(node): i for i, node in enumerate(instructions, 1)}
            parent = {id(child): node for node in recipe.iter() for child in node}
            units = []
            for element_ordinal, node in enumerate(recipe.iter(), 1):
                tag = lname(node.tag)
                if tag not in ROLE_TAGS:
                    continue
                ws = words(node)
                if tag in {"ingredient", "tool", "dish", "name"}:
                    raw = node.get("commodity") or " ".join(ws) or "EMPTY"
                else:
                    dw = direct_words(node) or ws
                    raw = dw[0] if dw else "EMPTY"
                ancestor = node if tag == "instruction" else parent.get(id(node))
                while ancestor is not None and lname(ancestor.tag) != "instruction":
                    ancestor = parent.get(id(ancestor))
                instruction = instruction_index.get(id(ancestor), 0) if ancestor is not None else 0
                field = f"I{instruction}" if instruction else f"E{element_ordinal}"
                units.append({"identity": opaque(raw), "field": field, "oracle_role": ROLE_MAP.get(tag, "OTHER")})
            if not units:
                continue
            output.append({
                "collection": collection, "record": recipe_id,
                "title": titles[0] if len(titles) == 1 else "",
                "single_title": len(titles) == 1,
                "concepts": concept_map.get(key, set()),
                "surface_hash": hashlib.sha256(normalized_text(recipe).encode()).hexdigest(),
                "graph": build_graph(units),
            })
    return output


def multiset_jaccard(a: Counter, b: Counter) -> float:
    keys = set(a) | set(b)
    if not keys: return 1.0
    inter = sum(min(a[k], b[k]) for k in keys)
    union = sum(max(a[k], b[k]) for k in keys)
    return inter / max(1, union)


def set_jaccard(a: set, b: set) -> float:
    return len(a & b) / max(1, len(a | b))


def size_similarity(a: dict[str, object], b: dict[str, object]) -> float:
    du = abs(math.log2(1 + int(a["unit_count"])) - math.log2(1 + int(b["unit_count"])))
    df = abs(math.log2(1 + int(a["field_count"])) - math.log2(1 + int(b["field_count"])))
    return math.exp(-(du + df))


def field_similarity(a: tuple[int, ...], b: tuple[int, ...]) -> float:
    diffs = [abs(a[i] - b[i]) / 3 for i in range(5)] + [float(a[5] != b[5])]
    return max(0.0, 1 - sum(diffs) / len(diffs))


def ordered_alignment(a: list[tuple[int, ...]], b: list[tuple[int, ...]]) -> float:
    if not a or not b: return float(not a and not b)
    dp = [[0.0] * (len(b) + 1) for _ in range(len(a) + 1)]
    for i in range(1, len(a) + 1):
        for j in range(1, len(b) + 1):
            dp[i][j] = max(dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1] + field_similarity(a[i - 1], b[j - 1]))
    return dp[-1][-1] / max(len(a), len(b))


def score_components(a: dict[str, object], b: dict[str, object]) -> dict[str, float]:
    size = size_similarity(a, b)
    ca = Counter(a["field_signatures"]); cb = Counter(b["field_signatures"])
    unordered = 0.8 * multiset_jaccard(ca, cb) + 0.2 * multiset_jaccard(a["repeat_edges"], b["repeat_edges"])
    ordered = ordered_alignment(a["field_signatures"], b["field_signatures"])
    repeat = multiset_jaccard(a["repeat_edges"], b["repeat_edges"])
    return {
        "SIZE_ONLY": size,
        "UNORDERED_GRAPH": 0.9 * unordered + 0.1 * size,
        "ORDERED_FIELD_GRAPH": 0.9 * ordered + 0.1 * size,
        "ORDERED_REPEAT_GRAPH": 0.7 * ordered + 0.2 * repeat + 0.1 * size,
        "GLOBAL_OPAQUE_ID_CEILING": 0.8 * set_jaccard(a["identities"], b["identities"]) + 0.2 * size,
    }


def correct(query: dict[str, object], candidate: dict[str, object]) -> bool:
    return bool(query["title"] and query["title"] == candidate["title"] and len(query["concepts"] & candidate["concepts"]) >= 2 and query["surface_hash"] != candidate["surface_hash"])


def transition_jaccard(a: dict[str, object], b: dict[str, object]) -> float:
    return multiset_jaccard(a["oracle_transitions"], b["oracle_transitions"])


def main() -> int:
    design = json.loads(DESIGN.read_text())
    oracle = read_tsv(ORACLE)
    records = parse_records(design["collections"], oracle)
    singles = [record for record in records if record["single_title"]]
    eligible = [record for record in singles if any(other["collection"] != record["collection"] and correct(record, other) for other in singles)]
    positive_pairs = []
    for i, a in enumerate(eligible):
        for b in eligible[i + 1:]:
            if a["collection"] != b["collection"] and correct(a, b):
                positive_pairs.append((a, b))
    census = [{
        "metric": "complete_records", "value": len(records), "forms_used_as_predictors": "NO",
    }, {
        "metric": "single_title_records", "value": len(singles), "forms_used_as_predictors": "NO",
    }, {
        "metric": "eligible_parallel_records", "value": len(eligible), "forms_used_as_predictors": "NO",
    }, {
        "metric": "cross_collection_parallel_pairs", "value": len(positive_pairs), "forms_used_as_predictors": "NO",
    }, {
        "metric": "parallel_pairs_with_identical_surface_hash", "value": sum(a["surface_hash"] == b["surface_hash"] for a, b in positive_pairs), "forms_used_as_predictors": "NO",
    }]
    write_tsv(PARALLELS, census)

    models = design["models"]
    retrieval_rows = []
    fold_rows = []
    rankings: dict[tuple[str, str], list[dict[str, object]]] = {}
    for held in design["collections"]:
        queries = [record for record in eligible if record["collection"] == held]
        candidates = [record for record in singles if record["collection"] != held]
        accumulators = {model: {"top1": 0, "top5": 0, "reciprocal": 0.0, "transition": 0.0} for model in models}
        for query in queries:
            scored = [(candidate, score_components(query["graph"], candidate["graph"])) for candidate in candidates]
            for model in models:
                ranked = [candidate for candidate, _ in sorted(scored, key=lambda item: (-item[1][model], str(item[0]["record"])))]
                rank = next((i + 1 for i, candidate in enumerate(ranked) if correct(query, candidate)), 0)
                accumulators[model]["top1"] += int(rank == 1); accumulators[model]["top5"] += int(0 < rank <= 5)
                accumulators[model]["reciprocal"] += (1 / rank) if 0 < rank <= int(design["retrieval"]["mrr_cutoff"]) else 0.0
                accumulators[model]["transition"] += transition_jaccard(query["graph"], ranked[0]["graph"])
                rankings[(str(query["collection"]), str(query["record"]), model)] = ranked[: int(design["retrieval"]["mrr_cutoff"])]
                retrieval_rows.append({
                    "held_collection": held, "query_record": query["record"], "model": model,
                    "candidate_count": len(ranked), "first_correct_rank": rank,
                    "top1_correct": int(rank == 1), "top5_correct": int(0 < rank <= 5),
                    "reciprocal_rank_100": f"{((1/rank) if 0 < rank <= 100 else 0):.9f}",
                    "top_candidate_record": ranked[0]["record"],
                    "top_candidate_transition_jaccard": f"{transition_jaccard(query['graph'], ranked[0]['graph']):.9f}",
                    "title_or_concept_exported": "NO",
                })
        for model in models:
            top1 = int(accumulators[model]["top1"]); top5 = int(accumulators[model]["top5"])
            reciprocal = float(accumulators[model]["reciprocal"]); transition_sum = float(accumulators[model]["transition"])
            fold_rows.append({
                "held_collection": held, "model": model, "queries": len(queries),
                "top1": top1, "top5": top5,
                "top1_rate": f"{top1/max(1,len(queries)):.9f}",
                "top5_rate": f"{top5/max(1,len(queries)):.9f}",
                "mrr100": f"{reciprocal/max(1,len(queries)):.9f}",
                "mean_top1_transition_jaccard": f"{transition_sum/max(1,len(queries)):.9f}",
            })
    write_tsv(RETRIEVAL, retrieval_rows)
    write_tsv(FOLDS, fold_rows)

    aggregate_rows = []
    aggregate_mrr = {}
    for model in models:
        selected = [row for row in fold_rows if row["model"] == model]
        queries = sum(int(row["queries"]) for row in selected)
        mrr = sum(float(row["mrr100"]) * int(row["queries"]) for row in selected) / queries
        aggregate_mrr[model] = mrr
        aggregate_rows.append({
            "model": model, "selection_eligible": "YES" if model in design["selection_eligible"] else "NO",
            "queries": queries, "top1": sum(int(row["top1"]) for row in selected),
            "top5": sum(int(row["top5"]) for row in selected),
            "top1_rate": f"{sum(int(row['top1']) for row in selected)/queries:.9f}",
            "top5_rate": f"{sum(int(row['top5']) for row in selected)/queries:.9f}",
            "mrr100": f"{mrr:.9f}",
            "positive_folds_vs_both_controls": "PENDING", "local_p": "PENDING", "max_two_p": "PENDING",
            "mean_top1_transition_jaccard": f"{sum(float(row['mean_top1_transition_jaccard'])*int(row['queries']) for row in selected)/queries:.9f}",
        })
    selected_model = min(design["selection_eligible"], key=lambda model: (-aggregate_mrr[model], model))
    controls = ("SIZE_ONLY", "UNORDERED_GRAPH")
    observed_gain = {
        model: aggregate_mrr[model] - max(aggregate_mrr[control] for control in controls)
        for model in design["selection_eligible"]
    }

    # Fixed-ranking truth-bundle null. Full truth bundles, rather than titles
    # alone, move within the frozen size/field opportunity strata.
    by_collection = {collection: [record for record in eligible if record["collection"] == collection] for collection in design["collections"]}
    rng = random.Random(int(design["null"]["seed"]))
    exceed_local = Counter(); exceed_max = Counter(); null_rows = []
    worlds = int(design["null"]["worlds"])
    for world in range(worlds):
        assigned: dict[tuple[str, str], dict[str, object]] = {}
        for collection, queries in by_collection.items():
            strata: dict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
            for query in queries:
                strata[(size_bucket(int(query["graph"]["unit_count"])), field_bucket(int(query["graph"]["field_count"])))].append(query)
            for values in strata.values():
                truth = values[:]; rng.shuffle(truth)
                for query, bundle in zip(values, truth): assigned[(collection, str(query["record"]))] = bundle
        world_mrr = {}
        for model in (*controls, *design["selection_eligible"]):
            total = 0.0
            for query in eligible:
                bundle = assigned[(str(query["collection"]), str(query["record"]))]
                ranked = rankings[(str(query["collection"]), str(query["record"]), model)]
                rank = next((i + 1 for i, candidate in enumerate(ranked) if correct(bundle, candidate)), 0)
                total += (1 / rank) if rank else 0.0
            world_mrr[model] = total / len(eligible)
        gains = {model: world_mrr[model] - max(world_mrr[c] for c in controls) for model in design["selection_eligible"]}
        maximum = max(gains.values())
        null_rows.append({"world": world, "max_two_mrr_gain": f"{maximum:.9f}"})
        for model in design["selection_eligible"]:
            exceed_local[model] += int(gains[model] >= observed_gain[model] - 1e-12)
            exceed_max[model] += int(maximum >= observed_gain[model] - 1e-12)
    write_tsv(NULL, null_rows)

    by_model_row = {row["model"]: row for row in aggregate_rows}
    for model in design["selection_eligible"]:
        positive_folds = 0
        for held in design["collections"]:
            m = next(float(row["mrr100"]) for row in fold_rows if row["held_collection"] == held and row["model"] == model)
            best_control = max(float(row["mrr100"]) for row in fold_rows if row["held_collection"] == held and row["model"] in controls)
            positive_folds += int(m > best_control)
        by_model_row[model]["positive_folds_vs_both_controls"] = positive_folds
        by_model_row[model]["local_p"] = f"{(exceed_local[model]+1)/(worlds+1):.9f}"
        by_model_row[model]["max_two_p"] = f"{(exceed_max[model]+1)/(worlds+1):.9f}"
    for control in controls + ("GLOBAL_OPAQUE_ID_CEILING",):
        by_model_row[control]["positive_folds_vs_both_controls"] = "NA"
        by_model_row[control]["local_p"] = "NA"
        by_model_row[control]["max_two_p"] = "NA"
    write_tsv(MODELS, aggregate_rows)

    chosen = by_model_row[selected_model]
    supported = (
        float(chosen["mrr100"]) > max(float(by_model_row[c]["mrr100"]) for c in controls)
        and float(chosen["top1_rate"]) > max(float(by_model_row[c]["top1_rate"]) for c in controls)
        and int(chosen["positive_folds_vs_both_controls"]) >= int(design["gates"]["positive_folds_min"])
        and float(chosen["max_two_p"]) <= float(design["gates"]["max_two_p_max"])
    )
    status = "ORDERED_RECIPE_GRAPH_CALIBRATED" if supported else "NO_COMPARATOR_GRAPH_CALIBRATION"
    inputs = [METHOD, AUDIT, DESIGN, SOURCE_FREEZE, MANIFEST, ORACLE] + [CACHE / f"{c}.recipes.xml" for c in design["collections"]]
    freeze = {
        "schema": "GDT341_GRAPH_FREEZE_V1", "status": status,
        "selected_model": selected_model, "selected_model_supported": supported,
        "representation": {
            "field_signature": design["field_signature"], "count_buckets": design["count_buckets"],
            "weights": design["ordered_repeat_weights"], "identity_scope": "LOCAL_EQUALITY_ONLY",
            "order_retained": True, "repeat_edges_retained": selected_model == "ORDERED_REPEAT_GRAPH",
        },
        "comparator_evidence": {key: chosen[key] for key in ("queries", "top1", "top5", "top1_rate", "top5_rate", "mrr100", "positive_folds_vs_both_controls", "max_two_p", "mean_top1_transition_jaccard")},
        "inputs": {str(path.relative_to(ROOT)): sha256_file(path) for path in inputs},
        "outputs": {str(path.relative_to(ROOT)): sha256_file(path) for path in (PARALLELS, FOLDS, RETRIEVAL, MODELS, NULL)},
        "implementation": {str(Path(__file__).relative_to(ROOT)): sha256_file(Path(__file__))},
        "voynich_tuple_values_retained_or_scored": False,
        "f84": {"opened": False, "parsed": False, "retained": False, "joined": False, "scored": False},
        "claim_ceiling": "External form-blind ordered recipe-graph retrieval only; no Voynich semantics.",
    }
    freeze["content_sha256"] = content_hash(freeze); FREEZE.write_bytes(canonical_json_bytes(freeze))
    result = {
        "schema": "GDT341_COMPARATOR_RESULT_V1", "status": status,
        "records": len(records), "eligible_parallel_records": len(eligible), "parallel_pairs": len(positive_pairs),
        "selected_model": selected_model, "selected_model_supported": supported,
        "freeze_sha256": sha256_file(FREEZE), "inputs": freeze["inputs"],
        "outputs": {**freeze["outputs"], str(FREEZE.relative_to(ROOT)): sha256_file(FREEZE)},
        "implementation": freeze["implementation"], "voynich_tuple_values_retained_or_scored": False, "f84": freeze["f84"],
    }
    result["content_sha256"] = content_hash(result); RESULT.write_bytes(canonical_json_bytes(result))

    lines = ["# GDT341 comparator report — ordered anonymous recipe graphs", "", f"Status: **{status}**.", "",
             f"The source-only census contains {len(eligible)} wording-distinct eligible records and {len(positive_pairs)} cross-collection parallel pairs. Titles, concepts, roles, and source forms were hidden during ranking.", "",
             "| model | top-1 | top-5 | MRR@100 | positive folds vs both controls | max-two p | hidden transition Jaccard |", "|---|---:|---:|---:|---:|---:|---:|"]
    for row in aggregate_rows:
        lines.append(f"| {row['model']} | {int(row['top1'])}/{row['queries']} ({float(row['top1_rate']):.1%}) | {int(row['top5'])}/{row['queries']} ({float(row['top5_rate']):.1%}) | {float(row['mrr100']):.4f} | {row['positive_folds_vs_both_controls']} | {row['max_two_p']} | {float(row['mean_top1_transition_jaccard']):.3f} |")
    lines += ["", f"Selected representation: **{selected_model}**.", "",
              "A successful result means that order/equality topology recovers known external parallels better than record size and an unordered graph. Hidden event-transition agreement is a post-ranking calibration, not a graph input.", "",
              "No Voynich record or tuple value was read or scored in Stage A. No semantic role, word, language, plaintext, or translation follows; f84 was not accessed.", ""]
    REPORT.write_text("\n".join(lines), encoding="utf-8")
    print(f"{status} selected={selected_model} eligible={len(eligible)} pairs={len(positive_pairs)} mrr={float(chosen['mrr100']):.4f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
