#!/usr/bin/env python3
"""Validate the GDT480 recurrent microrecord template atlas."""

from __future__ import annotations

import csv
import hashlib
import json
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt480_microrecord_template_atlas"
OUT = BASE / "artifacts"
RUN = BASE / "src/run.py"
G479 = ROOT / "experiments/yolo/gdt479_definitive_local_microrecord_edition/artifacts"
EVENTS_IN = G479 / "gdt479_183_definitive_local_events.tsv"
BUNDLES_IN = G479 / "gdt479_146_definitive_local_bundles.tsv"
RECORDS_IN = G479 / "gdt479_135_definitive_microrecords.tsv"
ASSIGNMENTS = OUT / "gdt480_135_record_template_assignments.tsv"
STRICT = OUT / "gdt480_strict_semantic_templates.tsv"
SHAPES = OUT / "gdt480_role_shape_templates.tsv"
COVERAGE = OUT / "gdt480_template_coverage_summary.tsv"
READABLE = OUT / "GDT480_MICRORECORD_TEMPLATE_ATLAS.md"
RESULT = OUT / "gdt480_result.json"
VALIDATION = OUT / "gdt480_validation.json"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def expected_class(record_count: int, page_count: int, register_count: int) -> str:
    if register_count > 1:
        return "CROSS_REGISTER"
    if page_count > 1:
        return "CROSS_PAGE"
    if record_count > 1:
        return "SAME_PAGE_RECURRENT"
    return "SINGLETON"


