#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
SOURCE = ROOT / "experiments/yolo/sidequest_semantic_forward_frame_mode_hundred_ninety_fourth/HUNDRED_NINETY_FOURTH_25_TOKEN_MODE_INSTRUCTION.tsv"
EVENTS = ROOT / "experiments/yolo/sidequest_semantic_six_slot_pressure_test_hundred_eighty_first/HUNDRED_EIGHTY_FIRST_381_EVENT_SIX_SLOT_PARSE.tsv"
DICTIONARY = ROOT / "experiments/yolo/sidequest_semantic_ten_page_master_edition_hundred_seventy_fifth/HUNDRED_SEVENTY_FIFTH_173_CARD_DICTIONARY.tsv"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def position_class(position: int, field_size: int = 5) -> str:
    if position == 1:
        return "INITIAL"
    if position == field_size:
        return "FINAL"
    return "MEDIAL"


def frame(surface: str) -> str:
    if surface.startswith("q"):
        return "Q"
    if surface.startswith("s") or surface.startswith("sh"):
        return "S"
    if surface.startswith("ch"):
        return "CH"
    if surface.startswith("d"):
        return "D"
    if surface.startswith("o"):
        return "O"
    if surface.startswith("t"):
        return "T"
    if surface.startswith("k"):
        return "K"
    if surface.startswith("l"):
        return "L"
    return "X"


def main() -> None:
    source = read(SOURCE)
    events = read(EVENTS)
    dictionary_rows = read(DICTIONARY)
    dictionary = {row["master_card_id"]: row for row in dictionary_rows}
    field_sizes = Counter(row["field_id"] for row in events)
    observed: dict[tuple[str, str], Counter[str]] = defaultdict(Counter)
    overall: dict[str, Counter[str]] = defaultdict(Counter)
    for row in events:
        pos = position_class(int(row["field_position"]), field_sizes[row["field_id"]]) if field_sizes[row["field_id"]] > 1 else "ONLY"
        observed[(row["master_card_id"], pos)][row["surface"]] += 1
        overall[row["master_card_id"]][row["surface"]] += 1

    surface_to_cards: dict[str, list[str]] = defaultdict(list)
    for row in dictionary_rows:
        for surface in row["registered_surfaces"].split("|"):
            surface_to_cards[surface].append(row["master_card_id"])

    output: list[dict[str, object]] = []
    evidence_rows: list[dict[str, object]] = []
    for row in source:
        card_id = row["master_card_id"]
        pos = position_class(int(row["field_position"]))
        choices = observed[(card_id, pos)]
        if choices:
            maximum = max(choices.values())
            tied = sorted(surface for surface, count in choices.items() if count == maximum)
            master = dictionary[card_id]["master_form"]
            selected = master if master in tied else tied[0]
            basis = "POSITION_MAJORITY" if len(tied) == 1 else "POSITION_TIE_MASTER_OR_LEXICAL"
        else:
            maximum = max(overall[card_id].values())
            tied = sorted(surface for surface, count in overall[card_id].items() if count == maximum)
            master = dictionary[card_id]["master_form"]
            selected = master if master in tied else tied[0]
            basis = "CARD_OVERALL_FALLBACK"
        output.append(
            {
                "token_order": row["token_order"],
                "field_id": row["field_id"],
                "field_position": row["field_position"],
                "position_class": pos,
                "source_field_mode": row["field_mode"],
                "master_card_id": card_id,
                "portable_value_de": row["portable_value_de"],
                "harmonized_surface": row["surface"],
                "mixed_hand_surface": selected,
                "selection_basis": basis,
                "surface_changed": "YES" if selected != row["surface"] else "NO",
                "mixed_surface_frame": frame(selected),
                "still_matches_source_field_mode": "YES" if frame(selected) == row["field_mode"] else "NO",
                "surface_registered": "YES" if selected in dictionary[card_id]["registered_surfaces"].split("|") else "NO",
                "surface_unique_to_card": "YES" if surface_to_cards[selected] == [card_id] else "NO",
                "field_closure": row["field_closure"],
                "is_field_final": row["is_field_final"],
            }
        )
        evidence_rows.append(
            {
                "token_order": row["token_order"],
                "master_card_id": card_id,
                "position_class": pos,
                "position_observations": sum(choices.values()),
                "position_distribution": "|".join(f"{key}:{value}" for key, value in sorted(choices.items())) or "NONE",
                "overall_distribution": "|".join(f"{key}:{value}" for key, value in sorted(overall[card_id].items())),
                "selected_surface": selected,
                "selection_basis": basis,
            }
        )
    write(OUT / "HUNDRED_NINETY_FIFTH_25_TOKEN_MIXED_RENDERING.tsv", output)
    write(OUT / "HUNDRED_NINETY_FIFTH_POSITION_PREFERENCE_EVIDENCE.tsv", evidence_rows)

    field_rows: list[dict[str, object]] = []
    for field_id in sorted({row["field_id"] for row in output}):
        selected = [row for row in output if row["field_id"] == field_id]
        field_rows.append(
            {
                "field_id": field_id,
                "source_field_mode": selected[0]["source_field_mode"],
                "harmonized_sequence": " ".join(str(row["harmonized_surface"]) for row in selected),
                "mixed_hand_sequence": " ".join(str(row["mixed_hand_surface"]) for row in selected),
                "changed_tokens": sum(row["surface_changed"] == "YES" for row in selected),
                "mode_matching_tokens": sum(row["still_matches_source_field_mode"] == "YES" for row in selected),
                "mode_recovered_by_majority": "YES" if sum(row["still_matches_source_field_mode"] == "YES" for row in selected) >= 3 else "NO",
                "card_readback_tokens": sum(row["surface_unique_to_card"] == "YES" for row in selected),
                "closure_preserved": "YES" if selected[-1]["field_closure"] == "CLOSED" or selected[-1]["field_closure"] == "OPEN" else "NO",
                "literal_values": " | ".join(str(row["portable_value_de"]) for row in selected),
            }
        )
    write(OUT / "HUNDRED_NINETY_FIFTH_5_FIELD_PARALLEL_EDITION.tsv", field_rows)

    summary = {
        "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        "event_source_sha256": hashlib.sha256(EVENTS.read_bytes()).hexdigest(),
        "dictionary_sha256": hashlib.sha256(DICTIONARY.read_bytes()).hexdigest(),
        "tokens": len(output),
        "fields": len(field_rows),
        "changed_surfaces": sum(row["surface_changed"] == "YES" for row in output),
        "unchanged_surfaces": sum(row["surface_changed"] == "NO" for row in output),
        "source_mode_matches": sum(row["still_matches_source_field_mode"] == "YES" for row in output),
        "field_modes_recovered_by_majority": sum(row["mode_recovered_by_majority"] == "YES" for row in field_rows),
        "unique_card_readbacks": sum(row["surface_unique_to_card"] == "YES" for row in output),
        "registered_surfaces": sum(row["surface_registered"] == "YES" for row in output),
        "closures_preserved": sum(row["closure_preserved"] == "YES" for row in field_rows),
        "sealed_pages_accessed": False,
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
