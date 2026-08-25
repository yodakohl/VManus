#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import subprocess
from pathlib import Path


HERE = Path(__file__).resolve().parent
PREFIX = "EIGHT_HUNDRED_FIFTY_FOURTH"


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    subprocess.run(["python", str(HERE / "build_eight_hundred_fifty_fourth.py")], check=True)
    source = read(f"{PREFIX}_6_SOURCE_COMMANDS.tsv")
    events = read(f"{PREFIX}_60_EVENT_RENDERINGS.tsv")
    steps = read(f"{PREFIX}_24_STEP_RENDERINGS.tsv")
    complete = read(f"{PREFIX}_4_COMPLETE_PREPARATIONS.tsv")
    summary = json.loads((HERE / f"{PREFIX}_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    checks = {
        "inventory": len(source) == 6 and len(events) == 60 and len(steps) == 24 and len(complete) == 4,
        "source": all(row["all_from_model_leaf"] == "YES" for row in source) and summary["event_positions"] == 15 and summary["unique_model_cards_used"] == 15,
        "four_per_position": all(sum(row["event_position"] == str(position) for row in events) == 4 for position in range(1, 16)),
        "registered": all(row["registered_and_same_meaning"] == "YES" and row["rendered_surface"] in row["registered_surfaces"].split("|") for row in events),
        "same_steps": all(row["same_step"] == "YES" for row in steps) and len({row["decoded_command_de"] for row in steps if row["step"] == "1"}) == 1,
        "same_complete": len({row["decoded_preparation_de"] for row in complete}) == 1 and all(row["same_six_step_preparation"] == "YES" for row in complete),
        "no_new_cards": summary["new_card_types_invented"] == 0,
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
