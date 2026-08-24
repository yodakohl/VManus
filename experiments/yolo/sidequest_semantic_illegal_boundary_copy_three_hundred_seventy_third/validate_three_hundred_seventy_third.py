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
    visible = read("THREE_HUNDRED_SEVENTY_THIRD_TEN_VISIBLE_FORMS.tsv")
    boundaries = read("THREE_HUNDRED_SEVENTY_THIRD_TWO_BOUNDARY_DECISIONS.tsv")
    actions = read("THREE_HUNDRED_SEVENTY_THIRD_TEN_CORRECTOR_ACTIONS.tsv")
    result = read("THREE_HUNDRED_SEVENTY_THIRD_RECONSTRUCTION.tsv")[0]
    checks = {
        "ten_visible": len(visible) == 10,
        "two_boundaries": len(boundaries) == 2,
        "one_legal": sum(r["corrector_decision"] == "LEGAL_READ_ONCE_ANTICIPATION" for r in boundaries) == 1,
        "one_illegal": sum(r["corrector_decision"] == "ILLEGAL_DUPLICATE_AT_REAL_RESET" for r in boundaries) == 1,
        "illegal_has_slot_drop": all(r["slot_drop_before_repeated_card"] == "YES" for r in boundaries if r["corrector_decision"] == "ILLEGAL_DUPLICATE_AT_REAL_RESET"),
        "distinct_removal_actions": {r["corrector_action"] for r in actions if r["source_contribution"] == "0"} == {"REMOVE_LICENSED_MARGIN_COPY", "DELETE_AND_MARK_SCRIBAL_ERROR"},
        "eight_sources": sum(int(r["source_contribution"]) for r in actions) == 8,
        "exact_result": result["exact_reconstruction"] == result["illegal_copy_not_licensed"] == "YES",
    }
    status = "PASS" if all(checks.values()) else "FAIL"
    payload = {"status": status, "checks": checks, "check_count": len(checks)}
    (HERE / "THREE_HUNDRED_SEVENTY_THIRD_VALIDATION.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if status != "PASS": raise SystemExit(json.dumps(payload, ensure_ascii=False, indent=2))
    print(f"PASS {len(checks)} checks")


if __name__ == "__main__":
    main()
