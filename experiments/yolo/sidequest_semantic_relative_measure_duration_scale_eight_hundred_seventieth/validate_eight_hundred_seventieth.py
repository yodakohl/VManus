#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import subprocess
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent
PREFIX = "EIGHT_HUNDRED_SEVENTIETH"


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    subprocess.run(["python", str(HERE / "build_eight_hundred_seventieth.py")], check=True)
    scales = read(f"{PREFIX}_6_RELATIVE_SCALE_COMPONENTS.tsv")
    audit = read(f"{PREFIX}_151_EVENT_SCALE_AUDIT.tsv")
    sample = read(f"{PREFIX}_43_SAMPLE_SCALE_EVENTS.tsv")
    counts = read(f"{PREFIX}_SAMPLE_COMPONENT_COUNTS.tsv")
    revisions = read(f"{PREFIX}_5_MASTER_VALUE_REVISIONS.tsv")
    summary = json.loads((HERE / f"{PREFIX}_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    sample_components = Counter(token for row in sample for token in row["relative_components"].split("+"))
    checks = {
        "six_scales": len(scales) == 6 and {row["component"] for row in scales} == {"AIN", "AIIN", "IIN", "E", "EE", "EEE"},
        "event_inventory": len(audit) == 151 and len({row["event_id"] for row in audit}) == 151 and len({row["exact_card_id"] for row in audit}) == 73,
        "statement_inventory": len({row["statement_id"] for row in audit}) == 78,
        "sample_inventory": len(sample) == 43 and all(row["page"] == "f56r" or row["record"] == "B2" for row in sample),
        "sample_counts": sample_components == {"AIN": 4, "AIIN": 9, "E": 13, "EE": 16, "EEE": 1},
        "count_table": len(counts) == 6 and {row["component"]: int(row["sample_occurrences"]) for row in counts} == {"AIN": 4, "AIIN": 9, "IIN": 0, "E": 13, "EE": 16, "EEE": 1},
        "five_revisions": len(revisions) == 5 and {row["slot"] for row in revisions} == {"PRODUCT", "MEASURE", "DURATION", "RESULT", "CONDITION"},
        "calibration_ceiling": all(row["absolute_unit_encoded"] == "NO" for row in scales) and summary["master_values_reduced_to_calibration"] == 2,
        "no_new_words": summary["new_word_meanings"] == 0,
        "sealed_pages": summary["sealed_pages"] == ["f84", "f84r"] and not any("f84" in " ".join(row.values()).lower() for row in scales + audit + sample + counts + revisions),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / f"{PREFIX}_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
