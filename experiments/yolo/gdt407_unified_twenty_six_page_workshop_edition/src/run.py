#!/usr/bin/env python3
"""Build one normalized 26-page edition from the current selected layers."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
HERE = Path(__file__).resolve().parent.parent
OUT = HERE / "artifacts"

OLD_EVENTS = ROOT / "experiments/yolo/gdt399_creative_scope_rebuild_after_visible_resegmentation/artifacts/gdt399_3888_event_replay.tsv"
OLD_STATEMENTS = ROOT / "experiments/yolo/gdt399_creative_scope_rebuild_after_visible_resegmentation/artifacts/gdt399_627_statement_scope_edition.tsv"
OLD_ATTACHMENTS = ROOT / "experiments/yolo/gdt402_factorized_scope_selector_head_license/artifacts/gdt402_4374_factorized_replay.tsv"
OLD_ATTACHMENT_DETAIL = ROOT / "experiments/yolo/gdt399_creative_scope_rebuild_after_visible_resegmentation/artifacts/gdt399_4374_scope_attachments.tsv"
OLD_ALL_GROUPS = ROOT / "experiments/yolo/sidequest_semantic_twenty_two_page_statement_consolidation_one_thousand_ninth/PASS1009_4581_EVENT_LEDGER.tsv"
NEW_EVENTS = ROOT / "experiments/yolo/gdt404_random_four_page_factorized_admission/artifacts/gdt404_688_event_first_pass.tsv"
NEW_STATEMENTS = ROOT / "experiments/yolo/gdt404_random_four_page_factorized_admission/artifacts/gdt404_statement_edition.tsv"
NEW_ATTACHMENTS = ROOT / "experiments/yolo/gdt404_random_four_page_factorized_admission/artifacts/gdt404_factorized_attachments.tsv"
ATOM_DICT = ROOT / "experiments/yolo/gdt405_second_random_batch_recipe_lock/artifacts/gdt405_46_locked_atom_dictionary.tsv"

EXPECTED_PAGES = {
    "f1r", "f10r", "f11r", "f13r", "f17r", "f18r", "f24v", "f55v", "f56r",
    "f67r2", "f68r1", "f69v", "f70v", "f71v", "f72r", "f75r", "f76r",
    "f77r", "f81r", "f81v", "f82r", "f83r", "f88r", "f88v", "f89r", "f95v",
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def folio_key(page: str) -> tuple[int, int, int, str]:
    match = re.fullmatch(r"f(\d+)([rv])(\d*)", page)
    if not match:
        return (9999, 9, 9, page)
    number, side, panel = match.groups()
    return (int(number), 0 if side == "r" else 1, int(panel or 0), page)


def event_number(identifier: str) -> int:
    match = re.search(r"(\d+)$", identifier)
    return int(match.group(1)) if match else 0


def literal(recipe: str, atom_values: dict[str, str]) -> str:
    return " · ".join(atom_values[token] for token in recipe.split("+") if token)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    old_events = read_tsv(OLD_EVENTS)
    old_statements = read_tsv(OLD_STATEMENTS)
    old_factors = read_tsv(OLD_ATTACHMENTS)
    old_attachment_detail = read_tsv(OLD_ATTACHMENT_DETAIL)
    old_all_groups = read_tsv(OLD_ALL_GROUPS)
    new_events = read_tsv(NEW_EVENTS)
    new_statements = read_tsv(NEW_STATEMENTS)
    new_factors = read_tsv(NEW_ATTACHMENTS)
    atom_rows = read_tsv(ATOM_DICT)
    atom_values = {row["atom"]: row["locked_working_value_de"] for row in atom_rows}

    assert (len(old_events), len(old_statements), len(old_factors), len(old_attachment_detail)) == (3888, 627, 4374, 4374)
    assert (len(new_events), len(new_statements), len(new_factors)) == (688, 88, 677)
    assert len(old_all_groups) == 4581
    assert len(atom_values) == 46

    old_source_by_event = {row["event_id"]: row for row in old_all_groups}
    old_statement_by_id = {row["statement_id"]: row for row in old_statements}
    old_detail_by_id = {row["attachment_id"]: row for row in old_attachment_detail}

    normalized_running: list[dict[str, object]] = []
    for row in old_events:
        source = old_source_by_event[row["event_id"]]
        statement = old_statement_by_id[row["statement_id"]]
        normalized_running.append({
            "source_layer": "ORIGINAL22_RUNNING", "source_event_id": row["event_id"],
            "source_replay_event_id": row["replay_event_id"],
            "physical_page": row["physical_page"], "source_panel": source["source_panel"],
            "register": row["register"], "locus": row["locus"],
            "source_order": int(source["book_event_ordinal"]), "source_statement_id": row["statement_id"],
            "owner_de": statement["owner_de"], "surface": row["surface"],
            "component_recipe": row["component_recipe"],
            "literal_core_reading_de": literal(row["component_recipe"], atom_values),
            "surface_status": "PASS1026_SELECTED_RECIPE", "admission_color": "GREEN_SELECTED_BASE",
            "source_local_role": "NONE",
        })
    for row in new_events:
        normalized_running.append({
            "source_layer": "GDT404_RANDOM4_RUNNING", "source_event_id": row["event_id"],
            "source_replay_event_id": row["event_id"],
            "physical_page": row["physical_page"], "source_panel": row["source_page_value"],
            "register": row["register"], "locus": row["locus"],
            "source_order": event_number(row["event_id"]), "source_statement_id": row["statement_id"],
            "owner_de": row["owner_id"], "surface": row["surface"],
            "component_recipe": row["visible_recipe"],
            "literal_core_reading_de": row["literal_core_reading_de"],
            "surface_status": row["surface_status"], "admission_color": row["admission_color"],
            "source_local_role": "NONE",
        })

    local_groups: list[dict[str, object]] = []
    for row in old_all_groups:
        if not row["event_role"].startswith("LOCAL_ADDRESS_OR_"):
            continue
        local_groups.append({
            "source_layer": "ORIGINAL22_LOCAL_ADDRESS", "source_event_id": row["event_id"],
            "source_replay_event_id": row["event_id"], "physical_page": row["physical_page"],
            "source_panel": row["source_panel"], "register": row["register"], "locus": row["locus"],
            "source_order": int(row["book_event_ordinal"]), "source_statement_id": "NONE",
            "owner_de": row["local_contextual_expansion_de"].split(":", 1)[0],
            "surface": row["surface"], "component_recipe": row["component_recipe"],
            "literal_core_reading_de": "LOKALE ADRESSE KOPIEREN",
            "source_local_role": row["event_role"],
            "surface_status": "LOCAL_ADDRESS_OR_LABEL__NO_PROSE_PARSE",
            "admission_color": "LOCAL_ONLY",
            "local_contextual_expansion_de": row["local_contextual_expansion_de"],
        })
    assert len(normalized_running) == 4576
    assert len(local_groups) == 693

    normalized_running.sort(key=lambda row: (folio_key(str(row["physical_page"])), int(row["source_order"])))
    running_id_by_source: dict[str, str] = {}
    for ordinal, row in enumerate(normalized_running, start=1):
        row["global_running_ordinal"] = ordinal
        row["global_running_event_id"] = f"G407-E{ordinal:04d}"
        running_id_by_source[str(row["source_event_id"])] = str(row["global_running_event_id"])

    all_groups = [dict(row, group_kind="RUNNING_EVENT") for row in normalized_running]
    all_groups.extend(dict(row, group_kind="LOCAL_ADDRESS_OR_LABEL") for row in local_groups)
    all_groups.sort(key=lambda row: (
        folio_key(str(row["physical_page"])), int(row["source_order"]),
        0 if row["group_kind"] == "RUNNING_EVENT" else 1,
    ))
    for ordinal, row in enumerate(all_groups, start=1):
        row["global_group_ordinal"] = ordinal
        row["global_group_id"] = f"G407-G{ordinal:04d}"
    group_ordinal_by_source = {str(row["source_event_id"]): int(row["global_group_ordinal"]) for row in all_groups}

    statement_rows: list[dict[str, object]] = []
    for row in old_statements:
        event_ids = [event["source_event_id"] for event in normalized_running if event["source_statement_id"] == row["statement_id"]]
        statement_rows.append({
            "source_layer": "ORIGINAL22_RUNNING", "source_statement_id": row["statement_id"],
            "physical_page": row["physical_page"], "register": row["register"], "owner_de": row["owner_de"],
            "event_count": int(row["event_count"]), "first_global_group_ordinal": min(group_ordinal_by_source[str(e)] for e in event_ids),
            "last_global_group_ordinal": max(group_ordinal_by_source[str(e)] for e in event_ids),
            "surface_sequence": row["surface_sequence"], "recipe_sequence": row["corrected_recipe_sequence"],
            "literal_core_sequence_de": " | ".join(literal(recipe.strip(), atom_values) for recipe in row["corrected_recipe_sequence"].split(" | ")),
            "action_chain_de": row["action_chain_de"], "argument_inventory_de": row["arguments_de"],
            "relation_inventory_de": row["relations_de"], "grade_inventory_de": row["grades_de"],
            "end_mode": row["end_mode"], "focus_attachment_count": int(row["focus_attachment_count"]),
            "bounded_forward_count": int(row["bounded_forward_count"]), "owner_only_count": int(row["owner_only_count"]),
            "selector_inventory": row["rule_families"], "head_inventory": "DERIVED_IN_GDT402",
            "scope_skeleton_de": row["scope_skeleton_de"], "edition_result": row["scope_result"],
        })
    for row in new_statements:
        event_ids = [event["source_event_id"] for event in normalized_running if event["source_statement_id"] == row["statement_id"]]
        statement_rows.append({
            "source_layer": "GDT404_RANDOM4_RUNNING", "source_statement_id": row["statement_id"],
            "physical_page": row["physical_page"], "register": row["register"], "owner_de": row["owner_id"],
            "event_count": int(row["event_count"]), "first_global_group_ordinal": min(group_ordinal_by_source[str(e)] for e in event_ids),
            "last_global_group_ordinal": max(group_ordinal_by_source[str(e)] for e in event_ids),
            "surface_sequence": row["surface_sequence"], "recipe_sequence": row["recipe_sequence"],
            "literal_core_sequence_de": row["literal_core_sequence_de"], "action_chain_de": row["action_chain_de"],
            "argument_inventory_de": row["argument_inventory_de"], "relation_inventory_de": row["relation_inventory_de"],
            "grade_inventory_de": row["grade_inventory_de"], "end_mode": row["end_mode"],
            "focus_attachment_count": int(row["focus_attachment_count"]),
            "bounded_forward_count": int(row["bounded_forward_count"]), "owner_only_count": int(row["owner_only_count"]),
            "selector_inventory": row["selector_inventory"], "head_inventory": row["head_inventory"],
            "scope_skeleton_de": row["scope_skeleton_de"], "edition_result": row["factorized_result"],
        })
    statement_rows.sort(key=lambda row: (int(row["first_global_group_ordinal"]), str(row["source_statement_id"])))
    statement_id_map: dict[str, str] = {}
    for ordinal, row in enumerate(statement_rows, start=1):
        row["global_statement_ordinal"] = ordinal
        row["global_statement_id"] = f"G407-S{ordinal:03d}"
        statement_id_map[str(row["source_statement_id"])] = str(row["global_statement_id"])
    assert len(statement_rows) == 715

    events_by_statement: dict[str, list[dict[str, object]]] = defaultdict(list)
    for event in normalized_running:
        events_by_statement[str(event["source_statement_id"])].append(event)
    action_source_by_card: dict[tuple[str, int], str] = {}
    for statement_id, events in events_by_statement.items():
        events.sort(key=lambda event: int(event["source_order"]))
        for card_ordinal, event in enumerate(events, start=1):
            action_source_by_card[(statement_id, card_ordinal)] = str(event["source_event_id"])

    def resolve_action(statement_id: str, card_ordinal: str) -> tuple[str, str]:
        ordinal = int(card_ordinal)
        if ordinal == 0:
            return "OWNER", f"OWNER::{statement_id_map[statement_id]}"
        source_id = action_source_by_card[(statement_id, ordinal)]
        return source_id, running_id_by_source[source_id]

    attachment_rows: list[dict[str, object]] = []
    for row in old_factors:
        detail = old_detail_by_id[row["attachment_id"]]
        resolved_action_source, resolved_action_global = resolve_action(
            row["statement_id"], detail["chosen_action_card_ordinal"]
        )
        attachment_rows.append({
            "source_layer": "ORIGINAL22_GDT402", "source_factorized_id": row["factorized_id"],
            "source_attachment_id": row["attachment_id"], "physical_page": row["physical_page"],
            "register": row["register"], "source_statement_id": row["statement_id"],
            "global_statement_id": statement_id_map[row["statement_id"]],
            "source_event_id": row["event_id"], "global_running_event_id": running_id_by_source[row["event_id"]],
            "surface": row["surface"], "focus_core": row["focus_core"],
            "focus_value_de": atom_values[row["focus_core"]], "focus_family": row["focus_family"],
            "focus_atom_ordinal": detail["focus_atom_ordinal"], "selector_rule": row["selector_rule"],
            "attachment_geometry": row["attachment_geometry"],
            "selected_action_source_event_id": row["selected_action_event_id"],
            "resolved_action_source_event_id": resolved_action_source,
            "selected_action_global_event_id": resolved_action_global,
            "selected_action_atom_ordinal": row["selected_action_atom_ordinal"],
            "action_core": row["action_core"], "action_value_de": atom_values.get(row["action_core"], "BESITZER"),
            "head_kind": row["head_kind"], "r_topology": row["r_topology"],
            "duplicate_mode": row["duplicate_mode"], "duplicate_role": row["duplicate_role"],
            "lookahead_cards": row["lookahead_cards"], "owner_boundary_crossed": row["owner_boundary_crossed"],
            "statement_boundary_crossed": "NO", "factorized_result": row["factorized_result"],
        })
    for row in new_factors:
        resolved_action_source, resolved_action_global = resolve_action(
            row["statement_id"], row["selected_action_card_ordinal"]
        )
        attachment_rows.append({
            "source_layer": "GDT404_FACTORIZED", "source_factorized_id": row["factorized_id"],
            "source_attachment_id": row["factorized_id"], "physical_page": row["physical_page"],
            "register": row["register"], "source_statement_id": row["statement_id"],
            "global_statement_id": statement_id_map[row["statement_id"]],
            "source_event_id": row["event_id"], "global_running_event_id": running_id_by_source[row["event_id"]],
            "surface": row["surface"], "focus_core": row["focus_core"],
            "focus_value_de": row["focus_value_de"], "focus_family": row["focus_family"],
            "focus_atom_ordinal": row["focus_atom_ordinal"], "selector_rule": row["selector_rule"],
            "attachment_geometry": row["attachment_geometry"],
            "selected_action_source_event_id": row["selected_action_event_id"],
            "resolved_action_source_event_id": resolved_action_source,
            "selected_action_global_event_id": resolved_action_global,
            "selected_action_atom_ordinal": row["selected_action_atom_ordinal"],
            "action_core": row["action_core"], "action_value_de": row["action_value_de"],
            "head_kind": row["head_kind"], "r_topology": row["r_topology"],
            "duplicate_mode": row["duplicate_mode"], "duplicate_role": row["duplicate_role"],
            "lookahead_cards": row["lookahead_cards"], "owner_boundary_crossed": row["owner_boundary_crossed"],
            "statement_boundary_crossed": row["statement_boundary_crossed"],
            "factorized_result": row["factorized_result"],
        })
    attachment_rows.sort(key=lambda row: (
        group_ordinal_by_source[str(row["source_event_id"])], int(row["focus_atom_ordinal"]), str(row["source_attachment_id"])
    ))
    for ordinal, row in enumerate(attachment_rows, start=1):
        row["global_attachment_ordinal"] = ordinal
        row["global_attachment_id"] = f"G407-A{ordinal:05d}"
    assert len(attachment_rows) == 5051

    running_fields = [
        "global_running_ordinal", "global_running_event_id", "source_layer", "source_event_id",
        "source_replay_event_id", "physical_page", "source_panel", "register", "locus", "source_order",
        "source_statement_id", "owner_de", "surface", "component_recipe", "literal_core_reading_de",
        "surface_status", "admission_color",
    ]
    local_fields = [
        "source_layer", "source_event_id", "physical_page", "source_panel", "register", "locus",
        "source_order", "owner_de", "surface", "component_recipe", "literal_core_reading_de",
        "local_contextual_expansion_de", "source_local_role", "surface_status", "admission_color",
    ]
    group_fields = [
        "global_group_ordinal", "global_group_id", "group_kind", "source_layer", "source_event_id",
        "physical_page", "source_panel", "register", "locus", "source_order", "source_statement_id",
        "owner_de", "surface", "component_recipe", "literal_core_reading_de", "surface_status", "admission_color",
        "source_local_role",
    ]
    statement_fields = [
        "global_statement_ordinal", "global_statement_id", "source_layer", "source_statement_id", "physical_page",
        "register", "owner_de", "event_count", "first_global_group_ordinal", "last_global_group_ordinal",
        "surface_sequence", "recipe_sequence", "literal_core_sequence_de", "action_chain_de",
        "argument_inventory_de", "relation_inventory_de", "grade_inventory_de", "end_mode",
        "focus_attachment_count", "bounded_forward_count", "owner_only_count", "selector_inventory",
        "head_inventory", "scope_skeleton_de", "edition_result",
    ]
    attachment_fields = [
        "global_attachment_ordinal", "global_attachment_id", "source_layer", "source_factorized_id",
        "source_attachment_id", "physical_page", "register", "source_statement_id", "global_statement_id",
        "source_event_id", "global_running_event_id", "surface", "focus_core", "focus_value_de", "focus_family",
        "focus_atom_ordinal", "selector_rule", "attachment_geometry", "selected_action_source_event_id",
        "resolved_action_source_event_id", "selected_action_global_event_id", "selected_action_atom_ordinal", "action_core", "action_value_de",
        "head_kind", "r_topology", "duplicate_mode", "duplicate_role", "lookahead_cards",
        "owner_boundary_crossed", "statement_boundary_crossed", "factorized_result",
    ]

    running_path = OUT / "gdt407_4576_running_event_edition.tsv"
    local_path = OUT / "gdt407_693_local_group_edition.tsv"
    group_path = OUT / "gdt407_5269_unified_group_ledger.tsv"
    statement_path = OUT / "gdt407_715_statement_edition.tsv"
    attachment_path = OUT / "gdt407_5051_attachment_edition.tsv"
    write_tsv(running_path, normalized_running, running_fields)
    write_tsv(local_path, local_groups, local_fields)
    write_tsv(group_path, all_groups, group_fields)
    write_tsv(statement_path, statement_rows, statement_fields)
    write_tsv(attachment_path, attachment_rows, attachment_fields)

    page_rows: list[dict[str, object]] = []
    for page in sorted(EXPECTED_PAGES, key=folio_key):
        groups = [row for row in all_groups if row["physical_page"] == page]
        statements = [row for row in statement_rows if row["physical_page"] == page]
        attachments = [row for row in attachment_rows if row["physical_page"] == page]
        page_rows.append({
            "page_ordinal": len(page_rows) + 1, "physical_page": page,
            "registers": "|".join(sorted({str(row["register"]) for row in groups})),
            "visible_group_count": len(groups),
            "running_event_count": sum(row["group_kind"] == "RUNNING_EVENT" for row in groups),
            "local_group_count": sum(row["group_kind"] == "LOCAL_ADDRESS_OR_LABEL" for row in groups),
            "statement_count": len(statements), "focus_attachment_count": len(attachments),
            "open_statement_count": sum("OPEN" in str(row["end_mode"]) for row in statements),
            "amber_event_count": sum(row.get("admission_color") == "AMBER" for row in groups),
            "distinct_surface_count": len({str(row["surface"]) for row in groups}),
        })
    page_path = OUT / "gdt407_26_page_summary.tsv"
    write_tsv(page_path, page_rows, list(page_rows[0]))

    readable = [
        "# Gemeinsame 26-Seiten-Werkstattausgabe", "",
        "Dies ist die zusammengeführte Kernlesung der bereits zugelassenen Seiten. Lokale Namen bleiben lokal; keine Zeile ist eine bestätigte Klartextübersetzung.", "",
    ]
    for page_row in page_rows:
        page = str(page_row["physical_page"])
        readable.extend([
            f"## {page}", "",
            f"{page_row['visible_group_count']} sichtbare Gruppen: {page_row['running_event_count']} laufend, {page_row['local_group_count']} lokal; {page_row['statement_count']} Aussagen.", "",
        ])
        for statement in (row for row in statement_rows if row["physical_page"] == page):
            readable.append(
                f"- **{statement['global_statement_id']}** · {statement['owner_de']} · "
                f"{statement['surface_sequence']} → {statement['literal_core_sequence_de']} "
                f"[{statement['end_mode']}]"
            )
        if int(page_row["local_group_count"]):
            readable.append(f"- **Lokales Register:** {page_row['local_group_count']} Bild-/Stationsadressen; vollständig im 693er Ledger.")
        readable.append("")
    readable_path = HERE / "TWENTY_SIX_PAGE_READABLE_CORE_EDITION.md"
    readable_path.write_text("\n".join(readable).rstrip() + "\n", encoding="utf-8")

    result = {
        "status": "UNIFIED_TWENTY_SIX_PAGE_EDITION_COMPLETE",
        "physical_pages": len(page_rows), "visible_groups": len(all_groups),
        "running_events": len(normalized_running), "local_groups": len(local_groups),
        "statements": len(statement_rows), "focus_attachments": len(attachment_rows),
        "old_running_events": len(old_events), "new_running_events": len(new_events),
        "old_statements": len(old_statements), "new_statements": len(new_statements),
        "old_attachments": len(old_factors), "new_attachments": len(new_factors),
        "page_order": [row["physical_page"] for row in page_rows],
        "source_sha256": {str(path.relative_to(ROOT)): sha256(path) for path in (
            OLD_EVENTS, OLD_STATEMENTS, OLD_ATTACHMENTS, OLD_ATTACHMENT_DETAIL, OLD_ALL_GROUPS,
            NEW_EVENTS, NEW_STATEMENTS, NEW_ATTACHMENTS, ATOM_DICT,
        )},
        "output_sha256": {str(path.relative_to(HERE)): sha256(path) for path in (
            running_path, local_path, group_path, statement_path, attachment_path, page_path, readable_path,
        )},
    }
    (OUT / "gdt407_result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
