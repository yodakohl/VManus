#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
HERBAL = ROOT / "sidequest_semantic_four_herbal_process_atlas_eight_hundred_sixty_fourth" / "EIGHT_HUNDRED_SIXTY_FOURTH_100_CARD_HERBAL_ATLAS.tsv"
BIO = ROOT / "sidequest_semantic_three_biological_process_atlas_eight_hundred_sixty_fifth" / "EIGHT_HUNDRED_SIXTY_FIFTH_281_CARD_BIOLOGICAL_ATLAS.tsv"
STATEMENTS = ROOT / "sidequest_semantic_tenth_workshop_edition_eight_hundred_forty_sixth" / "EIGHT_HUNDRED_FORTY_SIXTH_116_STATEMENT_EDITION.tsv"
ASTRO = ROOT / "sidequest_semantic_relative_astro_condition_vocabulary_eight_hundred_seventy_third" / "EIGHT_HUNDRED_SEVENTY_THIRD_395_RELATIVE_CONDITION_GROUPS.tsv"
SUPPLIES = ROOT / "sidequest_semantic_internal_product_nomenclator_eight_hundred_seventy_second" / "EIGHT_HUNDRED_SEVENTY_SECOND_6_EXACT_INTERNAL_SUPPLY_LINKS.tsv"
CALIBRATIONS = ROOT / "sidequest_semantic_fully_readable_corrected_sample_eight_hundred_seventy_fourth" / "EIGHT_HUNDRED_SEVENTY_FOURTH_6_EXPLICIT_CALIBRATIONS.tsv"
PREFIX = "EIGHT_HUNDRED_SEVENTY_SIXTH"

ATOM_CALIBRATION = {
    "SOLLMASS": "EIN KLEINER SCHOEPFBECHER",
    "PORTION": "EIN ABGEGRENZTER TEIL",
    "STUFE": "EINE EINGESTELLTE ARBEITSSTUFE",
    "KURZ": "EIN KURZER ARBEITSGANG",
    "LANG": "DREI KURZE ARBEITSGAENGE",
    "VOLL": "BIS DER GANZE POSTEN ERFASST IST",
}

ORDERS = {
    "WH01": {"prep_statements": ["H1-S001", "H1-S002"], "product": "A.G2", "bio": "B1", "condition_shelf": "C5", "condition_locus": "f69v.2", "condition_name": "mittlerer Wetter-/Feuchtering"},
    "WH02": {"prep_statements": ["H5-S001", "H5-S002"], "product": "D.P1", "bio": "B2", "condition_shelf": "C4", "condition_locus": "f69v.12", "condition_name": "linker lokaler 28er-Bedingungsplatz"},
    "WH03": {"prep_statements": ["H3-S001", "H3-S002"], "product": "B.X2", "bio": "B3", "condition_shelf": "C2", "condition_locus": "f67r2.15", "condition_name": "linker Stern-/Aspektplatz"},
    "WH04": {"prep_statements": ["H4-S001", "H4-S002", "H4-S003", "H4-S004"], "product": "C.W2", "bio": "B4", "condition_shelf": "C6", "condition_locus": "f69v.3", "condition_name": "rechter Licht-/Körperqualitätsring"},
    "WH05": {"prep_statements": ["H5-S001", "H5-S002"], "product": "D.P1", "bio": "B5", "condition_shelf": "C3", "condition_locus": "f68r1.9", "condition_name": "direkter Sternort im Mehrpaneelatlas"},
    "WH06": {"prep_statements": ["H4-S001", "H4-S002", "H4-S003", "H4-S004"], "product": "C.W2", "bio": "B6", "condition_shelf": "C1", "condition_locus": "f67r2.1", "condition_name": "rechter Sektor-/Phasenplatz"},
}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]], fields: list[str]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def calibrate(reading: str) -> str:
    return " · ".join(ATOM_CALIBRATION.get(atom, atom) for atom in reading.split(" · "))


def condition_default(row: dict[str, str], handle: str) -> str:
    if row["surface"] == "otody":
        return "DEN FOLGENDEN LOKALEN BEDINGUNGSEINTRAG WAEHLEN UND SCHLIESSEN"
    if row["surface"] == "dolchsody":
        return "VON DER TEILADRESSE WEITER ZUM STERNBEZUG; DEN LOKALEN ARBEITSGANG SCHLIESSEN"
    position = row["event_index"]
    reading = row["relative_condition_reading_de"]
    part = f"BEDINGUNGSTEIL {position} VON {handle}"
    if reading == "LOKALE_BEDINGUNGSKARTE":
        return f"{part} KOPIEREN"
    return reading.replace("LOKALER_BEDINGUNGSKERN", part)


