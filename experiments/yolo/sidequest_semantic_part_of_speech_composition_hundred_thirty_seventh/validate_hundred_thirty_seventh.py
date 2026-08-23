#!/usr/bin/env python3
import csv
import json
from pathlib import Path


OUT = Path(__file__).resolve().parent


def rows(name):
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main():
    cards = rows("HUNDRED_THIRTY_SEVENTH_173_TYPED_DICTIONARY.tsv")
    pairs = rows("HUNDRED_THIRTY_SEVENTH_RECURRENT_EXACT_PAIRS.tsv")
    triples = rows("HUNDRED_THIRTY_SEVENTH_RECURRENT_EXACT_TRIPLES.tsv")
    formulae = rows("HUNDRED_THIRTY_SEVENTH_FIVE_COMPOSITION_FORMULAE.tsv")
    statements = rows("HUNDRED_THIRTY_SEVENTH_116_TYPED_STATEMENTS.tsv")
    checks = {
        "cards_173": len(cards) == 173,
        "statements_116": len(statements) == 116,
        "recurrent_pairs_14": len(pairs) == 14,
        "recurrent_triples_1": len(triples) == 1,
        "formulae_5": len(formulae) == 5,
        "typed_all_cards": all(r["syntactic_type"] for r in cards),
        "typed_all_statements": all(r["type_signature"] for r in statements),
        "formula_f1_twice": next(r for r in formulae if r["formula_id"] == "F1_Y_AIIN_Y")["attested_count"] == "2",
        "formula_f2_revision": next(r for r in formulae if r["formula_id"] == "F2_OL_OLOR_OL")["revision"] == "CHOLOR_TO_DERSELBE_ANSATZ",
        "no_empty_cells": all(all(v for v in r.values()) for table in (cards, pairs, triples, formulae, statements) for r in table),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
