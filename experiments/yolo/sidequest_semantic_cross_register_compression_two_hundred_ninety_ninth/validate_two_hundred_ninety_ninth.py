#!/usr/bin/env python3
"""Validate Pass 299 compression audit."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def main() -> None:
    audit = read("TWO_HUNDRED_NINETY_NINTH_12_COMPRESSION_AUDIT.tsv")
    clean = read("TWO_HUNDRED_NINETY_NINTH_2_CLEAN_PROSE_SHORTENINGS.tsv")
    counts = Counter(row["compression_decision"] for row in audit)
    checks = {
        "twelve_leads": len(audit) == 12,
        "two_clean": counts["CLEAN_TWO_TO_ONE_SHORTENING"] == 2,
        "three_no_site": counts["NO_LOCAL_PROSE_SITE"] == 3,
        "seven_nuance_loss": counts["NUANCE_LOSS__KEEP_ASTRO_OR_FUTURE_PROSE"] == 7,
        "clean_rows_2": len(clean) == 2,
        "clean_surfaces": {row["hypothetical_compact_card"] for row in clean} == {"olar", "saral"},
        "clean_windows_two_cards": all(len(row["original_event_ids"].split(",")) == 2 for row in clean),
        "visible_text_not_replaced": all(row["manuscript_edit_policy"] == "DO_NOT_REPLACE_VISIBLE_TEXT__USE_AS_FORWARD_WRITING_PREDICTION" for row in audit),
        "no_sealed_page": not any("f" + "84" in path.read_text(encoding="utf-8").lower() for path in [HERE / "TWO_HUNDRED_NINETY_NINTH_12_COMPRESSION_AUDIT.tsv", HERE / "TWO_HUNDRED_NINETY_NINTH_TWO_COMPACT_WRITING_EXAMPLES.md", HERE / "TWO_HUNDRED_NINETY_NINTH_REPORT.md"]),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks, "failed": [key for key, value in checks.items() if not value]}
    (HERE / "VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result))
    raise SystemExit(0 if result["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
