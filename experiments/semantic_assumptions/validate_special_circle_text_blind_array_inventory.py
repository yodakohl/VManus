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
    assert Counter(row["occupancy_state"] for row in tsv_rows) == Counter({"TRANSCRIBED": 502, "UNREADABLE_TRACE": 1, "ABSENT": 1})
    assert [(row["page"], row["unit"], row["locus"], row["occupancy_state"]) for row in tsv_rows if row["occupancy_state"] != "TRANSCRIBED"] == [
        ("f67v2", "M1", "f67v2.21", "UNREADABLE_TRACE"),
        ("f72r2", "S1", "f72r2.33", "ABSENT"),
    ]
    assert [(row["page"], row["normalized_code"]) for row in tsv_rows if row["occupancy_state"] != "TRANSCRIBED"] == [
        ("f67v2", "NONE"),
        ("f72r2", "NONE"),
    ]
    source_by_locus = {row["locus"]: row for row in source_rows}
    assert "traces of brown ink" in source_by_locus["f67v2.21"]["local_comment"].lower()
    assert "unreadable" in source_by_locus["f67v2.21"]["local_comment"].lower()
    assert "not labeled" in source_by_locus["f72r2.33"]["local_comment"].lower()
    checks.append("exact_occupancy_states")
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
        "page_panels": 23,
        "physical_folios": 7,
        "slots": 504,
        "source_explicit_absent_slots": 1,
        "transcribed_slots": 502,
        "unreadable_trace_slots": 1,
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
    assert result["nontranscribed_slots"] == [
        {
            "array_id": "SCARR005|f67v2|M1",
            "locus": "f67v2.21",
            "occupancy_state": "UNREADABLE_TRACE",
            "page": "f67v2",
            "slot_index": 3,
            "unit": "M1",
        },
        {
            "array_id": "SCARR029|f72r2|S1",
            "locus": "f72r2.33",
            "occupancy_state": "ABSENT",
            "page": "f72r2",
            "slot_index": 14,
            "unit": "S1",
        },
    ]
    expected_report = (
        "# Special-circle text-blind array inventory\n\n"
        "Status: **PASS — CORRECTED VERSIONED FILLER-BLIND INVENTORY**.\n\n"
        "A mechanical scan of the current human exact-locus annotation table selects **45 arrays**, **504 slots**, "
        "**502 transcribed label/radial slots**, **1 unreadable trace slot**, and **1 source-explicit absent slot** across **23 page panels** on "
        "**7 physical folios** from f67 through f73. Selection uses only page, unit, and human layout code; no Voynich "
        "surface, family, member, root, parser role, gloss, or image feature enters.\n\n"
        "This is not the lost historical EAS001 inventory: its 45/504/7 scope differs from the historical 46/391/13 "
        "summary, and no historical score is inherited. The two nontranscribed rows are not homologous omissions: "
        "f67v2.21 retains unreadable ink traces, while only f72r2.33 is explicitly unlabelled. One secure absence on one "
        "folio is insufficient for an omission-pattern test. "
        "It establishes no record boundary or cross-diagram slot equivalence and supplies no direction, month, star, nymph, "
        "object, field, word, sound, language, cipher, plaintext, meaning, or translation.\n"
    )
    assert REPORT.read_text(encoding="utf-8") == expected_report
    assert result["schema"] == "SPECIAL_CIRCLE_TEXT_BLIND_ARRAY_INVENTORY_V2"
    assert result["status"] == "PASS_CORRECTED_VERSIONED_TEXT_BLIND_SPECIAL_CIRCLE_INVENTORY"
    assert result["decision"] == "STOP_OMISSION_PATTERN_ONE_EXPLICIT_ABSENCE"
    checks.append("report_status_and_ceiling")
    validation = {
        "experiment": "SPECIAL_CIRCLE_TEXT_BLIND_ARRAY_INVENTORY_VALIDATION",
        "schema": "SPECIAL_CIRCLE_TEXT_BLIND_ARRAY_INVENTORY_VALIDATION_V2",
        "status": "PASS_8_CHECK_INDEPENDENT_RECONSTRUCTION",
        "check_count": len(checks),
        "checks": checks,
        "validated_inventory_sha256": sha(TSV),
        "validated_result_sha256": sha(RESULT),
        "validated_report_sha256": sha(REPORT),
        "claim_ceiling": "Validation confirms only the corrected filler-blind special-circle inventory and supplies no translation.",
    }
    assert len(checks) == 8
    OUT_JSON.write_bytes(canonical(validation))
    OUT_MD.write_text(
        "# Special-circle text-blind inventory validation\n\n"
        "Status: **PASS — 8 independent reconstruction checks**.\n\n"
        "Independent code rebuilds the exact array selection and slot order, three occupancy states, page/folio scope, "
        "identity-field exclusion, aggregate counts, source bindings, historical noninheritance, and report ceiling. It "
        "validates only this new inventory and supplies no translation.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
