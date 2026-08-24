#!/usr/bin/env python3
"""Validate standalone words, aliases, and specialist atoms."""

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    standalone = read("SIX_HUNDRED_EIGHTH_FOURTEEN_STANDALONE_CARD_AUDIT.tsv")
    specialists = read("SIX_HUNDRED_EIGHTH_FIVE_SPECIALIST_ATOMS.tsv")
    words = read("SIX_HUNDRED_EIGHTH_THIRTY_SEVEN_SEMANTIC_WORDS.tsv")
    cards = read("SIX_HUNDRED_EIGHTH_173_CONSOLIDATED_CARD_DICTIONARY.tsv")
    events = read("SIX_HUNDRED_EIGHTH_381_CONSOLIDATED_EVENT_EDITION.tsv")
    statements = read("SIX_HUNDRED_EIGHTH_116_CONSOLIDATED_STATEMENTS.tsv")
    aliases = [row for row in standalone if row["working_status"].startswith("GRAPHIC_ALIAS")]
    checks = {
        "standalone14": len(standalone) == 14 and len({row["card_no"] for row in standalone}) == 14,
        "portable10_specialist2_alias2": sum(row["working_status"] == "PORTABLE_STANDALONE_WORD" for row in standalone) == 10 and sum(row["working_status"] == "LEARNED_SPECIALIST_WORD" for row in standalone) == 2 and len(aliases) == 2,
        "aliases_are_continue": all(row["spoken_word_de"] == "FORTSETZEN" and row["adds_new_semantic_word"] == "NO" for row in aliases),
        "specialists5": len(specialists) == 5 and {row["component"] for row in specialists} == {"CFH", "S", "LD", "DA", "IIN"},
        "semantic_words37": len(words) == 37 and len({row["canonical_component"] for row in words}) == 37,
        "ls_merged_into_ol": next(row for row in words if row["canonical_component"] == "OL")["graphic_component_aliases"] == "LS" and not any(row["canonical_component"] == "LS" for row in words),
        "cards173": len(cards) == 173 and len({row["card_no"] for row in cards}) == 173,
        "events381": len(events) == 381 and len({row["event_id"] for row in events}) == 381,
        "statements116": len(statements) == 116 and len({row["statement_id"] for row in statements}) == 116,
        "all_ls_semantically_ol": all("LS" not in row["semantic_component_parse"].split("+") for row in cards),
        "only_one_ls_alias_event": sum(row["graphic_alias_used"] == "LS_TO_OL" for row in events) == 1,
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SIX_HUNDRED_EIGHTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for key, value in checks.items():
        print(f"{key}\t{'PASS' if value else 'FAIL'}")
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
