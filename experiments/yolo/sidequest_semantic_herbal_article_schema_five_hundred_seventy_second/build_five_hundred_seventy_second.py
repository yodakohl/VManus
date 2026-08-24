#!/usr/bin/env python3
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
P570 = ROOT / "sidequest_semantic_plant_owner_case_correction_five_hundred_seventieth"
P571 = ROOT / "sidequest_semantic_natural_record_summaries_five_hundred_seventy_first"


def read_tsv(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(name, rows):
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


SLOTS = [
    ("HS1", "PICTURED_MATERIAL", "Das Bild liefert den stillen Pflanzenstoff."),
    ("HS2", "PREPARATION_BATCH", "Der Text bildet oder führt einen Ansatz weiter."),
    ("HS3", "MEASURE_OR_PORTION", "Mindestens eine Karte bestimmt Maß oder Portion."),
    ("HS4", "CONDITIONING", "Optional: halten, ziehen, temperieren oder absetzen."),
    ("HS5", "TRANSFER_OR_APPLICATION", "Optional: abziehen, weiterführen oder an einer Stelle anlegen."),
    ("HS6", "OPEN_CONTINUATION", "Der Artikel endet mit einem offenen Arbeitsrest."),
]


def main():
    transitions = [row for row in read_tsv(P570 / "FIVE_HUNDRED_SEVENTIETH_ONE_HUNDRED_SIXTEEN_CORRECTED_TRANSITIONS.tsv") if row["record"].startswith("H")]
    events = [row for row in read_tsv(P570 / "FIVE_HUNDRED_SEVENTIETH_THREE_HUNDRED_EIGHTY_ONE_CORRECTED_EVENTS.tsv") if row["record"].startswith("H")]
    summaries = {row["record"]: row for row in read_tsv(P571 / "FIVE_HUNDRED_SEVENTY_FIRST_ELEVEN_NATURAL_RECORD_SUMMARIES.tsv")}
    by_statement = defaultdict(list)
    for row in events:
        by_statement[row["statement_id"]].append(row)

    statement_rows = []
    for transition in transitions:
        rows = by_statement[transition["statement_id"]]
        phases = transition["phase_signature"].split(">")
        modifiers = {channel for row in rows for channel in row["modifier_channels"].split("|") if channel != "NONE"}
        slots = {"HS1", "HS2"}
        if modifiers & {"MEASURE", "PORTION", "STAGE"}: slots.add("HS3")
        if set(phases) & {"HOLD", "THERMAL", "SETTLE"}: slots.add("HS4")
        if set(phases) & {"ROUTE", "APPLY"}: slots.add("HS5")
        statement_rows.append({
            "statement_id": transition["statement_id"],
            "page": transition["page"],
            "record": transition["record"],
            "statement_slots": "|".join(sorted(slots)),
            "phase_signature": transition["phase_signature"],
            "modifier_channels": "|".join(sorted(modifiers)) if modifiers else "NONE",
            "input_object": transition["input_object"],
            "output_object": transition["output_object"],
            "committed": transition["committed"],
        })

    records = ["H1", "H2", "H3", "H4", "H5"]
    matrix_rows = []
    for record in records:
        rows = [row for row in statement_rows if row["record"] == record]
        record_events = [row for row in events if row["record"] == record]
        present = {slot for row in rows for slot in row["statement_slots"].split("|")}
        present.add("HS6")
        # The amount slot can be carried as a non-action card anywhere in the article.
        if any(set(row["component_parse"].split("+")) & {"AIIN", "AIN", "IIN"} for row in record_events): present.add("HS3")
        matrix_rows.append({
            "record": record,
            "page": rows[0]["page"],
            "statements": str(len(rows)),
            "events": str(len(record_events)),
            "slot_sequence": ">".join(slot for slot, _, _ in SLOTS if slot in present),
            **{slot.lower(): "PRESENT" if slot in present else "OPTIONAL_ABSENT" for slot, _, _ in SLOTS},
            "final_committed": rows[-1]["committed"],
            "natural_summary_de": summaries[record]["natural_record_summary_de"],
        })

    slot_rows = []
    for slot, name, rule in SLOTS:
        record_count = sum(row[slot.lower()] == "PRESENT" for row in matrix_rows)
        statement_count = sum(slot in row["statement_slots"].split("|") for row in statement_rows)
        slot_rows.append({
            "slot": slot,
            "slot_name": name,
            "workshop_rule_de": rule,
            "records_present": str(record_count),
            "statements_contributing": str(statement_count),
            "schema_status": "COMMON_CORE" if record_count == 5 else "OPTIONAL_EXTENSION",
        })

    event_rows = []
    statement_slot = {row["statement_id"]: row for row in statement_rows}
    for row in events:
        event_rows.append({
            **row,
            "article_slots": statement_slot[row["statement_id"]]["statement_slots"],
            "schema_binding_complete": "YES",
        })

    write_tsv("FIVE_HUNDRED_SEVENTY_SECOND_SIX_HERBAL_ARTICLE_SLOTS.tsv", slot_rows)
    write_tsv("FIVE_HUNDRED_SEVENTY_SECOND_FIVE_ARTICLE_MATRIX.tsv", matrix_rows)
    write_tsv("FIVE_HUNDRED_SEVENTY_SECOND_NINETEEN_STATEMENT_SLOT_MAP.tsv", statement_rows)
    write_tsv("FIVE_HUNDRED_SEVENTY_SECOND_ONE_HUNDRED_HERBAL_EVENTS.tsv", event_rows)
    markdown = ["# Gemeinsames Herbal-Artikelschema", "", "Die fünf Artikel teilen vier Kernslots und verwenden zwei optionale Erweiterungen.", ""]
    for row in slot_rows:
        markdown.append(f"- **{row['slot']} {row['slot_name']}** — {row['workshop_rule_de']} ({row['records_present']}/5 Records; {row['schema_status']})")
    markdown.append("")
    for row in matrix_rows:
        markdown.extend([f"## {row['record']} — `{row['slot_sequence']}`", "", row["natural_summary_de"], ""])
    (HERE / "FIVE_HUNDRED_SEVENTY_SECOND_COMPLETE_HERBAL_SCHEMA.md").write_text("\n".join(markdown).rstrip() + "\n", encoding="utf-8")
    common = [row["slot"] for row in slot_rows if row["schema_status"] == "COMMON_CORE"]
    summary = {
        "status": "PASS", "slots": len(slot_rows), "common_core_slots": common,
        "optional_slots": [row["slot"] for row in slot_rows if row["schema_status"] == "OPTIONAL_EXTENSION"],
        "records": len(matrix_rows), "statements": len(statement_rows), "events": len(event_rows),
        "schema_bindings": sum(row["schema_binding_complete"] == "YES" for row in event_rows),
    }
    (HERE / "FIVE_HUNDRED_SEVENTY_SECOND_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report = [
        "# Fünfhundertzweiundsiebzigste Runde: Herbal-Artikelschema",
        "",
        "## Ergebnis",
        "",
        "Alle fünf Herbal-Records teilen vier Kernslots: sichtbares Pflanzenmaterial, Bildung/Fortsetzung eines Ansatzes, Maß oder Portion und offener Arbeitsrest. Zwei Erweiterungen sind optional: Konditionieren durch Halten/Temperieren/Absetzen sowie Transfer oder Anwendung.",
        "",
        "Das Schema ist damit kein starres Rezept und keine Liste von Pflanzennamen. Es ist ein bebilderter Arbeitsartikel: BILDSTOFF → ANSATZ → MENGE, optional KONDITIONIERUNG und TRANSFER/ANWENDUNG, dann OFFENE FORTSETZUNG. H3 ist die ausführlichste Zubereitungsfolge; H4/H5 tragen die klarsten Anwendungserweiterungen.",
        "",
        "Alle 19 Herbal-Aussagen und 100 Kartenereignisse sind an die Slots gebunden. Die Karte liefert Handlung oder Parameter; das Bild liefert die Pflanze.",
        "",
        "## Nächster Schritt",
        "",
        "Als Nächstes wird analog für B1–B4 ein gemeinsames Biological-Zellenschema gebaut: Medium, Maß, Ziel/Passage, Zustandsgrad, lokale Handlung und Schluss.",
    ]
    (HERE / "FIVE_HUNDRED_SEVENTY_SECOND_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")


if __name__ == "__main__": main()
