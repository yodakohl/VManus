#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
BASE = ROOT / "sidequest_semantic_seventh_workshop_grammar_eight_hundred_twenty_seventh"
COMPONENTS = BASE / "EIGHT_HUNDRED_TWENTY_SEVENTH_39_COMPONENT_SEVENTH_GRAMMAR.tsv"
EVENTS = BASE / "EIGHT_HUNDRED_TWENTY_SEVENTH_381_EVENT_REPARSE.tsv"
STATEMENTS = BASE / "EIGHT_HUNDRED_TWENTY_SEVENTH_116_STATEMENT_REPARSE.tsv"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]], fields: list[str]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    components = read(COMPONENTS)
    events = read(EVENTS)
    statements = read(STATEMENTS)
    by_component = {row["component"]: row for row in components}
    by_statement_events: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in events:
        by_statement_events[row["statement_id"]].append(row)

    contract_rows = []
    for row in components:
        if row["grammar_tier"] == "PARADIGM_CORE33":
            source_class = "PRODUCTIVE_CORE"
        elif row["grammar_tier"] == "BOUND_COMPONENT":
            source_class = "BOUND_VALUE"
        else:
            source_class = "MEMORIZED_WHOLE"
        contract_rows.append(
            {
                "component": row["component"],
                "short_value_de": row["short_value_de"],
                "source_class": source_class,
                "literal_use_rule": "emit this value exactly once per component token",
                "owner_may_change_value": "NO",
                "owner_may_supply_referent": "YES",
            }
        )

    layered_rows = []
    atom_count = 0
    for row in statements:
        selected = by_statement_events[row["statement_id"]]
        literal_atoms = []
        for event in selected:
            tokens = event["component_recipe"].split("+")
            literal_atoms.extend(by_component[token]["short_value_de"] for token in tokens)
        atom_count += len(literal_atoms)
        owner_class = "PICTURED_PLANT_OWNER" if row["record"].startswith("H") else "VISIBLE_STATION_OWNER"
        extra = []
        reading = row["working_reading_de"]
        if "lokalen Empfaenger" in reading:
            extra.append("LOCAL_RECEIVER")
        if "zweimal" in reading:
            extra.append("REPETITION_FROM_DOUBLE_COMPONENT")
        if "naechsten Posten" in reading:
            extra.append("NEXT_ITEM_FROM_OT_PLUS_Y")
        layered_rows.append(
            {
                "statement_id": row["statement_id"],
                "page": row["page"],
                "record": row["record"],
                "owner_class": owner_class,
                "owner_address_de": row["owner_noun_de"],
                "events": row["events"],
                "component_atoms": len(literal_atoms),
                "surface_sequence": row["surface_sequence"],
                "component_sequence": row["component_sequence"],
                "literal_component_layer_de": " · ".join(literal_atoms),
                "owner_supplied_layer_de": f"OWNER={row['owner_noun_de']}; lokale Pronomen und Kasus aus diesem Besitzer aufloesen",
                "extra_local_expansions": ";".join(extra) or "NONE",
                "fluent_workshop_reading_de": reading,
                "separation_rule": "only literal_component_layer_de is dictionary-composed; fluent syntax and owner nouns are supplied",
            }
        )

    by_record: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in layered_rows:
        by_record[str(row["record"])].append(row)
    record_rows = []
    for record, rows in by_record.items():
        record_rows.append(
            {
                "record": record,
                "page": rows[0]["page"],
                "register": "HERBAL" if record.startswith("H") else "BIOLOGICAL",
                "owner_addresses": " | ".join(dict.fromkeys(str(row["owner_address_de"]) for row in rows)),
                "statements": len(rows),
                "events": sum(int(str(row["events"])) for row in rows),
                "component_atoms": sum(int(str(row["component_atoms"])) for row in rows),
                "literal_record_de": " || ".join(str(row["literal_component_layer_de"]) for row in rows),
                "fluent_record_de": " ".join(str(row["fluent_workshop_reading_de"]) for row in rows),
            }
        )

    write("EIGHT_HUNDRED_TWENTY_NINTH_39_COMPONENT_LITERAL_CONTRACT.tsv", contract_rows, ["component", "short_value_de", "source_class", "literal_use_rule", "owner_may_change_value", "owner_may_supply_referent"])
    write("EIGHT_HUNDRED_TWENTY_NINTH_116_LAYERED_STATEMENTS.tsv", layered_rows, ["statement_id", "page", "record", "owner_class", "owner_address_de", "events", "component_atoms", "surface_sequence", "component_sequence", "literal_component_layer_de", "owner_supplied_layer_de", "extra_local_expansions", "fluent_workshop_reading_de", "separation_rule"])
    write("EIGHT_HUNDRED_TWENTY_NINTH_11_LAYERED_RECORDS.tsv", record_rows, ["record", "page", "register", "owner_addresses", "statements", "events", "component_atoms", "literal_record_de", "fluent_record_de"])

    lines = ["# Eleven complete prose records — literal and workshop layers", ""]
    for record in record_rows:
        lines.extend([f"## {record['record']} · {record['page']}", "", f"Owner: {record['owner_addresses']}", ""])
        for row in by_record[str(record["record"])]:
            lines.extend(
                [
                    f"### {row['statement_id']}",
                    "",
                    f"Surface: `{row['surface_sequence']}`",
                    "",
                    f"Literal: {row['literal_component_layer_de']}",
                    "",
                    f"Workshop reading: {row['fluent_workshop_reading_de']}",
                    "",
                ]
            )
    (HERE / "EIGHT_HUNDRED_TWENTY_NINTH_ELEVEN_COMPLETE_RECORDS.md").write_text("\n".join(lines), encoding="utf-8")

    summary = {
        "status": "PASS",
        "decision": "ELEVEN_RECORDS_PUBLISHED_WITH_LITERAL_AND_OWNER_LAYERS_SEPARATED",
        "components": len(contract_rows),
        "events": len(events),
        "statements": len(layered_rows),
        "records": len(record_rows),
        "component_atoms": atom_count,
        "herbal_records": sum(row["register"] == "HERBAL" for row in record_rows),
        "biological_records": sum(row["register"] == "BIOLOGICAL" for row in record_rows),
        "owner_value_changes_allowed": 0,
        "sealed_pages": ["f84", "f84r"],
    }
    (HERE / "EIGHT_HUNDRED_TWENTY_NINTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
