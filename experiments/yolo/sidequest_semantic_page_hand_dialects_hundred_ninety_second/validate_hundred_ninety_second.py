#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path


OUT = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    events = read("HUNDRED_NINETY_SECOND_381_EVENT_PAGE_HAND_PROFILE.tsv")
    corrections = read("HUNDRED_NINETY_SECOND_8_PAGE_HAND_CORRECTIONS.tsv")
    pages = read("HUNDRED_NINETY_SECOND_7_PAGE_RENDERER_FINGERPRINTS.tsv")
    hands = read("HUNDRED_NINETY_SECOND_4_HAND_PROFILE_SUMMARY.tsv")
    summary = json.loads((OUT / "BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    checks = {
        "381_events": len(events) == 381 and len({row["event_id"] for row in events}) == 381,
        "eight_corrections": len(corrections) == 8,
        "seven_pages": len(pages) == 7,
        "four_profiles": len(hands) == 4,
        "selected_corrections_positive": all(int(row["net_gain"]) > 0 for row in corrections if row["selected_for_profile"] == "YES"),
        "rejected_candidates_nonpositive": all(int(row["net_gain"]) <= 0 for row in corrections if row["selected_for_profile"] == "NO"),
        "exact_sum": summary["page_hand_exact"] == sum(row["page_hand_match"] == "YES" for row in events),
        "gain_sum": summary["net_gain"] == sum(int(row["net_gain"]) for row in corrections if row["selected_for_profile"] == "YES"),
        "hand_partition": sum(int(row["events"]) for row in hands) == 381,
        "all_registered": all(row["surface_registered"] == "YES" for row in events),
        "sealed_absent": summary["sealed_pages_accessed"] is False,
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks, "summary": summary}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
