#!/usr/bin/env python3
"""Compile the complete thirty-page prose working edition."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt566_complete_thirty_page_prose_working_edition"
OUT = BASE / "artifacts"
G515 = ROOT / "experiments/yolo/gdt515_second_random_four_page_full_admission/artifacts"
G416 = ROOT / "experiments/yolo/gdt416_owner_local_imperative_sentence_compiler/artifacts"
G539 = ROOT / "experiments/yolo/gdt539_four_page_contextual_statement_edition/artifacts"
G565 = ROOT / "experiments/yolo/gdt565_state_microphrase_template_generator/artifacts"
INPUTS = {
    "navigation_events": G515 / "gdt515_5122_running_event_edition.tsv",
    "page_summary": G515 / "gdt515_30_page_summary.tsv",
    "old_clauses": G416 / "gdt416_4576_imperative_clauses.tsv",
    "old_statements": G416 / "gdt416_715_imperative_statements.tsv",
    "current_clauses": G539 / "gdt539_546_contextual_prose_events.tsv",
    "current_statements": G539 / "gdt539_78_contextual_statements.tsv",
    "state_generator": G565 / "gdt565_1656_template_replay.tsv",
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"Refusing to write empty table {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def packed(values: set[str] | list[str], separator: str = "|") -> str:
    return separator.join(sorted(set(values)))


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    navigation = read_tsv(INPUTS["navigation_events"])
    page_source = read_tsv(INPUTS["page_summary"])
    old_clauses = read_tsv(INPUTS["old_clauses"])
    old_statements = read_tsv(INPUTS["old_statements"])
    current_clauses = read_tsv(INPUTS["current_clauses"])
    current_statements = read_tsv(INPUTS["current_statements"])
    state_rows = read_tsv(INPUTS["state_generator"])
    expected_counts = [5122, 30, 4576, 715, 546, 78, 1656]
    if [len(navigation), len(page_source), len(old_clauses), len(old_statements), len(current_clauses), len(current_statements), len(state_rows)] != expected_counts:
        raise RuntimeError("Input count drift")

    old_by_id = {row["global_running_event_id"]: row for row in old_clauses}
    current_by_id = {row["event_id"]: row for row in current_clauses}
    state_by_id = {row["event_id"]: row for row in state_rows}
    old_statement_by_id = {row["global_statement_id"]: row for row in old_statements}
    current_statement_by_id = {row["statement_id"]: row for row in current_statements}
    if len(old_by_id) != 4576 or len(current_by_id) != 546 or len(state_by_id) != 1656:
        raise RuntimeError("Input key duplication")

    event_rows: list[dict[str, object]] = []
    for nav in sorted(navigation, key=lambda row: int(row["global_running_ordinal"])):
        navigation_id = nav["global_running_event_id"]
        if navigation_id in old_by_id:
            source = old_by_id[navigation_id]
            event_id = navigation_id
            cohort = "OLD26_GDT416"
            statement_id = source["global_statement_id"]
            card_ordinal = source["card_ordinal_in_statement"]
            final_recipe = source["component_recipe"]
            owner_id = source["owner_de"]
            owner_de = source["owner_de"]
            owner_class = source["owner_class"]
            owner_clause = source["imperative_clause_de"]
            portable_trace = source["portable_back_projection_de"]
            context_source_layer = "GDT416_OWNER_CONTEXT"
            source_roundtrip = source["roundtrip_exact"]
        else:
            event_id = nav["source_event_id"]
            if event_id not in current_by_id:
                raise RuntimeError(f"Navigation event has no clause source: {navigation_id}")
            source = current_by_id[event_id]
            cohort = "CURRENT4_GDT539"
            statement_id = source["statement_id"]
            card_ordinal = source["card_ordinal_in_statement"]
            final_recipe = source["final_context_recipe"]
            owner_id = source["owner_id"]
            owner_de = source["owner_de"]
            owner_class = source["content_role"]
            owner_clause = source["contextual_clause_de"]
            portable_trace = source["controlled_order_reading_de"]
            context_source_layer = "GDT539_OWNER_CONTEXT"
            source_roundtrip = "YES" if source["exact_recipe_roundtrip"] == final_recipe else "NO"

        state = state_by_id.get(event_id)
        if state is not None:
            if state["recipe"] != final_recipe:
                raise RuntimeError(f"State generator recipe mismatch at {event_id}")
            selected_clause = state["generated_microphrase_de"]
            selected_layer = "GDT565_STATE_GENERATOR"
            state_status = "STATE_CARD"
            state_replay_status = state["replay_status"]
            outer_template_id = state["outer_template_id"]
            structural_template_id = state["structural_template_id"]
            state_atom_alignment = state["written_atom_alignment"]
        else:
            selected_clause = owner_clause
            selected_layer = (
                "GDT416_OWNER_CONTEXT_NONSTATE"
                if cohort == "OLD26_GDT416" else "GDT539_OWNER_CONTEXT_NONSTATE"
            )
            state_status = "NONSTATE_CARD"
            state_replay_status = "NOT_APPLICABLE"
            outer_template_id = "NOT_APPLICABLE"
            structural_template_id = "NOT_APPLICABLE"
            state_atom_alignment = "NOT_APPLICABLE"

        event_rows.append({
            "edition_event_ordinal": len(event_rows) + 1,
            "navigation_event_id": navigation_id,
            "event_id": event_id,
            "cohort": cohort,
            "statement_id": statement_id,
            "card_ordinal_in_statement": card_ordinal,
            "physical_page": nav["physical_page"],
            "register": nav["register"],
            "owner_class_or_role": owner_class,
            "owner_id": owner_id,
            "owner_de": owner_de,
            "locus": nav["locus"],
            "surface": nav["surface"],
            "gdt515_navigation_recipe": nav["component_recipe"],
            "final_context_recipe": final_recipe,
            "recipe_relation_to_gdt515": "SAME" if nav["component_recipe"] == final_recipe else "LATER_CONTEXT_REPAIR",
            "portable_or_controlled_trace_de": portable_trace,
            "state_status": state_status,
            "selected_reading_layer": selected_layer,
            "state_replay_status": state_replay_status,
            "outer_template_id": outer_template_id,
            "structural_template_id": structural_template_id,
            "selected_working_clause_de": selected_clause,
            "owner_bound_control_clause_de": owner_clause,
            "selected_equals_owner_bound": "YES" if selected_clause == owner_clause else "NO",
            "state_atom_alignment": state_atom_alignment,
            "source_context_layer": context_source_layer,
            "source_recipe_roundtrip": source_roundtrip,
            "guard": "COMPLETE_PROSE_EVENT__SELECTED_AND_OWNER_BOUND_CHANNELS_DISTINCT",
        })

    if len({row["event_id"] for row in event_rows}) != 5122:
        raise RuntimeError("Edition event IDs are not unique")
    if set(state_by_id) != {row["event_id"] for row in event_rows if row["state_status"] == "STATE_CARD"}:
        raise RuntimeError("State-card partition drift")

    by_statement: dict[str, list[dict[str, object]]] = defaultdict(list)
    statement_order: list[str] = []
    for row in event_rows:
        statement_id = str(row["statement_id"])
        if statement_id not in by_statement:
            statement_order.append(statement_id)
        by_statement[statement_id].append(row)

    statement_rows: list[dict[str, object]] = []
    for ordinal, statement_id in enumerate(statement_order, 1):
        members = sorted(by_statement[statement_id], key=lambda row: int(row["card_ordinal_in_statement"]))
        cohort = str(members[0]["cohort"])
        source_statement = old_statement_by_id[statement_id] if cohort == "OLD26_GDT416" else current_statement_by_id[statement_id]
        owner_bound = " ".join(str(row["owner_bound_control_clause_de"]) for row in members)
        expected_owner_bound = (
            source_statement["imperative_reading_de"]
            if cohort == "OLD26_GDT416" else source_statement["contextual_working_reading_de"]
        )
        if owner_bound != expected_owner_bound:
            raise RuntimeError(f"Statement source replay mismatch: {statement_id}")
        state_count = sum(row["state_status"] == "STATE_CARD" for row in members)
        nonstate_count = len(members) - state_count
        statement_mode = (
            "ALL_STATE" if state_count == len(members)
            else "NO_STATE" if state_count == 0
            else "MIXED_STATE_AND_NONSTATE"
        )
        selected_reading = " ".join(str(row["selected_working_clause_de"]) for row in members)
        statement_rows.append({
            "edition_statement_ordinal": ordinal,
            "statement_id": statement_id,
            "cohort": cohort,
            "physical_page": members[0]["physical_page"],
            "register": members[0]["register"],
            "owner_id": members[0]["owner_id"],
            "owner_de": members[0]["owner_de"],
            "event_count": len(members),
            "state_card_count": state_count,
            "nonstate_card_count": nonstate_count,
            "statement_mode": statement_mode,
            "normalized_state_card_count": sum(row["state_replay_status"] == "EDITORIAL_DOUBLE_ARGUMENT_NORMALIZATION" for row in members),
            "event_ids": "|".join(str(row["event_id"]) for row in members),
            "surface_sequence": " ".join(str(row["surface"]) for row in members),
            "final_recipe_sequence": " | ".join(str(row["final_context_recipe"]) for row in members),
            "selected_layer_sequence": "|".join(str(row["selected_reading_layer"]) for row in members),
            "selected_working_reading_de": selected_reading,
            "owner_bound_control_reading_de": owner_bound,
            "owner_bound_source_statement_de": expected_owner_bound,
            "owner_bound_source_byte_exact": "YES",
            "selected_equals_owner_bound": "YES" if selected_reading == owner_bound else "NO",
            "end_mode": source_statement["end_mode"],
            "guard": "COMPLETE_STATEMENT__GENERATOR_AND_OWNER_CONTEXT_CHANNELS_RETAINED",
        })

    mode_profiles: list[dict[str, object]] = []
    mode_labels = {
        "ALL_STATE": "Aussage vollständig aus GDT565-Zustandskarten",
        "MIXED_STATE_AND_NONSTATE": "GDT565-Zustandskarten und ownergebundene Nichtzustandskarten gemischt",
        "NO_STATE": "keine Zustandskarte; ownergebundene Quellausgabe unverändert",
    }
    for mode in ("ALL_STATE", "MIXED_STATE_AND_NONSTATE", "NO_STATE"):
        members = [row for row in statement_rows if row["statement_mode"] == mode]
        mode_profiles.append({
            "statement_mode": mode,
            "statement_mode_de": mode_labels[mode],
            "statement_count": len(members),
            "event_count": sum(int(row["event_count"]) for row in members),
            "state_card_count": sum(int(row["state_card_count"]) for row in members),
            "nonstate_card_count": sum(int(row["nonstate_card_count"]) for row in members),
            "physical_page_count": len({str(row["physical_page"]) for row in members}),
            "register_count": len({str(row["register"]) for row in members}),
        })

    layer_profiles: list[dict[str, object]] = []
    for layer in ("GDT565_STATE_GENERATOR", "GDT416_OWNER_CONTEXT_NONSTATE", "GDT539_OWNER_CONTEXT_NONSTATE"):
        members = [row for row in event_rows if row["selected_reading_layer"] == layer]
        layer_profiles.append({
            "selected_reading_layer": layer,
            "event_count": len(members),
            "statement_count": len({str(row["statement_id"]) for row in members}),
            "physical_page_count": len({str(row["physical_page"]) for row in members}),
            "register_count": len({str(row["register"]) for row in members}),
            "distinct_recipe_count": len({str(row["final_context_recipe"]) for row in members}),
            "distinct_clause_count": len({str(row["selected_working_clause_de"]) for row in members}),
        })

    page_rows: list[dict[str, object]] = []
    for source_page in sorted(page_source, key=lambda row: int(row["page_ordinal"])):
        page = source_page["physical_page"]
        events = [row for row in event_rows if row["physical_page"] == page]
        statements = [row for row in statement_rows if row["physical_page"] == page]
        page_rows.append({
            "page_ordinal": source_page["page_ordinal"],
            "physical_page": page,
            "registers": source_page["registers"],
            "source_running_event_count": source_page["running_event_count"],
            "edition_event_count": len(events),
            "source_statement_count": source_page["statement_count"],
            "edition_statement_count": len(statements),
            "state_card_count": sum(row["state_status"] == "STATE_CARD" for row in events),
            "nonstate_card_count": sum(row["state_status"] == "NONSTATE_CARD" for row in events),
            "all_state_statement_count": sum(row["statement_mode"] == "ALL_STATE" for row in statements),
            "mixed_statement_count": sum(row["statement_mode"] == "MIXED_STATE_AND_NONSTATE" for row in statements),
            "no_state_statement_count": sum(row["statement_mode"] == "NO_STATE" for row in statements),
            "normalized_state_card_count": sum(row["state_replay_status"] == "EDITORIAL_DOUBLE_ARGUMENT_NORMALIZATION" for row in events),
            "recipe_repair_count_after_gdt515": sum(row["recipe_relation_to_gdt515"] == "LATER_CONTEXT_REPAIR" for row in events),
            "page_status": "ZERO_RUNNING_EVENT_PAGE_RETAINED" if not events else "COMPLETE_RUNNING_PAGE",
            "count_parity": "YES" if len(events) == int(source_page["running_event_count"]) and len(statements) == int(source_page["statement_count"]) else "NO",
        })

    source_mismatch_rows = [
        {
            "repair_ordinal": index,
            "event_id": row["event_id"],
            "physical_page": row["physical_page"],
            "surface": row["surface"],
            "gdt515_navigation_recipe": row["gdt515_navigation_recipe"],
            "final_context_recipe": row["final_context_recipe"],
            "state_status": row["state_status"],
            "selected_reading_layer": row["selected_reading_layer"],
            "repair_status": "EXPLICIT_LATER_CONTEXT_RECIPE_RETAINED",
        }
        for index, row in enumerate(
            [row for row in event_rows if row["recipe_relation_to_gdt515"] == "LATER_CONTEXT_REPAIR"], 1
        )
    ]

    result = {
        "status": "PASS_COMPLETE_5122_EVENT__793_STATEMENT__30_PAGE_WORKING_EDITION__1656_GENERATED_STATE__3466_OWNER_CONTEXT_NONSTATE__ZERO_REST",
        "admitted_page_count": len(page_rows),
        "running_page_count": sum(int(row["edition_event_count"]) > 0 for row in page_rows),
        "zero_running_page_count": sum(int(row["edition_event_count"]) == 0 for row in page_rows),
        "complete_event_count": len(event_rows),
        "complete_statement_count": len(statement_rows),
        "state_generator_event_count": sum(row["state_status"] == "STATE_CARD" for row in event_rows),
        "nonstate_owner_context_event_count": sum(row["state_status"] == "NONSTATE_CARD" for row in event_rows),
        "old_nonstate_event_count": sum(row["selected_reading_layer"] == "GDT416_OWNER_CONTEXT_NONSTATE" for row in event_rows),
        "current_nonstate_event_count": sum(row["selected_reading_layer"] == "GDT539_OWNER_CONTEXT_NONSTATE" for row in event_rows),
        "all_state_statement_count": sum(row["statement_mode"] == "ALL_STATE" for row in statement_rows),
        "mixed_statement_count": sum(row["statement_mode"] == "MIXED_STATE_AND_NONSTATE" for row in statement_rows),
        "no_state_statement_count": sum(row["statement_mode"] == "NO_STATE" for row in statement_rows),
        "state_touched_statement_count": sum(int(row["state_card_count"]) > 0 for row in statement_rows),
        "owner_bound_statement_byte_exact_count": sum(row["owner_bound_source_byte_exact"] == "YES" for row in statement_rows),
        "selected_clause_equals_owner_bound_count": sum(row["selected_equals_owner_bound"] == "YES" for row in event_rows),
        "selected_clause_differs_owner_bound_count": sum(row["selected_equals_owner_bound"] == "NO" for row in event_rows),
        "gdt565_editorial_normalization_count": sum(row["state_replay_status"] == "EDITORIAL_DOUBLE_ARGUMENT_NORMALIZATION" for row in event_rows),
        "later_context_recipe_repair_count": len(source_mismatch_rows),
        "all_events_have_selected_clause": all(row["selected_working_clause_de"] for row in event_rows),
        "all_events_have_owner_bound_control": all(row["owner_bound_control_clause_de"] for row in event_rows),
        "all_page_counts_match_gdt515": all(row["count_parity"] == "YES" for row in page_rows),
        "new_pages": 0,
        "new_events": 0,
        "new_statements": 0,
        "new_surfaces": 0,
        "new_root_values": 0,
        "input_sha256": {name: sha256(path) for name, path in INPUTS.items()},
    }

    write_tsv(OUT / "gdt566_5122_complete_prose_event_edition.tsv", event_rows)
    write_tsv(OUT / "gdt566_793_complete_statement_edition.tsv", statement_rows)
    write_tsv(OUT / "gdt566_30_page_edition_profiles.tsv", page_rows)
    write_tsv(OUT / "gdt566_3_statement_mode_profiles.tsv", mode_profiles)
    write_tsv(OUT / "gdt566_3_reading_layer_profiles.tsv", layer_profiles)
    write_tsv(OUT / "gdt566_10_later_context_recipe_repairs.tsv", source_mismatch_rows)

    book = [
        "# GDT566 – vollständige30-Seiten-Proseausgabe",
        "",
        "Diese Ausgabe enthält alle5.122 laufenden Karten in793 Aussagen. Zustandskarten benutzen",
        "die GDT565-Generatorzeile; Nichtzustandskarten behalten ihre ownergebundene GDT416/GDT539-Zeile.",
        "Die maschinenlesbare Ausgabe bewahrt daneben für jede Karte beide Kanäle.",
        "",
        "```text",
        "1.656 GDT565-Zustandskarten",
        "3.082 alte ownergebundene Nichtzustandskarten",
        "  384 aktuelle ownergebundene Nichtzustandskarten",
        "────────────────────────────────────────────",
        "5.122 Karten /793 Aussagen /30 zugelassene Seiten",
        "```",
        "",
    ]
    statements_by_page: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in statement_rows:
        statements_by_page[str(row["physical_page"])].append(row)
    for page in page_rows:
        book += [f"## {page['physical_page']}", ""]
        if int(page["edition_event_count"]) == 0:
            book += ["Keine laufende Prosa; die Seite bleibt als zugelassene reine Lokalregisterseite sichtbar.", ""]
            continue
        book += [
            f"{page['edition_event_count']} Karten, {page['edition_statement_count']} Aussagen, "
            f"{page['state_card_count']} Zustandskarten.",
            "",
        ]
        for statement in statements_by_page[str(page["physical_page"])]:
            book += [
                f"### {statement['statement_id']} · {statement['statement_mode']} · {statement['event_count']} Karten",
                "",
                f"**Formen:** {statement['surface_sequence']}",
                "",
                str(statement["selected_working_reading_de"]),
                "",
            ]
    (OUT / "GDT566_COMPLETE_THIRTY_PAGE_PROSE_EDITION.md").write_text("\n".join(book), encoding="utf-8")
    (OUT / "gdt566_result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
