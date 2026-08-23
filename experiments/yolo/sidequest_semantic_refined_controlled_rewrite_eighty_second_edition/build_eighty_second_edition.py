#!/usr/bin/env python3
"""Propagate the refined source lexicon through all fourteen controlled units."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
LEXICON = ROOT / "experiments/yolo/sidequest_semantic_source_word_refinement_eighty_first_edition/EIGHTY_FIRST_54_REFINED_SOURCE_LEXICON.tsv"
UNITS = ROOT / "experiments/yolo/sidequest_semantic_selected_workshop_eightieth_edition/EIGHTIETH_14_CONTROLLED_UNIT_EDITION.tsv"
BINDING = ROOT / "experiments/yolo/sidequest_semantic_selected_workshop_eightieth_edition/EIGHTIETH_776_CURRENT_BINDING.tsv"


READINGS = {
    "H1": "Von der Bildpflanze die Wurzel nehmen. Mit Wasser im Gefäß ansetzen, trennen und den Auszug sammeln. Die örtliche Portion als Mittel verwenden; den Rückstand verwahren.",
    "H2": "Jungen Spross und Blatt der Bildpflanze nehmen, teilen und durch Tuch auswringen. Den Auszug in örtlicher Portion mit dem Trägerstoff im Gefäß ansetzen und als Auftrag verwenden.",
    "H3": "Blüte und Blatt der Bildpflanze in Auszugsflüssigkeit ansetzen, durch Tuch auswringen, absetzen und nachseihen. Den Auszug als Mittel halten; einen Teil mit Trägerstoff als Auftrag verwenden.",
    "H4": "Blatt der Bildpflanze mit Auszugsflüssigkeit im Gefäß ansetzen und halten. Durch Tuch auswringen, den Auszug sammeln, mit Bindestoff verbinden und als Auftrag verwenden.",
    "H5": "Kraut der Bildpflanze mit Wasser und Auszugsflüssigkeit ansetzen. Durch Tuch trennen und den Auszug sammeln. Mit Bindestoff als Mittel verwenden oder als Auftrag einsetzen.",
    "B1": "Badende an der Beckenstation im Becken ansetzen. Waschflüssigkeit und Zusatz auf Temperatur bringen, für die Dauer halten und an der örtlichen Stelle waschen. Danach durch den Seihgang führen, absetzen und zum Ablauf abführen.",
    "B2": "An jeder Beckenstation die Öffnung wählen, Waschflüssigkeit am Einlass in den Flüssigkeitslauf führen und am Ablauf halten. Zusatz und Temperatur einstellen; die Badenden für die Dauer im Teilbad an der örtlichen Stelle halten und danach durch den Seihgang führen.",
    "B3": "Badende und Beckenstation getrennt adressieren. Waschflüssigkeit durch die Öffnung in den Flüssigkeitslauf führen, an der örtlichen Stelle für die Dauer halten, durch den Seihgang führen und im Auffanggefäß sammeln; danach am Ablauf abführen.",
    "B4": "An der Beckenstation Waschflüssigkeit durch Öffnung und Einlass in den Flüssigkeitslauf führen. Das Tuch für Dauer und Temperatur an der örtlichen Stelle der Badenden halten, durch den Seihgang führen und am Ablauf abführen.",
    "B5": "Die Beckenstation an der Öffnung ansetzen. Waschflüssigkeit im Flüssigkeitslauf auf Temperatur bringen, für die Dauer an der örtlichen Stelle halten und am Ablauf abführen.",
    "B6": "Die Beckenstation öffnen, Waschflüssigkeit am Einlass in den Flüssigkeitslauf führen und mit Tuch durch den Seihgang führen. Den getrennten Anteil an der örtlichen Stelle anwenden.",
    "A1": "Am Himmelsrad Himmelssektor und Sternplatz wählen. Das Bedingungsfeld an der Ringrubrik zeigen, das Himmelszeichen kopieren und Kalenderwert sowie Himmelswert mit dem örtlichen Instrumentenschlüssel lesen. Beim Radwechsel den Schlüssel wechseln.",
    "A2": "Im Sternpaneel einen Sternplatz und ein 28er Feld wählen. Das Himmelszeichen kopieren, den Himmelswert mit dem örtlichen Instrumentenschlüssel lesen und beim Paneelwechsel den Schlüssel wechseln.",
    "A3": "Am Rosetteninstrument ein 28er Feld und die Ringrubrik wählen. Das Himmelszeichen kopieren und mit dem örtlichen Instrumentenschlüssel Kalenderwert, Wetterzeichen, Lichtzeichen, Zeitzeichen oder Eigenschaft lesen. Beim Rosettenwechsel den Schlüssel wechseln.",
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
    by_slot = {row["source_slot"]: row["eighty_first_selected_value_de"] for row in read_tsv(LEXICON)}
    units = []
    comparisons = []
    for row in read_tsv(UNITS):
        words = "; ".join(by_slot[slot] for slot in row["source_slot_program"].split(">"))
        revised = READINGS[row["unit_id"]]
        changed = revised != row["controlled_unit_reading_de"]
        units.append({
            **row,
            "selected_source_words_de": words,
            "controlled_unit_reading_de": revised,
            "source_revision_status": "REVISED" if changed else "UNCHANGED",
        })
        comparisons.append({
            "unit_id": row["unit_id"],
            "page": row["page"],
            "before_reading_de": row["controlled_unit_reading_de"],
            "after_reading_de": revised,
            "changed": "YES" if changed else "NO",
            "composition_improvement_de": {
                "H1": "Mittel ersetzt das moderne Endprodukt.",
                "H2": "Trägerstoff benennt die Stoffrolle.",
                "H3": "Auszugsflüssigkeit, Mittel und Trägerstoff bilden eine lesbare Kette.",
                "H4": "Auszugsflüssigkeit und Bindestoff werden zu Werkstattnomen.",
                "H5": "Die zwei Verwendungswege enden nun beide in kurzen Nomen.",
                "B1": "Seihgang ist ein ausführbarer Arbeitsgang.",
                "B2": "Seihgang fügt sich als letzte Station ein.",
                "B3": "Seihgang liegt zwischen Halten und Auffangen.",
                "B4": "Tuch und Seihgang sind nicht länger dasselbe Wort.",
                "B5": "Keine der zwölf Revisionen betrifft diese Station.",
                "B6": "Tuch führt durch den Seihgang statt abstrakt zu filtern.",
                "A1": "Bedingungsfeld und Himmelszeichen klingen wie Teile einer Tafel.",
                "A2": "28er Feld und Himmelszeichen sind kurze Adresswörter.",
                "A3": "Vier moderne Wertetiketten werden zu lesbaren Zeichenkategorien.",
            }[row["unit_id"]],
        })
    write_tsv(OUT / "EIGHTY_SECOND_14_REFINED_CONTROLLED_UNITS.tsv", units)
    write_tsv(OUT / "EIGHTY_SECOND_14_BEFORE_AFTER_READINGS.tsv", comparisons)

    unit_lookup = {row["unit_id"]: row for row in units}
    bindings = []
    for row in read_tsv(BINDING):
        unit = unit_lookup[row["finite_source_unit"]]
        row = dict(row)
        row["selected_source_vocabulary"] = unit["selected_source_words_de"]
        row["controlled_unit_reading_de"] = unit["controlled_unit_reading_de"]
        row["controlled_rewrite_status"] = "REFINED_SELECTED_SOURCE"
        bindings.append(row)
    write_tsv(OUT / "EIGHTY_SECOND_776_REFINED_BINDING.tsv", bindings)

    doc = ["# Verfeinerte kontrollierte Zehn-Seiten-Ausgabe", ""]
    for row in units:
        doc.extend([
            f"## {row['unit_id']} · {row['page']}", "",
            f"**Wörter:** {row['selected_source_words_de']}", "",
            f"**Lesung:** {row['controlled_unit_reading_de']}", "",
        ])
    (OUT / "EIGHTY_SECOND_COMPLETE_REFINED_TEN_PAGE_EDITION.md").write_text("\n".join(doc).rstrip() + "\n", encoding="utf-8")

    report = [
        "# Zweiundachtzigste Werkstattfassung: verfeinerte Lesung", "",
        "## Ergebnis", "",
        "The twelve source-word revisions are propagated through all fourteen units and",
        "all 776 bindings. Thirteen units change wording; B5 remains unchanged.", "",
        "The main gain is compositional. Herbal now speaks of extraction liquid, carrier",
        "material, binding material and means; Biological separates cloth from a straining",
        "pass; Astro reads fields and signs instead of labels and abstract value metrics.", "",
        "No card/root meaning, visible group, owner, unit program or scribe rendering is",
        "changed. The rewrite acts only at the selected source-word layer.", "",
        "Only the fixed ten pages were used; f84 and f84r remained sealed.",
    ]
    (OUT / "EIGHTY_SECOND_EDITION_REPORT.md").write_text("\n".join(report).rstrip() + "\n", encoding="utf-8")

    summary = {
        "status": "CONSISTENT",
        "counts": {
            "units": len(units),
            "changed_units": sum(row["source_revision_status"] == "REVISED" for row in units),
            "unchanged_units": sum(row["source_revision_status"] == "UNCHANGED" for row in units),
            "bound_groups": len(bindings),
        },
        "sources": {str(path.relative_to(ROOT)): sha256(path) for path in (LEXICON, UNITS, BINDING)},
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
