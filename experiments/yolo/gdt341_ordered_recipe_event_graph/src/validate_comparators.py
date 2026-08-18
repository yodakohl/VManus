#!/usr/bin/env python3
"""Independent source/accounting validator for GDT341 Stage A."""

from __future__ import annotations

import csv
import hashlib
import itertools
import json
import math
import re
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path


def find_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists(): return candidate
    raise RuntimeError("root not found")


ROOT = find_root(Path(__file__).resolve())
EXP = ROOT / "experiments/yolo/gdt341_ordered_recipe_event_graph"
ART = EXP / "artifacts"
DESIGN = ART / "gdt341_comparator_design.json"
ORACLE = ROOT / "gdt176_corema_role_oracle.tsv"
CACHE = ROOT / ".gdt176/corema"
PARALLELS = ART / "gdt341_parallel_recipe_census.tsv"
FOLDS = ART / "gdt341_comparator_folds.tsv"
RETRIEVAL = ART / "gdt341_comparator_retrieval.tsv"
MODELS = ART / "gdt341_comparator_models.tsv"
NULL = ART / "gdt341_comparator_null.tsv"
FREEZE = ART / "gdt341_graph_freeze.json"
RESULT = ART / "gdt341_comparator_result.json"
COUNTER = ART / "gdt341_counterexamples.tsv"
VALIDATION = ART / "gdt341_comparator_validation.json"
NS = {"t": "http://www.tei-c.org/ns/1.0"}
XML_ID = "{http://www.w3.org/XML/1998/namespace}id"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle: return list(csv.DictReader(handle, delimiter="\t"))


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""): h.update(block)
    return h.hexdigest()


