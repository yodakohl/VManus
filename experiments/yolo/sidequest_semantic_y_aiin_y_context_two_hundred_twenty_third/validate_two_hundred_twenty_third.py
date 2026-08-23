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
    names = ["TWO_HUNDRED_TWENTY_THIRD_EIGHT_CONTEXT_STATEMENTS.tsv", "TWO_HUNDRED_TWENTY_THIRD_THREE_FRAME_PARSES.tsv", "TWO_HUNDRED_TWENTY_THIRD_TWO_CONTEXT_READINGS.md", "BUILD_SUMMARY.json"]
    return {name: hashlib.sha256((OUT / name).read_bytes()).hexdigest() for name in names}


def main() -> None:
    contexts = read("TWO_HUNDRED_TWENTY_THIRD_EIGHT_CONTEXT_STATEMENTS.tsv")
    parses = read("TWO_HUNDRED_TWENTY_THIRD_THREE_FRAME_PARSES.tsv")
    readable = (OUT / "TWO_HUNDRED_TWENTY_THIRD_TWO_CONTEXT_READINGS.md").read_text(encoding="utf-8")
    summary = json.loads((OUT / "BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    checks = {
        "eight_contexts": len(contexts) == 8 and len({row["statement_id"] for row in contexts}) == 8,
        "h2_three_b3_five": sum(row["record_unit_id"] == "H2" for row in contexts) == 3 and sum(row["record_unit_id"] == "B3" for row in contexts) == 5,
        "exact_two_targets": sum(row["contains_y_aiin_y"] == "YES" for row in contexts) == 2,
        "both_target_sequences": {row["visible_sequence"] for row in contexts if row["contains_y_aiin_y"] == "YES"} == {"ycheor cthy chor cthaiin qoctholy dy chy taiin shy", "chey daiin chey lchedy"},
        "three_parses_one_selected": len(parses) == 3 and sum(row["decision"] == "SELECT" for row in parses) == 1,
        "selected_value_bracket": next(row for row in parses if row["decision"] == "SELECT")["parse_name"] == "VALUE_BRACKET_WITH_REFERENT_RETURN",
        "aiin_stays_sollwert": "AIIN bleibt Sollwert" in readable,
        "all_contexts_readable": all(row["statement_id"] in readable for row in contexts),
        "sealed_not_accessed": summary["sealed_pages_accessed"] is False,
        "sealed_absent": "f84" not in readable.lower() and not any("f84" in value.lower() for table in (contexts, parses) for row in table for value in row.values()),
    }
    first = hashes()
    subprocess.run(["python3", str(OUT / "build_two_hundred_twenty_third.py")], check=True)
    second = hashes()
    checks["deterministic_rebuild"] = first == second
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks, "summary": summary, "artifact_sha256": second}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
