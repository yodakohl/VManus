#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import subprocess
from collections import Counter
from pathlib import Path

OUT = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def hashes() -> dict[str, str]:
    names = ["TWO_HUNDRED_TWENTY_FOURTH_NINE_ABA_WINDOWS.tsv", "TWO_HUNDRED_TWENTY_FOURTH_ABA_CONSTRUCTION_ENTRY.tsv", "TWO_HUNDRED_TWENTY_FOURTH_ABA_RETURN_RULE.md", "BUILD_SUMMARY.json"]
    return {name: hashlib.sha256((OUT / name).read_bytes()).hexdigest() for name in names}


def main() -> None:
    rows = read("TWO_HUNDRED_TWENTY_FOURTH_NINE_ABA_WINDOWS.tsv")
    construction = read("TWO_HUNDRED_TWENTY_FOURTH_ABA_CONSTRUCTION_ENTRY.tsv")
    readable = (OUT / "TWO_HUNDRED_TWENTY_FOURTH_ABA_RETURN_RULE.md").read_text(encoding="utf-8")
    summary = json.loads((OUT / "BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    categories = Counter(row["return_category"] for row in rows)
    checks = {
        "nine_windows": len(rows) == 9 and [row["aba_id"] for row in rows] == [f"ABA{i:02d}" for i in range(1, 10)],
        "outer_identity_exact": all(row["outer_identity_exact"] == "YES" for row in rows),
        "expected_categories": categories == {"REFERENT_RETURN": 4, "CONTINUATION_RETURN": 3, "VALUE_RETURN": 1, "ACTION_REPEAT_FROM_SOURCE": 1},
        "two_y_aiin_y": sum(row["value_window"] == "dies > Sollwert > dies" for row in rows) == 2,
        "one_construction": len(construction) == 1 and construction[0]["total_occurrences"] == "9",
        "five_pages": summary["pages"] == ["f10r", "f11r", "f81v", "f82r", "f83r"],
        "rule_readable": "A aktivieren" in readable and "größeren Werkstattkonvention" in readable,
        "sealed_not_accessed": summary["sealed_pages_accessed"] is False,
        "sealed_absent": "f84" not in readable.lower() and not any("f84" in value.lower() for table in (rows, construction) for row in table for value in row.values()),
    }
    first = hashes()
    subprocess.run(["python3", str(OUT / "build_two_hundred_twenty_fourth.py")], check=True)
    second = hashes()
    checks["deterministic_rebuild"] = first == second
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks, "summary": summary, "artifact_sha256": second}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
