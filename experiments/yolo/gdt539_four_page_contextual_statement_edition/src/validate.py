#!/usr/bin/env python3
"""Independent checks for GDT539 statement and role-scope outputs."""

from __future__ import annotations

import csv
import hashlib
import importlib.util
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
BASE = ROOT / "experiments/yolo/gdt539_four_page_contextual_statement_edition"
OUT = BASE / "artifacts"
G516 = ROOT / "experiments/yolo/gdt516_thirty_page_new_surface_family_consolidation/artifacts"
G515 = ROOT / "experiments/yolo/gdt515_second_random_four_page_full_admission/artifacts"
G538 = ROOT / "experiments/yolo/gdt538_final_159_phrase_consistency_edition/artifacts"

EVENTS_IN = G516 / "gdt516_597_contextualized_event_edition.tsv"
STATEMENTS_IN = G515 / "gdt515_prose_statement_edition.tsv"
PHRASES_IN = G538 / "gdt538_159_complete_phrase_dictionary.tsv"
ATOMS_IN = G538 / "gdt538_34_atom_phrase_lexicon.tsv"
PROSE = OUT / "gdt539_546_contextual_prose_events.tsv"
STATEMENTS = OUT / "gdt539_78_contextual_statements.tsv"
LOCAL = OUT / "gdt539_51_local_role_retention.tsv"
ROLES = OUT / "gdt539_159_surface_role_scopes.tsv"
LOCAL_DEFAULTS = OUT / "gdt539_14_local_surface_defaults.tsv"
ELLIPSIS = OUT / "gdt539_ellipsis_summary.tsv"
PAGES = OUT / "gdt539_4_page_summary.tsv"
BOOK = OUT / "GDT539_FOUR_PAGE_CONTEXTUAL_WORKING_EDITION.md"
RESULT = OUT / "gdt539_result.json"
VALIDATION = OUT / "gdt539_validation.json"
RUN = BASE / "src/run.py"
CLI = BASE / "src/role_surface.py"
EXTRA_CONTROLLED = {
    "HO": "[Klasse]",
    "LOCAL_CHAR_I": "[lokale Variante i]",
    "S_ADDR": "[hier: S-Adresse]",
    "LOCAL_CHAR_G": "[lokale Variante g]",
    "LOCAL_NAME_CORE_D": "[lokaler Namenkern d]",
}
CHANGED_SURFACES = {
    "keeol", "saiis", "aiicthy", "dairykodas", "dsholdaiir",
    "dalcheeeky", "chekchy", "kcheody",
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def import_reader():
    spec = importlib.util.spec_from_file_location("gdt539_role_surface", CLI)
    if spec is None or spec.loader is None:
        raise RuntimeError("Cannot import GDT539 role reader")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    source_events = read_tsv(EVENTS_IN)
    source_statements = read_tsv(STATEMENTS_IN)
    phrase_rows = read_tsv(PHRASES_IN)
    atom_rows = read_tsv(ATOMS_IN)
    prose = read_tsv(PROSE)
    statements = read_tsv(STATEMENTS)
    local = read_tsv(LOCAL)
    roles = read_tsv(ROLES)
    local_defaults = read_tsv(LOCAL_DEFAULTS)
    ellipsis = read_tsv(ELLIPSIS)
    pages = read_tsv(PAGES)
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    checks: list[dict[str, object]] = []

    def check(name: str, passed: bool, detail: object) -> None:
        checks.append({"check": name, "passed": bool(passed), "detail": detail})

    final_by_surface = {row["surface"]: row for row in phrase_rows}
    source_by_event = {row["event_id"]: row for row in source_events}
    prose_by_event = {row["event_id"]: row for row in prose}
    local_by_event = {row["event_id"]: row for row in local}
    role_by_surface = {row["surface"]: row for row in roles}
    local_default_by_surface = {row["surface"]: row for row in local_defaults}
    controlled = {row["atom"]: row["controlled_realization_de"] for row in atom_rows}
    controlled.update(EXTRA_CONTROLLED)

    check("source_event_count", len(source_events) == 597, len(source_events))
    check("source_statement_count", len(source_statements) == 78, len(source_statements))
    check("source_phrase_count", len(phrase_rows) == 159, len(phrase_rows))
    check("prose_event_count", len(prose) == 546, len(prose))
    check("statement_count", len(statements) == 78, len(statements))
    check("local_event_count", len(local) == 51, len(local))
    check("role_surface_count", len(roles) == 159, len(roles))
    check("local_default_count", len(local_defaults) == 14, len(local_defaults))
    check("ellipsis_class_count", len(ellipsis) == 4, len(ellipsis))
    check("page_count", len(pages) == 4, len(pages))

    source_prose_ids = {row["event_id"] for row in source_events if row["statement_id"] != "NONE"}
    source_local_ids = {row["event_id"] for row in source_events if row["statement_id"] == "NONE"}
    check("prose_event_partition", set(prose_by_event) == source_prose_ids, len(prose_by_event))
    check("local_event_partition", set(local_by_event) == source_local_ids, len(local_by_event))
    check("complete_event_partition", not (set(prose_by_event) & set(local_by_event)), 597)
    check(
        "all_source_events_covered",
        set(prose_by_event) | set(local_by_event) == set(source_by_event),
        len(set(prose_by_event) | set(local_by_event)),
    )

    expected_target_prose = {
        row["event_id"] for row in source_events
        if row["statement_id"] != "NONE" and row["surface"] in final_by_surface
    }
    expected_target_local = {
        row["event_id"] for row in source_events
        if row["statement_id"] == "NONE" and row["surface"] in final_by_surface
    }
    actual_target_prose = {
        row["event_id"] for row in prose if row["recipe_source"] == "GDT538_FINAL_SURFACE"
    }
    actual_target_local = {
        row["event_id"] for row in local if row["gdt538_surface_member"] == "YES"
    }
    check("target_prose_occurrences", actual_target_prose == expected_target_prose, len(actual_target_prose))
    check("target_local_occurrences", actual_target_local == expected_target_local, len(actual_target_local))
    check("target_prose_count", len(actual_target_prose) == 149, len(actual_target_prose))
    check("target_local_count", len(actual_target_local) == 19, len(actual_target_local))

    expected_prose_surfaces = {source_by_event[event]["surface"] for event in expected_target_prose}
    expected_local_surfaces = {source_by_event[event]["surface"] for event in expected_target_local}
    check("target_prose_surface_count", len(expected_prose_surfaces) == 145, len(expected_prose_surfaces))
    check("target_local_surface_count", len(expected_local_surfaces) == 14, len(expected_local_surfaces))
    check("target_role_surfaces_disjoint", not (expected_prose_surfaces & expected_local_surfaces), sorted(expected_prose_surfaces & expected_local_surfaces))
    check(
        "target_role_surfaces_complete",
        expected_prose_surfaces | expected_local_surfaces == set(final_by_surface),
        len(expected_prose_surfaces | expected_local_surfaces),
    )

    prose_recipe_ok = 0
    for row in prose:
        source = source_by_event[row["event_id"]]
        expected = (
            final_by_surface[row["surface"]]["final_working_recipe"]
            if row["surface"] in final_by_surface
            else source["gdt516_context_recipe"]
        )
        prose_recipe_ok += row["final_context_recipe"] == expected
    check("prose_recipe_replay", prose_recipe_ok == 546, prose_recipe_ok)
    check(
        "local_recipes_byte_preserved",
        all(row["local_recipe"] == source_by_event[row["event_id"]]["gdt516_context_recipe"] for row in local),
        len(local),
    )
    changed = {row["surface"] for row in prose if row["recipe_changed_after_gdt516"] == "YES"}
    check("changed_surface_inventory", changed == CHANGED_SURFACES, sorted(changed))
    check(
        "changed_event_count",
        sum(row["recipe_changed_after_gdt516"] == "YES" for row in prose) == 8,
        sum(row["recipe_changed_after_gdt516"] == "YES" for row in prose),
    )
    check(
        "target_local_recipe_match",
        all(row["gdt538_recipe_match"] == "YES" for row in local if row["gdt538_surface_member"] == "YES"),
        len(actual_target_local),
    )

    controlled_replays = 0
    for row in prose:
        atoms = row["final_context_recipe"].split("+")
        expected = " → ".join(controlled[atom] for atom in atoms) + "."
        controlled_replays += expected == row["controlled_order_reading_de"]
    for row in local:
        atoms = row["local_recipe"].split("+")
        expected = " → ".join(controlled[atom] for atom in atoms) + "."
        controlled_replays += expected == row["controlled_order_reading_de"]
    check("controlled_chain_replay", controlled_replays == 597, controlled_replays)
    check(
        "prose_exact_roundtrip",
        all(row["exact_recipe_roundtrip"] == row["final_context_recipe"] for row in prose),
        len(prose),
    )
    check(
        "local_exact_roundtrip",
        all(row["exact_recipe_roundtrip"] == row["local_recipe"] for row in local),
        len(local),
    )
    check(
        "all_contextual_phrases_present",
        all(row["contextual_clause_de"] and row["contextual_clause_de"].endswith(".") for row in prose),
        len(prose),
    )
    check(
        "all_local_phrases_present",
        all(row["local_working_phrase_de"] for row in local),
        len(local),
    )
    check(
        "local_never_uses_prose_phrase",
        all(row["gdt538_prose_phrase_applied"] == "NO" for row in local),
        len(local),
    )

    source_statement_by_id = {row["statement_id"]: row for row in source_statements}
    statement_by_id = {row["statement_id"]: row for row in statements}
    check("statement_key_set", set(statement_by_id) == set(source_statement_by_id), len(statement_by_id))
    statement_event_replay = 0
    statement_surface_replay = 0
    for statement_id, row in statement_by_id.items():
        source = source_statement_by_id[statement_id]
        ids = row["event_ids"].split("|")
        statement_event_replay += len(ids) == int(source["event_count"]) == int(row["event_count"])
        statement_surface_replay += row["surface_sequence"] == source["surface_sequence"]
    check("statement_event_replay", statement_event_replay == 78, statement_event_replay)
    check("statement_surface_replay", statement_surface_replay == 78, statement_surface_replay)
    check(
        "statement_backprojection_flags",
        all(row["all_events_backprojected"] == "YES" for row in statements),
        len(statements),
    )
    check(
        "statement_readings_present",
        all(row["contextual_working_reading_de"] for row in statements),
        len(statements),
    )
    touched = sum(int(row["target_event_count"]) > 0 for row in statements)
    check("target_touched_statement_count", touched == 49, touched)

    ordinal_by_event = {row["event_id"]: int(row["card_ordinal_in_statement"]) for row in prose}
    statement_by_event = {row["event_id"]: row["statement_id"] for row in prose}
    inherited_action_rows = [row for row in prose if row["inherited_action_root"] != "NONE"]
    inherited_argument_rows = [row for row in prose if row["inherited_argument_root"] != "NONE"]
    check("inherited_action_count", len(inherited_action_rows) == 143, len(inherited_action_rows))
    check("inherited_argument_count", len(inherited_argument_rows) == 189, len(inherited_argument_rows))
    check(
        "action_sources_same_statement_and_left",
        all(
            statement_by_event[row["inherited_action_source_event_id"]] == row["statement_id"]
            and ordinal_by_event[row["inherited_action_source_event_id"]] < int(row["card_ordinal_in_statement"])
            for row in inherited_action_rows
        ),
        len(inherited_action_rows),
    )
    check(
        "argument_sources_same_statement_and_left",
        all(
            statement_by_event[row["inherited_argument_source_event_id"]] == row["statement_id"]
            and ordinal_by_event[row["inherited_argument_source_event_id"]] < int(row["card_ordinal_in_statement"])
            for row in inherited_argument_rows
        ),
        len(inherited_argument_rows),
    )
    check(
        "same_statement_only_flags",
        all(row["same_statement_inheritance_only"] == "YES" and row["cross_statement_inheritance"] == "NO" for row in prose),
        len(prose),
    )
    actionless = [
        row for row in prose
        if row["explicit_action_roots"] == "NONE" and row["inherited_action_root"] == "NONE"
    ]
    check("standalone_fragment_count", len(actionless) == 16, len(actionless))
    check(
        "standalone_fragment_statement_start_count",
        sum(row["card_ordinal_in_statement"] == "1" for row in actionless) == 14,
        sum(row["card_ordinal_in_statement"] == "1" for row in actionless),
    )
    check(
        "all_target_prose_has_action_context",
        all(
            prose_by_event[event]["explicit_action_roots"] != "NONE"
            or prose_by_event[event]["inherited_action_root"] != "NONE"
            for event in actual_target_prose
        ),
        len(actual_target_prose),
    )
    check(
        "ellipsis_summary_total",
        sum(int(row["event_count"]) for row in ellipsis) == 546,
        sum(int(row["event_count"]) for row in ellipsis),
    )
    expected_ellipsis = Counter(row["ellipsis_status"] for row in prose)
    check(
        "ellipsis_summary_replay",
        expected_ellipsis == Counter({row["ellipsis_status"]: int(row["event_count"]) for row in ellipsis}),
        dict(expected_ellipsis),
    )

    check(
        "role_scope_inventory",
        Counter(row["observed_domain"] for row in roles)
        == Counter({"PROSE_STREAM": 145, "LOCAL_RECORD": 14}),
        dict(Counter(row["observed_domain"] for row in roles)),
    )
    check(
        "role_scope_corrections",
        sum(row["scope_changed_from_gdt538"] == "YES" for row in roles) == 14,
        sum(row["scope_changed_from_gdt538"] == "YES" for row in roles),
    )
    check(
        "no_role_collisions",
        all(row["role_collision_count"] == "0" for row in roles),
        len(roles),
    )
    check(
        "local_default_key_set",
        set(local_default_by_surface) == expected_local_surfaces,
        sorted(local_default_by_surface),
    )
    check(
        "local_default_scopes",
        all(row["lock_scope"] == "LOCAL_RECORD_ONLY" for row in local_defaults),
        len(local_defaults),
    )

    check(
        "page_event_totals",
        sum(int(row["prose_event_count"]) for row in pages) == 546
        and sum(int(row["local_event_count"]) for row in pages) == 51,
        {"prose": sum(int(row["prose_event_count"]) for row in pages), "local": sum(int(row["local_event_count"]) for row in pages)},
    )
    check(
        "page_statement_total",
        sum(int(row["statement_count"]) for row in pages) == 78,
        sum(int(row["statement_count"]) for row in pages),
    )

    reader = import_reader()
    auto = [reader.exact_role_lookup(surface, "AUTO", roles, local_defaults) for surface in role_by_surface]
    check("reader_auto_coverage", all(item is not None for item in auto), len(auto))
    check(
        "reader_auto_role_counts",
        Counter(item["observed_domain"] for item in auto)
        == Counter({"PROSE_STREAM": 145, "LOCAL_RECORD": 14}),
        dict(Counter(item["observed_domain"] for item in auto)),
    )
    check(
        "reader_matched_domain_coverage",
        all(
            reader.exact_role_lookup(
                row["surface"], row["observed_domain"], roles, local_defaults
            ) is not None
            for row in roles
        ),
        len(roles),
    )
    check(
        "reader_mismatched_domain_stops",
        all(
            reader.exact_role_lookup(
                row["surface"],
                "LOCAL_RECORD" if row["observed_domain"] == "PROSE_STREAM" else "PROSE_STREAM",
                roles,
                local_defaults,
            ) is None
            for row in roles
        ),
        len(roles),
    )

    cli_cases = [
        ("aiicthy", "PROSE_STREAM", "GDT539_ROLE_CORRECT_PROSE_SURFACE_LOCK"),
        ("c", "LOCAL_RECORD", "GDT539_ROLE_CORRECT_LOCAL_SURFACE_LOCK"),
        ("c", "PROSE_STREAM", "DELEGATED_BELOW_GDT539_ROLE_SCOPE"),
        ("aiicthy", "LOCAL_RECORD", "DELEGATED_BELOW_GDT539_ROLE_SCOPE"),
        ("aiin", "PROSE_STREAM", "DELEGATED_BELOW_GDT539_ROLE_SCOPE"),
    ]
    cli_results: list[dict] = []
    for surface, domain, expected_status in cli_cases:
        completed = subprocess.run(
            [sys.executable, str(CLI), "--surface", surface, "--domain", domain, "--page", "f66r"],
            cwd=ROOT, check=False, capture_output=True, text=True,
        )
        payload = json.loads(completed.stdout)
        payload["_returncode"] = completed.returncode
        payload["_expected_status"] = expected_status
        cli_results.append(payload)
    check(
        "cli_role_and_delegation_cases",
        all(item["_returncode"] == 0 and item["status"] == item["_expected_status"] for item in cli_results),
        [{"surface": item["surface"], "status": item["status"], "expected": item["_expected_status"]} for item in cli_results],
    )
    c_prose = cli_results[2]
    check(
        "local_to_prose_mismatch_bypasses_gdt538",
        c_prose["delegated_reader"] == "GDT517"
        and c_prose["base_intake"]["surface"] == "c",
        c_prose["delegated_reader"],
    )

    artifact_paths = [PROSE, STATEMENTS, LOCAL, ROLES, LOCAL_DEFAULTS, ELLIPSIS, PAGES, BOOK, RESULT]
    before = {path.name: digest(path) for path in artifact_paths}
    rerun = subprocess.run(
        [sys.executable, str(RUN)], cwd=ROOT, check=False, capture_output=True, text=True
    )
    after = {path.name: digest(path) for path in artifact_paths}
    check("generator_rerun_exit", rerun.returncode == 0, rerun.stderr or rerun.stdout)
    check("generator_byte_determinism", before == after, after)

    check(
        "result_status",
        result["status"] == "PASS_78_STATEMENTS_COMPLETE__145_PROSE_AND_14_LOCAL_SURFACES_SEPARATED",
        result["status"],
    )
    for key, expected in {
        "statement_count": 78,
        "prose_event_count": 546,
        "local_event_count": 51,
        "complete_event_count": 597,
        "target_surface_count": 159,
        "target_prose_surface_count": 145,
        "target_local_surface_count": 14,
        "target_prose_event_count": 149,
        "target_local_event_count": 19,
        "target_touched_statement_count": 49,
        "scope_correction_surface_count": 14,
        "final_recipe_change_event_count": 8,
        "inherited_action_event_count": 143,
        "inherited_argument_event_count": 189,
        "exact_event_backprojection_count": 546,
        "exact_local_backprojection_count": 51,
        "role_collision_count": 0,
        "cross_statement_inheritance_count": 0,
        "new_pages": 0,
        "root_meaning_changes": 0,
        "new_recipes": 0,
    }.items():
        check("result_" + key, result[key] == expected, result[key])

    failed = [row for row in checks if not row["passed"]]
    validation = {
        "status": "PASS" if not failed else "FAIL",
        "check_count": len(checks),
        "passed_count": len(checks) - len(failed),
        "failed_count": len(failed),
        "checks": checks,
    }
    VALIDATION.write_text(
        json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(validation, ensure_ascii=False, indent=2))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
