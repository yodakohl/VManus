#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import subprocess
from collections import Counter
from pathlib import Path


OUT = Path(__file__).resolve().parent


def rows(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    subprocess.run(["python3", str(OUT / "build_nine_hundred_fifty_eighth.py")], check=True)
    events = rows("PASS958_2511_CANONICAL_EVENT_DICTIONARY.tsv")
    prose = rows("PASS958_2010_CANONICAL_PROSE_INTERLINEAR.tsv")
    clauses = rows("PASS958_354_CANONICAL_CLAUSE_TRANSLATIONS.tsv")
    pages = rows("PASS958_14_CANONICAL_PAGE_READINGS.tsv")
    counts = Counter(row["codebook_layer"] for row in events)
    clause_ids = [event for row in clauses for event in row["event_ids"].split("|")]
    checks = [
        ("events_2511", len(events) == 2511, len(events)),
        ("prose_2010", len(prose) == 2010, len(prose)),
        ("clauses_354", len(clauses) == 354, len(clauses)),
        ("pages_14", len(pages) == 14, len(pages)),
        ("events_unique", len({row["event_id"] for row in events}) == 2511, "unique"),
        ("prose_unique", len({row["event_id"] for row in prose}) == 2010, "unique"),
        ("clause_partition", clause_ids == [row["event_id"] for row in prose], len(clause_ids)),
        ("page_sum", sum(int(row["events"]) for row in pages) == 2511, "sum"),
        ("productive_1220", counts["PRODUCTIVE_ABBREVIATION_COMPOSITION"] == 1220, counts),
        ("learned_790", counts["LEARNED_FORMULA_CARD"] == 790, counts),
        ("local_501", counts["LOCAL_NOMENCLATOR_OR_ADDRESS"] == 501, counts),
        ("f75_inset_10", sum(row["owner_correction"] == "F75R_TRIANGULAR_INSET_SINGLE_OWNER" for row in events) == 10, "inset"),
        ("all_read", all(row["canonical_card_reading_de"].strip() for row in events), "read"),
        ("sealed_absent", "f84" not in "".join(str(row) for row in events).lower(), "sealed"),
    ]
    result = {"status": "PASS" if all(ok for _, ok, _ in checks) else "FAIL", "checks": [{"name": name, "pass": ok, "detail": str(detail)} for name, ok, detail in checks]}
    (OUT / "PASS958_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
