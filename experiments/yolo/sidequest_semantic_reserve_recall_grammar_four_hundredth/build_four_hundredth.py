#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
EVENTS = ROOT / "experiments/yolo/sidequest_semantic_thermal_temporal_completion/SELECTED_381_THERMAL_TEMPORAL_INTERLINEAR.tsv"

H3_BRANCH = {
    "E046": ("RESERVE", "H3_WHOLE_CARD", "einen Blütenanteil zurücklegen"),
    "E047": ("OPEN_CONTINUATION", "PORTABLE_CH_OL", "einen Fortsetzungsposten eröffnen"),
    "E052": ("RECALL", "H3_WHOLE_CARD", "die zurückgelegten Blüten wieder aufnehmen"),
    "E053": ("ACTIVATE_CONTINUATION", "PORTABLE_OK_OL", "die Fortsetzung einsetzen"),
}

SIBLINGS = {
    "E013": ("H1", "OL", "CONTINUE", "den laufenden Gang fortsetzen"),
    "E026": ("H2", "OT+OL", "NEXT_CONTINUE", "danach fortsetzen"),
    "E027": ("H2", "OL", "CONTINUE", "fortsetzen"),
    "E028": ("H2", "OL+OR", "PREVIOUS_BATCH", "den vorigen Ansatz weiterführen"),
    "E029": ("H2", "OL", "CONTINUE", "fortsetzen"),
    "E080": ("H5", "OT+OR", "NEXT_BATCH", "einen Folgeansatz eröffnen"),
    "E083": ("H5", "CH+OL", "PREVIOUS_ITEM", "den vorigen Posten aufnehmen"),
    "E090": ("H5", "OK+OK+Y", "REPEAT_OPERATION", "den Posten erneut ansetzen"),
    "E098": ("H5", "OT+Y", "NEXT_ITEM", "den Folgeposten wählen"),
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
    events = read()
    by_id = {row["event_id"]: row for row in events}

    branch_rows = []
    for order, (event_id, (function, portability, reading)) in enumerate(H3_BRANCH.items(), 1):
        source = by_id[event_id]
        branch_rows.append({
            "order": order,
            "event_id": event_id,
            "surface": source["surface_display"],
            "joint_tuple_id": source["joint_tuple_id"],
            "function": function,
            "portability": portability,
            "working_reading_de": reading,
            "decision": "KEEP_AS_WHOLE_H3_CARD" if portability == "H3_WHOLE_CARD" else "READ_COMPOSITIONALLY",
        })
    write("FOUR_HUNDREDTH_FOUR_H3_BRANCH_CARDS.tsv", branch_rows)

    sibling_rows = []
    for event_id, (record, composition, function, reading) in SIBLINGS.items():
        source = by_id[event_id]
        sibling_rows.append({
            "event_id": event_id,
            "record": record,
            "page": source["page"],
            "statement_id": source["statement_id"],
            "surface": source["surface_display"],
            "joint_tuple_id": source["joint_tuple_id"],
            "composition": composition,
            "function": function,
            "working_reading_de": reading,
        })
    write("FOUR_HUNDREDTH_H1_H2_H5_SIBLINGS.tsv", sibling_rows)

    family_specs = [
        ("OL", "FORTSETZUNG", 19, "portable across Herbal and Biological records"),
        ("CH+OL", "FORTSETZUNGSPOSTEN", 2, "same exact card in H3 and H5"),
        ("OK+OL", "FORTSETZUNG EINSETZEN", 2, "two registered compositional surfaces in H3 and B4"),
        ("OT+OL", "DANACH FORTSETZEN", 1, "thin but compositionally regular"),
        ("OL+OR", "VORIGEN ANSATZ WEITERFÜHREN", 2, "same exact card in H2 and B1"),
        ("OK+OK+Y", "POSTEN ERNEUT ANSETZEN", 1, "independent repetition device in H5"),
        ("SHOYTY", "BLÜTENANTEIL ZURÜCKLEGEN", 1, "H3 learned reserve card; not a portable stem"),
        ("QOTCHY", "ZURÜCKGELEGTE BLÜTEN WIEDER AUFNEHMEN", 1, "H3 learned recall card; not a portable stem"),
    ]
    family_rows = [
        {"family": family, "small_value_de": value, "visible_events": count, "scope": scope}
        for family, value, count, scope in family_specs
    ]
    write("FOUR_HUNDREDTH_FUNCTIONAL_FAMILIES.tsv", family_rows)

    summary = {
        "status": "PASS",
        "h3_branch_cards": len(branch_rows),
        "cross_record_siblings": len(sibling_rows),
        "family_rows": len(family_rows),
        "decision": "PORTABLE_CONTINUATION_CORE_WITH_H3_LOCAL_RESERVE_RECALL_CARDS",
        "sibling_records": dict(Counter(row["record"] for row in sibling_rows)),
    }
    (HERE / "FOUR_HUNDREDTH_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
