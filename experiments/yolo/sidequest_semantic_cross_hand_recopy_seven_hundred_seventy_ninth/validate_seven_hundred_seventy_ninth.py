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
    events = read("SEVEN_HUNDRED_SEVENTY_NINTH_56_CROSS_HAND_EVENT_RECOPY.tsv")
    statements = read("SEVEN_HUNDRED_SEVENTY_NINTH_9_CROSS_HAND_STATEMENTS.tsv")
    pages = read("SEVEN_HUNDRED_SEVENTY_NINTH_2_RECOPY_SUMMARIES.tsv")
    summary = json.loads((HERE / "SEVEN_HUNDRED_SEVENTY_NINTH_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    by_page = {row["page"]: row for row in pages}
    checks = {
        "counts_56_9_2": (len(events), len(statements), len(pages)) == (56, 9, 2),
        "page_events_18_38": (int(by_page["f55v"]["events"]), int(by_page["f10r"]["events"])) == (18, 38),
        "all_cards_and_meanings_preserved": all(row["card_and_meaning_preserved"] == "YES" for row in events),
        "event_ids_unique": len({row["event_id"] for row in events}) == 56,
        "changes_have_target_evidence": all(row["target_hand_evidence_events"] not in {"", "LOCAL_MODEL_COPY"} for row in events if row["surface_changed"] == "YES"),
        "local_cards_unchanged": all(row["surface_changed"] == "NO" for row in events if row["render_mode"] == "LOCAL_WHOLE_CARD_PRESERVED"),
        "f55_expected_changes4": int(by_page["f55v"]["surface_changes"]) == 4,
        "some_f10_changes": int(by_page["f10r"]["surface_changes"]) > 0,
        "summary_preserves56": summary["cards_preserved"] == summary["meanings_preserved"] == 56,
        "fixed_pages_only": all("f84" not in "\t".join(row.values()).lower() for rows in (events, statements, pages) for row in rows),
        "summary_pass": summary["status"] == "PASS",
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SEVEN_HUNDRED_SEVENTY_NINTH_VALIDATION.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
