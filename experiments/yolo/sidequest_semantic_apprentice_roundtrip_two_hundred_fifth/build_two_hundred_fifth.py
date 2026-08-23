#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
BASE = ROOT / "experiments/yolo/sidequest_semantic_vocabulary_granularity_two_hundred_third"
DICT = BASE / "TWO_HUNDRED_THIRD_173_CARD_COMPACT_DICTIONARY.tsv"

FIELDS = [
    ("N01", "CH", "Eine Wurzel im Aufnahmegefäß mit weiterer Zutat als Ansatz auf Sollmaß bringen, kurz wärmen und kurz absetzen; Schluss.",
     ["MC071", "MC159", "MC034", "MC080", "MC039", "MC147", "MC128"]),
    ("N02", "D", "Vom vorigen Ansatz davon eine Portion nehmen, dorthin bringen und überführen; Schluss.",
     ["MC142", "MC055", "MC105", "MC154", "MC025"]),
    ("N03", "O", "Denselben Ansatz mit einem weiteren Anteil weiterführen, weiterbearbeiten und bereit halten.",
     ["MC157", "MC097", "MC153", "MC103", "MC161"]),
    ("N04", "Q", "Für den Folgeansatz einen Anteil zugeben, bemessen, dorthin einsetzen und einführen; Schluss.",
     ["MC013", "MC017", "MC120", "MC040", "MC005"]),
    ("N05", "S", "Auswringen, die Stehzeit halten, nachseihen, den Klarlauf lange sammeln; Schluss.",
     ["MC129", "MC111", "MC156", "MC119", "MC045"]),
    ("N06", "Q", "Frischwasser zugeben; danach dorthin durchleiten, lange einwirken lassen und weiter übertragen; Schluss.",
     ["MC138", "MC093", "MC035", "MC002", "MC057"]),
]


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def second_hand_surface(card: dict[str, str]) -> str:
    surfaces = card["registered_surfaces"].split("|")
    return surfaces[-1]


def main() -> None:
    dictionary_rows = read(DICT)
    dictionary = {row["master_card_id"]: row for row in dictionary_rows}
    surface_to_card: dict[str, str] = {}
    for row in dictionary_rows:
        for surface in row["registered_surfaces"].split("|"):
            surface_to_card[surface] = row["master_card_id"]

    token_rows: list[dict[str, object]] = []
    field_rows: list[dict[str, object]] = []
    sequence = 0
    for field_id, mode, instruction, card_ids in FIELDS:
        hand_a: list[str] = []
        hand_b: list[str] = []
        values: list[str] = []
        for position, card_id in enumerate(card_ids, 1):
            sequence += 1
            card = dictionary[card_id]
            surface_a = card["master_form"]
            surface_b = second_hand_surface(card)
            decoded_card = surface_to_card[surface_b]
            decoded_value = dictionary[decoded_card]["current_value_de"]
            hand_a.append(surface_a)
            hand_b.append(surface_b)
            values.append(decoded_value)
            token_rows.append({
                "sequence": sequence,
                "field_id": field_id,
                "field_mode": mode,
                "position": position,
                "intended_card_id": card_id,
                "hand_a_surface": surface_a,
                "hand_b_surface": surface_b,
                "surface_changed": "YES" if surface_a != surface_b else "NO",
                "decoded_card_id": decoded_card,
                "intended_value_de": card["current_value_de"],
                "decoded_value_de": decoded_value,
                "learning_mode": "GANZKARTE" if card["component_class"] == "MEMORIZED_WHOLE_CARD" else "KOMPONENTEN",
                "readback_status": "EXACT" if card_id == decoded_card and card["current_value_de"] == decoded_value else "ERROR",
            })
        field_rows.append({
            "field_id": field_id,
            "field_mode": mode,
            "source_instruction_de": instruction,
            "hand_a_text": " ".join(hand_a),
            "hand_b_text": " ".join(hand_b),
            "literal_readback_de": " | ".join(values),
            "token_count": len(card_ids),
            "whole_card_count": sum(dictionary[card_id]["component_class"] == "MEMORIZED_WHOLE_CARD" for card_id in card_ids),
            "productive_card_count": sum(dictionary[card_id]["component_class"] != "MEMORIZED_WHOLE_CARD" for card_id in card_ids),
        })
    write(OUT / "TWO_HUNDRED_FIFTH_32_TOKEN_ROUNDTRIP.tsv", token_rows)
    write(OUT / "TWO_HUNDRED_FIFTH_SIX_FIELD_WORKSHOP_TEXT.tsv", field_rows)

    summary = {
        "dictionary_source_sha256": hashlib.sha256(DICT.read_bytes()).hexdigest(),
        "fields": len(field_rows),
        "tokens": len(token_rows),
        "whole_card_tokens": sum(row["learning_mode"] == "GANZKARTE" for row in token_rows),
        "productive_tokens": sum(row["learning_mode"] == "KOMPONENTEN" for row in token_rows),
        "hand_b_surface_changes": sum(row["surface_changed"] == "YES" for row in token_rows),
        "exact_readbacks": sum(row["readback_status"] == "EXACT" for row in token_rows),
        "mode_distribution": dict(Counter(row["field_mode"] for row in field_rows)),
        "new_manuscript_data_created": False,
        "sealed_pages_accessed": False,
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
