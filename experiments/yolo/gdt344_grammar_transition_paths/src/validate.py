#!/usr/bin/env python3
"""Independent integrity/accounting validator for GDT344."""

from __future__ import annotations

import csv
import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path


def find_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("repository root not found")


ROOT = find_root(Path(__file__).resolve())
import sys
sys.path.insert(0, str(ROOT))
from tools.vmanus_experiment import GuardedTSV  # noqa: E402

EXP = ROOT / "experiments/yolo/gdt344_grammar_transition_paths"
ART = EXP / "artifacts"
DESIGN = ART / "gdt344_design.json"
NATIVE = ROOT / "gdt278_native_event_inventory.tsv"
INTER = ROOT / "gdt327_joint_tuple_interlinear.tsv"
TARGET_RECORDS = ROOT / "experiments/yolo/gdt340_recipe_pharma_section_semantic_schema/artifacts/gdt340_voynich_record_inventory.tsv"
ORACLE = ROOT / "gdt176_corema_role_oracle.tsv"
TRANSITIONS = ART / "gdt344_transition_inventory.tsv"
PATH_ATLAS = ART / "gdt344_path_atlas.tsv"
FORMAL_FOLDS = ART / "gdt344_formal_folds.tsv"
FORMAL_MODELS = ART / "gdt344_formal_models.tsv"
FORMAL_NULL = ART / "gdt344_formal_null.tsv"
COMPARATOR_FOLDS = ART / "gdt344_comparator_folds.tsv"
COMPARATOR_MODELS = ART / "gdt344_comparator_models.tsv"
COMPARATOR_NULL = ART / "gdt344_comparator_null.tsv"
TARGET_FOLDS = ART / "gdt344_target_folds.tsv"
RESULT = ART / "gdt344_result.json"
VALIDATION = ART / "gdt344_validation.json"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode()


def content_hash(document: dict[str, object]) -> str:
    copy = dict(document); copy.pop("content_sha256", None)
    return hashlib.sha256(canonical(copy)).hexdigest()


def hid(domain: str, value: object, length: int = 20) -> str:
    return hashlib.sha256((domain + "\0" + json.dumps(value, sort_keys=True, separators=(",", ":"))).encode()).hexdigest()[:length]


