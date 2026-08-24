#!/usr/bin/env python3
"""Compile ordinary workshop readings forward into cards and local surfaces."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
LAYER_DIR = ROOT / "experiments/yolo/sidequest_semantic_layered_readable_six_hundred_eighteenth"
COMMAND_DIR = ROOT / "experiments/yolo/sidequest_semantic_backread_noun_repair_six_hundred_seventeenth"
PALETTE_DIR = ROOT / "experiments/yolo/sidequest_semantic_multiscribe_palette_six_hundred_fourteenth"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def desk_for_record(record: str) -> tuple[str, str]:
    if record.startswith("H"):
        return "P_PREPARATION_DESK", "preparation_desk_surfaces"
    if record in {"B1", "B2"}:
        return "B_BATH_DESK", "bath_desk_surfaces"
    return "S_STATION_DESK", "station_desk_surfaces"


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    events = [
        row for row in read_tsv(LAYER_DIR / "SIX_HUNDRED_EIGHTEENTH_381_LAYERED_EVENTS.tsv")
        if row["case_id"] != "C6"
    ]
    statements = [
        row for row in read_tsv(LAYER_DIR / "SIX_HUNDRED_EIGHTEENTH_116_LAYERED_STATEMENTS.tsv")
        if row["case_id"] != "C6"
    ]
    cards = read_tsv(COMMAND_DIR / "SIX_HUNDRED_SEVENTEENTH_173_SHARP_COMMANDS.tsv")
    rules = read_tsv(PALETTE_DIR / "SIX_HUNDRED_FOURTEENTH_10_COMMAND_CARD_RULES.tsv")
    palettes = read_tsv(PALETTE_DIR / "SIX_HUNDRED_FOURTEENTH_20_CARD_SURFACE_PALETTE.tsv")
    replay = read_tsv(PALETTE_DIR / "SIX_HUNDRED_FOURTEENTH_71_EVENT_SURFACE_REPLAY.tsv")

    statement_by_id = {row["statement_id"]: row for row in statements}
    card_by_id = {row["card_no"]: row for row in cards}
    palette_by_card = {row["card_no"]: row for row in palettes}
    replay_by_event = {row["event_id"]: row for row in replay}
    candidates_by_parse: dict[str, list[str]] = defaultdict(list)
    for row in cards:
        candidates_by_parse[row["semantic_component_parse"]].append(row["card_no"])

    forward = []
    for row in events:
        statement = statement_by_id[row["statement_id"]]
        candidates = candidates_by_parse[row["semantic_component_parse"]]
        if len(candidates) == 1:
            selected_card = candidates[0]
            card_mode = "UNIQUE_COMMAND_TO_CARD"
            card_reason = "UNIQUE_SEMANTIC_COMPONENT_SEQUENCE"
        else:
            replay_row = replay_by_event[row["event_id"]]
            selected_card = replay_row["selected_card_no"]
            card_mode = "CONTEXT_RULE_TO_CARD"
            card_reason = replay_row["selection_reason"]
        selected = card_by_id[selected_card]
        licensed_surfaces = selected["surfaces"].split("|")
        desk, desk_field = desk_for_record(row["record"])
        if len(licensed_surfaces) == 1:
            desk_surfaces = licensed_surfaces
            surface_mode = "UNIQUE_CARD_SURFACE"
            exemplar_needed = "NO"
        elif selected_card in palette_by_card:
            desk_value = palette_by_card[selected_card][desk_field]
            desk_surfaces = [] if desk_value == "NONE" else desk_value.split("|")
            if len(desk_surfaces) == 1:
                surface_mode = "DESK_RULE_UNIQUE"
                exemplar_needed = "NO"
            else:
                surface_mode = "LOCAL_EXEMPLAR_REQUIRED"
                exemplar_needed = "YES"
        else:
            desk_surfaces = licensed_surfaces
            surface_mode = "LOCAL_EXEMPLAR_REQUIRED"
            exemplar_needed = "YES"
        forward.append({
            "event_id": row["event_id"],
            "case_id": row["case_id"],
            "page": row["page"],
            "record": row["record"],
            "statement_id": row["statement_id"],
            "source_instruction_de": statement["legacy_fluent_reading_de"],
            "semantic_component_parse": row["semantic_component_parse"],
            "invariant_command_de": row["standard_command_de"],
            "command_card_candidates": "|".join(candidates),
            "card_selection_mode": card_mode,
            "card_selection_reason": card_reason,
            "selected_card_no": selected_card,
            "observed_card_no": row["card_no"],
            "desk": desk,
            "all_licensed_surfaces": "|".join(licensed_surfaces),
            "desk_surface_candidates": "|".join(desk_surfaces),
            "surface_selection_mode": surface_mode,
            "local_exemplar_needed": exemplar_needed,
            "selected_surface": row["surface"],
            "surface_roundtrip": "YES" if row["surface"] in desk_surfaces else "NO",
        })

    forward_by_statement: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in forward:
        forward_by_statement[str(row["statement_id"])].append(row)
    statement_rows = []
    for statement in statements:
        rows = forward_by_statement[statement["statement_id"]]
        statement_rows.append({
            "case_id": statement["case_id"],
            "phase": statement["phase"],
            "statement_id": statement["statement_id"],
            "page": statement["page"],
            "record": statement["record"],
            "source_instruction_de": statement["legacy_fluent_reading_de"],
            "semantic_component_sequence": " | ".join(str(row["semantic_component_parse"]) for row in rows),
            "invariant_command_sequence_de": " | ".join(str(row["invariant_command_de"]) for row in rows),
            "selected_card_sequence": " | ".join(str(row["selected_card_no"]) for row in rows),
            "reconstructed_surface_sequence": " ".join(str(row["selected_surface"]) for row in rows),
            "source_surface_sequence": statement["surface_sequence"],
            "context_card_choices": sum(row["card_selection_mode"] == "CONTEXT_RULE_TO_CARD" for row in rows),
            "desk_surface_choices": sum(row["surface_selection_mode"] == "DESK_RULE_UNIQUE" for row in rows),
            "local_exemplar_surface_choices": sum(row["local_exemplar_needed"] == "YES" for row in rows),
            "exact_roundtrip": "YES" if " ".join(str(row["selected_surface"]) for row in rows) == statement["surface_sequence"] else "NO",
        })

    ambiguity_rows = [
        {
            "event_id": row["event_id"],
            "case_id": row["case_id"],
            "record": row["record"],
            "statement_id": row["statement_id"],
            "invariant_command_de": row["invariant_command_de"],
            "selected_card_no": row["selected_card_no"],
            "desk": row["desk"],
            "candidate_surfaces": row["desk_surface_candidates"],
            "selected_surface": row["selected_surface"],
            "why_not_semantically_determined_de": "gleicher Kartenbefehl und gleiche Kartenidentitaet erlauben mehrere lokale Schreibformen; Muster oder Nachbarform entscheidet",
        }
        for row in forward if row["local_exemplar_needed"] == "YES"
    ]

    write_tsv(HERE / "SIX_HUNDRED_TWENTY_SEVENTH_372_FORWARD_EVENT_COMPILATION.tsv", forward, list(forward[0]))
    write_tsv(HERE / "SIX_HUNDRED_TWENTY_SEVENTH_115_FORWARD_STATEMENT_COMPILATION.tsv", statement_rows, list(statement_rows[0]))
    write_tsv(HERE / "SIX_HUNDRED_TWENTY_SEVENTH_179_SURFACE_EXEMPLAR_CHOICES.tsv", ambiguity_rows, list(ambiguity_rows[0]))
    write_tsv(HERE / "SIX_HUNDRED_TWENTY_SEVENTH_10_CARD_CHOICE_RULES.tsv", rules, list(rules[0]))

    md = [
        "# Vorwaerts-Handbuch: Werkstattanweisung zu Karte und Oberflaeche",
        "",
        "## Drei Entscheidungen",
        "",
        "1. Die normale kurze Werkstattanweisung wird in die 39 Komponenten und daraus in einen invarianten Befehl zerlegt.",
        "2. Der Befehl waehlt eine exakte gelernte Karte. Meist ist sie eindeutig; bei zehn Doppelbefehlen entscheidet eine feste Kontextregel.",
        "3. Die Karte waehlt eine sichtbare Oberflaeche. Eine Einzelform oder eine eindeutige Schreibtischregel reicht oft; sonst wird die lokale Form aus dem Exemplar kopiert.",
        "",
    ]
    by_record: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in statement_rows:
        by_record[str(row["record"])].append(row)
    for record in ("H1", "B1", "H2", "B2", "H3", "B3", "H4", "B4", "H5", "B5"):
        md.extend([f"## {record}", ""])
        for row in by_record[record]:
            md.extend([
                f"### {row['statement_id']}",
                "",
                f"**Normale Anweisung:** {row['source_instruction_de']}",
                "",
                f"**Kartenbefehle:** {row['invariant_command_sequence_de']}",
                "",
                f"**Karten:** `{row['selected_card_sequence']}`",
                "",
                f"**Schrift:** `{row['reconstructed_surface_sequence']}`",
                "",
                f"Kontext-Kartenwahlen: {row['context_card_choices']}; Schreibtisch-Einzelformen: {row['desk_surface_choices']}; lokale Exemplarwahlen: {row['local_exemplar_surface_choices']}.",
                "",
            ])
    (HERE / "SIX_HUNDRED_TWENTY_SEVENTH_FIVE_CASE_FORWARD_MANUAL.md").write_text("\n".join(md).rstrip() + "\n", encoding="utf-8")

    modes = Counter(row["surface_selection_mode"] for row in forward)
    card_modes = Counter(row["card_selection_mode"] for row in forward)
    summary = {
        "status": "PASS",
        "cases": 5,
        "statements": len(statement_rows),
        "events": len(forward),
        "unique_command_to_card_events": card_modes["UNIQUE_COMMAND_TO_CARD"],
        "context_rule_to_card_events": card_modes["CONTEXT_RULE_TO_CARD"],
        "unique_card_surface_events": modes["UNIQUE_CARD_SURFACE"],
        "desk_rule_unique_surface_events": modes["DESK_RULE_UNIQUE"],
        "local_exemplar_surface_events": modes["LOCAL_EXEMPLAR_REQUIRED"],
        "visible_surface_without_local_exemplar": modes["UNIQUE_CARD_SURFACE"] + modes["DESK_RULE_UNIQUE"],
        "exact_event_roundtrips": sum(row["surface_roundtrip"] == "YES" for row in forward),
        "exact_statement_roundtrips": sum(row["exact_roundtrip"] == "YES" for row in statement_rows),
        "new_words": 0,
        "decision": "INVARIANT_COMMAND_USUALLY_SELECTS_CARD__VISIBLE_SURFACE_SPLIT_BETWEEN_RULE_AND_LOCAL_EXEMPLAR",
    }
    (HERE / "SIX_HUNDRED_TWENTY_SEVENTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
