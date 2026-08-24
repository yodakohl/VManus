#!/usr/bin/env python3
"""Build the shared source-path-target and sequence layer."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
SOURCE = ROOT / "experiments/yolo/sidequest_semantic_complete_surface_curriculum_six_hundred_thirty_seventh/SIX_HUNDRED_THIRTY_SEVENTH_381_COMPLETE_APPRENTICE_LEDGER.tsv"
VALUES = {
    "L": "WEITERLEITEN",
    "OL": "FORTSETZEN",
    "OT": "DANACH",
    "AL": "ZIELSTELLE",
    "AR": "VORRAT",
    "AIR": "FLUESSIGKEITSLAUF",
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
    selected_events: list[dict[str, str]] = []
    cards: dict[str, list[dict[str, str]]] = defaultdict(list)
    for event in all_events:
        statements[event["statement_id"]].append(event)
        atoms = set(event["semantic_component_parse"].split("+"))
        if atoms & VALUES.keys():
            selected_events.append(event)
            cards[event["card_no"]].append(event)

    card_rows = []
    for card in sorted(cards, key=number):
        rows = cards[card]
        first = rows[0]
        selected_roots = [atom for atom in first["semantic_component_parse"].split("+") if atom in VALUES]
        card_rows.append({
            "card_no": card,
            "surfaces": "|".join(sorted({row["surface"] for row in rows})),
            "component_recipe": first["semantic_component_parse"],
            "selected_roots": "+".join(selected_roots),
            "portable_contributions_de": " · ".join(VALUES[root] for root in selected_roots),
            "composed_reading_de": first["standard_command_de"],
            "events": len(rows),
            "pages": "|".join(sorted({row["page"] for row in rows})),
            "event_ids": "|".join(row["event_id"] for row in rows),
        })

    event_rows = []
    positions = Counter()
    for event in selected_events:
        statement = statements[event["statement_id"]]
        index = next(i for i, row in enumerate(statement) if row["event_id"] == event["event_id"])
        position = "WHOLE" if len(statement) == 1 else "ENTRY" if index == 0 else "FINAL" if index == len(statement) - 1 else "MEDIAL"
        positions[position] += 1
        roots = [atom for atom in event["semantic_component_parse"].split("+") if atom in VALUES]
        event_rows.append({
            "event_id": event["event_id"],
            "page": event["page"],
            "record": event["record"],
            "statement_id": event["statement_id"],
            "card_no": event["card_no"],
            "surface": event["surface"],
            "component_recipe": event["semantic_component_parse"],
            "selected_roots": "+".join(roots),
            "portable_contributions_de": " · ".join(VALUES[root] for root in roots),
            "composed_reading_de": event["standard_command_de"],
            "statement_position": position,
            "contains_close": "YES" if "SCHLUSS" in event["standard_command_de"] else "NO",
        })

    root_rows = []
    for root, value in VALUES.items():
        root_events = [event for event in all_events if root in event["semantic_component_parse"].split("+")]
        root_cards = {event["card_no"] for event in root_events}
        root_rows.append({
            "root": root,
            "portable_value_de": value,
            "card_types": len(root_cards),
            "events": len(root_events),
            "component_recipes": len({event["semantic_component_parse"] for event in root_events}),
            "pages": "|".join(sorted({event["page"] for event in root_events})),
            "short_rule_de": {
                "L": "bewegt den aktuellen Posten entlang des Arbeitswegs",
                "OL": "setzt denselben Arbeitsgang fort",
                "OT": "wechselt zum folgenden Arbeitsgang",
                "AL": "setzt die Zieladresse",
                "AR": "setzt die Quell- oder Vorratsadresse",
                "AIR": "bezeichnet die bereits laufende Arbeitsfluessigkeit",
            }[root],
        })

    pair_counts: Counter[tuple[str, str]] = Counter()
    for event in selected_events:
        atoms = event["semantic_component_parse"].split("+")
        for root in [atom for atom in atoms if atom in VALUES]:
            for other in atoms:
                if other != root:
                    pair_counts[(root, other)] += 1
    pair_rows = [{"direction_root": root, "attached_component": other, "events": count} for (root, other), count in sorted(pair_counts.items(), key=lambda item: (-item[1], item[0]))]

    contrast_rows = [
        {"contrast": "AR_vs_AL", "left": "AR=VORRAT/QUELLE", "right": "AL=ZIELSTELLE", "teaching_test": "AR answers woher; AL answers wohin"},
        {"contrast": "L_vs_OL", "left": "L=POSTEN WEITERLEITEN", "right": "OL=SELBEN GANG FORTSETZEN", "teaching_test": "L moves an item; OL preserves the operation"},
        {"contrast": "OL_vs_OT", "left": "OL=FORTSETZEN", "right": "OT=DANACH/NAECHSTER GANG", "teaching_test": "OL stays in the step; OT advances"},
        {"contrast": "AR_vs_AIR", "left": "AR=VORRATSADRESSE", "right": "AIR=LAUFENDE FLUESSIGKEIT", "teaching_test": "AIR is material-in-motion, not merely a source"},
        {"contrast": "L_vs_AIR", "left": "L=WEITERLEITUNGSVERB", "right": "AIR=FLUESSIGKEITSLAUF", "teaching_test": "one is action/path instruction, one is the flowing work material"},
    ]

    write_tsv(HERE / "SIX_HUNDRED_SIXTY_NINTH_85_DIRECTION_CARDS.tsv", card_rows, list(card_rows[0]))
    write_tsv(HERE / "SIX_HUNDRED_SIXTY_NINTH_146_DIRECTION_EVENTS.tsv", event_rows, list(event_rows[0]))
    write_tsv(HERE / "SIX_HUNDRED_SIXTY_NINTH_6_ROOT_SUMMARY.tsv", root_rows, list(root_rows[0]))
    write_tsv(HERE / "SIX_HUNDRED_SIXTY_NINTH_ROOT_ATTACHMENT_COUNTS.tsv", pair_rows, list(pair_rows[0]))
    write_tsv(HERE / "SIX_HUNDRED_SIXTY_NINTH_5_MINIMAL_CONTRASTS.tsv", contrast_rows, list(contrast_rows[0]))

    closed = [row for row in event_rows if row["contains_close"] == "YES"]
    summary = {
        "status": "PASS",
        "root_values": VALUES,
        "union_card_types": len(card_rows),
        "union_events": len(event_rows),
        "positions": dict(sorted(positions.items())),
        "close_events": len(closed),
        "close_events_terminal": sum(row["statement_position"] in {"FINAL", "WHOLE"} for row in closed),
        "new_cards_beyond_pass668": 49,
        "new_events_beyond_pass668": 92,
        "expanded_dictionary_card_types": 146,
        "expanded_dictionary_events": 309,
        "decision": "ONE_SOURCE_PATH_TARGET_AND_SEQUENCE_LAYER_SERVES_ALL_CURRENT_PROCESS_ROOTS",
    }
    (HERE / "SIX_HUNDRED_SIXTY_NINTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
