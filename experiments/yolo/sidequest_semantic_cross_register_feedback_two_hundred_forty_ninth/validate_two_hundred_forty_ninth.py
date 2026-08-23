#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent


def rows(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    events = rows("TWO_HUNDRED_FORTY_NINTH_REVISED_381_PROSE_EVENTS.tsv")
    statements = rows("TWO_HUNDRED_FORTY_NINTH_REVISED_116_STATEMENTS.tsv")
    revisions = rows("TWO_HUNDRED_FORTY_NINTH_15_EVENT_REVISIONS.tsv")
    affected = rows("TWO_HUNDRED_FORTY_NINTH_14_AFFECTED_STATEMENTS.tsv")
    counts = Counter(r["master_card_id"] for r in revisions)
    checks = {
        "381_events": len(events) == 381,
        "116_statements": len(statements) == 116,
        "15_revisions": len(revisions) == 15,
        "14_affected_statements": len(affected) == 14,
        "expected_card_counts": counts == {"MC007": 2, "MC002": 7, "MC034": 4, "MC159": 1, "MC100": 1},
        "all_events_have_core": all(r["portable_core_de"].strip() for r in events),
        "all_events_have_local": all(r["local_register_expansion_de"].strip() for r in events),
        "all_statements_complete": all(r["complete_local_translation_de"].strip() for r in statements),
        "366_unchanged": sum(r["value_status"] == "UNCHANGED_PORTABLE_VALUE" for r in events) == 366,
        "seven_fixed_pages": {r["page"] for r in events} == {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"},
        "sealed_pages_absent": all("f84" not in "\t".join(r.values()).lower() for r in events),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "VALIDATION.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        print(json.dumps(result, indent=2, ensure_ascii=False))
        raise SystemExit(1)
    print(f"PASS {sum(checks.values())}/{len(checks)}")


if __name__ == "__main__":
    main()