def main() -> int:
    checks: list[dict[str, object]] = []
    def check(name: str, condition: bool, detail: object = "") -> None:
        checks.append({"check": name, "pass": bool(condition), "detail": str(detail)})
        if not condition: raise AssertionError(f"{name}: {detail}")

    design = json.loads(DESIGN.read_text()); result = json.loads(RESULT.read_text())
    target_records = read_tsv(TARGET_RECORDS)
    page_panel = {row["page"]: row["panel"] for row in target_records if row["page"] != "page"}
    pages = set(page_panel)
    native_reader = GuardedTSV(NATIVE, selector_column="page", allowed_values=pages, forbidden_prefixes=("f84",), forbidden_action="error")
    native = list(native_reader)
    inter_reader = GuardedTSV(INTER, selector_column="page", allowed_values=pages, forbidden_prefixes=("f84",), forbidden_action="error")
    inter = list(inter_reader)
    nk = {(row["page"], row["locus"], row["group_index"]) for row in native}
    ik = {(row["page"], row["locus"], row["group_index"]) for row in inter}
    check("source_rows", len(native) == len(inter) == 2694, (len(native), len(inter)))
    check("source_join", len(nk) == len(ik) == 2694 and nk == ik)
    check("source_folios", len({row["physical_folio"] for row in inter}) == 17)
    check("source_records", len({(row["page"], row["record_ordinal"]) for row in inter}) == 94)
    check("source_fields", len({(row["page"], row["record_ordinal"], row["field_ordinal"]) for row in inter}) == 349)
    check("source_lines", len({row["locus"] for row in inter}) == 298)
    check("source_panels", {page_panel[row["page"]] for row in inter} == {"RECIPE_STARS_S", "PHARMA_P"})
    check("no_f84_source", not any(row["page"].startswith("f84") or row["locus"].startswith("f84") for row in native + inter))

    transitions = read_tsv(TRANSITIONS); atlas = read_tsv(PATH_ATLAS)
    formal_folds = read_tsv(FORMAL_FOLDS); formal_models = read_tsv(FORMAL_MODELS); formal_null = read_tsv(FORMAL_NULL)
    comparator_folds = read_tsv(COMPARATOR_FOLDS); comparator_models = read_tsv(COMPARATOR_MODELS); comparator_null = read_tsv(COMPARATOR_NULL)
    target_folds = read_tsv(TARGET_FOLDS)
    check("transition_rows", len(transitions) == 2660, len(transitions))
    check("transition_unique", len({row["edge_id"] for row in transitions}) == len(transitions))
    check("transition_panels", {row["panel"] for row in transitions} == {"RECIPE_STARS_S", "PHARMA_P"})
    check("transition_no_f84", not any(row["page"].startswith("f84") or row["source_locus"].startswith("f84") or row["target_locus"].startswith("f84") for row in transitions))
    check("transition_semantics", all(row["semantic_state"] == row["translation_state"] == "UNASSIGNED" for row in transitions))
    check("record_reset_count", sum(int(row["record_boundary"]) for row in transitions) == 60)
    check("line_reset_count", sum(int(row["line_reset"]) for row in transitions) == 264)
    check("field_boundary_count", sum(int(row["field_boundary"]) for row in transitions) == 705)
    for row in atlas:
        domain = "GDT344_SHAPE_PATH_V1" if row["resolution"] == "SHAPE" else "GDT344_VALUE_PATH_V1"
        check(f"path_hash:{row['path_id']}", row["path_id"] == hid(domain, json.loads(row["signature_json"])))
    for resolution in ("SHAPE", "VALUE"):
        check(f"path_event_sum:{resolution}", sum(int(row["events"]) for row in atlas if row["resolution"] == resolution) == 2660)
    check("atlas_semantics", all(row["semantic_state"] == "UNASSIGNED" for row in atlas))

    check("formal_fold_rows", len(formal_folds) == 17 * 4, len(formal_folds))
    check("formal_models", {row["model"] for row in formal_models} == set(design["formal_models"]))
    check("formal_null_worlds", len(formal_null) == int(design["formal_null"]["worlds"]))
    formal_by_model = {row["model"]: row for row in formal_models}
    for model in design["formal_models"]:
        rows = [row for row in formal_folds if row["model"] == model]
        check(f"formal_folds:{model}", len(rows) == 17)
        check(f"formal_bits:{model}", math.isclose(sum(float(row["total_bits"]) for row in rows), float(formal_by_model[model]["total_bits"]), abs_tol=2e-7))
        check(f"formal_edges:{model}", sum(int(row["scored_edges"]) for row in rows) == int(formal_by_model[model]["scored_edges"]))
        check(f"formal_unseen:{model}", sum(int(row["unseen_exact_pair_edges"]) for row in rows) == int(formal_by_model[model]["unseen_exact_pair_edges"]))
        check(f"formal_components:{model}", math.isclose(float(formal_by_model[model]["coordinate_bits"]) + float(formal_by_model[model]["gdt336_tuple_bits"]), float(formal_by_model[model]["total_bits"]), abs_tol=2e-7))
    placement_bits = float(formal_by_model["PLACEMENT"]["total_bits"]); exact_bits = float(formal_by_model["EXACT_PREDECESSOR"]["total_bits"])
    for model in ("PATH_SHAPE", "PATH_VALUE"):
        check(f"formal_gain_placement:{model}", math.isclose(placement_bits - float(formal_by_model[model]["total_bits"]), float(formal_by_model[model]["gain_over_placement"]), abs_tol=2e-7))
        check(f"formal_gain_exact:{model}", math.isclose(exact_bits - float(formal_by_model[model]["total_bits"]), float(formal_by_model[model]["gain_over_exact_predecessor"]), abs_tol=2e-7))

    check("comparator_fold_rows", len(comparator_folds) == 12)
    check("comparator_models", {row["model"] for row in comparator_models} == set(design["comparator_models"]))
    check("comparator_null_worlds", len(comparator_null) == int(design["comparator_null"]["worlds"]))
    class_counts = Counter()
    by_record: dict[tuple[str, str], set[str]] = defaultdict(set)
    for row in read_tsv(ORACLE): by_record[(row["collection_id"], row["recipe_id"])].add(row["role"])
    for roles in by_record.values():
        if not roles & {"INGREDIENT", "DISH"} or "INSTRUCTION" not in roles: continue
        s, a, r = bool(roles & {"TIME"}), bool(roles & {"SERVINGTIP", "HOUSEHOLDTIP"}), bool(roles & {"CLOSER", "DIETETICS"})
        total = s + a + r
        klass = "BASIC_MO" if total == 0 else ("MO_MULTI_OPTIONAL" if total >= 2 else ("MO_STATE_ONLY" if s else ("MO_APPLICATION_ONLY" if a else "MO_RESULT_ONLY")))
        class_counts[klass] += 1
    check("comparator_records", sum(class_counts.values()) == 1133, class_counts)
    comp_by_model = {row["model"]: row for row in comparator_models}
    for model in design["comparator_models"]:
        rows = [row for row in comparator_folds if row["model"] == model]
        check(f"comparator_folds:{model}", len(rows) == 6)
        check(f"comparator_records:{model}", sum(int(row["records"]) for row in rows) == 1133)
        check(f"comparator_bits:{model}", math.isclose(sum(float(row["bits"]) for row in rows), float(comp_by_model[model]["bits"]), abs_tol=2e-7))
    comparator_gain = float(comp_by_model["SHAPE_ONLY"]["bits"]) - float(comp_by_model["IDENTITY_FLOW_TOPOLOGY"]["bits"])
    check("comparator_gain", math.isclose(comparator_gain, float(comp_by_model["IDENTITY_FLOW_TOPOLOGY"]["gain_over_shape"]), abs_tol=2e-7))

    formal_supported = bool(result["formal_supported_models"])
    comparator_supported = result["comparator_status"] == "COMPARATOR_EVENT_PATH_CALIBRATED"
    check("stage_c_gate", result["stage_c_authorized"] is (formal_supported and comparator_supported))
    if not result["stage_c_authorized"]:
        check("target_empty", len(target_folds) == 0)
    check("no_semantic_assignment", result["voynich_semantic_assignments"] == 0 and result["tuple_merges"] == 0 and result["page_host_factorizations"] == 0)
    check("no_other_sections", result["other_section_rows_retained"] == 0)
    check("f84_flags", all(value is False for value in result["f84"].values()))
    for path, digest in result["inputs"].items(): check(f"input_hash:{path}", sha(ROOT / path) == digest)
    for path, digest in result["outputs"].items(): check(f"output_hash:{path}", sha(ROOT / path) == digest)
    for path, digest in result["implementation"].items(): check(f"implementation_hash:{path}", sha(ROOT / path) == digest)
    check("result_content_hash", content_hash(result) == result["content_sha256"])
    validation = {
        "schema": "GDT344_VALIDATION_V1", "status": "PASS", "checks_passed": len(checks), "checks_failed": 0,
        "result_sha256": sha(RESULT), "source_reconstruction": {"groups": len(inter), "transitions": len(transitions), "folios": 17, "records": 94},
        "comparator_class_counts": dict(sorted(class_counts.items())),
        "scope": "Independent guarded source join/capacity reconstruction, transition/path hash and count checks, fold/aggregate/null/gate arithmetic, output/input/implementation hashes, semantic-zero and f84 assertions. Statistical model fits and fixed-prediction permutations are not independently rerun.",
        "checks": checks,
    }
    validation["content_sha256"] = content_hash(validation)
    VALIDATION.write_bytes(canonical(validation))
    print(f"PASS {len(checks)}/{len(checks)} {result['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
