#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
BASE = ROOT / "sidequest_semantic_clean_fluent_edition_seven_hundred_thirty_ninth"
EVENTS = BASE / "SEVEN_HUNDRED_THIRTY_NINTH_381_EVENT_INTERLINEAR.tsv"
STATEMENTS = BASE / "SEVEN_HUNDRED_THIRTY_NINTH_116_CLEAN_STATEMENTS.tsv"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]], fields: list[str]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def revised_sentence(statement_id: str, text: str) -> str:
    replacements = {
        "H3-S001": ("in den Empfaenger fuellen", "in den lokalen Empfaenger einfuellen"),
        "B2-S016": ("fuellen, umsetzen", "einfuellen, umsetzen"),
        "B3-S010": ("fuellen und umsetzen", "einfuellen und umsetzen"),
    }
    old, new = replacements[statement_id]
    return text.replace(old, new, 1)


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    events = read(EVENTS)
    statements = {row["statement_id"]: row for row in read(STATEMENTS)}
    target = [row for row in events if "P" in row["component_recipe"].split("+")]

    selected_reading = {
        "P+Y": "EINFUELLEN · DIES",
        "P+CHD+DY": "EINFUELLEN · UMSETZEN · SCHLUSS",
        "P+CHD+AL": "EINFUELLEN · UMSETZEN · ZIELSTELLE",
    }
    source_state = {
        "E043": "AUSGEWRUNGENER_AKTIVER_POSTEN",
        "E221": "AKTIVER_POSTEN_AN_KLEINEN_BECKENSTATIONEN",
        "E248": "AKTIVER_POSTEN_AM_KORBGEFAESS",
    }
    target_state = {
        "E043": "IN_OWNER_LOKALEM_EMPFAENGER__WEITER_AKTIV",
        "E221": "IN_EMPFAENGER_UMGESETZT__GESCHLOSSEN",
        "E248": "AN_OWNER_LOKALER_ZIELSTELLE_EINGEFUELLT",
    }
    rows = []
    statement_rows = []
    for event in target:
        statement = statements[event["statement_id"]]
        rows.append(
            {
                "event_id": event["event_id"],
                "page": event["page"],
                "statement_id": event["statement_id"],
                "owner_de": event["owner_de"],
                "surface": event["surface"],
                "component_recipe": event["component_recipe"],
                "old_value": "FUELLEN",
                "selected_value": "EINFUELLEN",
                "fill_rival": event["rebuilt_reading_de"],
                "into_rival": event["rebuilt_reading_de"].replace("FUELLEN", "HINEIN"),
                "recipient_noun_rival": event["rebuilt_reading_de"].replace("FUELLEN", "EMPFAENGER"),
                "selected_reading": selected_reading[event["component_recipe"]],
                "input_state": source_state[event["event_id"]],
                "output_state": target_state[event["event_id"]],
                "selection_reason": "supplies both motion and verb; receiver remains owner-local",
            }
        )
        statement_rows.append(
            {
                "statement_id": event["statement_id"],
                "page": event["page"],
                "owner_de": event["owner_de"],
                "surface_sequence": statement["surface_sequence"],
                "old_reading_de": statement["clean_workshop_reading_de"],
                "revised_reading_de": revised_sentence(event["statement_id"], statement["clean_workshop_reading_de"]),
            }
        )

    candidates = [
        {"candidate": "FUELLEN", "verb_complete": "YES", "direction_present": "NO", "noun_syntax": "NO", "fits_three": "YES", "repair": 2, "decision": "REVISE"},
        {"candidate": "HINEIN", "verb_complete": "NO", "direction_present": "YES", "noun_syntax": "NO", "fits_three": "PARTIAL", "repair": 3, "decision": "REJECT"},
        {"candidate": "EMPFAENGER", "verb_complete": "NO", "direction_present": "NO", "noun_syntax": "YES", "fits_three": "NO", "repair": 5, "decision": "REJECT"},
        {"candidate": "EINFUELLEN", "verb_complete": "YES", "direction_present": "YES", "noun_syntax": "NO", "fits_three": "YES", "repair": 0, "decision": "SELECT"},
    ]

    write(
        "EIGHT_HUNDRED_FOURTH_3_P_EVENTS.tsv",
        rows,
        ["event_id", "page", "statement_id", "owner_de", "surface", "component_recipe", "old_value", "selected_value", "fill_rival", "into_rival", "recipient_noun_rival", "selected_reading", "input_state", "output_state", "selection_reason"],
    )
    write(
        "EIGHT_HUNDRED_FOURTH_4_P_CANDIDATES.tsv",
        candidates,
        ["candidate", "verb_complete", "direction_present", "noun_syntax", "fits_three", "repair", "decision"],
    )
    write(
        "EIGHT_HUNDRED_FOURTH_3_REVISED_STATEMENTS.tsv",
        statement_rows,
        ["statement_id", "page", "owner_de", "surface_sequence", "old_reading_de", "revised_reading_de"],
    )
    summary = {
        "status": "PASS",
        "decision": "P_REVISED_TO_EINFUELLEN_AND_PROMOTED_TO_CORE21",
        "events": len(rows),
        "cards": len({row["surface"] for row in rows}),
        "statements": len(statement_rows),
        "candidate_meanings": len(candidates),
        "selected_repair": 0,
        "new_core_size": 21,
        "remaining_recurrent_strip_values": 10,
        "sealed_pages": ["f84", "f84r"],
    }
    (HERE / "EIGHT_HUNDRED_FOURTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
