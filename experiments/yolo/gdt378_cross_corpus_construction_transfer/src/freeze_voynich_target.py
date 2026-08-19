#!/usr/bin/env python3
"""Freeze the GDT378 f84-free target design without scoring identities."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / "experiments/yolo/gdt378_cross_corpus_construction_transfer"
ART = BASE / "artifacts"
SOURCE = ROOT / "gdt327_joint_tuple_interlinear.tsv"
SIGNATURES = ART / "gdt378_secondary_transfer_signature_freeze.json"
METHOD = BASE / "TARGET_METHOD.md"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def content(obj):
    clone = dict(obj)
    clone.pop("content_hash", None)
    return hashlib.sha256(json.dumps(clone, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def main():
    signatures = json.loads(SIGNATURES.read_text())
    assert signatures["status"] == "FROZEN_BEFORE_ANY_VOYNICH_ACCESS" and signatures["signature_count"] == 4
    rows = 0
    records = set()
    folios = set()
    with SOURCE.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        required = {"page", "physical_folio", "locus", "record_ordinal", "field_ordinal", "joint_tuple_id", "observed_wrapper"}
        assert required <= set(reader.fieldnames or [])
        for row in reader:
            assert not any(row[key].lower().startswith("f84") for key in ("page", "physical_folio", "locus"))
            rows += 1
            records.add((row["page"], row["record_ordinal"]))
            folios.add(row["physical_folio"])
    assert rows == 8448 and len(records) == 288 and len(folios) == 91
    freeze = {
        "schema": "GDT378_VOYNICH_TARGET_DESIGN_FREEZE_V1",
        "status": "FROZEN_BEFORE_VOYNICH_TARGET_SCORING",
        "source_rows": rows,
        "records": len(records),
        "physical_folios": len(folios),
        "signatures": [row["anonymous_signature_id"] for row in signatures["signatures"]],
        "resolutions": ["ATOMIC_JOINT_TUPLE", "SOURCE_GROUP", "FIELD_CONSTRUCTION_SPAN", "GRAMMAR_SLOT_POSITION"],
        "slot_families": ["FROM_START", "FROM_END", "RELATIVE_QUARTILE", "CLOSURE", "FROM_START_X_CLOSURE"],
        "minimum_events": 12,
        "minimum_physical_folios": 3,
        "minimum_registers": 2,
        "minimum_positive_gain_folio_fraction": .60,
        "minimum_positive_residual_folio_fraction": 2 / 3,
        "minimum_positive_residual_registers": 2,
        "candidate_shrinkage": 16,
        "null_worlds": 4096,
        "max_family_p_max": .05,
        "null_scope": "TWO_SIDED_MAX_ALL_SIGNATURES_RESOLUTIONS_CANDIDATES_AND_SLOT_FAMILIES",
        "voynich_scored": False,
        "f84": {"opened": False, "parsed": False, "retained": False, "scored": False},
        "inputs": {
            str(SOURCE.relative_to(ROOT)): sha(SOURCE),
            str(SIGNATURES.relative_to(ROOT)): sha(SIGNATURES),
        },
        "documents": {str(METHOD.relative_to(ROOT)): sha(METHOD)},
        "implementation": {str(Path(__file__).relative_to(ROOT)): sha(Path(__file__))},
        "claim_ceiling": "ANONYMOUS_MULTI_RESOLUTION_CONSTRUCTION_TRANSFER_ONLY",
    }
    freeze["content_hash"] = content(freeze)
    (ART / "gdt378_voynich_target_design_freeze.json").write_text(json.dumps(freeze, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": freeze["status"], "rows": rows, "records": len(records), "folios": len(folios)}))


if __name__ == "__main__":
    main()
