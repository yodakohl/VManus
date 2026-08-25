#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import subprocess
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    subprocess.run(["python", str(HERE / "build_eight_hundredth.py")], check=True)
    cards = read("EIGHT_HUNDREDTH_58_RELEVANT_CARDS.tsv")
    families = read("EIGHT_HUNDREDTH_SHARED_TAILS.tsv")
    reads = read("EIGHT_HUNDREDTH_12_ACTION_READBACKS.tsv")
    stacks = read("EIGHT_HUNDREDTH_STACKED_COUNTEREXAMPLES.tsv")
    decisions = read("EIGHT_HUNDREDTH_6_COMPONENT_DECISIONS.tsv")
    summary = json.loads((HERE / "EIGHT_HUNDREDTH_BUILD_SUMMARY.json").read_text(encoding="utf-8"))

    checks = {
        "inventory_58_unique_cards": len(cards) == 58 and len({row["exact_card_id"] for row in cards}) == 58,
        "action_union_41_cards_54_events": summary["action_union_cards"] == 41 and summary["action_union_events"] == 54,
        "o_union_30_cards_42_events": summary["o_union_cards"] == 30 and summary["o_union_events"] == 42,
        "one_complete_action_microparadigm": summary["complete_action_microparadigms"] == 1,
        "four_source_events_twelve_readbacks": summary["action_source_events"] == 4 and len(reads) == 12,
        "all_readbacks_fix_tail_owner_statement": all(row["fixed_tail"] == "E+Y" and row["owner_fixed"] == "YES" and row["other_statement_events_fixed"] == "YES" for row in reads),
        "six_component_decisions": len(decisions) == 6 and {row["component"] for row in decisions} == {"CH", "SH", "CTH", "O", "OR", "HO"},
        "action_promoted_o_strip_retained": all(row["new_tier"] == "PARADIGM_CORE18" for row in decisions[:3]) and all(row["new_tier"] == "RECURRENT_RULE_STRIP" for row in decisions[3:]),
        "five_stacked_counterexamples": len(stacks) == 5,
        "o_group_has_three_distinct_level_stacks": sum(row["group"] == "O_OR_HO" for row in stacks) == 3,
        "new_core18_strip13": summary["new_core_size"] == 18 and summary["remaining_recurrent_strip_values"] == 13,
        "fixed_pages_sealed": summary["sealed_pages"] == ["f84", "f84r"] and set(summary["fixed_pages"]) == {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"},
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "EIGHT_HUNDREDTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
