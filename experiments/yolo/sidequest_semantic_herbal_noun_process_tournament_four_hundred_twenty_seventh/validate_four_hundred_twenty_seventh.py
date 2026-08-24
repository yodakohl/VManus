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
    candidates = read("FOUR_HUNDRED_TWENTY_SEVENTH_TWENTY_CANDIDATES.tsv")
    decisions = read("FOUR_HUNDRED_TWENTY_SEVENTH_FIVE_DECISIONS.tsv")
    events = read("FOUR_HUNDRED_TWENTY_SEVENTH_REVISED_HERBAL_100_EVENT_EDITION.tsv")
    provenance = read("FOUR_HUNDRED_TWENTY_SEVENTH_IMAGE_PROCESS_PROVENANCE.tsv")
    articles = read("FOUR_HUNDRED_TWENTY_SEVENTH_FIVE_ARTICLE_READINGS.tsv")
    checks = {
        "twenty_candidates": len(candidates) == 20,
        "one_selected_per_record": all(sum(row["record"] == record and row["decision"] == "SELECT" for row in candidates) == 1 for record in ["H1", "H2", "H3", "H4", "H5"]),
        "five_decisions": len(decisions) == 5,
        "two_revisions": sum(row["changed"] == "YES" for row in decisions) == 2,
        "three_retentions": sum(row["changed"] == "NO" for row in decisions) == 3,
        "selected_values": {row["selected_value_de"] for row in decisions} == {"Knolle", "Schüssel", "Blütenkraut", "abkühlen; Schluss", "ausziehen"},
        "one_hundred_events": len(events) == 100,
        "two_revised_rows": sum(row["pass427_decision"] == "REVISED" for row in events) == 2,
        "five_provenance_rows": len(provenance) == 5,
        "five_articles": len(articles) == 5,
        "sealed_pages_absent": all("f84" not in value.lower() for rows in (candidates, decisions, events, provenance, articles) for row in rows for value in row.values()),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FOUR_HUNDRED_TWENTY_SEVENTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(result)


if __name__ == "__main__":
    main()
