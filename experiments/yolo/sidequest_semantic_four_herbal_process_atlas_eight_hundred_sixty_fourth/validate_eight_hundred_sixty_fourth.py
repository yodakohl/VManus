#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import subprocess
from pathlib import Path


HERE = Path(__file__).resolve().parent
PREFIX = "EIGHT_HUNDRED_SIXTY_FOURTH"


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    subprocess.run(["python", str(HERE / "build_eight_hundred_sixty_fourth.py")], check=True)
    cards = read(f"{PREFIX}_100_CARD_HERBAL_ATLAS.tsv")
    statements = read(f"{PREFIX}_19_STATEMENT_HERBAL_ATLAS.tsv")
    pages = read(f"{PREFIX}_4_PAGE_PROCESS_PROFILES.tsv")
    shared = read(f"{PREFIX}_8_SHARED_EXACT_CARDS.tsv")
    summary = json.loads((HERE / f"{PREFIX}_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    checks = {
        "inventory": len(cards) == 100 and len(statements) == 19 and len(pages) == 4 and len(shared) == 8,
        "pages": {row["page"] for row in pages} == {"f10r", "f11r", "f55v", "f56r"},
        "events": [row["event_id"] for row in cards] == [f"E{i:03d}" for i in range(1, 101)],
        "atoms": summary["semantic_atoms"] == 206 and sum(int(row["semantic_atoms"]) for row in pages) == 206,
        "cards": summary["exact_card_types"] == 66 and sum(int(row["cards"]) for row in pages) == 100,
        "owners": summary["picture_owners"] == 4,
        "shared": summary["cross_page_exact_card_types"] == 8 and summary["cross_page_exact_card_events"] == 36 and summary["page_local_exact_card_events"] == 64,
        "universal": summary["all_four_page_cards"] == ["PROC009"],
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
