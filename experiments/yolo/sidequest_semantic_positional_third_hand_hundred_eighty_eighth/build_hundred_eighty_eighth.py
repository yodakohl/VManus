#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
OBSERVED = ROOT / "experiments/yolo/sidequest_semantic_six_slot_pressure_test_hundred_eighty_first/HUNDRED_EIGHTY_FIRST_381_EVENT_SIX_SLOT_PARSE.tsv"
TOKENS = ROOT / "experiments/yolo/sidequest_semantic_four_text_mini_section_hundred_eighty_sixth/HUNDRED_EIGHTY_SIXTH_73_TOKEN_MINI_SECTION.tsv"
FIELDS = ROOT / "experiments/yolo/sidequest_semantic_four_text_mini_section_hundred_eighty_sixth/HUNDRED_EIGHTY_SIXTH_18_FIELD_MINI_SECTION.tsv"
DICTIONARY = ROOT / "experiments/yolo/sidequest_semantic_ten_page_master_edition_hundred_seventy_fifth/HUNDRED_SEVENTY_FIFTH_173_CARD_DICTIONARY.tsv"


FALLBACK_ORDER = {
    "INITIAL": ["INITIAL", "ONLY", "MEDIAL", "FINAL"],
    "MEDIAL": ["MEDIAL", "INITIAL", "FINAL", "ONLY"],
    "FINAL": ["FINAL", "ONLY", "MEDIAL", "INITIAL"],
    "ONLY": ["ONLY", "FINAL", "INITIAL", "MEDIAL"],
}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def position_class(position: int, length: int) -> str:
    if length == 1:
        return "ONLY"
    if position == 1:
        return "INITIAL"
    if position == length:
        return "FINAL"
    return "MEDIAL"


