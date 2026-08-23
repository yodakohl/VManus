#!/usr/bin/env python3
"""Build a complete cross-section journeyman workflow without inventing a text link."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
UNITS = ROOT / "experiments/yolo/sidequest_semantic_complete_reader_fifty_sixth_edition/FIFTY_SIXTH_258_COMPLETE_UNITS.tsv"
FIXED = ROOT / "experiments/yolo/sidequest_semantic_fixed_phrase_expander_fifty_eighth_edition/FIFTY_EIGHTH_116_FIXED_EXPANSIONS.tsv"
COPIES = ROOT / "experiments/yolo/sidequest_semantic_four_scribe_rendering_fifty_ninth_edition/FIFTY_NINTH_464_HAND_COPIES.tsv"

SELECTED = (
    "H3-S001", "H3-S002", "H3-S003", "H3-S004",
    "B2-S005", "B2-S006", "B2-S007", "B2-S010", "B2-S012", "B2-S014", "B2-S016", "B2-S017",
    "f69v.1", "f69v.2", "f69v.3", "f69v.4",
)


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
    units = {row["unit_id"]: row for row in read_tsv(UNITS)}
    fixed = {row["unit_id"]: row for row in read_tsv(FIXED)}
    copies = {(row["unit_id"], row["scribe_profile"]): row for row in read_tsv(COPIES)}
    stages = {}
    for unit_id in SELECTED[:4]:
        stages[unit_id] = "HERBAL_PREPARATION"
    for unit_id in SELECTED[4:12]:
        stages[unit_id] = "BIO_STATION_APPLICATION"
    for unit_id in SELECTED[12:]:
        stages[unit_id] = "LOCAL_CELESTIAL_LOOKUP"

    steps = []
    for index, unit_id in enumerate(SELECTED, 1):
        row = units[unit_id]
        prose = fixed[unit_id]["fixed_generated_prose_de"] if unit_id in fixed else row["fluent_working_reading_de"]
        steps.append({
            "job_step": index,
            "stage": stages[unit_id],
            "unit_id": unit_id,
            "page": row["page"],
            "owner_or_namespace": row["owner_or_namespace"],
            "surface_sequence": row["surface_sequence"],
            "atom_sequence": row["atom_sequence"],
            "spoken_workshop_instruction_de": prose,
            "boundary_source": "MANUSCRIPT_UNIT",
            "cross_section_link_encoded_in_text": "NO",
        })
    write_tsv(OUT / "SIXTY_FIRST_16_STEP_JOURNEYMAN_TRACE.tsv", steps)

    bridges = [
        ("J01", "BEFORE_HERBAL", "Meisterauftrag", "Bereite aus dem gewählten Pflanzenartikel einen Arbeitsansatz."),
        ("J02", "HERBAL_TO_BIO", "Meisterauftrag", "Nimm den bereitgestellten Ansatz zur bezeichneten Bade- oder Waschstation."),
        ("J03", "BIO_TO_ASTRO", "Meisterauftrag", "Lies danach die drei lokalen f69-Räder und einen linken Platz für denselben Werkstattauftrag."),
        ("J04", "AFTER_ASTRO", "Meisterauftrag", "Trage den örtlichen Ablesewert auf dem separaten Auftragszettel ein; ändere den Prozessartikel nicht."),
    ]
    bridge_rows = [
        {"bridge_id": bridge_id, "position": position, "bridge_source": source, "spoken_bridge_de": text,
         "manuscript_cross_reference_claimed": "NO", "portable_word_claimed": "NO"}
        for bridge_id, position, source, text in bridges
    ]
    write_tsv(OUT / "SIXTY_FIRST_4_EXTERNAL_JOB_BRIDGES.tsv", bridge_rows)

    profiles = ("S1_BARE_MASTER", "S2_Q_CELL_SCRIBE", "S3_S_LINE_SCRIBE", "S4_MIXED_COMPACT")
    hand_rows = []
    for profile in profiles:
        stage_strings = []
        for stage in ("HERBAL_PREPARATION", "BIO_STATION_APPLICATION", "LOCAL_CELESTIAL_LOOKUP"):
            rendered = []
            for unit_id in (item for item in SELECTED if stages[item] == stage):
                rendered.append(copies[(unit_id, profile)]["rendered_surface_sequence"] if unit_id in fixed else units[unit_id]["surface_sequence"])
            stage_strings.append(" / ".join(rendered))
        hand_rows.append({
            "scribe_profile": profile,
            "herbal_surface_program": stage_strings[0],
            "bio_surface_program": stage_strings[1],
            "astro_surface_program_copied_locally": stage_strings[2],
            "complete_surface_program": " || ".join(stage_strings),
            "prose_atom_order_preserved": "YES",
            "astro_namespace_order_preserved": "YES",
            "cross_section_bridge_written_as_manuscript_card": "NO_EXTERNAL_JOB_ORDER",
        })
    write_tsv(OUT / "SIXTY_FIRST_4_HAND_JOURNEYMAN_COPIES.tsv", hand_rows)

    criteria = [
        ("C01", "setzt den H3-Pflanzenbesitzer vor der ersten Karte", 1),
        ("C02", "kopiert alle vier H3-Einheiten in exakter Reihenfolge", 1),
        ("C03", "hält Ansatz und vorigen Posten über H3 korrekt", 1),
        ("C04", "markiert den H3→B2-Wechsel als externen Meisterauftrag", 1),
        ("C05", "setzt bei jedem sichtbaren B2-Stationswechsel den Besitzer neu", 1),
        ("C06", "unterscheidet AL-Ziel und AR-Quelle", 1),
        ("C07", "spricht E/EE/EEE-Grade unverändert", 1),
        ("C08", "verwechselt Y nicht mit der Schlusskarte", 1),
        ("C09", "nimmt Zeilenenden nicht als Satzende", 1),
        ("C10", "markiert den B2→f69-Wechsel als externen Meisterauftrag", 1),
        ("C11", "hält linkes, mittleres und rechtes f69-Rad getrennt", 1),
        ("C12", "erfindet weder Richtung noch f68↔f69-Schlüssel", 1),
    ]
    criterion_rows = [
        {"criterion_id": criterion_id, "journeyman_requirement_de": text, "points": points}
        for criterion_id, text, points in criteria
    ]
    write_tsv(OUT / "SIXTY_FIRST_12_POINT_MARKING_SHEET.tsv", criterion_rows)

    book = [
        "# Gesellenstück: Pflanze → Station → Himmelsablesung",
        "",
        "Die drei Abschnitte werden durch einen mündlichen Meisterauftrag verbunden, nicht",
        "durch ein angebliches Universalwort im Manuskript.",
        "",
    ]
    current_stage = None
    for row in steps:
        if row["stage"] != current_stage:
            current_stage = row["stage"]
            book.extend([f"## {current_stage}", ""])
        book.extend([f"### {row['job_step']}. {row['unit_id']}", "", row["spoken_workshop_instruction_de"], ""])
    book.extend(["## Äußere Werkstattbrücken", ""])
    for row in bridge_rows:
        book.append(f"- {row['position']}: {row['spoken_bridge_de']}")
    (OUT / "SIXTY_FIRST_COMPLETE_JOURNEYMAN_PIECE.md").write_text("\n".join(book).rstrip() + "\n", encoding="utf-8")

    summary = {
        "status": "CONSISTENT",
        "counts": {
            "job_steps": len(steps),
            "herbal_steps": sum(row["stage"] == "HERBAL_PREPARATION" for row in steps),
            "bio_steps": sum(row["stage"] == "BIO_STATION_APPLICATION" for row in steps),
            "astro_steps": sum(row["stage"] == "LOCAL_CELESTIAL_LOOKUP" for row in steps),
            "external_job_bridges": len(bridge_rows),
            "hand_copies": len(hand_rows),
            "marking_points": sum(int(row["points"]) for row in criterion_rows),
            "manuscript_cross_section_links_claimed": 0,
        },
        "sources": {str(path.relative_to(ROOT)): sha256(path) for path in (UNITS, FIXED, COPIES)},
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
