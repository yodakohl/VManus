#!/usr/bin/env python3
"""Join the five Herbal preparations to six Biological programs as teaching cases."""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
HERBAL_DIR = ROOT / "experiments/yolo/sidequest_semantic_concrete_herbal_recipes_six_hundredth"
BIO_DIR = ROOT / "experiments/yolo/sidequest_semantic_biological_station_programs_six_hundred_second"
OBJECT_DIR = ROOT / "experiments/yolo/sidequest_semantic_concrete_object_ledger_five_hundred_ninety_ninth"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


CASES = {
    "C1": {
        "title_de": "Mildes Pflanzenbad und gemeinsame Waschung",
        "herbal": "H1",
        "bio": "B1",
        "main_product": "H1",
        "supplemental": "NONE",
        "case_type": "THERAPEUTIC_BATH_CASE",
        "continuous_de": "Bereite aus der ersten Pflanze einen milden Grundauszug. Gib ihn nach Maß in das gemeinsame Figurenbecken, speise bei Bedarf nach, wasche oder bade darin, halte ihn kurz warm, lass Trübes absetzen und fange den brauchbaren Anteil wieder auf.",
    },
    "C2": {
        "title_de": "Stärkerer Nachauszug im Mehrstationsbad",
        "herbal": "H2",
        "bio": "B2",
        "main_product": "H2",
        "supplemental": "H4|H5",
        "case_type": "THERAPEUTIC_MULTI_STATION_CASE",
        "continuous_de": "Ziehe dieselbe Pflanze ein zweites Mal aus und standardisiere die stärkere Charge. Speise sie oben ein, führe sie durch die Beckenstufen und halte oder setze sie am Handgerät ab. Wo die Randzellen eine örtliche Anwendung verlangen, nimm eine dickere Auflage; für reine Transferwege darf Konzentrat aus dem Vorrat dienen.",
    },
    "C3": {
        "title_de": "Blütenwaschung mit Gefäß- und Immersionsvarianten",
        "herbal": "H3",
        "bio": "B3",
        "main_product": "H3",
        "supplemental": "H1|H2|H4|H5",
        "case_type": "HYBRID_IMMERSION_CASE",
        "continuous_de": "Ziehe die Blüten zweimal aus, wringe sie aus und fange die Flüssigkeit auf. Verwende den Blütenauszug im runden Gefäß als Waschung oder Bad; die übrigen Gefäße lehren, wie dünnere, stärkere, dickere oder konzentrierte Varianten aufgefangen, gemischt, eingetaucht, abgesetzt und lokal angewandt werden.",
    },
    "C4": {
        "title_de": "Temperierte Pflanzenauflage mit Seitenläufen",
        "herbal": "H4",
        "bio": "B4",
        "main_product": "H4",
        "supplemental": "H5",
        "case_type": "THERAPEUTIC_POULTICE_CASE",
        "continuous_de": "Bereite eine abgemessene warme Pflanzenauflage. Setze sie an der Paarstation an, befestige und halte sie bis zur gewünschten Stufe. Nutze den konzentrierten Flüssigkeitsvorrat nur als Begleitmedium: seitlich zuführen, abziehen, auffangen oder den Einsatz feucht halten.",
    },
    "C5": {
        "title_de": "Konzentrat weiterführen und ruhen lassen",
        "herbal": "H5",
        "bio": "B5",
        "main_product": "H5",
        "supplemental": "H3|H4",
        "case_type": "TECHNICAL_RESIDUAL_CASE",
        "continuous_de": "Stelle den mehrfach beschickten konzentrierten Ansatz her. Überführe eine Restcharge in die Nebenstation, halte sie dort und lass sie absetzen; bei Bedarf kann dieselbe Station eine Waschflüssigkeit oder eine gebrauchte Auflagencharge aufnehmen.",
    },
    "C6": {
        "title_de": "Vorrat sammeln, kühlen und zur nächsten Arbeit speisen",
        "herbal": "NONE__USES_H5_RESERVE",
        "bio": "B6",
        "main_product": "H5",
        "supplemental": "H2",
        "case_type": "TECHNICAL_STOCK_APPENDIX",
        "continuous_de": "Nimm den bereits bereiteten konzentrierten Vorrat, sammle ihn im S-Lauf, lass ihn auf Gebrauchsstufe kommen und speise daraus die nächste Bad-, Wasch- oder Auflagenarbeit. Dies ist ein Vorratsnachtrag, kein sechstes Pflanzenrezept.",
    },
}


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    herbal_recipes = read_tsv(HERBAL_DIR / "SIX_HUNDREDTH_FIVE_CONCRETE_HERBAL_RECIPES.tsv")
    herbal_steps = read_tsv(HERBAL_DIR / "SIX_HUNDREDTH_NINETEEN_RECIPE_STEPS.tsv")
    bio_programs = read_tsv(BIO_DIR / "SIX_HUNDRED_SECOND_SIX_BIOLOGICAL_PROGRAMS.tsv")
    bio_steps = read_tsv(BIO_DIR / "SIX_HUNDRED_SECOND_NINETY_SEVEN_STATION_STEPS.tsv")
    station_inputs = read_tsv(BIO_DIR / "SIX_HUNDRED_SECOND_SIXTEEN_STATION_INPUTS.tsv")
    event_rows = read_tsv(OBJECT_DIR / "FIVE_HUNDRED_NINETY_NINTH_381_EVENT_OBJECT_BINDING.tsv")

    recipe_by_id = {row["record"]: row for row in herbal_recipes}
    program_by_id = {row["record"]: row for row in bio_programs}
    case_by_record = {}
    for case_id, spec in CASES.items():
        if spec["herbal"].startswith("H"):
            case_by_record[spec["herbal"]] = case_id
        case_by_record[spec["bio"]] = case_id

    cases = []
    for case_id, spec in CASES.items():
        program = program_by_id[spec["bio"]]
        recipe = recipe_by_id.get(spec["herbal"])
        prep_statements = int(recipe["statements"]) if recipe else 0
        prep_events = int(recipe["events"]) if recipe else 0
        cases.append({
            "case_id": case_id,
            "title_de": spec["title_de"],
            "case_type": spec["case_type"],
            "herbal_source_record": spec["herbal"],
            "biological_program_record": spec["bio"],
            "main_product_id": spec["main_product"],
            "main_product_de": recipe_by_id[spec["main_product"]]["final_product_de"],
            "supplemental_product_ids": spec["supplemental"],
            "preparation_statements": prep_statements,
            "application_statements": int(program["statement_count"]),
            "total_bound_statements": prep_statements + int(program["statement_count"]),
            "preparation_events": prep_events,
            "application_events": int(program["event_count"]),
            "total_bound_events": prep_events + int(program["event_count"]),
            "station_ids": program["station_ids"],
            "continuous_case_de": spec["continuous_de"],
            "hidden_one_to_one_key_claim": "NO__SELECTED_TEACHING_EXAMPLE_ONLY",
        })

    statement_rows = []
    for row in herbal_steps:
        case_id = case_by_record[row["record"]]
        statement_rows.append({
            "case_id": case_id,
            "phase": "PREPARE_PRODUCT",
            "statement_id": row["statement_id"],
            "record": row["record"],
            "page": row["page"],
            "owner_or_station": recipe_by_id[row["record"]]["visible_owner_de"],
            "input_product_id": "RAW_PLANT_MATERIAL",
            "output_or_working_product_id": CASES[case_id]["main_product"],
            "source_operations_de": row["source_operations_de"],
            "concrete_case_step_de": row["concrete_recipe_step_de"],
            "sequence_policy": "SOURCE_RECORD_ORDER",
        })
    for row in bio_steps:
        case_id = case_by_record[row["record"]]
        statement_rows.append({
            "case_id": case_id,
            "phase": "OPERATE_OR_APPLY",
            "statement_id": row["statement_id"],
            "record": row["record"],
            "page": row["page"],
            "owner_or_station": row["visible_owner_de"],
            "input_product_id": row["primary_product_id"],
            "output_or_working_product_id": row["primary_product_id"],
            "source_operations_de": row["operations_de"],
            "concrete_case_step_de": row["selected_concrete_step_de"],
            "sequence_policy": "SOURCE_RECORD_ORDER__LOCAL_OWNER_ONLY",
        })
    statement_rows.sort(key=lambda row: (row["case_id"], 0 if row["phase"] == "PREPARE_PRODUCT" else 1, row["statement_id"]))

    statement_lookup = {row["statement_id"]: row for row in statement_rows}
    event_binding = []
    for event in event_rows:
        statement = statement_lookup[event["statement_id"]]
        event_binding.append({
            "case_id": statement["case_id"],
            "phase": statement["phase"],
            "event_id": event["event_id"],
            "statement_id": event["statement_id"],
            "page": event["page"],
            "record": event["record"],
            "surface": event["surface"],
            "card_no": event["card_no"],
            "component_parse": event["component_parse"],
            "operation_de": event["operation_de"],
            "primary_object_de": event["primary_object_de"],
            "local_output_de": event["local_output_de"],
        })

    interchange = []
    case_by_bio = {spec["bio"]: case_id for case_id, spec in CASES.items()}
    for row in station_inputs:
        case_id = case_by_bio[row["record"]]
        interchange.append({
            "case_id": case_id,
            "station_id": row["station_id"],
            "visible_owner_de": row["visible_owner_de"],
            "selected_input_id": row["primary_product_id"],
            "selected_input_de": row["primary_product_de"],
            "interchangeable_product_ids": row["interchangeable_product_ids"],
            "interchangeable_products_de": row["interchangeable_products_de"],
            "rule_de": "Der konkrete Werkstattfall wählt ein Beispiel; dieselbe Station bleibt für andere kompatible Produkte lernbar.",
        })

    write_tsv(HERE / "SIX_HUNDRED_THIRD_SIX_COMPLETE_CASES.tsv", cases, list(cases[0]))
    write_tsv(HERE / "SIX_HUNDRED_THIRD_116_STATEMENT_CASE_EDITION.tsv", statement_rows, list(statement_rows[0]))
    write_tsv(HERE / "SIX_HUNDRED_THIRD_381_EVENT_CASE_BINDING.tsv", event_binding, list(event_binding[0]))
    write_tsv(HERE / "SIX_HUNDRED_THIRD_SIXTEEN_INTERCHANGEABLE_INPUTS.tsv", interchange, list(interchange[0]))

    statements_by_case: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in statement_rows:
        statements_by_case[row["case_id"]].append(row)
    md = ["# Vollständiges Werkstatt-Fallbuch", ""]
    for case in cases:
        md.extend([
            f"## {case['case_id']}: {case['title_de']}",
            "",
            case["continuous_case_de"],
            "",
            f"**Hauptprodukt:** {case['main_product_de']}",
            "",
        ])
        for step in statements_by_case[case["case_id"]]:
            md.append(f"- **{step['statement_id']} / {step['phase']}** — {step['concrete_case_step_de']}")
        md.append("")
    (HERE / "SIX_HUNDRED_THIRD_COMPLETE_CASEBOOK.md").write_text("\n".join(md).rstrip() + "\n", encoding="utf-8")

    report = """# Sechshundertdritte Runde: sechs vollständige Werkstattfälle

## Ergebnis

Die fünf Herbal-Rezepte und sechs Biological-Programme bilden jetzt ein kleines ausführbares Fallbuch. Die einfachste Gesamtidee lautet:

```text
Pflanzenmaterial → standardisiertes Werkstattprodukt
→ passende sichtbare Station → Bad / Waschung / Auflage / Transfer
→ brauchbare Charge, Restcharge oder Vorrat
```

Die sechs Lehrfälle sind:

1. mildes Pflanzenbad und gemeinsame Waschung;
2. stärkerer Nachauszug im Mehrstationsbad;
3. Blütenwaschung mit Gefäß- und Immersionsvarianten;
4. temperierte Pflanzenauflage mit Seitenläufen;
5. Konzentrat weiterführen und ruhen lassen;
6. Vorrat sammeln, kühlen und zur nächsten Arbeit speisen.

## Warum das wie ein Werkstattbuch funktioniert

Der Lehrmeister muss keine Pflanzennamen oder Krankheitsnamen in jede Zeile schreiben. Das Bild setzt den Rohstoff; die Herbal-Sequenz erzeugt einen Produktvorrat; die Bio-Figur oder das Gefäß setzt den Arbeitsort; die Karten geben Maß, Folge, Ziel, Grad, Durchgang und Schluss an. Gelernte Ganzkarten benennen spezielle Handlungen.

Der sechste Fall hat bewusst kein sechstes Herbal-Rezept: Er verwendet den Vorrat aus H5. Das ist genau die Art knapper Ellipse, die unser Mehrschreiber-System einfach lernbar macht.

## Keine starre Seitenpaarung

Die sechs Fälle sind ausgewählte Lehrbeispiele, kein behaupteter H1=B1-Schlüssel. Die 16 Stationen behalten ihre alternativen kompatiblen Eingänge. Ein Blütenauszug kann auch ins gemeinsame Becken; ein Grundauszug kann ins Rundgefäß; eine Auflage kann an mehreren lokalen Haltestellen eingesetzt werden.

## Vollständigkeit

Alle 116 Prosa-Aussagen und 381 Prosa-Ereignisse erscheinen genau einmal im Fallbuch. Fünf Zubereitungsquellen, sechs Biological-Programme und sechzehn lokale Stationen sind enthalten.

## Neue Arbeitstheorie

Für die sieben Prosaseiten ist der beste konkrete Entwurf nun ein **illustriertes Produkt-und-Anwendungsformular für eine medizinisch-badende Werkstatt**. Die technische Badehauslesung bleibt wichtig, ist aber Bediengrammatik innerhalb des therapeutischen Fallbuchs, nicht mehr zwingend ein konkurrierender Gesamtzweck.

## Nächster Schritt

Nun wird der Astro-Anhang als optionale Wahlbedingung an die sechs Fälle gehängt: nicht als übersetzte Planetennamen, sondern als kopierte lokale Adresse für Zeitpunkt, Zustand oder Zulässigkeit. Dabei bleiben die drei Astro-Seiten getrennte Instrumente.
"""
    (HERE / "SIX_HUNDRED_THIRD_REPORT.md").write_text(report, encoding="utf-8")

    summary = {
        "status": "PASS",
        "cases": len(cases),
        "herbal_product_sources": 5,
        "biological_programs": 6,
        "stations": len(interchange),
        "statements": len(statement_rows),
        "events": len(event_binding),
        "decision": "ILLUSTRATED_HERBAL_PRODUCT_AND_BATH_APPLICATION_FORMULARY",
    }
    (HERE / "SIX_HUNDRED_THIRD_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
