#!/usr/bin/env python3
"""Build the CHK short/long heat-grade reading from its five fixed-page events."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
LEDGER = ROOT / "experiments/yolo/sidequest_semantic_thermal_temporal_completion/SELECTED_381_THERMAL_TEMPORAL_INTERLINEAR.tsv"
TARGETS = {
    "d904bf7b044dd3922781": ("CHEKY", "CHK+E+Y", "Kurzwärme", "kurz wärmen"),
    "2c1a5fd92b9e3c762242": ("CHEEKY", "CHK+EE+Y", "Langwärme", "länger warm halten"),
}


def read() -> list[dict[str, str]]:
    with LEDGER.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, str]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    rows = read()
    by_statement = {}
    for row in rows:
        by_statement.setdefault(row["statement_id"], []).append(row)

    events = []
    statements = []
    for row in rows:
        if row["joint_tuple_id"] not in TARGETS:
            continue
        family, composition, atom, expansion = TARGETS[row["joint_tuple_id"]]
        statement = by_statement[row["statement_id"]]
        events.append(
            {
                "event_id": row["event_id"],
                "record_unit_id": row["record_unit_id"],
                "page": row["page"],
                "statement_id": row["statement_id"],
                "joint_tuple_id": row["joint_tuple_id"],
                "surface": row["surface_display"],
                "family_member": family,
                "composition": composition,
                "atomic_value_de": atom,
                "sentence_expansion_de": expansion,
                "full_surface_sequence": " ".join(x["surface_display"] for x in statement),
                "full_atomic_sequence": " → ".join(
                    atom if x["event_id"] == row["event_id"] else x["concrete_word_reading_de"]
                    for x in statement
                ),
            }
        )
        statements.append(
            {
                "statement_id": row["statement_id"],
                "page": row["page"],
                "target_event": row["event_id"],
                "selected_reading_de": {
                    "B1-S008": "Diesen Posten kurz wärmen, weiterführen und danach absetzen.",
                    "B1-S020": "Kurz wärmen und danach abseihen.",
                    "B4-S011": "Das Sollmaß kurz wärmen, mit dem vorigen Ansatz länger fortsetzen, eine Portion zugeben, umsetzen, weiterführen und ein zweites Mal waschen.",
                    "H4-S003": "Die Sollportion aus dem Auszug nehmen, länger warm halten und den Arbeitsgang abschließen.",
                    "B4-S008": "Das Sollmaß länger warm halten, an der ersten Öffnung kurz ansetzen und den Schritt schließen.",
                }[row["statement_id"]],
                "heat_source_visible": "NO",
                "workshop_reading": "TEXT_OPERATION_AT_LOCAL_OWNER",
            }
        )

    family = [
        {
            "component": "CHK",
            "value_de": "WÄRMEN",
            "function": "PROZESSKERN",
            "attested_members": "CHEKY|CHEEKY",
            "event_count": "5",
            "prediction": "Mit EEE ergäbe derselbe Kern Vollwärme oder vollständiges Durchwärmen.",
        },
        {
            "component": "E",
            "value_de": "KURZ",
            "function": "DAUERGRAD_I",
            "attested_members": "CHEKY",
            "event_count": "3",
            "prediction": "CHK+E+Y = Kurzwärme des laufenden Postens.",
        },
        {
            "component": "EE",
            "value_de": "LÄNGER",
            "function": "DAUERGRAD_II",
            "attested_members": "CHEEKY",
            "event_count": "2",
            "prediction": "CHK+EE+Y = Langwärme des laufenden Postens.",
        },
        {
            "component": "Y",
            "value_de": "DIESPOSTEN",
            "function": "AKTUELLER_REFERENT",
            "attested_members": "CHEKY|CHEEKY",
            "event_count": "5",
            "prediction": "Der Posten bleibt nach der Wärmeoperation verfügbar; diese Karten schließen nicht selbst.",
        },
    ]

    write("THREE_HUNDRED_TWENTY_FIRST_FIVE_CHK_EVENTS.tsv", events)
    write("THREE_HUNDRED_TWENTY_FIRST_FIVE_REVISED_STATEMENTS.tsv", statements)
    write("THREE_HUNDRED_TWENTY_FIRST_CHK_GRADE_RULE.tsv", family)
    names = [
        "THREE_HUNDRED_TWENTY_FIRST_FIVE_CHK_EVENTS.tsv",
        "THREE_HUNDRED_TWENTY_FIRST_FIVE_REVISED_STATEMENTS.tsv",
        "THREE_HUNDRED_TWENTY_FIRST_CHK_GRADE_RULE.tsv",
    ]
    summary = {
        "status": "PASS",
        "card_types": len(TARGETS),
        "events": len(events),
        "statements": len(statements),
        "short_grade_events": sum(x["family_member"] == "CHEKY" for x in events),
        "long_grade_events": sum(x["family_member"] == "CHEEKY" for x in events),
        "hashes": {name: hashlib.sha256((HERE / name).read_bytes()).hexdigest() for name in names},
    }
    (HERE / "THREE_HUNDRED_TWENTY_FIRST_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
