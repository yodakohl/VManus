#!/usr/bin/env python3
"""Validate repaired Herbal-to-Bio handoffs."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    handoffs = read("THREE_HUNDRED_THIRTY_FIRST_FIVE_REPAIRED_HANDOFFS.tsv")
    anchors = read("THREE_HUNDRED_THIRTY_FIRST_SEVEN_EXACT_ANCHORS.tsv")
    checks = {
        "five_handoffs": len(handoffs) == 5,
        "all_five_records": {x["herbal_record"] for x in handoffs} == {"H1", "H2", "H3", "H4", "H5"},
        "all_survive": all(x["handoff_status"] == "SURVIVES_REPAIRED_DICTIONARY" for x in handoffs),
        "seven_anchors": len(anchors) == 7,
        "every_handoff_anchored": all(int(x["exact_shared_anchor_count"]) >= 1 for x in handoffs),
        "same_identity_and_value": all(x["same_identity"] == "YES" and x["same_atomic_value"] == "YES" for x in anchors),
        "withdrawals_explicit": all(x["withdrawn_old_dependencies"] for x in handoffs),
        "no_direct_pointer": all(x["direct_cross_page_pointer"] == "NONE" for x in handoffs),
        "no_sealed_page": all("f84" not in (x["herbal_page"] + x["bio_page"]).lower() for x in handoffs),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "THREE_HUNDRED_THIRTY_FIRST_VALIDATION.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
