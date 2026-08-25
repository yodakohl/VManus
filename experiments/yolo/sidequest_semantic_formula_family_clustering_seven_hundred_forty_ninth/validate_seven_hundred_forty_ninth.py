#!/usr/bin/env python3
"""Validate Pass 749 phrase-family clustering."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    fragments = read("SEVEN_HUNDRED_FORTY_NINTH_12_FRAGMENT_FAMILIES.tsv")
    families = read("SEVEN_HUNDRED_FORTY_NINTH_4_PHRASE_FAMILIES.tsv")
    contexts = read("SEVEN_HUNDRED_FORTY_NINTH_21_REMAINING_FRAGMENT_CONTEXTS.tsv")
    summary = json.loads((HERE / "SEVEN_HUNDRED_FORTY_NINTH_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    lookup = {row["family"]: row for row in families}
    checks = {
        "counts_12_4_21": (len(fragments), len(families), len(contexts)) == (12, 4, 21),
        "all_fragments_assigned_once": len({row["cards"] for row in fragments}) == 12,
        "family_member_sum_12": sum(int(row["member_fragments"]) for row in families) == 12,
        "three_active_one_closed": (sum(row["status"] == "ACTIVE_PHRASE_FAMILY" for row in families), sum(row["status"] == "CLOSED_BY_PASS748" for row in families)) == (3, 1),
        "measure_11": lookup["MEASURE_ADDRESS_FRAME"]["remaining_occurrences"] == "11",
        "preparation_3": lookup["CURRENT_PREPARATION_FRAME"]["remaining_occurrences"] == "3",
        "continuation_7": lookup["CONTINUATION_FRAME"]["remaining_occurrences"] == "7",
        "activation_closed": lookup["STAGED_ACTIVATION_FRAME"]["remaining_occurrences"] == "0",
        "fifteen_statements": len({row["statement_id"] for row in contexts}) == 15,
        "fixed_pages_only": {row["page"] for row in contexts} <= {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"},
        "sealed_pages_absent": all("f84" not in "\t".join(row.values()).lower() for rows in (fragments, families, contexts) for row in rows),
        "no_semantic_or_deck_change": summary["semantic_changes"] == 0 and summary["deck_changes"] == 0,
        "summary_pass": summary["status"] == "PASS",
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SEVEN_HUNDRED_FORTY_NINTH_VALIDATION.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
