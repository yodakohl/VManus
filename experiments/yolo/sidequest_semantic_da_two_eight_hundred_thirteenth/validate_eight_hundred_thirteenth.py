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
    subprocess.run(["python", str(HERE / "build_eight_hundred_thirteenth.py")], check=True)
    candidates = read("EIGHT_HUNDRED_THIRTEENTH_5_DA_CANDIDATES.tsv")
    events = read("EIGHT_HUNDRED_THIRTEENTH_DA_EVENT.tsv")
    statements = read("EIGHT_HUNDRED_THIRTEENTH_REVISED_STATEMENT.tsv")
    extensions = read("EIGHT_HUNDRED_THIRTEENTH_4_EXTENSION_TESTS.tsv")
    summary = json.loads((HERE / "EIGHT_HUNDRED_THIRTEENTH_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    checks = {
        "one_event_statement": len(events) == 1 and events[0]["event_id"] == "E371" and len(statements) == 1,
        "five_candidates_two_selected_bound": len(candidates) == 5 and next(row for row in candidates if row["decision"] == "SELECT_BOUND")["candidate"] == "ZWEI",
        "statement_simplified": "bis zur zweiten Stufe" in statements[0]["revised_reading_de"] and statements[0]["old_reading_de"] != statements[0]["revised_reading_de"],
        "four_extension_tests_two_collisions": len(extensions) == 4 and summary["surface_collisions"] == 2,
        "collisions_are_ain_aiin": {row["naive_surface"] for row in extensions if row["surface_observed"] == "YES"} == {"dain", "daiin"},
        "core33_bound2_local1": summary["core_size"] == 33 and summary["bound_components"] == 2 and summary["remaining_local_singletons"] == 1,
        "sealed_pages": summary["sealed_pages"] == ["f84", "f84r"],
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "EIGHT_HUNDRED_THIRTEENTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
