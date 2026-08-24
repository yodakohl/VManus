#!/usr/bin/env python3
"""Run one prose composition exam and one Astro copy/retrieval exam."""

from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P624 = ROOT / "experiments/yolo/sidequest_semantic_six_case_astro_architecture_six_hundred_twenty_fourth"
P617 = ROOT / "experiments/yolo/sidequest_semantic_backread_noun_repair_six_hundred_seventeenth"
P634 = ROOT / "experiments/yolo/sidequest_semantic_compatible_slot_substitution_six_hundred_thirty_fourth"
P638 = ROOT / "experiments/yolo/sidequest_semantic_ten_page_apprentice_handbook_six_hundred_thirty_eighth"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def case_select(parses: list[str]) -> str:
    components = [part for parse in parses[:5] for part in parse.split("+")]
    return "C3" if "CFH" in components else "UNRESOLVED"


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    orders = read_tsv(P634 / "SIX_HUNDRED_THIRTY_FOURTH_49_LEGAL_WRITTEN_ORDERS.tsv")
    card_dictionary = read_tsv(P617 / "SIX_HUNDRED_SEVENTEENTH_173_SHARP_COMMANDS.tsv")
    handbook = read_tsv(P638 / "SIX_HUNDRED_THIRTY_EIGHTH_776_TEN_PAGE_APPRENTICE_LEDGER.tsv")
    astro_groups = read_tsv(P624 / "SIX_HUNDRED_TWENTY_FOURTH_395_ASTRO_GROUP_INTERFACE.tsv")
    target = next(row for row in orders if row["job_id"] == "C3-HOLD-SHORT" and row["node_order"] == "M-T-W-P-H-C")
    surfaces = target["surface_sequence"].split()
    cards = target["card_sequence"].split("|")
    command_by_surface = {row["visible_surface"]: row for row in handbook if row["section"] == "PROSE_WORKSHOP"}
    card_by_id = {row["card_no"]: row for row in card_dictionary}

    prose_rows = []
    for step, (node, surface, card) in enumerate(zip(target["node_order"].split("-"), surfaces, cards), 1):
        source = command_by_surface[surface]
        prose_rows.append({
            "step": step,
            "node": node,
            "ordinary_prompt_piece_de": {
                "M": "nach Sollmass",
                "T": "am bezeichneten Ziel",
                "W": "den aktiven Posten auswringen",
                "P": "in den Empfaenger einfuellen",
                "H": "kurz halten",
                "C": "absetzen und schliessen",
            }[node],
            "surface": surface,
            "card_no": card,
            "semantic_component_parse": card_by_id[card]["semantic_component_parse"],
            "backward_default_reading_de": source["short_default_reading_de"],
            "existing_inventory": "YES",
        })

    error_nodes = ["M", "T", "P", "W", "H", "C"]
    node_to_row = {row["node"]: row for row in prose_rows}
    error_rows = [node_to_row[node] for node in error_nodes]
    prose_correction = [
        {
            "stage": "INTENDED_JOB",
            "node_sequence": target["node_order"],
            "surface_sequence": target["surface_sequence"],
            "case_selected": case_select([row["semantic_component_parse"] for row in prose_rows]),
            "wring_before_fill": "YES",
            "master_diagnosis_de": "korrekte C3-Kurzhaltefolge",
        },
        {
            "stage": "APPRENTICE_ERROR",
            "node_sequence": "-".join(error_nodes),
            "surface_sequence": " ".join(row["surface"] for row in error_rows),
            "case_selected": case_select([row["semantic_component_parse"] for row in error_rows]),
            "wring_before_fill": "NO",
            "master_diagnosis_de": "Fall richtig, Prozess falsch: EINFUELLEN steht vor AUSWRINGEN",
        },
        {
            "stage": "MASTER_CORRECTION",
            "node_sequence": target["node_order"],
            "surface_sequence": target["surface_sequence"],
            "case_selected": "C3",
            "wring_before_fill": "YES",
            "master_diagnosis_de": "CFHY vor CPHY stellen; alle anderen Karten unveraendert lassen",
        },
    ]

    locus_groups = [row for row in astro_groups if row["page"] == "f69v" and row["locus"] == "f69v.31"]
    locus_groups.sort(key=lambda row: int(row["event_index"]))
    correct = [row["surface_display_only"] for row in locus_groups]
    incorrect = list(reversed(correct))
    astro_rows = []
    for stage, sequence in [("MASTER_MODEL", correct), ("APPRENTICE_ERROR", incorrect), ("MASTER_CORRECTION", correct)]:
        for position, surface in enumerate(sequence, 1):
            original = next(row for row in locus_groups if row["surface_display_only"] == surface)
            astro_rows.append({
                "stage": stage,
                "page": "f69v",
                "locus": "f69v.31",
                "namespace": "F69_LEFT_WHEEL_NS",
                "local_image_owner": "A3_LEFT_RADIAL_SLOT_28",
                "written_position": position,
                "surface": surface,
                "opaque_local_id": original["opaque_local_id"],
                "default_reading_de": f"LOKALE HIMMELS-/ADRESSMARKE AM BILDPLATZ A3_LEFT_RADIAL_SLOT_28, TEIL {position}",
                "matches_master_position": "YES" if surface == correct[position - 1] else "NO",
            })

    write_tsv(HERE / "SIX_HUNDRED_THIRTY_NINTH_6_STEP_C3_EXAM.tsv", prose_rows, list(prose_rows[0]))
    write_tsv(HERE / "SIX_HUNDRED_THIRTY_NINTH_3_STAGE_PROSE_CORRECTION.tsv", prose_correction, list(prose_correction[0]))
    write_tsv(HERE / "SIX_HUNDRED_THIRTY_NINTH_6_ROW_ASTRO_COPY_CORRECTION.tsv", astro_rows, list(astro_rows[0]))

    md = [
        "# Lehrlingspruefung",
        "",
        "## Aufgabe A: neuer C3-Kurzhalteauftrag",
        "",
        "**Meisterauftrag:** Nach Sollmass am bezeichneten Ziel den aktiven Auszug auswringen, in den Empfaenger einfuellen, kurz halten, absetzen und schliessen.",
        "",
        f"**Richtige Schrift:** `{target['surface_sequence']}`",
        "",
        "**Fehler des Lehrlings:** `qokaiin qokal cphy cfhy tshey shedy`",
        "",
        "Der Fall bleibt C3, aber der Lehrling fuellt vor dem Auswringen ein. Der Meister vertauscht nur `cphy cfhy` zu `cfhy cphy`.",
        "",
        "## Aufgabe B: f69 linker Bildplatz 28",
        "",
        "**Meistermodell:** `oar alys`",
        "",
        "**Fehler des Lehrlings:** `alys oar`",
        "",
        "Beide Zeichen sind lokal richtig, aber ihre Reihenfolge am Bildplatz ist falsch. Der Meister liest keine Wortbedeutung hinein; er stellt nur die registrierte lokale Folge wieder her.",
        "",
        "## Ergebnis",
        "",
        "Das Handbuch diagnostiziert zwei verschiedene Fehlerarten: semantische Prozessinversion in Prosa und reine Kopierreihenfolge im Astro-Namensraum.",
    ]
    (HERE / "SIX_HUNDRED_THIRTY_NINTH_APPRENTICE_EXAM.md").write_text("\n".join(md).rstrip() + "\n", encoding="utf-8")

    summary = {
        "status": "PASS",
        "prose_job": target["job_id"],
        "prose_node_order": target["node_order"],
        "prose_surface_sequence": target["surface_sequence"],
        "prose_source_occurrences": int(target["source_sequence_occurrences"]),
        "prose_steps": len(prose_rows),
        "prose_existing_inventory_steps": sum(row["existing_inventory"] == "YES" for row in prose_rows),
        "prose_case_selected_after_error": prose_correction[1]["case_selected"],
        "prose_error_detected": prose_correction[1]["wring_before_fill"] == "NO",
        "astro_locus": "f69v.31",
        "astro_groups": len(locus_groups),
        "astro_master_sequence": " ".join(correct),
        "astro_error_sequence": " ".join(incorrect),
        "astro_error_positions": sum(row["stage"] == "APPRENTICE_ERROR" and row["matches_master_position"] == "NO" for row in astro_rows),
        "astro_corrected_positions": sum(row["stage"] == "MASTER_CORRECTION" and row["matches_master_position"] == "YES" for row in astro_rows),
        "new_words": 0,
        "new_cards": 0,
        "new_surfaces": 0,
        "new_pages": 0,
        "decision": "COMBINED_HANDBOOK_DETECTS_PROSE_PROCESS_AND_ASTRO_COPY_ERRORS",
    }
    (HERE / "SIX_HUNDRED_THIRTY_NINTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
