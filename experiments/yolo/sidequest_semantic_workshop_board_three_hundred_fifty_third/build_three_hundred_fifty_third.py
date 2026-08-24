#!/usr/bin/env python3
"""Lay out all 173 cards on a six-slot by five-state workshop board."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
TRACE = ROOT / "experiments/yolo/sidequest_semantic_two_layer_production_rule_three_hundred_forty_sixth/THREE_HUNDRED_FORTY_SIXTH_381_TWO_LAYER_EVENT_TRACE.tsv"
MIXED = ROOT / "experiments/yolo/sidequest_semantic_mixed_workshop_edition_three_hundred_fortieth/THREE_HUNDRED_FORTIETH_381_MIXED_HAND_EVENTS.tsv"
CHART = ROOT / "experiments/yolo/sidequest_semantic_multiscribe_teaching_chart_three_hundred_thirty_eighth/THREE_HUNDRED_THIRTY_EIGHTH_COMPLETE_173_CARD_TEACHING_CHART.tsv"
PAIRS = ROOT / "experiments/yolo/sidequest_semantic_full_correction_index_three_hundred_fiftieth/THREE_HUNDRED_FIFTIETH_AMBIGUOUS_CARD_PAIRS.tsv"
MASTER = ROOT / "experiments/yolo/sidequest_semantic_twelve_card_master_tablet_three_hundred_fifty_first/THREE_HUNDRED_FIFTY_FIRST_TWELVE_CARD_MASTER_TABLET.tsv"

STATE_ORDER = ["M1_RAW_PART", "M2_PREPARATION", "M3_CLEAR_EXTRACT", "M4_MEASURED_PORTION", "M5_APPLICATION_ITEM"]
STATE_NAMES = {
    "M1_RAW_PART": "Rohteil",
    "M2_PREPARATION": "Ansatz",
    "M3_CLEAR_EXTRACT": "Klarauszug",
    "M4_MEASURED_PORTION": "Bemessene Portion",
    "M5_APPLICATION_ITEM": "Anwendungsposten",
}
SLOT_ORDER = ["S1_BEZUG_FOLGE", "S2_MATERIAL_MASS", "S3_PROZESS_TRANSFER", "S4_DAUER_ZUSTAND", "S5_ZIEL_ANWENDUNG", "S6_BEREIT_ABSCHLUSS"]


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def most_common(counter: Counter[str], order: list[str]) -> str:
    return min(counter, key=lambda item: (-counter[item], order.index(item)))


def main() -> None:
    trace = read_tsv(TRACE)
    mixed = {row["event_id"]: row for row in read_tsv(MIXED)}
    chart = {row["joint_tuple_id"]: row for row in read_tsv(CHART)}
    master = {row["joint_tuple_id"]: row for row in read_tsv(MASTER)}
    pair_source = read_tsv(PAIRS)

    pair_map = {}
    pair_rows = []
    for number, row in enumerate(pair_source, start=1):
        pair_id = f"P{number:02d}"
        tuple_ids = row["competing_joint_tuple_ids"].split("|")
        for tuple_id in tuple_ids:
            pair_map[tuple_id] = (pair_id, next(item for item in tuple_ids if item != tuple_id))
        pair_rows.append({
            "pair_id": pair_id,
            "atomic_value_de": row["atomic_value_de"],
            "slot_code": row["slot_code"],
            "joint_tuple_a": tuple_ids[0],
            "surface_palette_a": chart[tuple_ids[0]]["registered_surface_palette"],
            "joint_tuple_b": tuple_ids[1],
            "surface_palette_b": chart[tuple_ids[1]]["registered_surface_palette"],
            "teaching_rule_de": "Gleicher Werkstattwert und Slot; Besitzer oder rechte Folgekarte wählt die exakte Tafelkarte.",
        })

    event_state = {}
    current_state_by_record = {}
    for row in trace:
        record = row["record_unit_id"]
        if record not in current_state_by_record:
            current_state_by_record[record] = row["record_source_state_ids"].split("+")[0]
        if row["material_marker_state"] != "NONE":
            current_state_by_record[record] = row["material_marker_state"]
            state_source = "CARD_EXPLICIT_MARKER"
        else:
            state_source = "INHERITED_MATERIAL_THREAD"
        event_state[row["event_id"]] = (current_state_by_record[record], state_source)

    events_by_tuple: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in trace:
        tuple_id = mixed[row["event_id"]]["joint_tuple_id"]
        enriched = dict(row)
        enriched["state_id"], enriched["state_source"] = event_state[row["event_id"]]
        events_by_tuple[tuple_id].append(enriched)

    board = []
    for tuple_id, meta in chart.items():
        events = events_by_tuple[tuple_id]
        slot_counts = Counter(row["slot_code"] for row in events)
        state_counts = Counter(row["state_id"] for row in events)
        primary_slot = most_common(slot_counts, SLOT_ORDER)
        primary_state = most_common(state_counts, STATE_ORDER)
        explicit_states = Counter(row["state_id"] for row in events if row["state_source"] == "CARD_EXPLICIT_MARKER")
        pair_id, pair_mate = pair_map.get(tuple_id, ("NONE", "NONE"))
        master_row = master.get(tuple_id)
        board.append({
            "joint_tuple_id": tuple_id,
            "registered_surface_palette": meta["registered_surface_palette"],
            "atomic_value_de": meta["atomic_value_de"],
            "component_formula": meta["component_formula"],
            "deck_class": meta["deck_class"],
            "teaching_category": meta["teaching_category"],
            "primary_slot": primary_slot,
            "all_slots_with_counts": "|".join(f"{slot}:{slot_counts[slot]}" for slot in SLOT_ORDER if slot_counts[slot]),
            "primary_working_state": primary_state,
            "primary_working_state_de": STATE_NAMES[primary_state],
            "all_states_with_counts": "|".join(f"{state}:{state_counts[state]}" for state in STATE_ORDER if state_counts[state]),
            "explicit_marker_states": "|".join(f"{state}:{explicit_states[state]}" for state in STATE_ORDER if explicit_states[state]) if explicit_states else "NONE__THREAD_CONTEXT_ONLY",
            "events": len(events),
            "records": "|".join(sorted({row["record_unit_id"] for row in events})),
            "pages": "|".join(sorted({row["page"] for row in events})),
            "ambiguous_pair_id": pair_id,
            "pair_mate_joint_tuple_id": pair_mate,
            "master_tablet_no": master_row["tablet_no"] if master_row else "NONE",
            "master_pin_owner": master_row["picture_or_station_owner"] if master_row else "NONE",
            "board_address": f"{primary_state}__{primary_slot}",
        })
    board.sort(key=lambda row: (STATE_ORDER.index(row["primary_working_state"]), SLOT_ORDER.index(row["primary_slot"]), row["registered_surface_palette"]))
    write_tsv(
        HERE / "THREE_HUNDRED_FIFTY_THIRD_173_CARD_WORKSHOP_BOARD.tsv",
        board,
        ["joint_tuple_id", "registered_surface_palette", "atomic_value_de", "component_formula", "deck_class", "teaching_category", "primary_slot", "all_slots_with_counts", "primary_working_state", "primary_working_state_de", "all_states_with_counts", "explicit_marker_states", "events", "records", "pages", "ambiguous_pair_id", "pair_mate_joint_tuple_id", "master_tablet_no", "master_pin_owner", "board_address"],
    )

    cell_rows = []
    for state in STATE_ORDER:
        for slot in SLOT_ORDER:
            cards = [row for row in board if row["primary_working_state"] == state and row["primary_slot"] == slot]
            cell_rows.append({
                "state_id": state,
                "state_name_de": STATE_NAMES[state],
                "slot_code": slot,
                "board_address": f"{state}__{slot}",
                "card_types": len(cards),
                "events": sum(int(row["events"]) for row in cards),
                "master_cards": sum(row["master_tablet_no"] != "NONE" for row in cards),
                "pair_cards": sum(row["ambiguous_pair_id"] != "NONE" for row in cards),
                "surface_palettes": " || ".join(row["registered_surface_palette"] for row in cards) if cards else "EMPTY",
                "atomic_values_de": " || ".join(row["atomic_value_de"] for row in cards) if cards else "EMPTY",
            })
    write_tsv(HERE / "THREE_HUNDRED_FIFTY_THIRD_THIRTY_BOARD_CELLS.tsv", cell_rows,
              ["state_id", "state_name_de", "slot_code", "board_address", "card_types", "events", "master_cards", "pair_cards", "surface_palettes", "atomic_values_de"])
    write_tsv(HERE / "THREE_HUNDRED_FIFTY_THIRD_FOURTEEN_PAIR_PLACARDS.tsv", pair_rows,
              ["pair_id", "atomic_value_de", "slot_code", "joint_tuple_a", "surface_palette_a", "joint_tuple_b", "surface_palette_b", "teaching_rule_de"])

    pinned = [{
        "tablet_no": row["tablet_no"],
        "joint_tuple_id": tuple_id,
        "surface": row["whole_card_surface"],
        "work_value_de": row["concrete_work_value_de"],
        "pin_owner": row["picture_or_station_owner"],
        "board_address": next(item["board_address"] for item in board if item["joint_tuple_id"] == tuple_id),
        "mnemonic_de": row["master_mnemonic_de"],
    } for tuple_id, row in master.items()]
    write_tsv(HERE / "THREE_HUNDRED_FIFTY_THIRD_TWELVE_PINNED_MASTER_CARDS.tsv", pinned,
              ["tablet_no", "joint_tuple_id", "surface", "work_value_de", "pin_owner", "board_address", "mnemonic_de"])

    lines = [
        "# Das 173-Karten-Werkstattbrett",
        "",
        "Jede Karte hängt in einer Hauptzelle aus laufendem Stoffzustand und",
        "Arbeitsslot. Weitere belegte Zustände und Slots bleiben auf der Rückseite.",
        "Zwölf goldene Randkarten tragen ihren Bildbesitzer; vierzehn Doppelpaare",
        "hängen unmittelbar nebeneinander.",
        "",
    ]
    for state in STATE_ORDER:
        lines.extend([f"## {STATE_NAMES[state]}", ""])
        for slot in SLOT_ORDER:
            cell = next(row for row in cell_rows if row["state_id"] == state and row["slot_code"] == slot)
            lines.append(f"- **{slot}:** {cell['card_types']} Karten / {cell['events']} Einsätze — {cell['surface_palettes']}")
        lines.append("")
    (HERE / "THREE_HUNDRED_FIFTY_THIRD_WORKSHOP_BOARD.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")

    report = """# Pass 353 — das vollständige Werkstattbrett

