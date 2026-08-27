#!/usr/bin/env python3
"""Validate the GDT541 old-prefix exact-recipe context replay."""

from __future__ import annotations

import csv
import hashlib
import json
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
BASE = ROOT / "experiments/yolo/gdt541_old_prefix_exact_recipe_context_replay"
OUT = BASE / "artifacts"
G407 = ROOT / "experiments/yolo/gdt407_unified_twenty_six_page_workshop_edition/artifacts"
G516 = ROOT / "experiments/yolo/gdt516_thirty_page_new_surface_family_consolidation/artifacts"
G539 = ROOT / "experiments/yolo/gdt539_four_page_contextual_statement_edition/artifacts"
G540 = ROOT / "experiments/yolo/gdt540_target_surface_context_requirement_contract/artifacts"

OLD_EVENTS_IN = G407 / "gdt407_4576_running_event_edition.tsv"
OLD_STATEMENTS_IN = G407 / "gdt407_715_statement_edition.tsv"
G516_EXACT_IN = G516 / "gdt516_10_exact_old_recipe_carriers.tsv"
NEW_PROSE_IN = G539 / "gdt539_546_contextual_prose_events.tsv"
TARGET_IN = G540 / "gdt540_145_surface_context_contract.tsv"
TARGET_OCC_IN = G540 / "gdt540_149_occurrence_context_contract.tsv"

OLD_MATCH = OUT / "gdt541_49_old_exact_recipe_context_events.tsv"
PROFILE = OUT / "gdt541_11_recipe_context_profile_transfer.tsv"
QOKEES = OUT / "gdt541_7_ok_ee_s_cross_page_family.tsv"
SUMMARY = OUT / "gdt541_exact_recipe_context_summary.tsv"
BOOK = OUT / "GDT541_OLD_PREFIX_CONTEXT_REPLAY_BOOK.md"
RESULT = OUT / "gdt541_result.json"
VALIDATION = OUT / "gdt541_validation.json"
RUN = BASE / "src/run.py"
READER = BASE / "src/recipe_profile.py"
STATUS = "PASS_11_EXACT_RECIPE_PROFILES_REPLAY__QOKEES_SWITCH_REPLICATED"

ACTION_ROOTS = {"OK", "CH", "SH", "K", "S", "CHD", "T", "R", "P"}
ARGUMENT_ROOTS = {"Y", "AIIN", "AIN", "OR"}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def requirement(inherited_action: str, inherited_argument: str) -> str:
    if inherited_action and inherited_argument:
        return "REQUIRES_ACTIVE_ACTION_AND_ARGUMENT"
    if inherited_action:
        return "REQUIRES_ACTIVE_ACTION"
    if inherited_argument:
        return "REQUIRES_ACTIVE_ARGUMENT"
    return "SELF_CONTAINED"


