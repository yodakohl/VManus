#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
BASE = ROOT / "experiments/yolo/sidequest_semantic_vocabulary_granularity_two_hundred_third"
EVENTS = BASE / "TWO_HUNDRED_THIRD_381_EVENT_COMPACT_EDITION.tsv"
DICT = BASE / "TWO_HUNDRED_THIRD_173_CARD_COMPACT_DICTIONARY.tsv"

ROLE = {
    "MC039": "MENGE_STUFE",
    "MC153": "FORTSETZUNG",
    "MC123": "AKTIVER_POSTEN",
    "MC074": "TRANSFER",
    "MC026": "EINSATZ",
    "MC154": "ZIEL",
    "MC120": "MENGE_HANDLUNG",
    "MC080": "ZUBEREITUNG",
    "MC161": "ZUSTAND",
    "MC040": "ZIEL_EINSATZ",
    "MC055": "QUELLBEZUG",
    "MC119": "PRODUKT",
    "MC019": "ENDZUSTAND",
    "MC032": "DAUER_HANDLUNG",
    "MC086": "MATERIALTEIL",
    "MC157": "FORTGEFUEHRTE_ZUBEREITUNG",
    "MC171": "FOLGEPOSTEN",
}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    events = read(EVENTS)
    dictionary = {row["master_card_id"]: row for row in read(DICT)}
    by_card: dict[str, list[dict[str, str]]] = defaultdict(list)
    by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for event in events:
        by_card[event["master_card_id"]].append(event)
        by_statement[event["statement_id"]].append(event)

    bridge_ids = {
        card_id for card_id, rows in by_card.items()
        if {row["record_unit_id"][0] for row in rows} == {"H", "B"}
    }
    decision_rows: list[dict[str, object]] = []
    for card_id in sorted(bridge_ids, key=lambda value: (-len(by_card[value]), int(value[2:]))):
        rows = by_card[card_id]
        herbal = [row for row in rows if row["record_unit_id"].startswith("H")]
        bio = [row for row in rows if row["record_unit_id"].startswith("B")]
        if min(len(herbal), len(bio)) >= 2:
            portability = "STRONG_PORTABLE_CORE"
        elif len(rows) >= 5:
            portability = "ASYMMETRIC_PORTABLE_CORE"
        else:
            portability = "THIN_BUT_READABLE_BRIDGE"
        decision_rows.append({
            "master_card_id": card_id,
            "master_form": dictionary[card_id]["master_form"],
            "registered_surfaces": dictionary[card_id]["registered_surfaces"],
            "invariant_value_de": dictionary[card_id]["current_value_de"],
            "bridge_role": ROLE[card_id],
            "total_occurrences": len(rows),
            "herbal_occurrences": len(herbal),
            "bio_occurrences": len(bio),
            "herbal_records": "|".join(dict.fromkeys(row["record_unit_id"] for row in herbal)),
            "bio_records": "|".join(dict.fromkeys(row["record_unit_id"] for row in bio)),
            "herbal_example": f"{herbal[0]['statement_id']}:{herbal[0]['visible_surface']}",
            "bio_example": f"{bio[0]['statement_id']}:{bio[0]['visible_surface']}",
            "portability": portability,
            "reading_rule_de": "denselben kurzen Werkstattwert in beiden Registern lesen",
        })
    write(OUT / "TWO_HUNDRED_ELEVENTH_17_CROSS_REGISTER_CARDS.tsv", decision_rows)

    context_rows: list[dict[str, object]] = []
    for event in events:
        if event["master_card_id"] not in bridge_ids:
            continue
        statement = by_statement[event["statement_id"]]
        position = next(i for i, row in enumerate(statement) if row["event_id"] == event["event_id"])
        left = statement[position - 1]["portable_value_de"] if position else "START"
        right = statement[position + 1]["portable_value_de"] if position + 1 < len(statement) else "END"
        context_rows.append({
            "event_id": event["event_id"],
            "section": "HERBAL" if event["record_unit_id"].startswith("H") else "BIOLOGICAL",
            "record_unit_id": event["record_unit_id"],
            "page": event["page"],
            "statement_id": event["statement_id"],
            "visible_owner": event["visible_owner"],
            "master_card_id": event["master_card_id"],
            "visible_surface": event["visible_surface"],
            "invariant_value_de": event["portable_value_de"],
            "left_value_de": left,
            "right_value_de": right,
            "terminal_status": event["terminal_status"],
        })
    write(OUT / "TWO_HUNDRED_ELEVENTH_136_BRIDGE_OCCURRENCES.tsv", context_rows)

    summary = {
        "event_source_sha256": hashlib.sha256(EVENTS.read_bytes()).hexdigest(),
        "dictionary_source_sha256": hashlib.sha256(DICT.read_bytes()).hexdigest(),
        "bridge_cards": len(decision_rows),
        "bridge_occurrences": len(context_rows),
        "herbal_bridge_occurrences": sum(row["section"] == "HERBAL" for row in context_rows),
        "bio_bridge_occurrences": sum(row["section"] == "BIOLOGICAL" for row in context_rows),
        "productive_bridge_cards": sum(dictionary[row["master_card_id"]]["component_class"] == "PRODUCTIVE_COMPOSITION" for row in decision_rows),
        "whole_bridge_cards": sum(dictionary[row["master_card_id"]]["component_class"] == "MEMORIZED_WHOLE_CARD" for row in decision_rows),
        "portability_counts": dict(Counter(row["portability"] for row in decision_rows)),
        "all_prose_events": len(events),
        "sealed_pages_accessed": False,
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
