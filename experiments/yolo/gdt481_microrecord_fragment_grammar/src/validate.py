#!/usr/bin/env python3
"""Validate the GDT481 microrecord fragment grammar."""

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
BASE = ROOT / "experiments/yolo/gdt481_microrecord_fragment_grammar"
OUT = BASE / "artifacts"
RUN = BASE / "src/run.py"
G479 = ROOT / "experiments/yolo/gdt479_definitive_local_microrecord_edition/artifacts"
G480 = ROOT / "experiments/yolo/gdt480_microrecord_template_atlas/artifacts"
EVENTS_IN = G479 / "gdt479_183_definitive_local_events.tsv"
BUNDLES_IN = G479 / "gdt479_146_definitive_local_bundles.tsv"
RECORDS_IN = G479 / "gdt479_135_definitive_microrecords.tsv"
G480_IN = G480 / "gdt480_135_record_template_assignments.tsv"
EVENT_ASSIGNMENTS = OUT / "gdt481_183_event_fragment_assignments.tsv"
EVENT_STRICT = OUT / "gdt481_event_strict_templates.tsv"
EVENT_ROLES = OUT / "gdt481_event_role_shapes.tsv"
PAIR_ASSIGNMENTS = OUT / "gdt481_48_adjacent_pair_assignments.tsv"
PAIR_STRICT = OUT / "gdt481_pair_strict_templates.tsv"
PAIR_ROLES = OUT / "gdt481_pair_role_shapes.tsv"
RECORD_COVERAGE = OUT / "gdt481_135_record_fragment_coverage.tsv"
SUMMARY = OUT / "gdt481_fragment_coverage_summary.tsv"
READABLE = OUT / "GDT481_MICRORECORD_FRAGMENT_GRAMMAR.md"
RESULT = OUT / "gdt481_result.json"
VALIDATION = OUT / "gdt481_validation.json"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def recurrence_class(count: int, pages: int, registers: int) -> str:
    if registers > 1:
        return "CROSS_REGISTER"
    if pages > 1:
        return "CROSS_PAGE"
    if count > 1:
        return "SAME_PAGE_RECURRENT"
    return "SINGLETON"


