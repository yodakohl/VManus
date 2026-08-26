#!/usr/bin/env python3
"""Validate GDT399 inventories, attachment geometry, and deterministic build."""

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
HERE = Path(__file__).resolve().parents[1]
OUT = HERE / "artifacts"
RUN = HERE / "src/run.py"
P1026 = ROOT / "experiments/yolo/sidequest_semantic_visible_allograph_resegmentation_one_thousand_twenty_sixth/PASS1026_3888_CORRECTED_EVENT_LEDGER.tsv"
P1018 = ROOT / "experiments/yolo/sidequest_semantic_cross_register_core_revision_one_thousand_eighteenth/PASS1018_627_REVISED_CORE_EDITION.tsv"
P1009 = ROOT / "experiments/yolo/sidequest_semantic_twenty_two_page_statement_consolidation_one_thousand_ninth/PASS1009_4581_EVENT_LEDGER.tsv"
ATTACHMENTS = OUT / "gdt399_4374_scope_attachments.tsv"
STATEMENTS = OUT / "gdt399_627_statement_scope_edition.tsv"
EVENTS = OUT / "gdt399_3888_event_replay.tsv"
PAGES = OUT / "gdt399_22_page_replay.tsv"
REGISTERS = OUT / "gdt399_four_register_replay.tsv"
RULES = OUT / "gdt399_rule_support.tsv"
CHANGES = OUT / "gdt399_96_statement_change_audit.tsv"
RESULT = OUT / "gdt399_result.json"
VALIDATION = OUT / "gdt399_validation.json"
FOCI = {
    "AIIN": "WERT", "AIN": "ANTEIL", "OR": "EINHEIT", "Y": "AKTIVER POSTEN",
    "E": "GRAD I", "EE": "GRAD II", "EEE": "GRAD III", "AL": "ZIELORT",
    "AR": "AUSGANG", "L": "VERBINDUNG", "AIR": "LAUF",
}
ACTIONS = {"OK", "CH", "SH", "K", "S", "T", "CHD", "R", "P"}
RULE_FAMILIES = {
    "AL_AR_ORDERED_FALLBACK", "INHERITED_ACTION_STACK", "L_AIR_RIGHT_FALLBACK",
    "NEAREST_HEAD_LEFT_TIE", "ONE_CARD_FORWARD", "OWNER_CONTEXT",
    "PREVIOUS_CARD_STACK", "Q_OT_PACKAGE_FORWARD", "R_POSITIONAL_MARKING",
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    attachments = read_tsv(ATTACHMENTS)
    statements = read_tsv(STATEMENTS)
    events = read_tsv(EVENTS)
    pages = read_tsv(PAGES)
    registers = read_tsv(REGISTERS)
    rules = read_tsv(RULES)
    changes = read_tsv(CHANGES)
    source_events = read_tsv(P1026)
    source_statements = read_tsv(P1018)
    source_full = read_tsv(P1009)
    result = json.loads(RESULT.read_text(encoding="utf-8"))

    checks: dict[str, dict[str, object]] = {}

    def check(name: str, condition: bool, observed: object) -> None:
        checks[name] = {"pass": bool(condition), "observed": observed}

    check("attachment_count", len(attachments) == 4374, len(attachments))
    check("statement_count", len(statements) == 627, len(statements))
    check("event_count", len(events) == 3888, len(events))
    check("page_count", len(pages) == 22, len(pages))
    check("register_count", len(registers) == 4, len(registers))
    check("rule_family_count", len(rules) == 9, len(rules))
    check("change_statement_count", len(changes) == 96, len(changes))
    check("unique_attachment_ids", len({row["attachment_id"] for row in attachments}) == 4374, len({row["attachment_id"] for row in attachments}))
    check("unique_focus_keys", len({row["focus_key"] for row in attachments}) == 4374, len({row["focus_key"] for row in attachments}))
    check("unique_event_ids", len({row["event_id"] for row in events}) == 3888, len({row["event_id"] for row in events}))

    source_event_by_id = {row["source_event_id"]: row for row in source_events}
    replay_by_id = {row["event_id"]: row for row in events}
    event_alignment = all(
        row["event_id"] in source_event_by_id
        and row["surface"] == source_event_by_id[row["event_id"]]["surface"]
        and row["component_recipe"] == source_event_by_id[row["event_id"]]["pass1026_recipe"]
        for row in events
    )
    check("pass1026_event_alignment", event_alignment, sum(
        row["event_id"] in source_event_by_id
        and row["surface"] == source_event_by_id[row["event_id"]]["surface"]
        and row["component_recipe"] == source_event_by_id[row["event_id"]]["pass1026_recipe"]
        for row in events
    ))

    expected_focus: list[tuple[str, str, int]] = []
    for event in source_events:
        seen: Counter[str] = Counter()
        for atom in event["pass1026_recipe"].split("+"):
            if atom in FOCI:
                seen[atom] += 1
                expected_focus.append((event["source_event_id"], atom, seen[atom]))
    actual_focus = [
        (row["event_id"], row["focus_core"], int(row["focus_occurrence_ordinal"]))
        for row in attachments
    ]
    check("every_focus_atom_once", actual_focus == expected_focus, f"{len(actual_focus)}/{len(expected_focus)}")
    check("fixed_focus_values", all(FOCI[row["focus_core"]] == row["focus_value_de"] for row in attachments), len(attachments))
    check("all_scope_resolved", all(row["resolution_status"] == "COMPLETE_SELECTED_SCOPE" for row in attachments), Counter(row["resolution_status"] for row in attachments))
    check("lookahead_at_most_one", all(row["bounded_lookahead_cards"] in {"0", "1"} for row in attachments), Counter(row["bounded_lookahead_cards"] for row in attachments))
    check("no_owner_boundary_crossing", all(row["owner_boundary_crossed"] == "NO" for row in attachments), Counter(row["owner_boundary_crossed"] for row in attachments))

    statement_event_order: dict[str, list[str]] = defaultdict(list)
    for event in source_events:
        statement_event_order[event["statement_id"]].append(event["source_event_id"])
    source_position = {
        event_id: (statement_id, index)
        for statement_id, event_ids in statement_event_order.items()
        for index, event_id in enumerate(event_ids, start=1)
    }
    target_geometry_ok = True
    target_atom_ok = True
    for row in attachments:
        kind = row["chosen_attachment_class"]
        if kind == "OWNER_ONLY":
            target_geometry_ok &= row["chosen_action_event_id"] == "OWNER"
            continue
        target_id = row["chosen_action_event_id"]
        if target_id not in source_position:
            target_geometry_ok = False
            target_atom_ok = False
            continue
        source_statement, source_card = source_position[row["event_id"]]
        target_statement, target_card = source_position[target_id]
        target_geometry_ok &= source_statement == target_statement
        if kind in {"SAME_CARD_LEFT_ACTION", "SAME_CARD_RIGHT_ACTION"}:
            target_geometry_ok &= target_card == source_card
        elif kind == "PREVIOUS_CARD_ACTION":
            target_geometry_ok &= target_card == source_card - 1
        elif kind == "INHERITED_ACTION":
            target_geometry_ok &= target_card < source_card - 1
        elif kind == "BOUNDED_NEXT_CARD_ACTION":
            target_geometry_ok &= target_card == source_card + 1
        target_atoms = source_event_by_id[target_id]["pass1026_recipe"].split("+")
        atom_index = int(row["chosen_action_atom_ordinal"])
        target_atom_ok &= 1 <= atom_index <= len(target_atoms) and target_atoms[atom_index - 1] == row["chosen_action"] and row["chosen_action"] in ACTIONS
    check("attachment_target_geometry", target_geometry_ok, "same statement; 0/previous/inherited/+1 as labelled")
    check("attachment_target_action_atom", target_atom_ok, "all non-owner governors visibly present")

    recipes_by_surface: dict[str, set[str]] = defaultdict(set)
    for row in events:
        recipes_by_surface[row["surface"]].add(row["component_recipe"])
    conflicts = {surface: recipes for surface, recipes in recipes_by_surface.items() if len(recipes) > 1}
    check("one_surface_one_recipe", not conflicts, len(conflicts))
    check("changed_event_count", sum(row["pass1026_change"] != "UNCHANGED" for row in events) == 239, sum(row["pass1026_change"] != "UNCHANGED" for row in events))
    changed_statements = {row["statement_id"] for row in events if row["pass1026_change"] != "UNCHANGED"}
    check("changed_statement_identity", changed_statements == {row["statement_id"] for row in changes}, len(changed_statements))

    source_statement_by_id = {row["statement_id"]: row for row in source_statements}
    statement_alignment = all(
        row["statement_id"] in source_statement_by_id
        and row["event_count"] == source_statement_by_id[row["statement_id"]]["event_count"]
        and row["surface_sequence"] == source_statement_by_id[row["statement_id"]]["surface_sequence"]
        and row["scope_result"] == "COMPLETE_SELECTED_SCOPE__NO_OPEN_ATTACHMENTS"
        for row in statements
    )
    check("statement_alignment_and_completion", statement_alignment, sum(
        row["statement_id"] in source_statement_by_id and row["scope_result"] == "COMPLETE_SELECTED_SCOPE__NO_OPEN_ATTACHMENTS"
        for row in statements
    ))

    check("page_partition_4581", sum(int(row["visible_group_count"]) for row in pages) == 4581, sum(int(row["visible_group_count"]) for row in pages))
    check("page_partition_3888_running", sum(int(row["running_event_count"]) for row in pages) == 3888, sum(int(row["running_event_count"]) for row in pages))
    check("page_partition_693_local", sum(int(row["local_group_count"]) for row in pages) == 693, sum(int(row["local_group_count"]) for row in pages))
    check("page_partition_4374_focus", sum(int(row["focus_attachment_count"]) for row in pages) == 4374, sum(int(row["focus_attachment_count"]) for row in pages))
    check("all_running_pages_holdout", all(row["page_replay_result"] in {"PASS_FIXED_SCOPE_RULES", "LOCAL_ADDRESS_COPY_ONLY"} for row in pages), Counter(row["page_replay_result"] for row in pages))
    check("all_registers_holdout", all(row["register_replay_result"] == "PASS_FIXED_SCOPE" for row in registers), Counter(row["register_replay_result"] for row in registers))
    check("all_nine_rule_families", {row["rule_family"] for row in rules} == RULE_FAMILIES, sorted(row["rule_family"] for row in rules))
    check("all_rules_cross_page", all(row["survives_every_page_where_used"] == "YES" for row in rules), Counter(row["survives_every_page_where_used"] for row in rules))
    check("all_rules_cross_register", all(row["survives_every_register_where_used"] == "YES" for row in rules), Counter(row["survives_every_register_where_used"] for row in rules))
    check("focus_delta_32", int(result["focus_attachment_delta"]) == 32, result["focus_attachment_delta"])
    check("sealed_pages_absent", not any(row["physical_page"].startswith("f84") for row in events), sorted({row["physical_page"] for row in events if row["physical_page"].startswith("f84")}))

    result_hashes_ok = all(
        sha256(OUT / name) == digest for name, digest in result["output_hashes"].items()
    )
    check("result_output_hashes", result_hashes_ok, len(result["output_hashes"]))
    before = {path.name: sha256(path) for path in [ATTACHMENTS, STATEMENTS, EVENTS, PAGES, REGISTERS, RULES, CHANGES, RESULT, HERE / "REPORT.md"]}
    completed = subprocess.run([sys.executable, str(RUN)], cwd=ROOT, text=True, capture_output=True, check=False)
    after = {path.name: sha256(path) for path in [ATTACHMENTS, STATEMENTS, EVENTS, PAGES, REGISTERS, RULES, CHANGES, RESULT, HERE / "REPORT.md"]}
    check("deterministic_rebuild", completed.returncode == 0 and before == after, {"returncode": completed.returncode, "hashes_equal": before == after})

    failures = [name for name, value in checks.items() if not value["pass"]]
    payload = {
        "status": "PASS" if not failures else "FAIL",
        "check_count": len(checks),
        "failed_checks": failures,
        "checks": checks,
        "validated_output_hashes": after,
    }
    VALIDATION.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
