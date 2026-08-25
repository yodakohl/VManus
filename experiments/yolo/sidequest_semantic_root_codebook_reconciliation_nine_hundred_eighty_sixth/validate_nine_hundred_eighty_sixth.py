#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P984 = ROOT / "experiments/yolo/sidequest_semantic_53_root_plain_dictionary_nine_hundred_eighty_fourth"
P985 = ROOT / "experiments/yolo/sidequest_semantic_canonical_image_owned_workshop_edition_nine_hundred_eighty_fifth"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    roots = read(P984 / "PASS984_53_PORTABLE_ROOT_DICTIONARY.tsv")
    old_events = read(P985 / "PASS985_2511_EVENT_INTERLINEAR.tsv")
    old_clauses = read(P985 / "PASS985_354_COMPLETE_CLAUSE_EDITION.tsv")
    codebook = read(HERE / "PASS986_159_RECONCILED_CODEBOOK.tsv")
    events = read(HERE / "PASS986_2511_RECONCILED_EVENT_INTERLINEAR.tsv")
    clauses = read(HERE / "PASS986_354_RECONCILED_CLAUSES.tsv")
    changes = read(HERE / "PASS986_CODEBOOK_CHANGES.tsv")

    root_atomic = {row["root_id"]: row["atomic_meaning_de"] for row in roots}
    codebook_by_id = {row["teaching_unit_id"]: row for row in codebook}
    checks = {
        "codebook_159": len(codebook) == 159,
        "codebook_ids_unique": len(codebook_by_id) == 159,
        "roots_53": len(roots) == 53,
        "all_root_values_exact": all(codebook_by_id[root_id]["spoken_value_de"] == value for root_id, value in root_atomic.items()),
        "formulas_30": sum(row["layer"] == "C_LEARNED_FORMULA_CARD" for row in codebook) == 30,
        "events_2511": len(events) == 2511,
        "event_ids_unchanged": [row["event_id"] for row in events] == [row["event_id"] for row in old_events],
        "event_surfaces_unchanged": [row["surface"] for row in events] == [row["surface"] for row in old_events],
        "events_have_no_old_y_or_close_tokens": all(
            "DIES" not in row["complete_working_reading_de"].split(" · ")
            and "SCHLIESSEN" not in row["complete_working_reading_de"].split(" · ")
            for row in events
        ),
        "clauses_354": len(clauses) == 354,
        "clause_ids_unchanged": [row["clause_id"] for row in clauses] == [row["clause_id"] for row in old_clauses],
        "clause_events_unchanged": [row["event_ids"] for row in clauses] == [row["event_ids"] for row in old_clauses],
        "all_readings_present": all(row["complete_working_reading_de"] for row in events)
        and all(row["complete_working_translation_de"] for row in clauses),
        "change_table_nonempty": bool(changes),
        "sealed_absent": all("f84" not in row["physical_page"].lower() for row in events),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "PASS986_VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
