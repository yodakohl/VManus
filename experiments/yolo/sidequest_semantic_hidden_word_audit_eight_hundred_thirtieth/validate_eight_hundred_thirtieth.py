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
    subprocess.run(["python", str(HERE / "build_eight_hundred_thirtieth.py")], check=True)
    candidates = read("EIGHT_HUNDRED_THIRTIETH_10_HIDDEN_WORD_CANDIDATES.tsv")
    y_rows = read("EIGHT_HUNDRED_THIRTIETH_60_Y_STATEMENT_ALIGNMENT.tsv")
    summary = json.loads((HERE / "EIGHT_HUNDRED_THIRTIETH_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    posten = next(row for row in candidates if row["hidden_stem"] == "POSTEN")
    checks = {
        "ten_candidates": len(candidates) == 10,
        "sixty_y_statements": len(y_rows) == 60,
        "posten_alignment": int(posten["tokens"]) == 65 and int(posten["statements"]) == 59 and int(posten["records"]) == 11 and int(posten["word_and_component_statements"]) == 59,
        "no_false_positive_posten": int(posten["word_without_component"]) == 0 and summary["posten_without_y_statements"] == 0,
        "one_y_exception": int(posten["component_without_word"]) == 1 and sum(row["posten_present"] == "NO" for row in y_rows) == 1,
        "y_nominated": posten["decision"] == "NOMINATE_Y_TO_POSTEN" and summary["nominated_revision"] == "Y=DIES -> Y=POSTEN",
        "only_one_revision": sum(row["decision"].startswith("NOMINATE") for row in candidates) == 1 and summary["other_revisions"] == 0,
        "sealed_pages": summary["sealed_pages"] == ["f84", "f84r"],
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "EIGHT_HUNDRED_THIRTIETH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
