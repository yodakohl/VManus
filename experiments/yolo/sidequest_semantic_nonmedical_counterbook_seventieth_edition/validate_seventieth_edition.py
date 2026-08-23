#!/usr/bin/env python3
"""Validate the coherent fourteen-unit nonmedical counterbook."""

from __future__ import annotations

import csv
import json
from pathlib import Path


OUT = Path(__file__).resolve().parent
ALLOWED = {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r", "f67r2", "f68r1", "f69v"}


def read_tsv(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    units = read_tsv("SEVENTIETH_14_DUAL_CONTENT_UNITS.tsv")
    ledger = read_tsv("SEVENTIETH_776_DUAL_CONTENT_LEDGER.tsv")
    discriminators = read_tsv("SEVENTIETH_14_CONTENT_DISCRIMINATORS.tsv")
    checks = {
        "fourteen_units": len(units) == 14 and len({row["unit_id"] for row in units}) == 14,
        "776_groups": len(ledger) == 776 and len({row["unified_serial"] for row in ledger}) == 776,
        "fourteen_discriminators": len(discriminators) == 14 and len({row["unit_id"] for row in discriminators}) == 14,
        "unit_group_counts": sum(int(row["group_count"]) for row in units) == 776,
        "same_formal_architecture": all(row["shared_formal_architecture"] == "SAME_CARDS_SAME_CLAUSES_SAME_OWNERS" for row in units),
        "no_surface_or_form_change": all(row["formal_reading_changed"] == "NO" and row["surface_changed"] == "NO" for row in ledger),
        "all_content_frames_nonempty": all(row["medical_master_frame"] and row["nonmedical_master_frame"] for row in ledger),
        "score_range": all(0 <= int(row["medical_content_fit_0_to_5"]) <= 5 and 0 <= int(row["nonmedical_content_fit_0_to_5"]) <= 5 for row in units),
        "ten_pages": {row["page"] for row in ledger} == ALLOWED,
        "sealed_pages_absent": all("f84" not in "\t".join(row.values()).lower() for row in units + ledger + discriminators),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
