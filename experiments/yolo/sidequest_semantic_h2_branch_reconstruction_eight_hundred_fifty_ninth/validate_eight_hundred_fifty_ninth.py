#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import subprocess
from pathlib import Path


HERE = Path(__file__).resolve().parent
PREFIX = "EIGHT_HUNDRED_FIFTY_NINTH"


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    subprocess.run(["python", str(HERE / "build_eight_hundred_fifty_ninth.py")], check=True)
    cards = read(f"{PREFIX}_24_CARD_SOURCE_MAP.tsv")
    statements = read(f"{PREFIX}_3_STATEMENT_SOURCE_EDITION.tsv")
    states = read(f"{PREFIX}_4_STATE_TRANSITIONS.tsv")
    y_rows = read(f"{PREFIX}_5_Y_RENDERINGS.tsv")
    summary = json.loads((HERE / f"{PREFIX}_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    checks = {
        "inventory": len(cards) == 24 and len(statements) == 3 and len(states) == 4 and len(y_rows) == 5,
        "events": [row["event_id"] for row in cards] == [f"E{i:03d}" for i in range(15, 39)],
        "meanings": all(row["same_card_meaning"] == "YES" for row in cards),
        "atoms": summary["semantic_atoms"] == 42 and summary["atom_distribution"] == {"1": 14, "2": 5, "3": 2, "4": 3},
        "state": summary["state_resets"] == 0 and summary["explicit_closes"] == 0,
        "Y_identity": all(row["exact_card_id"] == "PROC019" and row["same_Y_card"] == "YES" for row in y_rows) and summary["Y_surfaces"] == ["chy", "dy", "shy"],
        "source_complete": all(row["latin_like_source_statement"] and row["mixed_workshop_shorthand"] for row in statements),
        "no_unmapped": summary["unmapped_cards"] == 0,
        "sealed_pages": summary["sealed_pages"] == ["f84", "f84r"],
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / f"{PREFIX}_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
