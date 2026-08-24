#!/usr/bin/env python3
"""Validate the eleven pocket-core opening prompts."""

from __future__ import annotations

import csv
import json
import subprocess
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    subprocess.run(["python3", str(HERE / "build_six_hundred_eighty_ninth.py")], check=True)
    prompts = read("SIX_HUNDRED_EIGHTY_NINTH_11_RECORD_OPENING_PROMPTS.tsv")
    projections = read("SIX_HUNDRED_EIGHTY_NINTH_54_OPENING_EVENT_PROJECTIONS.tsv")
    archetypes = read("SIX_HUNDRED_EIGHTY_NINTH_OPENING_ARCHETYPES.tsv")
    specialists = read("SIX_HUNDRED_EIGHTY_NINTH_SPECIALIST_INSERTIONS.tsv")
    checks = {
        "eleven_prompts": len(prompts) == 11 and len({row["record"] for row in prompts}) == 11,
        "fifty_four_opening_events": len(projections) == 54 and len({row["event_id"] for row in projections}) == 54,
        "event_counts_match": sum(int(row["opening_events"]) for row in prompts) == 54,
        "one_hundred_twenty_tokens": sum(int(row["pocket_core_token_count"]) + int(row["specialist_token_count"]) for row in prompts) == 120,
        "eighty_three_core_tokens": sum(int(row["pocket_core_token_count"]) for row in prompts) == 83,
        "thirty_seven_specialist_tokens": sum(int(row["specialist_token_count"]) for row in prompts) == 37,
        "all_prompts_present": all(row["simple_form_prompt_de"] for row in prompts),
        "five_archetypes_cover_records": len(archetypes) == 5 and sum(int(row["instances"]) for row in archetypes) == 11,
        "specialists_present": len(specialists) >= 8,
        "fixed_pages_only": {row["page"] for row in projections} <= {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"},
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks, "passed": sum(checks.values()), "total": len(checks)}
    (HERE / "SIX_HUNDRED_EIGHTY_NINTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
