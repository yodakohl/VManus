#!/usr/bin/env python3
"""Validate the recurrent recipe formula copybook."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def main() -> None:
    chains = read("THREE_HUNDRED_FIFTH_RECURRENT_CHAINS.tsv")
    formulas = read("THREE_HUNDRED_FIFTH_TEN_TEACHING_FORMULAS.tsv")
    statements = read("THREE_HUNDRED_FIFTH_116_FORMULA_ANNOTATED_STATEMENTS.tsv")
    checks = {
        "recurrent_15": len(chains) == 15,
        "fourteen_bigrams": sum(r["chain_length"] == "2" for r in chains) == 14,
        "one_trigram": sum(r["chain_length"] == "3" for r in chains) == 1,
        "no_fourgram": not any(r["chain_length"] == "4" for r in chains),
        "formulas_10": len(formulas) == 10 and {r["formula_id"] for r in formulas} == {f"F{i:02d}" for i in range(1, 11)},
        "formula_occurrences_23": sum(int(r["occurrence_count"]) for r in formulas) == 23,
        "statements_116": len(statements) == 116,
        "formula_hits_23": sum(int(r["formula_hit_count"]) for r in statements) == 23,
        "all_formula_cards_have_components": all(r["component_imperatives_de"].strip() for r in formulas),
        "no_semantic_or_claim": all(" OR " not in r["formula_reading_de"] for r in formulas),
        "no_sealed_page": not any("f" + "84" in p.read_text(encoding="utf-8").lower() for p in HERE.glob("*") if p.suffix in {".tsv", ".md"}),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks, "failed": [k for k, v in checks.items() if not v]}
    (HERE / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))
    raise SystemExit(0 if result["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
