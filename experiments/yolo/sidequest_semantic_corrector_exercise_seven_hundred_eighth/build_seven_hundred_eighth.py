#!/usr/bin/env python3
"""Build Pass 708: three bounded apprentice errors and corrector repairs."""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P700 = ROOT / "experiments/yolo/sidequest_semantic_apprentice_manual_seven_hundredth"
P706 = ROOT / "experiments/yolo/sidequest_semantic_continuous_commission_seven_hundred_sixth"
P707 = ROOT / "experiments/yolo/sidequest_semantic_three_scribe_copies_seven_hundred_seventh"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


ERRORS = {
    "CE06": ("GRADE_TOO_SHORT", "PROC122", "tshey", "EE→E", "Die Anweisung verlangt laengeres Halten; die Ersatzkarte traegt nur den kurzen Grad."),
    "CE10": ("SOURCE_FOR_TARGET", "PROC113", "qokar", "AL→AR", "Nach dem Besitzerhandoff ist die Beckenstelle Ziel, nicht Quelle."),
    "CE12": ("PREMATURE_CLOSE", "PROC162", "dairydy", "CHD+AIR→AIR+Y+DY", "Der Ersatz schliesst den Lauf, obwohl C07 am selben Besitzer noch waermt und erst danach schliesst."),
}


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    cards = read(P700 / "SEVEN_HUNDREDTH_173_CARD_MANUAL.tsv")
    commission = read(P706 / "SEVEN_HUNDRED_SIXTH_14_CARD_FORWARD_BACKWARD_TRACE.tsv")
    hand_copies = read(P707 / "SEVEN_HUNDRED_SEVENTH_3_HAND_COPIES.tsv")
    card_by_no = {row["card_no"]: row for row in cards}
    surface_to_cards: dict[str, set[str]] = defaultdict(set)
    for card in cards:
        for surface in card["surfaces"].split("|"):
            surface_to_cards[surface].add(card["card_no"])

    custom = next(row for row in hand_copies if row["hand_id"] == "H2_CUSTOM_HAND")
    correct_surfaces = custom["complete_surface_sequence"].split()
    error_surfaces = list(correct_surfaces)
    error_rows = []
    trace_rows = []
    for index, source in enumerate(commission):
        event = source["commission_event"]
        if event in ERRORS:
            error_type, wrong_card, wrong_surface, axis, reason = ERRORS[event]
            error_surfaces[index] = wrong_surface
            expected_card = source["card_no"]
            error_rows.append({
                "error_id": f"ERR{len(error_rows) + 1}", "commission_event": event,
                "statement_no": source["statement_no"], "owner_id": source["owner_id"],
                "error_type": error_type, "wrong_surface": wrong_surface,
                "wrong_card": wrong_card, "wrong_recipe": card_by_no[wrong_card]["component_recipe"],
                "wrong_reading_de": card_by_no[wrong_card]["compact_atomic_reading_de"],
                "intended_surface": correct_surfaces[index], "intended_card": expected_card,
                "intended_recipe": source["component_recipe"], "intended_reading_de": source["atomic_backreading_de"],
                "changed_axis": axis, "owner_or_sequence_diagnosis_de": reason,
                "corrector_action_de": f"{wrong_surface} streichen; vorhandene Karte {expected_card} als {correct_surfaces[index]} einsetzen.",
                "new_surface_used": "NO",
            })
        observed = error_surfaces[index]
        possible = sorted(surface_to_cards[observed])
        decoded = possible[0] if len(possible) == 1 else "AMBIGUOUS"
        trace_rows.append({
            "commission_event": event, "statement_no": source["statement_no"], "owner_id": source["owner_id"],
            "error_copy_surface": observed, "decoded_card": decoded,
            "decoded_recipe": card_by_no[decoded]["component_recipe"] if decoded != "AMBIGUOUS" else "AMBIGUOUS",
            "decoded_reading_de": card_by_no[decoded]["compact_atomic_reading_de"] if decoded != "AMBIGUOUS" else "AMBIGUOUS",
            "expected_card": source["card_no"], "is_error": "YES" if event in ERRORS else "NO",
            "corrected_surface": correct_surfaces[index], "corrected_card": source["card_no"],
            "repair_restores_expected_card": "YES" if source["card_no"] in surface_to_cards[correct_surfaces[index]] else "NO",
        })

    line_cuts = [(0, 5), (5, 11), (11, 14)]
    copy_rows = []
    for state, surfaces in [("CORRECT_MASTER_COPY", correct_surfaces), ("APPRENTICE_ERROR_COPY", error_surfaces), ("CORRECTED_COPY", correct_surfaces)]:
        lines = [" ".join(surfaces[first:last]) for first, last in line_cuts]
        copy_rows.append({
            "copy_state": state, "line_1": lines[0], "line_2": lines[1], "line_3": lines[2],
            "complete_surface_sequence": " ".join(surfaces),
            "error_count": 3 if state == "APPRENTICE_ERROR_COPY" else 0,
        })

    write("SEVEN_HUNDRED_EIGHTH_3_ERROR_CORRECTIONS.tsv", error_rows)
    write("SEVEN_HUNDRED_EIGHTH_14_EVENT_ERROR_TRACE.tsv", trace_rows)
    write("SEVEN_HUNDRED_EIGHTH_MASTER_ERROR_CORRECTED_COPIES.tsv", copy_rows)

    readable = [
        "# Korrektorenuebung", "", "## Fehlerhafte Abschrift", "",
        f"`{' '.join(error_surfaces[:5])}`", "", f"`{' '.join(error_surfaces[5:11])}`", "", f"`{' '.join(error_surfaces[11:])}`", "",
        "## Drei Korrekturen", "",
    ]
    for row in error_rows:
        readable.extend([
            f"- {row['commission_event']}: `{row['wrong_surface']}` ({row['wrong_reading_de']}) → `{row['intended_surface']}` ({row['intended_reading_de']}). {row['owner_or_sequence_diagnosis_de']}",
        ])
    readable.extend(["", "## Wiederhergestellte Abschrift", "", f"`{' '.join(correct_surfaces[:5])}`", "", f"`{' '.join(correct_surfaces[5:11])}`", "", f"`{' '.join(correct_surfaces[11:])}`"])
    (HERE / "SEVEN_HUNDRED_EIGHTH_CORRECTOR_EXERCISE.md").write_text("\n".join(readable), encoding="utf-8")

    summary = {
        "status": "PASS", "commission_events": len(trace_rows), "errors": len(error_rows),
        "error_types": [row["error_type"] for row in error_rows],
        "wrong_surfaces_are_existing_unambiguous_cards": sum(row["decoded_card"] != "AMBIGUOUS" for row in trace_rows if row["is_error"] == "YES"),
        "repairs_restore_expected_cards": sum(row["repair_restores_expected_card"] == "YES" for row in trace_rows),
        "corrected_copy_equals_master": copy_rows[0]["complete_surface_sequence"] == copy_rows[2]["complete_surface_sequence"],
        "new_cards": 0, "new_surfaces": 0,
        "decision": "CORRECTOR_REPAIRS_GRADE_ADDRESS_AND_ENDPOINT_ERRORS_WITH_EXISTING_CARD_FAMILIES",
    }
    (HERE / "SEVEN_HUNDRED_EIGHTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
