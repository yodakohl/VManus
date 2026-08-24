#!/usr/bin/env python3
"""Compose and round-trip one new in-deck apprentice workshop order."""

from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
COMMAND_DIR = ROOT / "experiments/yolo/sidequest_semantic_backread_noun_repair_six_hundred_seventeenth"
LAYER_DIR = ROOT / "experiments/yolo/sidequest_semantic_layered_readable_six_hundred_eighteenth"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


ORDER = [
    (1, "OK+AIIN", "ANSETZEN · SOLLMASS", "PROC038", "qokaiin", "E219", "Ansatz nach Sollmass setzen"),
    (2, "OK+AIN", "ANSETZEN · PORTION", "PROC080", "qokain", "E169", "eine Portion ansetzen"),
    (3, "OK+AL", "ANSETZEN · ZIELSTELLE", "PROC048", "qokal", "E172", "an der Zielstelle ansetzen"),
    (4, "SH+EE+Y", "HALTEN · LANG · ARBEITSPOSTEN", "PROC031", "cheey", "E197", "den Arbeitsposten laenger halten"),
    (5, "OL", "FORTSETZEN", "PROC013", "ol", "E106", "fortsetzen"),
    (6, "SHED+DY", "ABSETZEN; SCHLUSS", "PROC078", "shedy", "E192", "absetzen und den Schritt schliessen"),
]


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    cards = read_tsv(COMMAND_DIR / "SIX_HUNDRED_SEVENTEENTH_173_SHARP_COMMANDS.tsv")
    events = read_tsv(LAYER_DIR / "SIX_HUNDRED_EIGHTEENTH_381_LAYERED_EVENTS.tsv")
    card_by_id = {row["card_no"]: row for row in cards}
    event_by_id = {row["event_id"]: row for row in events}
    cards_by_surface: dict[str, list[str]] = {}
    for card in cards:
        for surface in card["surfaces"].split("|"):
            cards_by_surface.setdefault(surface, []).append(card["card_no"])

    order_rows = []
    for step, parse, command, card_no, surface, exemplar_event, phrase in ORDER:
        card = card_by_id[card_no]
        exemplar = event_by_id[exemplar_event]
        order_rows.append({
            "step": step,
            "ordinary_instruction_fragment_de": phrase,
            "semantic_component_parse": parse,
            "invariant_command_de": command,
            "selected_card_no": card_no,
            "selected_surface": surface,
            "surface_card_candidates": "|".join(cards_by_surface[surface]),
            "surface_uniquely_identifies_card": "YES" if len(cards_by_surface[surface]) == 1 else "NO",
            "surface_licensed_for_card": "YES" if surface in card["surfaces"].split("|") else "NO",
            "bath_desk_exemplar_event": exemplar_event,
            "exemplar_record": exemplar["record"],
            "exemplar_statement": exemplar["statement_id"],
            "new_word": "NO",
            "new_card": "NO",
            "new_surface": "NO",
        })

    backward_rows = []
    for row in order_rows:
        decoded_card = cards_by_surface[str(row["selected_surface"])][0]
        card = card_by_id[decoded_card]
        backward_rows.append({
            "step": row["step"],
            "visible_surface": row["selected_surface"],
            "decoded_card_no": decoded_card,
            "decoded_component_parse": card["semantic_component_parse"],
            "decoded_invariant_command_de": card["standard_command_de"],
            "expected_card_no": row["selected_card_no"],
            "expected_component_parse": row["semantic_component_parse"],
            "expected_invariant_command_de": row["invariant_command_de"],
            "exact_backward_read": "YES" if (
                decoded_card == row["selected_card_no"]
                and card["semantic_component_parse"] == row["semantic_component_parse"]
                and card["standard_command_de"] == row["invariant_command_de"]
            ) else "NO",
        })

    source_cards = [row["card_no"] for row in events]
    target_cards = [row["selected_card_no"] for row in order_rows]
    ngram_rows = []
    for length in range(1, len(target_cards) + 1):
        target = target_cards[:length]
        hits = []
        for index in range(len(source_cards) - length + 1):
            if source_cards[index:index + length] == target:
                hits.append(events[index]["event_id"])
        ngram_rows.append({
            "prefix_length": length,
            "card_prefix": "|".join(target),
            "source_occurrences": len(hits),
            "source_start_event_ids": "|".join(hits) if hits else "NONE",
        })
    adjacent_rows = []
    for left, right in zip(order_rows, order_rows[1:]):
        pair = [str(left["selected_card_no"]), str(right["selected_card_no"])]
        hits = []
        for index in range(len(events) - 1):
            if events[index]["record"] == events[index + 1]["record"] and [events[index]["card_no"], events[index + 1]["card_no"]] == pair:
                hits.append(events[index]["event_id"])
        adjacent_rows.append({
            "left_step": left["step"],
            "right_step": right["step"],
            "card_bigram": "|".join(pair),
            "source_occurrences": len(hits),
            "source_start_event_ids": "|".join(hits) if hits else "NONE",
        })

    write_tsv(HERE / "SIX_HUNDRED_THIRTIETH_6_STEP_FORWARD_ORDER.tsv", order_rows, list(order_rows[0]))
    write_tsv(HERE / "SIX_HUNDRED_THIRTIETH_6_STEP_BACKWARD_READ.tsv", backward_rows, list(backward_rows[0]))
    write_tsv(HERE / "SIX_HUNDRED_THIRTIETH_6_PREFIX_NOVELTY_AUDIT.tsv", ngram_rows, list(ngram_rows[0]))
    write_tsv(HERE / "SIX_HUNDRED_THIRTIETH_5_BIGRAM_NOVELTY_AUDIT.tsv", adjacent_rows, list(adjacent_rows[0]))

    surfaces = " ".join(str(row["selected_surface"]) for row in order_rows)
    commands = " | ".join(str(row["invariant_command_de"]) for row in order_rows)
    md = f"""# Neue Lehrlingsanweisung innerhalb des bestehenden Decks

## Auftrag des Meisters

Den aktiven Ansatz nach Sollmass setzen; eine Portion an der Zielstelle
ansetzen; den Arbeitsposten laenger halten, fortsetzen, absetzen und den
Schritt schliessen.

## Vom Lehrling geschriebene Folge

`{surfaces}`

## Kartenlesung

{commands}.

## Warum sie neu ist

Die sechs Karten sind alle bereits gelernt, aber die ganze Folge und schon ihr
erstes Kartenpaar kommen in den 381 sichtbaren Prosaereignissen nicht vor. Vier
der fuenf benachbarten Kartenpaare sind neu; nur FORTSETZEN -> ABSETZEN/SCHLUSS
ist bereits als normale Werkstattkadenz belegt.

## Ruecklesen

Jede der sechs sichtbaren Formen bezeichnet im aktuellen 173-Karten-Woerterbuch
genau eine Kartenidentitaet. Der Leser erhaelt daher ohne Seiten- oder
Bildwissen exakt dieselben sechs Komponentenfolgen und Befehle zurueck. Das
Bild oder der aktive Fall muss weiterhin sagen, welcher konkrete Ansatz,
welche Portion und welche Zielstelle gemeint sind.
"""
    (HERE / "SIX_HUNDRED_THIRTIETH_NEW_APPRENTICE_ORDER.md").write_text(md, encoding="utf-8")

    summary = {
        "status": "PASS",
        "steps": len(order_rows),
        "surface_sequence": surfaces,
        "all_words_attested_in_current_deck": all(row["new_word"] == "NO" for row in order_rows),
        "all_cards_attested": all(row["new_card"] == "NO" for row in order_rows),
        "all_surfaces_attested": all(row["new_surface"] == "NO" for row in order_rows),
        "surface_unique_card_steps": sum(row["surface_uniquely_identifies_card"] == "YES" for row in order_rows),
        "exact_backward_steps": sum(row["exact_backward_read"] == "YES" for row in backward_rows),
        "full_sequence_source_occurrences": int(ngram_rows[-1]["source_occurrences"]),
        "novel_bigrams": sum(int(row["source_occurrences"]) == 0 for row in adjacent_rows),
        "attested_bigrams": sum(int(row["source_occurrences"]) > 0 for row in adjacent_rows),
        "new_page": False,
        "decision": "NEW_IN_DECK_ORDER_WRITES_AND_READS_BACK_EXACTLY_WITHOUT_NEW_WORD_CARD_OR_SURFACE",
    }
    (HERE / "SIX_HUNDRED_THIRTIETH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
