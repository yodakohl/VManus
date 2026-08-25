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
    defaults = read("SEVEN_HUNDRED_EIGHTIETH_24_HAND_CARD_DEFAULTS.tsv")
    contexts = read("SEVEN_HUNDRED_EIGHTIETH_34_CONTEXT_RENDERER_ROWS.tsv")
    trace = read("SEVEN_HUNDRED_EIGHTIETH_381_FULL_CROSS_HAND_TRACE.tsv")
    directions = read("SEVEN_HUNDRED_EIGHTIETH_2_FULL_RECOPY_DIRECTIONS.tsv")
    rules = read("SEVEN_HUNDRED_EIGHTIETH_6_RECOPY_RULES.tsv")
    summary = json.loads((HERE / "SEVEN_HUNDRED_EIGHTIETH_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    direction = {row["source_hand"]: row for row in directions}
    checks = {
        "counts_24_34_381_2_6": (len(defaults), len(contexts), len(trace), len(directions), len(rules)) == (24, 34, 381, 2, 6),
        "twelve_cards_two_hands": len({row["exact_card_id"] for row in defaults}) == 12 and all(sum(entry["exact_card_id"] == row["exact_card_id"] for entry in defaults) == 2 for row in defaults),
        "event_ids_exact": [row["event_id"] for row in trace] == [f"E{i:03d}" for i in range(1, 382)],
        "coverage_106_275": (sum(row["access"] == "COMMON_12_HAND_RENDERER" for row in trace), sum(row["access"] == "LOCAL_CARD_MODEL" for row in trace)) == (106, 275),
        "changes84": sum(row["surface_changed"] == "YES" for row in trace) == 84,
        "all_preserved": all(row["identity_recipe_meaning_preserved"] == "YES" for row in trace),
        "hand1_direction_82_34_48_26": tuple(int(direction["HAND_1"][key]) for key in ("events", "common_renderer_events", "local_model_events", "surface_changes")) == (82, 34, 48, 26),
        "hand2_direction_299_72_227_58": tuple(int(direction["HAND_2"][key]) for key in ("events", "common_renderer_events", "local_model_events", "surface_changes")) == (299, 72, 227, 58),
        "local_models_unchanged": all(row["surface_changed"] == "NO" for row in trace if row["access"] == "LOCAL_CARD_MODEL"),
        "fixed_pages_only": all("f84" not in "\t".join(row.values()).lower() for rows in (defaults, contexts, trace, directions, rules) for row in rows),
        "summary_pass": summary["status"] == "PASS" and summary["preserved_events"] == 381,
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SEVEN_HUNDRED_EIGHTIETH_VALIDATION.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
