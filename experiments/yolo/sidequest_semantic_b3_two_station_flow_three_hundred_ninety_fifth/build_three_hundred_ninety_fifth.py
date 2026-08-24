#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
P393 = ROOT / "experiments/yolo/sidequest_semantic_owner_faithful_decomposition_three_hundred_ninety_third"

STATION_A = "B3_MARGIN_TO_MAIN_GAP_UNRESOLVED"
STATION_B = "B3_MAIN_ARCH_LINKED_PAIR"

TRACE = [
    ("E285", STATION_A, "UNSET_LOCAL_STATION_A", "LOCAL_STATION_A", "INITIALIZE_STATION", "CHEEDAR", "örtliche Beckenstation einrichten"),
    ("E286", STATION_A, "LOCAL_STATION_A", "SETTLING_THRESHOLD_A", "SET_SETTLING_THRESHOLD", "CHLD+AIIN", "Absetzstand festlegen"),
    ("E287", STATION_A, "SETTLING_THRESHOLD_A", "WORKED_BATCH_A", "WORK_CURRENT", "CHED+Y", "örtlichen Posten durcharbeiten"),
    ("E288", STATION_A, "WORKED_BATCH_A", "PORTION_ADDED_BATCH_A", "ADD_PORTION", "OK+AIN", "eine Portion zugeben"),
    ("E289", STATION_A, "PORTION_ADDED_BATCH_A", "READY_BATCH_A", "CHECK_READY", "CTH+Y", "Bereitschaft feststellen"),
    ("E290", STATION_A, "READY_BATCH_A", "CLEARPOINT_BATCH_A", "CHECK_CLEARPOINT", "CHEALROR", "Klarpunkt feststellen"),
    ("E291", STATION_B, "NEW_LOCAL_OWNER_B", "CLOSED_RECEIVING_STAGE_B", "RECEIVE_LONG_CLOSE", "SOLK+EE+DY", "am neuen Besitzer länger auffangen und schließen"),
]


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    cards = [row for row in read(P393 / "THREE_HUNDRED_NINETY_THIRD_25_COMPONENT_NOMENCLATOR_READINGS.tsv") if row["statement_id"] == "B3-S026"]
    by_event = {row["event_id"]: row for row in cards}
    trace_rows = []
    for order, (event_id, station, before, after, operation, cue, reading) in enumerate(TRACE, 1):
        source = by_event[event_id]
        trace_rows.append({
            "order": order,
            "event_id": event_id,
            "copy_surface": source["copy_surface"],
            "joint_tuple_id": source["joint_tuple_id"],
            "visible_owner_zone": station,
            "active_before": before,
            "operation": operation,
            "component_cue": cue,
            "active_after": after,
            "working_reading_de": reading,
            "physical_direction_claim": "NONE",
            "global_flow_claim": "NONE",
        })
    write("THREE_HUNDRED_NINETY_FIFTH_SEVEN_EVENT_TWO_STATION_TRACE.tsv", trace_rows)

    reset_rows = [
        {
            "after_event": "E290",
            "before_event": "E291",
            "from_owner": STATION_A,
            "to_owner": STATION_B,
            "textual_relation": "SAME_STATEMENT_WORKFLOW_NEXT",
            "material_identity_carried": "NO_NOT_VISIBLE",
            "physical_connection_visible": "NO",
            "direction_visible": "NO",
            "required_reader_action": "RESET_OWNER_KEEP_ONLY_WORKFLOW_ORDER",
        }
    ]
    write("THREE_HUNDRED_NINETY_FIFTH_OWNER_RESET.tsv", reset_rows)

    stage_rows = [
        {"stage": "A1", "owner_zone": STATION_A, "event_ids": "E285|E286", "stage_reading_de": "örtliche Station und Absetzstand einrichten", "next_relation": "LOCAL_STATE_PROGRESS"},
        {"stage": "A2", "owner_zone": STATION_A, "event_ids": "E287|E288", "stage_reading_de": "Posten durcharbeiten und Portion zugeben", "next_relation": "LOCAL_STATE_PROGRESS"},
        {"stage": "A3", "owner_zone": STATION_A, "event_ids": "E289|E290", "stage_reading_de": "Bereitschaft und Klarpunkt prüfen", "next_relation": "WORKFLOW_NEXT_WITH_OWNER_RESET"},
        {"stage": "B1", "owner_zone": STATION_B, "event_ids": "E291", "stage_reading_de": "am neuen Besitzer länger auffangen und schließen", "next_relation": "END"},
    ]
    write("THREE_HUNDRED_NINETY_FIFTH_FOUR_LOCAL_STAGES.tsv", stage_rows)

    comparison = [
        {"sequence": "H4_FULL_RECORD", "events": 18, "visible_owner_zones": 1, "statement_handoffs": 3, "material_genealogy": "CONTINUOUS_WORKING_DEFAULT", "physical_flow_claim": "NONE_REQUIRED"},
        {"sequence": "B3_S026", "events": 7, "visible_owner_zones": 2, "statement_handoffs": 0, "material_genealogy": "BROKEN_AT_E290_E291", "physical_flow_claim": "NONE"},
    ]
    write("THREE_HUNDRED_NINETY_FIFTH_H4_B3_FLOW_CONTRAST.tsv", comparison)

    reading = """# Pass 395 — B3-S026 als zweistufiger Stationsgang

Am nur örtlich bezeichneten ersten Posten richte die Beckenstation ein und lege
den Absetzstand fest. Arbeite den dortigen Posten durch, gib eine Portion zu und
prüfe erst die Bereitschaft, dann den Klarpunkt.

**Neuer sichtbarer Besitzer; keine gezeichnete Verbindung:** Am unteren
Figurenpaar fange den dortigen Posten länger auf und schließe den Schritt.

## Was der Satz verbindet

Der Text verbindet die beiden Teile als Arbeitsreihenfolge. Er beweist nicht,
dass dieselbe Flüssigkeit von Station A nach Station B fließt. Der Bildwechsel
setzt den Gegenstand zurück; nur „danach kommt der Empfangsschritt“ bleibt.

## Kurze Kartenlesung

`cheedar` Station → `chldaiin` Absetzstand → `chdy` bearbeiten → `okain`
Portion zugeben → `cthy` bereit → `chealror` Klarpunkt → **OWNER RESET** →
`olkeedy` länger auffangen; Schluss.
"""
    (HERE / "THREE_HUNDRED_NINETY_FIFTH_CONTINUOUS_B3_READING.md").write_text(reading, encoding="utf-8")
    report = """# Pass 395 — Arbeitsreihenfolge ja, sichtbarer Flüssigkeitsweg nein

B3-S026 besitzt eine klare operative Zustandsfolge, aber zwei sichtbare
Besitzerzonen. E285–E290 richten eine lokale Station ein, bearbeiten eine Charge
und prüfen Bereitschaft/Klarpunkt. E291 beginnt nach einem Bildreset am unteren
Paar und schließt dort einen längeren Empfangsschritt.

Die beste kreative Lesung bleibt daher konkret, ohne einen gezeichneten Kanal zu
erfinden. Grammatisch ist es ein Satz; ikonographisch sind es zwei lokale
Stationen. Im Gegensatz zum einbesitzigen H4-Artikel darf die Materialidentität
über den Reset nicht automatisch fortgeschrieben werden.

Als nächstes soll ein Werkstattschreiber genau diese Differenz in ein
Seitenlayout übersetzen: durchgehende Satzmarkierung, aber sichtbarer neuer
Besitzer und kein Verbindungspfeil.
"""
    (HERE / "THREE_HUNDRED_NINETY_FIFTH_REPORT.md").write_text(report, encoding="utf-8")
    summary = {
        "status": "PASS",
        "events": len(trace_rows),
        "visible_owner_zones": len({row["visible_owner_zone"] for row in trace_rows}),
        "owner_resets": len(reset_rows),
        "local_stages": len(stage_rows),
        "physical_connections_claimed": 0,
        "global_flows_claimed": 0,
    }
    (HERE / "THREE_HUNDRED_NINETY_FIFTH_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
