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
    subprocess.run(["python3", str(OUT / "build_nine_hundred_fiftieth.py")], check=True)
    events = rows("PASS950_2010_EXTENDED_CARD_INTERLINEAR.tsv")
    clauses = rows("PASS950_354_EXTENDED_CARD_CLAUSES.tsv")
    event_ids = [row["event_id"] for row in events]
    clause_ids = [event_id for row in clauses for event_id in row["event_ids"].split("|")]
    checks = [
        ("events_2010", len(events) == 2010, len(events)),
        ("clauses_354", len(clauses) == 354, len(clauses)),
        ("events_unique", len(set(event_ids)) == 2010, "unique"),
        ("clause_partition", clause_ids == event_ids, len(clause_ids)),
        ("clause_event_sum", sum(int(row["events"]) for row in clauses) == 2010, "sum"),
        ("all_literal", all(row["literal_card_chain_de"].strip() for row in clauses), "literal"),
        ("all_continuous", all(row["continuous_workshop_reading_de"].strip() for row in clauses), "continuous"),
        ("promotions_present", sum(int(row["newly_promoted_events"]) for row in clauses) > 0, "promoted"),
        ("sealed_absent", "f84" not in "".join(str(row) for row in events).lower(), "sealed"),
    ]
    result = {"status": "PASS" if all(ok for _, ok, _ in checks) else "FAIL", "checks": [{"name": name, "pass": ok, "detail": detail} for name, ok, detail in checks]}
    (OUT / "PASS950_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
