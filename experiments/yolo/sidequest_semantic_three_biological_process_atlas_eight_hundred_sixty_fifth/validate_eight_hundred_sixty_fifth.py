#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import subprocess
from pathlib import Path


HERE = Path(__file__).resolve().parent
PREFIX = "EIGHT_HUNDRED_SIXTY_FIFTH"


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    subprocess.run(["python", str(HERE / "build_eight_hundred_sixty_fifth.py")], check=True)
    cards = read(f"{PREFIX}_281_CARD_BIOLOGICAL_ATLAS.tsv")
    statements = read(f"{PREFIX}_97_STATEMENT_BIOLOGICAL_ATLAS.tsv")
    records = read(f"{PREFIX}_6_RECORD_PROCESS_PROFILES.tsv")
    pages = read(f"{PREFIX}_3_PAGE_PROCESS_PROFILES.tsv")
    shared = read(f"{PREFIX}_17_HERBAL_BIOLOGICAL_SHARED_CARDS.tsv")
    comparison = read(f"{PREFIX}_HERBAL_BIOLOGICAL_TEXT_TYPE_COMPARISON.tsv")
    summary = json.loads((HERE / f"{PREFIX}_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    checks = {
        "inventory": len(cards) == 281 and len(statements) == 97 and len(records) == 6 and len(pages) == 3 and len(shared) == 17 and len(comparison) == 2,
        "events": [row["event_id"] for row in cards] == [f"E{i:03d}" for i in range(101, 382)],
        "pages": {row["page"] for row in pages} == {"f81v", "f82r", "f83r"},
        "atoms": summary["semantic_atoms"] == 644 and sum(int(row["semantic_atoms"]) for row in records) == 644,
        "owners": summary["owners"] == 16,
        "closure": summary["closed_statements"] == 85 and summary["open_statements"] == 12,
        "shared": summary["shared_herbal_exact_cards"] == 17 and summary["shared_herbal_biological_events"] == 92 and summary["bio_local_events"] == 189,
        "compatible": all(row["application_compatible"] == "YES" for row in shared),
        "no_direct_join": summary["direct_herbal_crossreferences"] == 0,
        "sealed_pages": summary["sealed_pages"] == ["f84", "f84r"],
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / f"{PREFIX}_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
