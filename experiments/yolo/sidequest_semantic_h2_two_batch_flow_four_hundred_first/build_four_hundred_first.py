#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
EVENTS = ROOT / "experiments/yolo/sidequest_semantic_thermal_temporal_completion/SELECTED_381_THERMAL_TEMPORAL_INTERLINEAR.tsv"

TRACE = [
    ("E015", "OWNER_PLANT", "YOUNG_TOPS", "SELECT", "junge Spitzen mit Blättern und Blütenständen nehmen"),
    ("E016", "YOUNG_TOPS", "READY_TOPS", "READY", "die Pflanzenportion bereitstellen"),
    ("E017", "READY_TOPS", "PRIMARY_BATCH", "OPEN_BATCH", "den ersten Ansatz eröffnen"),
    ("E018", "PRIMARY_BATCH", "CRUSHED_PRIMARY", "CRUSH", "das Kraut zerstoßen"),
    ("E019", "CRUSHED_PRIMARY", "PRESSED_PRIMARY", "PRESS", "den ersten Ansatz abpressen"),
    ("E020", "PRESSED_PRIMARY", "PRESSED_PRIMARY", "RESUME", "diesen Arbeitsposten weiterführen"),
    ("E021", "PRESSED_PRIMARY", "PRESSED_PRIMARY", "RESUME", "denselben Posten weiterführen"),
    ("E022", "PRESSED_PRIMARY", "MEASURED_PRIMARY", "MEASURE", "das Sollmaß des ersten Auszugs setzen"),
    ("E023", "MEASURED_PRIMARY", "MEASURED_PRIMARY", "RESUME", "den abgemessenen Posten aktiv halten"),
    ("E024", "MEASURED_PRIMARY", "FOLLOW_ON_FRAME", "NEXT_BATCH", "einen Folgeansatz eröffnen"),
    ("E025", "FOLLOW_ON_FRAME", "FOLLOW_ON_BATCH", "OPEN_BATCH", "den zweiten Ansatz ansetzen"),
    ("E026", "FOLLOW_ON_BATCH", "FOLLOW_ON_BATCH", "NEXT_CONTINUE", "danach mit dem zweiten Ansatz fortfahren"),
    ("E027", "FOLLOW_ON_BATCH", "FOLLOW_ON_BATCH", "CONTINUE", "den Gang fortsetzen"),
    ("E028", "FOLLOW_ON_BATCH", "PRIMARY_AND_FOLLOW_ON", "REJOIN_PREVIOUS", "den ersten Ansatz wieder hinzunehmen"),
    ("E029", "PRIMARY_AND_FOLLOW_ON", "PRIMARY_AND_FOLLOW_ON", "CONTINUE", "beide Ansätze gemeinsam weiterführen"),
    ("E030", "PRIMARY_AND_FOLLOW_ON", "MEASURED_COMBINATION", "MEASURE", "das Sollmaß der Verbindung setzen"),
    ("E031", "MEASURED_COMBINATION", "SAME_STOCK_COMBINATION", "SOURCE", "aus demselben Vorrat ergänzen"),
    ("E032", "SAME_STOCK_COMBINATION", "VESSEL", "PLACE_IN_VESSEL", "alles in das bereitstehende Gefäß geben"),
    ("E033", "VESSEL", "PRIMARY_IN_VESSEL", "LOAD_BATCH", "den ersten Ansatz in das Gefäß geben"),
    ("E034", "PRIMARY_IN_VESSEL", "TWO_BATCH_VESSEL", "LOAD_BATCH", "den Folgeansatz dazugeben"),
    ("E035", "TWO_BATCH_VESSEL", "TWO_BATCH_VESSEL", "RESUME", "diesen Gefäßposten weiterführen"),
    ("E036", "TWO_BATCH_VESSEL", "SOFT_PREPARATION", "SOFT_STAGE", "bis zur weichen Zielstufe durcharbeiten"),
    ("E037", "SOFT_PREPARATION", "SOFT_PREPARATION", "RESUME", "diese weiche Zubereitung aufnehmen"),
    ("E038", "SOFT_PREPARATION", "EXTERNAL_APPLICATION", "APPLY", "auf die bezeichnete harte Stelle auflegen"),
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
    h2 = [row for row in read() if row["record_unit_id"] == "H2"]
    by_id = {row["event_id"]: row for row in h2}
    rows = []
    for order, (event_id, before, after, operation, reading) in enumerate(TRACE, 1):
        source = by_id[event_id]
        rows.append({
            "order": order,
            "event_id": event_id,
            "locus": source["locus"],
            "statement_id": source["statement_id"],
            "surface": source["surface_display"],
            "joint_tuple_id": source["joint_tuple_id"],
            "object_before": before,
            "operation": operation,
            "object_after": after,
            "card_value_de": source["concrete_word_reading_de"],
            "working_event_reading_de": reading,
        })
    write("FOUR_HUNDRED_FIRST_24_EVENT_H2_FLOW.tsv", rows)

    nodes = [
        ("OWNER_PLANT", "abgebildete Pflanze"),
        ("YOUNG_TOPS", "junge Spitzen, Blätter und Blütenstände"),
        ("PRIMARY_BATCH", "erster zerstoßener und abgepresster Ansatz"),
        ("MEASURED_PRIMARY", "abgemessener erster Auszug"),
        ("FOLLOW_ON_BATCH", "zweiter Ansatz aus demselben Pflanzenvorrat"),
        ("PRIMARY_AND_FOLLOW_ON", "wieder vereinigter Erst- und Folgeansatz"),
        ("MEASURED_COMBINATION", "abgemessene Verbindung beider Ansätze"),
        ("VESSEL", "Arbeitsgefäß"),
        ("TWO_BATCH_VESSEL", "beide Ansätze im Gefäß"),
        ("SOFT_PREPARATION", "weich gearbeitete Auflagenzubereitung"),
        ("EXTERNAL_APPLICATION", "äußerliche Auflage auf harte Stelle"),
    ]
    write("FOUR_HUNDRED_FIRST_11_OBJECT_NODES.tsv", [
        {"node_order": n, "node_id": node, "working_object_de": label}
        for n, (node, label) in enumerate(nodes, 1)
    ])

    comparisons = [
        {"record": "H1", "order_device": "OL continuation", "branch_device": "none", "material_pattern": "single preparation with continuation"},
        {"record": "H2", "order_device": "OT+OL and OL+OR", "branch_device": "follow-on then rejoin", "material_pattern": "two batches recombined in a vessel"},
        {"record": "H3", "order_device": "CH+OL and OK+OL", "branch_device": "reserve then recall", "material_pattern": "main extract plus reserved flower use"},
        {"record": "H5", "order_device": "CH+OL, OT and doubled OK", "branch_device": "repeat/reuse only", "material_pattern": "previous item and fresh follow-on item"},
    ]
    write("FOUR_HUNDRED_FIRST_HERBAL_ORDER_COMPARISON.tsv", comparisons)

    summary = {
        "status": "PASS",
        "events": len(rows),
        "statements": len({row["statement_id"] for row in rows}),
        "object_nodes": len(nodes),
        "material_batches": 2,
        "rejoin_event": "E028",
        "application_event": "E038",
    }
    (HERE / "FOUR_HUNDRED_FIRST_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
