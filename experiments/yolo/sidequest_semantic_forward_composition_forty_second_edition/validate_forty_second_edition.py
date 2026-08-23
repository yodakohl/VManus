#!/usr/bin/env python3
"""Consistency checks for forward-composed workshop commands."""

from __future__ import annotations

import csv
import json
from pathlib import Path


OUT = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    commands = read("FORTY_SECOND_20_FORWARD_COMMANDS.tsv")
    copies = read("FORTY_SECOND_80_SCRIBE_COPIES.tsv")
    checks = {
        "twenty_commands": len(commands) == 20,
        "commands_unique": len({row["exercise_id"] for row in commands}) == 20,
        "tuple_chains_unique": len({row["tuple_sequence"] for row in commands}) == 20,
        "five_owner_classes": len({row["silent_owner"] for row in commands}) == 5,
        "all_absent_from_fixed_text": all(row["occurs_in_fixed_statement"] == "NO" for row in commands),
        "all_absent_from_prior_dictations": all(row["occurs_in_prior_dictation"] == "NO" for row in commands),
        "eighty_copies": len(copies) == 80,
        "four_copies_each": all(sum(row["exercise_id"] == command["exercise_id"] for row in copies) == 4 for command in commands),
        "four_profiles": len({row["scribe_id"] for row in copies}) == 4,
        "tuple_invariant": all(len({row["tuple_sequence"] for row in copies if row["exercise_id"] == command["exercise_id"]}) == 1 for command in commands),
        "meaning_invariant": all(row["meaning_changed"] == "NO" for row in copies),
        "all_have_memory": all(row["initial_memory"] and row["final_memory"] for row in copies),
        "all_have_surface": all(row["scribe_surface_sequence"] for row in copies),
        "dictation_book_exists": (OUT / "FORTY_SECOND_MASTER_DICTATION_BOOK.md").exists(),
        "sealed_tokens_absent": not any("f84" in path.name.lower() for path in OUT.iterdir()),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
