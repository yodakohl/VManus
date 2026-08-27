#!/usr/bin/env python3
"""Validate the GDT540 target-surface context contract."""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt540_target_surface_context_requirement_contract"
OUT = BASE / "artifacts"
G539 = ROOT / "experiments/yolo/gdt539_four_page_contextual_statement_edition/artifacts"

PROSE_IN = G539 / "gdt539_546_contextual_prose_events.tsv"
OCCURRENCE = OUT / "gdt540_149_occurrence_context_contract.tsv"
SURFACE = OUT / "gdt540_145_surface_context_contract.tsv"
SUMMARY = OUT / "gdt540_context_contract_summary.tsv"
BOOK = OUT / "GDT540_TARGET_SURFACE_CONTEXT_CONTRACT.md"
RESULT = OUT / "gdt540_result.json"
VALIDATION = OUT / "gdt540_validation.json"
RUN = BASE / "src/run.py"
READER = BASE / "src/context_surface.py"
STATUS = "PASS_149_OCCURRENCES_CLASSIFIED__145_SURFACE_CONTRACTS__ONE_CONTEXT_SWITCH"

MODE_FROM_FLAGS = {
    (False, False): "SELF_CONTAINED",
    (True, False): "REQUIRES_ACTIVE_ACTION",
    (False, True): "REQUIRES_ACTIVE_ARGUMENT",
    (True, True): "REQUIRES_ACTIVE_ACTION_AND_ARGUMENT",
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def run_reader(*args: str) -> tuple[int, dict[str, object]]:
    proc = subprocess.run(
        [sys.executable, str(READER), *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    return proc.returncode, json.loads(proc.stdout)


def main() -> int:
    checks: list[dict[str, object]] = []

    def check(name: str, passed: bool, detail: object) -> None:
        checks.append({"check": name, "passed": bool(passed), "detail": detail})

    prose = read_tsv(PROSE_IN)
    occurrence = read_tsv(OCCURRENCE)
    surfaces = read_tsv(SURFACE)
    summary = read_tsv(SUMMARY)
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    targets = [row for row in prose if row["recipe_source"] == "GDT538_FINAL_SURFACE"]
    source_by_event = {row["event_id"]: row for row in prose}
    occurrence_by_event = {row["event_id"]: row for row in occurrence}
    surface_by_key = {row["surface"]: row for row in surfaces}

    check("source_prose_count", len(prose) == 546, len(prose))
    check("source_target_event_count", len(targets) == 149, len(targets))
    check("source_target_surface_count", len({row["surface"] for row in targets}) == 145, len({row["surface"] for row in targets}))
    check("occurrence_count", len(occurrence) == 149, len(occurrence))
    check("surface_count", len(surfaces) == 145, len(surfaces))
    check("occurrence_event_uniqueness", len(occurrence_by_event) == 149, len(occurrence_by_event))
    check("surface_key_uniqueness", len(surface_by_key) == 145, len(surface_by_key))
    check("target_event_set", set(occurrence_by_event) == {row["event_id"] for row in targets}, len(set(occurrence_by_event) ^ {row["event_id"] for row in targets}))
    check("occurrence_source_order", [row["event_id"] for row in occurrence] == [row["event_id"] for row in targets], len(occurrence))

    recipe_mismatches = []
    root_mismatches = []
    mode_mismatches = []
    roundtrip_mismatches = []
    source_errors = []
    action_distances: list[int] = []
    argument_distances: list[int] = []
    for source in targets:
        row = occurrence_by_event[source["event_id"]]
        if row["final_recipe"] != source["final_context_recipe"]:
            recipe_mismatches.append(source["event_id"])
        if (
            row["explicit_action_roots"] != source["explicit_action_roots"]
            or row["explicit_argument_roots"] != source["explicit_argument_roots"]
            or row["incoming_action_root"] != source["inherited_action_root"]
            or row["incoming_argument_root"] != source["inherited_argument_root"]
        ):
            root_mismatches.append(source["event_id"])
        expected_mode = MODE_FROM_FLAGS[
            (
                source["inherited_action_root"] != "NONE",
                source["inherited_argument_root"] != "NONE",
            )
        ]
        if row["known_occurrence_requirement"] != expected_mode:
            mode_mismatches.append(source["event_id"])
        if row["exact_recipe_roundtrip"] != row["final_recipe"]:
            roundtrip_mismatches.append(source["event_id"])
        for kind in ("action", "argument"):
            source_id = row[f"incoming_{kind}_source_event_id"]
            distance = row[f"incoming_{kind}_distance_cards"]
            if source_id == "NONE":
                if distance != "NONE":
                    source_errors.append((source["event_id"], kind, "distance_without_source"))
                continue
            source_row = source_by_event.get(source_id)
            expected_distance = (
                int(row["card_ordinal_in_statement"])
                - int(source_row["card_ordinal_in_statement"])
                if source_row
                else -999
            )
            if (
                source_row is None
                or source_row["statement_id"] != row["statement_id"]
                or expected_distance <= 0
                or str(expected_distance) != distance
            ):
                source_errors.append((source["event_id"], kind, source_id))
            (action_distances if kind == "action" else argument_distances).append(expected_distance)

    check("recipe_replay", not recipe_mismatches, recipe_mismatches)
    check("root_trace_replay", not root_mismatches, root_mismatches)
    check("mode_replay", not mode_mismatches, mode_mismatches)
    check("exact_recipe_roundtrip", not roundtrip_mismatches, roundtrip_mismatches)
    check("context_sources_same_statement_leftward", not source_errors, source_errors)
    check("action_dependency_count", len(action_distances) == 16, len(action_distances))
    check("argument_dependency_count", len(argument_distances) == 52, len(argument_distances))
    check("action_distance_distribution", Counter(action_distances) == Counter({1: 8, 2: 6, 3: 2}), dict(sorted(Counter(action_distances).items())))
    check("argument_distance_distribution", Counter(argument_distances) == Counter({1: 39, 2: 9, 3: 4}), dict(sorted(Counter(argument_distances).items())))

    mode_counts = Counter(row["known_occurrence_requirement"] for row in occurrence)
    expected_modes = {
        "SELF_CONTAINED": 92,
        "REQUIRES_ACTIVE_ACTION": 5,
        "REQUIRES_ACTIVE_ARGUMENT": 41,
        "REQUIRES_ACTIVE_ACTION_AND_ARGUMENT": 11,
    }
    check("occurrence_mode_distribution", mode_counts == expected_modes, dict(mode_counts))
    check("known_action_need_flags", all((row["known_clause_needs_active_action"] == "YES") == (row["incoming_action_root"] != "NONE") for row in occurrence), len(occurrence))
    check("known_argument_need_flags", all((row["known_clause_needs_active_argument"] == "YES") == (row["incoming_argument_root"] != "NONE") for row in occurrence), len(occurrence))
    check("resolved_action_complete", all(row["resolved_action_root"] != "NONE" for row in occurrence), len(occurrence))

    future_rule_errors = []
    for row in occurrence:
        has_action = row["explicit_action_roots"] != "NONE"
        has_argument = row["explicit_argument_roots"] != "NONE"
        expected_action_rule = (
            "USE_VISIBLE_ACTIONS__LAST_VISIBLE_ACTION_BECOMES_ACTIVE"
            if has_action
            else "USE_SAME_STATEMENT_ACTIVE_ACTION__ELSE_RENDER_NONVERBAL_FRAGMENT"
        )
        expected_argument_rule = (
            "USE_VISIBLE_ARGUMENTS__LAST_VISIBLE_ARGUMENT_BECOMES_ACTIVE"
            if has_argument
            else "USE_SAME_STATEMENT_ACTIVE_ARGUMENT_IF_AVAILABLE__ELSE_OBJECTLESS"
        )
        if row["future_action_contract"] != expected_action_rule or row["future_argument_contract"] != expected_argument_rule:
            future_rule_errors.append(row["event_id"])
    check("occurrence_future_rule_factorization", not future_rule_errors, future_rule_errors)

    surface_event_total = sum(int(row["event_count"]) for row in surfaces)
    check("surface_event_total", surface_event_total == 149, surface_event_total)
    profile_counts = Counter(row["observed_requirement_modes"] for row in surfaces)
    expected_profiles = {
        "SELF_CONTAINED": 88,
        "REQUIRES_ACTIVE_ARGUMENT": 40,
        "REQUIRES_ACTIVE_ACTION": 5,
        "REQUIRES_ACTIVE_ACTION_AND_ARGUMENT": 11,
        "SELF_CONTAINED|REQUIRES_ACTIVE_ARGUMENT": 1,
    }
    check("surface_profile_distribution", profile_counts == expected_profiles, dict(profile_counts))
    repeated = {row["surface"]: int(row["event_count"]) for row in surfaces if int(row["event_count"]) > 1}
    check("repeated_surface_inventory", repeated == {"keody": 3, "qokees": 2, "shain": 2}, repeated)
    switches = [row["surface"] for row in surfaces if row["surface_evidence_class"] == "REPEATED_CONTEXT_SWITCH"]
    check("context_switch_inventory", switches == ["qokees"], switches)
    consistent = [row["surface"] for row in surfaces if row["surface_evidence_class"] == "REPEATED_CONSISTENT_MODE"]
    check("consistent_repeat_inventory", consistent == ["keody", "shain"], consistent)
    check("singleton_surface_count", sum(row["surface_evidence_class"] == "SINGLETON_ONE_OBSERVED_MODE" for row in surfaces) == 142, sum(row["surface_evidence_class"] == "SINGLETON_ONE_OBSERVED_MODE" for row in surfaces))
    check("qokees_recipe", surface_by_key["qokees"]["final_recipe"] == "OK+EE+S", surface_by_key["qokees"]["final_recipe"])
    check("qokees_mode_switch", surface_by_key["qokees"]["observed_requirement_modes"] == "SELF_CONTAINED|REQUIRES_ACTIVE_ARGUMENT", surface_by_key["qokees"]["observed_requirement_modes"])
    check("qokees_argument_contract", surface_by_key["qokees"]["future_argument_contract"] == "USE_SAME_STATEMENT_ACTIVE_ARGUMENT_IF_AVAILABLE__ELSE_OBJECTLESS", surface_by_key["qokees"]["future_argument_contract"])
    check("surface_contract_coverage", all(row["future_action_contract"] and row["future_argument_contract"] and row["new_page_intake_de"] for row in surfaces), len(surfaces))
    check("surface_minimum_state_factor", all(row["minimum_future_state_for_verbal_clause"] == ("NONE" if row["visible_action_roots"] != "NONE" else "ACTIVE_ACTION") for row in surfaces), len(surfaces))
    check("surface_recipe_roundtrip_from_occurrences", all({occurrence_by_event[event_id]["final_recipe"] for event_id in row["event_ids"].split("|")} == {row["final_recipe"]} for row in surfaces), len(surfaces))

    summary_map = {row["metric"]: row["value"] for row in summary}
    expected_summary = {
        "target_occurrence_count": "149",
        "target_surface_count": "145",
        "target_statement_count": "49",
        "repeated_surface_count": "3",
        "repeated_context_switch_surface_count": "1",
        "max_action_source_distance_cards": "3",
        "max_argument_source_distance_cards": "3",
        "same_statement_source_count": "68",
        "future_rule_surface_coverage": "145",
    }
    check("summary_required_metrics", all(summary_map.get(key) == value for key, value in expected_summary.items()), {key: summary_map.get(key) for key in expected_summary})

    book = BOOK.read_text(encoding="utf-8")
    check("book_status", STATUS in book, STATUS)
    check("book_surface_inventory", all(f"`{surface}`" in book for surface in surface_by_key), len(surface_by_key))
    check("book_qokees_switch", "Argument übernehmen, falls vorhanden; sonst objektlos" in book, "qokees")

    reader_cases = []
    code, data = run_reader("qokees")
    reader_cases.append((code, data.get("status"), data.get("resolved_argument_root")))
    check("reader_qokees_objectless", code == 0 and data["status"] == "READY_FOR_CONTEXTUAL_WORKING_READING" and data["resolved_argument_root"] == "NONE" and data["argument_source"] == "OBJECTLESS", data)
    code, data = run_reader("qokees", "--active-argument", "Y")
    reader_cases.append((code, data.get("status"), data.get("resolved_argument_root")))
    check("reader_qokees_inherits_y", code == 0 and data["resolved_action_root"] == "S" and data["resolved_argument_root"] == "Y" and data["argument_source"] == "SAME_STATEMENT_STATE", data)
    code, data = run_reader("folchol")
    reader_cases.append((code, data.get("status"), data.get("resolved_action_root")))
    check("reader_folchol_fragment_without_action", code == 0 and data["status"] == "NONVERBAL_FRAGMENT_ONLY__MISSING_ACTIVE_ACTION", data)
    code, data = run_reader("folchol", "--active-action", "SH")
    reader_cases.append((code, data.get("status"), data.get("resolved_action_root")))
    check("reader_folchol_inherits_action", code == 0 and data["status"] == "READY_FOR_CONTEXTUAL_WORKING_READING" and data["resolved_action_root"] == "SH", data)
    code, data = run_reader("doiiin", "--active-action", "P", "--active-argument", "Y")
    reader_cases.append((code, data.get("status"), data.get("resolved_action_root")))
    check("reader_doiiin_inherits_both", code == 0 and data["resolved_action_root"] == "P" and data["resolved_argument_root"] == "Y", data)
    code, data = run_reader("shain")
    reader_cases.append((code, data.get("status"), data.get("resolved_action_root")))
    check("reader_shain_visible_both", code == 0 and data["resolved_action_root"] == "SH" and data["resolved_argument_root"] == "AIN", data)
    code, data = run_reader("not_a_gdt540_surface")
    reader_cases.append((code, data.get("status"), data.get("delegation")))
    check("reader_unknown_delegates", code == 2 and data["status"] == "UNKNOWN_GDT540_TARGET_SURFACE" and data["delegation"] == "GDT539_OR_LOWER_READER", data)
    check("reader_case_count", len(reader_cases) == 7, reader_cases)

    expected_result = {
        "status": STATUS,
        "target_occurrence_count": 149,
        "target_surface_count": 145,
        "target_statement_count": 49,
        "self_contained_occurrence_count": 92,
        "active_action_occurrence_count": 5,
        "active_argument_occurrence_count": 41,
        "both_active_occurrence_count": 11,
        "self_contained_only_surface_count": 88,
        "active_action_only_surface_count": 5,
        "active_argument_only_surface_count": 40,
        "both_active_only_surface_count": 11,
        "mixed_mode_surface_count": 1,
        "mixed_mode_surfaces": ["qokees"],
        "repeated_surface_count": 3,
        "repeated_surfaces": ["keody", "qokees", "shain"],
        "max_action_source_distance_cards": 3,
        "max_argument_source_distance_cards": 3,
        "new_pages": 0,
        "root_meaning_changes": 0,
        "recipe_changes": 0,
    }
    check("result_exact", result == expected_result, result)

    generated = [OCCURRENCE, SURFACE, SUMMARY, BOOK, RESULT]
    before = {path.name: sha256(path) for path in generated}
    rerun = subprocess.run(
        [sys.executable, str(RUN)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    after = {path.name: sha256(path) for path in generated}
    check("generator_rerun_exit", rerun.returncode == 0, rerun.stdout + rerun.stderr)
    check("generator_byte_determinism", before == after, after)

    failed = [item for item in checks if not item["passed"]]
    validation = {
        "status": "PASS" if not failed else "FAIL",
        "check_count": len(checks),
        "passed_count": len(checks) - len(failed),
        "failed_count": len(failed),
        "checks": checks,
    }
    VALIDATION.write_text(
        json.dumps(validation, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(validation, ensure_ascii=False, indent=2))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
