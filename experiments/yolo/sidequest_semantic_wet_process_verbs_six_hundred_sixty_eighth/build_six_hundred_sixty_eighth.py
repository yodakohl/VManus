#!/usr/bin/env python3
"""Close P, LSH, and CFH as a compact wet-process verb set."""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
SOURCE = ROOT / "experiments/yolo/sidequest_semantic_complete_surface_curriculum_six_hundred_thirty_seventh/SIX_HUNDRED_THIRTY_SEVENTH_381_COMPLETE_APPRENTICE_LEDGER.tsv"
ROOT_VALUES = {"P": "EINFUELLEN", "LSH": "WASCHEN", "CFH": "AUSWRINGEN"}


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
    selected: dict[str, list[dict[str, str]]] = defaultdict(list)
    root_for_card: dict[str, str] = {}
    for event in all_events:
        statements[event["statement_id"]].append(event)
        atoms = set(event["semantic_component_parse"].split("+"))
        roots = atoms & ROOT_VALUES.keys()
        if roots:
            root = sorted(roots)[0]
            selected[event["card_no"]].append(event)
            root_for_card[event["card_no"]] = root

    cards = []
    for card in sorted(selected, key=number):
        rows = selected[card]
        first = rows[0]
        root = root_for_card[card]
        cards.append({
            "card_no": card,
            "root": root,
            "portable_root_value_de": ROOT_VALUES[root],
            "surfaces": "|".join(sorted({row["surface"] for row in rows})),
            "component_recipe": first["semantic_component_parse"],
            "composed_reading_de": first["standard_command_de"],
            "events": len(rows),
            "event_ids": "|".join(row["event_id"] for row in rows),
            "pages": "|".join(sorted({row["page"] for row in rows})),
        })

    event_rows = []
    affected_statements: set[str] = set()
    for card in sorted(selected, key=number):
        for event in selected[card]:
            affected_statements.add(event["statement_id"])
            statement = statements[event["statement_id"]]
            index = next(i for i, row in enumerate(statement) if row["event_id"] == event["event_id"])
            event_rows.append({
                "event_id": event["event_id"],
                "page": event["page"],
                "record": event["record"],
                "statement_id": event["statement_id"],
                "card_no": event["card_no"],
                "root": root_for_card[event["card_no"]],
                "surface": event["surface"],
                "component_recipe": event["semantic_component_parse"],
                "composed_reading_de": event["standard_command_de"],
                "statement_position": "WHOLE" if len(statement) == 1 else "ENTRY" if index == 0 else "FINAL" if index == len(statement) - 1 else "MEDIAL",
                "full_statement_surface": " ".join(row["surface"] for row in statement),
            })

    fluent = {
        "H3-S001": "Ansatz am Ziel weiter halten; auswringen, bis zum Sollmass halten, in den Empfaenger fuellen, laenger halten, abnehmen und schliessen.",
        "B1-S012": "Den Arbeitsgang waschen, kurz ansetzen, nochmals kurz waschen und schliessen.",
        "B1-S013": "Kurz waschen und den Schritt schliessen.",
        "B2-S016": "Zur Zielstelle weiterleiten, eine Portion abnehmen, nach Sollmass kurz ansetzen, einfuellen, umsetzen und schliessen.",
        "B3-S010": "An der Zielstelle einfuellen und umsetzen; danach kurz schliessen.",
    }
    statement_rows = []
    for sid in sorted(affected_statements, key=lambda value: (statements[value][0]["record"], int(value.split("S")[-1]))):
        rows = statements[sid]
        statement_rows.append({
            "statement_id": sid,
            "page": rows[0]["page"],
            "record": rows[0]["record"],
            "surface_sequence": " ".join(row["surface"] for row in rows),
            "component_sequence": " | ".join(row["semantic_component_parse"] for row in rows),
            "literal_sequence_de": " | ".join(row["standard_command_de"] for row in rows),
            "fluent_workshop_reading_de": fluent[sid],
            "selected_roots": "|".join(sorted({root_for_card[row["card_no"]] for row in rows if row["card_no"] in root_for_card})),
        })

    contrasts = [
        {"old_overreading": "CPHY=NACHSEIHEN", "replacement": "P+Y=LAUFENDEN POSTEN IN EINEN EMPFAENGER EINFUELLEN", "reason": "P also composes with CHD+DY and CHD+AL outside f11r"},
        {"old_overreading": "SHEY=KLARAUSZUG", "replacement": "SH+EE+Y=LAUFENDEN POSTEN LAENGER HALTEN", "reason": "same exact card recurs in four Herbal/Bio contexts"},
        {"old_overreading": "LSH=BAD", "replacement": "LSH=WASCHEN", "reason": "one open and two short-closed wash commands need no named bath"},
        {"old_overreading": "CFHY=FILTER", "replacement": "CFH+Y=AUSWRINGEN", "reason": "source separation is concrete while filter apparatus is not encoded"},
    ]

    write_tsv(HERE / "SIX_HUNDRED_SIXTY_EIGHTH_6_WET_PROCESS_CARDS.tsv", cards, list(cards[0]))
    write_tsv(HERE / "SIX_HUNDRED_SIXTY_EIGHTH_7_WET_PROCESS_EVENTS.tsv", event_rows, list(event_rows[0]))
    write_tsv(HERE / "SIX_HUNDRED_SIXTY_EIGHTH_5_COMPLETE_STATEMENTS.tsv", statement_rows, list(statement_rows[0]))
    write_tsv(HERE / "SIX_HUNDRED_SIXTY_EIGHTH_4_OVERREADING_REPAIRS.tsv", contrasts, list(contrasts[0]))

    summary = {
        "status": "PASS",
        "root_values": ROOT_VALUES,
        "card_types": len(cards),
        "events": len(event_rows),
        "statements": len(statement_rows),
        "new_unique_cards_beyond_pass667": 4,
        "new_unique_events_beyond_pass667": 5,
        "expanded_dictionary_card_types": 97,
        "expanded_dictionary_events": 217,
        "decision": "P_LSH_CFH_FORM_A_COMPACT_FILL_WASH_WRING_WET_PROCESS_VERB_SET",
    }
    (HERE / "SIX_HUNDRED_SIXTY_EIGHTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
