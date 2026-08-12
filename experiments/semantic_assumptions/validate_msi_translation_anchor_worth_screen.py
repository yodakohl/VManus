#!/usr/bin/env python3
"""Independent compact reconstruction of the MSI worth-screen artifacts."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
METHOD = ROOT / "experiments/semantic_assumptions/MSI_TRANSLATION_ANCHOR_WORTH_SCREEN_METHOD.md"
OBS = ROOT / "experiments/semantic_assumptions/msi_translation_anchor_worth_screen_observations.tsv"
RESULT = ROOT / "experiments/semantic_assumptions/results/msi_translation_anchor_worth_screen.json"
REPORT = ROOT / "experiments/semantic_assumptions/results/msi_translation_anchor_worth_screen_report.md"
OUT_JSON = ROOT / "experiments/semantic_assumptions/results/msi_translation_anchor_worth_screen_validation.json"
OUT_MD = ROOT / "experiments/semantic_assumptions/results/msi_translation_anchor_worth_screen_validation_report.md"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(obj: object) -> bytes:
    return (json.dumps(obj, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode()


def main() -> None:
    checks: list[str] = []
    with OBS.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    folios = [row["folio"] for row in rows]
    assert folios == ["f8r", "f17r", "f47r", "f70v1", "f71r", "f102v1", "f116v"]
    checks.append("exact_seven_folio_order")
    assert len(set(folios)) == 7
    checks.append("physical_folios_unique")
    processed = 0
    comparators = 0
    for row in rows:
        assert row["decision"] == "NO_ANCHOR"
        assert row["legibility_gain"] == "YES"
        assert row["new_distinct_text_layer"] == "NO"
        assert row["explicit_equivalence"] == "NO"
        assert row["readable_owned_plain_legend"] == "NO"
        assert row["recoverable_correction_pair"] == "NO"
        pids = row["processed_file_ids"].split("|")
        phashes = row["processed_sha256s"].split("|")
        assert len(pids) == len(phashes) and all(len(value) == 64 for value in phashes)
        processed += len(pids)
        if row["comparator_file_ids"] != "NONE":
            cids = row["comparator_file_ids"].split("|")
            chashes = row["comparator_sha256s"].split("|")
            assert len(cids) == len(chashes) and all(len(value) == 64 for value in chashes)
            comparators += len(cids)
    checks.append("all_rows_fail_frozen_anchor_rule")
    assert processed == 10 and comparators == 5
    checks.append("source_file_counts")
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    expected_counts = {
        "explicit_equivalences": 0,
        "folios_inspected": 7,
        "legibility_gains": 7,
        "new_distinct_text_layers": 0,
        "ordinary_or_psc_comparators": 5,
        "processed_jpegs": 10,
        "readable_owned_plain_legends": 0,
        "recoverable_correction_pairs": 0,
        "translation_anchors": 0,
    }
    assert result["counts"] == expected_counts
    checks.append("result_counts_reconstructed")
    assert result["inputs"] == {
        "experiments/semantic_assumptions/MSI_TRANSLATION_ANCHOR_WORTH_SCREEN_METHOD.md": sha(METHOD),
        "experiments/semantic_assumptions/msi_translation_anchor_worth_screen_observations.tsv": sha(OBS),
    }
    checks.append("input_hashes_bound")
    assert result["status"] == "STOP_NO_NEW_TRANSLATION_ANCHOR_IN_PUBLIC_MSI_SUBSET"
    assert result["decision"] == "STOP_BOUNDED_MSI_WORTH_SCREEN_NO_ANCHOR"
    assert "no glyph, sound, word" in result["claim_ceiling"]
    checks.append("status_decision_claim_ceiling")
    expected_report = (
        "# Public MSI translation-anchor worth screen\n\n"
        "Decision: **STOP — NO NEW TRANSLATION ANCHOR IN THE BOUNDED PUBLIC MSI SUBSET**.\n\n"
        "Seven high-value folios were inspected from the public 2014 Lazarus Project release, using 10 processed JPEGs "
        "and 5 ordinary-light or PSC comparators. All seven gain legibility, but none exposes a new distinct text layer, "
        "explicit equivalence, owned readable plain legend, or recoverable before/after correction pair.\n\n"
        "f17r and f116v become clearer but remain the already registered mixed-script marginal contexts without a gloss "
        "device. f70v1 and f71r add contrast to existing zodiac registers; f70v1's extra pale material is consistent with "
        "show-through or offset rather than a hidden legend. f8r, f47r, and f102v1 reveal no separate writing state.\n\n"
        "This is source-bound native AI visual inspection, not human annotation. No OCR, automated transcription, CLIP, "
        "embedding, batch recognition, proposed reading, language fit, or decoder output was used. The stop applies only "
        "to this public processed-image subset and supplies no glyph, sound, word, language, cipher, plaintext, meaning, "
        "or translation.\n"
    )
    assert REPORT.read_text(encoding="utf-8") == expected_report
    checks.append("report_bytes_reconstructed")
    validation = {
        "experiment": "MSI_TRANSLATION_ANCHOR_WORTH_SCREEN_VALIDATION",
        "schema": "MSI_TRANSLATION_ANCHOR_WORTH_SCREEN_VALIDATION_V1",
        "status": "PASS_8_CHECK_COMPACT_RECONSTRUCTION",
        "validated_result_sha256": sha(RESULT),
        "validated_report_sha256": sha(REPORT),
        "check_count": len(checks),
        "checks": checks,
        "claim_ceiling": "Validation confirms only the bounded seven-folio source-data stop and supplies no translation.",
    }
    assert len(checks) == 8
    validation_report = (
        "# Public MSI translation-anchor worth-screen validation\n\n"
        "Status: **PASS — 8 compact reconstruction checks**.\n\n"
        "Independent code reconstructs the seven-folio order, source-file counts, frozen no-anchor rule, aggregate counts, "
        "input bindings, stop decision, claim ceiling, and exact report bytes. It validates only the bounded public-MSI "
        "stop and supplies no glyph, word, plaintext, or translation.\n"
    )
    OUT_JSON.write_bytes(canonical(validation))
    OUT_MD.write_text(validation_report, encoding="utf-8")


if __name__ == "__main__":
    main()
