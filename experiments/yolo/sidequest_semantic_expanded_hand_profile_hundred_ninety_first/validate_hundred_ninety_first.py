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
    events = read("HUNDRED_NINETY_FIRST_381_EVENT_EXPANDED_PROFILE.tsv")
    mappings = read("HUNDRED_NINETY_FIRST_19_POSITIONAL_MAPPINGS.tsv")
    rules = read("HUNDRED_NINETY_FIRST_6_SECOND_LAYER_RULES.tsv")
    residuals = read("HUNDRED_NINETY_FIRST_REMAINING_RESIDUALS.tsv")
    summary = json.loads((OUT / "BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    checks = {
        "381_events": len(events) == 381 and len({row["event_id"] for row in events}) == 381,
        "19_mappings": len(mappings) == 19,
        "six_rule_groups": len(rules) == 6,
        "all_mapping_gains_positive": all(int(row["net_gain"]) > 0 for row in mappings),
        "all_group_gains_positive": all(int(row["net_gain"]) > 0 for row in rules),
        "summary_exact": summary["expanded_exact"] == sum(row["expanded_match"] == "YES" for row in events),
        "summary_gain": summary["net_gain"] == summary["expanded_exact"] - summary["base_exact"],
        "residual_sum": summary["remaining_residual_events"] == sum(int(row["events"]) for row in residuals),
        "all_surfaces_registered": all(row["surface_registered"] == "YES" for row in events),
        "allowed_pages": {row["page"] for row in events} == {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"},
        "sealed_absent": summary["sealed_pages_accessed"] is False,
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks, "summary": summary}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
