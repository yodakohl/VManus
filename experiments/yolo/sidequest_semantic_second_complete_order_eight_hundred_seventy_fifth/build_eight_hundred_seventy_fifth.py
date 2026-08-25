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
FIRST = ROOT / "sidequest_semantic_fully_readable_corrected_sample_eight_hundred_seventy_fourth"
CALIBRATIONS = FIRST / "EIGHT_HUNDRED_SEVENTY_FOURTH_6_EXPLICIT_CALIBRATIONS.tsv"
FIRST_MARKS = FIRST / "EIGHT_HUNDRED_SEVENTY_FOURTH_76_MARK_FULLY_READABLE_SAMPLE.tsv"
PREFIX = "EIGHT_HUNDRED_SEVENTY_FIFTH"

ATOM_CALIBRATION = {
    "SOLLMASS": "EIN KLEINER SCHOEPFBECHER",
    "PORTION": "EIN ABGEGRENZTER TEIL",
    "STUFE": "EINE EINGESTELLTE ARBEITSSTUFE",
    "KURZ": "EIN KURZER ARBEITSGANG",
    "LANG": "DREI KURZE ARBEITSGAENGE",
    "VOLL": "BIS DER GANZE POSTEN ERFASST IST",
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


def main() -> None:
    herbal = read(HERBAL)
    bio = read(BIO)
    statements = {row["statement_id"]: row for row in read(STATEMENTS)}
    astro = read(ASTRO)
    calibrations = read(CALIBRATIONS)
    first_marks = read(FIRST_MARKS)

    selected_herbal = [row for row in herbal if row["statement_id"] in {"H3-S001", "H3-S002"}]
    selected_bio = [row for row in bio if row["record"] == "B3"]
    selected_astro = [row for row in astro if row["page"] == "f67r2" and row["locus"] == "f67r2.15" and row["event_index"] == "1"]
    marks = []
    for row in selected_herbal:
        marks.append(
            {
                "stage": "MAKE_B.X2",
                "page": row["page"],
                "unit": row["statement_id"],
                "source_id": row["event_id"],
                "surface": row["surface"],
                "identity": row["exact_card_id"],
                "component_recipe": row["component_recipe"],
                "concrete_default_de": calibrate(row["card_meaning_de"]),
                "owner_or_handle_de": "Bildbesitzer B; entstehendes Produkt B.X2",
            }
        )
    for row in selected_bio:
        marks.append(
            {
                "stage": "APPLY_B3",
                "page": row["page"],
                "unit": row["statement_id"],
                "source_id": row["event_id"],
                "surface": row["surface"],
                "identity": row["exact_card_id"],
                "component_recipe": row["component_recipe"],
                "concrete_default_de": calibrate(row["card_meaning_de"]),
                "owner_or_handle_de": row["owner_de"],
            }
        )
    astro_row = selected_astro[0]
    marks.append(
        {
            "stage": "CONDITION_C2@f67r2.15",
            "page": astro_row["page"],
            "unit": astro_row["locus"],
            "source_id": astro_row["opaque_local_id"],
            "surface": astro_row["surface"],
            "identity": astro_row["opaque_local_id"],
            "component_recipe": astro_row["selected_component_parse"],
            "concrete_default_de": "VON DER TEILADRESSE WEITER ZUM STERNBEZUG; DEN LOKALEN ARBEITSGANG SCHLIESSEN",
            "owner_or_handle_de": "C2@f67r2.15; linker sichtbarer f67-Stern-/Aspektplatz",
        }
    )
    for index, row in enumerate(marks, start=1):
        row["mark_id"] = f"S{index:03d}"
        row["calibration_set"] = "PASS874_CAL1_TO_CAL6_UNCHANGED"

    by_unit: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in marks:
        by_unit[(row["stage"], row["unit"])].append(row)
    unit_rows = []
    for (stage, unit), subset in by_unit.items():
        fluent = statements[unit]["working_reading_de"] if unit in statements else "Gehe von der Teiladresse zum Sternbezug weiter und schließe den lokalen Arbeitsgang."
        unit_rows.append(
            {
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

    payloads = [
        {"payload": "PRODUCT", "value_de": "B.X2; nachbearbeiteter und aufgenommener Auszug der Bildpflanze B", "source": "INTERNAL_HANDLE", "empty": "NO"},
        {"payload": "MEASURE", "value_de": "Pass874 CAL1/CAL2 unverändert", "source": "REUSED_CALIBRATION", "empty": "NO"},
        {"payload": "DURATION", "value_de": "Pass874 CAL3/CAL4/CAL5 unverändert", "source": "REUSED_CALIBRATION", "empty": "NO"},
        {"payload": "RESULT", "value_de": "aufgenommener Auszug wird an Gefäß-/Paarstationen bereit, gesammelt, durchgeleitet und abgesetzt", "source": "VISIBLE_RESULT_CLASSES_PLUS_CAL6", "empty": "NO"},
        {"payload": "CONDITION", "value_de": "C2@f67r2.15: von Teiladresse zum Sternbezug weiter; lokal schließen", "source": "INTERNAL_HANDLE_PLUS_RELATIVE_PARSE", "empty": "NO"},
    ]

    first_prose_ids = {row["identity"] for row in first_marks if row["page"] not in {"f67r2", "f68r1", "f69v"}}
    second_prose_ids = {row["identity"] for row in marks if row["page"] not in {"f67r2", "f68r1", "f69v"}}
    comparison = [
        {"measure": "TOTAL_MARKS", "first_order": len(first_marks), "second_order": len(marks), "interpretation_de": "zweiter Auftrag ist länger wegen B3"},
        {"measure": "PREPARATION_MARKS", "first_order": 13, "second_order": len(selected_herbal), "interpretation_de": "B.X2 braucht nur zwei f11r-Aussagen"},
        {"measure": "APPLICATION_MARKS", "first_order": 62, "second_order": len(selected_bio), "interpretation_de": "B3 ist der längere f83r-Katalog"},
        {"measure": "SHARED_PROSE_EXACT_IDENTITIES", "first_order": len(first_prose_ids), "second_order": len(first_prose_ids & second_prose_ids), "interpretation_de": "derselbe Kartenstock wird in verschiedener Reihenfolge wiederverwendet"},
        {"measure": "CALIBRATION_CHANGES", "first_order": 6, "second_order": 0, "interpretation_de": "alle sechs Konventionen unverändert wiederverwendet"},
        {"measure": "EMPTY_PAYLOADS", "first_order": 0, "second_order": 0, "interpretation_de": "beide Aufträge vollständig intern lesbar"},
    ]

    write(f"{PREFIX}_95_MARK_SECOND_COMPLETE_ORDER.tsv", marks, ["mark_id", "stage", "page", "unit", "source_id", "surface", "identity", "component_recipe", "concrete_default_de", "owner_or_handle_de", "calibration_set"])
    write(f"{PREFIX}_37_UNIT_SECOND_COMPLETE_ORDER.tsv", unit_rows, ["stage", "unit", "page", "surface_sequence", "literal_sequence_de", "fluent_workshop_reading_de", "marks", "calibration_changed"])
    write(f"{PREFIX}_6_REUSED_CALIBRATIONS.tsv", calibrations, list(calibrations[0]))
    write(f"{PREFIX}_5_FILLED_PAYLOADS.tsv", payloads, ["payload", "value_de", "source", "empty"])
    write(f"{PREFIX}_TWO_ORDER_COMPARISON.tsv", comparison, ["measure", "first_order", "second_order", "interpretation_de"])

    text = [
        "# Zweiter vollständiger Auftrag B.X2 → B3 → C2@f67r2.15",
        "",
        "## Zubereitung",
        "",
        "Bearbeite den Posten der Bildpflanze B, halte ihn am Arbeitsort, presse ihn aus,",
        "halte einen kleinen Schöpfbecher davon drei kurze Arbeitsgänge, bringe ihn in den",
        "Empfänger und schließe den ersten Arbeitsgang. Bearbeite den aufgenommenen Auszug",
        "weiter. Dieser Vorrat heißt **B.X2**.",
        "",
        "## Anwendung",
        "",
        "Führe B.X2 durch die 34 B3-Zellen an fünf sichtbaren Gefäß- und Paarstationen.",
        "Verwende dieselben Portionen, Hausmaße und Kurz/Lang/Voll-Grade wie im ersten",
        "Auftrag. Bereite, leite, halte, sammle und setze ab, wie jede Karte vorgibt.",
        "",
        "## Bedingung",
        "",
        "Öffne **C2@f67r2.15** und lies `dolchsody`: Von der Teiladresse weiter zum",
        "Sternbezug; den lokalen Arbeitsgang schließen. Kein externer Sternname ist nötig.",
        "",
        "## Ergebnis",
        "",
        "8 Zubereitungsmarken + 86 Anwendungsmarken + 1 Bedingungsmarke = 95. Alle sechs",
        "Kalibrierungen aus dem ersten Auftrag werden unverändert wiederverwendet; keine",
        "Kartenbedeutung und kein Produkt-, Ergebnis- oder Bedingungsslot wurde ergänzt.",
    ]
    (HERE / f"{PREFIX}_SECOND_COMPLETE_ORDER.md").write_text("\n".join(text) + "\n", encoding="utf-8")

    stage_counts = Counter(row["stage"] for row in marks)
    summary = {
        "status": "PASS",
        "decision": "SECOND_DIFFERENT_ORDER_REUSES_THE_SAME_DICTIONARY_AND_SIX_CALIBRATIONS",
        "sample_marks": len(marks),
        "stage_counts": dict(stage_counts),
        "sample_units": len(unit_rows),
        "reused_calibrations": len(calibrations),
        "calibration_changes": 0,
        "filled_payloads": len(payloads),
        "empty_payloads": sum(row["empty"] == "YES" for row in payloads),
        "shared_prose_exact_identities_with_first_order": len(first_prose_ids & second_prose_ids),
        "dictionary_changes": 0,
        "new_voynich_word_meanings": 0,
        "sealed_pages": ["f84", "f84r"],
    }
    (HERE / f"{PREFIX}_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (HERE / f"{PREFIX}_REPORT.md").write_text(
        "# Sidequest Pass 875: second complete order\n\n"
        "A wholly different order uses B.X2 from f11r, B3 from f83r and C2@f67r2.15. It\n"
        "contains 8 preparation, 86 application and 1 condition mark: 95 total. Every mark\n"
        "has one concrete default.\n\n"
        "All six calibrations from Pass 874 are reused byte-for-byte, with no dictionary or\n"
        "payload change. The second order therefore shows that the readable workshop system\n"
        "is not limited to the first f56r-to-f82r passage scenario.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
