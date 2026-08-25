#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import subprocess
from pathlib import Path


HERE = Path(__file__).resolve().parent
PREFIX = "EIGHT_HUNDRED_SIXTY_FIRST"


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    subprocess.run(["python", str(HERE / "build_eight_hundred_sixty_first.py")], check=True)
    cards = read(f"{PREFIX}_17_CARD_PAGE_EDITION.tsv")
    statements = read(f"{PREFIX}_4_STATEMENT_LAYER_MAP.tsv")
    registers = read(f"{PREFIX}_5_REGISTER_STORY.tsv")
    comparison = read(f"{PREFIX}_F10R_F11R_COMPARISON.tsv")
    summary = json.loads((HERE / f"{PREFIX}_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    checks = {
        "inventory": len(cards) == 17 and len(statements) == 4 and len(registers) == 5 and len(comparison) == 2,
        "events": [row["event_id"] for row in cards] == [f"E{i:03d}" for i in range(39, 56)],
        "meanings": all(row["same_card_meaning"] == "YES" for row in cards),
        "atoms": summary["semantic_atoms"] == 38 and sum(int(row["semantic_atoms"]) for row in statements) == 38,
        "close": summary["closes"] == 1 and sum(int(row["closes"]) for row in statements) == 1,
        "resume": summary["resume_whole_cards"] == 1 and sum(int(row["resume_cards"]) for row in statements) == 1,
        "picture": summary["picture_owners"] == 1,
        "comparison": {row["page"] for row in comparison} == {"f10r", "f11r"},
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
