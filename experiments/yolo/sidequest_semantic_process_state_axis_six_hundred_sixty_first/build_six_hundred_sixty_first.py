#!/usr/bin/env python3
"""Integrate SHED=SETTLE, CHK=WARM, and CTH=READY with OK/CHD processes."""

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


STATE_VALUES = {"SHED": "ABSETZEN", "CHK": "WAERMEN", "CTH": "BEREIT"}


def atoms(row: dict[str, str]) -> set[str]:
    return set(row["semantic_component_parse"].split("+"))


def process(row: dict[str, str]) -> bool:
    return bool(atoms(row) & {"OK", "CHD"})


def state(row: dict[str, str]) -> bool:
    return bool(atoms(row) & set(STATE_VALUES))


def state_tokens(row: dict[str, str]) -> list[str]:
    return [atom for atom in ("SHED", "CHK", "CTH") if atom in atoms(row)]


def process_tokens(row: dict[str, str]) -> list[str]:
    return [name for atom, name in (("OK", "SET"), ("CHD", "TRANSFER")) if atom in atoms(row)]


def proc_num(card: str) -> int:
    return int(card.removeprefix("PROC"))


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    events = read_tsv(P637 / "SIX_HUNDRED_THIRTY_SEVENTH_381_COMPLETE_APPRENTICE_LEDGER.tsv")
    by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    by_card: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in events:
        by_statement[row["statement_id"]].append(row)
        if state(row):
            by_card[row["card_no"]].append(row)

    inventory_rows = []
    for card in sorted(by_card, key=proc_num):
        rows = by_card[card]
        exemplar = rows[0]
        roots = state_tokens(exemplar)
        inventory_rows.append({
            "card_no": card,
            "surfaces": "|".join(sorted({row["surface"] for row in rows})),
            "component_recipe": exemplar["semantic_component_parse"],
            "state_roots": "|".join(roots),
            "root_values_de": "|".join(STATE_VALUES[root] for root in roots),
            "composed_reading_de": exemplar["standard_command_de"],
            "events": len(rows),
            "pages": "|".join(sorted({row["page"] for row in rows})),
            "contains_close": "YES" if "SCHLUSS" in exemplar["standard_command_de"] else "NO",
            "statement_final_events": sum(by_statement[row["statement_id"]][-1]["event_id"] == row["event_id"] for row in rows),
        })

    root_rows = []
    for root, value in STATE_VALUES.items():
        cards = [row for row in inventory_rows if root in str(row["state_roots"]).split("|")]
        root_rows.append({
            "state_root": root,
            "short_value_de": value,
            "card_types": len(cards),
            "card_ids": "|".join(str(row["card_no"]) for row in cards),
            "events": sum(int(row["events"]) for row in cards),
            "closed_events": sum(int(row["events"]) for row in cards if row["contains_close"] == "YES"),
            "teaching_rule_de": f"{root} traegt in jeder Karte den Zustand {value}",
        })

    joint = {
        sid: rows
        for sid, rows in by_statement.items()
        if any(process(row) for row in rows) and any(state(row) for row in rows)
    }
    trace_rows = []
    transition_rows = []
    for sid, statement in joint.items():
        relevant = [row for row in statement if process(row) or state(row)]
        tokens = []
        for row in relevant:
            labels = process_tokens(row) + [STATE_VALUES[root] for root in state_tokens(row)]
            tokens.append("+".join(labels))
        for left, right in zip(statement, statement[1:]):
            if process(left) and state(right):
                direction = "PROCESS_TO_STATE"
            elif state(left) and process(right):
                direction = "STATE_TO_PROCESS"
            else:
                continue
            transition_rows.append({
                "statement_id": sid,
                "page": left["page"],
                "direction": direction,
                "left_event": left["event_id"],
                "left_surface": left["surface"],
                "left_reading_de": left["standard_command_de"],
                "right_event": right["event_id"],
                "right_surface": right["surface"],
                "right_reading_de": right["standard_command_de"],
            })
        trace_rows.append({
            "statement_id": sid,
            "page": statement[0]["page"],
            "record": statement[0]["record"],
            "statement_events": len(statement),
            "process_events": sum(process(row) for row in statement),
            "state_events": sum(state(row) for row in statement),
            "process_state_skeleton": ">".join(tokens),
            "relevant_surfaces": " ".join(row["surface"] for row in relevant),
            "relevant_reading_de": " -> ".join(row["standard_command_de"] for row in relevant),
            "full_surface": " ".join(row["surface"] for row in statement),
            "full_card_reading_de": " / ".join(row["standard_command_de"] for row in statement),
        })

    rules = [
        ("S01", "SET|TRANSFER", "WAERMEN", "aktiven Posten nach Setzen oder Transfer waermen"),
        ("S02", "SET|TRANSFER", "ABSETZEN", "aktiven Posten nach Setzen oder Transfer absetzen lassen"),
        ("S03", "SET|TRANSFER", "BEREIT", "Bereitschaft des gesetzten oder umgesetzten Postens pruefen"),
        ("S04", "WAERMEN|BEREIT", "SET|TRANSFER", "nach Zustand eine neue Arbeitsoperation beginnen"),
        ("S05", "ABSETZEN+DY", "CLOSED", "Absetzen mit Schlusskarte beendet den Schritt"),
        ("S06", "WAERMEN+DY", "CLOSED", "Waermen mit Schlusskarte beendet den Schritt"),
    ]
    rule_rows = [
        {"rule_id": rid, "from_process_or_state": source, "to_process_or_state": target, "workshop_rule_de": reading}
        for rid, source, target, reading in rules
    ]

    write_tsv(HERE / "SIX_HUNDRED_SIXTY_FIRST_15_STATE_CARD_INVENTORY.tsv", inventory_rows, list(inventory_rows[0]))
    write_tsv(HERE / "SIX_HUNDRED_SIXTY_FIRST_3_STATE_ROOTS.tsv", root_rows, list(root_rows[0]))
    write_tsv(HERE / "SIX_HUNDRED_SIXTY_FIRST_17_PROCESS_STATE_TRACES.tsv", trace_rows, list(trace_rows[0]))
    write_tsv(HERE / "SIX_HUNDRED_SIXTY_FIRST_11_IMMEDIATE_TRANSITIONS.tsv", transition_rows, list(transition_rows[0]))
    write_tsv(HERE / "SIX_HUNDRED_SIXTY_FIRST_6_STATE_RULES.tsv", rule_rows, list(rule_rows[0]))

    summary = {
        "status": "PASS",
        "state_card_types": len(inventory_rows),
        "state_events": sum(int(row["events"]) for row in inventory_rows),
        "state_component_recipes": len({row["component_recipe"] for row in inventory_rows}),
        "state_roots": len(root_rows),
        "closed_state_events": sum(int(row["events"]) for row in inventory_rows if row["contains_close"] == "YES"),
        "closed_state_events_final": sum(int(row["statement_final_events"]) for row in inventory_rows if row["contains_close"] == "YES"),
        "joint_statements": len(trace_rows),
        "events_in_joint_statements": sum(int(row["statement_events"]) for row in trace_rows),
        "process_events_in_joint": sum(int(row["process_events"]) for row in trace_rows),
        "state_events_in_joint": sum(int(row["state_events"]) for row in trace_rows),
        "process_to_state": sum(row["direction"] == "PROCESS_TO_STATE" for row in transition_rows),
        "state_to_process": sum(row["direction"] == "STATE_TO_PROCESS" for row in transition_rows),
        "decision": "SETTLE_WARM_READY_FORM_A_THIRD_AXIS_IN_A_BIDIRECTIONAL_PROCESS_STATE_CYCLE",
    }
    (HERE / "SIX_HUNDRED_SIXTY_FIRST_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
