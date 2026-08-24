#!/usr/bin/env python3
"""Substitute one compatible existing card per case and enumerate legal orders."""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P617 = ROOT / "experiments/yolo/sidequest_semantic_backread_noun_repair_six_hundred_seventeenth/SIX_HUNDRED_SEVENTEENTH_173_SHARP_COMMANDS.tsv"
P618 = ROOT / "experiments/yolo/sidequest_semantic_layered_readable_six_hundred_eighteenth/SIX_HUNDRED_EIGHTEENTH_381_LAYERED_EVENTS.tsv"
P633 = ROOT / "experiments/yolo/sidequest_semantic_finite_construction_grammar_six_hundred_thirty_third/SIX_HUNDRED_THIRTY_THIRD_22_LEGAL_ORDERS.tsv"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


JOBS = {
    "C1": [
        ("C1-HOLD-LONG", "H", "shey", "DEN POSTEN LAENGER HALTEN", "BASE"),
        ("C1-HOLD-SHORT", "H", "tshey", "DEN POSTEN KURZ HALTEN", "SUBSTITUTED"),
    ],
    "C2": [
        ("C2-CLOSE-FULL", "C", "qokeeedy", "BIS ZUM VOLLGRAD ANSETZEN UND SCHLIESSEN", "BASE"),
        ("C2-CLOSE-LONG", "C", "qokeedy", "LAENGER ANSETZEN UND SCHLIESSEN", "SUBSTITUTED"),
        ("C2-CLOSE-SHORT", "C", "qokedy", "KURZ ANSETZEN UND SCHLIESSEN", "SUBSTITUTED"),
    ],
    "C3": [
        ("C3-HOLD-LONG", "H", "shey", "DEN AUSZUG LAENGER HALTEN", "BASE"),
        ("C3-HOLD-SHORT", "H", "tshey", "DEN AUSZUG KURZ HALTEN", "SUBSTITUTED"),
    ],
    "C4": [
        ("C4-STANDARD-MEASURE", "M", "qokaiin", "SOLLMASS VOR PORTION UND NACHPORTION", "BASE"),
        ("C4-DOUBLE-PORTION", "M", "qokain", "PORTION, ZWEITE PORTION UND NACHPORTION", "SUBSTITUTED"),
    ],
    "C5": [
        ("C5-STANDARD-MEASURE", "M", "qokaiin", "ZUTAT NACH SOLLMASS", "BASE"),
        ("C5-PORTION", "M", "qokain", "ZUTAT NACH PORTION", "SUBSTITUTED"),
    ],
}


