#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    events = read("PASS979_F13R_77_EVENT_ROOT_CROWN_EDITION.tsv")
    clauses = read("PASS979_FIVE_STAGE_ROOT_CROWN_ARTICLE.tsv")
    heads = [r for r in events if r["local_visual_headword_de"] != "NONE"]
    checks = {
        "events_77": len(events) == 77,
        "event_ids_unique": len({r["event_id"] for r in events}) == 77,
        "clauses_5": len(clauses) == 5,
        "clause_events_77": sum(int(r["event_count"]) for r in clauses) == 77,
        "five_headword_events": len(heads) == 5,
        "five_headwords_unique": len({r["local_visual_headword_de"] for r in heads}) == 5,
        "all_concrete": all(r["image_owned_expansion_de"] for r in events),
        "all_clauses_translated": all(r["complete_working_translation_de"] for r in clauses),
        "four_closed_one_open": [r["end_reason"] for r in clauses].count("LICENSED_DY_CLOSE") == 4 and [r["end_reason"] for r in clauses].count("PAGE_END_OPEN") == 1,
        "sealed_absent": all("f84" not in r["locus"].lower() for r in events),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "PASS979_VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
