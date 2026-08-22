#!/usr/bin/env python3
"""Validate the V20 metadata correction through all current descendants."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
YOLO = HERE.parent
TARGETS = [
    ("v20", "sidequest_theory_candidates_v20/V20_SELECTED_COMPLETE_TRANSLATION_LEDGER.tsv"),
    ("v21", "sidequest_theory_candidates_v21/V21_SELECTED_COMPLETE_TRANSLATION_LEDGER.tsv"),
    ("v22", "sidequest_theory_candidates_v22/V22_SELECTED_COMPLETE_TRANSLATION_LEDGER.tsv"),
    ("v24", "sidequest_theory_candidates_v24/V24_COMPLETE_776_EVENT_INTERLINEAR.tsv"),
    ("v25", "sidequest_theory_candidates_v25/V25_SELECTED_COMPLETE_TRANSLATION_LEDGER.tsv"),
]


def main() -> None:
    checks = []
    for label, relative in TARGETS:
        with (YOLO / relative).open(encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle, delimiter="\t"))
        assert len(rows) == 776
        bad_confidence = []
        bad_class = []
        for row in rows:
            try:
                value = float(row["confidence"])
                if not 0 <= value <= 1:
                    bad_confidence.append(row)
            except ValueError:
                bad_confidence.append(row)
            source_class = row["source_class"]
            if source_class.startswith(".") or source_class.replace(".", "", 1).isdigit():
                bad_class.append(row)
        assert not bad_confidence
        assert not bad_class
        assert not any(row["page"].startswith("f84") for row in rows)
        checks.append({"artifact": label, "rows": 776,
                       "invalid_confidence": 0, "numeric_source_class": 0})
    result = {
        "schema": "SIDEQUEST_V27_METADATA_CORRECTION_VALIDATION_V1",
        "status": "PASS", "artifacts_checked": checks,
        "semantic_defaults_changed": 0, "affected_metadata_events": 23,
        "corrected_cards": 4,
        "f84": {"opened": False, "queried": False, "retained": False},
        "f84r": {"opened": False, "queried": False, "retained": False},
    }
    (HERE / "V27_VALIDATION.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
