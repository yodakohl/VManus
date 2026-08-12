#!/usr/bin/env python3
"""Independent compact reconstruction of the correction-pair screen."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "experiments/semantic_assumptions"
METHOD = BASE / "PROCESSED_CORRECTION_PAIR_WORTH_SCREEN_METHOD.md"
OBS = BASE / "processed_correction_pair_worth_screen_observations.tsv"
EVT = ROOT / "transcription/sources/Stolfi_text25e1-52.evt"
RESULT = BASE / "results/processed_correction_pair_worth_screen.json"
REPORT = BASE / "results/processed_correction_pair_worth_screen_report.md"
OUT_JSON = BASE / "results/processed_correction_pair_worth_screen_validation.json"
OUT_MD = BASE / "results/processed_correction_pair_worth_screen_validation_report.md"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode()


def main() -> None:
    checks: list[str] = []
    with OBS.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    assert [(row["locus"], row["proposed_transition"]) for row in rows] == [
        ("f16r.2", "e_TO_l"),
        ("f24v.6", "a_TO_s"),
        ("f26r.1", "ch_TO_sh"),
    ]
    checks.append("exact_three_candidate_order")
    assert [int(row["candidate_instances"]) for row in rows] == [1, 1, 2]
    assert [(row["yale_manifest_item"], row["processed_image_number"], row["official_canvas_id"]) for row in rows] == [
        ("30", "031", "1006104"),
        ("47", "048", "1006121"),
        ("50", "051", "1006124"),
    ]
    checks.append("exact_instance_and_source_mapping")
    source = EVT.read_bytes()
    for locus, phrase in {
        b"<f16r.2;U>": b"corrected to @l",
        b"<f24v.6;U>": b"final @s is over the preceding @a",
        b"<f26r.1;U>": b"corrected to @'sh'",
    }.items():
        assert 0 < source.find(locus) - source.find(phrase) < 1000
    checks.append("human_proposals_reconstructed")
    for row in rows:
        assert len(row["official_sha256"]) == 64 and len(row["processed_sha256"]) == 64
        assert row["stable_after_form"] == "YES"
        assert row["stable_before_form"] == "NO"
        assert row["physical_order_resolved"] == "NO"
        assert row["distinct_from_variant_or_damage"] == "NO"
        assert row["recoverable_pair"] == "NO"
        assert row["decision"] == "NO_PAIR"
    checks.append("all_candidates_fail_pair_rule")
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    assert result["counts"] == {
        "candidate_instances": 4,
        "loci_inspected": 3,
        "official_images": 3,
        "processed_images": 3,
        "recoverable_correction_pairs": 0,
        "resolved_physical_orders": 0,
        "stable_before_forms": 0,
        "translation_anchors": 0,
        "visible_current_forms": 4,
    }
    checks.append("aggregate_counts_reconstructed")
    assert result["inputs"] == {
        "experiments/semantic_assumptions/PROCESSED_CORRECTION_PAIR_WORTH_SCREEN_METHOD.md": sha(METHOD),
        "experiments/semantic_assumptions/processed_correction_pair_worth_screen_observations.tsv": sha(OBS),
        "transcription/sources/Stolfi_text25e1-52.evt": sha(EVT),
    }
    checks.append("input_hashes_bound")
    assert result["status"] == "STOP_NO_RECOVERABLE_BEFORE_AFTER_CORRECTION_PAIR"
    assert result["decision"] == "STOP_BOUNDED_THREE_LOCUS_PROCESSED_SCREEN_NO_PAIR"
    assert "no character substitution" in result["claim_ceiling"]
    checks.append("status_decision_ceiling")
    expected_report = (
        "# Processed manuscript-correction pair worth screen\n\n"
        "Decision: **STOP — NO RECOVERABLE BEFORE/AFTER PAIR**.\n\n"
        "The official and paint-removal witnesses show the current unusual forms at f16r.2, f24v.6, and the two f26r.1 "
        "instances. None preserves an independently bounded earlier form plus a visible later intervention. The f26r "
        "plumes therefore remain sh-like variants rather than demonstrated `ch→sh` edits; the proposed f16r `e→l` and "
        "f24v `a→s` transitions likewise remain unresolved.\n\n"
        "This source-bound native AI assessment is machine-authored, not human annotation. Paint removal is an algorithmic "
        "display transform rather than physical-layer imaging. No OCR, automated transcription, glyph classifier, CLIP, "
        "embedding, similarity score, decoder, proposed reading, or language fit was used. The result establishes no "
        "character substitution, sound, word, language, cipher, plaintext, meaning, or translation.\n"
    )
    assert REPORT.read_text(encoding="utf-8") == expected_report
    checks.append("report_bytes_reconstructed")
    validation = {
        "experiment": "PROCESSED_CORRECTION_PAIR_WORTH_SCREEN_VALIDATION",
        "schema": "PROCESSED_CORRECTION_PAIR_WORTH_SCREEN_VALIDATION_V1",
        "status": "PASS_8_CHECK_COMPACT_RECONSTRUCTION",
        "check_count": len(checks),
        "checks": checks,
        "validated_result_sha256": sha(RESULT),
        "validated_report_sha256": sha(REPORT),
        "claim_ceiling": "Validation confirms only the bounded correction-pair stop and supplies no translation.",
    }
    assert len(checks) == 8
    OUT_JSON.write_bytes(canonical(validation))
    OUT_MD.write_text(
        "# Processed correction-pair validation\n\n"
        "Status: **PASS — 8 compact reconstruction checks**.\n\n"
        "Independent code reconstructs the fixed candidates, instance/source mappings, human proposals, no-pair rule, "
        "aggregate counts, input bindings, decision ceiling, and exact report bytes. It validates only this correction-pair "
        "stop and supplies no translation.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