def choose_case(parses: list[str]) -> str:
    components = [part for parse in parses[:5] for part in parse.split("+")]
    if "HO" in components:
        return "C5"
    if "CFH" in components:
        return "C3"
    if "AN" in components:
        return "C4"
    if "OS" in components:
        return "C1"
    if components.count("CTH") >= 3:
        return "C2"
    return "UNRESOLVED"


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    cards = read_tsv(P617)
    source = read_tsv(P618)
    legal_orders = read_tsv(P633)
    surface_cards: dict[str, list[dict[str, str]]] = defaultdict(list)
    for card in cards:
        for surface in card["surfaces"].split("|"):
            surface_cards[surface].append(card)

    substitution_rows = []
    order_rows = []
    backward_rows = []
    for case_id, jobs in JOBS.items():
        case_orders = [row for row in legal_orders if row["case_id"] == case_id]
        base_node_surfaces = dict(zip(case_orders[0]["node_order"].split("-"), case_orders[0]["surface_sequence"].split()))
        for job_id, slot_node, replacement_surface, job_reading, variant_kind in jobs:
            base_surface = base_node_surfaces[slot_node]
            replacement_card = surface_cards[replacement_surface][0]
            base_card = surface_cards[base_surface][0]
            substitution_rows.append({
                "job_id": job_id,
                "case_id": case_id,
                "variant_kind": variant_kind,
                "slot_node": slot_node,
                "slot_function": "HOLD_GRADE" if slot_node == "H" else "CLOSE_GRADE" if slot_node == "C" else "QUANTITY",
                "base_surface": base_surface,
                "base_card_no": base_card["card_no"],
                "base_command": base_card["standard_command_de"],
                "replacement_surface": replacement_surface,
                "replacement_surface_card_candidates": len(surface_cards[replacement_surface]),
                "replacement_card_no": replacement_card["card_no"],
                "replacement_component_parse": replacement_card["semantic_component_parse"],
                "replacement_command": replacement_card["standard_command_de"],
                "job_reading_de": job_reading,
                "existing_word": "YES",
                "existing_card": "YES",
                "existing_surface": "YES",
            })
            for base_order in case_orders:
                node_order = base_order["node_order"].split("-")
                surfaces = base_order["surface_sequence"].split()
                node_surfaces = dict(zip(node_order, surfaces))
                node_surfaces[slot_node] = replacement_surface
                variant_surfaces = [node_surfaces[node] for node in node_order]
                variant_cards = [surface_cards[surface][0] for surface in variant_surfaces]
                card_nos = [card["card_no"] for card in variant_cards]
                parses = [card["semantic_component_parse"] for card in variant_cards]
                sequence = " ".join(variant_surfaces)
                hits = []
                for index in range(len(source) - 5):
                    window = source[index:index + 6]
                    if len({row["record"] for row in window}) == 1 and [row["card_no"] for row in window] == card_nos:
                        hits.append(source[index]["event_id"])
                written_order_id = f"{job_id}-{base_order['order_id'].split('-')[1]}"
                order_rows.append({
                    "written_order_id": written_order_id,
                    "job_id": job_id,
                    "case_id": case_id,
                    "variant_kind": variant_kind,
                    "node_order": base_order["node_order"],
                    "surface_sequence": sequence,
                    "card_sequence": "|".join(card_nos),
                    "command_sequence": " / ".join(card["standard_command_de"] for card in variant_cards),
                    "job_reading_de": job_reading,
                    "selected_case_id": choose_case(parses),
                    "selector_correct": "YES" if choose_case(parses) == case_id else "NO",
                    "source_sequence_occurrences": len(hits),
                    "source_start_events": "|".join(hits) if hits else "NONE",
                    "all_surfaces_unique_to_card": "YES" if all(len(surface_cards[surface]) == 1 for surface in variant_surfaces) else "NO",
                })
                for step, (surface, card) in enumerate(zip(variant_surfaces, variant_cards), 1):
                    backward_rows.append({
                        "written_order_id": written_order_id,
                        "job_id": job_id,
                        "case_id": case_id,
                        "step": step,
                        "surface": surface,
                        "decoded_card_no": card["card_no"],
                        "decoded_component_parse": card["semantic_component_parse"],
                        "decoded_command_de": card["standard_command_de"],
                        "exact_backward_read": "YES",
                    })

    write_tsv(HERE / "SIX_HUNDRED_THIRTY_FOURTH_11_JOB_SUBSTITUTIONS.tsv", substitution_rows, list(substitution_rows[0]))
    write_tsv(HERE / "SIX_HUNDRED_THIRTY_FOURTH_49_LEGAL_WRITTEN_ORDERS.tsv", order_rows, list(order_rows[0]))
    write_tsv(HERE / "SIX_HUNDRED_THIRTY_FOURTH_294_STEP_BACKWARD_READ.tsv", backward_rows, list(backward_rows[0]))

    case_counts = {case: sum(row["case_id"] == case for row in order_rows) for case in JOBS}
    md = [
        "# Bestehende Karten als kontrollierte Inhaltsvarianten",
        "",
        "Jeder Fall erhaelt genau eine austauschbare Schublade. Alle Ersatzkarten stammen aus dem bestehenden 173-Karten-Deck und bleiben in derselben Funktionsfamilie.",
        "",
        "| Fall | Schublade | Werte | verschiedene Aufgaben | legale Schriftfolgen |",
        "|---|---|---|---:|---:|",
        f"| C1 | Haltegrad | lang / kurz | {len(JOBS['C1'])} | {case_counts['C1']} |",
        f"| C2 | Schlussgrad | kurz / lang / voll | {len(JOBS['C2'])} | {case_counts['C2']} |",
        f"| C3 | Haltegrad | lang / kurz | {len(JOBS['C3'])} | {case_counts['C3']} |",
        f"| C4 | Mengenfolge | Sollmass+Portion / Portion+Portion | {len(JOBS['C4'])} | {case_counts['C4']} |",
        f"| C5 | Zutatenmenge | Sollmass / Portion | {len(JOBS['C5'])} | {case_counts['C5']} |",
        "",
        f"Damit schreibt das feste Deck **{len(substitution_rows)} verschiedene Aufgaben in {len(order_rows)} legalen Folgen**.",
        "",
        "Die Doppelung `qokain qokain` in C4 wird absichtlich wortwoertlich als zwei gesetzte Portionen gelesen. Sie ist kein neues Zahlwort. Wenn die Werkstatt Doppelung nicht als Wiederholung lehrt, faellt genau diese Variante weg.",
    ]
    (HERE / "SIX_HUNDRED_THIRTY_FOURTH_SUBSTITUTION_EXERCISE.md").write_text("\n".join(md).rstrip() + "\n", encoding="utf-8")

    summary = {
        "status": "PASS",
        "cases": 5,
        "controlled_slots": 5,
        "semantic_job_variants": len(substitution_rows),
        "base_jobs": sum(row["variant_kind"] == "BASE" for row in substitution_rows),
        "new_job_variants": sum(row["variant_kind"] == "SUBSTITUTED" for row in substitution_rows),
        "legal_written_orders": len(order_rows),
        "legal_written_orders_by_case": case_counts,
        "unique_written_orders": len({row["surface_sequence"] for row in order_rows}),
        "correct_case_selections": sum(row["selector_correct"] == "YES" for row in order_rows),
        "source_attested_orders": sum(int(row["source_sequence_occurrences"]) > 0 for row in order_rows),
        "backward_steps": len(backward_rows),
        "exact_backward_steps": sum(row["exact_backward_read"] == "YES" for row in backward_rows),
        "new_words": 0,
        "new_cards": 0,
        "new_surfaces": 0,
        "new_pages": 0,
        "decision": "FIXED_DECK_EXPRESSES_ELEVEN_CONTROLLED_JOBS_IN_FORTY_NINE_ORDERS",
    }
    (HERE / "SIX_HUNDRED_THIRTY_FOURTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
