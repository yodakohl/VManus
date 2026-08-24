#!/usr/bin/env python3
"""Validate Pass 704 statement phrasebook."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    statements = read("SEVEN_HUNDRED_FOURTH_116_STATEMENT_TEMPLATES.tsv")
    pairs = read("SEVEN_HUNDRED_FOURTH_55_ROLE_BIGRAMS.tsv")
    exact = read("SEVEN_HUNDRED_FOURTH_14_RECURRENT_EXACT_PAIRS.tsv")
    triples = read("SEVEN_HUNDRED_FOURTH_33_RECURRENT_ROLE_TRIGRAMS.tsv")
    revised = read("SEVEN_HUNDRED_FOURTH_8_TEMPLATE_REVISED_PARAPHRASES.tsv")
    checks = {
        "statements_116": len(statements) == 116,
        "events_381": sum(int(row["events"]) for row in statements) == 381,
        "role_bigram_types_55": len(pairs) == 55,
        "role_bigram_tokens_265": sum(int(row["token_count"]) for row in pairs) == 265,
        "recurrent_role_pairs_37": sum(row["recurrent"] == "YES" for row in pairs) == 37,
        "recurrent_role_pair_tokens_247": sum(int(row["token_count"]) for row in pairs if row["recurrent"] == "YES") == 247,
        "recurrent_exact_pairs_14": len(exact) == 14,
        "recurrent_exact_pair_tokens_34": sum(int(row["token_count"]) for row in exact) == 34,
        "recurrent_role_trigrams_33": len(triples) == 33,
        "recurrent_role_trigram_tokens_111": sum(int(row["token_count"]) for row in triples) == 111,
        "revised_8": len(revised) == 8,
        "seven_attested_role_templates": sum(row["template_status"] == "ATTESTED_ROLE_TEMPLATE" for row in revised) == 7,
        "all_pair_templates_supported": all(int(row["role_template_support"]) >= 1 for row in revised if row["template_status"] == "ATTESTED_ROLE_TEMPLATE"),
        "no_new_surface": all(row["new_surface_invented"] == "NO" for row in revised),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SEVEN_HUNDRED_FOURTH_VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
