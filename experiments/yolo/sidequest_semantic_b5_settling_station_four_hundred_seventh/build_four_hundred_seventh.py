#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
EVENTS = ROOT / "experiments/yolo/sidequest_semantic_thermal_temporal_completion/SELECTED_381_THERMAL_TEMPORAL_INTERLINEAR.tsv"

TRACE = [
    ("E364", "SETTLING_STATION", "HOLD_SETTLE", "die Charge an der Absetzstelle halten"),
    ("E365", "TARGET_SITE", "ASSIGN_TARGET", "die örtliche Zielstelle wählen"),
    ("E366", "ACTIVE_CHARGE", "CONTINUE", "den laufenden Posten weiterführen"),
    ("E367", "WARM_STATE", "KEEP_WARM", "ihn warm halten"),
    ("E368", "TARGET_SITE", "WORK_AT_SITE", "an der Zielstelle umsetzen"),
    ("E369", "MEASURE", "SET_MEASURE", "das Sollmaß einstellen"),
    ("E370", "ACTIVE_CHARGE", "CONTINUE", "den bemessenen Posten weiterführen"),
    ("E371", "SECOND_OPENING", "SELECT_SECOND_OPENING", "die zweite Öffnung der Station wählen"),
    ("E372", "ACTIVE_CHARGE", "WORK_THROUGH", "die Charge durch den gewählten Ausgang durcharbeiten"),
]


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
    trace_rows = []
    for order, (event_id, role, operation, reading) in enumerate(TRACE, 1):
        source = by_id[event_id]
        trace_rows.append({
            "order": order,
            "event_id": event_id,
            "locus": source["locus"],
            "surface": source["surface_display"],
            "joint_tuple_id": source["joint_tuple_id"],
            "role": role,
            "operation": operation,
            "working_reading_de": reading,
            "owner": "B5_LEFT_OPEN_FRINGE_STATION",
        })
    write("FOUR_HUNDRED_SEVENTH_NINE_EVENT_B5_TRACE.tsv", trace_rows)

    comparison = [
        {"feature": "SHEDAL", "b3_s021": "after measure; before tempered state", "b5_s003": "instruction head at visible left open station", "shared_value": "Absetzstelle"},
        {"feature": "TEMPERATURE", "b3_s021": "SHECTHY=temperiert", "b5_s003": "LOL=warm", "shared_value": "charge reaches controlled thermal state"},
        {"feature": "MEASURE", "b3_s021": "SAIIN before settling", "b5_s003": "AIIN after warm target work", "shared_value": "Sollmaß is station-local"},
        {"feature": "TARGET", "b3_s021": "AL after resumed item", "b5_s003": "AL then CHD+AL", "shared_value": "local target within owner station"},
        {"feature": "END", "b3_s021": "DALCHDY terminal close", "b5_s003": "DAIIIN+CHEDY remains open at record end", "shared_value": "B5 hands charge onward rather than closing"},
    ]
    write("FOUR_HUNDRED_SEVENTH_B3_B5_STATION_COMPARISON.tsv", comparison)

    endings = [
        {"model": "SECOND_OUTLET_TRANSFER", "daiiin": "zweite Öffnung", "chedy": "laufenden Posten hindurcharbeiten", "score": 9, "decision": "SELECTED", "reason": "visible station has multiple open ends and CHEDY is nonterminal"},
        {"model": "SECOND_PROCESS_STAGE", "daiiin": "zweite Arbeitsstufe", "chedy": "weiter durcharbeiten", "score": 7, "decision": "RIVAL", "reason": "fits IIN grade but ignores the open-fringe owner geometry"},
        {"model": "SECOND_DOSE_MIX", "daiiin": "zweites Maß", "chedy": "einrühren", "score": 5, "decision": "RIVAL", "reason": "possible workshop phrase but duplicates preceding AIIN measure"},
    ]
    write("FOUR_HUNDRED_SEVENTH_THREE_ENDING_MODELS.tsv", endings)

    summary = {
        "status": "PASS",
        "events": len(trace_rows),
        "loci": len({row["locus"] for row in trace_rows}),
        "owner": "B5_LEFT_OPEN_FRINGE_STATION",
        "selected_ending": "SECOND_OUTLET_TRANSFER",
        "record_terminal_close": False,
    }
    (HERE / "FOUR_HUNDRED_SEVENTH_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
