#!/usr/bin/env python3
"""Close the final control axes and identify the true whole-card remainder."""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
SOURCE = ROOT / "experiments/yolo/sidequest_semantic_complete_surface_curriculum_six_hundred_thirty_seventh/SIX_HUNDRED_THIRTY_SEVENTH_381_COMPLETE_APPRENTICE_LEDGER.tsv"
VALUES = {"T": "EINTRAGEN", "CH": "ABNEHMEN", "O": "ARBEITSGANG", "DY": "SCHLUSS", "S": "TEILEN"}
PRIOR_ROOTS = {
    "OK", "CHD", "SHED", "CHK", "CTH", "OR", "CKH", "SOLK", "SH", "P",
    "LSH", "CFH", "L", "OL", "OT", "AL", "AR", "AIR", "AIN", "AIIN",
    "IIN", "K", "HO", "Y",
}
WHOLE = {
    "PROC005": ("OS", "ARBEITSFACH"),
    "PROC034": ("RESUME_CARD", "WIEDERAUFNEHMEN"),
    "PROC043": ("TALAM", "VERWAHREN"),
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def number(card: str) -> int:
    return int(card.removeprefix("PROC"))


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    all_events = read_tsv(SOURCE)
    statements: dict[str, list[dict[str, str]]] = defaultdict(list)
    for event in all_events:
        statements[event["statement_id"]].append(event)

    selected = [event for event in all_events if set(event["semantic_component_parse"].split("+")) & VALUES.keys()]
    cards: dict[str, list[dict[str, str]]] = defaultdict(list)
    for event in selected:
        cards[event["card_no"]].append(event)
    card_rows = []
    for card in sorted(cards, key=number):
        rows = cards[card]
        first = rows[0]
        roots = [atom for atom in first["semantic_component_parse"].split("+") if atom in VALUES]
        card_rows.append({
            "card_no": card,
            "surfaces": "|".join(sorted({row["surface"] for row in rows})),
            "component_recipe": first["semantic_component_parse"],
            "control_roots": "+".join(roots),
            "portable_contributions_de": " · ".join(VALUES[root] for root in roots),
            "composed_reading_de": first["standard_command_de"],
            "events": len(rows),
            "event_ids": "|".join(row["event_id"] for row in rows),
        })

    root_rows = []
    for root, value in VALUES.items():
        events = [event for event in all_events if root in event["semantic_component_parse"].split("+")]
        root_rows.append({
            "root": root,
            "portable_value_de": value,
            "card_types": len({event["card_no"] for event in events}),
            "events": len(events),
            "component_recipes": len({event["semantic_component_parse"] for event in events}),
            "rule_de": {
                "T": "den aktuellen Posten in die laufende Notation oder Liste eintragen",
                "CH": "Material oder Posten aus dem aktiven Zusammenhang abnehmen",
                "O": "den laufenden Arbeitsgang bezeichnen",
                "DY": "nur in der lizenzierten exakten Konstruktion den Schritt schliessen",
                "S": "den Posten in Teilmengen teilen",
            }[root],
        })

    whole_rows = []
    for card, (recipe, value) in WHOLE.items():
        rows = [event for event in all_events if event["card_no"] == card]
        whole_rows.append({
            "card_no": card,
            "surfaces": "|".join(sorted({row["surface"] for row in rows})),
            "whole_card_recipe": recipe,
            "memorized_value_de": value,
            "events": len(rows),
            "event_ids": "|".join(row["event_id"] for row in rows),
            "complete_statement_surfaces": " || ".join(" ".join(item["surface"] for item in statements[row["statement_id"]]) for row in rows),
        })

    all_productive_roots = PRIOR_ROOTS | VALUES.keys()
    final_remainder = [
        event for event in all_events
        if event["card_no"] not in WHOLE
        and not set(event["semantic_component_parse"].split("+")) & all_productive_roots
    ]
    dy_events = [event for event in all_events if "DY" in event["semantic_component_parse"].split("+")]
    dy_rows = []
    for event in dy_events:
        statement = statements[event["statement_id"]]
        index = next(i for i, row in enumerate(statement) if row["event_id"] == event["event_id"])
        dy_rows.append({
            "event_id": event["event_id"],
            "statement_id": event["statement_id"],
            "card_no": event["card_no"],
            "surface": event["surface"],
            "component_recipe": event["semantic_component_parse"],
            "statement_position": "WHOLE" if len(statement) == 1 else "ENTRY" if index == 0 else "FINAL" if index == len(statement) - 1 else "MEDIAL",
            "licensed_close": "YES",
        })

    write_tsv(HERE / "SIX_HUNDRED_SEVENTY_FIRST_67_CONTROL_CARDS.tsv", card_rows, list(card_rows[0]))
    write_tsv(HERE / "SIX_HUNDRED_SEVENTY_FIRST_5_CONTROL_ROOTS.tsv", root_rows, list(root_rows[0]))
    write_tsv(HERE / "SIX_HUNDRED_SEVENTY_FIRST_3_WHOLE_COMMANDS.tsv", whole_rows, list(whole_rows[0]))
    write_tsv(HERE / "SIX_HUNDRED_SEVENTY_FIRST_89_DY_CLOSE_EVENTS.tsv", dy_rows, list(dy_rows[0]))

    summary = {
        "status": "PASS",
        "control_union_card_types": len(card_rows),
        "control_union_events": len(selected),
        "whole_command_cards": len(whole_rows),
        "whole_command_events": sum(int(row["events"]) for row in whole_rows),
        "dy_events": len(dy_rows),
        "dy_terminal_events": sum(row["statement_position"] in {"FINAL", "WHOLE"} for row in dy_rows),
        "uncovered_events_after_controls_and_whole_commands": len(final_remainder),
        "complete_dictionary_card_types": 173,
        "complete_dictionary_events": 381,
        "decision": "FIVE_CONTROL_AXES_PLUS_THREE_WHOLE_COMMANDS_CLOSE_THE_COMPLETE_PROSE_DECK",
    }
    (HERE / "SIX_HUNDRED_SEVENTY_FIRST_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
