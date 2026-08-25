#!/usr/bin/env python3
"""Build Pass 726: edit all six Biological records as local station protocols."""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P724 = ROOT / "experiments/yolo/sidequest_semantic_concrete_medium_revision_seven_hundred_twenty_fourth"
P74 = ROOT / "experiments/yolo/sidequest_theory_candidates_v74"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


AIR_PROSE = {
    "B1-S002": "Am gemeinsamen zweireihigen Becken: Nach Mass ansetzen und Wasser zugeben. Am Ziel aus der Quelle weiterarbeiten: eine Portion und dann eine weitere Portion zugeben, weiter kuehlen und weiterleiten. Den Ansatz fortsetzen, kurz am Durchlass dem Ziel halten, erneut nach Mass laenger ansetzen, den Posten durch den Durchlass umsetzen und schliessen.",
    "B3-S014": "Am unteren Korbgefaess: Wasser ansetzen, laenger halten und den Schritt schliessen.",
    "B3-S030": "Am durch den Bogen verbundenen Hauptpaar: Den Posten nach Mass ansetzen, Wasser innerhalb dieses Besitzerpaares umsetzen; danach nochmals umsetzen und schliessen.",
    "B4-S014": "An der linken offenen Randstation: Den Ansatz als laufenden Posten fuehren, ihn kurz im Arbeitsgang am Durchlass halten, dieses Wasser lokal weiterfuehren und den Schritt schliessen.",
}


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    statements = [row for row in read(P724 / "SEVEN_HUNDRED_TWENTY_FOURTH_116_STATEMENTS.tsv") if row["record"].startswith("B")]
    events = [row for row in read(P724 / "SEVEN_HUNDRED_TWENTY_FOURTH_381_EVENTS.tsv") if row["record"].startswith("B")]
    v74 = {row["statement_id"]: row for row in read(P74 / "V74_R1_97_STATEMENT_EDITION.tsv")}

    statement_rows = []
    reset_rows = []
    previous_terminal_owner: dict[str, str] = {}
    for row in statements:
        owner = v74[row["statement_id"]]
        owner_sequence = owner["owner_sequence"]
        first_owner = owner_sequence.split(" > ")[0]
        terminal_owner = owner_sequence.split(" > ")[-1]
        record = row["record"]
        if record not in previous_terminal_owner:
            handoff = "RECORD_START"
        elif previous_terminal_owner[record] != first_owner:
            handoff = "YES"
            reset_rows.append({
                "reset_id": f"BR{len(reset_rows) + 1:02d}", "reset_kind": "BETWEEN_STATEMENTS",
                "record": record, "statement_id": row["statement_id"],
                "from_owner": previous_terminal_owner[record], "to_owner": first_owner,
                "visible_connection": "NO_ASSUMED_CONNECTION", "global_flow_claim": "NONE",
            })
        else:
            handoff = "NO"
        if owner["internal_owner_reset"] == "YES":
            reset_rows.append({
                "reset_id": f"BR{len(reset_rows) + 1:02d}", "reset_kind": "INSIDE_STATEMENT",
                "record": record, "statement_id": row["statement_id"],
                "from_owner": first_owner, "to_owner": terminal_owner,
                "visible_connection": "EXPLICIT_RESET__NO_ASSUMED_CONNECTION", "global_flow_claim": "NONE",
            })
        previous_terminal_owner[record] = terminal_owner
        prose = AIR_PROSE.get(row["statement_id"], row["pass724_working_reading_de"])
        prefix = ""
        if handoff == "RECORD_START":
            prefix = f"[Station {first_owner}] "
        elif handoff == "YES":
            prefix = f"[Besitzerwechsel zu {first_owner}] "
        if owner["internal_owner_reset"] == "YES":
            prefix += f"[Lokaler Wechsel innerhalb der Aussage: {owner_sequence}] "
        statement_rows.append({
            "statement_id": row["statement_id"], "page": row["page"], "record": record,
            "events": row["events"], "owner_sequence": owner_sequence,
            "owner_handoff_before": handoff, "internal_owner_reset": owner["internal_owner_reset"],
            "surface_sequence": row["surface_sequence"], "component_sequence": row["component_sequence"],
            "atomic_trace_de": row["pass724_atomic_trace_de"],
            "fluent_local_station_clause_de": prefix + prose,
            "water_named": "YES" if "Wasser" in prose else "NO",
            "global_flow_claim": "NONE", "form_status": "UNCHANGED",
        })

    statement_by_id = {row["statement_id"]: row for row in statement_rows}
    event_rows = []
    for row in events:
        statement = statement_by_id[row["statement_id"]]
        event_rows.append({
            "event_id": row["event_id"], "page": row["page"], "record": row["record"],
            "statement_id": row["statement_id"], "locus": row["locus"],
            "owner_sequence": statement["owner_sequence"], "card_no": row["card_no"],
            "surface": row["observed_surface"], "component_recipe": row["component_recipe"],
            "atomic_reading_de": row["pass724_semantic_de"],
            "station_clause_de": statement["fluent_local_station_clause_de"],
            "global_flow_claim": "NONE", "surface_owner_boundary_unchanged": "YES",
        })

    statements_by_record: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in statement_rows:
        statements_by_record[str(row["record"])].append(row)
    record_rows = []
    for record in ["B1", "B2", "B3", "B4", "B5", "B6"]:
        rows = statements_by_record[record]
        record_events = [row for row in event_rows if row["record"] == record]
        record_rows.append({
            "record": record, "page": rows[0]["page"], "statements": len(rows), "events": len(record_events),
            "owner_namespaces": " | ".join(dict.fromkeys(str(row["owner_sequence"]) for row in rows)),
            "between_statement_resets": sum(row["owner_handoff_before"] == "YES" for row in rows),
            "internal_resets": sum(row["internal_owner_reset"] == "YES" for row in rows),
            "water_statements": sum(row["water_named"] == "YES" for row in rows),
            "continuous_local_protocol_de": " ".join(str(row["fluent_local_station_clause_de"]) for row in rows),
            "global_flow_claim": "NONE",
        })

    air_rows = []
    for row in event_rows:
        if "AIR" in row["component_recipe"].split("+"):
            air_rows.append({
                "event_id": row["event_id"], "record": row["record"], "statement_id": row["statement_id"],
                "owner_sequence": row["owner_sequence"], "card_no": row["card_no"], "surface": row["surface"],
                "component_recipe": row["component_recipe"], "atomic_reading_de": row["atomic_reading_de"],
                "local_water_clause_de": statement_by_id[row["statement_id"]]["fluent_local_station_clause_de"],
                "connection_scope": "ONLY_WITHIN_NAMED_LOCAL_OWNER", "global_flow_claim": "NONE",
            })

    write("SEVEN_HUNDRED_TWENTY_SIXTH_281_BIO_EVENTS.tsv", event_rows)
    write("SEVEN_HUNDRED_TWENTY_SIXTH_97_BIO_STATEMENTS.tsv", statement_rows)
    write("SEVEN_HUNDRED_TWENTY_SIXTH_6_BIO_RECORDS.tsv", record_rows)
    write("SEVEN_HUNDRED_TWENTY_SIXTH_10_OWNER_RESETS.tsv", reset_rows)
    write("SEVEN_HUNDRED_TWENTY_SIXTH_4_LOCAL_WATER_EVENTS.tsv", air_rows)

    edition = ["# Sechs vollständige lokale Biological-Protokolle", "", "Wasser und Bewegung gelten nur innerhalb des jeweils genannten Bildbesitzers. Es wird kein globaler Kreislauf ergänzt.", ""]
    for record in record_rows:
        edition.extend([f"## {record['record']} — {record['page']}", ""])
        for statement in statements_by_record[str(record["record"])]:
            edition.extend([f"- **{statement['statement_id']}** {statement['fluent_local_station_clause_de']}"])
        edition.append("")
    (HERE / "SEVEN_HUNDRED_TWENTY_SIXTH_COMPLETE_BIO_PROTOCOLS.md").write_text("\n".join(edition), encoding="utf-8")

    summary = {
        "status": "PASS", "records": len(record_rows), "statements": len(statement_rows), "events": len(event_rows),
        "record_statement_counts": {row["record"]: int(row["statements"]) for row in record_rows},
        "record_event_counts": {row["record"]: int(row["events"]) for row in record_rows},
        "between_statement_owner_resets": sum(row["reset_kind"] == "BETWEEN_STATEMENTS" for row in reset_rows),
        "internal_owner_resets": sum(row["reset_kind"] == "INSIDE_STATEMENT" for row in reset_rows),
        "total_owner_resets": len(reset_rows), "local_air_water_events": len(air_rows),
        "global_flow_claims": 0, "form_changes": 0,
        "decision": "SIX_COMPLETE_BIO_PROTOCOLS_KEEP_FOUR_WATER_EVENTS_AND_ALL_TEN_OWNER_RESETS_STRICTLY_LOCAL",
    }
    (HERE / "SEVEN_HUNDRED_TWENTY_SIXTH_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
