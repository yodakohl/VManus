#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import subprocess
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    subprocess.run(["python", str(HERE / "build_eight_hundred_sixteenth.py")], check=True)
    candidates = read("EIGHT_HUNDRED_SIXTEENTH_6_OS_CANDIDATES.tsv")
    events = read("EIGHT_HUNDRED_SIXTEENTH_OS_EVENT.tsv")
    statements = read("EIGHT_HUNDRED_SIXTEENTH_REVISED_STATEMENT.tsv")
    clauses = read("EIGHT_HUNDRED_SIXTEENTH_3_CLAUSE_PARTS.tsv")
    summary = json.loads((HERE / "EIGHT_HUNDRED_SIXTEENTH_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    checks = {
        "one_event_statement": len(events) == 1 and events[0]["event_id"] == "E005" and len(statements) == 1,
        "six_candidates_dazu_selected": len(candidates) == 6 and next(row for row in candidates if row["decision"] == "SELECT_WHOLE_CONNECTOR")["candidate"] == "DAZU",
        "correct_neighbors": events[0]["previous_event"] == "E004" and events[0]["following_event"] == "E006",
        "statement_revised": "dazu Wasser entnehmen" in statements[0]["revised_reading_de"] and statements[0]["old_reading_de"] != statements[0]["revised_reading_de"],
        "three_clause_parts": len(clauses) == 3 and [row["phase"] for row in clauses] == ["BEFORE_OS", "OS", "AFTER_OS"],
        "architecture_33_3_3": summary["core_size"] == 33 and summary["bound_components"] == 3 and summary["whole_forms"] == 3,
        "sealed_pages": summary["sealed_pages"] == ["f84", "f84r"],
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "EIGHT_HUNDRED_SIXTEENTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
