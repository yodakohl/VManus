#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path


OUT = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    tokens = read("HUNDRED_NINETY_FIFTH_25_TOKEN_MIXED_RENDERING.tsv")
    evidence = read("HUNDRED_NINETY_FIFTH_POSITION_PREFERENCE_EVIDENCE.tsv")
    fields = read("HUNDRED_NINETY_FIFTH_5_FIELD_PARALLEL_EDITION.tsv")
    summary = json.loads((OUT / "BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    checks = {
        "25_tokens": len(tokens) == 25 and len(evidence) == 25,
        "five_fields": len(fields) == 5,
        "all_registered": all(row["surface_registered"] == "YES" for row in tokens),
        "all_cards_readable": all(row["surface_unique_to_card"] == "YES" for row in tokens),
        "all_closures_preserved": all(row["closure_preserved"] == "YES" for row in fields),
        "four_field_modes_survive": sum(row["mode_recovered_by_majority"] == "YES" for row in fields) == 4,
        "same_card_values": all(row["portable_value_de"] for row in tokens),
        "summary_changes": summary["changed_surfaces"] == sum(row["surface_changed"] == "YES" for row in tokens),
        "position_or_fallback_basis": all(row["selection_basis"] in {"POSITION_MAJORITY", "POSITION_TIE_MASTER_OR_LEXICAL", "CARD_OVERALL_FALLBACK"} for row in tokens),
        "sealed_absent": summary["sealed_pages_accessed"] is False,
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks, "summary": summary}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
