#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import subprocess
from pathlib import Path


HERE = Path(__file__).resolve().parent
PREFIX = "EIGHT_HUNDRED_SIXTIETH"


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    subprocess.run(["python", str(HERE / "build_eight_hundred_sixtieth.py")], check=True)
    cards = read(f"{PREFIX}_38_CARD_PAGE_EDITION.tsv")
    statements = read(f"{PREFIX}_5_STATEMENT_LAYER_MAP.tsv")
    registers = read(f"{PREFIX}_5_REGISTER_STORY.tsv")
    summary = json.loads((HERE / f"{PREFIX}_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    checks = {
        "inventory": len(cards) == 38 and len(statements) == 5 and len(registers) == 5,
        "events": [row["event_id"] for row in cards] == [f"E{i:03d}" for i in range(1, 39)],
        "statements": [row["statement_id"] for row in statements] == ["H1-S001", "H1-S002", "H2-S001", "H2-S002", "H2-S003"],
        "atoms": summary["semantic_atoms"] == 73 and sum(int(row["semantic_atoms"]) for row in statements) == 73,
        "layers": all(row["visible_layer"] == "CARD" and row["owner_layer"] == "PICTURE" for row in cards),
        "owner": summary["picture_owners"] == 1,
        "open": summary["explicit_closes"] == 0 and all(row["explicit_close"] == "NO" for row in statements),
        "components": summary["component_event_counts"]["Y"] == 16 and summary["component_event_counts"]["OR"] == 9,
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
