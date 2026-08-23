#!/usr/bin/env python3
import csv
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent


def rows(name):
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main():
    programs = rows("HUNDRED_THIRTEENTH_SEVEN_OPEN_FORMULA_PROGRAMS.tsv")
    renderings = rows("HUNDRED_THIRTEENTH_TWENTY_EIGHT_SCRIBAL_RENDERINGS.tsv")
    checks = {
        "programs_7": len(programs) == 7,
        "renderings_28": len(renderings) == 28,
        "four_per_program": all(sum(r["prediction_id"] == p["prediction_id"] for r in renderings) == 4 for p in programs),
        "cards_preserved": all(r["semantic_program_preserved"] == "YES" for r in renderings),
        "surfaces_preexisting": all(r["all_individual_surfaces_preexisting"] == "YES" for r in renderings),
        "four_hands": {r["renderer_id"] for r in renderings} == {"R-A", "R-B", "R-C", "R-D"},
        "sealed_absent": all("f84" not in "\t".join(r.values()).lower() for r in renderings),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