def main() -> int:
    checks: list[dict[str, object]] = []

    def check(name: str, condition: bool, detail: object) -> None:
        checks.append({"name": name, "pass": bool(condition), "detail": detail})

    generated = [ASSIGNMENTS, STRICT, SHAPES, COVERAGE, READABLE, RESULT]
    present = all(path.is_file() for path in generated)
    check("all_outputs_present", present, [path.name for path in generated])
    if not present:
        raise RuntimeError("Run GDT480 builder before validation")
    before = {path.name: sha256(path) for path in generated}
    completed = subprocess.run([sys.executable, str(RUN)], cwd=ROOT, capture_output=True, text=True, check=False)
    after = {path.name: sha256(path) for path in generated}
    check("builder_exit_zero", completed.returncode == 0, completed.stderr[-1000:])
    check("deterministic_rebuild", before == after, {"before": before, "after": after})

    source_events = read_tsv(EVENTS_IN)
    source_bundles = read_tsv(BUNDLES_IN)
    source_records = read_tsv(RECORDS_IN)
    assignments = read_tsv(ASSIGNMENTS)
    strict = read_tsv(STRICT)
    shapes = read_tsv(SHAPES)
    coverage = read_tsv(COVERAGE)
    readable = READABLE.read_text(encoding="utf-8")
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    source_record_map = {row["record_id"]: row for row in source_records}
    assignment_map = {row["record_id"]: row for row in assignments}
    strict_map = {row["strict_template_id"]: row for row in strict}
    shape_map = {row["role_shape_id"]: row for row in shapes}

    check("source_event_count_183", len(source_events) == 183, len(source_events))
    check("source_bundle_count_146", len(source_bundles) == 146, len(source_bundles))
    check("source_record_count_135", len(source_records) == 135, len(source_records))
    check("assignment_count_135", len(assignments) == 135, len(assignments))
    check("strict_template_count_120", len(strict) == 120, len(strict))
    check("role_shape_count_105", len(shapes) == 105, len(shapes))
    check("coverage_row_count_11", len(coverage) == 11, len(coverage))
    check("unique_assignment_records", len(assignment_map) == 135, len(assignment_map))
    check("unique_strict_ids", len(strict_map) == 120, len(strict_map))
    check("unique_shape_ids", len(shape_map) == 105, len(shape_map))
    check("record_key_set_exact", set(assignment_map) == set(source_record_map), len(assignment_map))
    check("record_order_exact", [row["record_id"] for row in assignments] == [row["record_id"] for row in source_records], [row["record_id"] for row in assignments[:3]])

    preserved_fields = (
        "physical_page", "register", "page_record_ordinal", "record_start_role",
        "bundle_count", "event_count", "bundle_ids", "surface_sequence",
        "active_model_sequence", "definitive_record_reading_de",
    )
    for field in preserved_fields:
        check(
            f"record_{field}_preserved",
            all(row[field] == source_record_map[row["record_id"]][field] for row in assignments),
            field,
        )
    check("all_strict_assignments_resolve", all(row["strict_template_id"] in strict_map for row in assignments), len(assignments))
    check("all_shape_assignments_resolve", all(row["role_shape_id"] in shape_map for row in assignments), len(assignments))
    check("all_default_flags_yes", all(row["all_sequences_have_default"] == "YES" for row in assignments), len(assignments))
    check("all_owner_neutral_phrases_present", all(row["owner_neutral_phrase_de"].strip() for row in assignments), len(assignments))
    check("all_strict_frames_present", all(row["strict_semantic_frame"].strip() for row in assignments), len(assignments))
    check("all_recipe_frames_present", all(row["recipe_frame"].strip() for row in assignments), len(assignments))
    check("all_role_frames_present", all(row["role_shape_frame"].strip() for row in assignments), len(assignments))

    strict_assignment_groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    shape_assignment_groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in assignments:
        strict_assignment_groups[row["strict_template_id"]].append(row)
        shape_assignment_groups[row["role_shape_id"]].append(row)
    check("all_strict_templates_used", set(strict_assignment_groups) == set(strict_map), len(strict_assignment_groups))
    check("all_shape_templates_used", set(shape_assignment_groups) == set(shape_map), len(shape_assignment_groups))
    check("strict_record_counts_exact", all(int(row["record_count"]) == len(strict_assignment_groups[row["strict_template_id"]]) for row in strict), len(strict))
    check("shape_record_counts_exact", all(int(row["record_count"]) == len(shape_assignment_groups[row["role_shape_id"]]) for row in shapes), len(shapes))
    check("assignment_strict_counts_exact", all(int(row["strict_template_record_count"]) == int(strict_map[row["strict_template_id"]]["record_count"]) for row in assignments), len(assignments))
    check("assignment_shape_counts_exact", all(int(row["role_shape_record_count"]) == int(shape_map[row["role_shape_id"]]["record_count"]) for row in assignments), len(assignments))
    check("assignment_strict_frames_exact", all(row["strict_semantic_frame"] == strict_map[row["strict_template_id"]]["strict_semantic_frame"] for row in assignments), len(assignments))
    check("assignment_shape_frames_exact", all(row["role_shape_frame"] == shape_map[row["role_shape_id"]]["role_shape_frame"] for row in assignments), len(assignments))
    check("strict_surface_type_counts_exact", all(int(row["surface_type_count"]) == len({item["surface_sequence"] for item in strict_assignment_groups[row["strict_template_id"]]}) for row in strict), len(strict))
    check("strict_surface_modes_exact", all(row["surface_recurrence_mode"] == ("MULTIPLE_SURFACES" if int(row["surface_type_count"]) > 1 else ("SAME_SURFACE" if int(row["record_count"]) > 1 else "SINGLETON")) for row in strict), len(strict))

    check("strict_singletons_107", sum(int(row["record_count"]) == 1 for row in strict) == 107, Counter(row["record_count"] for row in strict))
    check("strict_recurrent_templates_13", sum(int(row["record_count"]) > 1 for row in strict) == 13, Counter(row["record_count"] for row in strict))
    check("strict_recurrent_records_28", sum(int(row["record_count"]) for row in strict if int(row["record_count"]) > 1) == 28, None)
    check("strict_cross_page_templates_5", sum(int(row["page_count"]) > 1 for row in strict) == 5, None)
    check("strict_cross_register_templates_3", sum(int(row["register_count"]) > 1 for row in strict) == 3, None)
    check("strict_largest_count_4", max(int(row["record_count"]) for row in strict) == 4, None)
    check("all_recurrent_strict_phrases_stable", all(row["phrase_stable"] == "YES" for row in strict if int(row["record_count"]) > 1), [row["strict_template_id"] for row in strict if int(row["record_count"]) > 1 and row["phrase_stable"] != "YES"])
    check("strict_multisurface_recurrent_templates_8", sum(int(row["record_count"]) > 1 and int(row["surface_type_count"]) > 1 for row in strict) == 8, None)
    check("strict_multisurface_recurrent_records_18", sum(int(row["record_count"]) for row in strict if int(row["record_count"]) > 1 and int(row["surface_type_count"]) > 1) == 18, None)
    check("role_singletons_84", sum(int(row["record_count"]) == 1 for row in shapes) == 84, Counter(row["record_count"] for row in shapes))
    check("role_recurrent_templates_21", sum(int(row["record_count"]) > 1 for row in shapes) == 21, Counter(row["record_count"] for row in shapes))
    check("role_recurrent_records_51", sum(int(row["record_count"]) for row in shapes if int(row["record_count"]) > 1) == 51, None)
    check("role_cross_page_templates_13", sum(int(row["page_count"]) > 1 for row in shapes) == 13, None)
    check("role_cross_register_templates_8", sum(int(row["register_count"]) > 1 for row in shapes) == 8, None)
    check("role_largest_count_5", max(int(row["record_count"]) for row in shapes) == 5, None)
    check("role_multi_component_recurrent_templates_13", sum(int(row["record_count"]) > 1 and int(row["strict_template_count"]) > 1 for row in shapes) == 13, None)
    check("role_multi_component_recurrent_records_33", sum(int(row["record_count"]) for row in shapes if int(row["record_count"]) > 1 and int(row["strict_template_count"]) > 1) == 33, None)

    check("strict_recurrence_classes_exact", all(row["recurrence_class"] == expected_class(int(row["record_count"]), int(row["page_count"]), int(row["register_count"])) for row in strict), len(strict))
    check("shape_recurrence_classes_exact", all(row["recurrence_class"] == expected_class(int(row["record_count"]), int(row["page_count"]), int(row["register_count"])) for row in shapes), len(shapes))
    check("assignment_strict_classes_exact", all(row["strict_recurrence_class"] == strict_map[row["strict_template_id"]]["recurrence_class"] for row in assignments), len(assignments))
    check("assignment_shape_classes_exact", all(row["role_recurrence_class"] == shape_map[row["role_shape_id"]]["recurrence_class"] for row in assignments), len(assignments))

    expected_cross_register = {
        "G480-T005": {"G475-R005", "G475-R087", "G475-R100", "G475-R105"},
        "G480-T050": {"G475-R055", "G475-R133"},
        "G480-T071": {"G475-R080", "G475-R134"},
    }
    actual_cross_register = {
        row["strict_template_id"]: set(row["record_ids"].split("|"))
        for row in strict if int(row["register_count"]) > 1
    }
    check(
        "cross_register_strict_families_exact",
        actual_cross_register == expected_cross_register,
        {key: sorted(value) for key, value in actual_cross_register.items()},
    )
    check("ot_name_catalogue_template_largest", strict_map["G480-T005"]["record_count"] == "4" and strict_map["G480-T005"]["recipe_frames"].startswith("CATALOGUE[OT @START_FRESH_SIBLING"), strict_map["G480-T005"])
    check("cross_register_coordinate_template_exact", strict_map["G480-T050"]["strict_semantic_frame"].startswith("COORDINATE[DANACH · ZIELORT · POSTEN"), strict_map["G480-T050"]["strict_semantic_frame"])
    check("cross_register_double_name_template_exact", strict_map["G480-T071"]["strict_semantic_frame"] == "CATALOGUE[{N1} · AUSGANG · {N2} @NONE]", strict_map["G480-T071"]["strict_semantic_frame"])

    owner_terms = re.compile(r"Pflanzen|Pflanze|Sternstelle|Drogen|Droge|Badstation|Positions|Stationseinheit|Stationswert|Zielposition|Zielgefäß|Ausgangsposition|Ausgangsgefäß|Ringbahn|Sektoranteil|Namenseintragn")
    check("owner_neutral_phrase_vocabulary", all(not owner_terms.search(row["owner_neutral_phrase_de"]) for row in assignments), [row["record_id"] for row in assignments if owner_terms.search(row["owner_neutral_phrase_de"])][:10])
    check("owner_neutral_phrase_grammar_repairs", all(fragment not in row["owner_neutral_phrase_de"] for row in assignments for fragment in ("von der Ausgang", "zur Zielort", "Namenseintragn")), len(assignments))
    check("strict_names_are_slotted", all("NAME:" not in row["strict_semantic_frame"] for row in strict), len(strict))
    allowed_role_words = re.compile(r"^(?:COORDINATE|INSTRUCTION|CATALOGUE|ORDER|ARG|REL|ACTION|NAME|MOD|NONE|START_FRESH_SIBLING|KEEP_ACTIVE_UNIT|FORWARD_OPEN|BRIDGE_LEFT_TO_RIGHT|BACKWARD_HOLD|TERMINAL|[\[\]{}() @:|/·._-])+$")
    check("role_shapes_use_only_role_vocabulary", all(allowed_role_words.fullmatch(row["role_shape_frame"]) for row in shapes), [row["role_shape_id"] for row in shapes if not allowed_role_words.fullmatch(row["role_shape_frame"])][:10])

    expected_coverage = {
        ("STRICT", "all_templates"): (120, 135),
        ("STRICT", "recurrent"): (13, 28),
        ("STRICT", "cross_page"): (5, 12),
        ("STRICT", "cross_register"): (3, 8),
        ("STRICT", "stable_recurrent"): (13, 28),
        ("STRICT", "multisurface_recurrent"): (8, 18),
        ("ROLE", "all_templates"): (105, 135),
        ("ROLE", "recurrent"): (21, 51),
        ("ROLE", "cross_page"): (13, 33),
        ("ROLE", "cross_register"): (8, 22),
        ("ROLE", "multi_component_recurrent"): (13, 33),
    }
    actual_coverage = {(row["level"], row["subset"]): (int(row["template_count"]), int(row["record_count"])) for row in coverage}
    check(
        "coverage_summary_exact",
        actual_coverage == expected_coverage,
        {f"{key[0]}:{key[1]}": value for key, value in actual_coverage.items()},
    )
    check("coverage_all_fraction_one", all(row["record_coverage_fraction"] == "1.000000" for row in coverage if row["subset"] == "all_templates"), [row["record_coverage_fraction"] for row in coverage if row["subset"] == "all_templates"])

    check("all_recurrent_strict_ids_readable", all(row["strict_template_id"] in readable for row in strict if int(row["record_count"]) > 1), None)
    check("all_role_shape_ids_readable", all(row["role_shape_id"] in readable for row in shapes), None)
    check("readable_reports_exact_counts", "120" in readable and "105" in readable and "135" in readable, None)
    check("sealed_pages_absent", all(not row["physical_page"].startswith("f84") for row in assignments), sorted({row["physical_page"] for row in assignments}))

    check("result_status_exact", result.get("status") == "ALL_135_RECORDS_HAVE_TEMPLATES__RECURRENT_MICRORECORD_GRAMMAR_ATLAS_COMPLETE", result.get("status"))
    check("result_primary_counts_exact", (result.get("record_count"), result.get("strict_template_count"), result.get("role_shape_count")) == (135, 120, 105), {key: result.get(key) for key in ("record_count", "strict_template_count", "role_shape_count")})
    check("result_recurrence_counts_exact", (result.get("recurrent_strict_template_count"), result.get("records_in_recurrent_strict_templates"), result.get("recurrent_role_shape_count"), result.get("records_in_recurrent_role_shapes")) == (13, 28, 21, 51), None)
    check("result_cross_register_counts_exact", (result.get("cross_register_strict_template_count"), result.get("cross_register_role_shape_count")) == (3, 8), None)
    check("result_multisurface_counts_exact", (result.get("multisurface_recurrent_strict_template_count"), result.get("records_in_multisurface_recurrent_strict_templates")) == (8, 18), None)
    check("result_multi_component_shape_counts_exact", (result.get("multi_component_recurrent_role_shape_count"), result.get("records_in_multi_component_recurrent_role_shapes")) == (13, 33), None)
    unchanged_keys = ("component_meaning_change_count", "active_model_change_count", "record_boundary_change_count", "surface_change_count", "recipe_change_count", "new_page_count")
    check("result_no_source_changes", all(result.get(key) == 0 for key in unchanged_keys), {key: result.get(key) for key in unchanged_keys})

    failed = [row for row in checks if not row["pass"]]
    payload = {
        "status": "PASS" if not failed else "FAIL",
        "checks_passed": len(checks) - len(failed),
        "checks_total": len(checks),
        "failed_checks": [row["name"] for row in failed],
        "checks": checks,
    }
    VALIDATION.write_text(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({key: payload[key] for key in ("status", "checks_passed", "checks_total", "failed_checks")}, sort_keys=True))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
