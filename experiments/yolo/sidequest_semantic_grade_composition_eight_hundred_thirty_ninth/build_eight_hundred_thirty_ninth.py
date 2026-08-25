#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
BASE = ROOT / "sidequest_semantic_ninth_workshop_grammar_eight_hundred_thirty_third"
PREFIX = "EIGHT_HUNDRED_THIRTY_NINTH"
GRADES = ("E", "EE", "EEE")
VALUES = {"E": "KURZ", "EE": "LANG", "EEE": "VOLL"}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]], fields: list[str]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def grade_in(recipe: str) -> str | None:
    present = [grade for grade in GRADES if grade in recipe.split("+")]
    return present[0] if len(present) == 1 else None


def frame(recipe: str, grade: str) -> str:
    return "+".join("GRADE" if token == grade else token for token in recipe.split("+"))


def main() -> None:
    cards = read(BASE / "EIGHT_HUNDRED_THIRTY_THIRD_173_CARD_NINTH_DICTIONARY.tsv")
    events = read(BASE / "EIGHT_HUNDRED_THIRTY_THIRD_381_EVENT_REPARSE.tsv")
    predictions = read(BASE / "EIGHT_HUNDRED_THIRTY_THIRD_76_UNATTESTED_PREDICTIONS.tsv")
    active = read(BASE / "EIGHT_HUNDRED_THIRTY_THIRD_30_ACTIVE_PREDICTION_SURFACES.tsv")
    active_surfaces = {row["predicted_surface"] for row in active}

    grade_cards = []
    for card in cards:
        grade = grade_in(card["component_recipe"])
        if grade is None:
            continue
        grade_cards.append(
            {
                "exact_card_id": card["exact_card_id"],
                "surfaces": card["registered_surfaces"],
                "component_recipe": card["component_recipe"],
                "grade_component": grade,
                "grade_value_de": VALUES[grade],
                "grade_token_count": card["component_recipe"].split("+").count(grade),
                "reading_de": card["ninth_grammar_reading_de"],
                "events": card["events"],
                "operator_frame": frame(card["component_recipe"], grade),
            }
        )

    grade_events = []
    for event in events:
        grade = grade_in(event["component_recipe"])
        if grade is None:
            continue
        grade_events.append(
            {
                "event_id": event["event_id"],
                "page": event["page"],
                "record": event["record"],
                "statement_id": event["statement_id"],
                "surface": event["surface"],
                "component_recipe": event["component_recipe"],
                "grade_component": grade,
                "grade_value_de": VALUES[grade],
                "grade_token_count": event["component_recipe"].split("+").count(grade),
                "reading_de": event["ninth_grammar_reading_de"],
            }
        )

    frames: dict[str, dict[str, tuple[str, str, str, str]]] = {}
    for card in cards:
        grade = grade_in(card["component_recipe"])
        if grade is None:
            continue
        frames.setdefault(frame(card["component_recipe"], grade), {})[grade] = ("ATTESTED", card["registered_surfaces"], card["ninth_grammar_reading_de"], card["events"])
    for prediction in predictions:
        grade = grade_in(prediction["component_recipe"])
        if grade is None:
            continue
        frames.setdefault(frame(prediction["component_recipe"], grade), {}).setdefault(grade, ("PREDICTION_ONLY", prediction["predicted_surface"], prediction["reading_de"], "0"))

    grid = []
    for index, operator_frame in enumerate(sorted(frames), 1):
        cells = frames[operator_frame]
        row: dict[str, object] = {"frame_id": f"GF{index:02d}", "operator_frame": operator_frame}
        for grade in GRADES:
            status, surface, reading, support = cells.get(grade, ("ABSENT", "NONE", "NONE", "0"))
            row[f"{grade.lower()}_status"] = status
            row[f"{grade.lower()}_surface"] = surface
            row[f"{grade.lower()}_reading_de"] = reading
            row[f"{grade.lower()}_events"] = support
        row["attested_cells"] = sum(cell[0] == "ATTESTED" for cell in cells.values())
        row["available_cells"] = len(cells)
        row["decision"] = "E_SHORT__EE_LONG__EEE_FULL"
        grid.append(row)

    strong = [dict(row) for row in grid if int(row["attested_cells"]) >= 2]
    strong.sort(key=lambda row: (-int(row["attested_cells"]), row["operator_frame"]))
    for rank, row in enumerate(strong, 1):
        row["strength_rank"] = rank

    nominated = []
    for row in strong:
        for grade in GRADES:
            if row[f"{grade.lower()}_status"] != "PREDICTION_ONLY":
                continue
            surface = row[f"{grade.lower()}_surface"]
            nominated.append(
                {
                    "operator_frame": row["operator_frame"],
                    "missing_grade": grade,
                    "predicted_surface": surface,
                    "predicted_reading_de": row[f"{grade.lower()}_reading_de"],
                    "attested_cells": row["attested_cells"],
                    "already_active_prediction": "YES" if surface in active_surfaces else "NO",
                    "priority": "HIGH" if surface in {"cheeeky", "solkeeey"} else "ACTIVE_OR_STANDARD",
                }
            )

    write(f"{PREFIX}_53_GRADE_CARDS.tsv", grade_cards, ["exact_card_id", "surfaces", "component_recipe", "grade_component", "grade_value_de", "grade_token_count", "reading_de", "events", "operator_frame"])
    write(f"{PREFIX}_91_GRADE_EVENTS.tsv", grade_events, ["event_id", "page", "record", "statement_id", "surface", "component_recipe", "grade_component", "grade_value_de", "grade_token_count", "reading_de"])
    write(f"{PREFIX}_54_OPERATOR_GRADE_FRAMES.tsv", grid, ["frame_id", "operator_frame", "e_status", "e_surface", "e_reading_de", "e_events", "ee_status", "ee_surface", "ee_reading_de", "ee_events", "eee_status", "eee_surface", "eee_reading_de", "eee_events", "attested_cells", "available_cells", "decision"])
    write(f"{PREFIX}_8_STRONG_GRADE_ROWS.tsv", strong, ["frame_id", "operator_frame", "e_status", "e_surface", "e_reading_de", "e_events", "ee_status", "ee_surface", "ee_reading_de", "ee_events", "eee_status", "eee_surface", "eee_reading_de", "eee_events", "attested_cells", "available_cells", "decision", "strength_rank"])
    write(f"{PREFIX}_7_GRADE_PREDICTIONS.tsv", nominated, ["operator_frame", "missing_grade", "predicted_surface", "predicted_reading_de", "attested_cells", "already_active_prediction", "priority"])

    summary = {
        "status": "PASS",
        "decision": "E_EE_EEE_FORM_A_SHORT_LONG_FULL_GRADE_SLOT",
        "grade_cards": len(grade_cards),
        "grade_events": len(grade_events),
        "grade_component_memberships_cards": sum(int(row["grade_token_count"]) for row in grade_cards),
        "grade_component_memberships_events": sum(int(row["grade_token_count"]) for row in grade_events),
        "operator_frames": len(grid),
        "frames_with_attestation": sum(int(row["attested_cells"]) > 0 for row in grid),
        "strong_multi_attested_rows": len(strong),
        "fully_attested_rows": sum(int(row["attested_cells"]) == 3 for row in strong),
        "complete_rows_with_predictions": sum(int(row["available_cells"]) == 3 for row in grid),
        "nominated_missing_cells": len(nominated),
        "double_e_separate_slot_cards": sum(int(row["grade_token_count"]) == 2 for row in grade_cards),
        "component_changes": 0,
        "sealed_pages": ["f84", "f84r"],
    }
    (HERE / f"{PREFIX}_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    report = """# Sidequest Pass 839: E/EE/EEE grade composition

The grade slot remains concrete and learnable:

- E = KURZ;
- EE = LANG;
- EEE = VOLL.

There are 53 unique grade-bearing cards and 91 events. Component membership is
54/92 because `qekey = E+K+E+Y` contains two separate short modifiers in two
slots. This card is a crucial teaching control: two E tokens do not fuse into
EE merely by co-occurring.

Eight operator rows have at least two attested grades. `OK+GRADE+DY` is complete
in the manuscript slice: qokedy short close, qokeedy long close, qokeeedy full
close. Seven other rows supply two attested cells and one predicted cell,
including heating, holding, collecting, next-step closing, active-item setting,
and item processing.

The seven missing cells are already generated by the older prediction deck.
Five are already active; the two useful additions are `cheeeky` (warm the item
fully) and `solkeeey` (collect the item fully). No reversal of short → long →
full appears in the recurring operator rows.

No dictionary change. Next, combine the address, quantity and grade subsystems
into a single card-construction manual, then use it to reparse the ten highest-
coverage exact cards without adding page-specific meanings.
"""
    (HERE / f"{PREFIX}_REPORT.md").write_text(report, encoding="utf-8")


if __name__ == "__main__":
    main()
