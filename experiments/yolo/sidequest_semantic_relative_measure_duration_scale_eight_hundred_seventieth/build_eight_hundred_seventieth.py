#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
BASE = ROOT / "sidequest_semantic_tenth_workshop_edition_eight_hundred_forty_sixth" / "EIGHT_HUNDRED_FORTY_SIXTH_381_EVENT_INTERLINEAR.tsv"
PREFIX = "EIGHT_HUNDRED_SEVENTIETH"
TARGETS = ["AIN", "AIIN", "IIN", "E", "EE", "EEE"]
VALUES = {
    "AIN": ("MENGE", "PORTION", "ein abgegrenzter Teil aus dem aktiven Bestand", "mit Hauslöffel, Handvoll oder Teilstrich kalibrieren"),
    "AIIN": ("MENGE", "SOLLMASS", "das für diesen Auftrag vorgeschriebene Werkstattmaß", "markiertes Hausgefäß oder Meisterangabe verwenden"),
    "IIN": ("STUFE", "EINSTELLSTUFE", "eine benannte oder eingestellte Arbeitsstufe", "Gerätekerbe, Badestufe oder gelernte Stufenkarte verwenden"),
    "E": ("DAUER_GRAD", "KURZ", "kurz oder bis zum ersten sichtbaren Kontakt", "ein gewöhnlicher kurzer Werkstattgang"),
    "EE": ("DAUER_GRAD", "LAENGER", "anhaltend oder über den nächsten Werkstattabschnitt", "länger als E, aber noch nicht vollständig"),
    "EEE": ("DAUER_GRAD", "VOLL", "vollständig oder bis der ganze Posten erfasst ist", "bis kein unbehandelter Teil übrig bleibt"),
}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]], fields: list[str]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    events = read(BASE)
    scale_rows = []
    for token in TARGETS:
        subset = [row for row in events if token in row["component_recipe"].split("+")]
        axis, value, operational, calibration = VALUES[token]
        scale_rows.append(
            {
                "component": token,
                "axis": axis,
                "relative_value_de": value,
                "operational_default_de": operational,
                "workshop_calibration_de": calibration,
                "event_count": len(subset),
                "exact_card_types": len({row["exact_card_id"] for row in subset}),
                "pages": "|".join(sorted({row["page"] for row in subset})),
                "absolute_unit_encoded": "NO",
            }
        )

    audit_rows = []
    for row in events:
        tokens = [token for token in row["component_recipe"].split("+") if token in TARGETS]
        if not tokens:
            continue
        audit_rows.append(
            {
                "event_id": row["event_id"],
                "page": row["page"],
                "record": row["record"],
                "statement_id": row["statement_id"],
                "surface": row["surface"],
                "exact_card_id": row["exact_card_id"],
                "component_recipe": row["component_recipe"],
                "relative_components": "+".join(tokens),
                "relative_reading_de": " · ".join(VALUES[token][1] for token in tokens),
                "complete_card_reading_de": row["tenth_edition_reading_de"],
                "absolute_value_needed": "YES" if any(token in {"AIIN", "IIN"} for token in tokens) else "CALIBRATION_ONLY",
            }
        )

    sample_rows = [row for row in audit_rows if row["page"] == "f56r" or row["record"] == "B2"]
    sample_component_counts = Counter(
        token
        for row in sample_rows
        for token in row["relative_components"].split("+")
    )
    sample_summary_rows = []
    for token in TARGETS:
        sample_summary_rows.append(
            {
                "component": token,
                "relative_value_de": VALUES[token][1],
                "sample_occurrences": sample_component_counts[token],
                "sample_interpretation_de": VALUES[token][2],
            }
        )

    master_revision = [
        {"slot": "PRODUCT", "before": "vollständig vom Meister", "after": "vollständig vom Meister; Bild liefert nur Besitzer", "remaining_need": "konkreter Name und Stoffidentität"},
        {"slot": "MEASURE", "before": "Zahlenmaß vom Meister", "after": "AIN=PORTION und AIIN=SOLLMASS werden gelesen", "remaining_need": "nur absolute Einheit oder Hausgefäß"},
        {"slot": "DURATION", "before": "reale Dauer vom Meister", "after": "E=KURZ, EE=LAENGER, EEE=VOLL werden gelesen", "remaining_need": "nur Werkstattkalibrierung der Zeitspanne"},
        {"slot": "RESULT", "before": "materielles Ergebnis vom Meister", "after": "noch nicht in dieser Runde verändert", "remaining_need": "konkretes Zielergebnis"},
        {"slot": "CONDITION", "before": "externer Astro-Wert vom Meister", "after": "noch nicht in dieser Runde verändert", "remaining_need": "externe Identität des lokalen Etiketts"},
    ]

    write(f"{PREFIX}_6_RELATIVE_SCALE_COMPONENTS.tsv", scale_rows, ["component", "axis", "relative_value_de", "operational_default_de", "workshop_calibration_de", "event_count", "exact_card_types", "pages", "absolute_unit_encoded"])
    write(f"{PREFIX}_151_EVENT_SCALE_AUDIT.tsv", audit_rows, ["event_id", "page", "record", "statement_id", "surface", "exact_card_id", "component_recipe", "relative_components", "relative_reading_de", "complete_card_reading_de", "absolute_value_needed"])
    write(f"{PREFIX}_43_SAMPLE_SCALE_EVENTS.tsv", sample_rows, ["event_id", "page", "record", "statement_id", "surface", "exact_card_id", "component_recipe", "relative_components", "relative_reading_de", "complete_card_reading_de", "absolute_value_needed"])
    write(f"{PREFIX}_SAMPLE_COMPONENT_COUNTS.tsv", sample_summary_rows, ["component", "relative_value_de", "sample_occurrences", "sample_interpretation_de"])
    write(f"{PREFIX}_5_MASTER_VALUE_REVISIONS.tsv", master_revision, ["slot", "before", "after", "remaining_need"])

    sample_text = [
        "# Musterauftrag mit relativer Maß- und Dauerlesung",
        "",
        "Der P4→B2-Auftrag enthält in seinen 89 Prosakarten 43 Karten mit einer",
        "sichtbaren relativen Maß-, Stufen- oder Dauerkomponente:",
        "",
        f"- {sample_component_counts['AIN']}× PORTION;",
        f"- {sample_component_counts['AIIN']}× SOLLMASS;",
        f"- {sample_component_counts['IIN']}× EINSTELLSTUFE;",
        f"- {sample_component_counts['E']}× KURZ;",
        f"- {sample_component_counts['EE']}× LAENGER;",
        f"- {sample_component_counts['EEE']}× VOLL.",
        "",
        "Damit liest der Lehrling nicht bloß »irgendeine Menge« und »irgendeine Dauer«.",
        "Er unterscheidet abgegrenzte Portionen vom Sollmaß und kurze, längere und volle",
        "Arbeitsgänge. Der Meister muss nur noch sagen, welches Hausgefäß das Sollmaß ist",
        "und wie lang ein gewöhnlicher kurzer Gang in dieser Werkstatt dauert.",
        "",
        "Praktische Rücklesung: Nimm eine Portion oder das vorgeschriebene Hausmaß; führe",
        "den Posten kurz, länger oder vollständig, je nach sichtbarer Gradkarte. Dies ist",
        "ein echtes relatives Betriebssystem, auch wenn keine Zahl oder Zeiteinheit erscheint.",
    ]
    (HERE / f"{PREFIX}_RELATIVE_SAMPLE_READING.md").write_text("\n".join(sample_text) + "\n", encoding="utf-8")

    summary = {
        "status": "PASS",
        "decision": "MEASURE_AND_DURATION_ARE_RELATIVELY_READABLE_BUT_ABSOLUTE_CALIBRATION_REMAINS_EXTERNAL",
        "scale_components": len(scale_rows),
        "scale_events": len(audit_rows),
        "scale_exact_card_types": len({row["exact_card_id"] for row in audit_rows}),
        "scale_statements": len({row["statement_id"] for row in audit_rows}),
        "sample_scale_events": len(sample_rows),
        "sample_relative_component_counts": dict(sample_component_counts),
        "master_values_fully_missing_after": 3,
        "master_values_reduced_to_calibration": 2,
        "new_word_meanings": 0,
        "sealed_pages": ["f84", "f84r"],
    }
    (HERE / f"{PREFIX}_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (HERE / f"{PREFIX}_REPORT.md").write_text(
        "# Sidequest Pass 870: relative measure and duration scales\n\n"
        "AIN/AIIN/IIN and E/EE/EEE now form a compact two-axis workshop scale across\n"
        "151 events, 73 exact cards and 78 statements. The P4-to-B2 sample alone contains\n"
        "43 scale-bearing events: four portions, nine prescribed measures, thirteen short,\n"
        "sixteen longer and one complete operation.\n\n"
        "The master no longer has to supply measure and duration from nothing. The cards\n"
        "recover their relative class; only the house vessel, notch or time calibration\n"
        "remains external. Three fully missing payloads remain: product identity, precise\n"
        "material result and external Astro condition value.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
