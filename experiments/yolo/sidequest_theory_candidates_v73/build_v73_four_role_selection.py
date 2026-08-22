#!/usr/bin/env python3
"""Build the central V73 selection from the four frozen role editions."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def copy_bytes(source: str, target: str) -> None:
    (ROOT / target).write_bytes((ROOT / source).read_bytes())


def main() -> None:
    selected = {
        "V73_R2_100_HERBAL_EVENTS.tsv": "V73_SELECTED_100_EVENT_INTERLINEAR.tsv",
        "V73_R2_20_HERBAL_FIELDS.tsv": "V73_SELECTED_20_FIELD_EDITION.tsv",
        "V73_R2_FIVE_HERBAL_ARTICLES.tsv": "V73_SELECTED_FIVE_ARTICLES.tsv",
    }
    for source, target in selected.items():
        copy_bytes(source, target)

    events = read_tsv(ROOT / selected["V73_R2_100_HERBAL_EVENTS.tsv"])
    fields = read_tsv(ROOT / selected["V73_R2_20_HERBAL_FIELDS.tsv"])
    articles = read_tsv(ROOT / selected["V73_R2_FIVE_HERBAL_ARTICLES.tsv"])
    support = Counter(row["v69_support_class"] for row in events)

    role_bindings = {}
    for role, names in {
        "R1": ["V73_R1_100_EVENT_INTERLINEAR.tsv", "V73_R1_20_FIELD_EDITION.tsv", "V73_R1_FIVE_RECORD_ARTICLES.md", "V73_R1_HERBAL_THIRD_EDITION_REPORT.md", "V73_R1_VALIDATION.json"],
        "R2": ["V73_R2_100_HERBAL_EVENTS.tsv", "V73_R2_20_HERBAL_FIELDS.tsv", "V73_R2_19_HERBAL_STATEMENTS.tsv", "V73_R2_FIVE_HERBAL_ARTICLES.tsv", "V73_R2_UNSUPPORTED_NOUNS.tsv", "V73_R2_HERBAL_THIRD_EDITION_REPORT.md", "V73_R2_VALIDATION.json"],
        "R3": ["V73_R3_100_EVENT_INTERLINEAR.tsv", "V73_R3_20_FIELD_EDITION.tsv", "V73_R3_19_STATEMENT_REVISIONS.tsv", "V73_R3_FIVE_ARTICLES.tsv", "V73_R3_TECHNICAL_REPORT.md", "V73_R3_VALIDATION.json"],
        "R4": ["V73_R4_100_EVENT_INTERLINEAR.tsv", "V73_R4_20_FIELD_EDITION.tsv", "V73_R4_FIVE_RECORD_ARTICLES.md", "V73_R4_CHANCERY_HERBAL_REPORT.md", "V73_R4_VALIDATION.json"],
    }.items():
        role_bindings[role] = {name: sha256(ROOT / name) for name in names}

    checks = {
        "events_100": len(events) == 100,
        "event_serials_exact": [int(row["event_serial"]) for row in events] == list(range(1, 101)),
        "fields_20": len(fields) == 20,
        "field_ids_exact": {row["field_id"] for row in fields} == {f"F{i:03d}" for i in range(1, 21)},
        "articles_5": len(articles) == 5,
        "records_exact": {row["record_unit_id"] for row in articles} == {"H1", "H2", "H3", "H4", "H5"},
        "statements_19": len({row["statement_id"] for row in events}) == 19,
        "all_meanings_concrete": all(row["concrete_german_meaning_in_context"].strip() for row in events),
        "all_ceiling_labels_present": all(row["semantic_ceiling"].strip() for row in events),
        "known_or_formal_29": sum(value for key, value in support.items() if key != "UNKNOWN_EXEMPLAR_WHOLE_CARD") == 29,
        "exemplar_only_71": support["UNKNOWN_EXEMPLAR_WHOLE_CARD"] == 71,
        "four_visible_plant_owners": len({row["whole_plant_owner"] for row in events}) == 4,
        "all_role_validations_pass": all(json.loads((ROOT / f"V73_{role}_VALIDATION.json").read_text(encoding="utf-8"))["status"] == "PASS" for role in ("R1", "R2", "R3", "R4")),
        "f84_not_named": not any("f84" in row["page"].lower() for row in events),
    }
    status = "PASS" if all(checks.values()) else "FAIL"
    payload = {
        "schema": "V73_FOUR_ROLE_SELECTION_VALIDATION_V1",
        "status": status,
        "selection": {
            "primary": "R2_HISTORICAL_HERBAL_RECEPTARIUM",
            "strongest_rival": "R3_NONMEDICAL_PLANT_MATERIAL_PROCESS_REGISTER",
            "interpretation": "CREATIVE_MASTER_EXEMPLAR_NOT_DECIPHERMENT",
        },
        "counts": {
            "events": len(events),
            "fields": len(fields),
            "statements": len({row["statement_id"] for row in events}),
            "records": len(articles),
            "visible_plant_owners": len({row["whole_plant_owner"] for row in events}),
            "supported_or_formal_events": sum(value for key, value in support.items() if key != "UNKNOWN_EXEMPLAR_WHOLE_CARD"),
            "exemplar_only_events": support["UNKNOWN_EXEMPLAR_WHOLE_CARD"],
        },
        "checks": checks,
        "role_bindings": role_bindings,
        "selected_bindings": {target: sha256(ROOT / target) for target in selected.values()},
        "sealed_pages_opened": [],
    }
    (ROOT / "V73_VALIDATION.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if status != "PASS":
        raise SystemExit("V73 selection validation failed")
    print(json.dumps(payload["counts"], ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
