#!/usr/bin/env python3
"""Consistency checks for the five-owner root atlas."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


OUT = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    roots = read("FORTY_SIXTH_28_ROOT_TRANSFER_VERDICTS.tsv")
    atlas = read("FORTY_SIXTH_140_OWNER_EXPANSIONS.tsv")
    per_root = Counter(row["root"] for row in atlas)
    per_owner = Counter(row["owner_class"] for row in atlas)
    checks = {
        "twenty_eight_roots": len(roots) == 28,
        "roots_unique": len({row["root"] for row in roots}) == 28,
        "one_hundred_forty_expansions": len(atlas) == 140,
        "five_per_root": all(per_root[row["root"]] == 5 for row in roots),
        "twenty_eight_per_owner": len(per_owner) == 5 and all(value == 28 for value in per_owner.values()),
        "twenty_five_cross_register": sum(row["register_evidence"] == "ASTRO|PROSE" for row in roots) == 25,
        "three_prose_only": sum(row["register_evidence"] == "PROSE" for row in roots) == 3,
        "all_values_invariant": all(row["root_meaning_changed"] == "NO" for row in atlas),
        "all_have_concrete_expansion": all(row["spoken_owner_expansion_de"] for row in atlas),
        "all_owner_supply_explicit": all(row["concrete_noun_supplied_by_owner"] == "YES" for row in atlas),
        "atlas_exists": (OUT / "FORTY_SIXTH_FIVE_OWNER_ATLAS.md").exists(),
        "sealed_absent": not any("f84" in path.name.lower() for path in OUT.iterdir()),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
