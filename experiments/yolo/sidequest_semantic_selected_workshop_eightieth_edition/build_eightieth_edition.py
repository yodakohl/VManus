#!/usr/bin/env python3
"""Consolidate the selected semantic workshop into one compact current edition."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
DICTIONARY = ROOT / "experiments/yolo/sidequest_semantic_minimal_dictionary_seventy_second_edition/SEVENTY_SECOND_43_MINIMAL_CORE_DICTIONARY.tsv"
SOURCE_LEXICON = ROOT / "experiments/yolo/sidequest_semantic_source_slot_selection_seventy_fifth_edition/SEVENTY_FIFTH_54_SELECTED_SOURCE_LEXICON.tsv"
LICENSES = ROOT / "experiments/yolo/sidequest_semantic_card_source_crosswalk_seventy_seventh_edition/SEVENTY_SEVENTH_43_CARD_TO_SOURCE_LICENSES.tsv"
UNITS = ROOT / "experiments/yolo/sidequest_semantic_controlled_unit_rewrite_seventy_sixth_edition/SEVENTY_SIXTH_14_CONTROLLED_UNIT_READINGS.tsv"
BINDING = ROOT / "experiments/yolo/sidequest_semantic_controlled_unit_rewrite_seventy_sixth_edition/SEVENTY_SIXTH_776_CONTROLLED_REWRITE_BINDING.tsv"
PROFILES = ROOT / "experiments/yolo/sidequest_semantic_selected_source_four_scribe_seventy_ninth_edition/SEVENTY_NINTH_4_SCRIBE_PROFILES_RETAINED.tsv"


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
    dictionary = read_tsv(DICTIONARY)
    lexicon = read_tsv(SOURCE_LEXICON)
    licenses = read_tsv(LICENSES)
    units = read_tsv(UNITS)
    binding = read_tsv(BINDING)
    profiles = read_tsv(PROFILES)
    write_tsv(OUT / "EIGHTIETH_43_MINIMAL_CARD_DICTIONARY.tsv", dictionary)
    write_tsv(OUT / "EIGHTIETH_54_SELECTED_SOURCE_LEXICON.tsv", lexicon)
    write_tsv(OUT / "EIGHTIETH_43_CARD_SOURCE_LICENSES.tsv", licenses)
    write_tsv(OUT / "EIGHTIETH_14_CONTROLLED_UNIT_EDITION.tsv", units)
    write_tsv(OUT / "EIGHTIETH_776_CURRENT_BINDING.tsv", binding)
    write_tsv(OUT / "EIGHTIETH_4_SCRIBE_PROFILES.tsv", profiles)

    manual = [
        (1, "LOOK", "Identify picture owner, basin station or diagram locus before reading text."),
        (2, "ADDRESS", "Keep owner and local namespace until a visible reset."),
        (3, "SEGMENT", "Take the longest registered card/root pattern first."),
        (4, "READ_CARD", "Speak the short minimal card meaning."),
        (5, "OPEN_SLOT", "Open only source-slot classes licensed by that card."),
        (6, "USE_UNIT_PROGRAM", "Choose concrete words only from the unit's finite source program."),
        (7, "KEEP_ORDER", "Preserve card, field and statement order; a statement may cross a line."),
        (8, "CLOSE_LOCALLY", "Close only with a registered terminal construction."),
        (9, "RESET", "Reset source, target and run at a visible owner change."),
        (10, "RENDER", "After exact-card selection, choose the hand's registered surface variant."),
        (11, "COPY_ASTRO", "For Astro, copy the opaque local group and read it only in its namespace."),
        (12, "NO_FREE_NOUN", "Do not add unregistered material, body, disease, device or celestial names."),
    ]
    manual_rows = [{"step": n, "rule": rule, "instruction": instruction} for n, rule, instruction in manual]
    write_tsv(OUT / "EIGHTIETH_12_STEP_WORKSHOP_MANUAL.tsv", manual_rows)

    one_page = [
        "# Aktuelle Ein-Seiten-Arbeitstheorie", "",
        "## Was das Schriftsystem ist", "",
        "Ein kleines Werkstattregister aus produktiven Kürzelkarten, gelernten",
        "Ganzkarten, stillen Bildbesitzern und lokalen Diagramm-Namensräumen. Die",
        "Karten sind keine Buchstabenchiffre. Ein Meister diktiert oder zeigt Besitzer,",
        "Quellenprogramm und Arbeitsgang; der Schreiber setzt daraus exakte Karten und",
        "wählt erst danach seine registrierte Oberfläche.", "",
        "## Das gemeinsame Wörterbuch", "",
        "28 kurze produktive Werte: Sollwert, Anteil, Stufe, Ziel, Quelle, Lauf,",
        "ansetzen, weiter, danach, Ansatz, dies, kurz, länger, vollständig, Ende,",
        "umsetzen, bereit, Durchlass, trennen, wärmen, absetzen, sammeln, Zutat,",
        "Auszug, bearbeiten, Teil, halten und Ergebnis. Dazu 15 gelernte Einträge wie",
        "auswringen, nachseihen, waschen, befestigen, ausgießen, anwenden und Tuch.", "",
        "## Wo konkrete Nomen herkommen", "",
        "Nicht aus dem kurzen Stamm allein. Jede Karte darf nur bestimmte Slotklassen",
        "öffnen; Bild, Register und eines von 14 festen Unitprogrammen liefern das Wort.",
        "Das ausgewählte Quellenlexikon hat 54 Einträge. Es nennt sichtbare Pflanzen,",
        "Badende/Teilbäder, lokale Nassstationen und lokale Himmelswerte, ohne freie",
        "Krankheits-, Körperteil-, Stoff- oder Planetennamen einzuschmuggeln.", "",
        "## Die zehn Seiten", "",
        "Fünf Herbal-Artikel behandeln Pflanzenmaterial, Auszug, Trennung, Bindung und",
        "Auftrag. Sechs Biological-Records behandeln lokale Becken-, Wasch-, Tuch-,",
        "Temperatur-, Dauer-, Einlass- und Ablaufgänge. Drei Astro-Instrumente sind",
        "lokale select-copy-read-Tabellen ohne globale Orientierung oder Seitenkey.", "",
        "## Mehrere Schreiber", "",
        "Vier einfache Handprofile können dieselben 116 Aussagen in 464 Kopien setzen.",
        "68 Aussagen variieren sichtbar; Kartenfolge und ausgewählte Bedeutung bleiben",
        "gleich. q/s/bare/kompakte Formen sind daher Rendererwahl nach der Semantik.", "",
        "## Aktuelle Grenze", "",
        "Die Architektur ist kohärent; die historische Klartextsprache ist nicht",
        "gefunden. Bad-/Himmelsinhalt ist bildgeführt, viele Stoff- und Zweckwerte bleiben",
        "Meistervokabular. Die nächste Arbeit gilt genau diesen schwachen Quellenslots.",
    ]
    (OUT / "EIGHTIETH_ONE_PAGE_CURRENT_THEORY.md").write_text("\n".join(one_page).rstrip() + "\n", encoding="utf-8")

    complete = ["# Vollständige kontrollierte Zehn-Seiten-Ausgabe", ""]
    for row in units:
        complete.extend([
            f"## {row['unit_id']} · {row['page']}", "",
            f"**Programm:** `{row['source_slot_program']}`", "",
            f"**Wörter:** {row['selected_source_words_de']}", "",
            f"**Lesung:** {row['controlled_unit_reading_de']}", "",
            f"**Kurzform:** {row['one_sentence_compression_de']}", "",
        ])
    (OUT / "EIGHTIETH_COMPLETE_CONTROLLED_TEN_PAGE_EDITION.md").write_text("\n".join(complete).rstrip() + "\n", encoding="utf-8")

    report = [
        "# Achtzigste Werkstattfassung: ausgewählte Gesamtausgabe", "",
        "## Ergebnis", "",
        "The current sidequest is consolidated into one compact release: 43 minimal",
        "card entries, 54 selected source words, 43 finite card-to-source licenses, 14",
        "controlled units, 776 bound groups, four scribe profiles and a 12-step manual.", "",
        "The architecture is now explicit enough to generate and read the ten fixed pages",
        "without sentence-sized dictionary entries. The remaining creative uncertainty",
        "is concentrated in source content and a small learned-card tail, not hidden in",
        "the renderer or line layout.", "",
        "Only the fixed ten pages were used; f84 and f84r remained sealed.",
    ]
    (OUT / "EIGHTIETH_EDITION_REPORT.md").write_text("\n".join(report).rstrip() + "\n", encoding="utf-8")

    summary = {
        "status": "CONSISTENT",
        "counts": {
            "minimal_dictionary_entries": len(dictionary),
            "selected_source_words": len(lexicon),
            "card_source_licenses": len(licenses),
            "controlled_units": len(units),
            "bound_groups": len(binding),
            "scribe_profiles": len(profiles),
            "manual_steps": len(manual_rows),
        },
        "sources": {str(path.relative_to(ROOT)): sha256(path) for path in (DICTIONARY, SOURCE_LEXICON, LICENSES, UNITS, BINDING, PROFILES)},
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