def main() -> None:
    observed = read(OBSERVED)
    source_tokens = read(TOKENS)
    source_fields = read(FIELDS)
    dictionary = {row["master_card_id"]: row for row in read(DICTIONARY)}
    observed_field_size = Counter(row["field_id"] for row in observed)
    counts: dict[tuple[str, str], Counter[str]] = defaultdict(Counter)
    examples: dict[tuple[str, str, str], list[str]] = defaultdict(list)
    for row in observed:
        pclass = position_class(int(row["field_position"]), observed_field_size[row["field_id"]])
        counts[(row["master_card_id"], pclass)][row["surface"]] += 1
        examples[(row["master_card_id"], pclass, row["surface"])].append(row["event_id"])

    preference_rows = []
    for card_id, pclass in sorted(counts, key=lambda key: (int(key[0][2:]), ["INITIAL", "MEDIAL", "FINAL", "ONLY"].index(key[1]))):
        registered = dictionary[card_id]["registered_surfaces"].split("|")
        surface_counts = counts[(card_id, pclass)]
        preferred = max(registered, key=lambda surface: (surface_counts[surface], -registered.index(surface)))
        preference_rows.append(
            {
                "master_card_id": card_id,
                "value_de": dictionary[card_id]["portable_card_value_de"],
                "position_class": pclass,
                "observed_events": sum(surface_counts.values()),
                "surface_counts": "|".join(f"{surface}:{surface_counts[surface]}" for surface in registered if surface_counts[surface]),
                "preferred_surface": preferred,
                "preferred_event_ids": "|".join(examples[(card_id, pclass, preferred)]),
            }
        )
    write(OUT / "HUNDRED_EIGHTY_EIGHTH_227_POSITION_PREFERENCES.tsv", preference_rows)

    synthetic_field_size = Counter(row["global_field_id"] for row in source_tokens)
    synthetic_position = Counter()
    surface_to_card = {}
    for card_id, card in dictionary.items():
        for surface in card["registered_surfaces"].split("|"):
            if surface in surface_to_card:
                raise ValueError(surface)
            surface_to_card[surface] = card_id

    rendered = []
    fallback_rows = []
    for row in source_tokens:
        field_id = row["global_field_id"]
        synthetic_position[field_id] += 1
        target_class = position_class(synthetic_position[field_id], synthetic_field_size[field_id])
        evidence_class = next(candidate for candidate in FALLBACK_ORDER[target_class] if (row["master_card_id"], candidate) in counts)
        registered = dictionary[row["master_card_id"]]["registered_surfaces"].split("|")
        surface_counts = counts[(row["master_card_id"], evidence_class)]
        preferred = max(registered, key=lambda surface: (surface_counts[surface], -registered.index(surface)))
        fallback = evidence_class != target_class
        rendered.append(
            {
                "global_token_order": row["global_token_order"],
                "section": row["section"],
                "global_field_id": field_id,
                "field_position": synthetic_position[field_id],
                "target_position_class": target_class,
                "evidence_position_class": evidence_class,
                "position_fallback": "YES" if fallback else "NO",
                "grammar_slot": row["grammar_slot"],
                "master_card_id": row["master_card_id"],
                "hand_a_surface": row["surface"],
                "hand_c_surface": preferred,
                "surface_changed": "YES" if preferred != row["surface"] else "NO",
                "support_events": surface_counts[preferred],
                "decoded_card_id": surface_to_card[preferred],
                "value_de": row["value_de"],
                "finality_rule": row["finality_rule"],
            }
        )
        if fallback:
            fallback_rows.append(
                {
                    "fallback_id": f"F{len(fallback_rows) + 1:02d}",
                    "global_token_order": row["global_token_order"],
                    "global_field_id": field_id,
                    "master_card_id": row["master_card_id"],
                    "value_de": row["value_de"],
                    "requested_position": target_class,
                    "used_evidence_position": evidence_class,
                    "selected_surface": preferred,
                    "reason_de": "diese exakte Karte hat keinen beobachteten Beleg in der angeforderten Positionsklasse",
                }
            )
    write(OUT / "HUNDRED_EIGHTY_EIGHTH_73_TOKEN_HAND_C_RENDERING.tsv", rendered)
    write(OUT / "HUNDRED_EIGHTY_EIGHTH_12_POSITION_FALLBACKS.tsv", fallback_rows)

    field_rows = []
    for field in source_fields:
        rows = [row for row in rendered if row["global_field_id"] == field["global_field_id"]]
        field_rows.append(
            {
                "global_field_id": field["global_field_id"],
                "section": field["section"],
                "field_status": field["field_status"],
                "hand_a_sequence": field["visible_sequence"],
                "hand_c_sequence": " ".join(row["hand_c_surface"] for row in rows),
                "card_id_sequence": "|".join(row["master_card_id"] for row in rows),
                "decoded_card_id_sequence": "|".join(row["decoded_card_id"] for row in rows),
                "changed_tokens": sum(row["surface_changed"] == "YES" for row in rows),
                "position_fallbacks": sum(row["position_fallback"] == "YES" for row in rows),
                "reading_de": field["reading_de"],
            }
        )
    write(OUT / "HUNDRED_EIGHTY_EIGHTH_18_FIELD_HAND_C_EDITION.tsv", field_rows)

    changed_cards = []
    for card_id in sorted({row["master_card_id"] for row in rendered if row["surface_changed"] == "YES"}, key=lambda value: int(value[2:])):
        rows = [row for row in rendered if row["master_card_id"] == card_id]
        changed_cards.append(
            {
                "master_card_id": card_id,
                "value_de": dictionary[card_id]["portable_card_value_de"],
                "hand_a_surfaces": "|".join(sorted({row["hand_a_surface"] for row in rows})),
                "hand_c_surfaces": "|".join(sorted({row["hand_c_surface"] for row in rows})),
                "changed_occurrences": sum(row["surface_changed"] == "YES" for row in rows),
                "positional_classes_used": "|".join(sorted({row["evidence_position_class"] for row in rows})),
            }
        )
    write(OUT / "HUNDRED_EIGHTY_EIGHTH_11_CHANGED_CARD_MAP.tsv", changed_cards)

    section_lines = []
    for section in ["A", "C", "B", "D"]:
        sequence = " | ".join(row["hand_c_sequence"] for row in field_rows if row["section"] == section)
        section_lines.append(f"## {section}\n\n`{sequence}`")
    readable = "# Derselbe Mini-Abschnitt in positionsgewohnter Hand C\n\n" + "\n\n".join(section_lines) + "\n"
    (OUT / "HUNDRED_EIGHTY_EIGHTH_HAND_C_READABLE_EDITION.md").write_text(readable, encoding="utf-8")

    summary = {
        "observed_source_sha256": hashlib.sha256(OBSERVED.read_bytes()).hexdigest(),
        "token_source_sha256": hashlib.sha256(TOKENS.read_bytes()).hexdigest(),
        "field_source_sha256": hashlib.sha256(FIELDS.read_bytes()).hexdigest(),
        "dictionary_sha256": hashlib.sha256(DICTIONARY.read_bytes()).hexdigest(),
        "observed_preference_cells": len(preference_rows),
        "tokens": len(rendered),
        "fields": len(field_rows),
        "exact_position_support": sum(row["position_fallback"] == "NO" for row in rendered),
        "position_fallbacks": len(fallback_rows),
        "changed_tokens_from_hand_a": sum(row["surface_changed"] == "YES" for row in rendered),
        "unchanged_tokens_from_hand_a": sum(row["surface_changed"] == "NO" for row in rendered),
        "changed_cards": len(changed_cards),
        "exact_card_readbacks": sum(row["master_card_id"] == row["decoded_card_id"] for row in rendered),
        "new_surfaces": 0,
        "f84_or_f84r_access": False,
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
