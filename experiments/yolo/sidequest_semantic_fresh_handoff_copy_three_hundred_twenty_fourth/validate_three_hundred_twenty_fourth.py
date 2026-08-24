#!/usr/bin/env python3
"""Validate the fresh two-passage workshop copy."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    passages = read("THREE_HUNDRED_TWENTY_FOURTH_TWO_FRESH_PASSAGES.tsv")
    events = read("THREE_HUNDRED_TWENTY_FOURTH_14_RENDERED_EVENTS.tsv")
    roundtrip = read("THREE_HUNDRED_TWENTY_FOURTH_14_EVENT_ROUNDTRIP.tsv")
    checks = {
        "two_passages": len(passages) == 2,
        "fourteen_events": len(events) == 14,
        "fourteen_unique_events": len({x["new_event_id"] for x in events}) == 14,
        "all_cards_registered": all(x["card_identity_status"] == "ALREADY_REGISTERED" for x in events),
        "no_new_card_identity": all(x["all_cards_preexisting"] == "YES" for x in passages),
        "both_full_sequences_fresh": all(x["full_sequence_preexisting"] == "NO" for x in passages),
        "both_cross_line": all(x["line_break_is_statement_break"] == "NO" for x in passages),
        "one_open_one_closed": {x["terminal_status"] for x in passages} == {"OPEN_HANDOFF", "CLOSED_LOCAL_STEP"},
        "roundtrip_all": len(roundtrip) == 14 and all(x["identity_match"] == "YES" and x["meaning_match"] == "YES" for x in roundtrip),
        "not_manuscript_claim": all(x["manuscript_text_claim"] == "NO_CREATIVE_WORKSHOP_DEMONSTRATION" for x in passages),
        "no_sealed_page": all("f84" not in "\t".join(x.values()).lower() for rows in [passages, events, roundtrip] for x in rows),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "THREE_HUNDRED_TWENTY_FOURTH_VALIDATION.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
