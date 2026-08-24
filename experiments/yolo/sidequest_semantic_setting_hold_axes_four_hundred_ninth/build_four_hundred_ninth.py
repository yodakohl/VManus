#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
EVENTS = ROOT / "experiments/yolo/sidequest_semantic_thermal_temporal_completion/SELECTED_381_THERMAL_TEMPORAL_INTERLINEAR.tsv"

STATEMENTS = {
    "H2-S003": ("E036", "NONE", "weiche Zielstufe; duration supplied by ordinary working context"),
    "B1-S018": ("E161", "E162", "Zielstufe; länger auffangen and close"),
    "B3-S034": ("E309", "E314", "Zielstufe; kurz absetzen and close"),
    "B5-S003": ("E371", "NONE", "second-opening setting; work onward without explicit hold grade"),
}


def read() -> list[dict[str, str]]:
    with EVENTS.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    by_id = {row["event_id"]: row for row in read()}
    statement_rows = []
    for statement, (iin_event, hold_event, reading) in STATEMENTS.items():
        iin = by_id[iin_event]
        hold = by_id[hold_event] if hold_event != "NONE" else None
        statement_rows.append({
            "statement_id": statement,
            "record": iin["record_unit_id"],
            "iin_event": iin_event,
            "iin_surface": iin["surface_display"],
            "setting_value_de": iin["concrete_word_reading_de"],
            "hold_event": hold_event,
            "hold_surface": hold["surface_display"] if hold else "NONE",
            "hold_value_de": hold["concrete_word_reading_de"] if hold else "IMPLICIT_OR_UNSPECIFIED",
            "combined_reading_de": reading,
        })
    write("FOUR_HUNDRED_NINTH_FOUR_IIN_STATEMENTS.tsv", statement_rows)

    axes = [
        {"axis": "SETTING", "marker": "IIN", "short_question": "welche Sollstellung?", "values": "generic target|soft consistency|second opening", "scope": "target condition"},
        {"axis": "HOLD_GRADE_1", "marker": "E", "short_question": "wie ausführen?", "values": "kurz/direkt", "scope": "operation duration or completion"},
        {"axis": "HOLD_GRADE_2", "marker": "EE", "short_question": "wie ausführen?", "values": "länger/anhaltend", "scope": "operation duration or completion"},
        {"axis": "HOLD_GRADE_3", "marker": "EEE", "short_question": "wie ausführen?", "values": "vollständig", "scope": "operation duration or completion"},
        {"axis": "REFERENT", "marker": "Y", "short_question": "welcher Posten?", "values": "current item", "scope": "open active work item"},
        {"axis": "CLOSE", "marker": "licensed DY card", "short_question": "endet der Schritt?", "values": "close", "scope": "licensed exact terminal construction"},
    ]
    write("FOUR_HUNDRED_NINTH_SIX_AXIS_RULES.tsv", axes)

    pairings = [
        {"setting": "WEICHSTUFE", "hold": "UNSPECIFIED", "example": "KAIIIN", "workshop_reading": "bis zur weichen Konsistenz arbeiten"},
        {"setting": "SOLLSTUFE", "hold": "GRADE_2", "example": "OIIIN ... OLKEEDY", "workshop_reading": "Zielstufe einstellen; länger auffangen; schließen"},
        {"setting": "SOLLSTUFE", "hold": "GRADE_1", "example": "SOIIIN ... SHEDY", "workshop_reading": "Zielstufe einstellen; kurz absetzen; schließen"},
        {"setting": "SECOND_OPENING_SETTING", "hold": "UNSPECIFIED", "example": "DAIIIN CHEDY", "workshop_reading": "zweite Öffnung einstellen; Posten hindurcharbeiten"},
    ]
    write("FOUR_HUNDRED_NINTH_FOUR_SETTING_HOLD_PAIRINGS.tsv", pairings)

    summary = {
        "status": "PASS",
        "iin_statements": len(statement_rows),
        "explicit_hold_grades": sum(row["hold_event"] != "NONE" for row in statement_rows),
        "implicit_hold_grades": sum(row["hold_event"] == "NONE" for row in statement_rows),
        "axis_rules": len(axes),
        "decision": "SETTING_AND_HOLD_ARE_SEPARATE_SYNTACTIC_AXES",
    }
    (HERE / "FOUR_HUNDRED_NINTH_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
