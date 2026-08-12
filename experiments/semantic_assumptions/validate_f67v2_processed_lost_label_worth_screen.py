#!/usr/bin/env python3
"""Independent compact reconstruction of the f67v2 lost-label screen."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "experiments/semantic_assumptions"
METHOD = BASE / "F67V2_PROCESSED_LOST_LABEL_WORTH_SCREEN_METHOD.md"
OBS = BASE / "f67v2_processed_lost_label_worth_screen_observations.tsv"
ANNOTATIONS = BASE / "results/existing_human_exact_locus_annotations.tsv"
PRIOR = BASE / "results/special_circle_plain_legend_native_visual_screen.json"
RESULT = BASE / "results/f67v2_processed_lost_label_worth_screen.json"
REPORT = BASE / "results/f67v2_processed_lost_label_worth_screen_report.md"
OUT_JSON = BASE / "results/f67v2_processed_lost_label_worth_screen_validation.json"
OUT_MD = BASE / "results/f67v2_processed_lost_label_worth_screen_validation_report.md"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode()


def main() -> None:
    checks: list[str] = []
    with OBS.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    assert [row["target"] for row in rows] == ["SOUTHWEST_CORNER_LABEL", "GHOST_ANNULUS"]
    checks.append("exact_two_target_order")
    assert {(row["yale_manifest_item"], row["processed_image_number"], row["official_canvas_id"]) for row in rows} == {
        ("121", "122", "1006195")
    }
    assert {row["official_sha256"] for row in rows} == {"4799e8ebd8d968ea28dae919cfb86065566662b4e77c8b429d12e3e6e685638b"}
    assert {row["processed_sha256"] for row in rows} == {"964b1a1124af7fe50b6e0208638d28fe9c3637ac73aa00de3bd431445db4b6d4"}
    checks.append("exact_source_mapping_and_hashes")
    with ANNOTATIONS.open(newline="", encoding="utf-8") as handle:
        hit = [row for row in csv.DictReader(handle, delimiter="\t") if row["locus"] == "f67v2.21"]
    assert len(hit) == 1 and "written sideways upwards" in hit[0]["local_comment"] and "quite unreadable" in hit[0]["local_comment"]
    checks.append("human_target_annotation_reconstructed")
    for row in rows:
        assert row["stable_character_count"] == "0"
        assert row["stable_segmentation"] == "NO"
        assert row["distinct_from_damage_or_pigment"] == "NO"
        assert row["new_surface_recovered"] == "NO"
        assert row["decision"] == "NO_RECOVERY"
    checks.append("no_recovery_rule")
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    assert result["counts"] == {
        "new_register_surfaces": 0,
        "official_images": 1,
        "processed_images": 1,
        "stable_characters_recovered": 0,
        "stable_sequences_recovered": 0,
        "targets_inspected": 2,
        "translation_anchors": 0,
    }
    checks.append("aggregate_counts_reconstructed")
    assert result["inputs"] == {
        "experiments/semantic_assumptions/F67V2_PROCESSED_LOST_LABEL_WORTH_SCREEN_METHOD.md": sha(METHOD),
        "experiments/semantic_assumptions/f67v2_processed_lost_label_worth_screen_observations.tsv": sha(OBS),
        "experiments/semantic_assumptions/results/existing_human_exact_locus_annotations.tsv": sha(ANNOTATIONS),
        "experiments/semantic_assumptions/results/special_circle_plain_legend_native_visual_screen.json": sha(PRIOR),
    }
    checks.append("input_hashes_bound")
    assert result["status"] == "STOP_NO_RECOVERABLE_SOUTHWEST_LABEL_OR_GHOST_RING_TEXT"
    assert result["decision"] == "STOP_BOUNDED_F67V2_PROCESSED_SCREEN_NO_SURFACE"
    assert "no direction, corner name" in result["claim_ceiling"]
    checks.append("status_decision_ceiling")
    expected_report = (
        "# f67v2 processed lost-label worth screen\n\n"
        "Decision: **STOP — NO RECOVERABLE SOUTHWEST LABEL OR GHOST-RING TEXT**.\n\n"
        "The official Yale image retains faint brownish traces along the damaged west side of the southwest corner circle. "
        "The public paint-removal rendering suppresses the coloured sector but does not resolve a stable stroke sequence or "
        "character count. The faint annular trace likewise yields no stable glyph boundaries or recoverable sequence and "
        "cannot be distinguished here from reverse-side show-through, texture, or a transformation artefact.\n\n"
        "This source-bound native AI assessment is machine-authored, not human annotation. Paint removal is an algorithmic "
        "display transform rather than physical-layer imaging. No OCR, automated transcription, glyph classifier, CLIP, "
        "embedding, similarity score, proposed reading, decoder, or language fit was used. The result adds no missing "
        "special-circle surface and supplies no direction, corner name, object, word, sound, language, cipher, plaintext, "
        "meaning, or translation.\n"
    )
    assert REPORT.read_text(encoding="utf-8") == expected_report
    checks.append("report_bytes_reconstructed")
    validation = {
        "experiment": "F67V2_PROCESSED_LOST_LABEL_WORTH_SCREEN_VALIDATION",
        "schema": "F67V2_PROCESSED_LOST_LABEL_WORTH_SCREEN_VALIDATION_V1",
        "status": "PASS_8_CHECK_COMPACT_RECONSTRUCTION",
        "check_count": len(checks),
        "checks": checks,
        "validated_result_sha256": sha(RESULT),
        "validated_report_sha256": sha(REPORT),
        "claim_ceiling": "Validation confirms only the bounded f67v2 processed-image stop and supplies no translation.",
    }
    assert len(checks) == 8
    OUT_JSON.write_bytes(canonical(validation))
    OUT_MD.write_text(
        "# f67v2 processed lost-label validation\n\n"
        "Status: **PASS — 8 compact reconstruction checks**.\n\n"
        "Independent code reconstructs the two targets, Yale-to-processed mapping, human annotation, no-recovery rule, "
        "aggregate counts, input hashes, decision ceiling, and exact report bytes. It validates only this f67v2 stop and "
        "supplies no translation.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
