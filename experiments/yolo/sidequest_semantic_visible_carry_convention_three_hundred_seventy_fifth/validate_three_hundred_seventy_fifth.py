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
    conventions = read("THREE_HUNDRED_SEVENTY_FIFTH_THREE_CONVENTIONS.tsv")
    cases = read("THREE_HUNDRED_SEVENTY_FIFTH_THREE_DECISION_CASES.tsv")
    lines = read("THREE_HUNDRED_SEVENTY_FIFTH_SIX_MARKED_LINES.tsv")
    checks = {
        "three_candidates": len(conventions) == 3 and sum(r["selected"] == "YES" for r in conventions) == 1,
        "gap_selected": next(r for r in conventions if r["selected"] == "YES")["candidate"] == "EXTRA_MARGIN_GAP",
        "no_new_glyph": next(r for r in conventions if r["selected"] == "YES")["new_glyphs"] == "0",
        "three_cases": len(cases) == 3,
        "two_licensed": sum(r["corrector_decision"] == "LICENSED_READ_ONCE" for r in cases) == 2,
        "licensed_have_double_gap": all(r["gap_units_before_margin_form"] == "2" for r in cases if r["corrector_decision"] == "LICENSED_READ_ONCE"),
        "unmarked_not_licensed": all(r["corrector_decision"] != "LICENSED_READ_ONCE" for r in cases if r["gap_units_before_margin_form"] != "2"),
        "six_lines": len(lines) == 6 and len({r["layout_id"] for r in lines}) == 2,
    }
    status = "PASS" if all(checks.values()) else "FAIL"
    payload = {"status": status, "checks": checks, "check_count": len(checks)}
    (HERE / "THREE_HUNDRED_SEVENTY_FIFTH_VALIDATION.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if status != "PASS": raise SystemExit(json.dumps(payload, ensure_ascii=False, indent=2))
    print(f"PASS {len(checks)} checks")


if __name__ == "__main__":
    main()
