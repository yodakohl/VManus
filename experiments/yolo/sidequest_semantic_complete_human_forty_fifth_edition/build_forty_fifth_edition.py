#!/usr/bin/env python3
"""Build the integrated human-readable ten-page creative workshop edition."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
PROSE = ROOT / "experiments/yolo/sidequest_semantic_explicit_sentences_fortieth_edition/FORTIETH_116_EXPLICIT_SENTENCES.tsv"
ASTRO = ROOT / "experiments/yolo/sidequest_semantic_speakable_astro_thirty_sixth_edition/THIRTY_SIXTH_142_SPOKEN_LOCI.tsv"
KIT = [
    ("HUMAN_DICTIONARY", ROOT / "experiments/yolo/sidequest_semantic_human_dictionary_thirty_fifth_edition/THIRTY_FIFTH_56_TEACHING_ENTRIES.tsv", 56, "portable, bound, process and table entries"),
    ("ASTRO_MODULES", ROOT / "experiments/yolo/sidequest_semantic_speakable_astro_thirty_sixth_edition/THIRTY_SIXTH_13_INSTRUMENT_MODULES.tsv", 13, "local instrument namespaces"),
    ("PROCESS_MACROS", ROOT / "experiments/yolo/sidequest_semantic_process_macros_thirty_eighth_edition/THIRTY_EIGHTH_20_PROCESS_MACROS.tsv", 20, "multi-clause workshop moves"),
    ("MEMORY_SLOTS", ROOT / "experiments/yolo/sidequest_semantic_scribe_memory_thirty_ninth_edition/THIRTY_NINTH_FOUR_MEMORY_SLOTS.tsv", 4, "owner active target previous"),
    ("EXPLICIT_PROSE", PROSE, 116, "all spoken prose statements"),
    ("ERROR_RULES", ROOT / "experiments/yolo/sidequest_semantic_apprentice_error_book_forty_first_edition/FORTY_FIRST_EIGHT_ERROR_RULES.tsv", 8, "correction habits"),
    ("FORWARD_COMMANDS", ROOT / "experiments/yolo/sidequest_semantic_forward_composition_forty_second_edition/FORTY_SECOND_20_FORWARD_COMMANDS.tsv", 20, "new writing exercises"),
    ("SMALL_NOMENCLATOR", ROOT / "experiments/yolo/sidequest_semantic_nomenclator_forty_third_edition/FORTY_THIRD_15_NOMENCLATOR_LESSONS.tsv", 15, "twelve values and three splits"),
    ("APPRENTICE_CURRICULUM", ROOT / "experiments/yolo/sidequest_semantic_apprentice_curriculum_forty_fourth_edition/FORTY_FOURTH_24_LESSON_CURRICULUM.tsv", 24, "eight-day training order"),
]

PAGE_ORDER = ("f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r", "f67r2", "f68r1", "f69v")
PAGE_TITLES = {
    "f10r": "zwei offene Artikel zur breit gezähnten Bildpflanze",
    "f11r": "vierstufiger Pflanzen- und Filtergang",
    "f55v": "kurzer Pflanzenartikel mit Verwahrung",
    "f56r": "langer Pflanzenartikel mit Anwendung",
    "f81v": "gemeinsames zweireihiges Becken",
    "f82r": "mehrere lokale Becken- und Stationsvignetten",
    "f83r": "lokale Gefäß-, Bogen- und Randstationsgänge",
    "f67r2": "zwei getrennte himmlische Vergleichsräder",
    "f68r1": "mehrteiliger Sternstationsatlas",
    "f69v": "drei getrennte himmlische Nachschlageinstrumente",
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
    prose = read_tsv(PROSE)
    astro = read_tsv(ASTRO)
    unified: list[dict[str, object]] = []
    for row in prose:
        unified.append({
            "unit_order": len(unified) + 1,
            "page": row["page"],
            "unit_id": row["statement_id"],
            "unit_kind": "PROSE_STATEMENT",
            "owner_or_namespace": row["owner_expansion_de"],
            "group_count": len(row["surface_sequence"].split()),
            "surface_sequence": row["surface_sequence"],
            "atom_sequence": row["atom_sequence"],
            "short_workshop_reading_de": row["fluent_workshop_sentence_de"],
            "fully_spoken_reading_de": row["fully_explicit_apprentice_sentence_de"],
            "memory_or_orientation_rule": row["memory_values_restored"],
            "local_boundary": "OWNER_AND_EXEMPLAR_SUPPLY_CONCRETE_NOUNS",
        })
    for row in astro:
        unified.append({
            "unit_order": len(unified) + 1,
            "page": row["page"],
            "unit_id": row["locus"],
            "unit_kind": "ASTRO_LOCUS",
            "owner_or_namespace": f"{row['namespace_id']}::{row['visible_owner']}",
            "group_count": row["group_count"],
            "surface_sequence": row["surface_sequence"],
            "atom_sequence": row["atom_sequence"],
            "short_workshop_reading_de": row["portable_card_reading_de"],
            "fully_spoken_reading_de": row["spoken_instruction_de"],
            "memory_or_orientation_rule": row["orientation_rule"],
            "local_boundary": row["crosspage_rule"],
        })
    write_tsv(OUT / "FORTY_FIFTH_258_READING_UNITS.tsv", unified)

    by_page: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in unified:
        by_page[str(row["page"])].append(row)
    page_rows = []
    for page in PAGE_ORDER:
        rows = by_page[page]
        page_rows.append({
            "page": page,
            "page_title_de": PAGE_TITLES[page],
            "register": "PROSE" if page in {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"} else "ASTRO_LOOKUP",
            "reading_units": len(rows),
            "visible_groups": sum(int(row["group_count"]) for row in rows),
            "owner_or_namespace_count": len({str(row["owner_or_namespace"]) for row in rows}),
            "reading_mode": "KARTEN_PLUS_VIERFACH_MERKTAFEL" if rows[0]["unit_kind"] == "PROSE_STATEMENT" else "LOKALE_ADRESSE_PLUS_KARTENWERT",
            "continuous_text_rule": "STATEMENTS_IN_RECORD_ORDER" if rows[0]["unit_kind"] == "PROSE_STATEMENT" else "NO_LINEAR_TEXT__ADDRESS_EACH_LOCUS",
        })
    write_tsv(OUT / "FORTY_FIFTH_TEN_PAGE_SUMMARY.tsv", page_rows)

    kit_rows = [{
        "layer_order": index,
        "layer_id": layer_id,
        "source_path": str(path.relative_to(ROOT)),
        "source_sha256": sha256(path),
        "teaching_items": count,
        "purpose_de": purpose,
    } for index, (layer_id, path, count, purpose) in enumerate(KIT, 1)]
    write_tsv(OUT / "FORTY_FIFTH_CURRENT_TEACHING_KIT.tsv", kit_rows)

    lines = [
        "# Vollständige menschliche Zehnseiten-Ausgabe",
        "",
        "Diese Ausgabe zeigt unsere derzeit beste kreative Arbeitstheorie. Bei Prosa folgen",
        "auf jede sichtbare Kartenfolge zuerst die kurze Werkstattlesung und dann die bewusst",
        "vollständige Lehrlingsfassung mit Bildbesitzer und Merktafelreferenten. Die drei",
        "Himmelsseiten werden dagegen als lokale Instrumente angesprochen, nicht als Fließtext.",
        "",
    ]
    for page in PAGE_ORDER:
        page_meta = next(row for row in page_rows if row["page"] == page)
        lines.extend([
            f"## {page} — {PAGE_TITLES[page]}",
            "",
            f"{page_meta['reading_units']} Leseeinheiten, {page_meta['visible_groups']} sichtbare Gruppen. Modus: `{page_meta['reading_mode']}`.",
            "",
        ])
        for row in by_page[page]:
            lines.extend([
                f"### {row['unit_id']}",
                "",
                f"Besitzer/Adresse: **{row['owner_or_namespace']}**",
                "",
                f"Sichtbar: `{row['surface_sequence']}`",
                "",
                f"Karten: `{row['atom_sequence']}`",
                "",
                f"Kurz: {row['short_workshop_reading_de']}",
                "",
                f"Voll gesprochen: {row['fully_spoken_reading_de']}",
                "",
            ])
    lines.extend([
        "## Arbeitsgrenze",
        "",
        "Die Prosa ist eine vollständige kreative Übersetzung, aber konkrete Pflanzen, Stoffe,",
        "Beschwerden und Geräte kommen weiterhin aus Bild und Masterexemplar. Die Himmelsseiten",
        "geben lokale Bedien- und Ablesesätze, keine entzifferten Sternnamen. Genau diese Trennung",
        "macht die Ausgabe als Schreibsystem konsistent, ohne jedes sichtbare Zeichen zum Wort zu machen.",
    ])
    (OUT / "FORTY_FIFTH_COMPLETE_TEN_PAGE_HUMAN_EDITION.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")

    summary = {
        "status": "CONSISTENT",
        "counts": {
            "pages": len(page_rows),
            "reading_units": len(unified),
            "prose_statements": len(prose),
            "astro_loci": len(astro),
            "visible_groups": sum(int(row["group_count"]) for row in unified),
            "prose_groups": sum(int(row["group_count"]) for row in unified if row["unit_kind"] == "PROSE_STATEMENT"),
            "astro_groups": sum(int(row["group_count"]) for row in unified if row["unit_kind"] == "ASTRO_LOCUS"),
            "teaching_layers": len(kit_rows),
        },
        "sources": {str(path.relative_to(ROOT)): sha256(path) for path in (PROSE, ASTRO)},
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
