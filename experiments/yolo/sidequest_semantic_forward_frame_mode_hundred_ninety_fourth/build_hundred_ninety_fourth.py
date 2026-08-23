#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
DICTIONARY = ROOT / "experiments/yolo/sidequest_semantic_ten_page_master_edition_hundred_seventy_fifth/HUNDRED_SEVENTY_FIFTH_173_CARD_DICTIONARY.tsv"


PLAN = [
    ("N1", "CH", "GRUNDZUBEREITUNG_AUFBAU", "OPEN", [
        ("MC080", "chor"), ("MC039", "chaiin"), ("MC147", "cheky"), ("MC153", "cheol"), ("MC123", "chey"),
    ]),
    ("N2", "D", "VOM_VORIGEN_UEBERNEHMEN", "OPEN", [
        ("MC142", "dchol"), ("MC071", "dchey"), ("MC039", "daiin"), ("MC154", "dal"), ("MC055", "dar"),
    ]),
    ("N3", "O", "IM_AKTIVEN_ANSATZ_FORTSETZEN", "CLOSED", [
        ("MC080", "or"), ("MC017", "okain"), ("MC002", "okeey"), ("MC153", "ol"), ("MC028", "olchedy"),
    ]),
    ("N4", "Q", "BESTIMMTEN_TEILSCHRITT_AKTIVIEREN", "CLOSED", [
        ("MC120", "qokaiin"), ("MC040", "qokal"), ("MC002", "qokeey"), ("MC026", "qoky"), ("MC083", "qokedy"),
    ]),
    ("N5", "S", "ZUSTAND_ODER_ERGEBNIS_EINTRAGEN", "CLOSED", [
        ("MC039", "saiin"), ("MC113", "shedal"), ("MC137", "shecthy"), ("MC161", "shcthy"), ("MC025", "schedy"),
    ]),
]


FIELD_TRANSLATIONS = {
    "N1": "Den Grundansatz aufbauen: Sollmaß nehmen, kurz wärmen, weiterführen und beim aktuellen Posten belassen.",
    "N2": "Vom vorigen Ansatz einen Grundteil im Sollmaß übernehmen, dorthin bringen und davon weiternehmen.",
    "N3": "Im Ansatz fortfahren: einen Anteil zugeben, lange einwirken lassen, weiterführen und den Schritt schließen.",
    "N4": "Den bestimmten Teilschritt aktivieren: bemessen, am Ziel einsetzen, lange einwirken lassen, einsetzen und kurz abschließen.",
    "N5": "Sollmaß und Zielzustand eintragen, kurz vorbereiten, als bereit markieren und überführen; Schluss.",
}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def matches_mode(surface: str, mode: str) -> bool:
    if mode == "S":
        return surface.startswith("s") or surface.startswith("sh")
    return surface.startswith(mode.lower())


def main() -> None:
    dictionary_rows = read(DICTIONARY)
    dictionary = {row["master_card_id"]: row for row in dictionary_rows}
    surface_index: dict[str, list[str]] = defaultdict(list)
    for row in dictionary_rows:
        for surface in row["registered_surfaces"].split("|"):
            surface_index[surface].append(row["master_card_id"])

    token_rows: list[dict[str, object]] = []
    field_rows: list[dict[str, object]] = []
    token_number = 0
    for field_id, mode, intent, closure, cards in PLAN:
        start = token_number + 1
        for position, (card_id, surface) in enumerate(cards, 1):
            token_number += 1
            card = dictionary[card_id]
            token_rows.append(
                {
                    "token_order": token_number,
                    "field_id": field_id,
                    "field_position": position,
                    "field_mode": mode,
                    "field_intent_de": intent,
                    "master_card_id": card_id,
                    "surface": surface,
                    "portable_value_de": card["portable_card_value_de"],
                    "surface_matches_mode": "YES" if matches_mode(surface, mode) else "NO",
                    "surface_registered_for_card": "YES" if surface in card["registered_surfaces"].split("|") else "NO",
                    "surface_uniquely_reads_card": "YES" if surface_index[surface] == [card_id] else "NO",
                    "is_field_final": "YES" if position == len(cards) else "NO",
                    "field_closure": closure,
                }
            )
        field_rows.append(
            {
                "field_id": field_id,
                "field_mode": mode,
                "field_intent_de": intent,
                "closure": closure,
                "token_start": start,
                "token_end": token_number,
                "surface_sequence": " ".join(surface for _card, surface in cards),
                "card_sequence": " ".join(card for card, _surface in cards),
                "literal_value_sequence": " | ".join(dictionary[card]["portable_card_value_de"] for card, _surface in cards),
                "fluent_translation_de": FIELD_TRANSLATIONS[field_id],
            }
        )
    write(OUT / "HUNDRED_NINETY_FOURTH_25_TOKEN_MODE_INSTRUCTION.tsv", token_rows)
    write(OUT / "HUNDRED_NINETY_FOURTH_5_FIELD_MODE_PLAN.tsv", field_rows)

    readback_rows = []
    for row in token_rows:
        decoded_ids = surface_index[str(row["surface"])]
        decoded_id = decoded_ids[0] if len(decoded_ids) == 1 else "AMBIGUOUS"
        readback_rows.append(
            {
                "token_order": row["token_order"],
                "surface": row["surface"],
                "decoded_card_id": decoded_id,
                "intended_card_id": row["master_card_id"],
                "card_readback_exact": "YES" if decoded_id == row["master_card_id"] else "NO",
                "decoded_value_de": dictionary[decoded_id]["portable_card_value_de"] if decoded_id != "AMBIGUOUS" else "MEHRDEUTIG",
                "intended_mode": row["field_mode"],
                "mode_readback_exact": "YES" if matches_mode(str(row["surface"]), str(row["field_mode"])) else "NO",
            }
        )
    write(OUT / "HUNDRED_NINETY_FOURTH_25_TOKEN_SURFACE_READBACK.tsv", readback_rows)

    repeated_rows: list[dict[str, object]] = []
    used_by_card: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in token_rows:
        used_by_card[str(row["master_card_id"])].append(row)
    for card_id, selected in used_by_card.items():
        if len(selected) > 1:
            repeated_rows.append(
                {
                    "master_card_id": card_id,
                    "portable_value_de": dictionary[card_id]["portable_card_value_de"],
                    "modes": "|".join(str(row["field_mode"]) for row in selected),
                    "surfaces": "|".join(str(row["surface"]) for row in selected),
                    "same_card_value_preserved": "YES" if len({row["portable_value_de"] for row in selected}) == 1 else "NO",
                }
            )
    write(OUT / "HUNDRED_NINETY_FOURTH_REPEATED_CARD_MODE_ALLOMORPHS.tsv", repeated_rows)

    summary = {
        "dictionary_sha256": hashlib.sha256(DICTIONARY.read_bytes()).hexdigest(),
        "fields": len(field_rows),
        "tokens": len(token_rows),
        "modes": [row[1] for row in PLAN],
        "open_fields": sum(row[3] == "OPEN" for row in PLAN),
        "closed_fields": sum(row[3] == "CLOSED" for row in PLAN),
        "distinct_cards": len({row["master_card_id"] for row in token_rows}),
        "repeated_cross_mode_cards": len(repeated_rows),
        "registered_surfaces": sum(row["surface_registered_for_card"] == "YES" for row in token_rows),
        "unique_surface_readbacks": sum(row["card_readback_exact"] == "YES" for row in readback_rows),
        "mode_readbacks": sum(row["mode_readback_exact"] == "YES" for row in readback_rows),
        "sealed_pages_accessed": False,
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
