#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import subprocess
from pathlib import Path


HERE = Path(__file__).resolve().parent
PREFIX = "EIGHT_HUNDRED_SIXTY_THIRD"


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    subprocess.run(["python", str(HERE / "build_eight_hundred_sixty_third.py")], check=True)
    cards = read(f"{PREFIX}_27_CARD_PAGE_EDITION.tsv")
    statements = read(f"{PREFIX}_6_STATEMENT_LAYER_MAP.tsv")
    ho_rows = read(f"{PREFIX}_4_HO_INGREDIENT_OCCURRENCES.tsv")
    registers = read(f"{PREFIX}_6_REGISTER_STORY.tsv")
    summary = json.loads((HERE / f"{PREFIX}_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    checks = {
        "inventory": len(cards) == 27 and len(statements) == 6 and len(ho_rows) == 4 and len(registers) == 6,
        "events": [row["event_id"] for row in cards] == [f"E{i:03d}" for i in range(74, 101)],
        "meanings": all(row["same_card_meaning"] == "YES" for row in cards),
        "atoms": summary["semantic_atoms"] == 58 and sum(int(row["semantic_atoms"]) for row in statements) == 58,
        "HO_identity": all(row["exact_card_id"] == "PROC052" and row["portable_card_meaning_de"] == "ZUTAT" and row["same_card"] == "YES" for row in ho_rows),
        "HO_surfaces": summary["HO_surfaces_in_order"] == ["cho", "sho", "cho", "sho"],
        "HO_not_owner_operation": summary["HO_picture_owner_claims"] == 0 and summary["HO_operation_claims"] == 0,
        "close": summary["closes"] == 1,
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
