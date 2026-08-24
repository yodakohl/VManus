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
    positions = read("THREE_HUNDRED_SEVENTY_EIGHTH_14_POSITION_COLLATION.tsv")
    phenomena = read("THREE_HUNDRED_SEVENTY_EIGHTH_FOUR_PHENOMENA.tsv")
    visible = read("THREE_HUNDRED_SEVENTY_EIGHTH_TRAINEE_VISIBLE_FORMS.tsv")
    result = read("THREE_HUNDRED_SEVENTY_EIGHTH_CORRECTION_RESULT.tsv")[0]
    checks = {
        "14_positions": len(positions) == 14,
        "eight_variants": sum(r["collation_category"] == "REGISTERED_SURFACE_VARIANT" for r in positions) == 8,
        "one_omission": sum(r["collation_category"] == "TRUE_OMISSION" for r in positions) == 1,
        "omission_is_cphy": next(r for r in positions if r["collation_category"] == "TRUE_OMISSION")["expected_second_surface"] == "cphy",
        "four_phenomena": len(phenomena) == 4 and len({r["category"] for r in phenomena}) == 4,
        "14_visible_13_source": len(visible) == 14 and sum(int(r["source_contribution"]) for r in visible) == 13,
        "meaning_unchanged": all(r["meaning_changed"] == "NO" for r in positions),
        "restored_14": result["corrected_source_cards"] == "14" and result["exact_after_correction"] == "YES",
    }
    status = "PASS" if all(checks.values()) else "FAIL"
    payload = {"status": status, "checks": checks, "check_count": len(checks)}
    (HERE / "THREE_HUNDRED_SEVENTY_EIGHTH_VALIDATION.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if status != "PASS": raise SystemExit(json.dumps(payload, ensure_ascii=False, indent=2))
    print(f"PASS {len(checks)} checks")


if __name__ == "__main__":
    main()
