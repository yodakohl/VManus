#!/usr/bin/env python3
"""Consistency checker for the complete worked dossier."""

from __future__ import annotations

import csv
import json
from pathlib import Path


OUT = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    steps = read("THIRTY_SEVENTH_26_WORK_STEPS.tsv")
    lookup = read("THIRTY_SEVENTH_F68_LOOKUP_OPTIONS.tsv")
    jobs = read("THIRTY_SEVENTH_JOB_CARD.tsv")
    hands = read("THIRTY_SEVENTH_FOUR_HAND_RENDERING.tsv")
    checks = {
        "one_job": len(jobs) == 1,
        "steps_26": len(steps) == 26,
        "groups_79": sum(int(r["group_count"]) for r in steps) == 79,
        "what_4": sum(r["phase"] == "WHAT" for r in steps) == 4,
        "how_22": sum(r["phase"] == "HOW" for r in steps) == 22,
        "statements_unique": len({r["statement_id"] for r in steps}) == 26,
        "f68_options_37": len(lookup) == 37,
        "f68_groups_65": sum(int(r["group_count"]) for r in lookup) == 65,
        "one_astro_selected": sum(r["selected_for_worked_job"] == "YES" for r in lookup) == 1,
        "four_hands": len(hands) == 4,
        "hand_meaning_invariant": len({r["semantic_readback_de"] for r in hands}) == 1,
        "all_readings_concrete": all(r["master_dictation_de"] and r["apprentice_readback_de"] for r in steps),
        "dossier": (OUT / "THIRTY_SEVENTH_COMPLETE_WORKED_DOSSIER.md").exists(),
        "report": (OUT / "THIRTY_SEVENTH_EDITION_REPORT.md").exists(),
        "sealed_absent": not any("f84" in path.name.lower() for path in OUT.iterdir()),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
