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
    events = read("HUNDRED_NINETIETH_381_EVENT_GLOBAL_PROFILE.tsv")
    rules = read("HUNDRED_NINETIETH_5_RULE_GLOBAL_AUDIT.tsv")
    cards = read("HUNDRED_NINETIETH_173_CARD_ACCURACY.tsv")
    residuals = read("HUNDRED_NINETIETH_RESIDUAL_TRANSFORMATIONS.tsv")
    summary = json.loads((OUT / "BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    checks = {
        "381_events": len(events) == 381 and len({row["event_id"] for row in events}) == 381,
        "135_fields": len({row["field_id"] for row in events}) == 135,
        "173_cards": len(cards) == 173 and len({row["master_card_id"] for row in cards}) == 173,
        "five_rules": len(rules) == 5 and {row["rule_id"] for row in rules} == {f"R{i}" for i in range(1, 6)},
        "event_positions_valid": all(row["position_class"] in {"ONLY", "INITIAL", "MEDIAL", "FINAL"} for row in events),
        "all_predictions_registered": all(row["predicted_surface_registered"] == "YES" for row in events),
        "summary_counts_match": summary["five_rule_exact"] == sum(row["profile_matches"] == "YES" for row in events),
        "residual_counts_match": summary["remaining_residual_events"] == sum(int(row["event_count"]) for row in residuals),
        "rule_trigger_counts_match": summary["five_rule_triggers"] == sum(int(row["global_triggers"]) for row in rules),
        "allowed_pages_only": {row["page"] for row in events} == {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"},
        "sealed_absent": summary["sealed_pages_accessed"] is False,
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks, "summary": summary}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
