#!/usr/bin/env python3
import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def read(name):
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main():
    stamps = read("FIVE_HUNDRED_FIFTY_NINTH_EIGHT_WRAPPER_STAMPS.tsv")
    transforms = read("FIVE_HUNDRED_FIFTY_NINTH_TWENTY_SIX_TRANSFORM_DECK.tsv")
    palettes = read("FIVE_HUNDRED_FIFTY_NINTH_SEVENTEEN_LOCUS_PALETTES.tsv")
    programs = read("FIVE_HUNDRED_FIFTY_NINTH_THIRTY_FOUR_LOCUS_PROGRAMS.tsv")
    assignments = read("FIVE_HUNDRED_FIFTY_NINTH_FIFTY_NINE_COMPRESSED_ASSIGNMENTS.tsv")
    checks = {
        "eight_stamps": len(stamps) == 8 and {row["wrapper_stamp"] for row in stamps} == {"Ø", "q", "s", "ch", "d", "t", "sh", "che"},
        "twenty_six_transforms": len(transforms) == 26 and len({row["transform_id"] for row in transforms}) == 26,
        "seventeen_palettes": len(palettes) == 17 and len({row["palette_id"] for row in palettes}) == 17,
        "thirty_four_programs": len(programs) == 34 and len({row["locus"] for row in programs}) == 34,
        "fifty_nine_assignments": len(assignments) == 59 and len({row["event_id"] for row in assignments}) == 59,
        "uniform_22_27": sum(row["uniform_stamp"] == "YES" for row in programs) == 22 and sum(int(row["residual_events"]) for row in programs if row["uniform_stamp"] == "YES") == 27,
        "mixed_12_32": sum(row["uniform_stamp"] == "NO" for row in programs) == 12 and sum(int(row["residual_events"]) for row in programs if row["uniform_stamp"] == "NO") == 32,
        "all_refs_valid": {row["palette_id"] for row in programs + assignments} <= {row["palette_id"] for row in palettes} and {row["transform_id"] for row in assignments} <= {row["transform_id"] for row in transforms},
        "roundtrip": all(row["surface_roundtrip"] == "YES" for row in assignments),
        "no_free_choice": all(row["free_choice"] == "NO" for row in programs + assignments),
        "fixed_pages": {row["page"] for row in assignments} <= {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"},
        "seal_absent": all(not row["page"].lower().startswith("f84") for row in assignments),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FIVE_HUNDRED_FIFTY_NINTH_VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    for name, value in checks.items():
        print(f"{name}\t{'PASS' if value else 'FAIL'}")
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
