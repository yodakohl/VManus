#!/usr/bin/env python3
"""Validate Pass 300 statement-style edition."""

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
    statements = read("THREE_HUNDREDTH_116_STATEMENT_WRITING_STYLE.tsv")
    records = read("THREE_HUNDREDTH_11_RECORD_STYLE_SUMMARY.tsv")
    counts = Counter(row["style_decision"] for row in statements)
    checks = {
        "statements_116": len(statements) == 116,
        "events_381": sum(int(row["visible_card_count"]) for row in statements) == 381,
        "records_11": len(records) == 11,
        "single_44": counts["SINGLE_CARD_ALREADY_COMPACT"] == 44,
        "payload_17": counts["RETAIN_LEARNED_PAYLOAD_WITH_ITS_FRAME"] == 17,
        "process_commit_37": counts["RETAIN_PROCESS_SEQUENCE_AND_COMMIT_SCOPE"] == 37,
        "open_multi_16": counts["RETAIN_OPEN_MULTI_SLOT_INSTRUCTION"] == 16,
        "compact_2": counts["COMPACT_ALTERNATIVE_AVAILABLE__VISIBLE_PHRASE_RETAINED"] == 2,
        "compact_cards": {row["available_compact_card"] for row in statements if row["style_decision"].startswith("COMPACT_")} == {"olar", "saral"},
        "visible_sequences_kept": all(row["visible_text_policy"] == "KEEP_EXACT_VISIBLE_SEQUENCE" for row in statements),
        "no_sealed_page": not any("f" + "84" in path.read_text(encoding="utf-8").lower() for path in [HERE / "THREE_HUNDREDTH_116_STATEMENT_WRITING_STYLE.tsv", HERE / "THREE_HUNDREDTH_STATEMENT_STYLE_MANUAL.md", HERE / "THREE_HUNDREDTH_REPORT.md"]),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks, "failed": [key for key, value in checks.items() if not value]}
    (HERE / "VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result))
    raise SystemExit(0 if result["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
