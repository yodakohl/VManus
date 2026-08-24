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
    candidates = read("FOUR_HUNDRED_TWENTY_SIXTH_TWENTY_CANDIDATES.tsv")
    selected = read("FOUR_HUNDRED_TWENTY_SIXTH_FIVE_SELECTED_VALUES.tsv")
    events = read("FOUR_HUNDRED_TWENTY_SIXTH_REVISED_HERBAL_100_EVENT_EDITION.tsv")
    articles = read("FOUR_HUNDRED_TWENTY_SIXTH_FIVE_REVISED_ARTICLES.tsv")
    checks = {
        "twenty_candidates": len(candidates) == 20,
        "four_per_record": all(sum(row["record"] == record for row in candidates) == 4 for record in ["H1", "H2", "H3", "H4", "H5"]),
        "one_selected_per_record": all(sum(row["record"] == record and row["decision"] == "SELECT" for row in candidates) == 1 for record in ["H1", "H2", "H3", "H4", "H5"]),
        "five_selected_values": len(selected) == 5,
        "selected_set": {row["selected_value_de"] for row in selected} == {"schälen", "Brei", "Trank", "lagern", "erste Zutat"},
        "one_hundred_events": len(events) == 100,
        "five_revised_event_rows": sum(row["pass426_revision"] != "UNCHANGED" for row in events) == 5,
        "five_articles": len(articles) == 5,
        "sealed_pages_absent": all("f84" not in value.lower() for rows in (candidates, selected, events, articles) for row in rows for value in row.values()),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FOUR_HUNDRED_TWENTY_SIXTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(result)


if __name__ == "__main__":
    main()
