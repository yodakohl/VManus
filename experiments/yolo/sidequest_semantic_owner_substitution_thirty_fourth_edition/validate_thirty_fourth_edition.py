#!/usr/bin/env python3
"""Consistency checker for the thirty-fourth creative edition."""

from __future__ import annotations

import csv
import json
from pathlib import Path


OUT = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    rows = read("THIRTY_FOURTH_OWNER_SUBSTITUTIONS.tsv")
    nuclei = read("THIRTY_FOURTH_OWNER_NUCLEI.tsv")
    checks = {
        "eighteen_exercises": len(rows) == 18,
        "eighteen_nuclei": len(nuclei) == 18,
        "ids_unique": len({r["exercise_id"] for r in rows}) == 18,
        "atoms_unique": len({r["invariant_atoms"] for r in rows}) == 18,
        "all_observed": all(int(r["observed_occurrences"]) > 0 for r in rows),
        "all_three_expansions": all(r["herbal_expansion_de"] and r["biological_expansion_de"] and r["astro_expansion_de"] for r in rows),
        "same_nucleus_text": all(r["invariant_nucleus_de"] in r["invariant_prediction_de"] for r in rows),
        "exercise_status": all(r["status"] == "CREATIVE_OWNER_SUBSTITUTION__NOT_MANUSCRIPT_TEXT" for r in rows),
        "copybook": (OUT / "THIRTY_FOURTH_THREE_OWNER_COPYBOOK.md").exists(),
        "report": (OUT / "THIRTY_FOURTH_EDITION_REPORT.md").exists(),
        "sealed_absent": not any("f84" in path.name.lower() for path in OUT.iterdir()),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
