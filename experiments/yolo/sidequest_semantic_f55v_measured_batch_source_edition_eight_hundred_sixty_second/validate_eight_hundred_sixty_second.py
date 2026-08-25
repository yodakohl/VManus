#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import subprocess
from pathlib import Path


HERE = Path(__file__).resolve().parent
PREFIX = "EIGHT_HUNDRED_SIXTY_SECOND"


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    subprocess.run(["python", str(HERE / "build_eight_hundred_sixty_second.py")], check=True)
    cards = read(f"{PREFIX}_18_CARD_PAGE_EDITION.tsv")
    statements = read(f"{PREFIX}_4_STATEMENT_LAYER_MAP.tsv")
    registers = read(f"{PREFIX}_5_REGISTER_STORY.tsv")
    comparison = read(f"{PREFIX}_F11R_F55V_PROCESS_COMPARISON.tsv")
    summary = json.loads((HERE / f"{PREFIX}_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    checks = {
        "inventory": len(cards) == 18 and len(statements) == 4 and len(registers) == 5 and len(comparison) == 2,
        "events": [row["event_id"] for row in cards] == [f"E{i:03d}" for i in range(56, 74)],
        "meanings": all(row["same_card_meaning"] == "YES" for row in cards),
        "atoms": summary["semantic_atoms"] == 37 and sum(int(row["semantic_atoms"]) for row in statements) == 37,
        "process": summary["quantity_cards"] == 8 and summary["heat_cards"] == 1 and summary["press_or_passage_cards"] == 0 and summary["water_cards"] == 0,
        "closes": summary["closes"] == 2 and sum(int(row["closes"]) for row in statements) == 2,
        "comparison": {row["page"] for row in comparison} == {"f11r", "f55v"},
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
