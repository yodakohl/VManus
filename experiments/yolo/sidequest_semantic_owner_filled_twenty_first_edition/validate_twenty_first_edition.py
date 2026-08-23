#!/usr/bin/env python3
from pathlib import Path
import csv
import json

HERE = Path(__file__).resolve().parent


def read(name):
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


prose = read("TWENTY_FIRST_116_OWNER_FILLED_PROSE.tsv")
owners = read("OWNER_USAGE_SUMMARY.tsv")
checks = {
    "116": len(prose) == 116,
    "nineteen_herbal": sum(row["record_id"].startswith("H") for row in prose) == 19,
    "ninety_seven_bio": sum(row["record_id"].startswith("B") for row in prose) == 97,
    "381_groups": sum(int(row["group_count"]) for row in prose) == 381,
    "all_surfaces": all(row["surface_sequence"] for row in prose),
    "all_atoms": all(row["atom_sequence"] for row in prose),
    "all_literals": all(row["literal_card_reading_de"] for row in prose),
    "all_owners": all(row["image_owner"] for row in prose),
    "all_concrete": all(row["selected_concrete_reading_de"] for row in prose),
    "all_rivals": all(row["short_rival_de"] for row in prose),
    "owner_summary_matches": sum(int(row["statements"]) for row in owners) == 116,
    "complete_edition": (HERE / "COMPLETE_TEN_PAGE_OWNER_FILLED_TWENTY_FIRST_EDITION.md").exists(),
    "report": (HERE / "TWENTY_FIRST_EDITION_REPORT.md").exists(),
}
sealed = "f" + "84"
checks["sealed_absent"] = all(sealed not in path.read_text(encoding="utf-8").lower() for path in HERE.iterdir() if path.is_file())
result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
(HERE / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result, ensure_ascii=False, indent=2))
if result["status"] != "PASS":
    raise SystemExit(1)
