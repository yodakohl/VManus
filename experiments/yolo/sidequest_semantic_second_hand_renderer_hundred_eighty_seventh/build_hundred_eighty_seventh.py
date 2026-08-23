#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
TOKENS = ROOT / "experiments/yolo/sidequest_semantic_four_text_mini_section_hundred_eighty_sixth/HUNDRED_EIGHTY_SIXTH_73_TOKEN_MINI_SECTION.tsv"
FIELDS = ROOT / "experiments/yolo/sidequest_semantic_four_text_mini_section_hundred_eighty_sixth/HUNDRED_EIGHTY_SIXTH_18_FIELD_MINI_SECTION.tsv"
DICTIONARY = ROOT / "experiments/yolo/sidequest_semantic_ten_page_master_edition_hundred_seventy_fifth/HUNDRED_SEVENTY_FIFTH_173_CARD_DICTIONARY.tsv"


RULES = [
    ("H1", "KEEP_CARD", "Die exakte Karten-ID und ihr Wert bleiben unveraendert."),
    ("H2", "NEXT_REGISTERED_SURFACE", "Hat eine Karte mehrere registrierte Oberflaechen, nimmt Hand B die naechste in ihrer Lehrliste."),
    ("H3", "KEEP_FIELDS", "Tokenreihenfolge und alle achtzehn Feldgrenzen bleiben unveraendert."),
    ("H4", "KEEP_FINALITY", "Eine Schlusskarte bleibt letztes Token ihres Feldes."),
    ("H5", "READ_BY_SURFACE_TABLE", "Der Leser schlaegt die sichtbare Oberflaeche nach und gewinnt dieselbe exakte Karten-ID zurueck."),
]


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def next_surface(current: str, registered: list[str]) -> str:
    if len(registered) == 1:
        return current
    return registered[(registered.index(current) + 1) % len(registered)]


def main() -> None:
    source_tokens = read(TOKENS)
    source_fields = read(FIELDS)
    dictionary = {row["master_card_id"]: row for row in read(DICTIONARY)}
    surface_to_card = {}
    for card_id, row in dictionary.items():
        for surface in row["registered_surfaces"].split("|"):
            if surface in surface_to_card:
                raise ValueError(surface)
            surface_to_card[surface] = card_id

    rendered = []
    for row in source_tokens:
        card = dictionary[row["master_card_id"]]
        registered = card["registered_surfaces"].split("|")
        surface = next_surface(row["surface"], registered)
        rendered.append(
            {
                "global_token_order": row["global_token_order"],
                "section": row["section"],
                "global_field_id": row["global_field_id"],
                "grammar_slot": row["grammar_slot"],
                "master_card_id": row["master_card_id"],
                "hand_a_surface": row["surface"],
                "hand_b_surface": surface,
                "surface_changed": "YES" if surface != row["surface"] else "NO",
                "registered_surface_inventory": card["registered_surfaces"],
                "decoded_card_id": surface_to_card[surface],
                "hand_a_value_de": row["value_de"],
                "hand_b_decoded_value_de": dictionary[surface_to_card[surface]]["portable_card_value_de"],
                "finality_rule": row["finality_rule"],
            }
        )
    write(OUT / "HUNDRED_EIGHTY_SEVENTH_73_TOKEN_HAND_B_RENDERING.tsv", rendered)

    field_rows = []
    for field in source_fields:
        rows = [row for row in rendered if row["global_field_id"] == field["global_field_id"]]
        field_rows.append(
            {
                "global_field_id": field["global_field_id"],
                "section": field["section"],
                "field_status": field["field_status"],
                "hand_a_sequence": field["visible_sequence"],
                "hand_b_sequence": " ".join(row["hand_b_surface"] for row in rows),
                "card_id_sequence": "|".join(row["master_card_id"] for row in rows),
                "decoded_card_id_sequence": "|".join(row["decoded_card_id"] for row in rows),
                "changed_tokens": sum(row["surface_changed"] == "YES" for row in rows),
                "reading_de": field["reading_de"],
            }
        )
    write(OUT / "HUNDRED_EIGHTY_SEVENTH_18_FIELD_HAND_B_EDITION.tsv", field_rows)

    by_card: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rendered:
        by_card[row["master_card_id"]].append(row)
    changed_card_rows = []
    for card_id in sorted(by_card, key=lambda value: int(value[2:])):
        rows = by_card[card_id]
        if not any(row["surface_changed"] == "YES" for row in rows):
            continue
        changed_card_rows.append(
            {
                "master_card_id": card_id,
                "value_de": dictionary[card_id]["portable_card_value_de"],
                "registered_surfaces": dictionary[card_id]["registered_surfaces"],
                "hand_a_surfaces_used": "|".join(sorted({row["hand_a_surface"] for row in rows})),
                "hand_b_surfaces_used": "|".join(sorted({row["hand_b_surface"] for row in rows})),
                "changed_occurrences": sum(row["surface_changed"] == "YES" for row in rows),
                "readback_rule": "all surfaces map uniquely to this master_card_id",
            }
        )
    write(OUT / "HUNDRED_EIGHTY_SEVENTH_23_CARD_ALLOGRAPH_MAP.tsv", changed_card_rows)

    rule_rows = [
        {"rule_id": rid, "rule_name": name, "scribe_instruction_de": instruction}
        for rid, name, instruction in RULES
    ]
    write(OUT / "HUNDRED_EIGHTY_SEVENTH_5_RENDERER_RULES.tsv", rule_rows)

    summary = {
        "token_source_sha256": hashlib.sha256(TOKENS.read_bytes()).hexdigest(),
        "field_source_sha256": hashlib.sha256(FIELDS.read_bytes()).hexdigest(),
        "dictionary_sha256": hashlib.sha256(DICTIONARY.read_bytes()).hexdigest(),
        "tokens": len(rendered),
        "fields": len(field_rows),
        "distinct_cards": len(by_card),
        "changed_tokens": sum(row["surface_changed"] == "YES" for row in rendered),
        "unchanged_tokens": sum(row["surface_changed"] == "NO" for row in rendered),
        "cards_with_changed_surface": len(changed_card_rows),
        "exact_card_readbacks": sum(row["master_card_id"] == row["decoded_card_id"] for row in rendered),
        "exact_value_readbacks": sum(row["hand_a_value_de"] == row["hand_b_decoded_value_de"] for row in rendered),
        "new_surfaces": 0,
        "f84_or_f84r_access": False,
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
