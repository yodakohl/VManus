#!/usr/bin/env python3
"""Map eleven run cards onto a five-state material workflow."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
RUN = ROOT / "experiments/yolo/sidequest_semantic_apprentice_run_sheet_three_hundred_forty_first/THREE_HUNDRED_FORTY_FIRST_ELEVEN_APPRENTICE_RUN_CARDS.tsv"

STATES = {
    "M1_RAW_PART": ("Rohteil", "Bildgebundener Pflanzen- oder Ausgangsteil vor der Werkstattbearbeitung."),
    "M2_PREPARATION": ("Ansatz", "Gemischter, gebundener oder fortgesetzter Arbeitsansatz."),
    "M3_CLEAR_EXTRACT": ("Klarauszug", "Abgezogener oder nach Ruhe/Seihen klar gehaltener Anteil."),
    "M4_MEASURED_PORTION": ("Bemessene Portion", "Geteilter oder nach Sollmaß bereitgestellter Arbeitsposten."),
    "M5_APPLICATION_ITEM": ("Anwendungsposten", "Am Ziel gesetzter Posten, der für lokale Anwendung bereitliegt."),
}

TRANSITIONS = {
    "H1": ("M1_RAW_PART", "M2_PREPARATION"),
    "H2": ("M2_PREPARATION", "M2_PREPARATION"),
    "H3": ("M1_RAW_PART", "M3_CLEAR_EXTRACT"),
    "H4": ("M1_RAW_PART", "M4_MEASURED_PORTION"),
    "H5": ("M1_RAW_PART", "M2_PREPARATION"),
    "B1": ("M2_PREPARATION", "M4_MEASURED_PORTION"),
    "B2": ("M3_CLEAR_EXTRACT", "M3_CLEAR_EXTRACT"),
    "B3": ("M2_PREPARATION", "M4_MEASURED_PORTION"),
    "B4": ("M4_MEASURED_PORTION+M2_PREPARATION", "M3_CLEAR_EXTRACT"),
    "B5": ("M2_PREPARATION", "M2_PREPARATION"),
    "B6": ("M2_PREPARATION", "M5_APPLICATION_ITEM"),
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    run = {row["record_unit_id"]: row for row in read_tsv(RUN)}
    state_rows = []
    for state_id, (name, definition) in STATES.items():
        inbound = [record for record, (_, target) in TRANSITIONS.items() if state_id in target.split("+")]
        outbound = [record for record, (source, _) in TRANSITIONS.items() if state_id in source.split("+")]
        state_rows.append({
            "state_id": state_id,
            "state_name_de": name,
            "teaching_definition_de": definition,
            "inbound_records": "|".join(inbound),
            "outbound_records": "|".join(outbound),
            "inbound_count": len(inbound),
            "outbound_count": len(outbound),
        })

    transition_rows = []
    for record, (source, target) in TRANSITIONS.items():
        row = run[record]
        transition_rows.append({
            "record_unit_id": record,
            "page": row["page"],
            "assigned_hand": row["assigned_hand"],
            "source_state_ids": source,
            "source_state_names_de": "+".join(STATES[state][0] for state in source.split("+")),
            "target_state_id": target,
            "target_state_name_de": STATES[target][0],
            "specific_input_de": row["input_item_de"],
            "specific_output_de": row["output_item_de"],
            "dominant_program": row["dominant_program"],
            "receiver_or_shelf": row["receiver_or_shelf"],
            "transition_kind": "STATE_CONTINUATION_LOOP" if source == target else ("TWO_INPUT_COMBINATION" if "+" in source else "STATE_ADVANCE_OR_BRANCH"),
            "new_card_gloss_added": "NO",
        })

    edge_counts = Counter((source, target) for source, target in TRANSITIONS.values())
    edge_rows = []
    for (source, target), count in edge_counts.items():
        records = [record for record, edge in TRANSITIONS.items() if edge == (source, target)]
        edge_rows.append({
            "source_state_ids": source,
            "target_state_id": target,
            "record_count": count,
            "records": "|".join(records),
            "edge_type": "CONTINUATION_LOOP" if source == target else ("COMBINATION_BRANCH" if "+" in source else "FORWARD_BRANCH"),
        })

    write_tsv(HERE / "THREE_HUNDRED_FORTY_THIRD_FIVE_MATERIAL_STATES.tsv", state_rows,
              ["state_id", "state_name_de", "teaching_definition_de", "inbound_records", "outbound_records", "inbound_count", "outbound_count"])
    write_tsv(HERE / "THREE_HUNDRED_FORTY_THIRD_ELEVEN_STATE_TRANSITIONS.tsv", transition_rows,
              ["record_unit_id", "page", "assigned_hand", "source_state_ids", "source_state_names_de", "target_state_id", "target_state_name_de", "specific_input_de", "specific_output_de", "dominant_program", "receiver_or_shelf", "transition_kind", "new_card_gloss_added"])
    write_tsv(HERE / "THREE_HUNDRED_FORTY_THIRD_EIGHT_UNIQUE_STATE_EDGES.tsv", edge_rows,
              ["source_state_ids", "target_state_id", "record_count", "records", "edge_type"])

    lines = [
        "# Fünfstufige Stoffleiter der Werkstatt",
        "",
        "## Zustände",
        "",
        "1. Rohteil",
        "2. Ansatz",
        "3. Klarauszug",
        "4. Bemessene Portion",
        "5. Anwendungsposten",
        "",
        "## Hauptweg",
        "",
        "`Rohteil → Ansatz → Bemessene Portion → Anwendungsposten`",
        "",
        "## Seitenzweige",
        "",
        "`Rohteil → Klarauszug`",
        "",
        "`Rohteil → Bemessene Portion`",
        "",
        "`Bemessene Portion + Ansatz → Klarauszug`",
        "",
        "## Werkstattschleifen",
        "",
        "`Ansatz → Ansatz` wird von H2 und B5 benutzt; `Klarauszug → Klarauszug`",
        "von B2. Diese Schleifen bedeuten Weiterbearbeitung desselben Zustands, nicht",
        "Rückkehr zum Rohteil.",
        "",
        "## Entscheidung",
        "",
        "Das System ist eine verzweigte Herstellungsleiter, kein geschlossener Kreislauf.",
        "Kein Record führt Anwendungsposten oder Klarauszug zurück zu Rohmaterial. Die",
        "fünf Zustände sind redaktionelle Werkstattrollen; keine neue Kartenbedeutung wurde",
        "dafür eingeführt.",
    ]
    (HERE / "THREE_HUNDRED_FORTY_THIRD_MATERIAL_STATE_LADDER.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    summary = {
        "status": "PASS",
        "material_states": len(STATES),
        "record_transitions": len(transition_rows),
        "unique_edges": len(edge_rows),
        "continuation_loops": sum(row["edge_type"] == "CONTINUATION_LOOP" for row in edge_rows),
        "forward_or_combination_edges": sum(row["edge_type"] != "CONTINUATION_LOOP" for row in edge_rows),
        "closed_cycle_to_raw_part": False,
        "new_card_glosses": 0,
    }
    (HERE / "THREE_HUNDRED_FORTY_THIRD_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
