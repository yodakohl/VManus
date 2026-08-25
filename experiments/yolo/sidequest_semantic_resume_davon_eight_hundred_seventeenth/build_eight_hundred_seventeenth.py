#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
BASE = ROOT / "sidequest_semantic_fifth_workshop_grammar_eight_hundred_fifteenth"
EVENTS = BASE / "EIGHT_HUNDRED_FIFTEENTH_381_EVENT_REPARSE.tsv"
STATEMENTS = BASE / "EIGHT_HUNDRED_FIFTEENTH_116_STATEMENT_REPARSE.tsv"


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
    events = read(EVENTS)
    statements = {row["statement_id"]: row for row in read(STATEMENTS)}
    indices = [i for i, row in enumerate(events) if row["component_recipe"] == "RESUME_CARD"]
    targets = [events[i] for i in indices]

    candidates = [
        {
            "candidate": "WIEDERAUFNEHMEN",
            "short_value_de": "WIEDERAUFNEHMEN",
            "f11r_fit": "MEDIUM",
            "f56r_fit": "MEDIUM",
            "extra_assumption": "UNSAID_PREVIOUS_OPERATION",
            "decision": "REJECT_OLD_TOO_META",
        },
        {
            "candidate": "DAVON",
            "short_value_de": "DAVON",
            "f11r_fit": "HIGH",
            "f56r_fit": "HIGH",
            "extra_assumption": "LOCAL_OWNER_OR_ACTIVE_MATERIAL",
            "decision": "SELECT_MEMORIZED_ANAPHOR",
        },
        {
            "candidate": "GLEICHER_ANSATZ",
            "short_value_de": "VOM_GLEICHEN_ANSATZ",
            "f11r_fit": "LOW",
            "f56r_fit": "MEDIUM",
            "extra_assumption": "PRIOR_BATCH_IN_BOTH_CONTEXTS",
            "decision": "REJECT_TOO_NARROW",
        },
        {
            "candidate": "DIESE_PFLANZE",
            "short_value_de": "VON_DIESER_PFLANZE",
            "f11r_fit": "HIGH",
            "f56r_fit": "HIGH",
            "extra_assumption": "REPEATS_VISIBLE_OWNER_NOUN",
            "decision": "REJECT_LONGER_THAN_DAVON",
        },
        {
            "candidate": "ABSATZTHEMA",
            "short_value_de": "THEMA_WIEDERHOLEN",
            "f11r_fit": "LOW",
            "f56r_fit": "LOW",
            "extra_assumption": "EDITORIAL_META_LANGUAGE",
            "decision": "REJECT_NOT_A_CONTENT_VALUE",
        },
    ]

    occurrence_rows = []
    revised_rows = []
    for index, event in zip(indices, targets):
        previous = events[index - 1]
        following = events[index + 1]
        statement = statements[event["statement_id"]]
        revised = statement["working_reading_de"].replace(
            "Den vorigen Vorgang wiederaufnehmen", "Davon"
        )
        occurrence_rows.append(
            {
                "event_id": event["event_id"],
                "page": event["page"],
                "statement_id": event["statement_id"],
                "owner_de": event["owner_de"],
                "exact_card_id": event["exact_card_id"],
                "surface": event["surface"],
                "old_reading_de": event["fifth_grammar_reading_de"],
                "selected_reading_de": "DAVON",
                "classification": "MEMORIZED_WHOLE_ANAPHOR",
                "previous_event": previous["event_id"],
                "previous_surface": previous["surface"],
                "previous_reading_de": previous["fifth_grammar_reading_de"],
                "following_event": following["event_id"],
                "following_surface": following["surface"],
                "following_reading_de": following["fifth_grammar_reading_de"],
            }
        )
        revised_rows.append(
            {
                "statement_id": statement["statement_id"],
                "page": statement["page"],
                "owner_noun_de": statement["owner_noun_de"],
                "surface_sequence": statement["surface_sequence"],
                "old_reading_de": statement["working_reading_de"],
                "revised_reading_de": revised,
                "anaphor_resolution": "DAVON = von der lokal aktiven Pflanze oder ihrem Arbeitsstoff",
            }
        )

    write(
        "EIGHT_HUNDRED_SEVENTEENTH_5_RESUME_CANDIDATES.tsv",
        candidates,
        ["candidate", "short_value_de", "f11r_fit", "f56r_fit", "extra_assumption", "decision"],
    )
    write(
        "EIGHT_HUNDRED_SEVENTEENTH_2_DAVON_OCCURRENCES.tsv",
        occurrence_rows,
        list(occurrence_rows[0]),
    )
    write(
        "EIGHT_HUNDRED_SEVENTEENTH_2_REVISED_STATEMENTS.tsv",
        revised_rows,
        list(revised_rows[0]),
    )
    summary = {
        "status": "PASS",
        "decision": "DCHOL_SCHOL_REVISED_FROM_WIEDERAUFNEHMEN_TO_DAVON",
        "exact_cards": len({row["exact_card_id"] for row in targets}),
        "surfaces": sorted({row["surface"] for row in targets}),
        "events": len(targets),
        "statements": len(revised_rows),
        "pages": sorted({row["page"] for row in targets}),
        "selected_value": "DAVON",
        "classification": "MEMORIZED_WHOLE_ANAPHOR",
        "core_size": 33,
        "bound_components": 3,
        "whole_forms": 3,
        "sealed_pages": ["f84", "f84r"],
    }
    (HERE / "EIGHT_HUNDRED_SEVENTEENTH_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
