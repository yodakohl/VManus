#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
ATOMS = ROOT / "experiments/yolo/sidequest_semantic_integrated_fourteen_page_edition_nine_hundred_thirty_ninth/PASS939_56_CURRENT_ATOMIC_LEXICON.tsv"
FAMILIES = ROOT / "experiments/yolo/sidequest_semantic_long_formula_deck_nine_hundred_fifty_second/PASS952_79_LEARNED_CARD_FAMILIES.tsv"
VARIANTS = ROOT / "experiments/yolo/sidequest_semantic_long_formula_deck_nine_hundred_fifty_second/PASS952_155_SURFACE_VARIANTS.tsv"
EVENTS = ROOT / "experiments/yolo/sidequest_semantic_long_formula_deck_nine_hundred_fifty_second/PASS952_2511_LONG_FORMULA_EDITION.tsv"

LESSON_COMPONENTS = {
    1: {"Y", "CARRIER_Q", "RESUME_CARD", "D_ADDR", "A_ADDR", "AM_ADDR", "S_ADDR", "Z_ADDR"},
    2: {"OL", "OT", "S", "R", "DA", "LOCAL_CHAR_F", "G_LABEL", "LOCAL_CHAR_G", "LOCAL_CHAR_I", "D_LABEL", "S_LABEL", "LOCAL_CHAR_B", "M_LOCAL", "LOCAL_CHAR_J", "LOCAL_CHAR_Z"},
    3: {"AIIN", "AIN", "AL", "AR", "IIN"},
    4: {"OK", "O", "CH", "CHD", "K", "T", "P", "SH", "CHK"},
    5: {"E", "EE", "EEE", "DY", "CTH", "SHED"},
    6: {"L", "AIR", "CKH", "CHEO", "OR", "SOLK", "LSH", "CPH", "CFH", "HO", "AN", "OS", "LD"},
}

LESSONS = [
    (1, "Besitzer und Rückverweis", "Bildbesitzer zuerst setzen; DIES, Wiederaufnahme und Unter-/Innen-/Sternadressen lesen."),
    (2, "Reihe, Wahl und lokale Zeichen", "Fortsetzung, nächste Stelle, Auswahl, Marke und kleine Seitenzeichen verwenden."),
    (3, "Menge und Adresse", "Sollwert, Einheit, Ziel, Quelle und Stufe an den laufenden Posten binden."),
    (4, "Arbeitsverben", "Ansetzen, bearbeiten, entnehmen, umsetzen, zugeben, einstellen, einsetzen, halten und behandeln."),
    (5, "Grad und Ende", "Kurz, lang, voll, bereit, abgesetzt und kartenspezifisch geschlossen unterscheiden."),
    (6, "Weg, Durchlass und Stoffgang", "Verbindung, Laufweg, Durchlass, Auszug, Sammeln, Spülen, Gegenlauf und Trennen."),
    (7, "Häufigste Formelkarten", "Die Karten 1–20 als ungeteilte Werkstattwendungen lernen."),
    (8, "Mittlere Formelkarten", "Die Karten 21–47 samt Schreibvarianten lernen."),
    (9, "Erweiterte Formelkarten", "Die Karten 48–63 als häufige seitenübergreifende Wendungen lernen."),
    (10, "Lange Formeln und lokale Namen", "Die Karten 64–79 lesen; danach bildlokale Nomenklatorkarten aus dem Exemplar kopieren."),
]


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def atom_lesson(component: str) -> int:
    for lesson, members in LESSON_COMPONENTS.items():
        if component in members:
            return lesson
    raise KeyError(component)


