#!/usr/bin/env python3
from pathlib import Path
import csv
import json

HERE = Path(__file__).resolve().parent


def read(name):
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


copies = read("TWENTY_NINTH_68_SCRIBE_IDIOM_COPIES.tsv")
idioms = read("TWENTY_NINTH_17_IDIOM_COPYBOOK.tsv")
errors = read("TWENTY_NINTH_EIGHT_APPRENTICE_ERRORS.tsv")
checks = {
    "seventeen_idioms": len(idioms) == 17,
    "sixty_eight_copies": len(copies) == 68,
    "four_per_idiom": all(sum(row["pattern_id"] == idiom["pattern_id"] for row in copies) == 4 for idiom in idioms),
    "four_scribes": len({row["scribe_id"] for row in copies}) == 4,
    "tuple_invariant": all(row["tuple_sequence_changed"] == "NO" for row in copies),
    "meaning_invariant": all(row["meaning_changed"] == "NO" for row in copies),
    "one_meaning_per_idiom": all(int(row["meaning_variants"]) == 1 for row in idioms),
    "eight_errors": len(errors) == 8,
    "error_corrections": all(row["apprentice_error_de"] and row["master_correction_de"] for row in errors),
    "copybook": (HERE / "TWENTY_NINTH_FOUR_SCRIBE_IDIOM_COPYBOOK.md").exists(),
    "report": (HERE / "TWENTY_NINTH_EDITION_REPORT.md").exists(),
}
sealed = "f" + "84"
checks["sealed_absent"] = all(
    sealed not in path.read_text(encoding="utf-8").lower()
    for path in HERE.iterdir()
    if path.is_file()
)
result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
(HERE / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result, ensure_ascii=False, indent=2))
if result["status"] != "PASS":
    raise SystemExit(1)
