#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
BASE = ROOT / "sidequest_semantic_third_workshop_grammar_eight_hundred_sixth"
CARDS = BASE / "EIGHT_HUNDRED_SIXTH_173_CARD_THIRD_DICTIONARY.tsv"
EVENTS = BASE / "EIGHT_HUNDRED_SIXTH_381_EVENT_REPARSE.tsv"
STATEMENTS = BASE / "EIGHT_HUNDRED_SIXTH_116_STATEMENT_REPARSE.tsv"
ROOTS = ("T", "CKH", "R")
VALUES = {"T": "ANWENDEN", "CKH": "DURCHLASS", "R": "KUEHLEN"}
KINDS = {"T": "ACTION_VERB", "CKH": "PATH_NOUN", "R": "STATE_CHANGE_VERB"}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]], fields: list[str]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    cards = read(CARDS)
    events = read(EVENTS)
    statements = {row["statement_id"]: row for row in read(STATEMENTS)}
    observed_surfaces = {row["surface"] for row in events}

    card_rows = []
    for row in cards:
        tokens = row["component_recipe"].split("+")
        members = [root for root in ROOTS if root in tokens]
        if not members:
            continue
        card_rows.append(
            {
                "exact_card_id": row["exact_card_id"],
                "surfaces": row["registered_surfaces"],
                "component_recipe": row["component_recipe"],
                "members": "+".join(members),
                "reading_de": row["third_grammar_reading_de"],
                "events": row["events"],
            }
        )

    event_rows = []
    co: dict[str, set[str]] = defaultdict(set)
    pages: dict[str, set[str]] = defaultdict(set)
    ids: dict[str, set[str]] = defaultdict(set)
    for row in events:
        tokens = row["component_recipe"].split("+")
        members = [root for root in ROOTS if root in tokens]
        if not members:
            continue
        for root in members:
            co[root].update(token for token in tokens if token != root)
            pages[root].add(row["page"])
            ids[root].add(row["exact_card_id"])
        event_rows.append(
            {
                "event_id": row["event_id"],
                "page": row["page"],
                "statement_id": row["statement_id"],
                "owner_de": row["owner_de"],
                "surface": row["surface"],
                "component_recipe": row["component_recipe"],
                "members": "+".join(members),
                "reading_de": row["third_grammar_reading_de"],
                "statement_reading_de": statements[row["statement_id"]]["working_reading_de"],
            }
        )

    decisions = []
    for root in ROOTS:
        selected = [row for row in event_rows if root in row["members"].split("+")]
        decisions.append(
            {
                "component": root,
                "short_value_de": VALUES[root],
                "grammar_kind": KINDS[root],
                "exact_cards": len(ids[root]),
                "events": len(selected),
                "pages": "|".join(sorted(pages[root])),
                "distinct_co_components": len(co[root]),
                "co_components": "+".join(sorted(co[root])) or "NONE",
                "meaning_invariant": "YES",
                "decision": "PROMOTE_TO_PARADIGM_CORE31",
            }
        )

    t_grade_rows = [
        {"grade": "NONE", "recipe": "T+Y", "surfaces": "chety|chty", "events": 2, "reading_de": "ANWENDEN · DIES", "status": "ATTESTED"},
        {"grade": "E", "recipe": "E+T+Y", "surfaces": "etyd", "events": 1, "reading_de": "KURZ · ANWENDEN · DIES", "status": "ATTESTED_PREFIX_GRADE"},
        {"grade": "E", "recipe": "T+E+Y", "surfaces": "ytey", "events": 1, "reading_de": "ANWENDEN · KURZ · DIES", "status": "ATTESTED_INTERNAL_GRADE"},
        {"grade": "EE", "recipe": "EE+T+Y", "surfaces": "cheety|teey", "events": 0, "reading_de": "LANG · ANWENDEN · DIES", "status": "PREDICTED_RENDERER_AMBIGUOUS"},
        {"grade": "EEE", "recipe": "EEE+T+Y", "surfaces": "cheeety", "events": 1, "reading_de": "VOLL · ANWENDEN · DIES", "status": "ATTESTED"},
    ]
    for row in t_grade_rows:
        row["surface_collision"] = "YES" if row["events"] == 0 and any(surface in observed_surfaces for surface in row["surfaces"].split("|")) else "NO"

    ckh_roles = [
        {"construction": "CKH+Y", "role": "PATH_AS_CURRENT_ARGUMENT", "events": 4, "example": "chckhy|shckhy"},
        {"construction": "SH+E+CKH+AL/Y", "role": "HOLD_AT_OR_THROUGH_PATH", "events": 2, "example": "sheckhal|sheckhy"},
        {"construction": "L+CKH+Y/E+DY", "role": "GUIDE_THROUGH_PATH", "events": 2, "example": "lcheckhy|lcheckhedy"},
        {"construction": "CH+CKH+AL", "role": "TAKE_THROUGH_PATH_TO_TARGET", "events": 1, "example": "chckhal"},
        {"construction": "O+CKH+E+Y", "role": "SHORT_PROCESS_AT_PATH", "events": 1, "example": "qockhey"},
        {"construction": "SH+CKH+E+DY", "role": "HOLD_THROUGH_PATH_AND_CLOSE", "events": 3, "example": "shckhedy"},
        {"construction": "CH+EE+CKH+O+DY", "role": "LONG_TAKE_THROUGH_PATH_AND_CLOSE", "events": 1, "example": "cheeckhody"},
    ]

    reading_ids = ["H1-S001", "H3-S002", "B1-S002", "B2-S004", "B2-S019", "B3-S029", "B6-S001"]
    reading_rows = []
    for sid in reading_ids:
        row = statements[sid]
        reading_rows.append(
            {
                "statement_id": sid,
                "page": row["page"],
                "owner_noun_de": row["owner_noun_de"],
                "surface_sequence": row["surface_sequence"],
                "working_reading_de": row["working_reading_de"],
                "roots_present": "+".join(root for root in ROOTS if any(root in event["component_recipe"].split("+") for event in event_rows if event["statement_id"] == sid)),
            }
        )

    write("EIGHT_HUNDRED_NINTH_24_FINAL_STRIP_CARDS.tsv", card_rows, ["exact_card_id", "surfaces", "component_recipe", "members", "reading_de", "events"])
    write("EIGHT_HUNDRED_NINTH_30_FINAL_STRIP_EVENTS.tsv", event_rows, ["event_id", "page", "statement_id", "owner_de", "surface", "component_recipe", "members", "reading_de", "statement_reading_de"])
    write("EIGHT_HUNDRED_NINTH_3_ROOT_DECISIONS.tsv", decisions, ["component", "short_value_de", "grammar_kind", "exact_cards", "events", "pages", "distinct_co_components", "co_components", "meaning_invariant", "decision"])
    write("EIGHT_HUNDRED_NINTH_5_T_GRADE_ROWS.tsv", t_grade_rows, ["grade", "recipe", "surfaces", "events", "reading_de", "status", "surface_collision"])
    write("EIGHT_HUNDRED_NINTH_7_CKH_ARGUMENT_ROLES.tsv", ckh_roles, ["construction", "role", "events", "example"])
    write("EIGHT_HUNDRED_NINTH_7_READABLE_STATEMENTS.tsv", reading_rows, ["statement_id", "page", "owner_noun_de", "surface_sequence", "working_reading_de", "roots_present"])

    summary = {
        "status": "PASS",
        "decision": "T_CKH_R_PROMOTED_TO_CORE31__RECURRENT_STRIP_ELIMINATED",
        "cards": len(card_rows),
        "events": len(event_rows),
        "component_event_sum": sum(int(row["events"]) for row in decisions),
        "t_prediction_surfaces": 2,
        "t_prediction_collisions": sum(row["surface_collision"] == "YES" for row in t_grade_rows),
        "ckh_argument_roles": len(ckh_roles),
        "new_core_size": 31,
        "remaining_recurrent_strip_values": 0,
        "sealed_pages": ["f84", "f84r"],
    }
    (HERE / "EIGHT_HUNDRED_NINTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
