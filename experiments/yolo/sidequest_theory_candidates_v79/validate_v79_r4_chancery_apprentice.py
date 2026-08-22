#!/usr/bin/env python3
"""Validate the bounded V79 R4 apprentice artifacts."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def rows(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


manual = rows("V79_R4_COMPACT_MANUAL.tsv")
lines = rows("V79_R4_19_LINE_TRANSITION_AUDIT.tsv")
traces = rows("V79_R4_FORWARD_BACKWARD_TRACES.tsv")
errors = rows("V79_R4_ERROR_AUDIT.tsv")

checks = {
    "manual_12": len(manual) == 12,
    "line_transitions_19": len(lines) == 19,
    "one_generic_match": sum(r["generic_read_once_predicate"] == "MATCH" for r in lines) == 1,
    "generic_match_exact_pair": [(r["before_event"], r["after_event"]) for r in lines if r["generic_read_once_predicate"] == "MATCH"] == [("E180", "E181")],
    "four_owner_resets": sum(r["visible_owner_reset"] == "YES" for r in lines) == 4,
    "trace_12": len(traces) == 12,
    "three_units": {r["unit_id"] for r in traces} == {"H2", "B2", "A3_LEFT_28"},
    "four_trace_modes_each": all(sum(r["unit_id"] == unit for r in traces) == 4 for unit in {"H2", "B2", "A3_LEFT_28"}),
    "no_content_without_exemplar": all(r["concrete_content_recovery"].startswith("ZERO_") for r in traces if r["master_exemplar_access"] == "WITHOUT_MASTER_EXEMPLAR"),
    "with_exemplar_complete": all(r["exact_form_recovery"] == "COMPLETE" for r in traces if r["master_exemplar_access"] == "WITH_MASTER_EXEMPLAR"),
    "error_rows_10": len(errors) == 10,
    "no_new_word_rule": any(r["rule_id"] == "M11" and "UNKNOWN" in (r["apprentice_instruction"] + r["guard"]) for r in manual),
    "astro_no_join": any(r["failure"] == "F68_F69_KEY" and r["status"] == "HARD" for r in errors),
    # Exact-card hashes may coincidentally contain the hex substring ``f84``;
    # only materialized page/locus identifiers are seal-relevant here.
    "sealed_names_absent": not any(
        r[side].lower().startswith("f84")
        for r in lines
        for side in ("before_locus", "after_locus")
    ),
}
result = {
    "schema": "SIDEQUEST_V79_R4_VALIDATION_V1",
    "status": "PASS" if all(checks.values()) else "FAIL",
    "checks": checks,
    "passed": sum(checks.values()),
    "total": len(checks),
}
(HERE / "V79_R4_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"{result['status']} {result['passed']}/{result['total']}")
raise SystemExit(0 if result["status"] == "PASS" else 1)
