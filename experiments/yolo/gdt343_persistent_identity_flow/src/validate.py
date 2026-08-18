#!/usr/bin/env python3
"""Independent source/control/accounting validator for GDT343 Stage A."""

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
EXP = ROOT / "experiments/yolo/gdt343_persistent_identity_flow"
ART = EXP / "artifacts"
DESIGN = ART / "gdt343_comparator_design.json"
ORACLE = ROOT / "gdt176_corema_role_oracle.tsv"
CACHE = ROOT / ".gdt176/corema"
CENSUS = ART / "gdt343_source_census.tsv"
FOLDS = ART / "gdt343_comparator_folds.tsv"
RETRIEVAL = ART / "gdt343_comparator_retrieval.tsv"
MODELS = ART / "gdt343_comparator_models.tsv"
NULL = ART / "gdt343_comparator_null.tsv"
FREEZE = ART / "gdt343_flow_freeze.json"
RESULT = ART / "gdt343_comparator_result.json"
COUNTER = ART / "gdt343_counterexamples.tsv"
VALIDATION = ART / "gdt343_comparator_validation.json"
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
    return hashlib.sha256(("GDT343_RAW_WORD_CONTROL_V1\0" + value).encode()).hexdigest()[:20]


def opaque_concept(value: str) -> str:
    return hashlib.sha256(("GDT343_GLOBAL_CONCEPT_V1\0" + value).encode()).hexdigest()[:20]


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


def set_jaccard(a: set[str], b: set[str]) -> float:
    return len(a & b) / max(1, len(a | b))


