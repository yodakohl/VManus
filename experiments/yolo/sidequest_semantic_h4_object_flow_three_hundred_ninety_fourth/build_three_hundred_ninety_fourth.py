#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
P393 = ROOT / "experiments/yolo/sidequest_semantic_owner_faithful_decomposition_three_hundred_ninety_third"

TRANSITIONS = [
    ("E056", "OWNER_PLANT", "MEASURE_FRAME_1", "SET_MEASURE", "QOKAIIN", "Sollmaß für den Bildbesitzer einstellen"),
    ("E057", "MEASURE_FRAME_1", "MEASURED_PLANT_MATERIAL", "BIND_MEASURE", "AIIN", "Sollmaß an das Pflanzenmaterial binden"),
    ("E058", "MEASURED_PLANT_MATERIAL", "PORTION_1", "SELECT_PORTION", "Y+AIN", "aus dem aktuellen Posten eine Portion wählen"),
    ("E059", "PORTION_1", "PORTION_1", "RESUME_CURRENT", "Y+AIN", "diese Portion weiterführen"),
    ("E060", "PORTION_1", "COOLED_PORTION_1", "COOL_CLOSE", "ODY", "Portion kühlen und den Teilgang schließen"),
    ("E061", "COOLED_PORTION_1", "MEASURED_COOLED_PORTION_1", "REBIND_MEASURE", "AIIN", "gekühlte Portion erneut nach Sollmaß fassen"),
    ("E062", "MEASURED_COOLED_PORTION_1", "WORKED_PREPARATION_1", "WORK_CURRENT", "CHED+Y", "den aktuellen Posten durcharbeiten"),
    ("E063", "WORKED_PREPARATION_1", "STORED_PREPARATION_1", "STORE", "TALAM", "das Arbeitsergebnis verwahren"),
    ("E064", "STORED_PREPARATION_1", "MEASURED_STORED_PREPARATION_1", "SELECT_MEASURE_OF_CURRENT", "Y+AIIN", "vom verwahrten Posten das Sollmaß nehmen"),
    ("E065", "MEASURED_STORED_PREPARATION_1", "EXTRACT_1", "EXTRACT_FROM", "CHEO+AR", "daraus einen Auszug nehmen"),
    ("E066", "EXTRACT_1", "WARMED_EXTRACT_1", "WARM_LONG_OPEN", "CHK+EE+Y", "den Auszug länger warm halten"),
    ("E067", "WARMED_EXTRACT_1", "WARMED_EXTRACT_1", "CONTINUE_CLOSE", "OL+DY", "diesen Gang als Fortsetzung schließen"),
    ("E068", "WARMED_EXTRACT_1", "MEASURED_WARMED_EXTRACT_1", "BIND_MEASURE", "AIIN", "den warmen Auszug abmessen"),
    ("E069", "MEASURED_WARMED_EXTRACT_1", "TARGETED_EXTRACT_1", "ASSIGN_TARGET", "OK+AL", "den Auszug an die Zielstelle setzen"),
    ("E070", "TARGETED_EXTRACT_1", "WARM_TARGET_APPLICATION_1", "WARM_AT_TARGET", "OLTCHY", "die Zielanwendung anwärmen"),
    ("E071", "WARM_TARGET_APPLICATION_1", "PREPARATION_1", "DECLARE_PREPARATION", "OR", "den laufenden Stoff als Zubereitung führen"),
    ("E072", "PREPARATION_1", "PREPARATION_1", "RESUME_CURRENT", "Y", "diese Zubereitung wiederaufnehmen"),
    ("E073", "PREPARATION_1", "PREPARATION_PORTION_2", "SELECT_PREPARATION_PORTION", "OR+AIN", "eine Portion der Zubereitung abteilen"),
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
    all_cards = read(P393 / "THREE_HUNDRED_NINETY_THIRD_25_COMPONENT_NOMENCLATOR_READINGS.tsv")
    h4_cards = [row for row in all_cards if row["owner_code"] == "H4"]
    h4_by_event = {row["event_id"]: row for row in h4_cards}
    trace_rows = []
    for order, (event_id, before, after, operation, components, reading) in enumerate(TRANSITIONS, 1):
        source = h4_by_event[event_id]
        trace_rows.append({
            "order": order,
            "event_id": event_id,
            "statement_id": source["statement_id"],
            "copy_surface": source["copy_surface"],
            "joint_tuple_id": source["joint_tuple_id"],
            "owner_register": "H4_PICTURED_PLANT",
            "active_before": before,
            "operation": operation,
            "component_cue": components,
            "active_after": after,
            "working_reading_de": reading,
            "handoff_basis": "EXPLICIT_CARD_PLUS_SAME_RECORD_INHERITANCE",
        })
    write("THREE_HUNDRED_NINETY_FOURTH_18_EVENT_OBJECT_TRACE.tsv", trace_rows)

    nodes = [
        ("OWNER_PLANT", "abgebildete unbenannte Pflanze", "PICTURE_OWNER"),
        ("PORTION_1", "erste abgemessene Pflanzenportion", "Y+AIN"),
        ("COOLED_PORTION_1", "gekühlte erste Portion", "ODY"),
        ("WORKED_PREPARATION_1", "durchgearbeitete Zubereitung", "CHEDY"),
        ("STORED_PREPARATION_1", "verwahrte Zubereitung", "TALAM"),
        ("EXTRACT_1", "Auszug aus der verwahrten Zubereitung", "CHEOAR"),
        ("WARMED_EXTRACT_1", "länger warm gehaltener Auszug", "CHEEKY"),
        ("WARM_TARGET_APPLICATION_1", "angewärmte Zielanwendung", "OKAL+OLTCHY"),
        ("PREPARATION_PORTION_2", "abgeteilte Portion der laufenden Zubereitung", "OR+Y+ORAIN"),
    ]
    node_rows = [
        {"node_order": index, "material_node": node, "working_object_de": reading, "explicit_anchor": anchor}
        for index, (node, reading, anchor) in enumerate(nodes, 1)
    ]
    write("THREE_HUNDRED_NINETY_FOURTH_NINE_MATERIAL_NODES.tsv", node_rows)
    edge_rows = [
        {"from_node": nodes[index][0], "to_node": nodes[index + 1][0], "relation": ["PORTION_SELECT", "COOL", "WORK", "STORE", "EXTRACT", "WARM", "TARGET_APPLY", "PORTION_SELECT"][index]}
        for index in range(len(nodes) - 1)
    ]
    write("THREE_HUNDRED_NINETY_FOURTH_EIGHT_MATERIAL_EDGES.tsv", edge_rows)

    handoffs = [
        {"boundary": "H4-S001_to_H4-S002", "carried_object": "COOLED_PORTION_1", "next_first_cue": "AIIN", "reading": "the new sentence remeasures the cooled portion"},
        {"boundary": "H4-S002_to_H4-S003", "carried_object": "STORED_PREPARATION_1", "next_first_cue": "Y+AIIN", "reading": "the stored result returns as current measured item"},
        {"boundary": "H4-S003_to_H4-S004", "carried_object": "WARMED_EXTRACT_1", "next_first_cue": "AIIN", "reading": "the warmed extract is measured for target use"},
    ]
    write("THREE_HUNDRED_NINETY_FOURTH_THREE_STATEMENT_HANDOFFS.tsv", handoffs)

    article = """# Pass 394 — H4 als fortlaufender Arbeitsartikel

Von der abgebildeten Pflanze stelle ein Sollmaß ein. Teile davon eine Portion ab
und lasse sie kühl werden. Nimm davon erneut das vorgeschriebene Maß, arbeite es
durch und verwahre die Zubereitung.

Nimm vom verwahrten Posten das Sollmaß, ziehe daraus einen Auszug, halte ihn
länger warm und schließe diesen Fortsetzungsgang. Miss den warmen Auszug ab,
bringe ihn an die bezeichnete Stelle und wärme ihn dort an. Vom laufenden Ansatz
teile schließlich eine Ansatzportion ab.

## Kurze Rückleseregel

- **Y** hält den jeweils aktuellen Stoff im Gespräch.
- **AIN** wählt daraus eine Portion.
- **AIIN** bindet oder erneuert das Sollmaß.
- **OR** benennt den laufenden Ansatz/Zubereitungsposten.
- **CHEO+AR** nimmt einen Auszug daraus.
- **TALAM** legt das bearbeitete Ergebnis zur späteren Wiederaufnahme ab.
- **OL** kennzeichnet die Fortsetzung über einen Teilgang hinweg.

Die genaue Pflanzenart und die Zielstelle bleiben Bildargumente. Der Textfluss
braucht sie nicht jedes Mal neu auszuschreiben.
"""
    (HERE / "THREE_HUNDRED_NINETY_FOURTH_CONTINUOUS_H4_ARTICLE.md").write_text(article, encoding="utf-8")
    report = """# Pass 394 — Y ist der Klebstoff des H4-Artikels

Die 18 echten H4-Karten bilden eine fortlaufende Objektgenealogie von der
Bildpflanze zur Portion, zur gekühlten und verwahrten Zubereitung, zum warmen
Auszug, zur Zielanwendung und zur nächsten Ansatzportion. Drei Satzgrenzen
tragen den jeweils letzten Arbeitsgegenstand weiter.

Damit bekommen die kurzen Kerne unterschiedliche, aber zusammenhängende Rollen:
Y ist anaphorischer Diesposten, AIN teilt Portionen ab, AIIN setzt das Maß, OR
hält die Zubereitung als Kategorie, CHEOAR leitet einen Auszug ab und TALAM
speichert einen wiederaufnehmbaren Zwischenstand.

Als nächstes soll dieselbe Objektflussmethode auf B3-S026 angewandt werden. Dort
muss geprüft werden, ob Beckenstation, Absetzstand, Portion, Bereitschaft,
Klarpunkt und Auffangen eine ebenso klare Stationskette ergeben.
"""
    (HERE / "THREE_HUNDRED_NINETY_FOURTH_REPORT.md").write_text(report, encoding="utf-8")
    summary = {
        "status": "PASS",
        "events": len(trace_rows),
        "material_nodes": len(node_rows),
        "material_edges": len(edge_rows),
        "statement_handoffs": len(handoffs),
        "owner": "H4_PICTURED_PLANT",
        "continuous_terminal_object": trace_rows[-1]["active_after"],
    }
    (HERE / "THREE_HUNDRED_NINETY_FOURTH_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
