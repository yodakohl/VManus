#!/usr/bin/env python3
"""Freeze GDT135 before extracting the next-field compiler architecture."""
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
METHOD = ROOT / "GDT135_SECTION_B_FIELD_ARCHITECTURE_TRANSFER_METHOD.md"
INVENTORY = ROOT / "gdt134_general_continuation_inventory.tsv"
OUT = ROOT / "gdt135_prediction.json"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def csha(value):
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode()).hexdigest()


with INVENTORY.open(encoding="utf-8", newline="") as handle:
    rows = [
        row
        for row in csv.DictReader(handle, delimiter="\t")
        if row["primary_continuation_pair"] == "1" and row["section"] == "B"
    ]
assert len(rows) == 69
assert len({row["page"] for row in rows}) == 17
assert len({row["physical_folio"] for row in rows}) == 9
assert not any(row["page"].startswith("f84") or row["locus"].startswith("f84") for row in rows)

prediction = {
    "schema": "GDT135_SECTION_B_FIELD_ARCHITECTURE_TRANSFER_PREDICTION_V1",
    "status": "FROZEN_POSTSELECTED_BEFORE_TARGET_ARCHITECTURE_EXTRACTION",
    "chronology": "Postselected from the public GDT134 section-B COMPILER12 lead; target entry/closure architecture unextracted at freeze.",
    "panel": {
        "pairs": 69,
        "pages": 17,
        "physical_folios": 9,
        "selection": "GDT134_PRIMARY_CONTINUATION_TO_CONTINUATION_AND_SECTION_B",
    },
    "target": "NEXT_FIRST_FIELD_ENTRY_AND_CLOSURE_ARCHITECTURE_18_EXCLUDING_COUNT",
    "models": ["COMPILER12", "HOST_CHAR3", "RAW_CHAR3"],
    "lambda": 1000.0,
    "worlds": 4096,
    "exact_capacity_gate": 30,
    "exact_null": "PAGE_EXACT_SOURCE_COUNT_FINAL_FIELD_GROUPS_HOST_LENGTH_RAW_LENGTH_EXACT_TARGET_FIELD_COUNT",
    "coarse_null": "PAGE_EXACT_SOURCE_COUNT_EXACT_TARGET_FIELD_COUNT",
    "gates": {
        "compiler_gain_positive": True,
        "compiler_beats_host": True,
        "compiler_beats_raw": True,
        "compiler_positive_at_least_6_of_9_folios": True,
        "compiler_positive_both_source_line_parities": True,
        "exact_capacity_at_least_30": True,
        "exact_max_three_p_le_005": True,
    },
    "f84": {
        "retained_or_parsed": False,
        "new_f84r_access": False,
        "prior_limited_f84r_audit_exposure_inherited": True,
    },
    "claim_ceiling": "Section-B formal adjacent-field transition only; no semantics, language, plaintext, meaning, or translation.",
    "inputs": {
        METHOD.name: sha(METHOD),
        INVENTORY.name: sha(INVENTORY),
        "gdt134_result.json": sha(ROOT / "gdt134_result.json"),
        "gdt016_group_state_inventory.tsv": sha(ROOT / "gdt016_group_state_inventory.tsv"),
        "gdt046_line_frames.tsv": sha(ROOT / "gdt046_line_frames.tsv"),
    },
    "implementation": {Path(__file__).name: sha(Path(__file__))},
}
prediction["prediction_content_sha256"] = csha(prediction)
OUT.write_text(json.dumps(prediction, indent=2, sort_keys=True) + "\n")
print(json.dumps({"status": prediction["status"], "pairs": len(rows), "folios": 9}, sort_keys=True))
