#!/usr/bin/env python3
import csv
import json
from pathlib import Path


OUT = Path(__file__).resolve().parent


def rows(name):
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main():
    exercises = rows("HUNDRED_THIRTY_NINTH_EIGHT_COMPOSED_INSTRUCTIONS.tsv")
    copies = rows("HUNDRED_THIRTY_NINTH_32_FOUR_HAND_COPIES.tsv")
    traces = rows("HUNDRED_THIRTY_NINTH_TOKEN_ROUNDTRIP_TRACE.tsv")
    checks = {
        "instructions_8": len(exercises) == 8,
        "drawers_8": len({r["specialist_drawer"] for r in exercises}) == 8,
        "copies_32": len(copies) == 32,
        "four_hands": {r["renderer_id"] for r in copies} == {"R-A", "R-B", "R-C", "R-D"},
        "all_copy_roundtrip": all(r["roundtrip"] == "PASS" for r in copies),
        "all_token_roundtrip": all(r["roundtrip"] == "PASS" for r in traces),
        "visible_variation": all(int(r["distinct_visible_copies"]) >= 2 for r in exercises),
        "all_cells_nonempty": all(all(v for v in r.values()) for table in (exercises, copies, traces) for r in table),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
