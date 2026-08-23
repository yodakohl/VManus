#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
DICTIONARY = ROOT / "experiments/yolo/sidequest_semantic_ten_page_master_edition_hundred_seventy_fifth/HUNDRED_SEVENTY_FIFTH_173_CARD_DICTIONARY.tsv"
OBSERVED = ROOT / "experiments/yolo/sidequest_semantic_six_slot_pressure_test_hundred_eighty_first/HUNDRED_EIGHTY_FIRST_381_EVENT_SIX_SLOT_PARSE.tsv"
PALETTE = ROOT / "experiments/yolo/sidequest_semantic_three_text_writing_palette_hundred_eighty_third/HUNDRED_EIGHTY_THIRD_25_CARD_WRITING_PALETTE.tsv"
PALETTE_USAGE = ROOT / "experiments/yolo/sidequest_semantic_three_text_writing_palette_hundred_eighty_third/HUNDRED_EIGHTY_THIRD_48_TOKEN_PALETTE_USAGE.tsv"
RARE = ROOT / "experiments/yolo/sidequest_semantic_rare_card_prediction_hundred_seventy_sixth/HUNDRED_SEVENTY_SIXTH_143_RARE_CARD_PREDICTIONS.tsv"
SECOND = ROOT / "experiments/yolo/sidequest_semantic_second_forward_writing_hundred_seventy_ninth/HUNDRED_SEVENTY_NINTH_16_TOKEN_STOCK_ENCODING.tsv"


CORRECTED_FIELDS = {
    1: ("talam dchol ykaiin ches", "vom verwahrten vorigen Ansatz eine Sollportion nehmen und teilen", "OPEN"),
    2: ("ykain ody", "erste Portion abkuehlen und den Teilvorgang schliessen", "CLOSED"),
    3: ("talam oldy", "abgekuehlte Portion verwahren und freigeben", "CLOSED"),
    4: ("ykan cheky okal qokedy", "zweite Portion kurz waermen am ersten Ziel einsetzen und kurz einwirken", "CLOSED"),
    5: ("qotchy otal qoky rshedy", "Folgeposten zum naechsten Ziel bringen dort einsetzen und Waschfolge schliessen", "CLOSED"),
}


