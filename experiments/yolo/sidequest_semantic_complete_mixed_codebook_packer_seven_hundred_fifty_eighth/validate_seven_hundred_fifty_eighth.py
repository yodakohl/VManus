#!/usr/bin/env python3
"""Validate Pass 758 complete mixed codebook packer."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    exemplars = read("SEVEN_HUNDRED_FIFTY_EIGHTH_7_BOUND_EXEMPLARS.tsv")
    shells = read("SEVEN_HUNDRED_FIFTY_EIGHTH_3_FORMULA_SHELLS.tsv")
    motifs = read("SEVEN_HUNDRED_FIFTY_EIGHTH_8_SHARED_CARD_MOTIFS.tsv")
    layers = read("SEVEN_HUNDRED_FIFTY_EIGHTH_8_PACKER_LAYERS.tsv")
    audit = read("SEVEN_HUNDRED_FIFTY_EIGHTH_116_FINAL_PACKING_AUDIT.tsv")
    cards = read("SEVEN_HUNDRED_FIFTY_EIGHTH_381_FINAL_CARD_OUTPUT.tsv")
    records = read("SEVEN_HUNDRED_FIFTY_EIGHTH_11_RECORD_SUMMARY.tsv")
    summary = json.loads((HERE / "SEVEN_HUNDRED_FIFTY_EIGHTH_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    checks = {
        "counts_7_3_8_8_116_381_11": (len(exemplars), len(shells), len(motifs), len(layers), len(audit), len(cards), len(records)) == (7, 3, 8, 8, 116, 381, 11),
        "all_statements_exact": all(row["final_exact"] == "YES" for row in audit),
        "all_records_exact": all(row["record_exact"] == "YES" and row["statements"] == row["exact_statements"] for row in records),
        "seven_exemplars_applied": sum(row["applied_exemplar"] != "NONE" for row in audit) == 7,
        "three_shell_partition": sorted(int(row["statements"]) for row in shells) == [1, 3, 3],
        "layer_order_1_to_8": [int(row["application_order"]) for row in layers] == list(range(1, 9)),
        "card_ordinals_complete": all([int(row["card_ordinal_in_statement"]) for row in cards if row["statement_id"] == statement] == list(range(1, 1 + sum(row["statement_id"] == statement for row in cards))) for statement in {row["statement_id"] for row in cards}),
        "fixed_pages_only": {row["page"] for row in cards} <= {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"},
        "sealed_pages_absent": all("f84" not in "\t".join(row.values()).lower() for rows in (exemplars, shells, motifs, layers, audit, cards, records) for row in rows),
        "no_semantic_or_deck_change": summary["semantic_changes"] == 0 and summary["deck_changes"] == 0,
        "summary_exact": (summary["exact_statements"], summary["cards"], summary["exact_records"]) == (116, 381, 11),
        "summary_pass": summary["status"] == "PASS",
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SEVEN_HUNDRED_FIFTY_EIGHTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
