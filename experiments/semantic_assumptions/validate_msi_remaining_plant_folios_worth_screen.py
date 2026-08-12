#!/usr/bin/env python3
"""Independent compact reconstruction of the remaining-MSI screen."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "experiments/semantic_assumptions"
METHOD = BASE / "MSI_REMAINING_PLANT_FOLIOS_WORTH_SCREEN_METHOD.md"
OBS = BASE / "msi_remaining_plant_folios_worth_screen_observations.tsv"
RESULT = BASE / "results/msi_remaining_plant_folios_worth_screen.json"
REPORT = BASE / "results/msi_remaining_plant_folios_worth_screen_report.md"
OUT_JSON = BASE / "results/msi_remaining_plant_folios_worth_screen_validation.json"
OUT_MD = BASE / "results/msi_remaining_plant_folios_worth_screen_validation_report.md"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode()


def main() -> None:
    checks: list[str] = []
    with OBS.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    assert [row["folio"] for row in rows] == ["f26r", "f93r"]
    checks.append("exact_two_folio_order")
    processed = sum(len(row["processed_file_ids"].split("|")) for row in rows)
    comparators = sum(row["comparator_file_ids"] != "NONE" for row in rows)
    assert (processed, comparators) == (4, 1)
    checks.append("exact_source_counts")
    for row in rows:
        assert row["legibility_gain"] == "YES"
        assert row["new_distinct_text_layer"] == "NO"
        assert row["readable_owned_caption"] == "NO"
        assert row["explicit_equivalence"] == "NO"
        assert row["recoverable_correction_pair"] == "NO"
        assert row["decision"] == "NO_ANCHOR"
        assert all(len(value) == 64 for value in row["processed_sha256s"].split("|"))
    checks.append("all_rows_fail_anchor_rule")
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    assert result["counts"] == {
        "comparators": 1,
        "explicit_equivalences": 0,
        "folios_inspected": 2,
        "legibility_gains": 2,
        "new_distinct_text_layers": 0,
        "processed_jpegs": 4,
        "readable_owned_captions": 0,
        "recoverable_correction_pairs": 0,
        "translation_anchors": 0,
    }
    checks.append("aggregate_counts_reconstructed")
    assert result["inputs"] == {
        "experiments/semantic_assumptions/MSI_REMAINING_PLANT_FOLIOS_WORTH_SCREEN_METHOD.md": sha(METHOD),
        "experiments/semantic_assumptions/msi_remaining_plant_folios_worth_screen_observations.tsv": sha(OBS),
    }
    checks.append("input_hashes_bound")
    assert result["status"] == "STOP_NO_ANCHOR_IN_REMAINING_PUBLIC_MSI_PLANT_FOLIOS"
    assert result["decision"] == "STOP_BOUNDED_TWO_FOLIO_SCREEN_NO_ANCHOR"
    assert "no glyph, word, plant name" in result["claim_ceiling"]
    checks.append("status_decision_ceiling")
    expected_report = (
        "# Remaining public-MSI plant-folio worth screen\n\n"
        "Decision: **STOP — NO TRANSLATION ANCHOR ON f26r OR f93r**.\n\n"
        "Three processed f26r views and one processed f93r view plus one true-colour comparator improve separation of "
        "existing ink, pigment, stains, and reverse-side visibility. Neither folio exposes a new distinct text layer, "
        "singularly owned readable caption, explicit equivalence, or recoverable correction pair.\n\n"
        "This source-bound native AI visual assessment is machine-authored, not human annotation. It used no OCR, "
        "automated transcription, CLIP, embedding, image-similarity score, plant identification, proposed reading, "
        "decoder, or language fit. It closes only these two processed-image witnesses and supplies no glyph, word, "
        "plant name, language, cipher, plaintext, meaning, or translation.\n"
    )
    assert REPORT.read_text(encoding="utf-8") == expected_report
    checks.append("report_bytes_reconstructed")
    validation = {
        "experiment": "MSI_REMAINING_PLANT_FOLIOS_WORTH_SCREEN_VALIDATION",
        "schema": "MSI_REMAINING_PLANT_FOLIOS_WORTH_SCREEN_VALIDATION_V1",
        "status": "PASS_7_CHECK_COMPACT_RECONSTRUCTION",
        "check_count": len(checks),
        "checks": checks,
        "validated_result_sha256": sha(RESULT),
        "validated_report_sha256": sha(REPORT),
        "claim_ceiling": "Validation confirms only the bounded f26r/f93r source-data stop and supplies no translation.",
    }
    assert len(checks) == 7
    OUT_JSON.write_bytes(canonical(validation))
    OUT_MD.write_text(
        "# Remaining public-MSI plant-folio validation\n\n"
        "Status: **PASS — 7 compact reconstruction checks**.\n\n"
        "Independent code reconstructs the exact folio order, source counts, no-anchor rule, aggregate counts, input "
        "bindings, decision ceiling, and report bytes. It validates only the f26r/f93r stop and supplies no translation.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
