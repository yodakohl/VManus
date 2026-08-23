#!/usr/bin/env python3
"""Small consistency checker for the creative thirty-third edition."""

from __future__ import annotations

import csv
import json
from pathlib import Path


OUT = Path(__file__).resolve().parent


def rows(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    pairs = rows("THIRTY_THIRD_MINIMAL_PAIRS.tsv")
    stems = rows("THIRTY_THIRD_STEM_VERDICTS.tsv")
    ids = [r["pair_id"] for r in pairs]
    checks = {
        "thirty_seven_pairs": len(pairs) == 37,
        "six_axes": len({r["axis"] for r in pairs}) == 6,
        "pair_ids_unique": len(ids) == len(set(ids)),
        "both_sides_observed": all(int(r["left_occurrences"]) > 0 and int(r["right_occurrences"]) > 0 for r in pairs),
        "surfaces_nonempty": all(r["left_surface_types"] and r["right_surface_types"] for r in pairs),
        "examples_nonempty": all(r["left_example"] and r["right_example"] for r in pairs),
        "readings_concrete": all(r["left_reading_de"] and r["right_reading_de"] for r in pairs),
        "sixteen_stems": len(stems) == 16,
        "stem_symbols_unique": len({r["symbol"] for r in stems}) == len(stems),
        "contrast_book": (OUT / "THIRTY_THIRD_APPRENTICE_CONTRAST_BOOK.md").exists(),
        "report": (OUT / "THIRTY_THIRD_EDITION_REPORT.md").exists(),
        "sealed_absent": not any("f84" in path.name.lower() for path in OUT.iterdir()),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
