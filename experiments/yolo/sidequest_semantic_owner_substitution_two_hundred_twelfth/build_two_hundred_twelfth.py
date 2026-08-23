#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
BASE = ROOT / "experiments/yolo/sidequest_semantic_vocabulary_granularity_two_hundred_third"
DICT = BASE / "TWO_HUNDRED_THIRD_173_CARD_COMPACT_DICTIONARY.tsv"

FIELDS = [
    ("O01", "PF03", ["MC123", "MC039", "MC026"],
     "Diesen Pflanzenposten auf Sollmaß einsetzen.",
     "Diesen Stationsposten auf Sollmaß einsetzen.",
     "Pflanzenposten", "Stationsposten"),
    ("O02", "PF07", ["MC055", "MC039", "MC154"],
     "Davon das Sollmaß nehmen und an die nächste Pflanzenzubereitung bringen.",
     "Davon das Sollmaß nehmen und an die nächste Beckenstation bringen.",
     "Pflanzenzubereitung", "Beckenstation"),
    ("O03", "PF05", ["MC120", "MC040", "MC032"],
     "Bemessen, am Pflanzenansatz einsetzen und länger bearbeiten.",
     "Bemessen, an der Zielstation einsetzen und länger bearbeiten.",
     "Pflanzenansatz", "Zielstation"),
    ("O04", "WHOLE_CARD_BRIDGE", ["MC119"],
     "Den Klarlauf als geklärten Pflanzenauszug lesen.",
     "Den Klarlauf als klaren Stationsablauf lesen.",
     "geklärter Pflanzenauszug", "klarer Stationsablauf"),
]


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    dictionary = {row["master_card_id"]: row for row in read(DICT)}
    token_rows: list[dict[str, object]] = []
    field_rows: list[dict[str, object]] = []
    sequence = 0
    for field_id, license_id, card_ids, herbal, bio, herbal_owner_words, bio_owner_words in FIELDS:
        for position, card_id in enumerate(card_ids, 1):
            sequence += 1
            card = dictionary[card_id]
            token_rows.append({
                "sequence": sequence,
                "field_id": field_id,
                "position": position,
                "master_card_id": card_id,
                "surface": card["master_form"],
                "invariant_card_value_de": card["current_value_de"],
                "herbal_card_value_de": card["current_value_de"],
                "bio_card_value_de": card["current_value_de"],
                "value_changed_by_owner": "NO",
            })
        field_rows.append({
            "field_id": field_id,
            "license_id": license_id,
            "card_ids": "|".join(card_ids),
            "surface_text": " ".join(dictionary[card_id]["master_form"] for card_id in card_ids),
            "literal_card_values_de": " | ".join(dictionary[card_id]["current_value_de"] for card_id in card_ids),
            "herbal_visible_owner": "ganze Bildpflanze",
            "herbal_expansion_de": herbal,
            "herbal_owner_supplied_words": herbal_owner_words,
            "bio_visible_owner": "lokale Becken-/Gerätestation",
            "bio_expansion_de": bio,
            "bio_owner_supplied_words": bio_owner_words,
            "card_stream_identical": "YES",
        })
    write(OUT / "TWO_HUNDRED_TWELFTH_10_IDENTICAL_BRIDGE_TOKENS.tsv", token_rows)
    write(OUT / "TWO_HUNDRED_TWELFTH_FOUR_OWNER_SUBSTITUTIONS.tsv", field_rows)
    summary = {
        "dictionary_source_sha256": hashlib.sha256(DICT.read_bytes()).hexdigest(),
        "fields": len(field_rows),
        "tokens": len(token_rows),
        "unique_cards": len({row["master_card_id"] for row in token_rows}),
        "changed_card_values": sum(row["value_changed_by_owner"] == "YES" for row in token_rows),
        "owner_expansions": len(field_rows) * 2,
        "phrase_licensed_fields": sum(row["license_id"].startswith("PF") for row in field_rows),
        "whole_card_fields": sum(row["license_id"] == "WHOLE_CARD_BRIDGE" for row in field_rows),
        "sealed_pages_accessed": False,
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
