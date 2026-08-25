#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import subprocess
from pathlib import Path


HERE = Path(__file__).resolve().parent
PREFIX = "EIGHT_HUNDRED_FIFTY_THIRD"


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    subprocess.run(["python", str(HERE / "build_eight_hundred_fifty_third.py")], check=True)
    rows = read(f"{PREFIX}_16_MODEL_BOOK_ROWS.tsv")
    variants = read(f"{PREFIX}_52_VARIANT_READINGS.tsv")
    summary = json.loads((HERE / f"{PREFIX}_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    checks = {
        "inventory": len(rows) == 16 and len(variants) == 52,
        "unique_cards": len({row["exact_card_id"] for row in rows}) == 16,
        "surface_accounting": all(sum(item["exact_card_id"] == row["exact_card_id"] for item in variants) == int(row["surface_count"]) for row in rows),
        "same_meaning": all(row["same_card_and_meaning"] == "YES" and row["generated_by"] for row in variants),
        "families": summary["families"] == 8,
        "mixed_system": summary["productive_cards"] == 14 and summary["whole_cards"] == 2 and summary["bound_frames"] == 0,
        "commands": summary["empty_commands"] == 0,
        "no_hand_attribution": summary["actual_hand_attributions"] == 0,
        "sealed_pages": summary["sealed_pages"] == ["f84", "f84r"],
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / f"{PREFIX}_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
