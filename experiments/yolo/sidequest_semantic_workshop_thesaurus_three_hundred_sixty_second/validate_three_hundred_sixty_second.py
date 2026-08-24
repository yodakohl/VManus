#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    families = read("THREE_HUNDRED_SIXTY_SECOND_33_FAMILY_THESAURUS.tsv")
    phrases = read("THREE_HUNDRED_SIXTY_SECOND_159_PHRASE_INDEX.tsv")
    cards = read("THREE_HUNDRED_SIXTY_SECOND_380_FAMILY_TAGGED_CARDS.tsv")
    statements = read("THREE_HUNDRED_SIXTY_SECOND_116_FAMILY_PARSES.tsv")
    checks = {
        "33_families": len(families) == 33 and len({r["family_id"] for r in families}) == 33,
        "159_phrases": len(phrases) == 159 and len({r["controlled_phrase"] for r in phrases}) == 159,
        "all_phrases_have_known_family": {r["family_id"] for r in phrases} == {r["family_id"] for r in families},
        "fixed_formulas_unique": len({r["fixed_reverse_formula"] for r in phrases}) == 159,
        "380_cards": len(cards) == 380 and len({r["source_position_id"] for r in cards}) == 380,
        "card_formula_present": all(r["fixed_reverse_formula"] and r["family_id"] for r in cards),
        "116_statements": len(statements) == 116 and len({r["statement_id"] for r in statements}) == 116,
        "statement_reverse_exact": all(r["reverse_status"] == "EXACT" for r in statements),
        "all_events_once": sorted(r["event_id"] for r in cards) == sorted(e for r in statements for e in r["source_event_ids"].split("|")),
        "six_lessons": {r["family_id"][0] for r in families} == {"B", "M", "T", "D", "Z", "A"},
        "no_empty_synonyms_or_boundaries": all(r["allowed_free_synonyms_de"] and r["drift_boundary_de"] for r in families),
    }
    status = "PASS" if all(checks.values()) else "FAIL"
    result = {"status": status, "checks": checks, "check_count": len(checks)}
    (HERE / "THREE_HUNDRED_SIXTY_SECOND_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if status != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))
    print(f"PASS {len(checks)} checks")


if __name__ == "__main__":
    main()