def identity_score(a: dict[str, object], b: dict[str, object]) -> float:
    return 0.75 * multiset_jaccard(a["concept_multiset"], b["concept_multiset"]) + 0.15 * set_jaccard(a["global_concepts"], b["global_concepts"]) + 0.10 * size_similarity(a, b)


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
        concept_occurrences: list[str] = []
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
                concept_occurrences.append(opaque_concept(row["concept_id"]))
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
            "concept_multiset": Counter(concept_occurrences),
            "global_concepts": set(concept_occurrences),
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

    # Independently reconstruct both identity-only controls. This catches both
    # accidental use of CoReMA commodity/Q IDs as supposed raw words and any
    # accidental record-local anonymization of the globally persistent IDs.
    exported_retrieval = read_tsv(RETRIEVAL)
    independent: dict[str, dict[str, float | int]] = {}
    for model, score_fn, expected in (
        ("RAW_OPAQUE_WORD_IDENTITY", raw_score, (538, 578, 0.807524218)),
        ("GLOBAL_ANON_CONCEPT_IDENTITY", identity_score, (570, 644, 0.875523363)),
    ):
        export = {(row["held_collection"], row["query_record"]): row for row in exported_retrieval if row["model"] == model}
        top1 = top5 = 0
        rr = 0.0
        for query in eligible:
            candidates = [record for record in singles if record["collection"] != query["collection"]]
            ranked = sorted(candidates, key=lambda candidate: (-score_fn(query, candidate), str(candidate["record"])))
            rank = next((index + 1 for index, candidate in enumerate(ranked) if correct(query, candidate)), 0)
            top1 += int(rank == 1)
            top5 += int(0 < rank <= 5)
            rr += (1 / rank) if 0 < rank <= 100 else 0.0
            exported = export[(str(query["collection"]), str(query["record"]))]
            check(f"rank:{model}:{query['record']}", int(exported["first_correct_rank"]) == rank, rank)
        mrr = rr / len(eligible)
        check(f"independent_top1:{model}", top1 == expected[0], top1)
        check(f"independent_top5:{model}", top5 == expected[1], top5)
        check(f"independent_mrr:{model}", math.isclose(mrr, expected[2], abs_tol=5e-10), mrr)
        independent[model] = {"top1": top1, "top5": top5, "mrr100": mrr}

    folds = read_tsv(FOLDS)
    retrieval = read_tsv(RETRIEVAL)
    models = read_tsv(MODELS)
    null = read_tsv(NULL)
    counter = read_tsv(COUNTER)
    check("fold_rows", len(folds) == 18, len(folds))
    check("retrieval_rows", len(retrieval) == 688 * 3, len(retrieval))
    check("model_rows", len(models) == 3, len(models))
    check("null_worlds", len(null) == 4096, len(null))
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
    baseline = by_model[design["gates"]["baseline"]]
    flow = by_model[design["gates"]["candidate"]]
    observed_gain = float(flow["mrr100"]) - float(baseline["mrr100"])
    reconstructed_p = (1 + sum(float(row["c_minus_b_mrr_gain"]) >= observed_gain - 1e-12 for row in null)) / (len(null) + 1)
    check("inclusive_p", math.isclose(reconstructed_p, float(flow["inclusive_p"]), abs_tol=5e-10), reconstructed_p)
    positive_folds = 0
    for held in design["collections"]:
        candidate = next(float(row["mrr100"]) for row in folds if row["held_collection"] == held and row["model"] == design["gates"]["candidate"])
        base = next(float(row["mrr100"]) for row in folds if row["held_collection"] == held and row["model"] == design["gates"]["baseline"])
        positive_folds += int(candidate > base)
    check("positive_folds", positive_folds == int(flow["positive_folds_vs_B"]), positive_folds)
    supported = (
        float(flow["mrr100"]) > float(baseline["mrr100"])
        and float(flow["top1_rate"]) > float(baseline["top1_rate"])
        and positive_folds >= int(design["gates"]["positive_folds_min"])
        and reconstructed_p <= float(design["gates"]["inclusive_p_max"])
    )
    status = "PERSISTENT_IDENTITY_FLOW_CALIBRATED" if supported else "PERSISTENT_IDENTITY_FLOW_NOT_CALIBRATED"
    check("decision", status == freeze["status"] == result["status"], status)
    check("representation", freeze["representation"] == result["representation"] == "GLOBAL_ANON_IDENTITY_PLUS_FLOW")
    check("result_positive_folds", result["positive_folds_C_over_B"] == positive_folds)
    check("target_stop", freeze["target_gate"] == "STOP_BEFORE_GDT327_ACCESS" and result["voynich_target_values_retained_or_scored"] is False)
    check("f84_false", all(value is False for value in freeze["f84"].values()) and all(value is False for value in result["f84"].values()))
    for path, digest in {**freeze["inputs"], **freeze["outputs"], **freeze["implementation"]}.items():
        check(f"freeze_hash:{path}", sha(ROOT / path) == digest)
    for path, digest in {**result["inputs"], **result["outputs"], **result["implementation"]}.items():
        check(f"result_hash:{path}", sha(ROOT / path) == digest)
    check("freeze_content_hash", content_hash(freeze) == freeze["content_sha256"])
    check("result_content_hash", content_hash(result) == result["content_sha256"])
    validation = {
        "schema": "GDT343_COMPARATOR_VALIDATION_V1",
        "status": "PASS",
        "checks_passed": len(checks),
        "checks_failed": 0,
        "result_sha256": sha(RESULT),
        "freeze_sha256": sha(FREEZE),
        "source_reconstruction": {"records": len(records), "eligible": len(eligible), "pairs": len(pairs), "concept_rows": concept_rows},
        "identity_control_reconstruction": independent,
        "decision_reconstruction": {"status": status, "positive_folds": positive_folds, "inclusive_p": reconstructed_p},
        "scope": "Independent source truth/capacity census, full diplomatic-token and global-anonymous-identity reranks, exported score arithmetic, null decision, hashes, no-target state, and f84 flags. Candidate flow-augmented graph pair similarities are not independently recomputed.",
        "checks": checks,
    }
    validation["content_sha256"] = content_hash(validation)
    VALIDATION.write_bytes(canonical(validation))
    print(f"PASS {len(checks)}/{len(checks)} {status}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
