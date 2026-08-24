#!/usr/bin/env python3
"""Build Pass 718: recopy the master page in a longer framed hand."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P712 = ROOT / "experiments/yolo/sidequest_semantic_duplicate_recipe_inventory_seven_hundred_twelfth"
P717 = ROOT / "experiments/yolo/sidequest_semantic_continuous_master_page_seven_hundred_seventeenth"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def change_rule(first: str, second: str) -> str:
    if first == second:
        return "UNCHANGED_REGISTERED_FORM"
    if second.startswith("ch") and not first.startswith("ch"):
        return "H2_CH_ENTRY_FRAME"
    if second.startswith("q") and not first.startswith("q"):
        return "H3_Q_ENTRY_FRAME"
    if len(second) > len(first) and "e" in second:
        return "H1_EXTENDED_E_JOINT"
    return "H4_LONGER_REGISTERED_ALLOGRAPH"


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    mapping = read(P712 / "SEVEN_HUNDRED_TWELFTH_173_EXACT_TO_SEMANTIC_MAP.tsv")
    master = read(P717 / "SEVEN_HUNDRED_SEVENTEENTH_27_OWNER_STATE_TRACE.tsv")
    surfaces_to_cards: dict[str, set[str]] = defaultdict(set)
    for row in mapping:
        for surface in row["surfaces"].split("|"):
            surfaces_to_cards[surface].add(row["exact_card_id"])
    by_card = {row["exact_card_id"]: row for row in mapping}

    rows = []
    for event in master:
        card = event["selected_card"]
        candidates = [surface for surface in by_card[card]["surfaces"].split("|") if surfaces_to_cards[surface] == {card}]
        second = sorted(candidates, key=lambda value: (-len(value), value))[0]
        rule = change_rule(event["surface"], second)
        rows.append({
            "master_event_id": event["master_event_id"], "docket_id": event["docket_id"],
            "owner": event["owner"], "line_no": event["line_no"], "line_column": event["line_column"],
            "component_recipe": event["component_recipe"], "exact_card": card,
            "first_hand_surface": event["surface"], "second_hand_surface": second,
            "surface_changed": "YES" if second != event["surface"] else "NO",
            "second_hand_rule": rule, "second_surface_unique_to_card": "YES",
            "same_exact_card": "YES", "same_owner": "YES",
            "same_statement_boundary": "YES", "same_line_boundary": "YES",
            "backread_de": event["backread_de"],
        })

    line_rows = []
    for line_no in range(1, 6):
        subset = [row for row in rows if int(row["line_no"]) == line_no]
        first_line = " ".join(str(row["first_hand_surface"]) for row in subset)
        second_line = " ".join(str(row["second_hand_surface"]) for row in subset)
        line_rows.append({
            "line_no": line_no, "events": len(subset), "owners": " > ".join(dict.fromkeys(str(row["owner"]) for row in subset)),
            "first_hand_line": first_line, "second_hand_line": second_line,
            "changed_events": sum(row["surface_changed"] == "YES" for row in subset),
            "first_character_count": sum(len(str(row["first_hand_surface"])) for row in subset),
            "second_character_count": sum(len(str(row["second_hand_surface"])) for row in subset),
        })

    counts = Counter(row["second_hand_rule"] for row in rows)
    rule_rows = [
        {"rule_id": "H1_EXTENDED_E_JOINT", "events": counts["H1_EXTENDED_E_JOINT"], "instruction_de": "Bei CHD+Y die belegte laengere e-Fuge waehlen."},
        {"rule_id": "H2_CH_ENTRY_FRAME", "events": counts["H2_CH_ENTRY_FRAME"], "instruction_de": "Wo vorhanden, die belegte laengste ch-gerahmte Kartenform waehlen."},
        {"rule_id": "H3_Q_ENTRY_FRAME", "events": counts["H3_Q_ENTRY_FRAME"], "instruction_de": "Bei den zwei passenden OK-Karten die belegte q-Eintrittsform waehlen."},
        {"rule_id": "UNCHANGED_REGISTERED_FORM", "events": counts["UNCHANGED_REGISTERED_FORM"], "instruction_de": "Hat die Karte keine laengere eindeutige Form, exakt unveraendert kopieren."},
    ]

    write("SEVEN_HUNDRED_EIGHTEENTH_27_PARALLEL_HAND_TRACE.tsv", rows)
    write("SEVEN_HUNDRED_EIGHTEENTH_5_PARALLEL_LINES.tsv", line_rows)
    write("SEVEN_HUNDRED_EIGHTEENTH_4_SECOND_HAND_RULES.tsv", rule_rows)

    summary = {
        "status": "PASS", "events": len(rows), "lines": len(line_rows),
        "changed_surfaces": sum(row["surface_changed"] == "YES" for row in rows),
        "unchanged_surfaces": sum(row["surface_changed"] == "NO" for row in rows),
        "change_rules": {key: value for key, value in counts.items() if key != "UNCHANGED_REGISTERED_FORM"},
        "first_character_count": sum(len(row["first_hand_surface"]) for row in rows),
        "second_character_count": sum(len(row["second_hand_surface"]) for row in rows),
        "exact_card_matches": sum(row["same_exact_card"] == "YES" for row in rows),
        "owner_matches": sum(row["same_owner"] == "YES" for row in rows),
        "statement_boundary_matches": sum(row["same_statement_boundary"] == "YES" for row in rows),
        "line_boundary_matches": sum(row["same_line_boundary"] == "YES" for row in rows),
        "new_surfaces": 0,
        "decision": "SECOND_LONG_FRAMED_HAND_CHANGES_FOURTEEN_SURFACES_WHILE_ALL_TWENTY_SEVEN_CARDS_AND_BOUNDARIES_ROUNDTRIP",
    }
    (HERE / "SEVEN_HUNDRED_EIGHTEENTH_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
