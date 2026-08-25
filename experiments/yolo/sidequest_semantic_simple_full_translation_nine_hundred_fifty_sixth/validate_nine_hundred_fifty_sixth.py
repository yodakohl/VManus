#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import subprocess
from pathlib import Path


OUT = Path(__file__).resolve().parent


def rows(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    subprocess.run(["python3", str(OUT / "build_nine_hundred_fifty_sixth.py")], check=True)
    prose = rows("PASS956_2010_SIMPLE_PROSE_INTERLINEAR.tsv")
    clauses = rows("PASS956_354_SIMPLE_CLAUSE_TRANSLATIONS.tsv")
    prose_ids = [row["event_id"] for row in prose]
    clause_ids = [event for row in clauses for event in row["event_ids"].split("|")]
    checks = [
        ("prose_2010", len(prose) == 2010, len(prose)),
        ("clauses_354", len(clauses) == 354, len(clauses)),
        ("prose_unique", len(set(prose_ids)) == 2010, "unique"),
        ("clause_partition", clause_ids == prose_ids, len(clause_ids)),
        ("clause_sum", sum(int(row["events"]) for row in clauses) == 2010, "sum"),
        ("all_cards_read", all(row["simple_card_reading_de"].strip() for row in prose), "read"),
        ("all_clauses_read", all(row["simple_continuous_reading_de"].strip() for row in clauses), "read"),
        ("all_surface_bound", all("=" in row["surface_equals_reading"] for row in clauses), "bound"),
        ("sealed_absent", "f84" not in "".join(str(row) for row in prose).lower(), "sealed"),
    ]
    result = {"status": "PASS" if all(ok for _, ok, _ in checks) else "FAIL", "checks": [{"name": name, "pass": ok, "detail": detail} for name, ok, detail in checks]}
    (OUT / "PASS956_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
