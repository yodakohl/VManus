#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import subprocess
from pathlib import Path


HERE = Path(__file__).resolve().parent
PREFIX = "EIGHT_HUNDRED_FIFTY_SIXTH"


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    subprocess.run(["python", str(HERE / "build_eight_hundred_fifty_sixth.py")], check=True)
    steps = read(f"{PREFIX}_6_RECIPE_SKELETON_STEPS.tsv")
    mapping = read(f"{PREFIX}_15_ABBREVIATION_TO_CARD.tsv")
    sources = read(f"{PREFIX}_3_HISTORICAL_ANALOGUES.tsv")
    summary = json.loads((HERE / f"{PREFIX}_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    checks = {
        "inventory": len(steps) == 6 and len(mapping) == 15 and len(sources) == 3,
        "prompt_order": [int(row["prompt_position"]) for row in mapping] == list(range(1, 16)),
        "prompt_accounting": sum(int(row["prompt_count"]) for row in steps) == 15,
        "meaning_survives": all(row["meaning_survives_shortening"] == "YES" for row in mapping),
        "same_cards": all(row["same_cards_after_abbreviation"] == "YES" for row in steps),
        "source_links": all(row["url"].startswith("https://wellcomecollection.org/") for row in sources),
        "no_language_claim": summary["language_identification_claims"] == 0,
        "no_new_cards": summary["new_cards"] == 0,
        "sealed_pages": summary["sealed_pages"] == ["f84", "f84r"],
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / f"{PREFIX}_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