def reader(*args: str) -> tuple[int, dict[str, object]]:
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

    old_events = read_tsv(OLD_EVENTS_IN)
    old_statements = read_tsv(OLD_STATEMENTS_IN)
    g516_exact = read_tsv(G516_EXACT_IN)
    new_prose = read_tsv(NEW_PROSE_IN)
    targets = read_tsv(TARGET_IN)
    target_occ = read_tsv(TARGET_OCC_IN)
    old_match = read_tsv(OLD_MATCH)
    profiles = read_tsv(PROFILE)
    qokees = read_tsv(QOKEES)
    summary = read_tsv(SUMMARY)
    result = json.loads(RESULT.read_text(encoding="utf-8"))

    check("old_event_count", len(old_events) == 4576, len(old_events))
    check("old_statement_count", len(old_statements) == 715, len(old_statements))
    check("gdt516_exact_count", len(g516_exact) == 10, len(g516_exact))
    check("new_prose_count", len(new_prose) == 546, len(new_prose))
    check("target_surface_count", len(targets) == 145, len(targets))
    check("target_occurrence_count", len(target_occ) == 149, len(target_occ))
    check("target_recipe_uniqueness", len({row["final_recipe"] for row in targets}) == 145, len({row["final_recipe"] for row in targets}))
    check("old_event_id_uniqueness", len({row["global_running_event_id"] for row in old_events}) == 4576, len({row["global_running_event_id"] for row in old_events}))

    events_by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for event in old_events:
        events_by_statement[event["source_statement_id"]].append(event)
    statement_key_set = {row["source_statement_id"] for row in old_statements}
    check("statement_key_set", set(events_by_statement) == statement_key_set, len(set(events_by_statement) ^ statement_key_set))
    statement_count_errors = []
    statement_surface_errors = []
    statement_recipe_errors = []
    for statement in old_statements:
        material = sorted(events_by_statement[statement["source_statement_id"]], key=lambda row: int(row["global_running_ordinal"]))
        if len(material) != int(statement["event_count"]):
            statement_count_errors.append(statement["global_statement_id"])
        if " ".join(row["surface"] for row in material) != statement["surface_sequence"]:
            statement_surface_errors.append(statement["global_statement_id"])
        if " | ".join(row["component_recipe"] for row in material) != statement["recipe_sequence"]:
            statement_recipe_errors.append(statement["global_statement_id"])
    check("statement_event_counts", not statement_count_errors, statement_count_errors)
    check("statement_surface_replay", not statement_surface_errors, statement_surface_errors)
    check("statement_recipe_replay", not statement_recipe_errors, statement_recipe_errors)

    target_by_recipe = {row["final_recipe"]: row for row in targets}
    selected_source = [row for row in old_events if row["component_recipe"] in target_by_recipe]
    old_match_by_id = {row["old_global_event_id"]: row for row in old_match}
    check("selected_old_match_count", len(selected_source) == 49, len(selected_source))
    check("selected_old_recipe_count", len({row["component_recipe"] for row in selected_source}) == 11, len({row["component_recipe"] for row in selected_source}))
    check("artifact_old_match_count", len(old_match) == 49, len(old_match))
    check("artifact_old_event_uniqueness", len(old_match_by_id) == 49, len(old_match_by_id))
    check("old_event_set", set(old_match_by_id) == {row["global_running_event_id"] for row in selected_source}, len(set(old_match_by_id) ^ {row["global_running_event_id"] for row in selected_source}))
    check("old_exact_recipe_replay", all(old_match_by_id[row["global_running_event_id"]]["target_recipe"] == row["component_recipe"] for row in selected_source), len(selected_source))
    check("new_surfaces_absent_from_old_prefix", all(row["surface_same_as_target"] == "NO" for row in old_match), sum(row["surface_same_as_target"] == "YES" for row in old_match))
    check("old_surface_count", len({row["old_surface"] for row in old_match}) == 17, len({row["old_surface"] for row in old_match}))
    check("old_page_count", len({row["physical_page"] for row in old_match}) == 17, len({row["physical_page"] for row in old_match}))
    check("old_statement_contact_count", len({row["old_statement_id"] for row in old_match}) == 43, len({row["old_statement_id"] for row in old_match}))
    check("old_register_inventory", {row["register"] for row in old_match} == {"SOURCE_SECTION_T", "HERBAL", "CELESTIAL", "BIOLOGICAL", "PHARMA"}, sorted({row["register"] for row in old_match}))

    # Independently replay the two same-statement slots and compare every selected event.
    replay_errors = []
    action_distances: list[int] = []
    argument_distances: list[int] = []
    for statement in sorted(old_statements, key=lambda row: int(row["global_statement_ordinal"])):
        material = sorted(events_by_statement[statement["source_statement_id"]], key=lambda row: int(row["global_running_ordinal"]))
        active_action = ""
        active_argument = ""
        action_source = ""
        argument_source = ""
        ordinal_by_id = {row["global_running_event_id"]: pos for pos, row in enumerate(material, 1)}
        for pos, event in enumerate(material, 1):
            atoms = event["component_recipe"].split("+")
            actions = [atom for atom in atoms if atom in ACTION_ROOTS]
            arguments = [atom for atom in atoms if atom in ARGUMENT_ROOTS]
            inherited_action = ""
            inherited_argument = ""
            inherited_action_source = ""
            inherited_argument_source = ""
            if actions:
                active_action = actions[-1]
                action_source = event["global_running_event_id"]
            elif active_action and atoms != ["DY"]:
                inherited_action = active_action
                inherited_action_source = action_source
            if arguments:
                active_argument = arguments[-1]
                argument_source = event["global_running_event_id"]
            elif active_argument and (actions or inherited_action) and atoms != ["DY"]:
                inherited_argument = active_argument
                inherited_argument_source = argument_source
            if event["global_running_event_id"] not in old_match_by_id:
                continue
            row = old_match_by_id[event["global_running_event_id"]]
            expected = {
                "explicit_action_roots": "|".join(actions) or "NONE",
                "incoming_action_root": inherited_action or "NONE",
                "incoming_action_source_event_id": inherited_action_source or "NONE",
                "explicit_argument_roots": "|".join(arguments) or "NONE",
                "incoming_argument_root": inherited_argument or "NONE",
                "incoming_argument_source_event_id": inherited_argument_source or "NONE",
                "old_requirement_mode": requirement(inherited_action, inherited_argument),
                "resolved_action_root": actions[-1] if actions else inherited_action or "NONE",
                "resolved_argument_root": arguments[-1] if arguments else inherited_argument or "NONE",
            }
            if any(row[key] != value for key, value in expected.items()):
                replay_errors.append((event["global_running_event_id"], expected))
            if inherited_action_source:
                distance = pos - ordinal_by_id[inherited_action_source]
                action_distances.append(distance)
                if row["incoming_action_distance_cards"] != str(distance):
                    replay_errors.append((event["global_running_event_id"], "action_distance"))
            if inherited_argument_source:
                distance = pos - ordinal_by_id[inherited_argument_source]
                argument_distances.append(distance)
                if row["incoming_argument_distance_cards"] != str(distance):
                    replay_errors.append((event["global_running_event_id"], "argument_distance"))
    check("independent_context_replay", not replay_errors, replay_errors)
    check("old_action_distance_distribution", Counter(action_distances) == Counter({1: 2, 2: 1}), dict(sorted(Counter(action_distances).items())))
    check("old_argument_distance_distribution", Counter(argument_distances) == Counter({1: 7, 2: 1, 3: 2}), dict(sorted(Counter(argument_distances).items())))
    old_modes = Counter(row["old_requirement_mode"] for row in old_match)
    check("old_mode_distribution", old_modes == Counter({"SELF_CONTAINED": 39, "REQUIRES_ACTIVE_ARGUMENT": 7, "REQUIRES_ACTIVE_ACTION_AND_ARGUMENT": 3}), dict(old_modes))

    expected_carrier_counts = {
        "chekchy": 29,
        "chekeey": 6,
        "dalol": 1,
        "doiiin": 2,
        "okoy": 1,
        "qocthedy": 1,
        "qokaiir": 2,
        "qokchey": 1,
        "qokee": 1,
        "qokees": 4,
        "shee": 1,
    }
    profile_by_surface = {row["target_surface"]: row for row in profiles}
    check("profile_count", len(profiles) == 11, len(profiles))
    check("profile_surface_inventory", set(profile_by_surface) == set(expected_carrier_counts), sorted(profile_by_surface))
    check("profile_carrier_counts", {surface: int(profile_by_surface[surface]["old_carrier_event_count"]) for surface in profile_by_surface} == expected_carrier_counts, {surface: int(profile_by_surface[surface]["old_carrier_event_count"]) for surface in profile_by_surface})
    check("profile_exact_matches", all(row["profile_relation"] == "EXACT_PROFILE_MATCH" for row in profiles), [row["target_surface"] for row in profiles if row["profile_relation"] != "EXACT_PROFILE_MATCH"])
    check("profile_mode_set_equality", all(set(row["target_observed_modes"].split("|")) == set(row["old_observed_modes"].split("|")) for row in profiles), len(profiles))
    contextual = [row["target_surface"] for row in profiles if row["replication_kind"] == "CONTEXTUAL_EXACT_RECIPE_REPLICATION"]
    check("contextual_profile_inventory", contextual == ["dalol", "doiiin", "qokaiir", "qokee", "qokees", "shee"], contextual)
    g516_surfaces = {row["surface"] for row in g516_exact}
    check("gdt516_ten_retained", g516_surfaces < set(profile_by_surface), sorted(g516_surfaces))
    check("post_gdt516_contact", set(profile_by_surface) - g516_surfaces == {"chekchy"}, sorted(set(profile_by_surface) - g516_surfaces))
    check("chekchy_old_support", profile_by_surface["chekchy"]["target_recipe"] == "CH+K+Y" and profile_by_surface["chekchy"]["old_carrier_event_count"] == "29" and profile_by_surface["chekchy"]["old_surface_count"] == "5", profile_by_surface["chekchy"])

    check("qokees_family_count", len(qokees) == 7, len(qokees))
    check("qokees_exact_recipe", all(row["recipe"] == "OK+EE+S" for row in qokees), len(qokees))
    check("qokees_layer_split", Counter(row["corpus_layer"] for row in qokees) == Counter({"OLD_GDT407_PREFIX": 4, "SELECTED_GDT539_FOUR_PAGES": 3}), dict(Counter(row["corpus_layer"] for row in qokees)))
    check("qokees_mode_split", Counter(row["argument_mode"] for row in qokees) == Counter({"ARGUMENT_FROM_SAME_STATEMENT": 5, "OBJECTLESS": 2}), dict(Counter(row["argument_mode"] for row in qokees)))
    old_qokees = [row for row in qokees if row["corpus_layer"] == "OLD_GDT407_PREFIX"]
    check("old_qokees_switch", Counter(row["argument_mode"] for row in old_qokees) == Counter({"ARGUMENT_FROM_SAME_STATEMENT": 3, "OBJECTLESS": 1}), dict(Counter(row["argument_mode"] for row in old_qokees)))
    check("qokees_surface_inventory", {row["surface"] for row in qokees} == {"qokees", "okees", "chokees"}, sorted({row["surface"] for row in qokees}))
    check("qokees_page_inventory", {row["physical_page"] for row in qokees} == {"f31r", "f66r", "f72r", "f76r"}, sorted({row["physical_page"] for row in qokees}))
    check("qokees_register_count", len({row["register"] for row in qokees}) == 4, sorted({row["register"] for row in qokees}))
    check("qokees_argument_is_y", all(row["incoming_argument_root"] == "Y" for row in qokees if row["argument_mode"] == "ARGUMENT_FROM_SAME_STATEMENT"), [(row["event_id"], row["incoming_argument_root"]) for row in qokees])
    check("qokees_argument_immediate", all(row["immediate_previous_surface"] != "NONE" and row["incoming_argument_source_event_id"] != "NONE" for row in qokees if row["argument_mode"] == "ARGUMENT_FROM_SAME_STATEMENT"), [(row["event_id"], row["immediate_previous_surface"]) for row in qokees])
    objectless_contexts = {(row["corpus_layer"], row["immediate_previous_surface"]) for row in qokees if row["argument_mode"] == "OBJECTLESS"}
    check("qokees_objectless_contexts", objectless_contexts == {("OLD_GDT407_PREFIX", "qoked"), ("SELECTED_GDT539_FOUR_PAGES", "NONE")}, sorted(objectless_contexts))

    summary_map = {row["metric"]: row["value"] for row in summary}
    expected_summary = {
        "target_recipe_count": "145",
        "old_exact_carrier_recipe_count": "11",
        "old_exact_carrier_event_count": "49",
        "old_exact_carrier_surface_count": "17",
        "old_exact_carrier_page_count": "17",
        "old_exact_carrier_statement_count": "43",
        "old_exact_carrier_register_count": "5",
        "exact_profile_match_count": "11",
        "contextual_profile_match_count": "6",
        "qokees_family_event_count": "7",
        "qokees_family_argument_event_count": "5",
        "qokees_family_objectless_event_count": "2",
        "post_gdt516_new_exact_contact": "chekchy",
    }
    check("summary_required_metrics", all(summary_map.get(key) == value for key, value in expected_summary.items()), {key: summary_map.get(key) for key in expected_summary})

    book = BOOK.read_text(encoding="utf-8")
    check("book_status", STATUS in book, STATUS)
    check("book_profile_inventory", all(f"`{surface}`" in book for surface in profile_by_surface), len(profile_by_surface))
    check("book_qokees_counts", "Fünf übernehmen" in book and "zwei bleiben objektlos" in book, "OK+EE+S")

    code, data = reader("qokees")
    check("reader_qokees", code == 0 and data["profile_relation"] == "EXACT_PROFILE_MATCH" and data["old_carrier_event_count"] == 4 and len(data["old_events"]) == 4, data)
    code, data = reader("CH+K+Y")
    check("reader_recipe_key", code == 0 and data["target_surface"] == "chekchy" and data["old_carrier_event_count"] == 29, {key: data[key] for key in ("status", "target_surface", "old_carrier_event_count")})
    code, data = reader("folchol")
    check("reader_uncovered_delegates", code == 2 and data["status"] == "NO_OLD_EXACT_RECIPE_PROFILE" and data["delegation"] == "GDT540_SURFACE_CONTRACT", data)

    expected_result = {
        "status": STATUS,
        "target_recipe_count": 145,
        "old_exact_carrier_recipe_count": 11,
        "old_exact_carrier_event_count": 49,
        "old_exact_carrier_surface_count": 17,
        "old_exact_carrier_page_count": 17,
        "old_exact_carrier_statement_count": 43,
        "old_exact_carrier_register_count": 5,
        "exact_profile_match_count": 11,
        "contextual_profile_match_count": 6,
        "old_mode_counts": {
            "REQUIRES_ACTIVE_ACTION_AND_ARGUMENT": 3,
            "REQUIRES_ACTIVE_ARGUMENT": 7,
            "SELF_CONTAINED": 39,
        },
        "qokees_family_event_count": 7,
        "qokees_family_argument_event_count": 5,
        "qokees_family_objectless_event_count": 2,
        "post_gdt516_new_exact_contact_surface": "chekchy",
        "post_gdt516_new_exact_contact_old_event_count": 29,
        "new_pages": 0,
        "recipe_changes": 0,
        "root_meaning_changes": 0,
    }
    check("result_exact", result == expected_result, result)

    generated = [OLD_MATCH, PROFILE, QOKEES, SUMMARY, BOOK, RESULT]
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
    VALIDATION.write_text(json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(validation, ensure_ascii=False, indent=2))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
