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
    lines = read("THREE_HUNDRED_SEVENTY_SECOND_SIX_UNMARKED_LINES.tsv")
    boundaries = read("THREE_HUNDRED_SEVENTY_SECOND_FOUR_CORRECTOR_BOUNDARIES.tsv")
    actions = read("THREE_HUNDRED_SEVENTY_SECOND_EIGHTEEN_CORRECTOR_ACTIONS.tsv")
    recon = read("THREE_HUNDRED_SEVENTY_SECOND_TWO_RECONSTRUCTIONS.tsv")
    checks = {
        "six_unmarked_lines": len(lines) == 6 and all(r["role_labels_visible"] == r["boundary_labels_visible"] == "NO" for r in lines),
        "four_decisions": len(boundaries) == 4,
        "two_read_once": sum(r["corrector_decision"] == "READ_ONCE_REMOVE_LEFT_MARGIN_COPY" for r in boundaries) == 2,
        "two_resets": sum(r["corrector_decision"] == "RESET_NEW_MICROCYCLE" for r in boundaries) == 2,
        "eighteen_actions": len(actions) == 18,
        "two_removed": sum(r["corrector_action"] == "REMOVE_LEFT_MARGIN_COPY" for r in actions) == 2,
        "sixteen_sources": sum(int(r["source_contribution"]) for r in actions) == 16,
        "two_exact_reconstructions": len(recon) == 2 and all(r["exact_reconstruction"] == "YES" for r in recon),
    }
    status = "PASS" if all(checks.values()) else "FAIL"
    result = {"status": status, "checks": checks, "check_count": len(checks)}
    (HERE / "THREE_HUNDRED_SEVENTY_SECOND_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if status != "PASS": raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))
    print(f"PASS {len(checks)} checks")


if __name__ == "__main__":
    main()
