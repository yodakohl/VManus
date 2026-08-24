#!/usr/bin/env python3

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def rows(name):
    with (HERE / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


markers = rows("THREE_HUNDRED_FORTY_FIFTH_79_ORDERED_STATE_MARKERS.tsv")
links = rows("THREE_HUNDRED_FORTY_FIFTH_41_WITHIN_STATEMENT_STATE_LINKS.tsv")
formulas = rows("THREE_HUNDRED_FORTY_FIFTH_NINE_RECURRENT_STATE_FORMULAS.tsv")
statements = rows("THREE_HUNDRED_FORTY_FIFTH_116_STATEMENT_STATE_SKELETONS.tsv")
checks = {
    "seventy_nine_markers": len(markers) == 79 and len({row["event_id"] for row in markers}) == 79,
    "forty_one_links": len(links) == 41,
    "twenty_direct_links": sum(row["direct_card_adjacency"] == "YES" for row in links) == 20,
    "twenty_one_gapped_links": sum(row["direct_card_adjacency"] == "NO" for row in links) == 21,
    "nine_recurrent_formulas": len(formulas) == 9 and len({row["formula_id"] for row in formulas}) == 9,
    "all_formula_counts_at_least_two": all(int(row["within_statement_count"]) >= 2 for row in formulas),
    "formula_counts_reconcile": all(int(row["within_statement_count"]) == int(row["direct_adjacency_count"]) + int(row["gapped_count"]) for row in formulas),
    "all_116_statements": len(statements) == 116,
    "fixed_pages_only": {row["page"] for row in markers} == {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"},
    "sealed_absent": all(row["page"] not in {"f84", "f84r"} for row in markers),
}
result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
(HERE / "THREE_HUNDRED_FORTY_FIFTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
if result["status"] != "PASS":
    raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))
print("PASS", len(checks), "checks")
