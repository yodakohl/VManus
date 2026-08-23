#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import subprocess
from pathlib import Path

OUT = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def hashes() -> dict[str, str]:
    names = ["TWO_HUNDRED_SIXTH_26_PAIR_PRESSURE.tsv", "TWO_HUNDRED_SIXTH_SIX_FIELD_SUPPORT.tsv", "BUILD_SUMMARY.json"]
    return {name: hashlib.sha256((OUT / name).read_bytes()).hexdigest() for name in names}


def main() -> None:
    pairs = read("TWO_HUNDRED_SIXTH_26_PAIR_PRESSURE.tsv")
    fields = read("TWO_HUNDRED_SIXTH_SIX_FIELD_SUPPORT.tsv")
    summary = json.loads((OUT / "BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    checks = {
        "26_pairs": len(pairs) == 26,
        "six_fields": len(fields) == 6,
        "support_split": summary["support_counts"] == {"THIN_DRAWER_RECOMBINATION": 5, "DIRECT_EXACT_BIGRAM": 4, "SUPPORTED_DRAWER_RECOMBINATION": 17},
        "no_drawer_violation": summary["drawer_unattested_pairs"] == 0,
        "three_fields_thin": summary["fields_with_thin_recombination"] == 3,
        "direct_chain_is_n05": sum(row["field_id"] == "N05" and row["support_class"] == "DIRECT_EXACT_BIGRAM" for row in pairs) == 3,
        "no_new_card_types": summary["fresh_card_types"] == 0,
        "every_pair_has_example": all(row["drawer_example_statement"] != "NONE" for row in pairs),
        "sealed_not_accessed": summary["sealed_pages_accessed"] is False,
        "sealed_absent": not any("f84" in value.lower() for rows in (pairs, fields) for row in rows for value in row.values()),
    }
    first = hashes()
    subprocess.run(["python3", str(OUT / "build_two_hundred_sixth.py")], check=True)
    second = hashes()
    checks["deterministic_rebuild"] = first == second
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks, "summary": summary, "artifact_sha256": second}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