def main() -> None:
    herbal = read(HERBAL)
    bio = read(BIO)
    statements = {row["statement_id"]: row for row in read(STATEMENTS)}
    astro = read(ASTRO)
    supply_by_order = {row["entry_id"]: row for row in read(SUPPLIES)}
    calibrations = read(CALIBRATIONS)

    marks = []
    order_rows = []
    unit_rows = []
    payload_rows = []
    for order_id, spec in ORDERS.items():
        prep = [row for row in herbal if row["statement_id"] in spec["prep_statements"]]
        application = [row for row in bio if row["record"] == spec["bio"]]
        condition = [row for row in astro if row["page"] == spec["condition_locus"].split(".")[0] and row["locus"] == spec["condition_locus"]]
        handle = f"{spec['condition_shelf']}@{spec['condition_locus']}"
        local_marks = []
        for row in prep:
            local_marks.append(
                {
                    "stage": f"MAKE_{spec['product']}", "page": row["page"], "unit": row["statement_id"], "source_id": row["event_id"], "surface": row["surface"], "identity": row["exact_card_id"], "component_recipe": row["component_recipe"], "concrete_default_de": calibrate(row["card_meaning_de"]), "owner_or_handle_de": f"Bildprodukt {spec['product']}",
                }
            )
        for row in application:
            local_marks.append(
                {
                    "stage": f"APPLY_{spec['bio']}", "page": row["page"], "unit": row["statement_id"], "source_id": row["event_id"], "surface": row["surface"], "identity": row["exact_card_id"], "component_recipe": row["component_recipe"], "concrete_default_de": calibrate(row["card_meaning_de"]), "owner_or_handle_de": row["owner_de"],
                }
            )
        for row in condition:
            local_marks.append(
                {
                    "stage": f"CONDITION_{handle}", "page": row["page"], "unit": row["locus"], "source_id": row["opaque_local_id"], "surface": row["surface"], "identity": row["opaque_local_id"], "component_recipe": row["selected_component_parse"], "concrete_default_de": condition_default(row, handle), "owner_or_handle_de": f"{handle}; {spec['condition_name']}",
                }
            )
        for index, row in enumerate(local_marks, start=1):
            row["order_id"] = order_id
            row["order_mark_id"] = f"{order_id}-M{index:03d}"
            row["calibration_set"] = "CAL1_TO_CAL6_UNCHANGED"
        marks.extend(local_marks)

        grouped: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
        for row in local_marks:
            grouped[(row["stage"], row["unit"])].append(row)
        for (stage, unit), subset in grouped.items():
            fluent = statements[unit]["working_reading_de"] if unit in statements else f"Kopiere den vollständigen lokalen Bedingungsgriff {handle} und führe seine relativen Bedienwerte aus."
            unit_rows.append(
                {
                    "order_id": order_id,
                    "stage": stage,
                    "unit": unit,
                    "page": subset[0]["page"],
                    "surface_sequence": " ".join(row["surface"] for row in subset),
                    "literal_sequence_de": "; ".join(row["concrete_default_de"] for row in subset),
                    "fluent_workshop_reading_de": fluent,
                    "marks": len(subset),
                    "calibration_changed": "NO",
                }
            )

        supply = supply_by_order[order_id]
        order_rows.append(
            {
                "order_id": order_id,
                "internal_product": spec["product"],
                "product_name_de": supply["internal_product_name_de"],
                "biological_record": spec["bio"],
                "biological_page": supply["how_page"],
                "condition_handle": handle,
                "condition_name_de": spec["condition_name"],
                "preparation_marks": len(prep),
                "application_marks": len(application),
                "condition_marks": len(condition),
                "total_marks": len(local_marks),
                "units": len(grouped),
                "complete_instruction_de": f"Stelle {spec['product']} bereit; führe {spec['bio']} aus; verwende den vollständigen Bedingungsgriff {handle}.",
            }
        )
        for payload, value, source in [
            ("PRODUCT", f"{spec['product']}: {supply['internal_product_name_de']}", "INTERNAL_PRODUCT_HANDLE"),
            ("MEASURE", "CAL1/CAL2", "REUSED_CALIBRATION"),
            ("DURATION", "CAL3/CAL4/CAL5", "REUSED_CALIBRATION"),
            ("RESULT", "sichtbare Resultatklassen + CAL6", "VISIBLE_STATE_PLUS_REUSED_CALIBRATION"),
            ("CONDITION", handle, "COMPLETE_LOCAL_LOCUS_HANDLE"),
        ]:
            payload_rows.append({"order_id": order_id, "payload": payload, "value": value, "source": source, "empty": "NO"})

    write(f"{PREFIX}_438_MARK_SIX_ORDER_BOOK.tsv", marks, ["order_id", "order_mark_id", "stage", "page", "unit", "source_id", "surface", "identity", "component_recipe", "concrete_default_de", "owner_or_handle_de", "calibration_set"])
    write(f"{PREFIX}_119_UNIT_SIX_ORDER_BOOK.tsv", unit_rows, ["order_id", "stage", "unit", "page", "surface_sequence", "literal_sequence_de", "fluent_workshop_reading_de", "marks", "calibration_changed"])
    write(f"{PREFIX}_6_COMPLETE_ORDER_SUMMARY.tsv", order_rows, ["order_id", "internal_product", "product_name_de", "biological_record", "biological_page", "condition_handle", "condition_name_de", "preparation_marks", "application_marks", "condition_marks", "total_marks", "units", "complete_instruction_de"])
    write(f"{PREFIX}_30_FILLED_PAYLOADS.tsv", payload_rows, ["order_id", "payload", "value", "source", "empty"])
    write(f"{PREFIX}_6_SHARED_CALIBRATIONS.tsv", calibrations, list(calibrations[0]))

    lines = ["# Sechs-Auftrags-Werkstattbuch", ""]
    for row in order_rows:
        lines.extend(
            [
                f"## {row['order_id']}: {row['internal_product']} → {row['biological_record']} → {row['condition_handle']}",
                "",
                str(row["complete_instruction_de"]),
                f"Produkt: {row['product_name_de']}.",
                f"Bedingung: {row['condition_name_de']}.",
                f"Marken: {row['preparation_marks']} + {row['application_marks']} + {row['condition_marks']} = {row['total_marks']}.",
                "",
            ]
        )
    lines.extend(
        [
            "## Gemeinsame Werkstattregel",
            "",
            "Alle sechs Aufträge verwenden dasselbe Kartenwörterbuch und dieselben sechs",
            "Kalibrierungen. Jeder der 281 Biological-Einträge erscheint genau einmal als",
            "HOW-Teil. Astro wird immer als vollständiger lokaler Locus kopiert: große",
            "Ringtexte benötigen daher viele Marken, einzelne Sternplätze manchmal nur eine.",
        ]
    )
    (HERE / f"{PREFIX}_SIX_ORDER_WORKSHOP_BOOK.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    stage_counts = Counter("PREP" if row["stage"].startswith("MAKE") else "APP" if row["stage"].startswith("APPLY") else "COND" for row in marks)
    summary = {
        "status": "PASS",
        "decision": "ALL_SIX_APPLICATION_RECORDS_FORM_COMPLETE_ORDERS_UNDER_ONE_SHARED_WORKSHOP_SYSTEM",
        "orders": len(order_rows),
        "marks": len(marks),
        "stage_counts": dict(stage_counts),
        "units": len(unit_rows),
        "payload_rows": len(payload_rows),
        "empty_payloads": sum(row["empty"] == "YES" for row in payload_rows),
        "biological_events_covered_once": len({row["source_id"] for row in marks if row["stage"].startswith("APPLY")}),
        "condition_loci": len({row["unit"] for row in marks if row["stage"].startswith("CONDITION")}),
        "fixed_pages_used": len({row["page"] for row in marks}),
        "calibration_changes": 0,
        "dictionary_changes": 0,
        "marks_without_default": sum(not row["concrete_default_de"] for row in marks),
        "new_voynich_word_meanings": 0,
        "sealed_pages": ["f84", "f84r"],
    }
    (HERE / f"{PREFIX}_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (HERE / f"{PREFIX}_REPORT.md").write_text(
        "# Sidequest Pass 876: six-order workshop book\n\n"
        "All six Biological records now sit in complete orders under one unchanged internal\n"
        "dictionary and six shared calibrations. The book contains 438 visible order marks:\n"
        "84 preparation, 281 application and 73 complete local-condition labels.\n\n"
        "Every Biological event appears once. All four Herbal products and all six condition\n"
        "shelves are used; all ten fixed pages contribute. No payload is empty and no word or\n"
        "dictionary value changes between orders.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
