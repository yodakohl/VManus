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
    events = read("FOUR_HUNDRED_FIFTY_NINTH_381_EVENT_FINAL_REVERSE_WRITER.tsv")
    cards = read("FOUR_HUNDRED_FIFTY_NINTH_173_CARD_FINAL_DICTIONARY.tsv")
    rules = read("FOUR_HUNDRED_FIFTY_NINTH_ELEVEN_EXACT_SELECTION_RULES.tsv")
    audit = read("FOUR_HUNDRED_FIFTY_NINTH_61_ALIAS_OCCURRENCE_AUDIT.tsv")
    checks = {
        "events_381": len(events) == 381,
        "event_order": [row["event_id"] for row in events] == [f"E{n:03d}" for n in range(1, 382)],
        "cards_173": len(cards) == 173,
        "rules_11": len(rules) == 11,
        "alias_events_61": len(audit) == 61,
        "selection_partition": [sum(row["selection_layer"] == layer for row in events) for layer in ("UNIQUE_VALUE", "LOCAL_CONTEXT", "STATEMENT_POSITION", "RECORD_RENDERER")] == [320, 24, 21, 16],
        "exact_recovery_381": all(row["exact_card_recovered"] == "YES" for row in events),
        "alias_recovery_61": all(row["recovered"] == "YES" for row in audit),
        "six_whole_card_events_9": sum(row["lexicon_class"] == "MEMORIZED_WHOLE_CARD" for row in events) == 9,
        "productive_events_372": sum(row["lexicon_class"] == "PRODUCTIVE_COMPOSITION" for row in events) == 372,
        "fixed_pages": {row["page"] for row in events} == {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"},
        "sealed_absent": all("f84" not in (row["page"] + row["locus"]).lower() for row in events),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FOUR_HUNDRED_FIFTY_NINTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(result)


if __name__ == "__main__":
    main()
