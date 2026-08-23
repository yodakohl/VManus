#!/usr/bin/env python3
"""Validate the four-renderer workshop simulation."""

from __future__ import annotations

import csv
import json
from pathlib import Path


OUT = Path(__file__).resolve().parent


def rows(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    profiles = rows("NINETY_EIGHTH_FOUR_RENDERER_PROFILES.tsv")
    programs = rows("NINETY_EIGHTH_12_SOURCE_PROGRAMS.tsv")
    rendered = rows("NINETY_EIGHTH_48_SCRIBAL_REALIZATIONS.tsv")
    checks = {
        "profiles_4": len(profiles) == 4,
        "programs_12": len(programs) == 12,
        "realizations_48": len(rendered) == 48,
        "full_cross_product": {(row["program_id"], row["renderer_id"]) for row in rendered} == {(p["program_id"], r["renderer_id"]) for p in programs for r in profiles},
        "all_programs_preserved": all(row["semantic_program_preserved"] == "YES" for row in rendered),
        "card_sequences_invariant": all(len({row["card_identity_sequence"] for row in rendered if row["program_id"] == program["program_id"]}) == 1 for program in programs),
        "four_output_profiles_present": {row["renderer_id"] for row in rendered} == {"R-A", "R-B", "R-C", "R-D"},
        "no_empty_surfaces": all(row["visible_surface_sequence"] for row in rendered),
        "sealed_absent": all("f84" not in "\t".join(row.values()).lower() for row in rendered),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
