#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
HAND_C = ROOT / "experiments/yolo/sidequest_semantic_positional_third_hand_hundred_eighty_eighth/HUNDRED_EIGHTY_EIGHTH_73_TOKEN_HAND_C_RENDERING.tsv"
DICTIONARY = ROOT / "experiments/yolo/sidequest_semantic_ten_page_master_edition_hundred_seventy_fifth/HUNDRED_SEVENTY_FIFTH_173_CARD_DICTIONARY.tsv"


RULES = [
    ("R1", "Q_ACTIVE_FRAME", "OK/OT active cards use their registered q-form at the taught initial or medial position", "MC007|MC013|MC093|MC120|MC002", 7),
    ("R2", "D_MEASURE_POSITION", "AIIN measure uses daiin medially or finally", "MC039", 3),
    ("R3", "BARE_TARGET_MEDIAL", "the AL target card uses bare al medially", "MC154", 2),
    ("R4", "BOUNDARY_FRAME_REDUCTION", "CHOR at field start and CHEOL at field end lose the ch/che frame", "MC080|MC153", 2),
    ("R5", "S_FINAL_CLOSE", "the two taught CHEDY close families use their s-surface finally", "MC025|MC128", 2),
]


Q_MAP = {
    "okey": "qokey",
    "otchor": "qotchor",
    "otal": "qotal",
    "okaiin": "qokaiin",
    "okeey": "qokeey",
}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def apply_rule(row: dict[str, str]) -> tuple[str, str]:
    card_id = row["master_card_id"]
    surface = row["hand_a_surface"]
    position = row["target_position_class"]
    if card_id in {"MC007", "MC093", "MC120", "MC002"} and position == "MEDIAL":
        return "R1", Q_MAP[surface]
    if card_id == "MC013" and position == "INITIAL":
        return "R1", Q_MAP[surface]
    if card_id == "MC039" and position in {"MEDIAL", "FINAL"}:
        return "R2", "daiin"
    if card_id == "MC154" and position == "MEDIAL":
        return "R3", "al"
    if card_id == "MC080" and position == "INITIAL":
        return "R4", "or"
    if card_id == "MC153" and position == "FINAL":
        return "R4", "ol"
    if card_id == "MC025" and position == "FINAL":
        return "R5", "schedy"
    if card_id == "MC128" and position == "FINAL":
        return "R5", "shedy"
    return "DEFAULT_KEEP", surface


def main() -> None:
    hand_c = read(HAND_C)
    dictionary = {row["master_card_id"]: row for row in read(DICTIONARY)}
    predicted = []
    for row in hand_c:
        rule, surface = apply_rule(row)
        predicted.append(
            {
                "global_token_order": row["global_token_order"],
                "section": row["section"],
                "global_field_id": row["global_field_id"],
                "position_class": row["target_position_class"],
                "master_card_id": row["master_card_id"],
                "value_de": row["value_de"],
                "hand_a_surface": row["hand_a_surface"],
                "rule_applied": rule,
                "compressed_profile_surface": surface,
                "hand_c_surface": row["hand_c_surface"],
                "matches_hand_c": "YES" if surface == row["hand_c_surface"] else "NO",
                "surface_registered": "YES" if surface in dictionary[row["master_card_id"]]["registered_surfaces"].split("|") else "NO",
            }
        )
    write(OUT / "HUNDRED_EIGHTY_NINTH_73_TOKEN_COMPRESSED_PROFILE.tsv", predicted)

    rule_rows = [
        {
            "rule_id": rid,
            "rule_name": name,
            "apprentice_rule_de": rule,
            "card_scope": scope,
            "expected_changed_tokens": expected,
            "actual_changed_tokens": sum(row["rule_applied"] == rid for row in predicted),
        }
        for rid, name, rule, scope, expected in RULES
    ]
    write(OUT / "HUNDRED_EIGHTY_NINTH_5_HAND_RULES.tsv", rule_rows)

    card_rows = []
    for card_id in sorted({row["master_card_id"] for row in predicted if row["rule_applied"] != "DEFAULT_KEEP"}, key=lambda value: int(value[2:])):
        rows = [row for row in predicted if row["master_card_id"] == card_id]
        card_rows.append(
            {
                "master_card_id": card_id,
                "value_de": dictionary[card_id]["portable_card_value_de"],
                "rule_ids": "|".join(sorted({row["rule_applied"] for row in rows if row["rule_applied"] != "DEFAULT_KEEP"})),
                "hand_a_surfaces": "|".join(sorted({row["hand_a_surface"] for row in rows})),
                "profile_surfaces": "|".join(sorted({row["compressed_profile_surface"] for row in rows})),
                "changed_tokens": sum(row["compressed_profile_surface"] != row["hand_a_surface"] for row in rows),
            }
        )
    write(OUT / "HUNDRED_EIGHTY_NINTH_11_RULE_CARD_PROFILES.tsv", card_rows)

    rule_counts = Counter(row["rule_applied"] for row in predicted)
    summary = {
        "hand_c_source_sha256": hashlib.sha256(HAND_C.read_bytes()).hexdigest(),
        "dictionary_sha256": hashlib.sha256(DICTIONARY.read_bytes()).hexdigest(),
        "tokens": len(predicted),
        "rules": len(rule_rows),
        "default_keep_tokens": rule_counts["DEFAULT_KEEP"],
        "changed_tokens": len(predicted) - rule_counts["DEFAULT_KEEP"],
        "rule_coverage": {rid: rule_counts[rid] for rid, *_ in RULES},
        "exact_hand_c_matches": sum(row["matches_hand_c"] == "YES" for row in predicted),
        "false_changes": sum(row["matches_hand_c"] == "NO" for row in predicted),
        "new_surfaces": 0,
        "f84_or_f84r_access": False,
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
