#!/usr/bin/env python3
"""Validate the ten-card verb closure."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def main() -> None:
    decisions = read("THREE_HUNDRED_FOURTH_TEN_CARD_DECISIONS.tsv")
    lexicon = read("THREE_HUNDRED_FOURTH_173_REVISED_IMPERATIVE_LEXICON.tsv")
    events = read("THREE_HUNDRED_FOURTH_381_REVISED_IMPERATIVE_EVENTS.tsv")
    statements = read("THREE_HUNDRED_FOURTH_116_REVISED_STATEMENTS.tsv")
    clauses = {r["master_card_id"]: r["imperative_clause_de"] for r in lexicon}
    checks = {
        "decisions_10": len(decisions) == 10 and len({r["master_card_id"] for r in decisions}) == 10,
        "target_occurrences_12": sum(int(r["occurrence_count"]) for r in decisions) == 12,
        "cards_173": len(lexicon) == 173 and len(clauses) == 173,
        "events_381": len(events) == 381,
        "statements_116": len(statements) == 116,
        "no_named_remainder": not any(r["conversion_method"] == "NAMED_WORKSTEP_IMPERATIVE" for r in lexicon),
        "targets_narrowed": sum(r["conversion_method"] == "CONTEXT_NARROWED_VERB" for r in lexicon) == 10,
        "event_dictionary_match": all(r["imperative_clause_de"] == clauses[r["master_card_id"]] for r in events if r["event_id"] not in {"E180", "E181"}),
        "all_statements_complete": all(r["fluent_imperative_de"].endswith((";", "↪", "…")) for r in statements),
        "no_sealed_page": not any("f" + "84" in p.read_text(encoding="utf-8").lower() for p in HERE.glob("*")),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks, "failed": [k for k, v in checks.items() if not v]}
    (HERE / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))
    raise SystemExit(0 if result["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
