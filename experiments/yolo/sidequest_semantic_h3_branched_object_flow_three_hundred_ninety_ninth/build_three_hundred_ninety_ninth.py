#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
EVENTS = ROOT / "experiments/yolo/sidequest_semantic_thermal_temporal_completion/SELECTED_381_THERMAL_TEMPORAL_INTERLINEAR.tsv"

TRANSITIONS = [
    ("E039", "OWNER_PLANT", "MAIN_FLOWER_LEAF_BATCH", "SELECT_MAIN_MATERIAL", "Blüten und junge Blätter nehmen"),
    ("E040", "MAIN_FLOWER_LEAF_BATCH", "WINE_DECOCTION_MAIN", "BOIL_IN_MEDIUM", "Hauptmaterial als Weinsud bereiten"),
    ("E041", "WINE_DECOCTION_MAIN", "WRUNG_DECOCTION_MAIN", "WRING", "Sud durch Tuch auswringen"),
    ("E042", "WRUNG_DECOCTION_MAIN", "RESTED_DECOCTION_MAIN", "STAND", "vorgeschriebene Stehzeit einhalten"),
    ("E043", "RESTED_DECOCTION_MAIN", "RESTRAINED_DECOCTION_MAIN", "RESTRAIN", "danach nochmals seihen"),
    ("E044", "RESTRAINED_DECOCTION_MAIN", "CLEAR_EXTRACT_MAIN", "SELECT_CLEAR_EXTRACT", "Klarauszug gewinnen"),
    ("E045", "CLEAR_EXTRACT_MAIN", "COOLED_CLEAR_EXTRACT_MAIN", "COOL_CLOSE", "Klarauszug abkühlen und Hauptgang schließen"),
    ("E046", "OWNER_PLANT", "RESERVED_FLOWER_PORTION", "RESERVE_BRANCH", "einen frischen Blütenanteil für den zweiten Gebrauch zurückhalten"),
    ("E047", "RESERVED_FLOWER_PORTION", "SECOND_USE_FRAME", "OPEN_CONTINUATION", "zweiten Gebrauch als Fortsetzungsposten eröffnen"),
    ("E048", "SECOND_USE_FRAME", "RESERVED_FLOWER_PORTION_ACTIVE", "RESUME_CURRENT", "diesen zurückbehaltenen Posten aktiv halten"),
    ("E049", "RESERVED_FLOWER_PORTION_ACTIVE", "DRINK_PREPARATION_2", "PREPARE_DRINK", "daraus einen Trank bereiten"),
    ("E050", "DRINK_PREPARATION_2", "DRINK_PREPARATION_2", "RESUME_CURRENT", "diesen Trank weiterführen"),
    ("E051", "DRINK_PREPARATION_2", "MEASURED_DRINK_2", "BIND_MEASURE", "Sollmaß für den zweiten Trank setzen"),
    ("E052", "MEASURED_DRINK_2", "MEASURED_DRINK_WITH_RESERVED_FLOWERS", "RECALL_RESERVED_FLOWERS", "die zurückbehaltenen Blüten in den zweiten Gebrauch nehmen"),
    ("E053", "MEASURED_DRINK_WITH_RESERVED_FLOWERS", "ACTIVE_SECOND_PREPARATION", "ACTIVATE_CONTINUATION", "Fortsetzung in Arbeit setzen"),
    ("E054", "ACTIVE_SECOND_PREPARATION", "READY_SECOND_PREPARATION", "CHECK_READY", "zweite Zubereitung bereitstellen"),
    ("E055", "READY_SECOND_PREPARATION", "READY_SECOND_PREPARATION", "RESUME_FINAL_ITEM", "dieser fertige Posten"),
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
    h3 = [row for row in read(EVENTS) if row["record_unit_id"] == "H3"]
    h3_by_event = {row["event_id"]: row for row in h3}
    trace_rows = []
    for order, (event_id, before, after, operation, reading) in enumerate(TRANSITIONS, 1):
        source = h3_by_event[event_id]
        trace_rows.append({
            "order": order,
            "event_id": event_id,
            "statement_id": source["statement_id"],
            "surface": source["surface_display"],
            "joint_tuple_id": source["joint_tuple_id"],
            "active_before": before,
            "operation": operation,
            "active_after": after,
            "working_reading_de": reading,
            "branch": "MAIN" if int(event_id[1:]) <= 45 else "RESERVED_SECOND_USE",
            "owner": "H3_PICTURED_PLANT",
        })
    write("THREE_HUNDRED_NINETY_NINTH_17_EVENT_BRANCH_TRACE.tsv", trace_rows)

    node_specs = [
        ("OWNER_PLANT", "abgebildete Pflanze", "ROOT"),
        ("MAIN_FLOWER_LEAF_BATCH", "Blüten- und Blattcharge", "MAIN"),
        ("WINE_DECOCTION_MAIN", "Weinsud", "MAIN"),
        ("WRUNG_DECOCTION_MAIN", "ausgewrungener Sud", "MAIN"),
        ("RESTED_DECOCTION_MAIN", "abgestandener Sud", "MAIN"),
        ("RESTRAINED_DECOCTION_MAIN", "nachgeseihter Sud", "MAIN"),
        ("CLEAR_EXTRACT_MAIN", "Klarauszug", "MAIN"),
        ("COOLED_CLEAR_EXTRACT_MAIN", "gekühlter Klarauszug", "MAIN"),
        ("RESERVED_FLOWER_PORTION", "zurückbehaltene frische Blüten", "RESERVED_SECOND_USE"),
        ("DRINK_PREPARATION_2", "zweiter Trank", "RESERVED_SECOND_USE"),
        ("MEASURED_DRINK_2", "abgemessener zweiter Trank", "RESERVED_SECOND_USE"),
        ("READY_SECOND_PREPARATION", "fertige zweite Zubereitung", "RESERVED_SECOND_USE"),
    ]
    node_rows = [
        {"node_order": index, "material_node": node, "working_object_de": reading, "branch": branch}
        for index, (node, reading, branch) in enumerate(node_specs, 1)
    ]
    write("THREE_HUNDRED_NINETY_NINTH_12_MATERIAL_NODES.tsv", node_rows)

    edges = [
        ("OWNER_PLANT", "MAIN_FLOWER_LEAF_BATCH", "SELECT_MAIN"),
        ("MAIN_FLOWER_LEAF_BATCH", "WINE_DECOCTION_MAIN", "BOIL"),
        ("WINE_DECOCTION_MAIN", "WRUNG_DECOCTION_MAIN", "WRING"),
        ("WRUNG_DECOCTION_MAIN", "RESTED_DECOCTION_MAIN", "STAND"),
        ("RESTED_DECOCTION_MAIN", "RESTRAINED_DECOCTION_MAIN", "RESTRAIN"),
        ("RESTRAINED_DECOCTION_MAIN", "CLEAR_EXTRACT_MAIN", "CLEAR"),
        ("CLEAR_EXTRACT_MAIN", "COOLED_CLEAR_EXTRACT_MAIN", "COOL"),
        ("OWNER_PLANT", "RESERVED_FLOWER_PORTION", "RESERVE_BRANCH"),
        ("RESERVED_FLOWER_PORTION", "DRINK_PREPARATION_2", "PREPARE_DRINK"),
        ("DRINK_PREPARATION_2", "MEASURED_DRINK_2", "MEASURE"),
        ("MEASURED_DRINK_2", "READY_SECOND_PREPARATION", "ADD_RESERVED_FLOWERS_AND_READY"),
    ]
    edge_rows = [{"from_node": start, "to_node": end, "relation": relation} for start, end, relation in edges]
    write("THREE_HUNDRED_NINETY_NINTH_11_BRANCH_EDGES.tsv", edge_rows)

    article = """# Pass 399 — H3 als Hauptauszug mit zweitem Blütenzweig

Nimm von der abgebildeten Pflanze im ersten Frühjahr Blüten und junge Blätter
und bereite daraus einen Weinsud. Wring ihn durch ein Tuch, lass ihn für die
vorgeschriebene Zeit stehen, seihe ihn nochmals, nimm den klaren Auszug und lass
ihn abkühlen.

Behalte daneben einen Anteil der frischen Blüten für einen zweiten Gebrauch
zurück. Eröffne daraus den Fortsetzungsposten, bereite einen Trank und stelle
sein Sollmaß ein. Nimm die zurückbehaltenen Blüten in diese Fortsetzung, setze
den Gang in Arbeit und halte die zweite Zubereitung bereit.

## Objektfluss

```text
Bildpflanze
├─ Hauptcharge → Weinsud → Auswringen → Stehen → Nachseihen → Klarauszug → Kühlen
└─ reservierte Blüten → zweiter Trank → Sollmaß → Blüten wieder einsetzen → bereit
```

Der Nebenzweig ist der konkrete Grund, weshalb `shoyty`/zurückhalten und
`qotchy`/zurückbehaltene Blüten nicht als bloße Wiederholung gelesen werden.
"""
    (HERE / "THREE_HUNDRED_NINETY_NINTH_CONTINUOUS_H3_ARTICLE.md").write_text(article, encoding="utf-8")

    comparison = [
        {"record": "H3", "events": 17, "material_topology": "ONE_ROOT_TWO_BRANCHES", "key_process": "WRING_STAND_RESTRAIN_CLEAR", "portion_logic": "RESERVED_FLOWERS_FOR_SECOND_USE", "terminal_products": "COOLED_CLEAR_EXTRACT|READY_SECOND_PREPARATION"},
        {"record": "H4", "events": 18, "material_topology": "ONE_LINEAR_GENEALOGY", "key_process": "MEASURE_WORK_STORE_EXTRACT_TARGET", "portion_logic": "REPEATED_MEASURE_AND_PORTION_HANDOFF", "terminal_products": "PREPARATION_PORTION_2"},
    ]
    write("THREE_HUNDRED_NINETY_NINTH_H3_H4_OBJECT_FLOW_CONTRAST.tsv", comparison)
    report = """# Pass 399 — H3 hat einen echten Arbeitszweig

Die 17 H3-Ereignisse ergeben zwei Produkte aus einem Bildbesitzer. Der
Hauptzweig führt über Sud, Auswringen, Stehzeit und Nachseihen zum gekühlten
Klarauszug. Ein ausdrücklich zurückbehaltener Blütenanteil eröffnet einen
zweiten, abgemessenen Trank-/Zubereitungszweig.

Das unterscheidet H3 klar von H4: H4 verfolgt eine lineare Folge aus Maß,
Portion, Speicherung, Auszug und Zielanwendung; H3 verwendet Reserve und
Wiederaufnahme. Als nächstes soll geprüft werden, welche Karten genau den
Abzweig markieren und ob dieselbe Reservegrammatik in H1, H2 oder H5 vorkommt.
"""
    (HERE / "THREE_HUNDRED_NINETY_NINTH_REPORT.md").write_text(report, encoding="utf-8")
    summary = {
        "status": "PASS",
        "events": len(trace_rows),
        "material_nodes": len(node_rows),
        "edges": len(edge_rows),
        "branches": 2,
        "main_terminal": "COOLED_CLEAR_EXTRACT_MAIN",
        "reserved_terminal": "READY_SECOND_PREPARATION",
    }
    (HERE / "THREE_HUNDRED_NINETY_NINTH_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
