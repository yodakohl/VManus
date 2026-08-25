#!/usr/bin/env python3
"""Validate Pass 739 clean fluent edition."""

from __future__ import annotations

import csv
import json
import re
from collections import defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
P738 = HERE.parent / "sidequest_semantic_remainder_closure_seven_hundred_thirty_eighth"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    components = read(HERE / "SEVEN_HUNDRED_THIRTY_NINTH_39_COMPONENT_DICTIONARY.tsv")
    cards = read(HERE / "SEVEN_HUNDRED_THIRTY_NINTH_173_CARD_DICTIONARY.tsv")
    events = read(HERE / "SEVEN_HUNDRED_THIRTY_NINTH_381_EVENT_INTERLINEAR.tsv")
    statements = read(HERE / "SEVEN_HUNDRED_THIRTY_NINTH_116_CLEAN_STATEMENTS.tsv")
    records = read(HERE / "SEVEN_HUNDRED_THIRTY_NINTH_11_CLEAN_RECORDS.tsv")
    purge = read(HERE / "SEVEN_HUNDRED_THIRTY_NINTH_LEGACY_PURGE.tsv")
    source_cards = read(P738 / "SEVEN_HUNDRED_THIRTY_EIGHTH_173_CARD_DICTIONARY.tsv")
    source_events = read(P738 / "SEVEN_HUNDRED_THIRTY_EIGHTH_381_EVENT_INTERLINEAR.tsv")
    summary = json.loads((HERE / "SEVEN_HUNDRED_THIRTY_NINTH_BUILD_SUMMARY.json").read_text(encoding="utf-8"))

    by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in events:
        by_statement[row["statement_id"]].append(row)

    forbidden = re.compile(
        r"\bMass\b|\bZiel\b|\bFortsetz\w*|\bweiterleit\w*|\bauffang\w*|\beinfuell\w*|klar\w*\s+abl|Fluessigkeit\s+klar",
        re.IGNORECASE,
    )
    allowed_pages = {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"}
    checks = {
        "inventory_exact_39_173_381_116_11": (len(components), len(cards), len(events), len(statements), len(records)) == (39, 173, 381, 116, 11),
        "event_ids_unique": len({row["event_id"] for row in events}) == 381,
        "card_ids_unique": len({row["exact_card_id"] for row in cards}) == 173,
        "cards_semantically_unchanged": all(
            {key: row[key] for key in source_cards[0]} == source
            for row, source in zip(cards, source_cards)
        ),
        "events_semantically_and_formally_unchanged": all(
            {key: row[key] for key in source_events[0]} == source
            for row, source in zip(events, source_events)
        ),
        "statement_event_counts": all(len(by_statement[row["statement_id"]]) == int(row["events"]) for row in statements),
        "statement_literal_rebuilt_exactly": all(
            row["codebook_literal_de"] == " | ".join(event["rebuilt_reading_de"] for event in by_statement[row["statement_id"]])
            for row in statements
        ),
        "statement_surfaces_rebuilt_exactly": all(
            row["surface_sequence"] == " ".join(event["surface"] for event in by_statement[row["statement_id"]])
            for row in statements
        ),
        "all_readings_nonempty": all(row["clean_workshop_reading_de"].strip() for row in statements) and all(row["continuous_clean_reading_de"].strip() for row in records),
        "all_owners_explicit": all(
            row["owner_noun_de"].strip()
            and row["clean_workshop_reading_de"].startswith(("Bei ", "An ", "Am ", "Im "))
            for row in statements
        ),
        "legacy_terms_absent": all(not forbidden.search(row["clean_workshop_reading_de"]) for row in statements),
        "purge_performed": sum(int(row["replacements"]) for row in purge) >= 40,
        "only_fixed_prose_pages": {row["page"] for row in events} <= allowed_pages,
        "sealed_pages_absent": all("f84" not in "\t".join(row.values()).lower() for rows in [components, cards, events, statements, records, purge] for row in rows),
        "summary_pass_and_no_changes": summary["status"] == "PASS" and summary["semantic_changes"] == 0 and summary["form_owner_boundary_changes"] == 0,
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SEVEN_HUNDRED_THIRTY_NINTH_VALIDATION.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
