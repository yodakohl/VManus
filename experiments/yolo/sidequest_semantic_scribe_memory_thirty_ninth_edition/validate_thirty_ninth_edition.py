#!/usr/bin/env python3
"""Consistency checks for the practical four-slot memory slate."""

from __future__ import annotations

import csv
import json
from pathlib import Path


OUT = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    slots = read("THIRTY_NINTH_FOUR_MEMORY_SLOTS.tsv")
    transitions = read("THIRTY_NINTH_116_MEMORY_TRANSITIONS.tsv")
    worked = read("THIRTY_NINTH_26_WORKED_JOB_MEMORY_TRACE.tsv")
    required = {"OWNER", "ACTIVE", "TARGET", "PREVIOUS"}
    checks = {
        "four_slots": len(slots) == 4 and {row["slot"] for row in slots} == required,
        "statements_116": len(transitions) == 116,
        "statement_ids_unique": len({row["statement_id"] for row in transitions}) == 116,
        "sequence_complete": [int(row["sequence"]) for row in transitions] == list(range(1, 117)),
        "records_11": len({row["record_id"] for row in transitions}) == 11,
        "pages_7": len({row["page"] for row in transitions}) == 7,
        "record_starts_11": sum(row["entry_boundary"] == "RECORD_START" for row in transitions) == 11,
        "memory_load_bounded": all(0 <= int(row["memory_slots_filled_pre"]) <= 4 and 0 <= int(row["memory_slots_filled_post"]) <= 4 for row in transitions),
        "all_have_surface": all(row["surface_sequence"] for row in transitions),
        "all_have_atoms": all(row["atom_sequence"] for row in transitions),
        "all_have_macro_program": all(row["macro_program"] for row in transitions),
        "all_have_expanded_reading": all(row["expanded_workshop_reading_de"] for row in transitions),
        "worked_steps_26": len(worked) == 26,
        "worked_ids_unique": len({row["statement_id"] for row in worked}) == 26,
        "worked_step_order": [int(row["job_step"]) for row in worked] == list(range(1, 27)),
        "manual_exists": (OUT / "THIRTY_NINTH_SCRIBE_MEMORY_MANUAL.md").exists(),
        "sealed_page_absent": all(row["page"] not in {"f84", "f84r"} for row in transitions),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
