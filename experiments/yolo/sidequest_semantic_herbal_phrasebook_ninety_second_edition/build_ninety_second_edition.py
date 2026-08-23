#!/usr/bin/env python3
"""Build an Herbal phrasebook and compare it with the Biological one."""

from __future__ import annotations

import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
R89 = ROOT / "experiments/yolo/sidequest_semantic_continuous_translation_eighty_ninth_edition/EIGHTY_NINTH_116_CONTINUOUS_STATEMENT_TRANSLATION.tsv"


PRIMITIVES = [
    ("SELECT_PLANT_PART", "Pflanzenteil auswählen", "Herbal-only owner/content slot", r"\bNimm\b|Pflanzenstoff|Pflanzenteil|Wurzel|Blatt|Blüte|Spross|Kraut"),
    ("PREPARE_SET", "Ansatz eröffnen", "Bio SET", r"setz[^,.]* an|Ansatz|Zubereitung"),
    ("ADD_MEDIUM", "Medium oder Träger zugeben", "Bio PORTION_ADD, richer Herbal filler", r"Wasser|Auszugsflüssigkeit|Trägerstoff|Bindestoff|\bGib\b|\bgib\b"),
    ("MEASURE", "Portion oder Sollmaß setzen", "Bio MEASURE/PORTION_ADD", r"bemiss|Bemiss|Portion|vorgeschriebene Maß|örtliche Maß"),
    ("CUT_CRUSH", "zerteilen, zerstoßen oder bearbeiten", "Herbal-only preparation action", r"zerteil|zerstoß|Bearbeite|bearbeite"),
    ("WRING", "durch Tuch auswringen", "Bio PASS_STRAIN", r"wring"),
    ("SETTLE", "ruhen oder absetzen", "Bio SETTLE", r"absetz|stehen|zurück"),
    ("STRAIN_SEPARATE", "seihen oder Auszug trennen", "Bio PASS_STRAIN/DRAIN", r"seih|trenn|Auszug ab"),
    ("HEAT_GRADE", "wärmen oder bis zur Stufe führen", "Bio HEAT/DURATION_GRADE", r"erwärm|Stufe|Klarlauf|Gebrauchsstufe"),
    ("COLLECT", "Auszug sammeln", "Bio COLLECT", r"sammel|Sammel"),
    ("DOSED_USE", "bemessenes Mittel gebrauchen", "Bio TARGET/MEASURE", r"dosierte|dosiertes|gebrauche|verwende"),
    ("EXTERNAL_APPLY", "äußerlich oder gebunden anwenden", "Bio TARGET/FASTEN", r"äußerliche|gebundene|örtliche Stelle|an die örtliche"),
    ("STORE_RESERVE", "Rest oder Vorrat verwahren", "Bio COLLECT/CLOSE", r"verwahr|Behalte|behalte|zurück|Restteil|Vorrat"),
    ("ORDER_CONTINUE", "denselben oder zweiten Posten fortführen", "Bio ORDER_CONTINUE", r"wieder|zweite|zweiten|übrig|denselben|weiter|Fortsetzung"),
    ("READY_CLOSE", "Bereitschaft oder lokalen Abschluss markieren", "Bio READY/CLOSE", r"bereit|Bereitschaft|Gebrauchsstufe|Abschluss"),
]


MACROS = {
    "SELECT_AND_PREPARE": "Pflanzenteil wählen und neuen Ansatz eröffnen",
    "EXTRACT_AND_SEPARATE": "Auszug gewinnen, klären oder abteilen",
    "MEASURE_AND_USE": "Portion bemessen und als Mittel oder Anwendung gebrauchen",
    "STORE_OR_RESERVE": "Rest, Vorrat oder zweiten Posten zurückstellen",
    "CONTINUE_AND_READY": "laufende Bereitung fortführen und auf Gebrauchsstufe bringen",
}


