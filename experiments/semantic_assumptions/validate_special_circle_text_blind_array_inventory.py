#!/usr/bin/env python3
"""Independent reconstruction of the special-circle filler-blind inventory."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "experiments/semantic_assumptions"
SOURCE = BASE / "results/existing_human_exact_locus_annotations.tsv"
METHOD = BASE / "SPECIAL_CIRCLE_TEXT_BLIND_ARRAY_INVENTORY_METHOD.md"
TSV = BASE / "results/special_circle_text_blind_array_inventory.tsv"
RESULT = BASE / "results/special_circle_text_blind_array_inventory.json"
REPORT = BASE / "results/special_circle_text_blind_array_inventory_report.md"
OUT_JSON = BASE / "results/special_circle_text_blind_array_inventory_validation.json"
OUT_MD = BASE / "results/special_circle_text_blind_array_inventory_validation_report.md"
SUFFIXES = {"L0", "Ls", "Lz", "La", "Ri", "Ro"}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode()


def main() -> None:
    checks: list[str] = []
    with SOURCE.open(newline="", encoding="utf-8") as handle:
        source_rows = list(csv.DictReader(handle, delimiter="\t"))
    groups: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    order: list[tuple[str, str]] = []
    for row in source_rows:
        match = re.match(r"^f(\d+)", row["page"])
        if not match or not 67 <= int(match.group(1)) <= 73:
            continue
        key = (row["page"], row["unit"])
        if key not in groups:
            order.append(key)
        groups[key].append(row)
    selected = [
        (key, groups[key])
        for key in order
        if sum(bool(row["normalized_code"]) and row["normalized_code"][-2:] in SUFFIXES for row in groups[key]) >= 3
    ]
    assert len(selected) == 45
    checks.append("exact_mechanical_array_selection")
    reconstructed: list[tuple[str, str, str, str, str, str]] = []
    for array_index, ((page, unit), rows) in enumerate(selected, 1):
        array_id = f"SCARR{array_index:03d}|{page}|{unit}"
        for slot_index, row in enumerate(rows, 1):
            reconstructed.append((array_id, str(slot_index), str(len(rows)), page, unit, row["locus"]))
    with TSV.open(newline="", encoding="utf-8") as handle:
        tsv_rows = list(csv.DictReader(handle, delimiter="\t"))
    observed = [(row["array_id"], row["slot_index"], row["slot_count"], row["page"], row["unit"], row["locus"]) for row in tsv_rows]
    assert observed == reconstructed
    checks.append("exact_array_and_slot_order")
    assert (len(tsv_rows), sum(row["occupied"] == "YES" for row in tsv_rows), sum(row["occupied"] == "NO" for row in tsv_rows)) == (504, 502, 2)
    assert [(row["page"], row["unit"], row["locus"]) for row in tsv_rows if row["occupied"] == "NO"] == [
        ("f67v2", "M1", "f67v2.21"),
        ("f72r2", "S1", "f72r2.33"),
    ]
    checks.append("exact_occupied_and_missing_slots")
    assert len({row["page"] for row in tsv_rows}) == 23
    assert len({row["physical_folio"] for row in tsv_rows}) == 7
    assert all(67 <= int(row["physical_folio"][1:]) <= 73 for row in tsv_rows)
    checks.append("exact_page_and_folio_scope")
    source_fields = set(source_rows[0])
    assert not ({"surface", "family", "member", "root", "translation", "meaning"} & source_fields)
    assert all("surface" not in row and "family" not in row and "member" not in row and "root" not in row for row in tsv_rows)
    checks.append("filler_identity_fields_absent")
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    assert result["counts"] == {
        "arrays": 45,
        "occupied_slots": 502,
        "page_panels": 23,
        "physical_folios": 7,
        "slots": 504,
        "source_explicit_missing_slots": 2,
        "within_array_linear_adjacencies": 459,
    }
    assert result["inventory_tsv_sha256"] == sha(TSV)
    checks.append("aggregate_counts_and_tsv_hash")
    assert result["inputs"] == {
        "experiments/semantic_assumptions/SPECIAL_CIRCLE_TEXT_BLIND_ARRAY_INVENTORY_METHOD.md": sha(METHOD),
        "experiments/semantic_assumptions/results/existing_human_exact_locus_annotations.tsv": sha(SOURCE),
    }
    assert result["historical_eas001_relation"] == {
        "current_counts": {"arrays": 45, "physical_folios": 7, "slots": 504},
        "historical_counts": {"arrays": 46, "physical_folios": 13, "slots": 391},
        "historical_score_inherited": False,
        "same_inventory": False,
    }
    checks.append("inputs_and_historical_noninheritance")
    expected_report = (
        "# Special-circle text-blind array inventory\n\n"
        "Status: **PASS — NEW VERSIONED FILLER-BLIND INVENTORY**.\n\n"
        "A mechanical scan of the current human exact-locus annotation table selects **45 arrays**, **504 slots**, "
        "**502 occupied label/radial slots**, and **2 source-explicit missing slots** across **23 page panels** on "
        "**7 physical folios** from f67 through f73. Selection uses only page, unit, and human layout code; no Voynich "
        "surface, family, member, root, parser role, gloss, or image feature enters.\n\n"
        "This is not the lost historical EAS001 inventory: its 45/504/7 scope differs from the historical 46/391/13 "
        "summary, and no historical score is inherited. The new inventory authorizes only a separate score-blind design. "
        "It establishes no record boundary or cross-diagram slot equivalence and supplies no direction, month, star, nymph, "
        "object, field, word, sound, language, cipher, plaintext, meaning, or translation.\n"
    )
    assert REPORT.read_text(encoding="utf-8") == expected_report
    assert result["status"] == "PASS_NEW_VERSIONED_TEXT_BLIND_SPECIAL_CIRCLE_INVENTORY"
    assert result["decision"] == "AUTHORIZE_SEPARATE_SCORE_BLIND_DESIGN_ONLY"
    checks.append("report_status_and_ceiling")
    validation = {
        "experiment": "SPECIAL_CIRCLE_TEXT_BLIND_ARRAY_INVENTORY_VALIDATION",
        "schema": "SPECIAL_CIRCLE_TEXT_BLIND_ARRAY_INVENTORY_VALIDATION_V1",
        "status": "PASS_8_CHECK_INDEPENDENT_RECONSTRUCTION",
        "check_count": len(checks),
        "checks": checks,
        "validated_inventory_sha256": sha(TSV),
        "validated_result_sha256": sha(RESULT),
        "validated_report_sha256": sha(REPORT),
        "claim_ceiling": "Validation confirms only the new filler-blind special-circle inventory and supplies no translation.",
    }
    assert len(checks) == 8
    OUT_JSON.write_bytes(canonical(validation))
    OUT_MD.write_text(
        "# Special-circle text-blind inventory validation\n\n"
        "Status: **PASS — 8 independent reconstruction checks**.\n\n"
        "Independent code rebuilds the exact array selection and slot order, occupied/missing slots, page/folio scope, "
        "identity-field exclusion, aggregate counts, source bindings, historical noninheritance, and report ceiling. It "
        "validates only this new inventory and supplies no translation.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
