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
    subprocess.run(["python", str(HERE / "build_eight_hundred_thirty_second.py")], check=True)
    candidates = read("EIGHT_HUNDRED_THIRTY_SECOND_8_HIDDEN_WORD_CANDIDATES.tsv")
    o_rows = read("EIGHT_HUNDRED_THIRTY_SECOND_17_O_STATEMENT_ALIGNMENT.tsv")
    summary = json.loads((HERE / "EIGHT_HUNDRED_THIRTY_SECOND_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    work = next(row for row in candidates if row["hidden_stem"] == "ARBEITSGANG")
    checks = {
        "eight_candidates": len(candidates) == 8,
        "seventeen_o_statements": len(o_rows) == 17,
        "arbeitsgang_alignment": int(work["tokens"]) == 15 and int(work["statements"]) == 14 and int(work["records"]) == 9 and int(work["word_and_component_statements"]) == 14,
        "no_false_positive": int(work["word_without_component"]) == 0 and summary["arbeitsgang_without_o"] == 0,
        "three_missing_word": int(work["component_without_word"]) == 3 and sum(row["arbeitsgang_present"] == "NO" for row in o_rows) == 3,
        "o_nominated": work["decision"] == "NOMINATE_O_TO_ARBEITSGANG" and summary["nominated_revision"] == "O=VORGANG -> O=ARBEITSGANG",
        "only_one_nominee": sum(row["decision"].startswith("NOMINATE") for row in candidates) == 1,
        "sealed_pages": summary["sealed_pages"] == ["f84", "f84r"],
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "EIGHT_HUNDRED_THIRTY_SECOND_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
