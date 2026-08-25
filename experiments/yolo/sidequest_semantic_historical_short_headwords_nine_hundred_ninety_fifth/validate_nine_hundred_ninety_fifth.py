#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def rows(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    codebook = rows("PASS995_159_SHORT_HEADWORD_CODEBOOK.tsv")
    roots = rows("PASS995_53_SHORT_PORTABLE_ROOTS.tsv")
    events = rows("PASS995_2511_REVISED_EVENT_INTERLINEAR.tsv")
    clauses = rows("PASS995_354_REVISED_NATURAL_CLAUSES.tsv")
    bio = rows("PASS995_1280_REVISED_BIOLOGICAL_EVENT_PHRASES.tsv")
    revisions = rows("PASS995_SIX_HEADWORD_REVISIONS.tsv")
    root_values = {row["root_id"]: row["atomic_meaning_de"] for row in roots}
    code_values = {
        row["teaching_unit_id"]: row["spoken_value_de"]
        for row in codebook
        if row["teaching_unit_id"].startswith("R-")
    }
    old = {"SOLLWERT", "EINHEIT", "ARBEITSSATZ", "EINSTELLEN", "MARKIEREN", "START"}
    payload = "\n".join(str(row) for row in codebook + roots + events + bio)
    checks = {
        "revisions_6": len(revisions) == 6,
        "codebook_159": len(codebook) == 159,
        "roots_53": len(roots) == 53,
        "events_2511": len(events) == 2511,
        "clauses_354": len(clauses) == 354,
        "bio_1280": len(bio) == 1280,
        "root_codebook_match": all(code_values.get(root_id) == value for root_id, value in root_values.items()),
        "new_values_exact": {row["new_atomic_value_de"] for row in revisions}
        == {"MASS", "PORTION", "ANSATZ", "STELLEN", "MERKEN", "BEGINN"},
        "old_atomic_values_absent": not any(value in root_values.values() for value in old),
        "generic_bio_repairs_absent": not any(
            phrase in row["natural_event_phrase_de"]
            for row in bio
            for phrase in ("ANSATZ verwenden", "MERKEN verwenden", "MASS verwenden", "PORTION verwenden", "STELLEN verwenden", "BEGINN verwenden")
        ),
        "all_values_present": all(row["complete_working_reading_de"].strip() for row in events),
        "sealed_absent": "f84" not in payload.lower(),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "PASS995_VALIDATION.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
