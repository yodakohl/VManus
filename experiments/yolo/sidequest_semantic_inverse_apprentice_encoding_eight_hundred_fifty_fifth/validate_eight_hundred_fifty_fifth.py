#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import subprocess
from pathlib import Path


HERE = Path(__file__).resolve().parent
PREFIX = "EIGHT_HUNDRED_FIFTY_FIFTH"


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    subprocess.run(["python", str(HERE / "build_eight_hundred_fifty_fifth.py")], check=True)
    lexicon = read(f"{PREFIX}_15_PROMPT_LEXICON.tsv")
    decisions = read(f"{PREFIX}_60_ENCODING_DECISIONS.tsv")
    steps = read(f"{PREFIX}_24_ENCODED_STEPS.tsv")
    complete = read(f"{PREFIX}_4_COMPLETE_ENCODINGS.tsv")
    traps = read(f"{PREFIX}_5_ENCODING_TRAPS.tsv")
    summary = json.loads((HERE / f"{PREFIX}_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    checks = {
        "inventory": len(lexicon) == 15 and len(decisions) == 60 and len(steps) == 24 and len(complete) == 4 and len(traps) == 5,
        "four_per_prompt": all(sum(row["prompt_position"] == str(position) for row in decisions) == 4 for position in range(1, 16)),
        "card_choices": all(row["same_card_choice"] == "YES" and row["chosen_exact_card_id"] == row["expected_exact_card_id"] for row in decisions),
        "registered": all(row["registered_surface"] == "YES" for row in decisions),
        "steps": all(row["same_encoding"] == "YES" and row["chosen_exact_card_sequence"] == row["expected_exact_card_sequence"] for row in steps),
        "complete": len({row["chosen_exact_card_sequence"] for row in complete}) == 1 and all(row["same_fifteen_cards"] == row["same_six_steps"] == "YES" for row in complete),
        "four_surfaces": summary["surface_sequences"] == 4,
        "no_new_cards": summary["new_cards"] == 0,
        "no_manuscript_claims": summary["manuscript_claims"] == 0,
        "sealed_pages": summary["sealed_pages"] == ["f84", "f84r"],
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / f"{PREFIX}_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
