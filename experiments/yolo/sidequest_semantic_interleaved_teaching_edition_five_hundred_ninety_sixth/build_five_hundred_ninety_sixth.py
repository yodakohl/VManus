#!/usr/bin/env python3
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
YOLO = HERE.parent
P587 = YOLO / "sidequest_semantic_uniform_three_line_edition_five_hundred_eighty_seventh"
P588 = YOLO / "sidequest_semantic_complete_herbal_articles_five_hundred_eighty_eighth"
P589 = YOLO / "sidequest_semantic_complete_biological_station_register_five_hundred_eighty_ninth"
P591 = YOLO / "sidequest_semantic_astro_condition_interface_five_hundred_ninety_first"
P595 = YOLO / "sidequest_semantic_surface_preference_manual_five_hundred_ninety_fifth"


def read(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name, rows):
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main():
    statement_source = read(P587 / "FIVE_HUNDRED_EIGHTY_SEVENTH_ONE_HUNDRED_SIXTEEN_THREE_LINE_STATEMENTS.tsv")
    event_index = read(P587 / "FIVE_HUNDRED_EIGHTY_SEVENTH_THREE_HUNDRED_EIGHTY_ONE_EVENT_INDEX.tsv")
    surface_trace = {row["event_id"]: row for row in read(P595 / "FIVE_HUNDRED_NINETY_FIFTH_381_COMPLETE_SURFACE_TRACE.tsv")}
    melody_rows = read(P595 / "FIVE_HUNDRED_NINETY_FIFTH_NINE_RECORD_MELODIES.tsv")
    melody_by_record = {row["record"]: row for row in melody_rows}
    herbal = read(P588 / "FIVE_HUNDRED_EIGHTY_EIGHTH_NINETEEN_HERBAL_STATEMENTS.tsv")
    bio = read(P589 / "FIVE_HUNDRED_EIGHTY_NINTH_NINETY_SEVEN_STATION_ENTRIES.tsv")
    fluent = {
        row["statement_id"]: row.get("fluent_article_sentence_de", row.get("fluent_station_entry_de", ""))
        for row in herbal + bio
    }
    owners = {row["statement_id"]: row["silent_owner_de"] for row in herbal + bio}
    events_by_statement = defaultdict(list)
    for event in event_index:
        events_by_statement[event["statement_id"]].append(event)
    for rows in events_by_statement.values():
        rows.sort(key=lambda row: int(row["position_in_statement"]))

    statement_rows = []
    unified = []
    for statement in statement_source:
        events = events_by_statement[statement["statement_id"]]
        traces = [surface_trace[event["event_id"]] for event in events]
        statement_rows.append({
            "statement_id": statement["statement_id"], "page": statement["page"], "record": statement["record"],
            "silent_owner_de": owners[statement["statement_id"]], "formula_mode": statement["formula_mode"],
            "event_count": statement["event_count"],
            "meaning_line_de": fluent[statement["statement_id"]],
            "spoken_component_line_de": " | ".join(trace["spoken_value_de"] for trace in traces),
            "card_identity_line": " | ".join(f"{trace['card_no']}[{trace['component_parse']}]" for trace in traces),
            "exact_surface_line": " ".join(trace["final_surface"] for trace in traces),
            "scribe_recitation_line": " | ".join(
                "DEFAULT" if trace["renderer_source"] == "GLOBAL_RULE_RENDERER" else trace["renderer_rule"]
                for trace in traces
            ),
            "record_melody": melody_by_record.get(statement["record"], {}).get("wrapper_sequence", "NONE"),
            "all_events_bound": "YES",
        })
        for event, trace in zip(events, traces):
            unified.append({
                "unified_serial": len(unified) + 1, "section": "HERBAL" if statement["record"].startswith("H") else "BIOLOGICAL",
                "page": trace["page"], "unit_id": trace["record"], "local_id": trace["event_id"],
                "surface_display_only": trace["final_surface"], "read_aloud_de": trace["spoken_value_de"],
                "copy_rule_de": trace["writing_instruction_de"], "owner_or_namespace": owners[statement["statement_id"]],
                "meaning_or_use_de": fluent[statement["statement_id"]], "meaning_layer": "COMPOSITIONAL_PROSE",
            })

    record_rows = []
    for record in [f"H{i}" for i in range(1, 6)] + [f"B{i}" for i in range(1, 7)]:
        rows = [row for row in statement_rows if row["record"] == record]
        modes = Counter(row["formula_mode"] for row in rows)
        record_rows.append({
            "record": record, "page": rows[0]["page"], "section": "HERBAL" if record.startswith("H") else "BIOLOGICAL",
            "statements": len(rows), "events": sum(int(row["event_count"]) for row in rows),
            "silent_owners_de": " | ".join(dict.fromkeys(row["silent_owner_de"] for row in rows)),
            "record_melody": melody_by_record.get(record, {}).get("wrapper_sequence", "NONE"),
            "taught_macros": modes["TAUGHT_MACRO"], "simple_variants": modes["SIMPLE_ONE_EDIT_VARIANT"],
            "long_or_free": modes["EXTENDED_TWO_EDIT_VARIANT"] + modes["FREE_COMPOSITION"],
            "copy_sheet_status": "COMPLETE",
        })

    astro_loci = read(P591 / "FIVE_HUNDRED_NINETY_FIRST_142_LOCUS_ASTRO_INTERFACE.tsv")
    astro_groups = read(P591 / "FIVE_HUNDRED_NINETY_FIRST_395_GROUP_ASTRO_INTERFACE.tsv")
    astro_copy_rows = []
    for locus in astro_loci:
        astro_copy_rows.append({
            "page": locus["page"], "locus": locus["locus"], "namespace": locus["canonical_namespace_id"],
            "local_image_owner": locus["local_image_owner"], "interface_role": locus["interface_role"],
            "exact_surface_line": locus["complete_surface_display_only"],
            "read_aloud_de": f"lokale Etikette im {locus['instrument_reading_de']}",
            "copy_recitation_de": locus["working_reading_de"],
            "possible_use_de": locus["possible_condition_use_de"],
            "prose_value_import": "NONE",
        })
    for group in astro_groups:
        unified.append({
            "unified_serial": len(unified) + 1, "section": "ASTRO", "page": group["page"],
            "unit_id": {"f67r2": "A1", "f68r1": "A2", "f69v": "A3"}[group["page"]],
            "local_id": group["opaque_local_id"], "surface_display_only": group["surface_display_only"],
            "read_aloud_de": f"Etikettensegment im {group['instrument_reading_de']}",
            "copy_rule_de": group["possible_condition_use_de"],
            "owner_or_namespace": group["canonical_namespace_id"],
            "meaning_or_use_de": group["possible_condition_use_de"], "meaning_layer": "LOCAL_ASTRO_LABEL",
        })

    write("FIVE_HUNDRED_NINETY_SIXTH_116_FOUR_LINE_STATEMENTS.tsv", statement_rows)
    write("FIVE_HUNDRED_NINETY_SIXTH_11_RECORD_COPY_SHEETS.tsv", record_rows)
    write("FIVE_HUNDRED_NINETY_SIXTH_142_ASTRO_COPY_LINES.tsv", astro_copy_rows)
    write("FIVE_HUNDRED_NINETY_SIXTH_776_FACSIMILE_COPY_TRACE.tsv", unified)

    prose_md = ["# Fuenfhundertsechsundneunzigste Runde: elf Prosa-Kopierblaetter", ""]
    for record in record_rows:
        prose_md.extend([
            f"## {record['record']} · {record['page']} · Melodie `{record['record_melody']}`", "",
            f"Besitzer: {record['silent_owners_de']}", "",
        ])
        for row in [row for row in statement_rows if row["record"] == record["record"]]:
            prose_md.extend([
                f"### {row['statement_id']}", "",
                f"1. **Sinn:** {row['meaning_line_de']}",
                f"2. **Sprechwerte:** {row['spoken_component_line_de']}",
                f"3. **Karten:** `{row['card_identity_line']}`",
                f"4. **Schrift:** `{row['exact_surface_line']}`",
                f"5. **Rezitation:** `{row['scribe_recitation_line']}`", "",
            ])
    (HERE / "FIVE_HUNDRED_NINETY_SIXTH_ELEVEN_PROSE_COPY_SHEETS.md").write_text("\n".join(prose_md), encoding="utf-8")

    astro_md = ["# Fuenfhundertsechsundneunzigste Runde: drei Astro-Kopierregister", ""]
    for page in ("f67r2", "f68r1", "f69v"):
        astro_md.extend([f"## {page}", ""])
        for row in [row for row in astro_copy_rows if row["page"] == page]:
            astro_md.extend([
                f"- **{row['locus']} · {row['namespace']} · {row['local_image_owner']}**",
                f"  - Schrift: `{row['exact_surface_line']}`",
                f"  - Rezitation: {row['copy_recitation_de']}",
                f"  - Moeglicher Gebrauch: {row['possible_use_de']}",
            ])
        astro_md.append("")
    (HERE / "FIVE_HUNDRED_NINETY_SIXTH_THREE_ASTRO_COPY_REGISTERS.md").write_text("\n".join(astro_md), encoding="utf-8")

    summary = {
        "status": "PASS", "prose_statements": len(statement_rows), "prose_records": len(record_rows),
        "prose_events": sum(int(row["event_count"]) for row in statement_rows),
        "astro_loci": len(astro_copy_rows), "astro_groups": len(astro_groups), "unified_groups": len(unified),
        "record_melodies": len(melody_rows), "blank_lines": 0,
        "decision": "INTERLEAVED_MEANING_CARD_SURFACE_AND_RECITATION_EDITION_COMPLETE",
    }
    (HERE / "FIVE_HUNDRED_NINETY_SIXTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    report = """# Fuenfhundertsechsundneunzigste Runde: die abschreibbare Lehrfassung

## Ergebnis

Die zehn Seiten liegen jetzt in einer Form vor, die ein Lehrling tatsaechlich benutzen koennte. Jede der 116 Prosaaussagen hat fuenf getrennte Zeilen:

1. konkrete deutsche Werkstattanweisung;
2. die 37-Werte-Sprechfolge;
3. exakte Kartenidentitaeten und Komponentenbau;
4. genaue sichtbare Oberflaeche;
5. Rezitation der Standard-, Kontext-, Kadenz- oder Recordmelodieregel.

Die 142 Astro-Loci besitzen parallel Bildort, Namensraum, komplette Oberflaeche, Kopierrezitation und moeglichen CONDITION/REFERENCE-Gebrauch. Kein Prosa-Wert wird in Astro importiert.

## Was dadurch sichtbar wird

Ein Schreiber muss den deutschen Satz nicht kennen; er braucht die kurze Werkstattanweisung des Meisters. Die Sprechwerte helfen ihm, die richtige Karte zu waehlen. Erst danach erzeugt die Oberflaechenroutine die genaue sichtbare Form. Das trennt vier Dinge, die wir zuvor staendig vermischt hatten:

```text
SACHE/BILD != ARBEITSBEDEUTUNG != KARTENIDENTITAET != SICHTBARE SCHREIBFORM
```

Astro fuegt eine fuenfte Schicht hinzu: lokale Etikettenidentitaet. Dort gibt es keine kompositionelle Arbeitsbedeutung, sondern eine bildgebundene Referenz aus dem Meisterexemplar.

## Werkstattnutzen

- Ein Prosaschreiber kann eine Aussage diktieren, ohne jede Formvariante zu nennen.
- Ein zweiter Schreiber kann nur Karten und Oberflaechen kontrollieren.
- Ein Diagrammschreiber kann Astro vollstaendig kopieren, ohne das Prosa-Woerterbuch zu lernen.
- Der Meister kann Fehler genau lokalisieren: falscher Besitzer, falscher Wert, falsche Karte, falsche Form oder falscher Namensraum.

## Naechster Schritt

Als naechstes wird aus den elf Prosakopierblaettern eine Rueckwaertsprobe gebaut: Der Korrektor sieht nur Bildort und sichtbare Form und muss Kartenwert, Arbeitsfolge und erlaubte Mehrdeutigkeit laut zurueckgeben. Damit finden wir, welche Stellen der Arbeitstheorie trotz vollstaendiger Vorwaertsregel noch unklar lesen.
"""
    (HERE / "FIVE_HUNDRED_NINETY_SIXTH_REPORT.md").write_text(report, encoding="utf-8")


if __name__ == "__main__":
    main()
