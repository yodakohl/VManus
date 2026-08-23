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
    names = ["TWO_HUNDRED_TWENTY_EIGHTH_FIFTY_READING_UNITS.tsv", "TWO_HUNDRED_TWENTY_EIGHTH_TWO_CONTINUOUS_PASSAGES.tsv", "TWO_HUNDRED_TWENTY_EIGHTH_ADDED_CONNECTIVES.tsv", "TWO_HUNDRED_TWENTY_EIGHTH_TWO_READABLE_PASSAGES.md", "BUILD_SUMMARY.json"]
    return {name: hashlib.sha256((OUT / name).read_bytes()).hexdigest() for name in names}


def main() -> None:
    units = read("TWO_HUNDRED_TWENTY_EIGHTH_FIFTY_READING_UNITS.tsv")
    passages = read("TWO_HUNDRED_TWENTY_EIGHTH_TWO_CONTINUOUS_PASSAGES.tsv")
    connectives = read("TWO_HUNDRED_TWENTY_EIGHTH_ADDED_CONNECTIVES.tsv")
    readable = (OUT / "TWO_HUNDRED_TWENTY_EIGHTH_TWO_READABLE_PASSAGES.md").read_text(encoding="utf-8")
    summary = json.loads((OUT / "BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    checks = {
        "fifty_units": len(units) == 50 and len({row["reading_unit_id"] for row in units}) == 50,
        "two_passages": len(passages) == 2 and {row["passage_id"] for row in passages} == {"P_H2", "P_B3"},
        "h2_16_b3_34": sum(row["passage_id"] == "P_H2" for row in units) == 16 and sum(row["passage_id"] == "P_B3" for row in units) == 34,
        "sixty_visible_cards": summary["visible_cards"] == 60 and summary["source_tokens"] == 60,
        "five_composites": summary["composite_units"] == 5,
        "connectives_do_not_change_cards": all(row["changes_card_meaning"] == "NO" for row in connectives),
        "exact_passage_bounds": {(row["passage_id"], row["first_statement"], row["last_statement"]) for row in passages} == {("P_H2", "H2-S001", "H2-S003"), ("P_B3", "B3-S001", "B3-S016")},
        "no_global_flow_claim": "keinen geschlossenen oder gerichteten Gesamtwasserkreislauf" in readable,
        "sealed_not_accessed": summary["sealed_pages_accessed"] is False,
        "sealed_absent": "f84" not in readable.lower() and not any("f84" in value.lower() for table in (units, passages, connectives) for row in table for value in row.values()),
    }
    first = hashes()
    subprocess.run(["python3", str(OUT / "build_two_hundred_twenty_eighth.py")], check=True)
    second = hashes()
    checks["deterministic_rebuild"] = first == second
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks, "summary": summary, "artifact_sha256": second}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
