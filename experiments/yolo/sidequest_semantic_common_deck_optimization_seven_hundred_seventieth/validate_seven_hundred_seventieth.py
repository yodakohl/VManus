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
    ranking = read("SEVEN_HUNDRED_SEVENTIETH_17_COMMON_CARD_RANKING.tsv")
    options = read("SEVEN_HUNDRED_SEVENTIETH_4_CORE_OPTIONS.tsv")
    active = read("SEVEN_HUNDRED_SEVENTIETH_12_ACTIVE_TEACHING_BOARD.tsv")
    reference = read("SEVEN_HUNDRED_SEVENTIETH_5_SHARED_REFERENCE_STRIP.tsv")
    burden = read("SEVEN_HUNDRED_SEVENTIETH_ROLE_LOOKUP_BURDEN.tsv")
    summary = json.loads((HERE / "SEVEN_HUNDRED_SEVENTIETH_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    choice = next(row for row in options if row["decision"] == "SELECT")
    checks = {
        "counts_17_4_12_5_2": (len(ranking), len(options), len(active), len(reference), len(burden)) == (17, 4, 12, 5, 2),
        "ranks_complete": [int(row["rank"]) for row in ranking] == list(range(1, 18)),
        "event_partition_126_10_136": (sum(int(row["events"]) for row in active), sum(int(row["events"]) for row in reference), sum(int(row["events"]) for row in ranking)) == (126, 10, 136),
        "selected_12": choice["core_cards"] == "12" and choice["common136_coverage_pct"] == "92.6",
        "reference_split_5_5": (sum(int(row["herbal_events"]) for row in reference), sum(int(row["bio_events"]) for row in reference)) == (5, 5),
        "burden_rates_5_0_1_8": [row["reference_lookup_rate_pct"] for row in burden] == ["5.0", "1.8"],
        "no_card_loss": {row["exact_card_id"] for row in active}.isdisjoint({row["exact_card_id"] for row in reference}) and {row["exact_card_id"] for row in active + reference} == {row["exact_card_id"] for row in ranking},
        "fixed_pages_only": all("f84" not in "\t".join(row.values()).lower() for rows in (ranking, options, active, reference, burden) for row in rows),
        "summary_pass": summary["status"] == "PASS" and summary["selected_active_cards"] == 12,
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SEVEN_HUNDRED_SEVENTIETH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
