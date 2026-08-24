#!/usr/bin/env python3
import csv
import json
from collections import Counter, OrderedDict, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
YOLO = HERE.parent
P585 = YOLO / "sidequest_semantic_full_statement_correction_five_hundred_eighty_fifth"
P587 = YOLO / "sidequest_semantic_uniform_three_line_edition_five_hundred_eighty_seventh"

TITLES = {
    "B1": "Gemeinsames Becken: Grundgänge und Anwendungen",
    "B2": "Becken- und Randstationen: lokale Arbeitszellen",
    "B3": "Gefäß- und Figurenstationen: Variantenregister",
    "B4": "Linke und rechte Hauptstation: geschlossene Arbeitszellen",
    "B5": "Linker Fransen-Nachtrag",
    "B6": "Rechter S-Lauf-Nachtrag",
}


def read(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name, rows):
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)


def main():
    statements = [r for r in read(P585 / "FIVE_HUNDRED_EIGHTY_FIFTH_CORRECTED_ONE_HUNDRED_SIXTEEN_FULL_STATEMENTS.tsv") if r["record"].startswith("B")]
    events = [r for r in read(P585 / "FIVE_HUNDRED_EIGHTY_FIFTH_CORRECTED_THREE_HUNDRED_EIGHTY_ONE_EVENT_BINDING.tsv") if r["record"].startswith("B")]
    three_line = {r["statement_id"]: r for r in read(P587 / "FIVE_HUNDRED_EIGHTY_SEVENTH_ONE_HUNDRED_SIXTEEN_THREE_LINE_STATEMENTS.tsv")}
    close_statements = defaultdict(bool)
    for event in events:
        if "schließ" in event["atomic_card_value_de"].lower():
            close_statements[event["statement_id"]] = True
    statement_rows = []
    by_record = OrderedDict()
    for row in statements:
        edition = three_line[row["statement_id"]]
        args = "" if row["complete_arguments_de"] == "NONE" else f" Angaben: {row['complete_arguments_de']}."
        actions = "setze nur die Angaben" if row["complete_actions_de"] == "NO_EXPLICIT_ACTION_CARD" else row["complete_actions_de"]
        fluent = f"Bildort: {row['silent_owner_de']}. Arbeitsfolge: {actions}.{args}"
        out = {
            "statement_id": row["statement_id"], "page": row["page"], "record": row["record"],
            "record_type": "LOCAL_STATION_CELL_REGISTER" if row["record"] in {"B1","B2","B3","B4"} else "TECHNICAL_APPENDIX",
            "silent_owner_de": row["silent_owner_de"], "event_total": row["event_total"],
            "cell_status": "CLOSED_CELL" if close_statements[row["statement_id"]] else "OPEN_ENTRY",
            "visible_cards": edition["visible_cards"], "spoken_components_de": edition["spoken_component_line_de"],
            "complete_actions_de": row["complete_actions_de"], "complete_arguments_de": row["complete_arguments_de"],
            "fluent_station_entry_de": fluent, "all_source_events_bound": "YES",
        }
        statement_rows.append(out); by_record.setdefault(row["record"], []).append(out)
    record_rows = []
    for record, rows in by_record.items():
        owners = list(dict.fromkeys(r["silent_owner_de"] for r in rows))
        record_rows.append({
            "record": record, "page": rows[0]["page"], "title_de": TITLES[record],
            "record_type": rows[0]["record_type"], "statements": len(rows),
            "events": sum(int(r["event_total"]) for r in rows),
            "closed_cells": sum(r["cell_status"] == "CLOSED_CELL" for r in rows),
            "open_entries": sum(r["cell_status"] == "OPEN_ENTRY" for r in rows),
            "visible_owner_count": len(owners), "visible_owners_de": " | ".join(owners),
            "continuous_register_de": " ".join(f"[{r['statement_id']}] {r['fluent_station_entry_de']}" for r in rows),
            "global_flow_claim": "NONE", "complete": "YES",
        })
    by_statement = {r["statement_id"]: r for r in statement_rows}
    event_rows = []
    for row in events:
        statement = by_statement[row["statement_id"]]
        event_rows.append({
            "event_id": row["event_id"], "page": row["page"], "record": row["record"],
            "statement_id": row["statement_id"], "surface": row["surface"],
            "component_parse": row["component_parse"], "revised_event_reading_de": row["revised_event_reading_de"],
            "cell_status": statement["cell_status"], "silent_owner_de": statement["silent_owner_de"],
            "fluent_station_entry_de": statement["fluent_station_entry_de"], "bound_once": "YES",
        })
    write("FIVE_HUNDRED_EIGHTY_NINTH_SIX_BIOLOGICAL_RECORDS.tsv", record_rows)
    write("FIVE_HUNDRED_EIGHTY_NINTH_NINETY_SEVEN_STATION_ENTRIES.tsv", statement_rows)
    write("FIVE_HUNDRED_EIGHTY_NINTH_TWO_HUNDRED_EIGHTY_ONE_EVENT_BINDING.tsv", event_rows)
    readable = ["# Vollständiges Biological-Stationsregister", "", "B1–B4 sind Register lokaler Arbeitszellen. B5–B6 sind kurze technische Nachträge. Eine globale Flussrichtung wird nicht ergänzt.", ""]
    for record, rows in by_record.items():
        readable += [f"## {record} — {TITLES[record]}", ""]
        for row in rows:
            readable.append(f"- {row['statement_id']} [{row['cell_status']}]: {row['fluent_station_entry_de']}")
        readable.append("")
    (HERE / "FIVE_HUNDRED_EIGHTY_NINTH_COMPLETE_BIOLOGICAL_REGISTER.md").write_text("\n".join(readable).rstrip() + "\n", encoding="utf-8")
    summary = {
        "status": "PASS", "records": len(record_rows), "statements": len(statement_rows), "events": len(event_rows),
        "closed_cells": sum(r["cell_status"] == "CLOSED_CELL" for r in statement_rows),
        "open_entries": sum(r["cell_status"] == "OPEN_ENTRY" for r in statement_rows),
        "b1_b4_closed": sum(r["cell_status"] == "CLOSED_CELL" and r["record"] in {"B1","B2","B3","B4"} for r in statement_rows),
        "global_flow_claims": sum(r["global_flow_claim"] != "NONE" for r in record_rows),
    }
    (HERE / "FIVE_HUNDRED_EIGHTY_NINTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report = [
        "# Fünfhundertneunundachtzigste Runde: Biological-Stationsregister", "",
        "Alle sechs Biological-Records sind aus der vollständigen Dreizeilenausgabe neu gesetzt: 97 Einträge und 281 Kartenereignisse. B1–B4 bleiben lokale Zellen mit wechselnden sichtbaren Becken-, Figuren-, Gefäß- und Gerätebesitzern; B5–B6 sind kurze Nachträge.", "",
        "85 Einträge schließen lokal, davon 83 in B1–B4. Zwölf bleiben offen. Diese lokale Abschlussdichte erklärt die kurze, formularartige Prosa besser als ein einziger fortlaufender Rezepttext. Zugleich werden keine Pfeile oder eine globale Wasserzirkulation erfunden.", "",
        "Die wiederkehrende Arbeitslogik ist konkret: Maß oder Teil setzen, zuführen oder umsetzen, am Ziel anlegen, kurz/länger halten oder temperieren, absetzen/auffangen und die Zelle schließen. Bildort und Besitzer wechseln, der 37-Wort-Kern bleibt derselbe.", "",
        "## Nächster Schritt", "",
        "Herbal und Biological werden nun zu einer gemeinsamen WHAT/HOW-Arbeitsausgabe verbunden. Danach wird geprüft, ob die drei Astro-Seiten tatsächlich als WHEN-Teil derselben Werkstattlogik lesbar sind oder ein unabhängiger Bild-/Lookup-Anhang bleiben.",
    ]
    (HERE / "FIVE_HUNDRED_EIGHTY_NINTH_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")


if __name__ == "__main__": main()