def canonical(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode()


def content_hash(document: dict) -> str:
    copy = dict(document); copy.pop("content_sha256", None)
    return hashlib.sha256(canonical(copy)).hexdigest()


def norm_title(value: str) -> str:
    return re.sub(r"\W+", " ", value.lower()).strip()


def main() -> int:
    checks = []
    def check(name: str, condition: bool, detail: object = "") -> None:
        checks.append({"check": name, "pass": bool(condition), "detail": str(detail)})
        if not condition: raise AssertionError(f"{name}: {detail}")

    design = json.loads(DESIGN.read_text())
    freeze = json.loads(FREEZE.read_text())
    result = json.loads(RESULT.read_text())
    oracle = read_tsv(ORACLE)
    title_map: dict[tuple[str, str], list[str]] = defaultdict(list)
    concept_map: dict[tuple[str, str], set[str]] = defaultdict(set)
    for row in oracle:
        key = (row["collection_id"], row["recipe_id"])
        if row["role"] == "TITLE" and row["editor_english_label"] != "NONE": title_map[key].append(norm_title(row["editor_english_label"]))
        if row["concept_id"] != "NONE": concept_map[key].add(row["concept_id"])
    surfaces = {}
    records = set()
    for collection in design["collections"]:
        root = ET.parse(CACHE / f"{collection}.recipes.xml").getroot()
        for ordinal, recipe in enumerate(root.findall('.//*[@type="recipe"]', NS), 1):
            record = recipe.get(XML_ID, f"{collection}.ordinal{ordinal}")
            key = (collection, record); records.add(key)
            normalized = " ".join(" ".join(recipe.itertext()).lower().split())
            surfaces[key] = hashlib.sha256(normalized.encode()).hexdigest()
    singles = {key: values[0] for key, values in title_map.items() if len(set(values)) == 1}
    pairs = []; eligible = set()
    for a, b in itertools.combinations(sorted(singles), 2):
        if a[0] == b[0]: continue
        if singles[a] == singles[b] and len(concept_map[a] & concept_map[b]) >= 2 and surfaces[a] != surfaces[b]:
            pairs.append((a, b)); eligible.update((a, b))
    check("complete_records", len(records) == 1136, len(records))
    check("single_title_records", len(singles) == 1115, len(singles))
    check("parallel_pairs", len(pairs) == 657, len(pairs))
    check("eligible_records", len(eligible) == 688, len(eligible))
    check("different_surfaces", all(surfaces[a] != surfaces[b] for a, b in pairs))
    census = {row["metric"]: int(row["value"]) for row in read_tsv(PARALLELS)}
    check("census_export", census == {"complete_records": 1136, "single_title_records": 1115, "eligible_parallel_records": 688, "cross_collection_parallel_pairs": 657, "parallel_pairs_with_identical_surface_hash": 0}, census)
    folds = read_tsv(FOLDS); retrieval = read_tsv(RETRIEVAL); models = read_tsv(MODELS); null = read_tsv(NULL); counter = read_tsv(COUNTER)
    check("fold_rows", len(folds) == 30, len(folds))
    check("retrieval_rows", len(retrieval) == 688 * 5, len(retrieval))
    check("model_rows", len(models) == 5, len(models))
    check("null_worlds", len(null) == 2048, len(null))
    check("counterexamples", len(counter) == 6, len(counter))
    by_model = {row["model"]: row for row in models}
    for model in design["models"]:
        rr = [row for row in retrieval if row["model"] == model]
        check(f"queries:{model}", len(rr) == 688)
        check(f"top1:{model}", sum(int(row["top1_correct"]) for row in rr) == int(by_model[model]["top1"]))
        check(f"top5:{model}", sum(int(row["top5_correct"]) for row in rr) == int(by_model[model]["top5"]))
        mrr = sum(float(row["reciprocal_rank_100"]) for row in rr) / len(rr)
        check(f"mrr:{model}", math.isclose(mrr, float(by_model[model]["mrr100"]), abs_tol=1e-8), mrr)
    selected = min(design["selection_eligible"], key=lambda model: (-float(by_model[model]["mrr100"]), model))
    controls = [by_model[name] for name in design["gates"]["must_beat"]]
    chosen = by_model[selected]
    supported = float(chosen["mrr100"]) > max(float(r["mrr100"]) for r in controls) and float(chosen["top1_rate"]) > max(float(r["top1_rate"]) for r in controls) and int(chosen["positive_folds_vs_both_controls"]) >= 4 and float(chosen["max_two_p"]) <= .05
    status = "ORDERED_RECIPE_GRAPH_CALIBRATED" if supported else "NO_COMPARATOR_GRAPH_CALIBRATION"
    check("selected", selected == freeze["selected_model"] == result["selected_model"], selected)
    check("status", status == freeze["status"] == result["status"], status)
    check("unordered_dominates", float(by_model["UNORDERED_GRAPH"]["mrr100"]) > float(chosen["mrr100"]) and float(by_model["UNORDERED_GRAPH"]["top1_rate"]) > float(chosen["top1_rate"]))
    check("no_voynich_scoring", freeze["voynich_tuple_values_retained_or_scored"] is False and result["voynich_tuple_values_retained_or_scored"] is False)
    check("f84_false", all(value is False for value in freeze["f84"].values()) and all(value is False for value in result["f84"].values()))
    for path, digest in {**freeze["inputs"], **freeze["outputs"], **freeze["implementation"]}.items(): check(f"freeze_hash:{path}", sha(ROOT / path) == digest)
    for path, digest in {**result["inputs"], **result["outputs"], **result["implementation"]}.items(): check(f"result_hash:{path}", sha(ROOT / path) == digest)
    check("freeze_content_hash", content_hash(freeze) == freeze["content_sha256"])
    check("result_content_hash", content_hash(result) == result["content_sha256"])
    validation = {"schema": "GDT341_COMPARATOR_VALIDATION_V1", "status": "PASS", "checks_passed": len(checks), "checks_failed": 0,
                  "result_sha256": sha(RESULT), "freeze_sha256": sha(FREEZE),
                  "source_reconstruction": {"records": len(records), "single_title": len(singles), "eligible": len(eligible), "pairs": len(pairs)},
                  "decision_reconstruction": {"selected": selected, "status": status},
                  "scope": "Independent source truth census, exported retrieval arithmetic, decision, hashes and no-target-access state; graph similarities and null worlds are not independently recomputed.", "checks": checks}
    validation["content_sha256"] = content_hash(validation); VALIDATION.write_bytes(canonical(validation))
    print(f"PASS {len(checks)}/{len(checks)} {status}")
    return 0


if __name__ == "__main__": raise SystemExit(main())
