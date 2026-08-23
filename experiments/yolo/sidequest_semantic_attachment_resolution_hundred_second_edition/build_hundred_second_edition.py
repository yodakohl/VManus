#!/usr/bin/env python3
"""Resolve the 27 equal-distance attachments with one apprentice convention."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
ATTACHMENTS = ROOT / "experiments/yolo/sidequest_semantic_clause_attachment/COMPLETE_381_ATTACHED_EVENTS.tsv"
ATOMIC = ROOT / "experiments/yolo/sidequest_semantic_atomic_defaults_hundred_first_edition/HUNDRED_FIRST_381_EVENT_ATOMIC_INTERLINEAR.tsv"
STATEMENTS = ROOT / "experiments/yolo/sidequest_semantic_centennial_working_edition/HUNDREDTH_116_STATEMENT_TRANSLATION.tsv"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, fields: list[str], rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    source = read_tsv(ATTACHMENTS)
    atomic_by_serial = {row["event_serial"]: row for row in read_tsv(ATOMIC)}
    statement_source = {row["statement_id"]: row for row in read_tsv(STATEMENTS)}
    by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in source:
        by_statement[row["statement_id"]].append(row)

    resolved: list[dict[str, object]] = []
    ambiguous_rows: list[dict[str, object]] = []
    for statement_id, events in by_statement.items():
        action_indices = [i for i, row in enumerate(events) if row["syntactic_role"] == "ACTION_HEAD"]
        for index, row in enumerate(events):
            previous_action = max((i for i in action_indices if i < index), default=None)
            next_action = min((i for i in action_indices if i > index), default=None)
            prior = events[previous_action] if previous_action is not None else None
            following = events[next_action] if next_action is not None else None
            selected_host = row["attachment_host_event_id"]
            selected_direction = row["attachment_direction"]
            selection_rule = "KEEP_UNAMBIGUOUS_ATTACHMENT"
            alternative = "NONE"
            if row["attachment_ambiguity"] == "EQUAL_DISTANCE":
                alternative = following["event_id"] if following else "NONE"
                if row["syntactic_role"] == "CONTENT_OR_STATE" and following is not None:
                    selected_host = following["event_id"]
                    selected_direction = "FORWARD"
                    selection_rule = "MATERIAL_OR_STATE_BETWEEN_ACTIONS_FEEDS_NEXT_ACTION"
                else:
                    selected_host = prior["event_id"] if prior else row["attachment_host_event_id"]
                    selected_direction = "BACKWARD"
                    selection_rule = "SOURCE_QUANTITY_TARGET_OR_FINAL_RESULT_MODIFIES_COMPLETED_ACTION"
                ambiguous_rows.append({
                    "event_id": row["event_id"],
                    "event_serial": row["event_serial"],
                    "statement_id": statement_id,
                    "page": row["page"],
                    "surface": row["surface_display"],
                    "semantic_atoms": row["corrected_semantic_atoms"],
                    "atomic_default_de": atomic_by_serial[row["event_serial"]]["atomic_default_de"],
                    "previous_action_event": prior["event_id"] if prior else "NONE",
                    "previous_action_head": prior["action_head"] if prior else "NONE",
                    "next_action_event": following["event_id"] if following else "NONE",
                    "next_action_head": following["action_head"] if following else "NONE",
                    "selected_host_event": selected_host,
                    "selected_direction": selected_direction,
                    "discarded_alternative_host": alternative if selected_direction == "BACKWARD" else (prior["event_id"] if prior else "NONE"),
                    "selection_rule": selection_rule,
                })
            resolved.append({
                "event_serial": row["event_serial"],
                "event_id": row["event_id"],
                "statement_id": statement_id,
                "record_unit_id": row["record_unit_id"],
                "page": row["page"],
                "surface": row["surface_display"],
                "master_card_id": row["master_card_id"],
                "semantic_atoms": row["corrected_semantic_atoms"],
                "atomic_default_de": atomic_by_serial[row["event_serial"]]["atomic_default_de"],
                "syntactic_role": row["syntactic_role"],
                "selected_host_event": selected_host,
                "selected_direction": selected_direction,
                "selection_rule": selection_rule,
                "was_equal_distance": "YES" if row["attachment_ambiguity"] == "EQUAL_DISTANCE" else "NO",
            })

    statement_rows: list[dict[str, object]] = []
    resolved_by_statement: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in resolved:
        resolved_by_statement[str(row["statement_id"])].append(row)
    for statement_id, events in sorted(resolved_by_statement.items(), key=lambda item: int(statement_source[item[0]]["statement_order"])):
        source_statement = statement_source[statement_id]
        trace = " | ".join(f"{row['surface']}[{row['atomic_default_de']}→{row['selected_host_event']}]" for row in events)
        statement_rows.append({
            "statement_order": source_statement["statement_order"],
            "statement_id": statement_id,
            "record_unit_id": source_statement["record_unit_id"],
            "page": source_statement["page"],
            "event_count": source_statement["event_count"],
            "equal_distance_resolutions": sum(row["was_equal_distance"] == "YES" for row in events),
            "resolved_attachment_trace": trace,
            "card_near_workshop_reading_de": source_statement["card_near_workshop_reading_de"],
            "concrete_source_expansion_de": source_statement["concrete_source_expansion_de"],
        })

    write_tsv(OUT / "HUNDRED_SECOND_381_RESOLVED_ATTACHMENTS.tsv", list(resolved[0]), sorted(resolved, key=lambda row: int(row["event_serial"])))
    write_tsv(OUT / "HUNDRED_SECOND_27_AMBIGUOUS_DECISIONS.tsv", list(ambiguous_rows[0]), sorted(ambiguous_rows, key=lambda row: int(row["event_serial"])))
    write_tsv(OUT / "HUNDRED_SECOND_116_RESOLVED_STATEMENTS.tsv", list(statement_rows[0]), statement_rows)

    directions = Counter(row["selected_direction"] for row in ambiguous_rows)
    roles = Counter(next(row["syntactic_role"] for row in resolved if row["event_id"] == ambiguous["event_id"]) for ambiguous in ambiguous_rows)
    report = [
        "# Hundertzweite Runde: Die 27 echten Satzanschlüsse", "",
        "## Gewählte Werkstattregel", "",
        "Wenn eine Karte genau zwischen zwei Arbeitsköpfen steht, wird nicht jedes Mal frei",
        "übersetzt. Quelle, Maß, Stufe, Ziel und aktueller Posten hängen rückwärts am gerade",
        "vollzogenen Gang. Ein materieller Posten oder Zustand zwischen zwei Gängen wird",
        "vorwärts zum nächsten Gang genommen. Ein Ergebnis ohne folgenden Gang bleibt beim",
        "vorigen Gang.", "",
        f"Damit sind alle 27 Gleichstandsstellen fest lesbar: {directions['BACKWARD']} rückwärts",
        f"und {directions['FORWARD']} vorwärts. Die 354 bereits eindeutigen Ereignisse bleiben",
        "unverändert. Das Wörterbuch selbst wird dabei nicht angefasst.", "",
        "Die Regel entspricht einer knappen Werkstattnotiz: erst einen Gang setzen, danach",
        "dessen Werte notieren; steht anschließend ein neuer Stoffposten vor dem nächsten",
        "Verb, gehört er zum nächsten Arbeitsgang. So kann ein Lehrling dieselbe Sequenz",
        "ohne improvisierte Satzbedeutungen lesen.", "",
        "Nur die festen Prosaseiten wurden verwendet; f84 und f84r blieben versiegelt.",
    ]
    (OUT / "HUNDRED_SECOND_ATTACHMENT_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    summary = {
        "status": "CONSISTENT", "events": len(resolved), "statements": len(statement_rows),
        "equal_distance_decisions": len(ambiguous_rows), "directions": dict(directions),
        "ambiguous_roles": dict(roles),
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
