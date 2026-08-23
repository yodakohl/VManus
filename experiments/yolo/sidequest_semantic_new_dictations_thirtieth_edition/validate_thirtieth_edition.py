#!/usr/bin/env python3
from pathlib import Path
import csv
import json

HERE = Path(__file__).resolve().parent


def read(name):
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


exercises = read("THIRTIETH_12_NEW_DICTATIONS.tsv")
copies = read("THIRTIETH_48_SCRIBE_COPIES.tsv")
checks = {
    "twelve_exercises": len(exercises) == 12,
    "forty_eight_copies": len(copies) == 48,
    "four_per_exercise": all(sum(row["exercise_id"] == exercise["exercise_id"] for row in copies) == 4 for exercise in exercises),
    "four_scribes": len({row["scribe_id"] for row in copies}) == 4,
    "all_tuple_chains_new": all(row["occurs_contiguously_in_current_statement"] == "NO" for row in exercises),
    "all_registered": all(row["uses_only_registered_idiom_cards"] == "YES" for row in copies),
    "tuple_invariant": all(row["tuple_sequence_changed"] == "NO" for row in copies),
    "meaning_invariant": all(row["meaning_changed"] == "NO" for row in copies),
    "exercise_not_claim": all(row["new_manuscript_claim"] == "NO_APPRENTICE_EXERCISE" for row in copies),
    "all_complete": all(all(row[field] for field in row) for row in exercises),
    "book": (HERE / "THIRTIETH_APPRENTICE_DICTATION_BOOK.md").exists(),
    "report": (HERE / "THIRTIETH_EDITION_REPORT.md").exists(),
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