Alle 173 Karten stehen jetzt auf einem einzigen benutzbaren Brett mit 30 Zellen:
fünf laufende Stoffzustände kreuzen sechs Arbeitsslots. Die Zustandsreihe sagt,
an welchem Stofffaden die Karte am häufigsten benutzt wird; sie behauptet nicht,
dass jede Operationskarte selbst diesen Stoff bedeutet. Mehrfachbelegungen
stehen mit Zählung auf der Kartenrückseite.

Vierzehn gleichwertige Doppelpaare hängen nebeneinander. Zwölf gelernte
Ganzkarten werden zusätzlich an ihren Bild-/Stationsbesitzer gepinnt. Damit kann
ein Schreiber vom Arbeitsauftrag zur Kartenfamilie, vom Stofffaden zur Brettreihe
und vom lokalen Bild zur exakten Ausnahme gelangen.

Als Nächstes sollte ein kompletter neuer Arbeitsauftrag nur mit diesem Brett
gesetzt werden: ein Herbal-Auszug, der in einer Bio-Station zu einer bemessenen
Anwendung wird. Danach wird geprüft, wo der Schreiber trotzdem zur laufenden
Seitenvorlage greifen muss.
"""
    (HERE / "THREE_HUNDRED_FIFTY_THIRD_REPORT.md").write_text(report, encoding="utf-8")

    summary = {
        "status": "PASS",
        "card_types": len(board),
        "events": sum(int(row["events"]) for row in board),
        "board_cells": len(cell_rows),
        "occupied_cells": sum(int(row["card_types"]) > 0 for row in cell_rows),
        "ambiguous_pairs": len(pair_rows),
        "pair_cards": len(pair_map),
        "pinned_master_cards": len(pinned),
        "states": len(STATE_ORDER),
        "slots": len(SLOT_ORDER),
    }
    (HERE / "THREE_HUNDRED_FIFTY_THIRD_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
