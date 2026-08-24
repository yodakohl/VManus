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
    visible = read("THREE_HUNDRED_SEVENTY_FIRST_EIGHTEEN_VISIBLE_FORMS.tsv")
    boundaries = read("THREE_HUNDRED_SEVENTY_FIRST_FOUR_BOUNDARIES.tsv")
    recon = read("THREE_HUNDRED_SEVENTY_FIRST_SIXTEEN_SOURCE_RECONSTRUCTIONS.tsv")
    layouts = {r["layout_id"] for r in visible}
    checks = {
        "two_layouts": len(layouts) == 2,
        "eighteen_visible": len(visible) == 18,
        "six_lines": len({(r["layout_id"], r["line_no"]) for r in visible}) == 6,
        "all_lines_fit": all(int(r["line_used_width"]) <= int(r["line_capacity"]) for r in visible),
        "two_copies": sum(r["visibility_role"] == "ANTICIPATION_COPY" for r in visible) == 2,
        "sixteen_sources": sum(int(r["source_contribution"]) for r in visible) == 16,
        "four_boundaries": len(boundaries) == 4 and sum(r["decision"] == "READ_ONCE_ANTICIPATION" for r in boundaries) == 2 and sum(r["decision"] == "REAL_MICROCYCLE_RESET" for r in boundaries) == 2,
        "copies_same_identity": all(r["same_identity_across_margin"] == "YES" for r in boundaries if r["decision"] == "READ_ONCE_ANTICIPATION"),
        "resets_change_cycle": all(r["left_cycle"] != r["right_cycle"] for r in boundaries if r["decision"] == "REAL_MICROCYCLE_RESET"),
        "sixteen_exact_reconstructions": len(recon) == 16 and all(r["recovered_exact"] == "YES" for r in recon),
    }
    status = "PASS" if all(checks.values()) else "FAIL"
    result = {"status": status, "checks": checks, "check_count": len(checks)}
    (HERE / "THREE_HUNDRED_SEVENTY_FIRST_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if status != "PASS": raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))
    print(f"PASS {len(checks)} checks")


if __name__ == "__main__":
    main()
