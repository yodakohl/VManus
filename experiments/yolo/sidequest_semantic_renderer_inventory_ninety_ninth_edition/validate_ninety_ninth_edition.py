#!/usr/bin/env python3
"""Validate the complete renderer inventory."""

from __future__ import annotations

import csv
import json
from pathlib import Path


OUT = Path(__file__).resolve().parent


def rows(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    families = rows("NINETY_NINTH_173_RENDERER_FAMILIES.tsv")
    surfaces = rows("NINETY_NINTH_230_SURFACE_COVERAGE.tsv")
    gestures = rows("NINETY_NINTH_RENDERER_GESTURES.tsv")
    checks = {
        "families_173": len(families) == 173,
        "surfaces_230": len(surfaces) == 230,
        "surface_strings_unique": len({row["visible_surface"] for row in surfaces}) == 230,
        "one_master_per_card": all(sum(row["master_card_id"] == family["master_card_id"] and row["is_master_form"] == "YES" for row in surfaces) == 1 for family in families),
        "all_meanings_preserved": all(row["meaning_preserved"] == "YES" for row in surfaces),
        "gestures_9_with_zero": len(gestures) == 9,
        "semantic_gestures_none": all(row["semantic_contribution"] == "NONE" for row in gestures),
        "known_classes": set(row["family_class"] for row in families) <= {"SINGLE_REGISTERED_FORM", "FREE_STABLE_HOST_PLUS_ENTRIES", "BOUND_STABLE_HOST_PLUS_ENTRIES", "MINIMAL_HOST__LEARN_ALLOGRAPH_SET"},
        "sealed_absent": all("f84" not in "\t".join(row.values()).lower() for row in surfaces),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
