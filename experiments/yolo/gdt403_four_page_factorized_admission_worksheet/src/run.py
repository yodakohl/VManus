#!/usr/bin/env python3
"""Build the blank four-page intake sheet for the GDT402 parser."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
HERE = Path(__file__).resolve().parents[1]
OUT = HERE / "artifacts"
G402 = ROOT / "experiments/yolo/gdt402_factorized_scope_selector_head_license"
G401 = ROOT / "experiments/yolo/gdt401_amber_forward_r_composition_closure"
AXES = G402 / "artifacts/gdt402_axis_inventory.tsv"
RESULT402 = G402 / "artifacts/gdt402_result.json"
PARSER402 = G402 / "DETERMINISTIC_NEXT_PAGE_PARSER.md"
ERROR_DECK401 = G401 / "artifacts/gdt401_error_deck_v2.tsv"
ERROR_GUIDE401 = G401 / "NEXT_FOUR_PAGE_ERROR_DECK_V2.md"

SELECTORS = {
    "NEAREST_HEAD_LEFT_TIE": "naechsten sichtbaren Kopf waehlen; bei Gleichstand links",
    "AL_AR_ORDERED_FALLBACK": "links, dann aktiver Kopf, dann gleicher Kartenkopf rechts, sonst Besitzer",
    "L_AIR_RIGHT_FALLBACK": "rechts, sonst links, sonst aktiver Kopf oder Besitzer",
    "PREVIOUS_CARD_STACK": "unmittelbar vorigen offenen Handlungskopf verwenden",
    "INHERITED_ACTION_STACK": "im selben Besitzerblock geerbten Handlungskopf verwenden",
    "ONE_CARD_FORWARD": "ersten sichtbaren Kopf genau der naechsten Karte verwenden",
    "Q_OT_PACKAGE_FORWARD": "Q- oder OT-Paket zum ersten Kopf genau der naechsten Karte reichen",
    "OWNER_CONTEXT": "sichtbaren Besitzer verwenden, wenn kein Handlungskopf lizenziert ist",
}

GEOMETRIES = {
    "SAME_CARD_LEFT_ACTION": "Zielkopf links in derselben Karte",
    "SAME_CARD_RIGHT_ACTION": "Zielkopf rechts in derselben Karte",
    "PREVIOUS_CARD_ACTION": "Zielkopf in der unmittelbar vorigen Karte",
    "BOUNDED_NEXT_CARD_ACTION": "Zielkopf in genau der naechsten Karte",
    "INHERITED_ACTION": "Zielkopf aus offenem Besitzer-Stack geerbt",
    "OWNER_ONLY": "kein Handlungskopf; sichtbarer Besitzer ist Ziel",
}

HEADS = {
    "CH": "sichtbarer CH-Handlungskopf",
    "CHD": "sichtbarer CHD-Handlungskopf",
    "K": "sichtbarer K-Handlungskopf",
    "OK": "sichtbarer OK-Handlungskopf",
    "P": "sichtbarer P-Handlungskopf",
    "R": "sichtbarer R-Handlungskopf; Lage getrennt bestimmen",
    "S": "sichtbarer S-Handlungskopf",
    "SH": "sichtbarer SH-Handlungskopf",
    "T": "sichtbarer T-Handlungskopf",
    "OWNER": "sichtbarer Bild-, Layout- oder Abschnittsbesitzer",
}

R_TOPOLOGIES = {
    "NONE": "kein R-Zielkopf in diesem Anschluss",
    "R_POSITIONAL_HEAD": "R eroeffnet einen eigenen Kopf mit rechtem Glied",
    "R_POSITIONAL_TAIL": "voriger Kopf bleibt aktiv; R hat kein eigenes rechtes Glied",
    "R_POSITIONAL_NESTED": "voriger Kopf bleibt aktiv; R besitzt zugleich ein eigenes rechtes Glied",
}

DUPLICATE_MODES = {
    "SINGLE": "keine sichtbare Doppelung",
    "FREE_PLURAL_OR_REPEAT": "zwei freie Peers; keine Kopie loeschen",
    "PACKAGE_SCOPE_DESCENT": "erste Kopie bindet aussen, zweite eine sichtbare Untereinheit",
}

EVENT_FIELDS = [
    "page_slot", "page_id", "locus_id", "statement_id", "event_id", "card_ordinal",
    "surface", "surface_status", "visible_recipe", "recipe_support_id", "owner_id",
    "owner_evidence", "focus_atom_ordinal", "focus_core", "focus_family",
    "scope_selector", "attachment_geometry", "target_card_offset", "target_event_id",
    "target_atom_ordinal", "target_head", "r_topology", "duplicate_mode",
    "duplicate_role", "boundary_crossing", "lookahead_cards", "core_contract_status",
    "working_core_value", "local_expansion", "admission_color", "stop_reason_code",
    "repair_or_next_action", "review_note",
]


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str] | None = None) -> None:
    if fields is None:
        if not rows:
            raise AssertionError(f"fields required for empty output: {path.name}")
        fields = list(rows[0])
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    upstream_axes = read_tsv(AXES)
    result402 = json.loads(RESULT402.read_text(encoding="utf-8"))
    error_deck = read_tsv(ERROR_DECK401)
    if result402["attachment_count"] != 4374 or result402["factorized_fail_count"] != 0:
        raise AssertionError("GDT402 parser is not the expected complete base")
    if len(error_deck) != 14:
        raise AssertionError("GDT401 V2 error deck changed")

    expected = {
        "SCOPE_SELECTOR": set(SELECTORS),
        "ATTACHMENT_GEOMETRY": set(GEOMETRIES),
        "ACTION_HEAD": set(HEADS),
        "R_TOPOLOGY": set(R_TOPOLOGIES),
        "DUPLICATE_MODE": set(DUPLICATE_MODES),
    }
    by_axis: dict[str, dict[str, dict[str, str]]] = {axis: {} for axis in expected}
    for row in upstream_axes:
        if row["axis"] in by_axis:
            by_axis[row["axis"]][row["value"]] = row
    if {axis: set(values) for axis, values in by_axis.items()} != expected:
        raise AssertionError("GDT402 factor axes changed")

    descriptions = {
        "SCOPE_SELECTOR": SELECTORS,
        "ATTACHMENT_GEOMETRY": GEOMETRIES,
        "ACTION_HEAD": HEADS,
        "R_TOPOLOGY": R_TOPOLOGIES,
        "DUPLICATE_MODE": DUPLICATE_MODES,
    }
    axis_rows: list[dict[str, object]] = []
    for axis in ["SCOPE_SELECTOR", "ATTACHMENT_GEOMETRY", "ACTION_HEAD", "R_TOPOLOGY", "DUPLICATE_MODE"]:
        for value in sorted(expected[axis]):
            source = by_axis[axis][value]
            special = (
                axis == "R_TOPOLOGY" and value == "R_POSITIONAL_NESTED"
            ) or (
                axis == "DUPLICATE_MODE" and value == "PACKAGE_SCOPE_DESCENT"
            )
            axis_rows.append({
                "axis": axis,
                "value": value,
                "current_occurrences": source["occurrences"],
                "current_page_count": source["page_count"],
                "current_register_count": source["register_count"],
                "operator_rule": descriptions[axis][value],
                "future_policy": "AMBER_IF_NEW_VISIBLE_SHAPE" if special else "GREEN_IF_VISIBLE_CONDITIONS_MATCH",
            })

    page_rows = []
    for ordinal in range(1, 5):
        page_rows.append({
            "page_slot": f"PAGE_SLOT_{ordinal}",
            "release_status": "UNRELEASED",
            "page_id": "PENDING_USER_RELEASE",
            "register_or_section": "PENDING",
            "source_reference": "PENDING",
            "source_sha256": "PENDING",
            "locus_count": "PENDING",
            "event_count": "PENDING",
            "statement_count": "PENDING",
            "owner_block_count": "PENDING",
            "page_decision": "PENDING",
            "notes": "Do not populate before user release",
        })

    decision_rows = [
        {"priority": 1, "color": "GREEN", "code": "EXACT_SURFACE_ONE_RECIPE", "trigger": "known surface with identical visible recipe", "decision": "READ_WITH_EXISTING_RECIPE", "allowed_repair": "NONE"},
        {"priority": 2, "color": "GREEN", "code": "KNOWN_RECIPE_NEW_SURFACE", "trigger": "new rendering licensed by a named package rule", "decision": "READ_AS_LICENSED_RENDERING", "allowed_repair": "NONE"},
        {"priority": 3, "color": "GREEN", "code": "NEW_VISIBLE_COMPOSITION", "trigger": "new surface composed only of visible fixed cores", "decision": "COMPOSE_FROM_FIXED_CORE_VALUES", "allowed_repair": "NONE"},
        {"priority": 4, "color": "GREEN", "code": "FACTORIZED_SCOPE_MATCH", "trigger": "one old selector plus one old geometry and licensed head", "decision": "PARSE_FACTORS_IN_ORDER", "allowed_repair": "NONE"},
        {"priority": 5, "color": "GREEN", "code": "OWNER_ELLIPSIS", "trigger": "no action head and visible owner is available", "decision": "BIND_TO_OWNER", "allowed_repair": "NONE"},
        {"priority": 6, "color": "GREEN", "code": "NEW_LOCAL_ADDRESS", "trigger": "new local name or address confined to its visible owner", "decision": "KEEP_LOCAL_WITHOUT_PORTABLE_WORD", "allowed_repair": "NONE"},
        {"priority": 7, "color": "AMBER", "code": "NEW_MICROFORM_OLD_FACTORS", "trigger": "new microform but all selector, geometry and head factors are old", "decision": "KEEP_FACTORIZED_AND_RECORD_NEW_MICROFORM", "allowed_repair": "VISIBLE_FACTORIZATION_ONLY"},
        {"priority": 8, "color": "AMBER", "code": "NEW_R_OR_DUPLICATE_SHAPE", "trigger": "new visible R or duplicate arrangement compatible with existing topology logic", "decision": "RECORD_SHAPE_AND_CHECK_WITHOUT_NEW_MEANING", "allowed_repair": "VISIBLE_TOPOLOGY_ONLY"},
        {"priority": 9, "color": "AMBER", "code": "SEMANTIC_EXPANSION_ONLY", "trigger": "structure parses but local concrete expansion is new", "decision": "KEEP_CORE_READING_AND_MARK_LOCAL_EXPANSION", "allowed_repair": "LOCAL_GLOSS_ONLY"},
        {"priority": 10, "color": "RED", "code": "SAME_SURFACE_DIFFERENT_RECIPE", "trigger": "known surface requires a second recipe", "decision": "STOP_PAGE", "allowed_repair": "VISIBLE_RESEGMENTATION_ONLY"},
        {"priority": 11, "color": "RED", "code": "INVISIBLE_ATOM_IMPORT", "trigger": "an atom is copied from an edit-neighbour but is not visible", "decision": "STOP_PAGE", "allowed_repair": "REMOVE_IMPORTED_ATOM"},
        {"priority": 12, "color": "RED", "code": "LOOKAHEAD_OVER_ONE_CARD", "trigger": "target head is more than one card ahead", "decision": "STOP_BATCH", "allowed_repair": "NONE"},
        {"priority": 13, "color": "RED", "code": "OWNER_BOUNDARY_CROSS", "trigger": "attachment crosses a visible owner boundary", "decision": "STOP_BATCH", "allowed_repair": "NONE"},
        {"priority": 14, "color": "RED", "code": "STATEMENT_BOUNDARY_CROSS", "trigger": "attachment crosses a real statement boundary", "decision": "STOP_BATCH", "allowed_repair": "NONE"},
        {"priority": 15, "color": "RED", "code": "UNKNOWN_SELECTOR", "trigger": "a ninth scope selector is required", "decision": "STOP_BATCH", "allowed_repair": "NONE"},
        {"priority": 16, "color": "RED", "code": "UNKNOWN_HEAD", "trigger": "an eleventh target-head class is required", "decision": "STOP_BATCH", "allowed_repair": "NONE"},
        {"priority": 17, "color": "RED", "code": "NEW_COARSE_SCOPE", "trigger": "case cannot be expressed by the factorized axes", "decision": "STOP_BATCH", "allowed_repair": "NONE"},
        {"priority": 18, "color": "RED", "code": "KNOWN_CORE_RETUNED", "trigger": "a known core needs a different portable value", "decision": "STOP_BATCH_BEFORE_DICTIONARY_CHANGE", "allowed_repair": "NONE"},
        {"priority": 19, "color": "RED", "code": "LABEL_OPENS_PROSE_WITHOUT_LAYOUT", "trigger": "an image label is treated as running prose without a layout signal", "decision": "KEEP_AS_ADDRESS_AND_STOP_CLAIM", "allowed_repair": "ADDRESS_ONLY"},
    ]

    checklist_rows = [
        {"step": 1, "operation": "REGISTER_PAGE", "required_output": "page slot, page id, source and hash", "stop_if": "page not explicitly released"},
        {"step": 2, "operation": "MARK_OWNERS", "required_output": "visible owner blocks before card parsing", "stop_if": "owner boundary cannot be stated"},
        {"step": 3, "operation": "COPY_SURFACE", "required_output": "physical card order without normalization", "stop_if": "source order is uncertain"},
        {"step": 4, "operation": "SEGMENT_VISIBLE_RECIPE", "required_output": "visible atoms only", "stop_if": "invisible atom would be needed"},
        {"step": 5, "operation": "CLASSIFY_SURFACE", "required_output": "known, licensed rendering, new composition or unresolved", "stop_if": "known surface needs second recipe"},
        {"step": 6, "operation": "SELECT_SCOPE_RULE", "required_output": "exactly one of eight selectors", "stop_if": "ninth selector is needed"},
        {"step": 7, "operation": "LOCATE_BY_GEOMETRY", "required_output": "exactly one of six geometries", "stop_if": "more than one card or a boundary is crossed"},
        {"step": 8, "operation": "LICENSE_TARGET_HEAD", "required_output": "one of ten visible heads", "stop_if": "eleventh head is needed"},
        {"step": 9, "operation": "RESOLVE_R_TOPOLOGY", "required_output": "one of four R modes", "stop_if": "R shape cannot be read positionally"},
        {"step": 10, "operation": "RESOLVE_DUPLICATION", "required_output": "one of three duplicate modes", "stop_if": "a visible copy must be deleted"},
        {"step": 11, "operation": "BIND_TARGET_INTERNALS", "required_output": "target card read from first head inward", "stop_if": "inner atom changes outer selector"},
        {"step": 12, "operation": "CHECK_CORE_CONTRACT", "required_output": "old values unchanged; local gloss separated", "stop_if": "known core must be retuned"},
        {"step": 13, "operation": "ASSIGN_COLOR", "required_output": "GREEN, AMBER or RED plus exact code", "stop_if": "color lacks a catalog code"},
        {"step": 14, "operation": "SUMMARIZE_PAGE", "required_output": "counts and page decision", "stop_if": "any RED row is unresolved"},
    ]

    write_tsv(OUT / "gdt403_parser_axis_catalog.tsv", axis_rows)
    write_tsv(OUT / "gdt403_four_page_slots.tsv", page_rows)
    write_tsv(OUT / "gdt403_event_admission_template.tsv", [], EVENT_FIELDS)
    write_tsv(OUT / "gdt403_decision_catalog.tsv", decision_rows)
    write_tsv(OUT / "gdt403_operator_checklist.tsv", checklist_rows)

    generated = [
        OUT / "gdt403_parser_axis_catalog.tsv",
        OUT / "gdt403_four_page_slots.tsv",
        OUT / "gdt403_event_admission_template.tsv",
        OUT / "gdt403_decision_catalog.tsv",
        OUT / "gdt403_operator_checklist.tsv",
    ]
    result = {
        "experiment_id": "GDT403",
        "status": "FOUR_PAGE_WORKSHEET_READY__WAITING_FOR_USER_RELEASE",
        "upstream_attachment_count": 4374,
        "page_slot_count": 4,
        "released_page_count": 0,
        "loaded_event_count": 0,
        "scope_selector_count": len(SELECTORS),
        "attachment_geometry_count": len(GEOMETRIES),
        "action_head_count": len(HEADS),
        "r_topology_count": len(R_TOPOLOGIES),
        "duplicate_mode_count": len(DUPLICATE_MODES),
        "event_template_column_count": len(EVENT_FIELDS),
        "green_code_count": sum(row["color"] == "GREEN" for row in decision_rows),
        "amber_code_count": sum(row["color"] == "AMBER" for row in decision_rows),
        "red_code_count": sum(row["color"] == "RED" for row in decision_rows),
        "hard_contract": {
            "max_forward_cards": 1,
            "owner_boundary_crossing": "FORBIDDEN",
            "statement_boundary_crossing": "FORBIDDEN",
            "invisible_atom_import": "FORBIDDEN",
            "known_core_retuning": "FORBIDDEN",
        },
        "input_hashes": {
            str(path.relative_to(ROOT)): sha256(path)
            for path in [AXES, RESULT402, PARSER402, ERROR_DECK401, ERROR_GUIDE401]
        },
        "output_hashes": {path.name: sha256(path) for path in generated},
    }
    (OUT / "gdt403_result.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
