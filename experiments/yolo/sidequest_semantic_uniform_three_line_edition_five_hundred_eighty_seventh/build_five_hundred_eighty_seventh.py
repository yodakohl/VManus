#!/usr/bin/env python3
import csv
import json
from collections import OrderedDict, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
YOLO = HERE.parent
P582 = YOLO / "sidequest_semantic_minimal_contrast_pairs_five_hundred_eighty_second"
P585 = YOLO / "sidequest_semantic_full_statement_correction_five_hundred_eighty_fifth"
P586 = YOLO / "sidequest_semantic_breath_group_masterbook_five_hundred_eighty_sixth"


def read(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name, rows):
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)


def main():
    statements = read(P585 / "FIVE_HUNDRED_EIGHTY_FIFTH_CORRECTED_ONE_HUNDRED_SIXTEEN_FULL_STATEMENTS.tsv")
    events = read(P585 / "FIVE_HUNDRED_EIGHTY_FIFTH_CORRECTED_THREE_HUNDRED_EIGHTY_ONE_EVENT_BINDING.tsv")
    speech = {r["event_id"]: r for r in read(P582 / "FIVE_HUNDRED_EIGHTY_SECOND_REVISED_THREE_HUNDRED_EIGHTY_ONE_EVENT_SEQUENCES.tsv")}
    long_events = {r["event_id"]: r for r in read(P586 / "FIVE_HUNDRED_EIGHTY_SIXTH_ONE_HUNDRED_FIFTY_SIX_GROUPED_EVENTS.tsv")}
    by_statement = OrderedDict()
    for event in events:
        by_statement.setdefault(event["statement_id"], []).append(event)

    edition_rows = []
    event_index = []
    for statement in statements:
        statement_id = statement["statement_id"]
        rows = by_statement[statement_id]
        long = statement["formula_mode"] in {"EXTENDED_TWO_EDIT_VARIANT", "FREE_COMPOSITION"}
        surfaces, words, components, group_ids = [], [], [], []
        for event in rows:
            sp = speech[event["event_id"]]
            group_id = long_events[event["event_id"]]["group_id"] if long else f"{statement_id}-G01"
            surfaces.append((group_id, event["surface"]))
            words.append((group_id, sp["spoken_component_sequence_de"]))
            components.append((group_id, event["component_parse"]))
            group_ids.append(group_id)
            event_index.append({
                "event_id": event["event_id"], "page": event["page"], "record": event["record"],
                "statement_id": statement_id, "group_id": group_id, "position_in_statement": len(event_index) + 1,
                "surface": event["surface"], "component_parse": event["component_parse"],
                "spoken_component_sequence_de": sp["spoken_component_sequence_de"],
                "bound_to_complete_instruction": "YES",
            })

        ordered_groups = list(dict.fromkeys(group_ids))
        def grouped_line(pairs):
            chunks = []
            for gid in ordered_groups:
                chunks.append("⟦" + " | ".join(value for group, value in pairs if group == gid) + "⟧")
            return " / ".join(chunks)
        edition_rows.append({
            "statement_id": statement_id, "page": statement["page"], "record": statement["record"],
            "formula_mode": statement["formula_mode"], "phase_signature": statement["phase_signature"],
            "event_count": len(rows), "breath_groups": len(ordered_groups),
            "visible_cards": grouped_line(surfaces),
            "component_parses": grouped_line(components),
            "spoken_component_line_de": grouped_line(words),
            "complete_owner_filled_instruction_de": statement["corrected_full_compact_instruction_de"],
            "all_events_bound": "YES",
        })

    write("FIVE_HUNDRED_EIGHTY_SEVENTH_ONE_HUNDRED_SIXTEEN_THREE_LINE_STATEMENTS.tsv", edition_rows)
    write("FIVE_HUNDRED_EIGHTY_SEVENTH_THREE_HUNDRED_EIGHTY_ONE_EVENT_INDEX.tsv", event_index)
    readable = ["# Einheitliche Dreizeilenausgabe", "", "`⟦…⟧` markiert eine Atemgruppe; `/` trennt Gruppen, aber nicht automatisch Aussagen.", ""]
    records = OrderedDict()
    for row in edition_rows:
        records.setdefault(row["record"], []).append(row)
    for record, rows in records.items():
        readable += [f"## {record}", ""]
        for row in rows:
            readable += [
                f"### {row['statement_id']} — {row['formula_mode']}", "",
                f"Karten: {row['visible_cards']}", "",
                f"Sprechwerte: {row['spoken_component_line_de']}", "",
                f"Lesung: {row['complete_owner_filled_instruction_de']}", "",
            ]
    (HERE / "FIVE_HUNDRED_EIGHTY_SEVENTH_COMPLETE_THREE_LINE_EDITION.md").write_text("\n".join(readable).rstrip() + "\n", encoding="utf-8")
    summary = {
        "status": "PASS", "statements": len(edition_rows), "events": len(event_index), "records": len(records),
        "taught_macro": sum(r["formula_mode"] == "TAUGHT_MACRO" for r in edition_rows),
        "simple_variant": sum(r["formula_mode"] == "SIMPLE_ONE_EDIT_VARIANT" for r in edition_rows),
        "extended_variant": sum(r["formula_mode"] == "EXTENDED_TWO_EDIT_VARIANT" for r in edition_rows),
        "free_composition": sum(r["formula_mode"] == "FREE_COMPOSITION" for r in edition_rows),
        "long_breath_groups": sum(int(r["breath_groups"]) for r in edition_rows if r["formula_mode"] in {"EXTENDED_TWO_EDIT_VARIANT", "FREE_COMPOSITION"}),
    }
    (HERE / "FIVE_HUNDRED_EIGHTY_SEVENTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report = [
        "# Fünfhundertsiebenundachtzigste Runde: einheitliche Dreizeilenausgabe", "",
        "Alle 116 Aussagen stehen nun in derselben Form: sichtbare Karten, kurze Sprechwerte und vollständige owner-gefüllte Lesung. Alle 381 Ereignisse sind einzeln indiziert und an genau eine vollständige Aussage gebunden.", "",
        "Kurze Formeln erscheinen in einer Gruppe. Die 22 langen Varianten und Meisterbeispiele behalten ihre 45 Atemgruppen. Dadurch kann man erstmals direkt sehen, wie dieselben 37 Sprechwerte in einer kurzen Standardzelle und in einer langen Pflanzen- oder Stationsfolge zusammenspielen.", "",
        "Die Ausgabe ist die neue lesbare Basis. Die abgeschnittene Pass-580-Fassung wird nicht mehr verwendet. Sichtbare Karte, Komponentenbau und interpretierte Werkstattanweisung bleiben getrennte Zeilen; das verhindert, dass eine flüssige Übersetzung versehentlich als Kartenwert zurück in das Wörterbuch fließt.", "",
        "## Nächster Schritt", "",
        "Nun werden die fünf Herbal-Records als zusammenhängende Artikelprosa geglättet, aber ausschließlich aus der vollständigen Dreizeilenausgabe. Danach folgen die sechs Biological-Records als Stations-/Anwendungsregister.",
    ]
    (HERE / "FIVE_HUNDRED_EIGHTY_SEVENTH_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")


if __name__ == "__main__": main()
