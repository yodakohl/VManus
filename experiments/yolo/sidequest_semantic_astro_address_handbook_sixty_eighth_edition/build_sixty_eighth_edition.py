#!/usr/bin/env python3
"""Build three separate Astro address-and-readout manuals."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
GROUPS = ROOT / "experiments/yolo/sidequest_theory_candidates_v75/V75_SELECTED_395_GROUP_CELESTIAL_EDITION.tsv"
LOCI = ROOT / "experiments/yolo/sidequest_theory_candidates_v75/V75_SELECTED_142_LOCUS_CELESTIAL_EDITION.tsv"
INSTRUMENTS = ROOT / "experiments/yolo/sidequest_theory_candidates_v75/V75_SELECTED_THREE_INSTRUMENTS.tsv"
NAMESPACES = ROOT / "experiments/yolo/sidequest_theory_candidates_v75/V75_SELECTED_NAMESPACE_REGISTRY.tsv"

MANUALS = {
    "A1": {
        "title": "Zwei getrennte Himmelsräder",
        "instruction": "Wähle zuerst linkes oder rechtes Rad. Zeige den lokalen Sektor, Sternplatz, Ring oder Bedingungsplatz. Kopiere das Etikett und lies ausschließlich den Eintrag dieses Rades im Meisterexemplar. Lösche beim Radwechsel jeden lokalen Schlüssel.",
        "content_wager": "rechts ein 12-teiliges Zeichen-/Kalenderrad mit Bedingungen; links ein Stern-/Aspekt- oder Lehrkreis",
        "forbidden": "kein 7×12-Schema, keine Verbindung zwischen den Rädern, kein Start und keine Umlaufrichtung",
    },
    "A2": {
        "title": "Mehrpaneeliger Sternatlas",
        "instruction": "Wähle das sichtbare Paneel oder Zentrum und danach genau einen lokalen Sternplatz. Kopiere sein Etikett als paneelgebundenen Exemplareintrag. Ein anderes Zentrum eröffnet einen neuen Namensraum.",
        "content_wager": "28 räumliche Stern- oder Mondstationsadressen innerhalb eines mehrteiligen Himmelsatlanten",
        "forbidden": "kein einheitliches Zentrum, keine feste Kreisrichtung und kein Schlüssel zu f69v",
    },
    "A3": {
        "title": "Drei getrennte Rosetteninstrumente",
        "instruction": "Wähle linkes, mittleres oder rechtes Rad. Links kann einer von 28 lokalen Plätzen nachgeschlagen werden; Mitte und rechts tragen eigene Rubriken. Kein Wert darf zwischen den drei Rädern wandern.",
        "content_wager": "links Mondstations-/Kalenderinventar; Mitte möglicher Witterungs- oder Zustandsring; rechts möglicher Licht-/Planeten-/Komplexionsring",
        "forbidden": "keine eine 28-Schritt-Regelfolge, kein gemeinsamer Start und keine Zuordnung zu f68r1",
    },
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
    groups = read_tsv(GROUPS)
    loci = read_tsv(LOCI)
    instruments = {row["diagram_id"]: row for row in read_tsv(INSTRUMENTS)}
    namespaces = read_tsv(NAMESPACES)

    group_rows = []
    for row in groups:
        group_rows.append({
            "group_serial": row["group_serial"],
            "diagram_id": row["diagram_id"],
            "page": row["page"],
            "locus": row["locus"],
            "event_index": row["event_index"],
            "opaque_local_id": row["opaque_local_id"],
            "local_owner": row["local_image_owner"],
            "local_namespace": row["local_namespace"],
            "copy_instruction_de": f"Kopiere Gruppe {row['event_index']} am Besitzer {row['local_image_owner']}.",
            "local_readout_instruction_de": "Schlage den vollständigen Wert nur im lokalen Instrumentenexemplar nach.",
            "working_content_class": row["local_content_class"],
            "orientation": "NONE",
            "crosspage_key": "NONE",
            "prose_grammar_import": "NONE",
        })
    write_tsv(OUT / "SIXTY_EIGHTH_395_ASTRO_GROUP_ADDRESS_LEDGER.tsv", group_rows)

    locus_rows = []
    for row in loci:
        locus_rows.append({
            "page": row["page"],
            "diagram_id": row["diagram_id"],
            "locus": row["locus"],
            "group_count": row["group_count"],
            "local_owner": row["local_image_owner"],
            "local_namespace": row["local_namespace"],
            "silent_argument_default": row["silent_argument_default"],
            "lookup_action_de": f"Zeige {row['silent_argument_default']}; kopiere alle {row['group_count']} Gruppen; lies den Wert nur unter {row['local_namespace']}.",
            "complete_local_working_label": row["complete_copied_local_meaning_or_label"],
            "content_wager": MANUALS[row["diagram_id"]]["content_wager"],
            "orientation": "NONE",
            "crosspage_key": "NONE",
        })
    write_tsv(OUT / "SIXTY_EIGHTH_142_ASTRO_LOCUS_MANUAL.tsv", locus_rows)

    instrument_rows = []
    for diagram_id in ("A1", "A2", "A3"):
        source = instruments[diagram_id]
        manual = MANUALS[diagram_id]
        instrument_rows.append({
            "diagram_id": diagram_id,
            "page": source["page"],
            "title_de": manual["title"],
            "locus_count": source["locus_count"],
            "group_count": source["group_count"],
            "visible_system": source["repaired_visual_system"],
            "apprentice_lookup_instruction_de": manual["instruction"],
            "creative_content_wager": manual["content_wager"],
            "strongest_competing_instrument": source["strongest_competing_instrument"],
            "forbidden_join_or_order": manual["forbidden"],
            "orientation": "NONE",
            "crosspage_mapping": "NONE",
            "prose_card_import": "NONE",
        })
    write_tsv(OUT / "SIXTY_EIGHTH_3_ASTRO_INSTRUMENT_CARDS.tsv", instrument_rows)

    namespace_rows = []
    for order, row in enumerate(namespaces, start=1):
        namespace_rows.append({
            "namespace_order": order,
            **row,
            "entry_rule": "CLEAR_PREVIOUS_INSTRUMENT_KEY_THEN_COPY_LOCAL_LABEL",
            "portable_word_value": "NONE__LOCAL_NOMENCLATOR_ONLY",
        })
    write_tsv(OUT / "SIXTY_EIGHTH_13_LOCAL_NAMESPACES.tsv", namespace_rows)

    # Four spaced examples per page; addresses remain editorial, not a claimed reading order.
    examples = []
    page_loci = {page: [row for row in locus_rows if row["page"] == page] for page in ("f67r2", "f68r1", "f69v")}
    for page in ("f67r2", "f68r1", "f69v"):
        rows = page_loci[page]
        indices = (0, len(rows) // 3, (2 * len(rows)) // 3, len(rows) - 1)
        for local_order, index in enumerate(indices, start=1):
            row = rows[index]
            examples.append({
                "example_id": f"{row['diagram_id']}-X{local_order:02d}",
                "page": page,
                "locus": row["locus"],
                "local_owner": row["local_owner"],
                "namespace": row["local_namespace"],
                "lookup_trace_de": row["lookup_action_de"],
                "creative_master_category": row["content_wager"],
                "exact_external_name": "NOT_ASSIGNED",
            })
    write_tsv(OUT / "SIXTY_EIGHTH_12_EXAMPLE_LOOKUPS.tsv", examples)

    doc = [
        "# Drei getrennte Astro-Instrumente", "",
        "Astro benutzt kein importiertes Prosa-Wörterbuch. Ein Lehrling zeigt einen",
        "sichtbaren Locus, kopiert dessen lokales Etikett und schlägt es nur im",
        "zugehörigen Instrumentenexemplar nach. Start, Drehrichtung und Seitenjoin",
        "werden nicht ergänzt.", "",
    ]
    for row in instrument_rows:
        doc.extend([
            f"## {row['diagram_id']} · {row['page']} · {row['title_de']}", "",
            f"**Gebrauch:** {row['apprentice_lookup_instruction_de']}", "",
            f"**Konkrete Arbeitswette:** {row['creative_content_wager']}.", "",
            f"**Nicht erlaubt:** {row['forbidden_join_or_order']}.", "",
        ])
    (OUT / "SIXTY_EIGHTH_COMPLETE_ASTRO_ADDRESS_HANDBOOK.md").write_text("\n".join(doc).rstrip() + "\n", encoding="utf-8")

    count_by_page = Counter(row["page"] for row in group_rows)
    report = [
        "# Achtundsechzigste Werkstattfassung: Astro-Adresshandbuch", "",
        "## Ergebnis", "",
        "Die 395 Astrogruppen und 142 Loci sind als drei getrennte lokale Instrumente",
        "vollständig ansprechbar. f67r2 enthält zwei nicht verbundene Räder; f68r1",
        "einen mehrpaneeligen Sternatlas; f69v drei heterogene Rosetten, wobei nur das",
        "linke Rad ein sichtbares 28-Platz-Inventar trägt.", "",
        "Die kreative Inhaltswette bleibt himmels- und kalenderbezogen: Zeichen- oder",
        "Kalendersektoren, Stern-/Mondstationsplätze, Bedingungen, Witterung, Licht oder",
        "Komplexion. Diese Kategorien gehören zum lokalen Meisterexemplar. Sie werden",
        "nicht als globale Wortstämme gelesen.", "",
        "Es gibt keine Leserichtung, keinen gemeinsamen Start, keinen f68–f69-Schlüssel",
        "und keinen Import der Herbal/Bio-Kartenwerte.", "",
        f"Gruppen: f67r2 {count_by_page['f67r2']}, f68r1 {count_by_page['f68r1']}, f69v {count_by_page['f69v']}.", "",
        "Nur f67r2, f68r1 und f69v wurden verwendet; f84 und f84r blieben versiegelt.",
    ]
    (OUT / "SIXTY_EIGHTH_EDITION_REPORT.md").write_text("\n".join(report).rstrip() + "\n", encoding="utf-8")

    summary = {
        "status": "CONSISTENT",
        "counts": {
            "astro_pages": 3,
            "astro_instruments": len(instrument_rows),
            "local_namespaces": len(namespace_rows),
            "astro_loci": len(locus_rows),
            "astro_groups": len(group_rows),
            "example_lookups": len(examples),
        },
        "page_group_counts": dict(sorted(count_by_page.items())),
        "sources": {str(path.relative_to(ROOT)): sha256(path) for path in (GROUPS, LOCI, INSTRUMENTS, NAMESPACES)},
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
