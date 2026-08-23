#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def rows(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    statements = rows("TWO_HUNDRED_FORTY_FIRST_FIFTY_FOUR_F83R_MOTIF_READINGS.tsv")
    motifs = rows("TWO_HUNDRED_FORTY_FIRST_SEVEN_MOTIF_CURRICULUM.tsv")
    exceptions = rows("TWO_HUNDRED_FORTY_FIRST_THREE_ATOMIC_EXCEPTIONS.tsv")
    checks = {
        "54_statements": len(statements) == 54,
        "54_unique_ids": len({r["statement_id"] for r in statements}) == 54,
        "seven_motifs": len(motifs) == 7,
        "old_six_cover_44": sum(r["coverage_status"] == "MOTIF_COVERED" and r["new_handoff_motif"] == "NONE" for r in statements) == 44,
        "m07_adds_7": sum(r["new_handoff_motif"] == "M07" for r in statements) == 7,
        "covered_51": sum(r["coverage_status"] == "MOTIF_COVERED" for r in statements) == 51,
        "three_exceptions": len(exceptions) == 3,
        "expected_exceptions": {r["statement_id"] for r in exceptions} == {"B3-S009", "B4-S004", "B4-S010"},
        "all_readings_concrete": all(r["complete_station_reading_de"].strip() for r in statements),
        "no_unknown": all("UNKNOWN" not in "\t".join(r.values()) for r in statements),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        print(json.dumps(result, ensure_ascii=False, indent=2))
        raise SystemExit(1)
    print(f"PASS {sum(checks.values())}/{len(checks)}")


if __name__ == "__main__":
    main()
