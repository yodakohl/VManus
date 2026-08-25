#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import subprocess
from pathlib import Path


HERE = Path(__file__).resolve().parent
PREFIX = "EIGHT_HUNDRED_SIXTY_SEVENTH"


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    subprocess.run(["python", str(HERE / "build_eight_hundred_sixty_seventh.py")], check=True)
    slots = read(f"{PREFIX}_4_UNNAMED_PRODUCT_SLOTS.tsv")
    entries = read(f"{PREFIX}_6_WHAT_HOW_ENTRIES.tsv")
    teaching = read(f"{PREFIX}_6_STEP_APPRENTICE_USE.tsv")
    channels = read(f"{PREFIX}_INFORMATION_CHANNELS.tsv")
    summary = json.loads((HERE / f"{PREFIX}_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    checks = {
        "four_slots": len(slots) == 4 and {row["product_slot"] for row in slots} == {"P1", "P2", "P3", "P4"},
        "six_entries": len(entries) == 6 and {row["how_record"] for row in entries} == {"B1", "B2", "B3", "B4", "B5", "B6"},
        "all_slots_used": {row["what_slot"] for row in entries} == {"P1", "P2", "P3", "P4"},
        "complete_bio": sum(int(row["cards"]) for row in entries) == 281 and sum(int(row["statements"]) for row in entries) == 97,
        "six_teaching_steps": len(teaching) == 6 and {int(row["step"]) for row in teaching} == set(range(1, 7)),
        "three_channels": {row["input_channel"] for row in teaching} == {"PICTURE", "CARDS", "MASTER_OR_MEMORY"},
        "unnamed_products": all(row["exact_product_name_visible"] == "NO" for row in slots) and all(row["exact_product_identity"] == "UNNAMED" for row in entries),
        "information_partition": len(channels) == 7 and all(row["current_readability"] for row in channels),
        "no_new_meaning": summary["new_card_meanings"] == 0,
        "sealed_pages": summary["sealed_pages"] == ["f84", "f84r"] and not any("f84" in " ".join(row.values()).lower() for row in slots + entries + teaching + channels),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / f"{PREFIX}_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
