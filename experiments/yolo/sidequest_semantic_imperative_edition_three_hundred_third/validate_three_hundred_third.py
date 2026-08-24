#!/usr/bin/env python3
"""Validate the complete imperative edition."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def main() -> None:
    lexicon = read("THREE_HUNDRED_THIRD_173_IMPERATIVE_CARD_LEXICON.tsv")
    events = read("THREE_HUNDRED_THIRD_381_IMPERATIVE_EVENTS.tsv")
    statements = read("THREE_HUNDRED_THIRD_116_FLUENT_IMPERATIVE_STATEMENTS.tsv")
    card_clause = {r["master_card_id"]: r["imperative_clause_de"] for r in lexicon}
    checks = {
        "cards_173": len(lexicon) == 173 and len(card_clause) == 173,
        "events_381": len(events) == 381 and len({r["event_id"] for r in events}) == 381,
        "statements_116": len(statements) == 116 and len({r["statement_id"] for r in statements}) == 116,
        "records_11": len({r["record_unit_id"] for r in statements}) == 11,
        "source_tokens_380": sum(int(r["read_source_token_count"]) for r in statements) == 380,
        "dictionary_event_identity": all(r["imperative_clause_de"] == card_clause[r["master_card_id"]] for r in events if r["event_id"] not in {"E180", "E181"}),
        "all_cards_concrete": all(r["source_short_value_de"].strip() and r["imperative_clause_de"].strip() for r in lexicon),
        "no_placeholders": not any(any(word in r["imperative_clause_de"].upper() for word in ["UNKNOWN", "EXEMPLAR", "FORMAL_LABEL"]) for r in lexicon),
        "all_statements_punctuated": all(r["fluent_imperative_de"].endswith((";", "↪", "…")) for r in statements),
        "read_once_visible": sum("sichtbare Wiederholung" in r["imperative_clause_de"] for r in events) == 1,
        "no_sealed_page": not any("f" + "84" in p.read_text(encoding="utf-8").lower() for p in HERE.glob("*")),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks, "failed": [k for k, v in checks.items() if not v]}
    (HERE / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))
    raise SystemExit(0 if result["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
