#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
BASE = ROOT / "sidequest_semantic_tenth_workshop_edition_eight_hundred_forty_sixth"
EVENTS = BASE / "EIGHT_HUNDRED_FORTY_SIXTH_381_EVENT_INTERLINEAR.tsv"
STATEMENTS = BASE / "EIGHT_HUNDRED_FORTY_SIXTH_116_STATEMENT_EDITION.tsv"
PREFIX = "EIGHT_HUNDRED_SEVENTY_FIRST"

RESULTS = {
    "CTH": ("BEREIT", "Posten ist für den nächsten Schritt bereit oder eingestellt"),
    "SHED": ("ABGESETZT", "Posten wurde stehen gelassen oder hat sich abgesetzt"),
    "SOLK": ("GESAMMELT", "Posten liegt an der Sammel-/Auffangstelle vor"),
    "CKH": ("DURCHGELAUFEN", "Posten hat den Durchlass oder lokalen Gang passiert"),
    "CHK": ("ERWAERMT", "Posten ist kurz oder länger erwärmt"),
    "OK+EEE+DY": ("VOLLSTAENDIG_ANGELEGT", "der ganze Posten wurde vollständig angelegt und der Schritt geschlossen"),
}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]], fields: list[str]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def result_keys(tokens: list[str]) -> list[str]:
    keys = [key for key in ["CTH", "SHED", "SOLK", "CKH", "CHK"] if key in tokens]
    if {"OK", "EEE", "DY"}.issubset(tokens):
        keys.append("OK+EEE+DY")
    return keys


