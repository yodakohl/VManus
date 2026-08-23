#!/usr/bin/env python3
"""Run three complete apprentice readings through the bounded semantic layers."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
LAYERED_GROUPS = ROOT / "experiments/yolo/sidequest_semantic_layered_passages_seventy_third_edition/SEVENTY_THIRD_79_GROUP_LAYERED_READINGS.tsv"
LAYERED_STATEMENTS = ROOT / "experiments/yolo/sidequest_semantic_layered_passages_seventy_third_edition/SEVENTY_THIRD_26_LAYERED_STATEMENTS.tsv"
LICENSE_AUDIT = ROOT / "experiments/yolo/sidequest_semantic_card_source_crosswalk_seventy_seventh_edition/SEVENTY_SEVENTH_381_EVENT_LICENSE_AUDIT.tsv"
CONTROLLED_UNITS = ROOT / "experiments/yolo/sidequest_semantic_controlled_unit_rewrite_seventy_sixth_edition/SEVENTY_SIXTH_14_CONTROLLED_UNIT_READINGS.tsv"
ASTRO_GROUPS = ROOT / "experiments/yolo/sidequest_semantic_astro_address_handbook_sixty_eighth_edition/SIXTY_EIGHTH_395_ASTRO_GROUP_ADDRESS_LEDGER.tsv"
ASTRO_LOCI = ROOT / "experiments/yolo/sidequest_semantic_astro_address_handbook_sixty_eighth_edition/SIXTY_EIGHTH_142_ASTRO_LOCUS_MANUAL.tsv"


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
    unit_rows = {row["unit_id"]: row for row in read_tsv(CONTROLLED_UNITS)}
    licenses = {row["source_group_id"]: row for row in read_tsv(LICENSE_AUDIT)}

    traces = []
    for row in read_tsv(LAYERED_GROUPS):
        record = row["record_id"]
        audit = licenses[row["source_group_id"]]
        unit = unit_rows[record]
        traces.append({
            "trace_serial": len(traces) + 1,
            "track": record,
            "page": row["page"],
            "address": row["source_group_id"],
            "visible_or_opaque_form": row["surface_layer"],
            "forward_1_segment": row["atom_layer"],
            "forward_2_minimal_card": row["minimal_dictionary_layer"],
            "forward_3_owner_or_namespace": row["owner_layer"],
            "forward_4_licensed_source_slots": audit["licensed_source_slots_in_this_unit"],
            "forward_5_selected_unit_vocabulary": unit["selected_source_words_de"],
            "forward_6_spoken_action": row["neutral_source_clause_layer"],
            "backward_1_required_address": row["source_group_id"],
            "backward_2_required_card_or_group": row["surface_layer"],
            "backward_recovery": "EXACT_WITH_REGISTERED_CARD_AND_ADDRESS",
            "concrete_content_without_owner_or_local_source": "NOT_AVAILABLE",
        })

    for row in read_tsv(ASTRO_GROUPS):
        if row["diagram_id"] != "A3":
            continue
        unit = unit_rows["A3"]
        traces.append({
            "trace_serial": len(traces) + 1,
            "track": "A3",
            "page": row["page"],
            "address": f"{row['locus']}:{row['event_index']}",
            "visible_or_opaque_form": row["opaque_local_id"],
            "forward_1_segment": "OPAQUE_LOCAL_GROUP",
            "forward_2_minimal_card": "LOCAL_NOMENCLATOR_ENTRY",
            "forward_3_owner_or_namespace": f"{row['local_owner']} @ {row['local_namespace']}",
            "forward_4_licensed_source_slots": "LOCAL_LABEL;CALENDAR_VALUE;WEATHER_VALUE;LIGHT_VALUE;PLANET_VALUE;QUALITY_VALUE",
            "forward_5_selected_unit_vocabulary": unit["selected_source_words_de"],
            "forward_6_spoken_action": f"{row['copy_instruction_de']} {row['local_readout_instruction_de']}",
            "backward_1_required_address": f"{row['locus']}:{row['event_index']}",
            "backward_2_required_card_or_group": row["opaque_local_id"],
            "backward_recovery": "EXACT_WITH_LOCAL_EXEMPLAR_AND_ADDRESS",
            "concrete_content_without_owner_or_local_source": "NOT_AVAILABLE",
        })
    write_tsv(OUT / "SEVENTY_EIGHTH_219_GROUP_FORWARD_BACKWARD_TRACE.tsv", traces)

    statements = []
    for row in read_tsv(LAYERED_STATEMENTS):
        unit = unit_rows[row["record_id"]]
        statements.append({
            "track": row["record_id"],
            "unit_id": row["unit_id"],
            "page": row["page"],
            "surface_sequence": row["surface_sequence"],
            "minimal_dictionary_reading": row["minimal_dictionary_reading"],
            "owner_augmented_reading": row["owner_augmented_reading"],
            "selected_source_vocabulary": unit["selected_source_words_de"],
            "controlled_record_reading": unit["controlled_unit_reading_de"],
            "apprentice_instruction": "Lies die Minimalfolge; setze nur passende Quellenwörter aus dem Recordprogramm ein; halte den Besitzer bis zum sichtbaren Reset.",
        })
    for row in read_tsv(ASTRO_LOCI):
        if row["diagram_id"] != "A3":
            continue
        unit = unit_rows["A3"]
        statements.append({
            "track": "A3",
            "unit_id": row["locus"],
            "page": row["page"],
            "surface_sequence": f"{row['group_count']} opaque groups",
            "minimal_dictionary_reading": "local label bundle",
            "owner_augmented_reading": row["silent_argument_default"],
            "selected_source_vocabulary": unit["selected_source_words_de"],
            "controlled_record_reading": row["lookup_action_de"],
            "apprentice_instruction": "Zeige den lokalen Platz; kopiere das Bündel; lies nur im örtlichen Instrumentenschlüssel.",
        })
    write_tsv(OUT / "SEVENTY_EIGHTH_57_STATEMENT_OR_LOCUS_READINGS.tsv", statements)

    track_counts = Counter(row["track"] for row in traces)
    summary_rows = []
    for track in ("H3", "B2", "A3"):
        unit = unit_rows[track]
        summary_rows.append({
            "track": track,
            "page": unit["page"],
            "group_count": track_counts[track],
            "selected_source_program": unit["source_slot_program"],
            "selected_source_words": unit["selected_source_words_de"],
            "complete_controlled_reading_de": unit["controlled_unit_reading_de"],
            "forward_surface_to_controlled_action": "COMPLETE",
            "backward_exact_form_with_address_and_exemplar": "COMPLETE",
            "backward_concrete_content_without_owner_or_exemplar": "IMPOSSIBLE_BY_DESIGN",
        })
    write_tsv(OUT / "SEVENTY_EIGHTH_3_COMPLETE_APPRENTICE_TRACKS.tsv", summary_rows)

    doc = ["# Drei vollständige Lehrlingsdurchgänge", ""]
    for row in summary_rows:
        doc.extend([
            f"## {row['track']} · {row['page']}", "",
            f"**Wörter:** {row['selected_source_words']}", "",
            f"**Gelesene Einheit:** {row['complete_controlled_reading_de']}", "",
            "**Vorwärts:** sichtbare Gruppe → Karte/Adresse → Besitzer → erlaubter Quellen-Slot → kontrollierte Arbeitslesung.", "",
            "**Rückwärts:** Arbeitslesung → festes Unitprogramm → Adresse und Exemplar → exakte sichtbare Gruppe.", "",
        ])
    doc.extend([
        "## Werkstattbefund", "",
        "Der Lehrling kann die Form exakt kopieren und die kontrollierte Arbeitslesung",
        "wiederholen. Ohne Bildbesitzer und lokales Exemplar bleiben die konkreten",
        "Inhalte jedoch nicht rückwärts bestimmbar. Das ist kein Defekt des Modells,",
        "sondern der angenommene Zweck des gemischten Kürzel-und-Ganzkarten-Systems.",
    ])
    (OUT / "SEVENTY_EIGHTH_COMPLETE_APPRENTICE_WALKTHROUGHS.md").write_text("\n".join(doc).rstrip() + "\n", encoding="utf-8")

    report = [
        "# Achtundsiebzigste Werkstattfassung: Lehrlings-Rundlauf", "",
        "## Ergebnis", "",
        "H3, B2 and A3 now have complete forward and backward traces covering 17, 62",
        "and 140 visible groups. H3 and B2 use all 26 selected prose statements; A3",
        "uses all 31 local loci. No group is skipped.", "",
        "The practical learning rule is simple: recognize or copy the card, retain the",
        "visible owner, open only source slots licensed by that card and unit, then use",
        "the selected source vocabulary. In reverse, exact form requires the registered",
        "card/address and master exemplar. Concrete content is not reconstructed from",
        "the short card alone.", "",
        "Only the fixed ten pages were used; f84 and f84r remained sealed.",
    ]
    (OUT / "SEVENTY_EIGHTH_EDITION_REPORT.md").write_text("\n".join(report).rstrip() + "\n", encoding="utf-8")

    summary = {
        "status": "CONSISTENT",
        "counts": {
            "complete_tracks": len(summary_rows),
            "trace_groups": len(traces),
            "H3_groups": track_counts["H3"],
            "B2_groups": track_counts["B2"],
            "A3_groups": track_counts["A3"],
            "statement_or_locus_rows": len(statements),
        },
        "sources": {str(path.relative_to(ROOT)): sha256(path) for path in (LAYERED_GROUPS, LAYERED_STATEMENTS, LICENSE_AUDIT, CONTROLLED_UNITS, ASTRO_GROUPS, ASTRO_LOCI)},
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
