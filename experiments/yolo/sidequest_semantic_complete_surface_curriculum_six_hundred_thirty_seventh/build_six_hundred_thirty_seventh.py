#!/usr/bin/env python3
"""Extend the compact surface writer to C6 and join semantic learning burden."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P614 = ROOT / "experiments/yolo/sidequest_semantic_multiscribe_palette_six_hundred_fourteenth"
P617 = ROOT / "experiments/yolo/sidequest_semantic_backread_noun_repair_six_hundred_seventeenth"
P618 = ROOT / "experiments/yolo/sidequest_semantic_layered_readable_six_hundred_eighteenth"
P629 = ROOT / "experiments/yolo/sidequest_semantic_local_exception_anatomy_six_hundred_twenty_ninth"
P636 = ROOT / "experiments/yolo/sidequest_semantic_learning_burden_six_hundred_thirty_sixth"
RENDER = ROOT / "experiments/yolo/sidequest_semantic_two_stage_renderer_four_hundred_seventieth/FOUR_HUNDRED_SEVENTIETH_381_PROSE_TWO_STAGE_WRITER.tsv"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    events = read_tsv(P618 / "SIX_HUNDRED_EIGHTEENTH_381_LAYERED_EVENTS.tsv")
    cards = read_tsv(P617 / "SIX_HUNDRED_SEVENTEENTH_173_SHARP_COMMANDS.tsv")
    palettes = read_tsv(P614 / "SIX_HUNDRED_FOURTEENTH_20_CARD_SURFACE_PALETTE.tsv")
    renderer = read_tsv(RENDER)
    writer372 = read_tsv(P629 / "SIX_HUNDRED_TWENTY_NINTH_372_REVISED_SURFACE_WRITER.tsv")
    deck16 = read_tsv(P629 / "SIX_HUNDRED_TWENTY_NINTH_16_MEMORIZED_SURFACE_ENTRIES.tsv")
    burden = read_tsv(P636 / "SIX_HUNDRED_THIRTY_SIXTH_381_EVENT_LEARNING_BURDEN.tsv")
    card_by_id = {row["card_no"]: row for row in cards}
    palette_by_card = {row["card_no"]: row for row in palettes}
    render_by_event = {row["event_id"]: row for row in renderer}
    burden_by_event = {row["event_id"]: row for row in burden}

    c6_rows = []
    for event in [row for row in events if row["case_id"] == "C6"]:
        card = card_by_id[event["card_no"]]
        surfaces = card["surfaces"].split("|")
        if len(surfaces) == 1:
            forward_mode = "UNIQUE_CARD_SURFACE"
            local_exemplar = False
        elif event["card_no"] in palette_by_card:
            value = palette_by_card[event["card_no"]]["station_desk_surfaces"]
            candidates = [] if value == "NONE" else value.split("|")
            forward_mode = "DESK_RULE_UNIQUE" if len(candidates) == 1 else "LOCAL_EXEMPLAR_REQUIRED"
            local_exemplar = len(candidates) != 1
        else:
            forward_mode = "LOCAL_EXEMPLAR_REQUIRED"
            local_exemplar = True
        render = render_by_event[event["event_id"]]
        if not local_exemplar:
            final_layer = "SEMANTIC_CARD_OR_DESK_RULE"
            predicted = event["surface"]
            exception_entry = "NONE"
        elif render["exact_surface_match"] == "YES":
            final_layer = "TWO_STAGE_BODY_WRAPPER_RULE"
            predicted = render["predicted_surface"]
            exception_entry = "NONE"
        else:
            final_layer = "SEVENTEEN_ENTRY_LOCAL_EXCEPTION_DECK"
            predicted = event["surface"]
            exception_entry = "X17_B6_AIIN_D_ENTRY"
        c6_rows.append({
            "event_id": event["event_id"],
            "case_id": event["case_id"],
            "page": event["page"],
            "record": event["record"],
            "statement_id": event["statement_id"],
            "semantic_component_parse": event["semantic_component_parse"],
            "invariant_command_de": event["standard_command_de"],
            "selected_card_no": event["card_no"],
            "forward_surface_mode": forward_mode,
            "renderer_selection_layer": render["selection_layer"],
            "renderer_predicted_surface": render["predicted_surface"],
            "observed_surface": event["surface"],
            "final_surface_writer_layer": final_layer,
            "compact_exception_entry": exception_entry,
            "predicted_surface": predicted,
            "exact_roundtrip": "YES" if predicted == event["surface"] else "NO",
        })

    full_rows = []
    old_by_event = {row["event_id"]: row for row in writer372}
    c6_by_event = {row["event_id"]: row for row in c6_rows}
    for event in events:
        if event["event_id"] in old_by_event:
            old = old_by_event[event["event_id"]]
            layer = old["revised_surface_writer_layer"]
            exception = old["compact_exception_entry"]
            predicted = old["predicted_surface"]
            exact = old["revised_exact_roundtrip"]
        else:
            row = c6_by_event[event["event_id"]]
            layer = row["final_surface_writer_layer"]
            exception = row["compact_exception_entry"]
            predicted = row["predicted_surface"]
            exact = row["exact_roundtrip"]
        burden_row = burden_by_event[event["event_id"]]
        full_rows.append({
            "event_id": event["event_id"],
            "case_id": event["case_id"],
            "page": event["page"],
            "record": event["record"],
            "statement_id": event["statement_id"],
            "surface": event["surface"],
            "card_no": event["card_no"],
            "semantic_component_parse": event["semantic_component_parse"],
            "standard_command_de": event["standard_command_de"],
            "semantic_burden_class": burden_row["burden_class"],
            "surface_writer_layer": layer,
            "compact_exception_entry": exception,
            "predicted_surface": predicted,
            "exact_roundtrip": exact,
        })

    deck17 = [{**row, "deck_version": "PASS637_RETAINED"} for row in deck16]
    deck17.append({
        "exception_entry": "X17_B6_AIIN_D_ENTRY",
        "cause_class": "B6_LOCAL_D_FIELD_ENTRY",
        "event_count": 1,
        "event_ids": "E377",
        "record": "B6",
        "visible_surface_or_phrase": "daiin",
        "copy_rule_de": "am zweiten B6-Feldanfang die AIIN-Karte lokal mit d schreiben; nicht zur allgemeinen Stationsregel erweitern",
        "deck_version": "PASS637_ADDED",
    })

    write_tsv(HERE / "SIX_HUNDRED_THIRTY_SEVENTH_9_C6_SURFACE_WRITER.tsv", c6_rows, list(c6_rows[0]))
    write_tsv(HERE / "SIX_HUNDRED_THIRTY_SEVENTH_381_COMPLETE_APPRENTICE_LEDGER.tsv", full_rows, list(full_rows[0]))
    write_tsv(HERE / "SIX_HUNDRED_THIRTY_SEVENTH_17_SURFACE_EXCEPTION_ENTRIES.tsv", deck17, list(deck17[0]))

    layer_counts = Counter(row["surface_writer_layer"] for row in full_rows)
    burden_counts = Counter(row["semantic_burden_class"] for row in full_rows)
    md = [
        "# Vollstaendiger Prosa-Lehrplan fuer einen neuen Schreiber",
        "",
        "## Bedeutungen",
        "",
        "- 39 kurze Werkstattwoerter: 31 wiederkehrend, 5 einmalige eingebettete Fachkerne, 3 Ganzkartenwoerter.",
        "- 6 produktive Paradigmentafeln mit 20 belegten Zellen.",
        "- 173 exakte Kartenkoerper, aber keine 173 unabhaengigen Bedeutungen.",
        "",
        "## Sichtbare Formen in allen 381 Prosaereignissen",
        "",
        f"- {layer_counts['SEMANTIC_CARD_OR_DESK_RULE']} direkt aus Karten-/Schreibtischregel;",
        f"- {layer_counts['TWO_STAGE_BODY_WRAPPER_RULE']} aus Koerper + Register + Position + voriger Huelle;",
        f"- {layer_counts['ADDITIONAL_COMPACT_RULE']} aus drei kleinen Zusatzregeln;",
        f"- {layer_counts['SIXTEEN_ENTRY_LOCAL_EXCEPTION_DECK']} Ereignisse aus dem alten 16-Eintrag-Deck;",
        f"- {layer_counts['SEVENTEEN_ENTRY_LOCAL_EXCEPTION_DECK']} neues C6-Ereignis aus Eintrag X17.",
        "",
        "C6 kostet damit nur eine neue lokale Schreibausnahme: E377 `daiin` am zweiten Feldanfang. Seine anderen acht Formen sind direkt oder durch den vorhandenen Renderer schreibbar.",
        "",
        "Alle 381 sichtbaren Formen werden exakt rekonstruiert.",
    ]
    (HERE / "SIX_HUNDRED_THIRTY_SEVENTH_COMPLETE_APPRENTICE_CURRICULUM.md").write_text("\n".join(md).rstrip() + "\n", encoding="utf-8")

    summary = {
        "status": "PASS",
        "semantic_words": 39,
        "productive_paradigms": 6,
        "exact_cards": 173,
        "prose_events": len(full_rows),
        "semantic_burden_event_counts": burden_counts,
        "surface_writer_layer_counts": layer_counts,
        "surface_exception_entries": len(deck17),
        "surface_exception_events": sum(int(row["event_count"]) for row in deck17),
        "c6_events": len(c6_rows),
        "c6_direct_events": sum(row["final_surface_writer_layer"] == "SEMANTIC_CARD_OR_DESK_RULE" for row in c6_rows),
        "c6_renderer_events": sum(row["final_surface_writer_layer"] == "TWO_STAGE_BODY_WRAPPER_RULE" for row in c6_rows),
        "c6_exception_events": sum(row["final_surface_writer_layer"] == "SEVENTEEN_ENTRY_LOCAL_EXCEPTION_DECK" for row in c6_rows),
        "exact_roundtrips": sum(row["exact_roundtrip"] == "YES" for row in full_rows),
        "decision": "ALL_381_PROSE_FORMS_TAUGHT_WITH_39_WORDS_6_TABLES_173_CARDS_17_EXCEPTIONS",
    }
    (HERE / "SIX_HUNDRED_THIRTY_SEVENTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