def main() -> None:
    atoms = read_tsv(ATOMS)
    families = read_tsv(FAMILIES)
    variants = read_tsv(VARIANTS)
    events = read_tsv(EVENTS)

    entries: list[dict[str, object]] = []
    for index, row in enumerate(atoms, 1):
        entries.append({
            "apprentice_entry_id": f"A{index:03d}",
            "entry_tier": "PRODUCTIVE_ABBREVIATION",
            "lesson": atom_lesson(row["component"]),
            "recognition_form": row["component"],
            "workshop_value_de": row["workshop_expansion_de"],
            "image_value_de": row["image_expansion_de"],
            "surface_variants": "PRODUCTIVE_RENDERING",
            "events_or_atom_uses": row["total_atom_occurrences"],
            "copy_or_compose_rule_de": "Bedeutung beitragen und mit Nachbarkürzeln zusammensetzen.",
        })
    for row in families:
        number = int(row["learned_card_id"].split("K")[-1])
        lesson = 7 if number <= 20 else 8 if number <= 47 else 9 if number <= 63 else 10
        entries.append({
            "apprentice_entry_id": f"A{len(entries) + 1:03d}",
            "entry_tier": "LEARNED_FORMULA_CARD",
            "lesson": lesson,
            "recognition_form": row["component_recipe"],
            "workshop_value_de": row["workshop_learned_value_de"],
            "image_value_de": row["image_register_value_de"],
            "surface_variants": row["surface_variants"],
            "events_or_atom_uses": row["events"],
            "copy_or_compose_rule_de": "Als ganze Karte erkennen; nicht bei jedem Auftreten neu ausdeuten.",
        })
    write_tsv(OUT / "PASS953_135_ENTRY_APPRENTICE_CODEBOOK.tsv", entries)
    write_tsv(OUT / "PASS953_155_FORMULA_SURFACE_VARIANTS.tsv", variants)

    layer_counts = Counter(row["codebook_layer"] for row in events)
    lesson_rows: list[dict[str, object]] = []
    for number, title, instruction in LESSONS:
        lesson_entries = [row for row in entries if int(row["lesson"]) == number]
        lesson_rows.append({
            "lesson": number,
            "lesson_title_de": title,
            "entries": len(lesson_entries),
            "entry_ids": "|".join(str(row["apprentice_entry_id"]) for row in lesson_entries),
            "instruction_de": instruction,
            "oral_exercise_de": "Meister zeigt Bildbesitzer und spricht die Kartenwerte; Lehrling setzt zwei neue Beispiele und liest sie zurück.",
        })
    write_tsv(OUT / "PASS953_10_LESSON_PLAN.tsv", lesson_rows)

    manual = [
        "# Lehrbuch für das 135-Einträge-System",
        "",
        "## Die einfache Regel",
        "",
        "1. Lies zuerst das Bild oder den bereits aktiven Besitzer.",
        "2. Erkenne eine der 79 vertrauten Ganzformeln, wenn ihre Komponentenfolge passt.",
        "3. Andernfalls setze die Bedeutung aus den 56 kurzen Kürzeln zusammen.",
        "4. Lokale Namen und Adressen werden aus dem Seitenexemplar kopiert.",
        "5. Ein fehlendes Zeilenende beendet keinen Satz; nur die gelernte Endkarte schließt den Teilgang.",
        "",
        "## Zehn Lektionen",
        "",
    ]
    for row in lesson_rows:
        manual.extend([f"### {row['lesson']}. {row['lesson_title_de']} ({row['entries']} Einträge)", "", str(row["instruction_de"]), ""])
    manual.extend([
        "## Was der Lehrling danach kann",
        "",
        f"Er kann {layer_counts['LEARNED_FORMULA_CARD']} sichtbare Ereignisse direkt als Formelkarten lesen, {layer_counts['PRODUCTIVE_ABBREVIATION_COMPOSITION']} aus Kürzeln bilden und {layer_counts['LOCAL_NOMENCLATOR_OR_ADDRESS']} lokale Bild-/Adresswerte am Exemplar nachschlagen.",
    ])
    (OUT / "PASS953_COMPLETE_APPRENTICE_MANUAL.md").write_text("\n".join(manual) + "\n", encoding="utf-8")

    report = f"""# Pass 953 — ein 1420er Lehrling kann das System lernen

Das aktuelle Modell verlangt **135 gelernte Einträge**: 56 produktive Kürzel und
79 Formelkarten. Die Formelvarianten werden nicht als zusätzliche Wörter gezählt.
Zehn Unterrichtsstufen führen von Bildbesitzer und Rückverweis über Menge,
Adresse, Handlung und Grad bis zu langen Formeln und lokalen Nomenklatorwerten.

Die Ereignisbilanz bleibt {dict(layer_counts)}. Das ist kein Alphabetunterricht,
sondern ein kleines praktisches Karten- und Kürzelbuch mit mündlicher Einweisung
und Seitenexemplar.
"""
    (OUT / "PASS953_REPORT.md").write_text(report, encoding="utf-8")
    outputs = {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in sorted(OUT.glob("PASS953_*")) if "BUILD_SUMMARY" not in path.name and "VALIDATION" not in path.name}
    summary = {"entries": len(entries), "abbreviations": len(atoms), "formula_cards": len(families), "lessons": len(lesson_rows), "layer_counts": layer_counts, "outputs": outputs}
    (OUT / "PASS953_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
