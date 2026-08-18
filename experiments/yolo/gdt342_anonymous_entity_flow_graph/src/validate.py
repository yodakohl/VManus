#!/usr/bin/env python3
"""Independent source/control/accounting validator for GDT342 Stage A."""

from __future__ import annotations

import csv
import hashlib
import itertools
import json
import math
import re
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from pathlib import Path


def find_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("repository root not found")


ROOT = find_root(Path(__file__).resolve())
EXP = ROOT / "experiments/yolo/gdt342_anonymous_entity_flow_graph"
ART = EXP / "artifacts"
DESIGN = ART / "gdt342_comparator_design.json"
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
VALIDATION = ART / "gdt342_comparator_validation.json"
NS = {"t": "http://www.tei-c.org/ns/1.0"}
XML_ID = "{http://www.w3.org/XML/1998/namespace}id"
ROLE_TAGS = {
    "opener", "instruction", "ingredient", "tool", "dish", "name",
    "closer", "kitchenTip", "householdTip", "servingTip", "time",
    "dietetics", "alternative", "ref", "unclear",
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def canonical(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode()


def content_hash(document: dict[str, object]) -> str:
    copy = dict(document)
    copy.pop("content_sha256", None)
    return hashlib.sha256(canonical(copy)).hexdigest()


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


def multiset_jaccard(a: Counter, b: Counter) -> float:
    keys = set(a) | set(b)
    if not keys:
        return 1.0
    return sum(min(a[k], b[k]) for k in keys) / max(1, sum(max(a[k], b[k]) for k in keys))


def size_similarity(a: dict[str, object], b: dict[str, object]) -> float:
    du = abs(math.log2(1 + int(a["unit_count"])) - math.log2(1 + int(b["unit_count"])))
    df = abs(math.log2(1 + int(a["field_count"])) - math.log2(1 + int(b["field_count"])))
    return math.exp(-(du + df))


def raw_score(a: dict[str, object], b: dict[str, object]) -> float:
    return 0.85 * multiset_jaccard(a["raw_words"], b["raw_words"]) + 0.15 * size_similarity(a, b)


def correct(a: dict[str, object], b: dict[str, object]) -> bool:
    return bool(a["title"] and a["title"] == b["title"] and len(a["concepts"] & b["concepts"]) >= 2 and a["surface_hash"] != b["surface_hash"])


def main() -> int:
    checks: list[dict[str, object]] = []

    def check(name: str, condition: bool, detail: object = "") -> None:
        checks.append({"check": name, "pass": bool(condition), "detail": str(detail)})
        if not condition:
            raise AssertionError(f"{name}: {detail}")

    design = json.loads(DESIGN.read_text())
    freeze = json.loads(FREEZE.read_text())
    result = json.loads(RESULT.read_text())
    oracle = read_tsv(ORACLE)
    by_record: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    titles: dict[tuple[str, str], list[str]] = defaultdict(list)
    concepts: dict[tuple[str, str], set[str]] = defaultdict(set)
    for row in oracle:
        key = (row["collection_id"], row["recipe_id"])
        by_record[key].append(row)
        if row["role"] == "TITLE" and row["editor_english_label"] != "NONE":
            titles[key].append(norm_title(row["editor_english_label"]))
        if row["concept_id"] != "NONE":
            concepts[key].add(row["concept_id"])

    raw_sources: dict[tuple[str, str], dict[str, object]] = {}
    for collection in design["collections"]:
        root = ET.parse(CACHE / f"{collection}.recipes.xml").getroot()
        for ordinal, recipe in enumerate(root.findall('.//*[@type="recipe"]', NS), 1):
            record = recipe.get(XML_ID, f"{collection}.ordinal{ordinal}")
            raw = Counter()
            for node in recipe.iter():
                tag = lname(node.tag)
                if tag not in ROLE_TAGS or tag == "title":
                    continue
                source_tokens = words(node) if tag in {"ingredient", "tool", "dish", "name"} else direct_words(node)
                for token in source_tokens or ["EMPTY"]:
                    raw[opaque_word(token)] += 1
            raw_sources[(collection, record)] = {"raw_words": raw, "surface_hash": hashlib.sha256(normalized_text(recipe).encode()).hexdigest()}

    records = []
    concept_rows = 0
    records_with_concept = 0
    records_with_repeat = 0
    records_with_cross_field = 0
    for key in sorted(raw_sources):
        rows = sorted(by_record[key], key=lambda row: int(row["element_ordinal"]))
        instruction_counter = 0
        fields = set()
        concept_fields: dict[str, set[str]] = defaultdict(set)
        unit_count = 0
        for row in rows:
            if row["role"] == "TITLE":
                continue
            unit_count += 1
            ordinal = int(row["element_ordinal"])
            parent = int(row["parent_instruction_ordinal"])
            if row["role"] == "INSTRUCTION":
                instruction_counter += 1
                field = f"I{instruction_counter}"
            elif parent:
                field = f"I{parent}"
            else:
                field = f"E{ordinal}"
            fields.add(field)
            if row["concept_id"] != "NONE":
                concept_rows += 1
                concept_fields[row["concept_id"]].add(field)
        records_with_concept += int(bool(concept_fields))
        repeated_counts = Counter(row["concept_id"] for row in rows if row["role"] != "TITLE" and row["concept_id"] != "NONE")
        records_with_repeat += int(any(value >= 2 for value in repeated_counts.values()))
        records_with_cross_field += int(any(len(value) >= 2 for value in concept_fields.values()))
        title_values = sorted(set(titles.get(key, ())))
        records.append({
            "collection": key[0], "record": key[1],
            "title": title_values[0] if len(title_values) == 1 else "",
            "single_title": len(title_values) == 1,
            "concepts": concepts.get(key, set()),
            "surface_hash": raw_sources[key]["surface_hash"],
            "raw_words": raw_sources[key]["raw_words"],
            "unit_count": unit_count, "field_count": len(fields),
        })
    singles = [record for record in records if record["single_title"]]
    eligible = [record for record in singles if any(other["collection"] != record["collection"] and correct(record, other) for other in singles)]
    pairs = [(a, b) for a, b in itertools.combinations(eligible, 2) if a["collection"] != b["collection"] and correct(a, b)]
    check("complete_records", len(records) == 1136, len(records))
    check("single_title_records", len(singles) == 1115, len(singles))
    check("eligible_records", len(eligible) == 688, len(eligible))
    check("parallel_pairs", len(pairs) == 657, len(pairs))
    check("different_surfaces", all(a["surface_hash"] != b["surface_hash"] for a, b in pairs))
    check("concept_rows", concept_rows == 13612, concept_rows)
    check("records_with_concept", records_with_concept == 1134, records_with_concept)
    check("records_with_repeat", records_with_repeat == 989, records_with_repeat)
    check("records_with_cross_field", records_with_cross_field == 983, records_with_cross_field)
    census = {row["metric"]: int(row["value"]) for row in read_tsv(CENSUS)}
    expected_census = {
        "complete_records": 1136, "single_title_records": 1115,
        "eligible_parallel_records": 688, "cross_collection_parallel_pairs": 657,
        "parallel_pairs_with_identical_surface_hash": 0,
        "concept_linked_rows": 13612, "records_with_concept_link": 1134,
        "records_with_repeated_identity": 989, "records_with_cross_field_identity": 983,
    }
    check("census_export", census == expected_census, census)

    # Independently reconstruct the corrected diplomatic-token baseline. This
    # catches accidental use of CoReMA commodity/Q IDs as supposed raw words.
    exported_retrieval = read_tsv(RETRIEVAL)
    raw_export = {(row["held_collection"], row["query_record"]): row for row in exported_retrieval if row["model"] == "RAW_OPAQUE_WORD_IDENTITY"}
    independent_top1 = independent_top5 = 0
    independent_rr = 0.0
    for query in eligible:
        candidates = [record for record in singles if record["collection"] != query["collection"]]
        ranked = sorted(candidates, key=lambda candidate: (-raw_score(query, candidate), str(candidate["record"])))
        rank = next((index + 1 for index, candidate in enumerate(ranked) if correct(query, candidate)), 0)
        independent_top1 += int(rank == 1)
        independent_top5 += int(0 < rank <= 5)
        independent_rr += (1 / rank) if 0 < rank <= 100 else 0.0
        exported = raw_export[(str(query["collection"]), str(query["record"]))]
        check(f"raw_rank:{query['record']}", int(exported["first_correct_rank"]) == rank, rank)
    check("raw_top1", independent_top1 == 538, independent_top1)
    check("raw_top5", independent_top5 == 578, independent_top5)
    check("raw_mrr", math.isclose(independent_rr / len(eligible), 0.807524218, abs_tol=5e-10), independent_rr / len(eligible))

    folds = read_tsv(FOLDS)
    retrieval = read_tsv(RETRIEVAL)
    models = read_tsv(MODELS)
    null = read_tsv(NULL)
    counter = read_tsv(COUNTER)
    check("fold_rows", len(folds) == 36, len(folds))
    check("retrieval_rows", len(retrieval) == 688 * 6, len(retrieval))
    check("model_rows", len(models) == 6, len(models))
    check("null_worlds", len(null) == 2048, len(null))
    check("counterexamples", len(counter) == 6, len(counter))
    check("no_export_flags", all(row["concept_title_or_source_form_exported"] == "NO" for row in retrieval))
    by_model = {row["model"]: row for row in models}
    for model in design["models"]:
        selected = [row for row in retrieval if row["model"] == model]
        check(f"queries:{model}", len(selected) == 688, len(selected))
        check(f"top1:{model}", sum(int(row["top1_correct"]) for row in selected) == int(by_model[model]["top1"]))
        check(f"top5:{model}", sum(int(row["top5_correct"]) for row in selected) == int(by_model[model]["top5"]))
        measured_mrr = sum(float(row["reciprocal_rank_100"]) for row in selected) / len(selected)
        check(f"mrr:{model}", math.isclose(measured_mrr, float(by_model[model]["mrr100"]), abs_tol=1e-8), measured_mrr)
    controls = design["required_controls"]
    flow = by_model["ANON_ENTITY_FLOW"]
    observed_gain = float(flow["mrr100"]) - max(float(by_model[name]["mrr100"]) for name in controls)
    reconstructed_p = (1 + sum(float(row["entity_flow_mrr_gain_over_best_control"]) >= observed_gain - 1e-12 for row in null)) / (len(null) + 1)
    check("inclusive_p", math.isclose(reconstructed_p, float(flow["inclusive_p"]), abs_tol=5e-10), reconstructed_p)
    positive_folds = 0
    for held in design["collections"]:
        candidate = next(float(row["mrr100"]) for row in folds if row["held_collection"] == held and row["model"] == "ANON_ENTITY_FLOW")
        best = max(float(row["mrr100"]) for row in folds if row["held_collection"] == held and row["model"] in controls)
        positive_folds += int(candidate > best)
    check("positive_folds", positive_folds == int(flow["positive_folds_vs_all_controls"]), positive_folds)
    supported = (
        float(flow["mrr100"]) > max(float(by_model[name]["mrr100"]) for name in controls)
        and float(flow["top1_rate"]) > max(float(by_model[name]["top1_rate"]) for name in controls)
        and positive_folds >= int(design["gates"]["positive_folds_min"])
        and reconstructed_p <= float(design["gates"]["inclusive_p_max"])
    )
    status = "ANONYMOUS_ENTITY_FLOW_CALIBRATED" if supported else "ANONYMOUS_ENTITY_FLOW_NOT_CALIBRATED"
    check("decision", status == freeze["status"] == result["status"], status)
    check("representation", freeze["representation"] == result["representation"] == "ANON_ENTITY_FLOW")
    check("target_stop", freeze["target_gate"] == "STOP_BEFORE_GDT327_ACCESS" and result["voynich_target_values_retained_or_scored"] is False)
    check("f84_false", all(value is False for value in freeze["f84"].values()) and all(value is False for value in result["f84"].values()))
    for path, digest in {**freeze["inputs"], **freeze["outputs"], **freeze["implementation"]}.items():
        check(f"freeze_hash:{path}", sha(ROOT / path) == digest)
    for path, digest in {**result["inputs"], **result["outputs"], **result["implementation"]}.items():
        check(f"result_hash:{path}", sha(ROOT / path) == digest)
    check("freeze_content_hash", content_hash(freeze) == freeze["content_sha256"])
    check("result_content_hash", content_hash(result) == result["content_sha256"])
    validation = {
        "schema": "GDT342_COMPARATOR_VALIDATION_V1",
        "status": "PASS",
        "checks_passed": len(checks),
        "checks_failed": 0,
        "result_sha256": sha(RESULT),
        "freeze_sha256": sha(FREEZE),
        "source_reconstruction": {"records": len(records), "eligible": len(eligible), "pairs": len(pairs), "concept_rows": concept_rows},
        "raw_diplomatic_control_reconstruction": {"top1": independent_top1, "top5": independent_top5, "mrr100": independent_rr / len(eligible)},
        "decision_reconstruction": {"status": status, "positive_folds": positive_folds, "inclusive_p": reconstructed_p},
        "scope": "Independent source truth/capacity census, full diplomatic-token raw-control rerank, exported score arithmetic, null decision, hashes, no-target state, and f84 flags. Candidate graph pair similarities are not independently recomputed.",
        "checks": checks,
    }
    validation["content_sha256"] = content_hash(validation)
    VALIDATION.write_bytes(canonical(validation))
    print(f"PASS {len(checks)}/{len(checks)} {status}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