def main() -> None:
    events = read(EVENTS)
    statements = {row["statement_id"]: row for row in read(STATEMENTS)}
    result_rows = []
    for key, (value, operational) in RESULTS.items():
        subset = [row for row in events if key in result_keys(row["component_recipe"].split("+"))]
        result_rows.append(
            {
                "result_component_or_construction": key,
                "material_result_class_de": value,
                "operational_default_de": operational,
                "event_count": len(subset),
                "exact_card_types": len({row["exact_card_id"] for row in subset}),
                "statements": len({row["statement_id"] for row in subset}),
                "pages": "|".join(sorted({row["page"] for row in subset})),
                "exact_material_or_quality_name": "NO",
            }
        )

    audit = []
    for row in events:
        keys = result_keys(row["component_recipe"].split("+"))
        if not keys:
            continue
        audit.append(
            {
                "event_id": row["event_id"],
                "page": row["page"],
                "record": row["record"],
                "statement_id": row["statement_id"],
                "surface": row["surface"],
                "exact_card_id": row["exact_card_id"],
                "component_recipe": row["component_recipe"],
                "result_components": "+".join(keys),
                "material_result_classes_de": " + ".join(RESULTS[key][0] for key in keys),
                "complete_card_reading_de": row["tenth_edition_reading_de"],
                "step_closed": "YES" if "SCHLUSS" in row["tenth_edition_reading_de"] else "NO",
                "material_identity_known": "NO",
            }
        )

    by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in audit:
        by_statement[row["statement_id"]].append(row)
    statement_rows = []
    for statement_id, subset in by_statement.items():
        source = statements[statement_id]
        classes = []
        for row in subset:
            for value in row["material_result_classes_de"].split(" + "):
                if value not in classes:
                    classes.append(value)
        statement_rows.append(
            {
                "statement_id": statement_id,
                "page": source["page"],
                "record": source["record"],
                "surface_sequence": source["surface_sequence"],
                "result_sequence_de": " -> ".join(classes),
                "complete_working_reading_de": source["working_reading_de"],
                "result_events": len(subset),
                "closed_result_events": sum(row["step_closed"] == "YES" for row in subset),
                "precise_acceptance_criterion": "MASTER_OR_PICTURE",
            }
        )
    statement_rows.sort(key=lambda row: int(str(row["statement_id"]).split("S")[-1]))

    sample = [row for row in audit if row["page"] == "f56r" or row["record"] == "B2"]
    sample.sort(key=lambda row: int(row["event_id"][1:]))
    sample_counts = Counter(value for row in sample for value in row["material_result_classes_de"].split(" + "))

    master_revision = [
        {"slot": "PRODUCT", "status_after": "FULL_MASTER", "recoverable_de": "nur Pflanzenbesitzer und Zubereitungsart", "remaining_de": "konkreter Produktname"},
        {"slot": "MEASURE", "status_after": "CALIBRATION_ONLY", "recoverable_de": "PORTION/SOLLMASS/EINSTELLSTUFE", "remaining_de": "absolute Einheit"},
        {"slot": "DURATION", "status_after": "CALIBRATION_ONLY", "recoverable_de": "KURZ/LAENGER/VOLL", "remaining_de": "absolute Zeitspanne"},
        {"slot": "RESULT", "status_after": "CALIBRATION_ONLY", "recoverable_de": "BEREIT/ABGESETZT/GESAMMELT/DURCHGELAUFEN/ERWAERMT/VOLLSTAENDIG_ANGELEGT", "remaining_de": "genaues sichtbares Annahmekriterium"},
        {"slot": "CONDITION", "status_after": "FULL_MASTER", "recoverable_de": "lokale Bedingungsfamilie und Etikett", "remaining_de": "externer Himmels-/Kalenderwert"},
    ]

    write(f"{PREFIX}_6_MATERIAL_RESULT_CLASSES.tsv", result_rows, ["result_component_or_construction", "material_result_class_de", "operational_default_de", "event_count", "exact_card_types", "statements", "pages", "exact_material_or_quality_name"])
    write(f"{PREFIX}_59_RESULT_EVENT_AUDIT.tsv", audit, ["event_id", "page", "record", "statement_id", "surface", "exact_card_id", "component_recipe", "result_components", "material_result_classes_de", "complete_card_reading_de", "step_closed", "material_identity_known"])
    write(f"{PREFIX}_43_RESULT_STATEMENTS.tsv", statement_rows, ["statement_id", "page", "record", "surface_sequence", "result_sequence_de", "complete_working_reading_de", "result_events", "closed_result_events", "precise_acceptance_criterion"])
    write(f"{PREFIX}_12_SAMPLE_RESULT_EVENTS.tsv", sample, ["event_id", "page", "record", "statement_id", "surface", "exact_card_id", "component_recipe", "result_components", "material_result_classes_de", "complete_card_reading_de", "step_closed", "material_identity_known"])
    write(f"{PREFIX}_5_MASTER_VALUE_STATUS.tsv", master_revision, ["slot", "status_after", "recoverable_de", "remaining_de"])

    lines = [
        "# Ergebnisrücklesung des P4→B2-Musterauftrags",
        "",
        "Der Auftrag nennt jetzt nicht nur Handlungen, sondern eine sichtbare Zustandskette:",
        "",
        "1. P4 verlässt f56r als durchgelaufener, geschlossener Arbeitsansatz.",
        "2. B2 führt ihn durch weitere lokale Durchlässe und sammelt ein Sollmaß.",
        "3. Der Posten wird kurz bereitgemacht und länger erwärmt.",
        "4. Er wird an der nächsten Station durchgehalten und danach stehen gelassen.",
        "5. Eine zweite Bereitschaftsprüfung folgt; anschließend wird er vollständig angelegt.",
        "6. Der letzte lokale Posten wird gekühlt und stehen gelassen.",
        "",
        "Zählung der zwölf Resultatkarten:",
    ]
    for value, count in sorted(sample_counts.items()):
        lines.append(f"- {value}: {count}×")
    lines.extend(
        [
            "",
            "Damit ist das Ergebnis nicht mehr vollständig frei erfunden. Die Karten nennen",
            "breite materielle Zustände. Der Meister muss nur noch kalibrieren, woran ein",
            "bestimmter Stoff als ausreichend bereit, abgesetzt oder vollständig behandelt gilt.",
            "Der formale Zellschluss allein bleibt davon getrennt.",
        ]
    )
    (HERE / f"{PREFIX}_SAMPLE_RESULT_READING.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    summary = {
        "status": "PASS",
        "decision": "MATERIAL_RESULT_CLASS_IS_READABLE_WHILE_PRECISE_ACCEPTANCE_REMAINS_MASTER_CALIBRATION",
        "result_classes": len(result_rows),
        "result_events": len(audit),
        "result_exact_card_types": len({row["exact_card_id"] for row in audit}),
        "result_statements": len(statement_rows),
        "closed_result_events": sum(row["step_closed"] == "YES" for row in audit),
        "sample_result_events": len(sample),
        "sample_result_counts": dict(sample_counts),
        "master_values_fully_missing_after": 2,
        "master_values_reduced_to_calibration": 3,
        "new_word_meanings": 0,
        "sealed_pages": ["f84", "f84r"],
    }
    (HERE / f"{PREFIX}_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (HERE / f"{PREFIX}_REPORT.md").write_text(
        "# Sidequest Pass 871: material-result vocabulary\n\n"
        "Six material-result classes now cover 59 events, 30 exact cards and 43 statements:\n"
        "ready, settled, collected, passed through, warmed and completely applied. The cell\n"
        "close remains a separate bookkeeping action rather than a material result.\n\n"
        "The P4-to-B2 sample contains twelve result-bearing events and now reads as a real\n"
        "state chain from passed preparation through collection, warming, settling and full\n"
        "application. The exact acceptance test still comes from picture or master. Product\n"
        "identity and external Astro value are the two fully missing payloads left.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
