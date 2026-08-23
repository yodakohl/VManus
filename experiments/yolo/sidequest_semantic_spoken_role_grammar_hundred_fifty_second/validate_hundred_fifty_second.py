#!/usr/bin/env python3
import csv
import json
from pathlib import Path


OUT = Path(__file__).resolve().parent


def rows(name):
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main():
    lexicon = rows("HUNDRED_FIFTY_SECOND_173_ROLE_LEXICON.tsv")
    events = rows("HUNDRED_FIFTY_SECOND_381_ROLE_EVENTS.tsv")
    clauses = rows("HUNDRED_FIFTY_SECOND_116_ROLE_PARSES.tsv")
    patterns = rows("HUNDRED_FIFTY_SECOND_ROLE_PATTERNS.tsv")
    role_by_id = {row["master_card_id"]: row["spoken_role"] for row in lexicon}
    checks = {
        "lexicon_173": len(lexicon) == 173,
        "events_381": len(events) == 381,
        "clauses_116": len(clauses) == 116,
        "roles_12": len({row["spoken_role"] for row in lexicon}) == 12,
        "event_roles_match": all(row["spoken_role"] == role_by_id[row["master_card_id"]] for row in events),
        "pattern_counts_sum_116": sum(int(row["statement_count"]) for row in patterns) == 116,
        "patterns_unique": len(patterns) == len({row["role_sequence"] for row in patterns}),
        "all_values_preserved": all(row["card_value_de"] for row in lexicon) and all(row["card_value_de"] for row in events),
        "no_empty_cells": all(all(v for v in row.values()) for table in (lexicon, events, clauses, patterns) for row in table),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
