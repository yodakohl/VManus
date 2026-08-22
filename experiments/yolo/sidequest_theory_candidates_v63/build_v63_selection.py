#!/usr/bin/env python3
"""Bind the selected bounded V63 slot parser."""

from __future__ import annotations

import csv
import hashlib
import json
import shutil
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent


def rows(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    json_validations = [HERE / "V63_R1_VALIDATION.json", HERE / "V63_R2_VALIDATION.json", HERE / "V63_R4_VALIDATION.json"]
    r3_validator = HERE / "V63_R3_VALIDATE_BOUNDED_SLOT_PARSER.py"
    sources = {
        "templates": HERE / "V63_R3_TEMPLATE_DEFINITIONS.tsv",
        "events": HERE / "V63_R3_381_EVENT_TEMPLATE_LEDGER.tsv",
        "fields": HERE / "V63_R3_135_FIELD_SLOT_PARSE.tsv",
        "statements": HERE / "V63_R3_116_STATEMENT_SLOT_PARSE.tsv",
        "baselines": HERE / "V63_R3_BASELINE_COMPARISON.tsv",
    }
    outputs = {
        "templates": HERE / "V63_SELECTED_TEMPLATE_DEFINITIONS.tsv",
        "events": HERE / "V63_SELECTED_381_EVENT_TEMPLATE_LEDGER.tsv",
        "fields": HERE / "V63_SELECTED_135_FIELD_SLOT_PARSE.tsv",
        "statements": HERE / "V63_SELECTED_116_STATEMENT_SLOT_PARSE.tsv",
        "baselines": HERE / "V63_SELECTED_BASELINE_COMPARISON.tsv",
    }
    for key in sources:
        shutil.copyfile(sources[key], outputs[key])
    events = rows(sources["events"])
    fields = rows(sources["fields"])
    statements = rows(sources["statements"])
    checks = {
        "r1_r2_r4_validations_pass": all(json.loads(path.read_text(encoding="utf-8"))["status"] == "PASS" for path in json_validations),
        "r3_validator_source_present": r3_validator.exists(),
        "events_381": len(events) == 381,
        "recognized_events_119": sum(row["event_template"] != "EXEMPLAR_ONLY" for row in events) == 119,
        "field_profile": Counter(row["parse_status"] for row in fields) == Counter({"UNIQUE": 14, "AMBIGUOUS": 56, "UNPARSED": 65}),
        "statement_profile": Counter(row["parse_status"] for row in statements) == Counter({"UNIQUE": 12, "AMBIGUOUS": 49, "UNPARSED": 55}),
        "all_135_fields": len(fields) == 135,
        "all_116_statements": len(statements) == 116,
        "no_f84": all(not row["page"].startswith("f84") for row in events + fields + statements),
    }
    validation = {
        "schema": "SIDEQUEST_V63_FOUR_ROLE_SELECTION_V1",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "selected_model": "R3_BOUNDED_ORDERED_SLOT_PARSER",
        "role_evidence_hashes": {
            **{str(path.relative_to(ROOT)): sha(path) for path in json_validations},
            str(r3_validator.relative_to(ROOT)): sha(r3_validator),
        },
        "outputs": {str(path.relative_to(ROOT)): sha(path) for path in outputs.values()},
    }
    (HERE / "V63_SELECTION_VALIDATION.json").write_text(json.dumps(validation, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if validation["status"] != "PASS":
        raise SystemExit(json.dumps(validation, indent=2))


if __name__ == "__main__":
    main()
