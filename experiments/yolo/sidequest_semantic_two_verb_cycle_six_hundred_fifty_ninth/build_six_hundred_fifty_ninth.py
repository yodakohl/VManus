#!/usr/bin/env python3
"""Combine OK=ANSETZEN and CHD=UMSETZEN into a two-verb workshop cycle."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P637 = ROOT / "experiments/yolo/sidequest_semantic_complete_surface_curriculum_six_hundred_thirty_seventh"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def has_ok(row: dict[str, str]) -> bool:
    return "OK" in row["semantic_component_parse"].split("+")


def has_chd(row: dict[str, str]) -> bool:
    return "CHD" in row["semantic_component_parse"].split("+")


def verb_token(row: dict[str, str]) -> str:
    if has_ok(row) and has_chd(row):
        return "FUSED_SET_TRANSFER_CLOSE"
    if has_ok(row):
        return "SET"
    if has_chd(row):
        return "TRANSFER"
    raise ValueError(row["event_id"])


def cycle_class(tokens: list[str]) -> str:
    if tokens == ["FUSED_SET_TRANSFER_CLOSE"]:
        return "FUSED_SHORTCUT"
    if tokens in (["SET", "TRANSFER"], ["TRANSFER", "SET"]):
        return "SINGLE_HANDOFF"
    if tokens in (["SET", "TRANSFER", "SET"], ["TRANSFER", "SET", "TRANSFER"]):
        return "ALTERNATING_CYCLE"
    return "EXTENDED_RECONFIGURATION_CHAIN"


RULES = [
    ("T01", "READY", "SET", "CONFIGURED", "Posten, Menge, Ziel oder Dauer ansetzen"),
    ("T02", "CONFIGURED", "TRANSFER", "TRANSFERRED_ACTIVE", "gesetzten Posten umsetzen oder weiterleiten"),
    ("T03", "TRANSFERRED_ACTIVE", "SET", "RECONFIGURED", "nach dem Umsetzen eine neue Einstellung ansetzen"),
    ("T04", "RECONFIGURED", "TRANSFER", "TRANSFERRED_ACTIVE", "erneut umsetzen; der Zyklus darf wechseln"),
    ("T05", "READY|CONFIGURED", "FUSED_SET_TRANSFER_CLOSE", "CLOSED", "ansetzen, umsetzen und in derselben Karte schliessen"),
    ("T06", "ANY_ACTIVE", "SET_CLOSE|TRANSFER_CLOSE", "CLOSED", "lizenzierte Schlussvariante beendet die Aussage"),
]


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    events = read_tsv(P637 / "SIX_HUNDRED_THIRTY_SEVENTH_381_COMPLETE_APPRENTICE_LEDGER.tsv")
    by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for event in events:
        by_statement[event["statement_id"]].append(event)

    union_events = [row for row in events if has_ok(row) or has_chd(row)]
    joint = {
        sid: rows
        for sid, rows in by_statement.items()
        if any(has_ok(row) for row in rows) and any(has_chd(row) for row in rows)
    }
    statement_rows = []
    transition_rows = []
    fused_rows = []
    precedence = Counter()
    for sid, statement in joint.items():
        roots = [row for row in statement if has_ok(row) or has_chd(row)]
        tokens = [verb_token(row) for row in roots]
        ok_positions = [i for i, row in enumerate(statement) if has_ok(row)]
        chd_positions = [i for i, row in enumerate(statement) if has_chd(row)]
        for i in ok_positions:
            for j in chd_positions:
                precedence["FUSED_SAME_CARD" if i == j else "SET_BEFORE_TRANSFER" if i < j else "TRANSFER_BEFORE_SET"] += 1
        for left, right in zip(statement, statement[1:]):
            if has_ok(left) and not has_chd(left) and has_chd(right) and not has_ok(right):
                transition = "SET_TO_TRANSFER"
            elif has_chd(left) and not has_ok(left) and has_ok(right) and not has_chd(right):
                transition = "TRANSFER_TO_SET"
            else:
                continue
            transition_rows.append({
                "statement_id": sid,
                "page": left["page"],
                "transition": transition,
                "left_event": left["event_id"],
                "left_surface": left["surface"],
                "left_reading_de": left["standard_command_de"],
                "right_event": right["event_id"],
                "right_surface": right["surface"],
                "right_reading_de": right["standard_command_de"],
            })
        for row in roots:
            if has_ok(row) and has_chd(row):
                fused_rows.append({
                    "event_id": row["event_id"],
                    "statement_id": sid,
                    "page": row["page"],
                    "card_no": row["card_no"],
                    "surface": row["surface"],
                    "component_recipe": row["semantic_component_parse"],
                    "reading_de": row["standard_command_de"],
                    "statement_final": "YES" if statement[-1]["event_id"] == row["event_id"] else "NO",
                })
        statement_rows.append({
            "statement_id": sid,
            "page": statement[0]["page"],
            "record": statement[0]["record"],
            "statement_events": len(statement),
            "root_events": len(roots),
            "verb_skeleton": ">".join(tokens),
            "cycle_class": cycle_class(tokens),
            "root_surfaces": " ".join(row["surface"] for row in roots),
            "root_readings_de": " -> ".join(row["standard_command_de"] for row in roots),
            "full_surface": " ".join(row["surface"] for row in statement),
            "full_card_reading_de": " / ".join(row["standard_command_de"] for row in statement),
        })

    pattern_counts = Counter(row["verb_skeleton"] for row in statement_rows)
    pattern_rows = [
        {
            "verb_skeleton": pattern,
            "statements": count,
            "statement_ids": "|".join(row["statement_id"] for row in statement_rows if row["verb_skeleton"] == pattern),
        }
        for pattern, count in sorted(pattern_counts.items(), key=lambda item: (-item[1], item[0]))
    ]
    rule_rows = [
        {"rule_id": rid, "from_state": source, "verb": verb, "to_state": target, "workshop_rule_de": reading}
        for rid, source, verb, target, reading in RULES
    ]

    write_tsv(HERE / "SIX_HUNDRED_FIFTY_NINTH_18_JOINT_STATEMENT_TRACES.tsv", statement_rows, list(statement_rows[0]))
    write_tsv(HERE / "SIX_HUNDRED_FIFTY_NINTH_11_IMMEDIATE_TRANSITIONS.tsv", transition_rows, list(transition_rows[0]))
    write_tsv(HERE / "SIX_HUNDRED_FIFTY_NINTH_5_FUSED_SHORTCUTS.tsv", fused_rows, list(fused_rows[0]))
    write_tsv(HERE / "SIX_HUNDRED_FIFTY_NINTH_10_VERB_SKELETONS.tsv", pattern_rows, list(pattern_rows[0]))
    write_tsv(HERE / "SIX_HUNDRED_FIFTY_NINTH_6_CYCLE_RULES.tsv", rule_rows, list(rule_rows[0]))

    summary = {
        "status": "PASS",
        "union_card_types": len({row["card_no"] for row in union_events}),
        "union_events": len(union_events),
        "overlap_fused_events": sum(has_ok(row) and has_chd(row) for row in union_events),
        "joint_statements": len(statement_rows),
        "events_in_joint_statements": sum(int(row["statement_events"]) for row in statement_rows),
        "root_events_in_joint_statements": sum(int(row["root_events"]) for row in statement_rows),
        "verb_skeleton_types": len(pattern_rows),
        "immediate_set_to_transfer": sum(row["transition"] == "SET_TO_TRANSFER" for row in transition_rows),
        "immediate_transfer_to_set": sum(row["transition"] == "TRANSFER_TO_SET" for row in transition_rows),
        "pairwise_set_before_transfer": precedence["SET_BEFORE_TRANSFER"],
        "pairwise_transfer_before_set": precedence["TRANSFER_BEFORE_SET"],
        "fused_same_card": precedence["FUSED_SAME_CARD"],
        "closed_union_events": sum("SCHLUSS" in row["standard_command_de"] for row in union_events),
        "decision": "SET_AND_TRANSFER_FORM_A_BIDIRECTIONAL_RECONFIGURATION_CYCLE_NOT_FIXED_PRECEDENCE",
    }
    (HERE / "SIX_HUNDRED_FIFTY_NINTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
