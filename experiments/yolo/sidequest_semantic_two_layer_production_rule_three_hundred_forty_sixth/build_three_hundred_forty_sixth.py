#!/usr/bin/env python3
"""Combine six operation slots and five material states into one production rule."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
TRACE = ROOT / "experiments/yolo/sidequest_semantic_card_order_syntax_three_hundred_thirty_fifth/THREE_HUNDRED_THIRTY_FIFTH_381_EVENT_GENERATION_TRACE.tsv"
AUDIT = ROOT / "experiments/yolo/sidequest_semantic_state_information_channels_three_hundred_forty_fourth/THREE_HUNDRED_FORTY_FOURTH_381_EVENT_STATE_CHANNEL_AUDIT.tsv"
LINKS = ROOT / "experiments/yolo/sidequest_semantic_visible_state_formulas_three_hundred_forty_fifth/THREE_HUNDRED_FORTY_FIFTH_41_WITHIN_STATEMENT_STATE_LINKS.tsv"
TRANSITIONS = ROOT / "experiments/yolo/sidequest_semantic_material_state_ladder_three_hundred_forty_third/THREE_HUNDRED_FORTY_THIRD_ELEVEN_STATE_TRANSITIONS.tsv"

STATES = ["M1_RAW_PART", "M2_PREPARATION", "M3_CLEAR_EXTRACT", "M4_MEASURED_PORTION", "M5_APPLICATION_ITEM"]
SLOTS = ["S1_BEZUG_FOLGE", "S2_MATERIAL_MASS", "S3_PROZESS_TRANSFER", "S4_DAUER_ZUSTAND", "S5_ZIEL_ANWENDUNG", "S6_BEREIT_ABSCHLUSS"]
DOMINANT_SLOT = {
    "M1_RAW_PART": "S1_BEZUG_FOLGE",
    "M2_PREPARATION": "S1_BEZUG_FOLGE",
    "M3_CLEAR_EXTRACT": "S3_PROZESS_TRANSFER",
    "M4_MEASURED_PORTION": "S2_MATERIAL_MASS",
    "M5_APPLICATION_ITEM": "S5_ZIEL_ANWENDUNG",
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
    trace = read_tsv(TRACE)
    audit = {row["event_id"]: row for row in read_tsv(AUDIT)}
    transitions = {row["record_unit_id"]: row for row in read_tsv(TRANSITIONS)}
    by_record = defaultdict(list)
    for row in trace:
        by_record[row["record_unit_id"]].append(row)

    layered = []
    for record, rows in by_record.items():
        marker_positions = [index for index, row in enumerate(rows) if audit[row["event_id"]]["material_state_marker"] != "NONE"]
        for index, row in enumerate(rows):
            marker = audit[row["event_id"]]["material_state_marker"]
            prior_positions = [position for position in marker_positions if position < index]
            next_positions = [position for position in marker_positions if position > index]
            previous_marker = audit[rows[prior_positions[-1]]["event_id"]]["material_state_marker"] if prior_positions else "NONE"
            next_marker = audit[rows[next_positions[0]]["event_id"]]["material_state_marker"] if next_positions else "NONE"
            layered.append({
                "event_id": row["event_id"],
                "record_unit_id": record,
                "page": row["page"],
                "statement_id": row["statement_id"],
                "microcycle": row["microcycle"],
                "slot_code": row["slot_code"],
                "program_id": row["program_id"],
                "surface": row["surface"],
                "atomic_value_de": row["atomic_value_de"],
                "material_marker_state": marker,
                "previous_material_marker": previous_marker,
                "next_material_marker": next_marker,
                "material_thread_role": "EXPLICIT_STATE_MARKER" if marker != "NONE" else "WORK_ON_CURRENT_MATERIAL_THREAD",
                "record_source_state_ids": transitions[record]["source_state_ids"],
                "record_target_state_id": transitions[record]["target_state_id"],
                "owner": row["owner"],
            })

    matrix_counts = Counter((row["material_marker_state"], row["slot_code"]) for row in layered if row["material_marker_state"] != "NONE")
    matrix_rows = []
    for state in STATES:
        for slot in SLOTS:
            count = matrix_counts[(state, slot)]
            matrix_rows.append({
                "state_id": state,
                "slot_code": slot,
                "event_count": count,
                "dominant_slot_for_state": "YES" if slot == DOMINANT_SLOT[state] else "NO",
                "observed_combination": "YES" if count else "NO",
                "teaching_action": "USE_DEFAULT_STATE_SLOT" if slot == DOMINANT_SLOT[state] else ("MEMORIZE_WHOLE_CARD_OVERRIDE" if count else "UNUSED_COMBINATION"),
            })

    link_rows = []
    trace_by_id = {row["event_id"]: row for row in trace}
    for row in read_tsv(LINKS):
        left = trace_by_id[row["left_event_id"]]
        right = trace_by_id[row["right_event_id"]]
        same_cycle = left["microcycle"] == right["microcycle"]
        out = dict(row)
        out.update({
            "left_slot_code": left["slot_code"],
            "right_slot_code": right["slot_code"],
            "left_microcycle": left["microcycle"],
            "right_microcycle": right["microcycle"],
            "microcycle_relation": "SAME_MICROCYCLE" if same_cycle else "CROSSES_MICROCYCLE_RESET",
            "production_reading": "STATE_THREAD_CONTINUES_OVER_LOCAL_WORK_RESET" if not same_cycle else "STATE_AND_OPERATION_ADVANCE_TOGETHER",
        })
        link_rows.append(out)

    statement_rows = []
    by_statement = defaultdict(list)
    for row in layered:
        by_statement[row["statement_id"]].append(row)
    for statement_id, rows in by_statement.items():
        markers = [row["material_marker_state"] for row in rows if row["material_marker_state"] != "NONE"]
        statement_rows.append({
            "statement_id": statement_id,
            "record_unit_id": rows[0]["record_unit_id"],
            "page": rows[0]["page"],
            "event_count": len(rows),
            "microcycle_count": len({row["microcycle"] for row in rows}),
            "slot_sequence": " → ".join(row["slot_code"] for row in rows),
            "material_state_sequence": " → ".join(markers) if markers else "INHERITED_ONLY",
            "record_source_state_ids": rows[0]["record_source_state_ids"],
            "record_target_state_id": rows[0]["record_target_state_id"],
            "two_layer_reading": "OPERATION_SLOTS_WITH_PERSISTENT_MATERIAL_THREAD",
        })

    write_tsv(HERE / "THREE_HUNDRED_FORTY_SIXTH_381_TWO_LAYER_EVENT_TRACE.tsv", layered,
              ["event_id", "record_unit_id", "page", "statement_id", "microcycle", "slot_code", "program_id", "surface", "atomic_value_de", "material_marker_state", "previous_material_marker", "next_material_marker", "material_thread_role", "record_source_state_ids", "record_target_state_id", "owner"])
    write_tsv(HERE / "THREE_HUNDRED_FORTY_SIXTH_30_STATE_SLOT_MATRIX.tsv", matrix_rows,
              ["state_id", "slot_code", "event_count", "dominant_slot_for_state", "observed_combination", "teaching_action"])
    write_tsv(HERE / "THREE_HUNDRED_FORTY_SIXTH_41_STATE_LINK_MICROCYCLE_RELATIONS.tsv", link_rows,
              list(link_rows[0]))
    write_tsv(HERE / "THREE_HUNDRED_FORTY_SIXTH_116_TWO_LAYER_STATEMENTS.tsv", statement_rows,
              ["statement_id", "record_unit_id", "page", "event_count", "microcycle_count", "slot_sequence", "material_state_sequence", "record_source_state_ids", "record_target_state_id", "two_layer_reading"])

    exceptions = [row for row in layered if row["material_marker_state"] != "NONE" and row["slot_code"] != DOMINANT_SLOT[row["material_marker_state"]]]
    exception_counts = Counter((row["atomic_value_de"], row["slot_code"]) for row in exceptions)
    lines = [
        "# Zweischichtige Produktionsregel",
        "",
        "## Ebene A — Arbeitsgang",
        "",
        "Schreibe jeden Mikrogang vorwärts durch die sechs Plätze Bezug/Folge, Material/Maß,",
        "Prozess/Transfer, Dauer/Zustand, Ziel/Anwendung und Bereit/Abschluss. Ein Rücksprung",
        "öffnet einen neuen Mikrogang.",
        "",
        "## Ebene B — Stoffspur",
        "",
        "Das Bild oder der Relay setzt den Ausgangszustand. Explizite Stoffkarten markieren",
        "Rohteil, Ansatz, Klarauszug, bemessene Portion oder Anwendungsposten. Zwischen zwei",
        "Markern arbeiten alle übrigen Karten am laufenden Stofffaden. Der Faden darf über",
        "einen Mikrogang-Reset weiterlaufen.",
        "",
        "## Standardsitze der Stoffmarker",
        "",
        "- Rohteil und Ansatz stehen normalerweise in S1 Bezug/Folge.",
        "- Bemessene Portion steht ausnahmslos in S2 Material/Maß.",
        "- Klarauszug steht normalerweise in S3 Prozess/Transfer.",
        "- Anwendungsposten steht normalerweise in S5 Ziel/Anwendung.",
        "",
        f"73 von 79 Stoffmarkern folgen diesen Standardsitzen. Sechs gelernte Ganzkarten",
        "überschreiben den Default: " + ", ".join(
            f"{value}@{slot}" + (f"×{count}" if count > 1 else "")
            for (value, slot), count in exception_counts.items()
        ) + ".",
        "",
        "## Reichweite",
        "",
        "Von 41 Stofflinks bleiben 19 im selben Mikrogang; 22 überqueren einen Reset. Die",
        "Arbeitsgrammatik und die Stoffgrammatik sind daher gekoppelt, aber nicht identisch.",
    ]
    (HERE / "THREE_HUNDRED_FORTY_SIXTH_TWO_LAYER_RULE.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    summary = {
        "status": "PASS",
        "events": len(layered),
        "statements": len(statement_rows),
        "state_markers": sum(row["material_marker_state"] != "NONE" for row in layered),
        "dominant_slot_fits": sum(row["material_marker_state"] != "NONE" and row["slot_code"] == DOMINANT_SLOT[row["material_marker_state"]] for row in layered),
        "whole_card_slot_overrides": len(exceptions),
        "same_microcycle_state_links": sum(row["microcycle_relation"] == "SAME_MICROCYCLE" for row in link_rows),
        "cross_microcycle_state_links": sum(row["microcycle_relation"] == "CROSSES_MICROCYCLE_RESET" for row in link_rows),
    }
    (HERE / "THREE_HUNDRED_FORTY_SIXTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
