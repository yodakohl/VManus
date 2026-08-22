#!/usr/bin/env python3
"""Assign every fixed prose field to one of five teachable templates."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent
V26 = HERE.parent / "sidequest_theory_candidates_v26"
HERBAL = {"f10r", "f11r", "f55v", "f56r"}


def main() -> None:
    with (V26 / "V26_COMPLETE_135_FIELD_TRANSLATION.tsv").open(
            encoding="utf-8", newline="") as handle:
        fields = list(csv.DictReader(handle, delimiter="\t"))
    assert len(fields) == 135
    output = []
    for row in fields:
        size = len(row["visible_source_field"].split())
        closed = row["closure"] != "OPEN"
        if closed and size == 1:
            template = "T1_SOLO_COMMIT"
            production = "CLOSE_CARD"
            reading = "execute or record one licensed operation/value and commit it"
        elif closed and size <= 3:
            template = "T2_SHORT_COMMIT"
            production = "HEAD_OR_ARGUMENT + OPTIONAL_MODIFIER + CLOSE"
            reading = "instantiate one short operation with at most one local argument; commit"
        elif closed:
            template = "T3_MULTI_CARD_COMMIT"
            production = "HEAD? + ARGUMENT_OR_RELATION* + CONDITION? + ACTION_CLOSE"
            reading = "fill a complete multi-slot operation and commit its result"
        elif row["page"] in HERBAL:
            template = "T4_OPEN_ARTICLE_CLAUSE"
            production = "OWNER_INHERITED + PART_OR_PROPERTY + PREPARATION_OR_USE*"
            reading = "continue the pictured-simple article without forcing a sentence end"
        else:
            template = "T5_OPEN_WORKSHEET_CONTINUATION"
            production = "ACTIVE_CELL_OR_BATCH + ARGUMENT_OR_RELATION* + CARRY"
            reading = "carry an unfinished application/configuration into the next field or line"
        out = dict(row)
        out["template_id"] = template
        out["template_production"] = production
        out["template_reading"] = reading
        out["field_card_count"] = str(size)
        output.append(out)
    path = HERE / "V28_ALL_135_FIELD_TEMPLATES.tsv"
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(output[0]), delimiter="\t",
                                lineterminator="\n")
        writer.writeheader()
        writer.writerows(output)
    counts = Counter(row["template_id"] for row in output)
    assert counts == {
        "T1_SOLO_COMMIT": 44, "T2_SHORT_COMMIT": 28,
        "T3_MULTI_CARD_COMMIT": 18, "T4_OPEN_ARTICLE_CLAUSE": 15,
        "T5_OPEN_WORKSHEET_CONTINUATION": 30,
    }
    result = {
        "schema": "SIDEQUEST_V28_FIVE_TEMPLATE_GRAMMAR_V1", "status": "PASS",
        "fields": 135, "templates": 5, "template_counts": dict(sorted(counts.items())),
        "coverage": 1.0, "semantic_defaults_changed": 0,
        "f84": {"opened": False, "queried": False, "retained": False},
        "f84r": {"opened": False, "queried": False, "retained": False},
    }
    (HERE / "V28_VALIDATION.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
