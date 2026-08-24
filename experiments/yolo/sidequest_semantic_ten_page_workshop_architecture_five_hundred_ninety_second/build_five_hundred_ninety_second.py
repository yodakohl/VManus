#!/usr/bin/env python3
import csv
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
YOLO = HERE.parent
P587 = YOLO / "sidequest_semantic_uniform_three_line_edition_five_hundred_eighty_seventh"
P588 = YOLO / "sidequest_semantic_complete_herbal_articles_five_hundred_eighty_eighth"
P589 = YOLO / "sidequest_semantic_complete_biological_station_register_five_hundred_eighty_ninth"
P591 = YOLO / "sidequest_semantic_astro_condition_interface_five_hundred_ninety_first"


def read(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name, rows):
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main():
    event_rows = read(P587 / "FIVE_HUNDRED_EIGHTY_SEVENTH_THREE_HUNDRED_EIGHTY_ONE_EVENT_INDEX.tsv")
    statements = read(P587 / "FIVE_HUNDRED_EIGHTY_SEVENTH_ONE_HUNDRED_SIXTEEN_THREE_LINE_STATEMENTS.tsv")
    herbal_articles = read(P588 / "FIVE_HUNDRED_EIGHTY_EIGHTH_FIVE_COMPLETE_HERBAL_ARTICLES.tsv")
    herbal_statements = read(P588 / "FIVE_HUNDRED_EIGHTY_EIGHTH_NINETEEN_HERBAL_STATEMENTS.tsv")
    bio_records = read(P589 / "FIVE_HUNDRED_EIGHTY_NINTH_SIX_BIOLOGICAL_RECORDS.tsv")
    bio_statements = read(P589 / "FIVE_HUNDRED_EIGHTY_NINTH_NINETY_SEVEN_STATION_ENTRIES.tsv")
    astro_groups = read(P591 / "FIVE_HUNDRED_NINETY_FIRST_395_GROUP_ASTRO_INTERFACE.tsv")
    astro_loci = read(P591 / "FIVE_HUNDRED_NINETY_FIRST_142_LOCUS_ASTRO_INTERFACE.tsv")

    statement_owner = {row["statement_id"]: row["silent_owner_de"] for row in herbal_statements + bio_statements}
    statement_reading = {
        row["statement_id"]: row.get("fluent_article_sentence_de", row.get("fluent_station_entry_de", ""))
        for row in herbal_statements + bio_statements
    }
    statement_complete = {row["statement_id"]: row["complete_owner_filled_instruction_de"] for row in statements}

    unified = []
    for event in event_rows:
        section = "HERBAL" if event["record"].startswith("H") else "BIOLOGICAL"
        unified.append({
            "unified_serial": len(unified) + 1,
            "section": section,
            "page": event["page"],
            "unit_id": event["record"],
            "local_statement_or_locus": event["statement_id"],
            "local_event_id": event["event_id"],
            "surface_display_only": event["surface"],
            "reader_layer": "SHARED_COMPOSITIONAL_PROSE_GRAMMAR",
            "portable_or_local_value_de": event["spoken_component_sequence_de"],
            "silent_owner_or_namespace": statement_owner[event["statement_id"]],
            "complete_local_instruction_de": statement_complete[event["statement_id"]],
            "section_role": "WHAT_MATERIAL_AND_PREPARATION" if section == "HERBAL" else "HOW_WHERE_LOCAL_STATION_AND_APPLICATION",
            "handoff_status": "WORKSHOP_MEMORY_ONLY__NO_WRITTEN_CROSS_POINTER",
            "exact_source_binding": "PASS587_EVENT_INDEX",
        })
    for group in astro_groups:
        unified.append({
            "unified_serial": len(unified) + 1,
            "section": "ASTRO",
            "page": group["page"],
            "unit_id": {"f67r2": "A1", "f68r1": "A2", "f69v": "A3"}[group["page"]],
            "local_statement_or_locus": group["locus"],
            "local_event_id": group["opaque_local_id"],
            "surface_display_only": group["surface_display_only"],
            "reader_layer": "LOCAL_CELESTIAL_EXEMPLAR_LABEL",
            "portable_or_local_value_de": f"Etikettensegment im {group['instrument_reading_de']}",
            "silent_owner_or_namespace": group["canonical_namespace_id"],
            "complete_local_instruction_de": group["possible_condition_use_de"],
            "section_role": "OPTIONAL_CONDITION_OR_REFERENCE",
            "handoff_status": "OPTIONAL_WORKSHOP_USE__NO_WRITTEN_PROSE_POINTER",
            "exact_source_binding": "PASS591_ASTRO_INTERFACE",
        })

    unit_rows = []
    for row in herbal_articles:
        unit_rows.append({
            "unit_id": row["record"], "page": row["page"], "section": "HERBAL",
            "section_role": "WHAT_MATERIAL_AND_PREPARATION", "visible_groups": int(row["events"]),
            "internal_units": int(row["statements"]), "silent_owner_or_namespace": row["silent_owner_de"],
            "continuous_working_reading_de": row["continuous_article_de"],
            "output_to_next_register_de": "vorbereiteter Stoff/Ansatz bleibt im Werkstattgedaechtnis; keine Zielstation wird ausgeschrieben",
            "explicit_cross_pointer": "NO",
        })
    for row in bio_records:
        unit_rows.append({
            "unit_id": row["record"], "page": row["page"], "section": "BIOLOGICAL",
            "section_role": "HOW_WHERE_LOCAL_STATION_AND_APPLICATION", "visible_groups": int(row["events"]),
            "internal_units": int(row["statements"]), "silent_owner_or_namespace": row["visible_owners_de"],
            "continuous_working_reading_de": row["continuous_register_de"],
            "output_to_next_register_de": "lokaler Arbeitszustand schliesst meist in derselben Zelle; keine Pflanzennummer wird ausgeschrieben",
            "explicit_cross_pointer": "NO",
        })
    for page, unit, title in (
        ("f67r2", "A1", "zwei getrennte Himmelsraeder fuer grobe und feine Bedingungs-/Referenzwahl"),
        ("f68r1", "A2", "mehrpaneeliger Sternatlas mit 28 raeumlichen Sternplaetzen"),
        ("f69v", "A3", "drei getrennte Himmelsraeder; links 28 lokale Plaetze, Mitte Wetter, rechts Licht/Gestirn"),
    ):
        groups = [row for row in astro_groups if row["page"] == page]
        loci = [row for row in astro_loci if row["page"] == page]
        unit_rows.append({
            "unit_id": unit, "page": page, "section": "ASTRO",
            "section_role": "OPTIONAL_CONDITION_OR_REFERENCE", "visible_groups": len(groups),
            "internal_units": len(loci),
            "silent_owner_or_namespace": " | ".join(sorted({row["canonical_namespace_id"] for row in groups})),
            "continuous_working_reading_de": title,
            "output_to_next_register_de": "lokale Himmelsbedingung kann im Meisterexemplar nachgeschlagen werden; kein Prosastring wird eingesetzt",
            "explicit_cross_pointer": "NO",
        })

    page_rows = []
    for page in ("f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r", "f67r2", "f68r1", "f69v"):
        units = [row for row in unit_rows if row["page"] == page]
        page_rows.append({
            "page": page,
            "section": units[0]["section"],
            "unit_ids": "|".join(row["unit_id"] for row in units),
            "visible_groups": sum(int(row["visible_groups"]) for row in units),
            "internal_units": sum(int(row["internal_units"]) for row in units),
            "page_workshop_role_de": {
                "HERBAL": "Bildbesitzer setzen; Stoff- und Zubereitungsartikel in offener Prosa lesen",
                "BIOLOGICAL": "lokale Figur/Becken/Station setzen; kurze Arbeits- und Anwendungszellen lesen",
                "ASTRO": "lokales Himmelsinstrument zeigen; Etikette nur im richtigen Namensraum nachschlagen",
            }[units[0]["section"]],
            "cross_page_rule_de": "gemeinsame Werkstattpraxis, aber keine automatisch geerbte konkrete Referenz",
        })

    manual = [
        (1, "DRAW_OWNER", "Bild und lokale Raumaufteilung zuerst anlegen", "sichtbarer Besitzer/Instrumentplatz"),
        (2, "DECLARE_SECTION", "Herbal, Biological oder Astro ausrufen", "richtige Leseschicht"),
        (3, "HERBAL_OWNER", "bei Herbal die abgebildete Pflanze als stummes Thema aktivieren", "WHAT"),
        (4, "HERBAL_COMPOSE", "37 kurze Werkstattwerte zu Stoff-/Zubereitungsaussagen zusammensetzen", "offener Artikel"),
        (5, "BIO_OWNER", "bei Biological die kleinste sichtbare Figur/Becken/Station aktivieren", "HOW/WHERE"),
        (6, "BIO_COMPOSE", "dieselbe Werkstattgrammatik mit lokalem Stationsbesitzer lesen", "lokale Arbeitszelle"),
        (7, "CLOSE_LOCAL", "eine gelernte Schlusskonstruktion beendet nur ihre Zelle", "kein globales Zeilenende"),
        (8, "MEMORY_HANDOFF", "Stoff oder Ansatz nur dann zwischen Registern tragen, wenn der Meister ihn nennt", "keine geschriebene Eins-zu-eins-Paarung"),
        (9, "ASTRO_OPTION", "Himmelsanhang nur aufrufen, wenn eine Bedingung verlangt ist", "CONDITION/REFERENCE"),
        (10, "ASTRO_NAMESPACE", "Seite, Rad/Paneel und lokalen Bildplatz zeigen", "einer von 13 Namensraeumen"),
        (11, "ASTRO_COPY", "vollstaendige lokale Etikette in Quellordnung lesen", "keine Prosa-Komposition"),
        (12, "ASTRO_LOOKUP", "konkreten Wert nur aus diesem lokalen Meisterexemplar holen", "optionale Himmelsbedingung"),
        (13, "RESET_ASTRO", "bei Rad-, Paneel- oder Seitenwechsel alle Astro-Schluessel loeschen", "kein f68-f69-Join"),
        (14, "NO_ORIENTATION", "editorische Reihenfolge nicht als Kreisrichtung lesen", "kein Start/keine Rotation"),
        (15, "CORRECT", "Oberflaeche, Besitzer, Komposition und lokalen Abschluss getrennt pruefen", "mehrschreiberfaehige Ruecklesung"),
    ]
    manual_rows = [{"step": n, "operation": op, "instruction_de": text, "output": output} for n, op, text, output in manual]

    architecture_rows = [
        {
            "model": "WHAT_HOW_PLUS_OPTIONAL_CONDITION_REFERENCE",
            "fit_de": "Herbal und Biological teilen Grammatik; Astro liefert bei Bedarf lokale Himmelsbedingungen aus eigener Etikettenschicht",
            "strength_de": "erklaert Bilder, Registerunterschiede und praktische Gesamtfolge ohne Stringjoin",
            "cost_de": "konkrete Uebergaben und Astro-Nutzung muessen im Werkstattgedaechtnis stehen",
            "working_rank": 1,
        },
        {
            "model": "WHAT_HOW_PLUS_INDEPENDENT_CELESTIAL_ATLAS",
            "fit_de": "Herbal/Biological bilden das praktische Paar; Astro ist ein eigener Himmels-Lehr- oder Merkatlas",
            "strength_de": "erklaert fehlende Verweise, 13 Namensraeume und fehlende Orientierung am einfachsten",
            "cost_de": "erklaert weniger gut, warum genau dieser Atlas mit dem praktischen Teil zusammengebunden ist",
            "working_rank": 2,
        },
        {
            "model": "THREE_INDEPENDENT_IMAGE_REGISTERS",
            "fit_de": "Pflanzen-, Bad- und Himmelsseiten teilen nur eine Werkstatt und Exemplarlogik",
            "strength_de": "braucht keine thematische Gesamtidee",
            "cost_de": "verschenkt die gemeinsame Herbal/Biological-Grammatik und den praktischen Bildzusammenhang",
            "working_rank": 3,
        },
    ]

    write("FIVE_HUNDRED_NINETY_SECOND_776_UNIFIED_WORKSHOP_LEDGER.tsv", unified)
    write("FIVE_HUNDRED_NINETY_SECOND_FOURTEEN_UNIT_ARCHITECTURE.tsv", unit_rows)
    write("FIVE_HUNDRED_NINETY_SECOND_TEN_PAGE_ROLES.tsv", page_rows)
    write("FIVE_HUNDRED_NINETY_SECOND_FIFTEEN_STEP_MANUAL.tsv", manual_rows)
    write("FIVE_HUNDRED_NINETY_SECOND_ARCHITECTURE_COMPARISON.tsv", architecture_rows)

    readable = ["# Fuenfhundertzweiundneunzigste Runde: lesbare Zehn-Seiten-Werkstattausgabe", ""]
    for row in unit_rows:
        readable.extend([
            f"## {row['unit_id']} · {row['page']} · {row['section_role']}", "",
            f"**Stummer Besitzer/Namensraum:** {row['silent_owner_or_namespace']}", "",
            row["continuous_working_reading_de"], "",
            f"**Uebergabe:** {row['output_to_next_register_de']}", "",
        ])
    (HERE / "FIVE_HUNDRED_NINETY_SECOND_COMPLETE_TEN_PAGE_EDITION.md").write_text("\n".join(readable), encoding="utf-8")

    summary = {
        "status": "PASS",
        "pages": len(page_rows), "units": len(unit_rows), "visible_groups": len(unified),
        "prose_events": sum(row["section"] != "ASTRO" for row in unified),
        "astro_groups": sum(row["section"] == "ASTRO" for row in unified),
        "prose_statements": len(statements), "astro_loci": len(astro_loci),
        "prose_reader_values": 37, "astro_namespaces": len({row["silent_owner_or_namespace"] for row in unified if row["section"] == "ASTRO"}),
        "explicit_cross_register_pointers": 0,
        "decision": "WHAT_HOW_PLUS_OPTIONAL_CONDITION_REFERENCE_SELECTED",
    }
    (HERE / "FIVE_HUNDRED_NINETY_SECOND_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    report = f"""# Fuenfhundertzweiundneunzigste Runde: eine Werkstatt, zwei Lesemaschinen

## Neue Gesamtfassung

Die beste Theorie fuer die zehn Seiten ist jetzt **nicht** ein einziges durchgehendes Woerterbuch. Die kleine Werkstatt betreibt zwei leicht lehrbare Lesemaschinen:

1. **Herbal + Biological:** 37 kurze gesprochene Werte werden kompositionell gelesen. Das Bild setzt den stummen Besitzer. Herbal entfaltet offene Stoff-/Zubereitungsartikel (`WAS`); Biological setzt dieselben Werte in kurze lokale Arbeits- und Anwendungszellen (`WIE/WO`).
2. **Astro:** 395 Gruppen werden als 142 lokal gelernte Etiketten in 13 Namensraeumen gelesen. Sie koennen eine Himmelsbedingung oder Referenz liefern, werden aber nicht mit der Prosa-Grammatik zerlegt.

Die vollstaendige Ausgabe bindet {summary['visible_groups']} sichtbare Gruppen: {summary['prose_events']} Prosaereignisse und {summary['astro_groups']} Astrogruppen. Kein Zeichen bleibt ohne Werkstattfunktion. Bei Astro ist die Funktion jedoch eine lokale Etikettenadresse, keine erfundene Wortuebersetzung.

## Der wahrscheinlichste Buchzweck

Das fuehrende Modell ist ein bebildertes praktisches Kompendium:

```text
Pflanzenbild -> WAS wird vorbereitet
Bad-/Stationsbild -> WIE und WO wird es gehandhabt oder angewandt
Himmelsinstrument -> unter welcher BEDINGUNG kann ein lokaler Meistereintrag konsultiert werden
```

Der Himmelsanhang ist optional. Ein Bad- oder Pflanzenartikel benoetigt nicht sichtbar immer einen Astroeintrag. Umgekehrt ist kein Astroplatz an genau eine Pflanze oder Station gebunden. Diese lose Kopplung passt besser zu einem realen Werkstattbuch als unser frueheres strenges `WHAT/HOW/WHEN`: Ein Meister kann die Himmelslage bei Bedarf muendlich oder aus einem zweiten Register einbringen.

## Was mehrere Schreiber lernen

- Bilder und Raumeinteilung kommen zuerst.
- In Prosa wird der Bildbesitzer still gehalten und nur die kurze Arbeitsfolge gesprochen.
- Ein Zellschluss gilt lokal, nicht automatisch fuer Zeile, Absatz oder ganzes Verfahren.
- Zwischen Herbal und Biological wird ein Stoff nur durch Werkstattwissen uebergeben; die Seiten schreiben keine Paarungsnummer.
- Astro beginnt mit einem harten Registerwechsel: Seite, Rad/Paneel und Bildplatz muessen gezeigt werden.
- Ein Astroetikett wird als Ganzes aus dem richtigen lokalen Exemplar gelesen.
- Bei jedem Instrumentwechsel werden Orientierung und lokale Schluessel geloescht.

## Staerkster Rivale

Fast gleich gut bleibt: Herbal/Biological sind ein praktisches Paar, Astro dagegen ein unabhaengiger Himmels-Lehratlas. Der Unterschied ist vorerst nicht textlich entscheidbar. Wir behalten die praktischere Gesamtlesung als Arbeitsbasis, aber bauen keine konkrete Behandlung, Pflanze oder Handlung an einen Astroplatz.

## Naechster Schritt

Als naechstes wird geprueft, welche Aufgaben verschiedene Haende in dieser Zwei-Maschinen-Werkstatt haben koennten: Bildbesitzer setzen, Prosa komponieren, Astroetiketten kopieren, Zellen schliessen und Fehler korrigieren. Das soll die Theorie einfacher lehrbar machen, nicht neue Bedeutungen erfinden.
"""
    (HERE / "FIVE_HUNDRED_NINETY_SECOND_REPORT.md").write_text(report, encoding="utf-8")


if __name__ == "__main__":
    main()
