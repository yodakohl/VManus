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
    names = [
        "TWO_HUNDRED_EIGHTEENTH_TOP20_SEMANTIC_DEBT.tsv",
        "TWO_HUNDRED_EIGHTEENTH_116_TIGHTENED_STATEMENTS.tsv",
        "TWO_HUNDRED_EIGHTEENTH_TIGHTENED_PROSE_EDITION.md",
        "BUILD_SUMMARY.json",
    ]
    return {name: hashlib.sha256((OUT / name).read_bytes()).hexdigest() for name in names}


def main() -> None:
    debt = read("TWO_HUNDRED_EIGHTEENTH_TOP20_SEMANTIC_DEBT.tsv")
    rows = read("TWO_HUNDRED_EIGHTEENTH_116_TIGHTENED_STATEMENTS.tsv")
    summary = json.loads((OUT / "BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    edition = (OUT / "TWO_HUNDRED_EIGHTEENTH_TIGHTENED_PROSE_EDITION.md").read_text(encoding="utf-8")
    changed = [row for row in rows if row["r218_editorial_status"] == "TIGHTENED"]
    unchanged = [row for row in rows if row["r218_editorial_status"] == "UNCHANGED"]
    checks = {
        "20_unique_debt_rows": len(debt) == 20 and len({row["statement_id"] for row in debt}) == 20,
        "rank_1_to_20": [int(row["debt_rank"]) for row in debt] == list(range(1, 21)),
        "all_top20_shorter": all(int(row["words_removed"]) > 0 for row in debt),
        "116_statements": len(rows) == 116 and len({row["statement_id"] for row in rows}) == 116,
        "381_events": summary["events"] == 381,
        "20_changed_96_unchanged": len(changed) == 20 and len(unchanged) == 96,
        "card_readings_preserved": all(row["layered_card_reading"] for row in rows),
        "all_records_present": all(f"## {unit}" in edition for unit in ("H1", "H2", "H3", "H4", "H5", "B1", "B2", "B3", "B4", "B5", "B6")),
        "summary_matches": summary["tightened"] == 20 and summary["unchanged"] == 96 and summary["words_removed"] > 0,
        "sealed_absent": "f84" not in edition.lower() and not any("f84" in value.lower() for table in (debt, rows) for row in table for value in row.values()),
        "sealed_not_accessed": summary["sealed_pages_accessed"] is False,
    }
    first = hashes()
    subprocess.run(["python3", str(OUT / "build_two_hundred_eighteenth.py")], check=True)
    second = hashes()
    checks["deterministic_rebuild"] = first == second
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks, "summary": summary, "artifact_sha256": second}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