def main() -> int:
    checks: list[dict[str, object]] = []

    def check(name: str, condition: bool, detail: object) -> None:
        checks.append({"name": name, "pass": bool(condition), "detail": detail})

    generated = [EVENT_ASSIGNMENTS, EVENT_STRICT, EVENT_ROLES, PAIR_ASSIGNMENTS,
                 PAIR_STRICT, PAIR_ROLES, RECORD_COVERAGE, SUMMARY, READABLE, RESULT]
    present = all(path.is_file() for path in generated)
    check("all_outputs_present", present, [path.name for path in generated])
    if not present:
        raise RuntimeError("Run GDT481 builder before validation")
    before = {path.name: sha256(path) for path in generated}
    completed = subprocess.run([sys.executable, str(RUN)], cwd=ROOT, capture_output=True, text=True, check=False)
    after = {path.name: sha256(path) for path in generated}
    check("builder_exit_zero", completed.returncode == 0, completed.stderr[-1000:])
    check("deterministic_rebuild", before == after, {"before": before, "after": after})

    source_events = read_tsv(EVENTS_IN)
    source_bundles = read_tsv(BUNDLES_IN)
    source_records = read_tsv(RECORDS_IN)
    g480 = read_tsv(G480_IN)
    event_assignments = read_tsv(EVENT_ASSIGNMENTS)
    event_strict = read_tsv(EVENT_STRICT)
    event_roles = read_tsv(EVENT_ROLES)
    pair_assignments = read_tsv(PAIR_ASSIGNMENTS)
    pair_strict = read_tsv(PAIR_STRICT)
    pair_roles = read_tsv(PAIR_ROLES)
    coverage = read_tsv(RECORD_COVERAGE)
    summary = read_tsv(SUMMARY)
    readable = READABLE.read_text(encoding="utf-8")
    result = json.loads(RESULT.read_text(encoding="utf-8"))

    source_event_map = {row["source_event_id"]: row for row in source_events}
    bundle_map = {row["bundle_id"]: row for row in source_bundles}
    record_map = {row["record_id"]: row for row in source_records}
    g480_map = {row["record_id"]: row for row in g480}
    event_assignment_map = {row["source_event_id"]: row for row in event_assignments}
    event_strict_map = {row["template_id"]: row for row in event_strict}
    event_role_map = {row["template_id"]: row for row in event_roles}
    pair_strict_map = {row["template_id"]: row for row in pair_strict}
    pair_role_map = {row["template_id"]: row for row in pair_roles}
    coverage_map = {row["record_id"]: row for row in coverage}

    check("source_event_count_183", len(source_events) == 183, len(source_events))
    check("source_bundle_count_146", len(source_bundles) == 146, len(source_bundles))
    check("source_record_count_135", len(source_records) == 135, len(source_records))
    check("gdt480_assignment_count_135", len(g480) == 135, len(g480))
    check("event_assignment_count_183", len(event_assignments) == 183, len(event_assignments))
    check("pair_assignment_count_48", len(pair_assignments) == 48, len(pair_assignments))
    check("record_coverage_count_135", len(coverage) == 135, len(coverage))
    check("summary_count_14", len(summary) == 14, len(summary))
    check("event_strict_template_count_149", len(event_strict) == 149, len(event_strict))
    check("event_role_shape_count_118", len(event_roles) == 118, len(event_roles))
    check("pair_strict_template_count_47", len(pair_strict) == 47, len(pair_strict))
    check("pair_role_shape_count_45", len(pair_roles) == 45, len(pair_roles))

    check("unique_event_assignment_ids", len({row["event_fragment_id"] for row in event_assignments}) == 183, None)
    check("unique_source_event_assignments", len(event_assignment_map) == 183, None)
    check("unique_pair_assignment_ids", len({row["pair_fragment_id"] for row in pair_assignments}) == 48, None)
    check("unique_event_strict_ids", len(event_strict_map) == 149, None)
    check("unique_event_role_ids", len(event_role_map) == 118, None)
    check("unique_pair_strict_ids", len(pair_strict_map) == 47, None)
    check("unique_pair_role_ids", len(pair_role_map) == 45, None)
    check("unique_record_coverage", len(coverage_map) == 135, None)
    check("source_event_key_set_exact", set(event_assignment_map) == set(source_event_map), len(event_assignment_map))
    check("record_coverage_key_set_exact", set(coverage_map) == set(record_map), len(coverage_map))
    check("event_source_order_exact", [row["source_event_id"] for row in event_assignments] == [row["source_event_id"] for row in source_events], [row["source_event_id"] for row in event_assignments[:3]])
    check("coverage_record_order_exact", [row["record_id"] for row in coverage] == [row["record_id"] for row in source_records], [row["record_id"] for row in coverage[:3]])

    check("event_surfaces_preserved", all(row["surface"] == source_event_map[row["source_event_id"]]["surface"] for row in event_assignments), len(event_assignments))
    check("event_bundle_links_preserved", all(row["bundle_id"] == source_event_map[row["source_event_id"]]["bundle_id"] for row in event_assignments), len(event_assignments))
    check("event_models_preserved", all(row["active_model"] == bundle_map[row["bundle_id"]]["active_model"] for row in event_assignments), len(event_assignments))
    check("event_readings_preserved", all(row["definitive_fragment_reading_de"] == source_event_map[row["source_event_id"]]["definitive_event_reading_de"] for row in event_assignments), len(event_assignments))
    check("event_defaults_complete", all(row["all_fragments_have_default"] == "YES" for row in event_assignments), len(event_assignments))
    check("pair_defaults_complete", all(row["all_fragments_have_default"] == "YES" for row in pair_assignments), len(pair_assignments))
    check("all_event_strict_ids_resolve", all(row["strict_template_id"] in event_strict_map for row in event_assignments), len(event_assignments))
    check("all_event_role_ids_resolve", all(row["role_shape_id"] in event_role_map for row in event_assignments), len(event_assignments))
    check("all_pair_strict_ids_resolve", all(row["strict_template_id"] in pair_strict_map for row in pair_assignments), len(pair_assignments))
    check("all_pair_role_ids_resolve", all(row["role_shape_id"] in pair_role_map for row in pair_assignments), len(pair_assignments))

    expected_pairs: list[tuple[str, str, str]] = []
    for record in source_records:
        source_ids: list[str] = []
        for bundle_id in record["bundle_ids"].split("|"):
            source_ids.extend(row["source_event_id"] for row in source_events if row["bundle_id"] == bundle_id)
        expected_pairs.extend((record["record_id"], source_ids[index], source_ids[index + 1]) for index in range(len(source_ids) - 1))
    actual_pairs = [(row["record_id"], row["left_source_event_id"], row["right_source_event_id"]) for row in pair_assignments]
    check("pair_adjacency_exact", actual_pairs == expected_pairs, actual_pairs[:3])
    check("pair_total_equals_events_minus_records", len(pair_assignments) == len(source_events) - len(source_records), len(pair_assignments))
    check("pair_pages_preserved", all(row["physical_page"] == record_map[row["record_id"]]["physical_page"] for row in pair_assignments), len(pair_assignments))
    check("pair_surfaces_preserved", all(row["surface_pair"] == source_event_map[row["left_source_event_id"]]["surface"] + "|" + source_event_map[row["right_source_event_id"]]["surface"] for row in pair_assignments), len(pair_assignments))
    check("cross_bundle_pair_count_11", sum(row["pair_boundary"].startswith("CROSS_BUNDLE") for row in pair_assignments) == 11, Counter(row["pair_boundary"] for row in pair_assignments))
    check("cross_bundle_pairs_are_real_bundle_changes", all((row["left_bundle_id"] != row["right_bundle_id"]) == row["pair_boundary"].startswith("CROSS_BUNDLE") for row in pair_assignments), None)

    def check_groups(assignments: list[dict[str, str]], templates: list[dict[str, str]], assignment_id: str, template_id: str, frame_key: str) -> None:
        groups: dict[str, list[dict[str, str]]] = defaultdict(list)
        for row in assignments:
            groups[row[assignment_id]].append(row)
        template_map = {row["template_id"]: row for row in templates}
        check(f"{template_id}_all_templates_used", set(groups) == set(template_map), len(groups))
        check(f"{template_id}_occurrence_counts_exact", all(int(row["occurrence_count"]) == len(groups[row["template_id"]]) for row in templates), len(templates))
        check(f"{template_id}_frames_exact", all(item[frame_key] == template_map[item[assignment_id]][frame_key] for item in assignments), len(assignments))
        check(f"{template_id}_classes_exact", all(row["recurrence_class"] == recurrence_class(int(row["occurrence_count"]), int(row["page_count"]), int(row["register_count"])) for row in templates), len(templates))
        check(f"{template_id}_surface_counts_exact", all(int(row["surface_type_count"]) == len({item["surface"] if "surface" in item else item["surface_pair"] for item in groups[row["template_id"]]}) for row in templates), len(templates))

    check_groups(event_assignments, event_strict, "strict_template_id", "event_strict", "strict_frame")
    check_groups(event_assignments, event_roles, "role_shape_id", "event_role", "role_frame")
    check_groups(pair_assignments, pair_strict, "strict_template_id", "pair_strict", "strict_frame")
    check_groups(pair_assignments, pair_roles, "role_shape_id", "pair_role", "role_frame")

    recurrent_event_strict = [row for row in event_strict if int(row["occurrence_count"]) > 1]
    recurrent_event_roles = [row for row in event_roles if int(row["occurrence_count"]) > 1]
    recurrent_pair_strict = [row for row in pair_strict if int(row["occurrence_count"]) > 1]
    recurrent_pair_roles = [row for row in pair_roles if int(row["occurrence_count"]) > 1]
    check("recurrent_event_strict_templates_27", len(recurrent_event_strict) == 27, len(recurrent_event_strict))
    check("events_in_recurrent_strict_templates_61", sum(int(row["occurrence_count"]) for row in recurrent_event_strict) == 61, None)
    check("cross_page_event_strict_templates_14", sum(int(row["page_count"]) > 1 for row in event_strict) == 14, None)
    check("cross_register_event_strict_templates_8", sum(int(row["register_count"]) > 1 for row in event_strict) == 8, None)
    check("events_in_cross_register_strict_templates_20", sum(int(row["occurrence_count"]) for row in event_strict if int(row["register_count"]) > 1) == 20, None)
    check("multisurface_recurrent_event_templates_16", sum(int(row["surface_type_count"]) > 1 for row in recurrent_event_strict) == 16, None)
    check("events_in_multisurface_recurrent_templates_38", sum(int(row["occurrence_count"]) for row in recurrent_event_strict if int(row["surface_type_count"]) > 1) == 38, None)
    check("recurrent_event_role_shapes_39", len(recurrent_event_roles) == 39, len(recurrent_event_roles))
    check("events_in_recurrent_role_shapes_104", sum(int(row["occurrence_count"]) for row in recurrent_event_roles) == 104, None)
    check("cross_register_event_role_shapes_16", sum(int(row["register_count"]) > 1 for row in event_roles) == 16, None)

    check("recurrent_pair_strict_templates_1", len(recurrent_pair_strict) == 1, len(recurrent_pair_strict))
    check("pairs_in_recurrent_strict_templates_2", sum(int(row["occurrence_count"]) for row in recurrent_pair_strict) == 2, None)
    check("recurrent_pair_is_okeey_ary", recurrent_pair_strict[0]["surface_examples"] == "okeey|ary" and set(recurrent_pair_strict[0]["record_ids"].split("|")) == {"G475-R030", "G475-R042"}, recurrent_pair_strict[0])
    check("no_multisurface_recurrent_pair", all(int(row["surface_type_count"]) == 1 for row in recurrent_pair_strict), None)
    check("no_cross_page_strict_pair", all(int(row["page_count"]) == 1 for row in pair_strict), None)
    check("no_cross_register_strict_pair", all(int(row["register_count"]) == 1 for row in pair_strict), None)
    check("no_recurrent_cross_bundle_pair", all(not (int(row["strict_occurrence_count"]) > 1 and row["pair_boundary"].startswith("CROSS_BUNDLE")) for row in pair_assignments), None)
    check("recurrent_pair_role_shapes_3", len(recurrent_pair_roles) == 3, len(recurrent_pair_roles))
    check("pairs_in_recurrent_role_shapes_6", sum(int(row["occurrence_count"]) for row in recurrent_pair_roles) == 6, None)
    check("no_cross_register_role_pair", all(int(row["register_count"]) == 1 for row in pair_roles), None)

    check("strongest_event_template_exact", event_strict_map["G481-ET001"]["occurrence_count"] == "5" and event_strict_map["G481-ET001"]["register_count"] == "4" and event_strict_map["G481-ET001"]["strict_frame"].startswith("CATALOGUE[DANACH · {N1}"), event_strict_map["G481-ET001"])
    expected_cross_register_event_ids = {"G481-ET001", "G481-ET004", "G481-ET033", "G481-ET061", "G481-ET074", "G481-ET080", "G481-ET092", "G481-ET094"}
    check("cross_register_event_template_ids_exact", {row["template_id"] for row in event_strict if int(row["register_count"]) > 1} == expected_cross_register_event_ids, [row["template_id"] for row in event_strict if int(row["register_count"]) > 1])

    check("gdt480_singleton_record_count_107", sum(row["gdt480_whole_record_singleton"] == "YES" for row in coverage) == 107, None)
    singleton = [row for row in coverage if row["gdt480_whole_record_singleton"] == "YES"]
    check("singleton_any_strict_event_28", sum(int(row["recurrent_strict_event_count"]) > 0 for row in singleton) == 28, None)
    check("singleton_all_strict_events_8", sum(row["all_events_strict_recurrent"] == "YES" for row in singleton) == 8, None)
    check("singleton_any_strict_pair_0", sum(row["any_strict_pair_recurrent"] == "YES" for row in singleton) == 0, None)
    check("singleton_any_role_event_59", sum(int(row["recurrent_role_event_count"]) > 0 for row in singleton) == 59, None)
    check("singleton_all_role_events_39", sum(row["all_events_role_recurrent"] == "YES" for row in singleton) == 39, None)
    check("singleton_any_role_pair_4", sum(row["any_role_pair_recurrent"] == "YES" for row in singleton) == 4, None)
    check("singleton_no_recurrent_fragment_48", sum(row["decomposition_class"] == "SINGLETON_FRAGMENT_TAIL" for row in singleton) == 48, None)
    no_fragment = [row for row in singleton if row["decomposition_class"] == "SINGLETON_FRAGMENT_TAIL"]
    check("no_fragment_single_event_records_45", sum(int(row["event_count"]) == 1 for row in no_fragment) == 45, Counter(row["event_count"] for row in no_fragment))
    check("no_fragment_event_count_profile_exact", Counter(row["event_count"] for row in no_fragment) == Counter({"1": 45, "2": 2, "3": 1}), Counter(row["event_count"] for row in no_fragment))
    check("no_fragment_page_profile_exact", Counter(row["physical_page"] for row in no_fragment) == Counter({"f72r": 18, "f89r": 16, "f88v": 6, "f71v": 4, "f77r": 4}), Counter(row["physical_page"] for row in no_fragment))
    check("coverage_event_totals_183", sum(int(row["event_count"]) for row in coverage) == 183, None)
    check("coverage_pair_totals_48", sum(int(row["pair_count"]) for row in coverage) == 48, None)
    check("coverage_gdt480_links_exact", all(row["gdt480_strict_template_id"] == g480_map[row["record_id"]]["strict_template_id"] and row["gdt480_strict_recurrence_class"] == g480_map[row["record_id"]]["strict_recurrence_class"] for row in coverage), len(coverage))
    check("coverage_source_readings_exact", all(row["definitive_record_reading_de"] == record_map[row["record_id"]]["definitive_record_reading_de"] for row in coverage), len(coverage))

    expected_summary = {
        ("ALL_RECORDS", "ANY_RECURRENT_STRICT_EVENT"): 56,
        ("ALL_RECORDS", "ALL_EVENTS_RECURRENT_STRICT"): 36,
        ("ALL_RECORDS", "ANY_RECURRENT_STRICT_PAIR"): 2,
        ("ALL_RECORDS", "ANY_RECURRENT_ROLE_EVENT"): 87,
        ("ALL_RECORDS", "ALL_EVENTS_RECURRENT_ROLE"): 67,
        ("ALL_RECORDS", "ANY_RECURRENT_ROLE_PAIR"): 6,
        ("ALL_RECORDS", "NO_RECURRENT_FRAGMENT"): 48,
        ("GDT480_SINGLETON_RECORDS", "ANY_RECURRENT_STRICT_EVENT"): 28,
        ("GDT480_SINGLETON_RECORDS", "ALL_EVENTS_RECURRENT_STRICT"): 8,
        ("GDT480_SINGLETON_RECORDS", "ANY_RECURRENT_STRICT_PAIR"): 0,
        ("GDT480_SINGLETON_RECORDS", "ANY_RECURRENT_ROLE_EVENT"): 59,
        ("GDT480_SINGLETON_RECORDS", "ALL_EVENTS_RECURRENT_ROLE"): 39,
        ("GDT480_SINGLETON_RECORDS", "ANY_RECURRENT_ROLE_PAIR"): 4,
        ("GDT480_SINGLETON_RECORDS", "NO_RECURRENT_FRAGMENT"): 48,
    }
    actual_summary = {(row["scope"], row["metric"]): int(row["record_count"]) for row in summary}
    check("coverage_summary_exact", actual_summary == expected_summary, {f"{key[0]}:{key[1]}": value for key, value in actual_summary.items()})

    owner_terms = re.compile(r"Pflanzen|Pflanze|Sternstelle|Drogen|Droge|Badstation|Positions|Stationseinheit|Stationswert|Zielposition|Zielgefäß|Ausgangsposition|Ausgangsgefäß|Ringbahn|Sektoranteil|Namenseintragn")
    check("event_phrases_owner_neutral", all(not owner_terms.search(row["owner_neutral_phrase_de"]) for row in event_assignments), [row["source_event_id"] for row in event_assignments if owner_terms.search(row["owner_neutral_phrase_de"])][:10])
    check("pair_phrases_owner_neutral", all(not owner_terms.search(row["owner_neutral_phrase_de"]) for row in pair_assignments), [row["pair_fragment_id"] for row in pair_assignments if owner_terms.search(row["owner_neutral_phrase_de"])][:10])
    check("strict_names_slotted", all("NAME:" not in row["strict_frame"] for row in event_strict + pair_strict), None)
    allowed_role_words = re.compile(r"^(?:COORDINATE|INSTRUCTION|CATALOGUE|ORDER|ARG|REL|ACTION|NAME|MOD|NONE|SAME_BUNDLE|CROSS_BUNDLE|EXPLICIT_CONTINUATION_OL|START_FRESH_SIBLING|KEEP_ACTIVE_UNIT|FORWARD_OPEN|BRIDGE_LEFT_TO_RIGHT|BACKWARD_HOLD|TERMINAL|[\[\]{}() <>@:|/·._-])+$")
    check("event_role_vocabulary_bounded", all(allowed_role_words.fullmatch(row["role_frame"]) for row in event_roles), [row["template_id"] for row in event_roles if not allowed_role_words.fullmatch(row["role_frame"])][:10])
    check("pair_role_vocabulary_bounded", all(allowed_role_words.fullmatch(row["role_frame"]) for row in pair_roles), [row["template_id"] for row in pair_roles if not allowed_role_words.fullmatch(row["role_frame"])][:10])
    check("sealed_pages_absent", all(not row["physical_page"].startswith("f84") for row in event_assignments + pair_assignments + coverage), sorted({row["physical_page"] for row in coverage}))
    check("all_recurrent_event_ids_readable", all(row["template_id"] in readable for row in recurrent_event_strict), None)
    check("all_recurrent_pair_ids_readable", all(row["template_id"] in readable for row in recurrent_pair_strict), None)

    check("result_status_exact", result.get("status") == "EVENT_FRAGMENTS_REACH_59_OF_107_SINGLETON_RECORDS__ADJACENT_PAIRS_REMAIN_SPARSE", result.get("status"))
    check("result_assignment_counts_exact", (result.get("event_count"), result.get("adjacent_pair_count"), result.get("cross_bundle_pair_count")) == (183, 48, 11), None)
    check("result_template_counts_exact", (result.get("event_strict_template_count"), result.get("event_role_shape_count"), result.get("pair_strict_template_count"), result.get("pair_role_shape_count")) == (149, 118, 47, 45), None)
    check("result_event_recurrence_exact", (result.get("recurrent_event_strict_template_count"), result.get("events_in_recurrent_strict_templates"), result.get("recurrent_event_role_shape_count"), result.get("events_in_recurrent_role_shapes")) == (27, 61, 39, 104), None)
    check("result_pair_recurrence_exact", (result.get("recurrent_pair_strict_template_count"), result.get("pairs_in_recurrent_strict_templates"), result.get("recurrent_pair_role_shape_count"), result.get("pairs_in_recurrent_role_shapes")) == (1, 2, 3, 6), None)
    check("result_singleton_coverage_exact", (result.get("gdt480_singleton_record_count"), result.get("singleton_records_with_any_recurrent_strict_event"), result.get("singleton_records_with_all_events_recurrent_strict"), result.get("singleton_records_with_any_recurrent_role_event"), result.get("singleton_records_with_all_events_recurrent_role"), result.get("singleton_records_with_no_recurrent_fragment")) == (107, 28, 8, 59, 39, 48), None)
    check("result_no_fragment_profiles_exact", result.get("no_recurrent_fragment_single_event_record_count") == 45 and result.get("no_recurrent_fragment_event_count_profile") == {"1": 45, "2": 2, "3": 1} and result.get("no_recurrent_fragment_page_counts") == {"f71v": 4, "f72r": 18, "f77r": 4, "f88v": 6, "f89r": 16}, {key: result.get(key) for key in ("no_recurrent_fragment_single_event_record_count", "no_recurrent_fragment_event_count_profile", "no_recurrent_fragment_page_counts")})
    check("result_all_defaults_exact", (result.get("all_events_have_default_count"), result.get("all_pairs_have_default_count")) == (183, 48), None)
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
