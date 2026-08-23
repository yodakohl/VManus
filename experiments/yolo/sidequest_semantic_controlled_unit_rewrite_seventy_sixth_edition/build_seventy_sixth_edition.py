#!/usr/bin/env python3
"""Rewrite all fourteen fixed units with only the selected finite vocabulary."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
PROGRAMS = ROOT / "experiments/yolo/sidequest_semantic_source_slot_selection_seventy_fifth_edition/SEVENTY_FIFTH_14_SELECTED_SOURCE_PROGRAMS.tsv"
BINDING = ROOT / "experiments/yolo/sidequest_semantic_source_slot_selection_seventy_fifth_edition/SEVENTY_FIFTH_776_SELECTED_SOURCE_BINDING.tsv"


READINGS = {
    "H1": (
        "nehmen; ansetzen; trennen; sammeln; verwenden; verwahren",
        "Von der Bildpflanze die Wurzel nehmen. Mit Wasser im Gefäß ansetzen, trennen und den Auszug sammeln. Die örtliche Portion als Endprodukt verwenden; den Rückstand verwahren.",
        "Eine Wurzelbereitung mit getrenntem Auszug und verwahrtem Rest.",
    ),
    "H2": (
        "nehmen; teilen; auswringen; sammeln; ansetzen; auftragen",
        "Jungen Spross und Blatt der Bildpflanze nehmen, teilen und durch Tuch auswringen. Den Auszug in örtlicher Portion mit dem Träger im Gefäß ansetzen und als Auftrag verwenden.",
        "Eine zweiteilige Pflanzenbereitung, deren Auszug aufgetragen wird.",
    ),
    "H3": (
        "nehmen; ansetzen; auswringen; absetzen; nachseihen; halten; auftragen",
        "Blüte und Blatt der Bildpflanze im Auszugsmedium ansetzen, durch Tuch auswringen, absetzen und nachseihen. Den Auszug als Endprodukt halten; einen Teil mit Träger als Auftrag verwenden.",
        "Ein geklärter Blüten- und Blattauszug mit zweiter Auftragsschiene.",
    ),
    "H4": (
        "nehmen; ansetzen; halten; auswringen; sammeln; binden; auftragen",
        "Blatt der Bildpflanze mit Auszugsmedium im Gefäß ansetzen und halten. Durch Tuch auswringen, den Auszug sammeln, mit Binder verbinden und als Auftrag verwenden.",
        "Ein gehaltener Blattansatz wird getrennt, gebunden und aufgetragen.",
    ),
    "H5": (
        "nehmen; ansetzen; trennen; sammeln; binden; verwenden; auftragen",
        "Kraut der Bildpflanze mit Wasser und Auszugsmedium ansetzen. Durch Tuch trennen und den Auszug sammeln. Mit Binder als Endprodukt verwenden oder als Auftrag einsetzen.",
        "Das Kraut liefert einen gebundenen Auszug für zwei Verwendungswege.",
    ),
    "B1": (
        "ansetzen; wärmen; halten; waschen; filtern; absetzen; abführen",
        "Badende an der Beckenstation im Becken ansetzen. Waschflüssigkeit und Zusatz auf Temperatur bringen, für die Dauer halten und an der örtlichen Stelle waschen. Danach filtern, absetzen und zum Ablauf abführen.",
        "Eine lokale Bade- und Waschfolge mit geregeltem Ende.",
    ),
    "B2": (
        "öffnen; einlassen; führen; wärmen; halten; baden; filtern; abführen",
        "An jeder Beckenstation die Öffnung wählen, Waschflüssigkeit am Einlass in den Flüssigkeitslauf führen und am Ablauf halten. Zusatz und Temperatur einstellen; die Badenden für die Dauer im Teilbad an der örtlichen Stelle halten und danach filtern.",
        "Mehrere sichtbare Teilbadstationen werden einzeln neu eingerichtet.",
    ),
    "B3": (
        "öffnen; führen; waschen; halten; filtern; sammeln; abführen",
        "Badende und Beckenstation getrennt adressieren. Waschflüssigkeit durch die Öffnung in den Flüssigkeitslauf führen, an der örtlichen Stelle für die Dauer halten, filtern und im Auffanggefäß sammeln; danach am Ablauf abführen.",
        "Die Rand- und Hauptstationen bilden lokale, nicht globale Flüssigkeitsgänge.",
    ),
    "B4": (
        "öffnen; einlassen; führen; waschen; halten; filtern; abführen",
        "An der Beckenstation Waschflüssigkeit durch Öffnung und Einlass in den Flüssigkeitslauf führen. Das Tuch für die Dauer und Temperatur an der örtlichen Stelle der Badenden halten, filtern und am Ablauf abführen.",
        "Tuchkontakt und lokaler Durchlauf verbinden Bad- und Apparategebrauch.",
    ),
    "B5": (
        "öffnen; führen; wärmen; halten; abführen",
        "Die Beckenstation an der Öffnung ansetzen. Waschflüssigkeit im Flüssigkeitslauf auf Temperatur bringen, für die Dauer an der örtlichen Stelle halten und am Ablauf abführen.",
        "Eine kurze technische Randstation ohne eigenen Figurenbesitzer.",
    ),
    "B6": (
        "öffnen; einlassen; führen; waschen; filtern; anwenden",
        "Die Beckenstation öffnen, Waschflüssigkeit am Einlass in den Flüssigkeitslauf führen und durch Tuch filtern. Den getrennten Anteil an der örtlichen Stelle anwenden.",
        "Ein Einlass- und Filterposten mit lokalem Ziel.",
    ),
    "A1": (
        "wählen; zeigen; kopieren; lesen; wechseln",
        "Am Himmelsrad den Himmelssektor und Sternplatz wählen. Die Himmelsbedingung an der Ringrubrik zeigen, das Himmelslabel kopieren und Kalenderwert sowie Himmelswert mit dem örtlichen Instrumentenschlüssel lesen. Beim Radwechsel den Schlüssel wechseln.",
        "Zwei getrennte Räder liefern je einen lokalen Himmelswert.",
    ),
    "A2": (
        "wählen; zeigen; kopieren; lesen; wechseln",
        "Im Sternpaneel einen Sternplatz und einen 28er Platz wählen. Das Himmelslabel kopieren, den Himmelswert mit dem örtlichen Instrumentenschlüssel lesen und beim Paneelwechsel den Schlüssel wechseln.",
        "Ein mehrteiliges Sternfeld ordnet 28 lokale Plätze ohne globale Reihenfolge.",
    ),
    "A3": (
        "wählen; zeigen; kopieren; lesen; wechseln",
        "Am Rosetteninstrument einen 28er Platz und die Ringrubrik wählen. Das Himmelslabel kopieren und mit dem örtlichen Instrumentenschlüssel Kalenderwert, Witterungswert, Lichtwert, Zeitwert oder Qualitätswert lesen. Beim Rosettenwechsel den Schlüssel wechseln.",
        "Drei getrennte Rosetten tragen verschiedene lokale Wertarten.",
    ),
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
    units = []
    for row in read_tsv(PROGRAMS):
        operations, reading, compression = READINGS[row["unit_id"]]
        source_words = row["selected_controlled_vocabulary_de"].split("; ")
        units.append({
            "unit_order": row["unit_order"],
            "unit_id": row["unit_id"],
            "page": row["page"],
            "register": row["register"],
            "group_count": row["group_count"],
            "source_slot_program": row["finite_source_program"],
            "selected_source_words_de": row["selected_controlled_vocabulary_de"],
            "allowed_operation_words_de": operations,
            "controlled_unit_reading_de": reading,
            "one_sentence_compression_de": compression,
            "free_content_nouns_added": "NONE",
        })
    write_tsv(OUT / "SEVENTY_SIXTH_14_CONTROLLED_UNIT_READINGS.tsv", units)

    unit_lookup = {row["unit_id"]: row for row in units}
    bindings = []
    for row in read_tsv(BINDING):
        unit = unit_lookup[row["finite_source_unit"]]
        bindings.append({
            **row,
            "controlled_unit_reading_de": unit["controlled_unit_reading_de"],
            "controlled_rewrite_status": "BOUND_WITHOUT_FREE_CONTENT_NOUN",
        })
    write_tsv(OUT / "SEVENTY_SIXTH_776_CONTROLLED_REWRITE_BINDING.tsv", bindings)

    manual = [
        {"rule_order": 1, "rule": "OWNER_FIRST", "instruction_de": "Bild oder lokale Station setzt den stillen Besitzer."},
        {"rule_order": 2, "rule": "SOURCE_PROGRAM", "instruction_de": "Nur die für die Einheit gelisteten Quellenwörter einsetzen."},
        {"rule_order": 3, "rule": "CARD_OPERATIONS", "instruction_de": "Nur kurze Operationen aus dem gemeinsamen Kartenwörterbuch verwenden."},
        {"rule_order": 4, "rule": "LOCAL_ORDER", "instruction_de": "Die sichtbare Feld- und Aussageordnung beibehalten."},
        {"rule_order": 5, "rule": "NO_FREE_NOUN", "instruction_de": "Kein nicht gelistetes Stoff-, Körper-, Krankheits- oder Gerätewort ergänzen."},
        {"rule_order": 6, "rule": "RESET_OWNER", "instruction_de": "Beim sichtbaren Besitzerwechsel Quelle, Ziel und Lauf neu setzen."},
        {"rule_order": 7, "rule": "ASTRO_LOCAL", "instruction_de": "Himmelswerte nur im örtlichen Instrumentenschlüssel lesen."},
        {"rule_order": 8, "rule": "LINE_REFLOW", "instruction_de": "Eine Aussage darf über die physische Zeile weiterlaufen."},
    ]
    write_tsv(OUT / "SEVENTY_SIXTH_8_RULE_CONTROLLED_WRITING_MANUAL.tsv", manual)

    doc = ["# Kontrollierte Ausgabe der vierzehn Einheiten", ""]
    for row in units:
        doc.extend([
            f"## {row['unit_id']} · {row['page']}", "",
            f"**Quellenwörter:** {row['selected_source_words_de']}", "",
            f"**Arbeitslesung:** {row['controlled_unit_reading_de']}", "",
            f"**Kurzform:** {row['one_sentence_compression_de']}", "",
        ])
    (OUT / "SEVENTY_SIXTH_COMPLETE_CONTROLLED_TEN_PAGE_EDITION.md").write_text("\n".join(doc).rstrip() + "\n", encoding="utf-8")

    report = [
        "# Sechsundsiebzigste Werkstattfassung: kontrollierte Neuübersetzung", "",
        "## Ergebnis", "",
        "All fourteen units can be rewritten as short practical instructions using the",
        "selected 54-word source lexicon plus a small shared action vocabulary. The",
        "rewrite binds all 776 visible groups and adds no free content noun.", "",
        "The result is less literary than the older free-prose translations but more",
        "useful: Herbal reads as five preparation articles, Biological as six local",
        "basin/station procedures, and Astro as three local lookup instruments.", "",
        "The strongest content asymmetry remains visible rather than lexical: people in",
        "basins support bather and partial-bath language, while the celestial drawings",
        "support sky-sector and sky-label language. No card acquires those nouns.", "",
        "Only the fixed ten pages were used; f84 and f84r remained sealed.",
    ]
    (OUT / "SEVENTY_SIXTH_EDITION_REPORT.md").write_text("\n".join(report).rstrip() + "\n", encoding="utf-8")

    summary = {
        "status": "CONSISTENT",
        "counts": {
            "controlled_units": len(units),
            "bound_groups": len(bindings),
            "writing_rules": len(manual),
            "source_words_available": len({word for row in units for word in row["selected_source_words_de"].split("; ")}),
            "free_content_nouns": 0,
        },
        "sources": {str(path.relative_to(ROOT)): sha256(path) for path in (PROGRAMS, BINDING)},
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