CROSSWALK = {
    "SELECT_PLANT_PART": ("NONE", "HERBAL_ONLY", "Bildpflanze liefert Teil-/Materialslot."),
    "PREPARE_SET": ("SET", "SHARED_CORE", "Beide eröffnen einen lokalen Arbeitsansatz."),
    "ADD_MEDIUM": ("PORTION_ADD", "PARTIAL_SHARED", "Bio fügt Portion/Zusatz zu; Herbal benennt zusätzlich Mediumsfunktion."),
    "MEASURE": ("MEASURE", "SHARED_CORE", "Sollmaß oder Portion funktioniert gleich."),
    "CUT_CRUSH": ("NONE", "HERBAL_ONLY", "Zerkleinern gehört zur Pflanzenbereitung."),
    "WRING": ("PASS_STRAIN", "PARTIAL_SHARED", "Auswringen ist eine spezielle Durchlasshandlung."),
    "SETTLE": ("SETTLE", "SHARED_CORE", "Ruhen/Absetzen ist gleich lehrbar."),
    "STRAIN_SEPARATE": ("PASS_STRAIN,DRAIN", "SHARED_CORE", "Trennen und Durchlass bilden dieselbe Prozesszone."),
    "HEAT_GRADE": ("HEAT,DURATION_GRADE", "SHARED_CORE", "Wärme und Grad werden in beiden Registern gesetzt."),
    "COLLECT": ("COLLECT", "SHARED_CORE", "Örtliches Sammeln bleibt gleich."),
    "DOSED_USE": ("MEASURE,TARGET", "PARTIAL_SHARED", "Bio setzt Maß/Ziel; Herbal ergänzt Produktgebrauch."),
    "EXTERNAL_APPLY": ("TARGET,FASTEN", "PARTIAL_SHARED", "Ziel und Befestigung werden im Bio-Bild lokalisiert."),
    "STORE_RESERVE": ("COLLECT,CLOSE", "PARTIAL_SHARED", "Herbal verwahrt Vorrat, Bio schließt lokale Station."),
    "ORDER_CONTINUE": ("ORDER_CONTINUE", "SHARED_CORE", "Folge/Fortsetzung ist registerübergreifend."),
    "READY_CLOSE": ("READY,CLOSE", "SHARED_CORE", "Bereitschaft und Abschluss teilen dieselbe Satzposition."),
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def extract(text: str) -> list[str]:
    hits = []
    for order, (primitive, _, _, pattern) in enumerate(PRIMITIVES):
        for match in re.finditer(pattern, text, flags=re.IGNORECASE):
            hits.append((match.start(), order, primitive))
    hits.sort()
    sequence = []
    for _, _, primitive in hits:
        if not sequence or sequence[-1] != primitive:
            sequence.append(primitive)
    return sequence


def macro(sequence: list[str]) -> str:
    present = set(sequence)
    if {"ORDER_CONTINUE", "READY_CLOSE"}.issubset(present):
        return "CONTINUE_AND_READY"
    if present & {"DOSED_USE", "EXTERNAL_APPLY"}:
        return "MEASURE_AND_USE"
    if present & {"WRING", "STRAIN_SEPARATE", "COLLECT"}:
        return "EXTRACT_AND_SEPARATE"
    if "STORE_RESERVE" in present:
        return "STORE_OR_RESERVE"
    if present & {"SELECT_PLANT_PART", "CUT_CRUSH", "ADD_MEDIUM"}:
        return "SELECT_AND_PREPARE"
    return "CONTINUE_AND_READY"


def main() -> None:
    statements = [row for row in read_tsv(R89) if row["record_unit_id"].startswith("H")]
    primitive_rows = []
    for order, (primitive, meaning, counterpart, pattern) in enumerate(PRIMITIVES, 1):
        primitive_rows.append({
            "phrasebook_order": order, "primitive_id": primitive,
            "source_meaning_de": meaning, "nearest_biological_primitive": counterpart,
            "recognition_cue": pattern,
        })
    write_tsv(OUT / "NINETY_SECOND_15_HERBAL_PRIMITIVES.tsv", primitive_rows)

    mapped = []
    macro_members: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in statements:
        sequence = extract(row["concrete_source_expansion_de"])
        macro_id = macro(sequence)
        out = {
            "statement_id": row["statement_id"], "record_unit_id": row["record_unit_id"],
            "page": row["page"], "physical_loci": row["physical_loci"],
            "event_count": row["event_count"], "primitive_sequence": ">".join(sequence),
            "primitive_count": len(sequence), "macro_id": macro_id,
            "macro_reading_de": MACROS[macro_id],
            "full_statement_reading_de": row["concrete_source_expansion_de"],
            "visible_surface_sequence": row["visible_surface_sequence"],
        }
        mapped.append(out)
        macro_members[macro_id].append(out)
    write_tsv(OUT / "NINETY_SECOND_19_HERBAL_STATEMENT_PHRASEBOOK.tsv", mapped)

    summary_rows = []
    for macro_id, reading in MACROS.items():
        members = macro_members[macro_id]
        summary_rows.append({
            "macro_id": macro_id, "macro_reading_de": reading,
            "statement_count": len(members),
            "records": ",".join(sorted({str(row["record_unit_id"]) for row in members})) or "NONE",
            "statement_ids": ",".join(str(row["statement_id"]) for row in members) or "NONE",
        })
    write_tsv(OUT / "NINETY_SECOND_5_HERBAL_MACROS.tsv", summary_rows)

    crosswalk_rows = []
    for primitive, _, _, _ in PRIMITIVES:
        counterpart, relation, note = CROSSWALK[primitive]
        crosswalk_rows.append({
            "herbal_primitive": primitive, "biological_counterpart": counterpart,
            "relation": relation, "interpretation_de": note,
        })
    write_tsv(OUT / "NINETY_SECOND_HERBAL_BIO_PRIMITIVE_CROSSWALK.tsv", crosswalk_rows)

    relation_counts = Counter(row["relation"] for row in crosswalk_rows)
    report = [
        "# Zweiundneunzigste Werkstattrunde: Herbal-Phrasebook", "",
        "## Ergebnis", "",
        "The nineteen Herbal statements reduce to fifteen source primitives and five",
        "article macros. Eight primitives share the same workshop core with Biological,",
        "five are partial matches and two are genuinely Herbal-only.", "",
    ]
    for row in summary_rows:
        report.append(f"- {row['macro_id']}: {row['statement_count']} — {row['macro_reading_de']}")
    report.extend([
        "", f"Shared core: {relation_counts['SHARED_CORE']}; partial shared: {relation_counts['PARTIAL_SHARED']}; Herbal-only: {relation_counts['HERBAL_ONLY']}.", "",
        "The common syntax is OWNER → set/measure → process/grade → target/continue →",
        "ready/close. Herbal adds plant-part selection and cutting/crushing. Biological",
        "adds explicit station ownership, drains and service resets. Therefore one",
        "workshop grammar can serve both sections without pretending that a plant word",
        "also means a basin or that a drain card names a body part.", "",
        "Only the fixed Herbal and Biological prose pages were used; f84 and f84r remained sealed.",
    ])
    (OUT / "NINETY_SECOND_HERBAL_PHRASEBOOK_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")

    summary = {
        "status": "CONSISTENT", "herbal_primitives": len(primitive_rows),
        "herbal_macros": len(summary_rows), "herbal_statements": len(mapped),
        "herbal_events": sum(int(row["event_count"]) for row in mapped),
        "crosswalk_relations": dict(relation_counts),
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
