#!/usr/bin/env python3
"""Validate the compact five-case surface manual."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    residual = read("SIX_HUNDRED_TWENTY_EIGHTH_179_SURFACE_RULE_DECOMPOSITION.tsv")
    exceptions = read("SIX_HUNDRED_TWENTY_EIGHTH_21_LOCAL_SURFACE_EXCEPTIONS.tsv")
    compact = read("SIX_HUNDRED_TWENTY_EIGHTH_372_COMPACT_SURFACE_WRITER.tsv")
    rules = read("SIX_HUNDRED_TWENTY_EIGHTH_USED_WRAPPER_RULES.tsv")
    resolution = Counter(row["resolution_class"] for row in residual)
    layers = Counter(row["surface_writer_layer"] for row in compact)
    checks = {
        "residual179": len(residual) == 179 and len({row["event_id"] for row in residual}) == 179,
        "resolution_counts": resolution == {"BODY_REGISTER_POSITION_RULE": 68, "PREVIOUS_WRAPPER_RULE": 66, "REGISTER_POSITION_PREVIOUS_MAJORITY": 24, "MEMORIZED_LOCAL_EXCEPTION": 21},
        "renderer_resolves158": sum(row["renderer_exact"] == "YES" for row in residual) == 158,
        "exceptions21": len(exceptions) == 21 and {row["event_id"] for row in exceptions} == {row["event_id"] for row in residual if row["local_exception_needed"] == "YES"},
        "compact372": len(compact) == 372 and len({row["event_id"] for row in compact}) == 372,
        "compact_layer_counts": layers == {"SEMANTIC_CARD_OR_DESK_RULE": 193, "TWO_STAGE_BODY_WRAPPER_RULE": 158, "TWENTY_ONE_LOCAL_EXCEPTION_DECK": 21},
        "all_exact": all(row["exact_roundtrip"] == "YES" for row in compact) and all(row["final_roundtrip"] == "YES" for row in residual),
        "q_after_close16": sum(row["predicted_q_after_close_entry"] == "YES" and row["renderer_exact"] == "YES" for row in residual) == 16,
        "rules_nonempty": len(rules) > 0,
        "five_cases": {row["case_id"] for row in compact} == {f"C{i}" for i in range(1, 6)},
        "no_sealed_pages": not any(row["page"].startswith("f84") for row in compact),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SIX_HUNDRED_TWENTY_EIGHTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for key, value in checks.items():
        print(f"{key}\t{'PASS' if value else 'FAIL'}")
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
