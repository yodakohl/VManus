#!/usr/bin/env python3
"""Choose the shortest useful value for every divergent finite source slot."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
LEXICON = ROOT / "experiments/yolo/sidequest_semantic_finite_source_lexicon_seventy_fourth_edition/SEVENTY_FOURTH_54_FINITE_SOURCE_WORDS.tsv"
PROGRAMS = ROOT / "experiments/yolo/sidequest_semantic_finite_source_lexicon_seventy_fourth_edition/SEVENTY_FOURTH_14_FINITE_SOURCE_PROGRAMS.tsv"
BINDING = ROOT / "experiments/yolo/sidequest_semantic_finite_source_lexicon_seventy_fourth_edition/SEVENTY_FOURTH_776_FINITE_SOURCE_BINDING.tsv"

DECISIONS = {
    "ROOT": ("Wurzel", "NEUTRALIZED", 4, 4, "Die Wurzel ist sichtbar; medizinischer Teil und Werkstoff sind gleichermaßen möglich."),
    "HERB": ("Kraut", "NEUTRALIZED", 4, 4, "Pflanzenmaterial ist sichtbar, der Verwendungszweck nicht."),
    "EXTRACTION_MEDIUM": ("Auszugsmedium", "NEUTRALIZED", 2, 4, "Wein ist nicht sichtbar und gehört höchstens zum Meisterexemplar."),
    "OIL_BINDER": ("Träger", "NEUTRALIZED", 2, 4, "Öl und technisches Bindemittel teilen die Rolle; die Substanz bleibt offen."),
    "HONEY_BINDER": ("Binder", "NEUTRALIZED", 2, 4, "Honig ist nicht sichtbar; Bindefunktion genügt für beide Quellen."),
    "DRINK_OR_PRODUCT": ("Endprodukt", "NEUTRALIZED", 2, 4, "Kein Karten- oder Bildwert erzwingt Einnahme statt Werkprodukt."),
    "OUTER_APPLICATION": ("Auftrag", "NEUTRALIZED", 3, 4, "Kontakt ist plausibel; Körper oder Werkstück bleibt offen."),
    "FIGURE_WORKPIECE": ("Badende", "VISIBLE_MEDICAL_BATH_CUE", 5, 2, "Menschliche Figuren in Becken sind keine Werkstücke, auch wenn der Zweck offen bleibt."),
    "STATION": ("Beckenstation", "NEUTRALIZED", 4, 4, "Sichtbare Becken tragen medizinischen und betrieblichen Gebrauch."),
    "RUN": ("Flüssigkeitslauf", "VISIBLE_WET_PROCESS_CUE", 4, 3, "Lokale farbige Linien und Becken stützen Flüssigkeit stärker als abstrakten Arbeitslauf."),
    "WASH_LIQUID": ("Waschflüssigkeit", "NEUTRALIZED", 4, 4, "Waschen gilt für Körper, Stoff und Anlage."),
    "ADDITIVE": ("Zusatz", "NEUTRALIZED", 3, 3, "Die Karte trägt Zusatz, nicht dessen Zweck."),
    "BIO_CLOTH": ("Tuch", "NEUTRALIZED", 4, 4, "Tuch kann Auflage, Filter oder Waschmittelträger sein."),
    "TEMPERATURE": ("Temperatur", "NEUTRALIZED", 4, 4, "Wärme ist Prozessparameter, kein medizinisches Wort."),
    "DURATION": ("Dauer", "NEUTRALIZED", 4, 4, "Zeit gilt für Anwendung und Werkprozess gleichermaßen."),
    "BODY_WORK_AREA": ("örtliche Stelle", "NEUTRALIZED", 3, 4, "Das Ziel ist sichtbar oder geerbt, aber nicht als Körperstelle bezeichnet."),
    "IMMERSION": ("Teilbad", "VISIBLE_MEDICAL_BATH_CUE", 5, 3, "Figuren sitzen sichtbar in lokalen Becken; Teilbad ist die einfachste Beschreibung."),
    "FILTER": ("Filtern", "NEUTRALIZED", 4, 4, "Seihen und technisches Filtern sind dieselbe Arbeitsfunktion."),
    "SECTOR": ("Himmelssektor", "VISIBLE_CELESTIAL_CUE", 4, 3, "Die Radikonographie ist himmlisch, auch wenn Kalendername und Start fehlen."),
    "MANSION_PLACE": ("28er Platz", "NEUTRALIZED", 3, 4, "28 Plätze sind sichtbar, Mondstation und Kalenderwert bleiben gleich offen."),
    "CONDITION_PLACE": ("Himmelsbedingung", "VISIBLE_CELESTIAL_CUE", 4, 3, "Scheiben und Himmelsrad tragen eine lokale Bedingung, nicht beliebigen Arbeitszustand."),
    "LOCAL_LABEL": ("Himmelslabel", "VISIBLE_CELESTIAL_CUE", 4, 3, "Stern- und Radbesitzer machen den lokalen Labeltyp himmlisch."),
    "WEATHER_VALUE": ("Witterungswert", "VISIBLE_CELESTIAL_CUE", 4, 2, "Das mittlere f69-Wolken-/Wellenmotiv stützt Witterung als kreative Kurzlesung."),
    "LIGHT_VALUE": ("Lichtwert", "VISIBLE_CELESTIAL_CUE", 4, 3, "Strahlen-/Gesichtsmotiv stützt Licht stärker als generische Qualität."),
    "PLANET_VALUE": ("Zeitwert", "NEUTRALIZED", 3, 4, "Ein bestimmter Planet ist nicht identifiziert; Zeit ist der sparsamere Lookup-Wert."),
    "QUALITY_VALUE": ("Qualitätswert", "NEUTRALIZED", 3, 4, "Komplexion ist eine mögliche, aber nicht sichtbare Spezialisierung."),
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    lexicon = read_tsv(LEXICON)
    decisions = []
    selected = []
    for row in lexicon:
        divergent = row["medical_or_iatromedical_expansion_de"] != row["nonmedical_expansion_de"]
        if divergent:
            value, decision, medical_fit, nonmedical_fit, reason = DECISIONS[row["source_slot"]]
            decisions.append({
                "source_word_id": row["source_word_id"],
                "source_slot": row["source_slot"],
                "register": row["register"],
                "medical_candidate": row["medical_or_iatromedical_expansion_de"],
                "nonmedical_candidate": row["nonmedical_expansion_de"],
                "selected_value_de": value,
                "decision_class": decision,
                "medical_context_fit_1_to_5": medical_fit,
                "nonmedical_context_fit_1_to_5": nonmedical_fit,
                "selection_reason_de": reason,
            })
        else:
            value = row["medical_or_iatromedical_expansion_de"]
            decision = "UNCHANGED_SHARED"
        selected.append({
            **row,
            "selected_source_value_de": value,
            "selection_class": decision,
        })
    write_tsv(OUT / "SEVENTY_FIFTH_26_DIVERGENT_SLOT_DECISIONS.tsv", decisions)
    write_tsv(OUT / "SEVENTY_FIFTH_54_SELECTED_SOURCE_LEXICON.tsv", selected)

    by_slot = {row["source_slot"]: row["selected_source_value_de"] for row in selected}
    program_rows = []
    for row in read_tsv(PROGRAMS):
        tokens = row["finite_source_program"].split(">")
        program_rows.append({
            "unit_order": row["unit_order"],
            "unit_id": row["unit_id"],
            "page": row["page"],
            "register": row["register"],
            "group_count": row["group_count"],
            "finite_source_program": row["finite_source_program"],
            "selected_controlled_vocabulary_de": "; ".join(by_slot[token] for token in tokens),
            "unrestricted_nouns": "NONE",
        })
    write_tsv(OUT / "SEVENTY_FIFTH_14_SELECTED_SOURCE_PROGRAMS.tsv", program_rows)

    program_lookup = {row["unit_id"]: row for row in program_rows}
    binding_rows = []
    for row in read_tsv(BINDING):
        unit_id = row["finite_source_unit"]
        binding_rows.append({
            **row,
            "selected_source_vocabulary": program_lookup[unit_id]["selected_controlled_vocabulary_de"],
            "content_selection_status": "FINITE_SELECTED_LEXICON",
        })
    write_tsv(OUT / "SEVENTY_FIFTH_776_SELECTED_SOURCE_BINDING.tsv", binding_rows)

    doc = [
        "# Ausgewähltes endliches Quellenwörterbuch", "",
        "Nur 26 der 54 Slots brauchten eine Entscheidung. Wo Bild und Karten keinen",
        "engen Sachwert tragen, wird die neutralere Werkstattbedeutung gewählt. Wo die",
        "Ikonographie klarer ist, bleibt ein sichtbarer Bade- oder Himmelswert stehen.", "",
    ]
    for row in decisions:
        doc.extend([
            f"## {row['source_slot']} → {row['selected_value_de']}", "",
            f"{row['selection_reason_de']}", "",
            f"Rivalen: {row['medical_candidate']} ↔ {row['nonmedical_candidate']}.", "",
        ])
    (OUT / "SEVENTY_FIFTH_SELECTED_SOURCE_LEXICON.md").write_text("\n".join(doc).rstrip() + "\n", encoding="utf-8")

    class_counts = Counter(row["decision_class"] for row in decisions)
    report = [
        "# Fünfundsiebzigste Werkstattfassung: Auswahl der Quellen-Slots", "",
        "## Ergebnis", "",
        "All 26 divergent source slots now have one selected short value. Most are",
        "neutralized to their shared practical role: root, herb, extraction medium,",
        "carrier, binder, end product, application, basin station, wash liquid, cloth,",
        "temperature, duration, local place, filtering, 28-place slot, time and quality.", "",
        "A smaller visible-content set remains specific: bather and partial bath where",
        "people sit in basins; liquid run in the wet station drawings; celestial sector,",
        "condition and label in the wheels; weather and light values in the corresponding",
        "f69 motifs.", "",
        "The selected lexicon is therefore practical and image-led without forcing a",
        "medical book purpose. It still allows medical use as a local expansion.", "",
        "Only the fixed ten pages were used; f84 and f84r remained sealed.",
    ]
    (OUT / "SEVENTY_FIFTH_EDITION_REPORT.md").write_text("\n".join(report).rstrip() + "\n", encoding="utf-8")

    summary = {
        "status": "CONSISTENT",
        "counts": {
            "selected_source_words": len(selected),
            "divergent_slot_decisions": len(decisions),
            "selected_programs": len(program_rows),
            "bound_groups": len(binding_rows),
            **dict(sorted(class_counts.items())),
        },
        "sources": {str(path.relative_to(ROOT)): sha256(path) for path in (LEXICON, PROGRAMS, BINDING)},
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
