#!/usr/bin/env python3
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
    assignments = read("TWO_HUNDRED_SEVENTY_SIXTH_142_TEMPLATE_ASSIGNMENTS.tsv")
    templates = read("TWO_HUNDRED_SEVENTY_SIXTH_EIGHT_ASTRO_TEMPLATES.tsv")
    crosswalk = read("TWO_HUNDRED_SEVENTY_SIXTH_ASTRO_PROSE_CROSSWALK.tsv")
    expected = {"LOCAL_NAMED_ENTRY": 40, "ADDRESSED_ENTRY": 34, "GRADED_OR_QUANTIFIED_VALUE": 20, "ACTION_OR_PATH": 15, "ROW_CONTINUATION": 10, "SOURCE_TO_TARGET": 10, "CONDITION_ENTRY": 8, "FOLLOWING_RELATION": 5}
    checks = {
        "142_assignments": len(assignments) == 142,
        "eight_templates": len(templates) == 8,
        "counts_exact": Counter(r["astro_template"] for r in assignments) == expected,
        "template_sum_142": sum(int(r["locus_count"]) for r in templates) == 142,
        "page_loci": Counter(r["page"] for r in assignments) == {"f67r2": 74, "f68r1": 37, "f69v": 31},
        "all_loci_unique": len({(r["page"], r["locus"]) for r in assignments}) == 142,
        "five_shared_questions": len(crosswalk) == 5,
        "close_prose_only": next(r for r in crosswalk if r["shared_question"] == "ABSCHLUSS")["astro_templates"] == "NONE",
        "all_readings_nonempty": all(r["template_reading_de"].strip() and r["continuous_default_reading_de"].strip() for r in assignments),
        "sealed_pages_absent": all(r["page"] not in {"f84", "f84r"} for r in assignments),
    }
    status = "PASS" if all(checks.values()) else "FAIL"
    (OUT / "VALIDATION.json").write_text(json.dumps({"status": status, "checks": checks}, indent=2) + "\n", encoding="utf-8")
    if status != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
