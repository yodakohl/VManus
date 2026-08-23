#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
BASE = ROOT / "experiments/yolo/sidequest_semantic_vocabulary_granularity_two_hundred_third"
APP = ROOT / "experiments/yolo/sidequest_semantic_apprentice_dictionary_two_hundred_fourth"
DICT = BASE / "TWO_HUNDRED_THIRD_173_CARD_COMPACT_DICTIONARY.tsv"
INDEX = APP / "TWO_HUNDRED_FOURTH_173_CARD_APPRENTICE_INDEX.tsv"

FIELDS = [
    ("P01", "CH", "LEARNED_CHAIN", "LC02", ["MC086", "MC159", "MC014"], "Einen Teil in das Aufnahmegefäß geben und Flüssigkeit zugießen."),
    ("P02", "D", "PRODUCTIVE_FRAME", "PF07", ["MC055", "MC105", "MC154"], "Davon eine Portion nehmen und dorthin bringen."),
    ("P03", "O", "PRODUCTIVE_FRAME", "PF03", ["MC103", "MC039", "MC026"], "Weiterbearbeiten, auf Sollmaß bringen und einsetzen."),
    ("P04", "Q", "PRODUCTIVE_FRAME", "PF01", ["MC120", "MC040", "MC005"], "Bemessen, dorthin einsetzen und einführen; Schluss."),
    ("P05", "S", "LEARNED_CHAIN", "LC04", ["MC098", "MC049", "MC129", "MC111", "MC156", "MC119", "MC037"], "Kochgut ansetzen, auswringen, die Stehzeit halten, nachseihen, den Klarlauf kalt stellen; Schluss."),
    ("P06", "Q", "PRODUCTIVE_FRAME", "PF09", ["MC035", "MC002", "MC057"], "Durchleiten, lange einwirken lassen und als Folgetransfer schließen."),
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
    dictionary_rows = read(DICT)
    dictionary = {row["master_card_id"]: row for row in dictionary_rows}
    index = {row["master_card_id"]: row for row in read(INDEX)}
    surface_map = {surface: row["master_card_id"] for row in dictionary_rows for surface in row["registered_surfaces"].split("|")}
    token_rows: list[dict[str, object]] = []
    field_rows: list[dict[str, object]] = []
    pair_rows: list[dict[str, object]] = []
    sequence = 0
    for field_id, mode, license_type, license_id, card_ids, reading in FIELDS:
        hand_a: list[str] = []
        hand_b: list[str] = []
        values: list[str] = []
        drawers = [index[card_id]["drawer"] for card_id in card_ids]
        for position, card_id in enumerate(card_ids, 1):
            sequence += 1
            card = dictionary[card_id]
            a = card["master_form"]
            b = card["registered_surfaces"].split("|")[-1]
            decoded = surface_map[b]
            hand_a.append(a)
            hand_b.append(b)
            values.append(card["current_value_de"])
            token_rows.append({
                "sequence": sequence,
                "field_id": field_id,
                "field_mode": mode,
                "position": position,
                "license_type": license_type,
                "license_id": license_id,
                "intended_card_id": card_id,
                "hand_a_surface": a,
                "hand_b_surface": b,
                "surface_changed": "YES" if a != b else "NO",
                "decoded_card_id": decoded,
                "value_de": card["current_value_de"],
                "drawer": drawers[position - 1],
                "readback_status": "EXACT" if decoded == card_id else "ERROR",
            })
        for pair_position, (left, right) in enumerate(zip(card_ids, card_ids[1:]), 1):
            pair_rows.append({
                "field_id": field_id,
                "pair_position": pair_position,
                "left_card_id": left,
                "right_card_id": right,
                "left_drawer": index[left]["drawer"],
                "right_drawer": index[right]["drawer"],
                "license_type": license_type,
                "license_id": license_id,
                "bridge_status": "LICENSED_EXEMPLAR_CHAIN" if license_type == "LEARNED_CHAIN" else "LICENSED_PRODUCTIVE_FRAME",
            })
        field_rows.append({
            "field_id": field_id,
            "field_mode": mode,
            "license_type": license_type,
            "license_id": license_id,
            "drawer_sequence": " > ".join(drawers),
            "hand_a_text": " ".join(hand_a),
            "hand_b_text": " ".join(hand_b),
            "literal_values_de": " | ".join(values),
            "fluent_reading_de": reading,
            "token_count": len(card_ids),
        })
    write(OUT / "TWO_HUNDRED_EIGHTH_22_TOKEN_LICENSED_ROUNDTRIP.tsv", token_rows)
    write(OUT / "TWO_HUNDRED_EIGHTH_SIX_LICENSED_FIELDS.tsv", field_rows)
    write(OUT / "TWO_HUNDRED_EIGHTH_16_LICENSED_BRIDGES.tsv", pair_rows)
    summary = {
        "dictionary_source_sha256": hashlib.sha256(DICT.read_bytes()).hexdigest(),
        "fields": len(field_rows),
        "tokens": len(token_rows),
        "bridges": len(pair_rows),
        "productive_frame_fields": sum(row["license_type"] == "PRODUCTIVE_FRAME" for row in field_rows),
        "learned_chain_fields": sum(row["license_type"] == "LEARNED_CHAIN" for row in field_rows),
        "hand_b_surface_changes": sum(row["surface_changed"] == "YES" for row in token_rows),
        "exact_readbacks": sum(row["readback_status"] == "EXACT" for row in token_rows),
        "unlicensed_bridges": sum(not row["bridge_status"].startswith("LICENSED") for row in pair_rows),
        "sealed_pages_accessed": False,
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