SECOND_FIELD_MAP = {1: 1, 2: 1, 3: 1, 4: 1, 5: 2, 6: 2, 7: 3, 8: 3, 9: 4, 10: 4, 11: 4, 12: 4, 13: 5, 14: 5, 15: 5, 16: 5}
SECOND_SLOT_OVERRIDES = {"MC100": "G6", "MC107": "G2", "MC026": "G4"}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    dictionary = read(DICTIONARY)
    observed = read(OBSERVED)
    palette = {row["master_card_id"]: row for row in read(PALETTE)}
    palette_usage = read(PALETTE_USAGE)
    rare = {row["master_card_id"]: row for row in read(RARE)}
    observed_by_card: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in observed:
        observed_by_card[row["master_card_id"]].append(row)

    maximum_order = {}
    for row in palette_usage:
        key = (row["exercise"], row["field"])
        maximum_order[key] = max(maximum_order.get(key, 0), int(row["token_order"]))

    lexicon_rows = []
    alignment_rows = []
    for card in dictionary:
        card_id = card["master_card_id"]
        uses = observed_by_card[card_id]
        slot_counts = Counter(row["primary_grammar_slot"] for row in uses)
        if len(slot_counts) != 1:
            raise ValueError(card_id)
        observed_slot = next(iter(slot_counts))
        terminal_events = sum(row["field_close_role"] == "YES" for row in uses)
        if terminal_events == len(uses):
            finality = "ALWAYS_FIELD_FINAL"
        elif terminal_events:
            finality = "SOMETIMES_FIELD_FINAL"
        else:
            finality = "NOT_OBSERVED_AS_CLOSE"
        palette_row = palette.get(card_id)
        forward_slots = palette_row["palette_slots"] if palette_row else "NOT_YET_USED"
        forward_violation = "NO"
        if finality == "ALWAYS_FIELD_FINAL" and palette_row:
            for use in palette_usage:
                if use["master_card_id"] == card_id and int(use["token_order"]) != maximum_order[(use["exercise"], use["field"])]:
                    forward_violation = "YES"
        if not palette_row:
            alignment = "UNUSED_IN_FORWARD_PALETTE"
        elif forward_violation == "YES":
            alignment = "STRUCTURAL_REPAIR_REQUIRED"
        else:
            forward_set = set(forward_slots.split("|"))
            if forward_set == {observed_slot}:
                alignment = "EXACT_SLOT_MATCH"
            elif observed_slot in forward_set:
                alignment = "FORWARD_SLOT_EXTENSION"
            else:
                alignment = "SEMANTIC_ROLE_BRIDGE_WITH_POSITIONAL_RULES"
        if palette_row:
            writing_class = "CURRENT_25_CARD_PALETTE"
        elif card["portable_scope"].startswith("ACTIVE"):
            writing_class = "NEW_PORTABLE_SLOT_CANDIDATE"
        else:
            writing_class = "LOCAL_LEARNED_SLOT_CANDIDATE"
        rare_row = rare.get(card_id)
        composition_class = rare_row["prediction_status"] if rare_row else "COMMON_CARD_NOT_IN_RARE_AUDIT"
        lexicon_rows.append(
            {
                "master_card_id": card_id,
                "master_form": card["master_form"],
                "registered_surfaces": card["registered_surfaces"],
                "portable_value_de": card["portable_card_value_de"],
                "syntactic_type": card["syntactic_type"],
                "portable_scope": card["portable_scope"],
                "event_count": len(uses),
                "observed_slot": observed_slot,
                "observed_role_combinations": "|".join(sorted({row["source_roles"] for row in uses})),
                "terminal_events": terminal_events,
                "finality_rule": finality,
                "forward_palette_slots": forward_slots,
                "forward_alignment": alignment,
                "writing_class": writing_class,
                "composition_class": composition_class,
            }
        )
        if palette_row and alignment != "EXACT_SLOT_MATCH":
            if card_id == "MC100":
                correction = "split field after ody: ykain ody | talam oldy"
            else:
                correction = "retain card but teach observed role plus embedded forward role"
            alignment_rows.append(
                {
                    "master_card_id": card_id,
                    "master_form": card["master_form"],
                    "value_de": card["portable_card_value_de"],
                    "observed_slot": observed_slot,
                    "forward_slots": forward_slots,
                    "alignment": alignment,
                    "terminal_evidence": f"{terminal_events}/{len(uses)}",
                    "repair_or_teaching_rule_de": correction,
                }
            )
    write(OUT / "HUNDRED_EIGHTY_FOURTH_173_CARD_SIX_SLOT_LEXICON.tsv", lexicon_rows)
    unused = [row for row in lexicon_rows if row["writing_class"] != "CURRENT_25_CARD_PALETTE"]
    write(OUT / "HUNDRED_EIGHTY_FOURTH_148_UNUSED_SLOT_CANDIDATES.tsv", unused)
    write(OUT / "HUNDRED_EIGHTY_FOURTH_8_FORWARD_ALIGNMENT_CORRECTIONS.tsv", alignment_rows)

    shortlist = []
    for slot in [f"G{i}" for i in range(1, 7)]:
        candidates = [row for row in unused if row["observed_slot"] == slot]
        candidates.sort(
            key=lambda row: (
                row["writing_class"] == "NEW_PORTABLE_SLOT_CANDIDATE",
                int(row["event_count"]),
                -int(str(row["master_card_id"])[2:]),
            ),
            reverse=True,
        )
        for rank, row in enumerate(candidates[:4], start=1):
            shortlist.append(
                {
                    "slot": slot,
                    "slot_rank": rank,
                    "master_card_id": row["master_card_id"],
                    "master_form": row["master_form"],
                    "portable_value_de": row["portable_value_de"],
                    "event_count": row["event_count"],
                    "writing_class": row["writing_class"],
                    "finality_rule": row["finality_rule"],
                    "fourth_instruction_use_de": "use only with this observed slot and finality rule",
                }
            )
    write(OUT / "HUNDRED_EIGHTY_FOURTH_24_LOW_OVERLAP_SHORTLIST.tsv", shortlist)

    second_rows = []
    for row in read(SECOND):
        order = int(row["token_order"])
        card_id = row["master_card_id"]
        second_rows.append(
            {
                "token_order": order,
                "corrected_field": SECOND_FIELD_MAP[order],
                "master_card_id": card_id,
                "surface": row["chosen_visible_surface"],
                "dictionary_value_de": row["dictionary_value_de"],
                "corrected_slot": SECOND_SLOT_OVERRIDES.get(card_id, "UNCHANGED_FROM_R179"),
                "field_final": "YES" if order in {4, 6, 8, 12, 16} else "NO",
                "correction_note_de": "ody is terminal in its sole manuscript use" if card_id == "MC100" else "field boundary update only",
            }
        )
    write(OUT / "HUNDRED_EIGHTY_FOURTH_CORRECTED_16_TOKEN_SECOND_EXERCISE.tsv", second_rows)
    corrected_field_rows = [
        {
            "field": field,
            "visible_sequence": sequence,
            "corrected_reading_de": reading,
            "field_status": status,
        }
        for field, (sequence, reading, status) in CORRECTED_FIELDS.items()
    ]
    write(OUT / "HUNDRED_EIGHTY_FOURTH_CORRECTED_5_FIELD_SECOND_EXERCISE.tsv", corrected_field_rows)

    slot_distribution = Counter(row["observed_slot"] for row in lexicon_rows)
    alignment_distribution = Counter(row["forward_alignment"] for row in lexicon_rows if row["writing_class"] == "CURRENT_25_CARD_PALETTE")
    summary = {
        "dictionary_sha256": hashlib.sha256(DICTIONARY.read_bytes()).hexdigest(),
        "observed_parse_sha256": hashlib.sha256(OBSERVED.read_bytes()).hexdigest(),
        "palette_sha256": hashlib.sha256(PALETTE.read_bytes()).hexdigest(),
        "cards": len(lexicon_rows),
        "unused_cards": len(unused),
        "slot_distribution": {slot: slot_distribution[slot] for slot in sorted(slot_distribution)},
        "shortlist": len(shortlist),
        "alignment_distribution": dict(sorted(alignment_distribution.items())),
        "forward_terminal_violations": sum(row["forward_alignment"] == "STRUCTURAL_REPAIR_REQUIRED" for row in lexicon_rows),
        "corrected_second_exercise_fields": len(corrected_field_rows),
        "new_card_values": 0,
        "f84_or_f84r_access": False,
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
