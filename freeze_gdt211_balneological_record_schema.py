#!/usr/bin/env python3
"""Validate and freeze the external GDT211 bath-record schema."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
AUDIT = ROOT / "GDT211_BALNEOLOGICAL_RECORD_SCHEMA_SOURCE_AUDIT.md"
INVENTORY = ROOT / "gdt211_de_balneis_entry_inventory.tsv"
PROVENANCE = ROOT / "gdt211_source_provenance.json"
OUTPUT = ROOT / "gdt211_source_freeze.json"
ROLES = (
    "identity",
    "location_access",
    "hydraulic_physical",
    "indication",
    "procedure_caution",
    "outcome_testimony",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def content_sha(value: dict) -> str:
    payload = json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode()).hexdigest()


with INVENTORY.open(encoding="utf-8", newline="") as handle:
    rows = list(csv.DictReader(handle, delimiter="\t"))

assert len(rows) == 33
assert [int(row["entry_number"]) for row in rows] == list(range(1, 34))
assert len({row["title"] for row in rows}) == 33
assert all(row["annotation_type"] == "READABLE_SOURCE_ROLE_ANNOTATION" for row in rows)
assert all(row[role] in {"0", "1"} for row in rows for role in ROLES)

baths = [row for row in rows if row["record_class"] == "BATH_RECORD"]
meta = [row for row in rows if row["record_class"] == "META_DEDICATION"]
assert len(baths) == 32 and len(meta) == 1 and meta[0]["entry_number"] == "31"
assert all(row["identity"] == "1" and row["indication"] == "1" for row in baths)
role_counts = {role: sum(int(row[role]) for row in baths) for role in ROLES}
assert role_counts == {
    "identity": 32,
    "location_access": 17,
    "hydraulic_physical": 23,
    "indication": 32,
    "procedure_caution": 20,
    "outcome_testimony": 6,
}

provenance = json.loads(PROVENANCE.read_text(encoding="utf-8"))
assert provenance["f84_accessed"] is False
assert provenance["downloaded_text_sha256"] == "397968f02fc5faf54161f2c0df9e7557f96d36e649a27a140e64c2cfe0c69ecd"

result = {
    "schema": "GDT211_BALNEOLOGICAL_RECORD_SCHEMA_SOURCE_FREEZE_V1",
    "status": "EXTERNAL_BALNEOLOGICAL_RECORD_SCHEMA_FROZEN_BEFORE_Q13_SCORE",
    "numbered_compositions": len(rows),
    "eligible_bath_records": len(baths),
    "excluded_meta_records": len(meta),
    "role_counts": role_counts,
    "record_schema": [
        "IDENTITY",
        "OPTIONAL_LOCATION_ACCESS",
        "OPTIONAL_HYDRAULIC_PHYSICAL",
        "INDICATION",
        "OPTIONAL_PROCEDURE_CAUTION",
        "OPTIONAL_OUTCOME_TESTIMONY",
    ],
    "pre_target_predictions": [
        "PARAGRAPH_START_FIRST_PAGE_HOST_LOWER_CROSS_FOLIO_RECURRENCE",
        "CONTINUATION_MATERIAL_HIGHER_REUSABLE_PAGE_HOST_FRACTION",
    ],
    "semantic_mapping": "NONE",
    "f84": {"accessed": False, "retained": False, "queried": False, "scored": False},
    "inputs": {
        AUDIT.name: sha256(AUDIT),
        INVENTORY.name: sha256(INVENTORY),
        PROVENANCE.name: sha256(PROVENANCE),
    },
    "implementation": {Path(__file__).name: sha256(Path(__file__))},
    "claim_ceiling": "External readable-source record schema only; no Voynich word, role, meaning, plaintext, language, or translation.",
}
result["result_content_sha256"] = content_sha(result)
OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
print(json.dumps({"status": result["status"], "bath_records": len(baths), "role_counts": role_counts}, sort_keys=True))
