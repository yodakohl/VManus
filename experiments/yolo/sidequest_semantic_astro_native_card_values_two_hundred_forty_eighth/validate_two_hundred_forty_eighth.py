#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def rows(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    cards = rows("TWO_HUNDRED_FORTY_EIGHTH_29_DIAGRAM_NATIVE_CARDS.tsv")
    groups = rows("TWO_HUNDRED_FORTY_EIGHTH_REVISED_395_GROUP_MANUAL.tsv")
    feedback = rows("TWO_HUNDRED_FORTY_EIGHTH_FIVE_PROSE_FEEDBACK_REVISIONS.tsv")
    checks = {
        "29_cards": len(cards) == 29,
        "395_groups": len(groups) == 395,
        "five_feedback_revisions": len(feedback) == 5,
        "sixteen_additional_revised": sum(r["value_scope"] == "REGISTER_NEUTRAL_CORE_WITH_LOCAL_EXPANSION" for r in cards) == 16,
        "thirteen_common_retained": sum(r["value_scope"] == "THREE_REGISTER_COMMON" for r in cards) == 13,
        "all_card_values_concrete": all(r["diagram_native_value_de"].strip() for r in cards),
        "all_group_cores_present": all(r["portable_card_core_de"].strip() for r in groups),
        "expected_feedback": {r["card_family"] for r in feedback} == {"OKEY", "OKEEY", "CHO", "OS", "ODY"},
        "no_wet_literal_in_additional": all(not any(word in r["diagram_native_value_de"].lower() for word in ("wasser", "zutat", "gefäß", "abkühl", "einwirk")) for r in cards if r["value_scope"] == "REGISTER_NEUTRAL_CORE_WITH_LOCAL_EXPANSION"),
        "sealed_pages_absent": all("f84" not in "\t".join(r.values()).lower() for r in groups),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "VALIDATION.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        print(json.dumps(result, indent=2, ensure_ascii=False))
        raise SystemExit(1)
    print(f"PASS {sum(checks.values())}/{len(checks)}")


if __name__ == "__main__":
    main()
