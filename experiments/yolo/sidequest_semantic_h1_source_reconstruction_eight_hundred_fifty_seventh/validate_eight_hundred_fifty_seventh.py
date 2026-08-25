#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import subprocess
from pathlib import Path


HERE = Path(__file__).resolve().parent
PREFIX = "EIGHT_HUNDRED_FIFTY_SEVENTH"


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    subprocess.run(["python", str(HERE / "build_eight_hundred_fifty_seventh.py")], check=True)
    rows = read(f"{PREFIX}_10_CARD_SOURCE_MAP.tsv")
    edition = read(f"{PREFIX}_H1_S001_SOURCE_EDITION.tsv")
    summary = json.loads((HERE / f"{PREFIX}_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    checks = {
        "inventory": len(rows) == 10 and len(edition) == 1,
        "events": [row["event_id"] for row in rows] == [f"E{i:03d}" for i in range(1, 11)],
        "meanings": all(row["same_card_meaning"] == "YES" and row["latin_like_source_phrase"] and row["mixed_workshop_shorthand"] for row in rows),
        "owner": all(row["picture_owner_inherited"] == "YES" for row in rows) and edition[0]["picture_owner_is_silent_argument"] == "YES",
        "atoms": sum(int(row["semantic_atom_count"]) for row in rows) == 23 and summary["atom_count_distribution"] == {"1": 3, "2": 3, "3": 3, "5": 1},
        "densest": summary["densest_recipe"] == "OT+Y+T+CH+OL",
        "no_unmapped": summary["unmapped_cards"] == 0,
        "no_language_claim": summary["language_identification_claims"] == 0,
        "sealed_pages": summary["sealed_pages"] == ["f84", "f84r"],
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / f"{PREFIX}_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
