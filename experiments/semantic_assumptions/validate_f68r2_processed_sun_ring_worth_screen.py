#!/usr/bin/env python3
"""Independent compact reconstruction of the f68r2 processed Sun-ring screen."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "experiments/semantic_assumptions"
METHOD = BASE / "F68R2_PROCESSED_SUN_RING_WORTH_SCREEN_METHOD.md"
OBS = BASE / "f68r2_processed_sun_ring_worth_screen_observations.tsv"
PRIOR = BASE / "results/f68r2_sun_ring_native_visual_script_check.json"
PLAIN_SCREEN = BASE / "results/special_circle_plain_legend_native_visual_screen.json"
RESULT = BASE / "results/f68r2_processed_sun_ring_worth_screen.json"
REPORT = BASE / "results/f68r2_processed_sun_ring_worth_screen_report.md"
OUT_JSON = BASE / "results/f68r2_processed_sun_ring_worth_screen_validation.json"
OUT_MD = BASE / "results/f68r2_processed_sun_ring_worth_screen_validation_report.md"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode()


def main() -> None:
    checks: list[str] = []
    with OBS.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    assert len(rows) == 1 and rows[0]["target"] == "SUN_RING_DISPUTED_ENDING" and rows[0]["locus"] == "f68r2.31"
    checks.append("exact_fixed_target")
    row = rows[0]
    assert (row["yale_manifest_item"], row["processed_image_number"], row["official_canvas_id"]) == ("122", "123", "1006196")
    assert row["official_sha256"] == "4b0f31d1e08b8f026886aa599232b7dfcd33417b1eef43a44e619c3ebd21faa5"
    assert row["processed_sha256"] == "d0f514f06eef6ad84a52fd2225017a352bce97a3d68b02bf201a5285a06dd09e"
    checks.append("exact_source_mapping_and_hashes")
    assert row["orientations_inspected"] == "4"
    assert row["stable_plain_character_count"] == "0"
    assert row["stable_plain_segmentation"] == "NO"
    assert row["separate_inscription_or_equivalence"] == "NO"
    assert row["decision"] == "NO_NEW_ANCHOR"
    checks.append("exact_no_anchor_rule")
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    assert result["counts"] == {
        "official_images": 1,
        "orientations_inspected": 4,
        "processed_images": 1,
        "separate_inscriptions_or_equivalences": 0,
        "stable_plain_characters": 0,
        "targets_inspected": 1,
        "translation_anchors": 0,
    }
    checks.append("aggregate_counts_reconstructed")
    assert result["inputs"] == {
        "experiments/semantic_assumptions/F68R2_PROCESSED_SUN_RING_WORTH_SCREEN_METHOD.md": sha(METHOD),
        "experiments/semantic_assumptions/f68r2_processed_sun_ring_worth_screen_observations.tsv": sha(OBS),
        "experiments/semantic_assumptions/results/f68r2_sun_ring_native_visual_script_check.json": sha(PRIOR),
        "experiments/semantic_assumptions/results/special_circle_plain_legend_native_visual_screen.json": sha(PLAIN_SCREEN),
    }
    checks.append("input_bindings_reconstructed")
    assert result["status"] == "STOP_PROCESSED_RENDERING_NO_READABLE_PLAIN_SCRIPT_OR_EQUIVALENCE"
    assert result["decision"] == "CLOSE_BOUNDED_PROCESSED_F68R2_NEAR_MISS"
    assert "no SUN/Suna word" in result["claim_ceiling"]
    checks.append("status_decision_ceiling")
    expected_report = (
        "# f68r2 processed Sun-ring worth screen\n\n"
        "Decision: **STOP — NO READABLE PLAIN-SCRIPT SEQUENCE OR EQUIVALENCE**.\n\n"
        "The public paint-removal rendering suppresses the lower medallion's blue paint and increases the contrast of "
        "the existing brown circular writing. The disputed ending remains in the same narrow register as the ordinary "
        "Voynich-style forms. Inspection of the bounded medallion crop in four orientations yields no stable plain-"
        "alphabet character sequence and no separately bounded inscription, gloss, pointer, or equivalence.\n\n"
        "This is source-bound native AI inspection, not human palaeography. The processed rendering is an algorithmic "
        "display transform rather than physical-layer or multispectral evidence. No OCR, automated transcription, glyph "
        "classifier, CLIP, embedding, proposed reading, decoder, or language fit was used. This closes only the new "
        "processed-image witness; it supplies no SUN/Suna word, koiin preference, letter, sound, language, cipher, "
        "plaintext, meaning, or translation.\n"
    )
    assert REPORT.read_text(encoding="utf-8") == expected_report
    checks.append("report_bytes_reconstructed")
    assert result["source_mapping"] == {
        "official_canvas_id": "1006196",
        "official_dimensions": "7993x3828",
        "official_sha256": row["official_sha256"],
        "official_url": row["official_url"],
        "processed_dimensions": "3996x1914",
        "processed_image_number": 123,
        "processed_sha256": row["processed_sha256"],
        "processed_url": row["processed_url"],
        "yale_manifest_item": 122,
    }
    checks.append("exact_source_projection")
    validation = {
        "experiment": "F68R2_PROCESSED_SUN_RING_WORTH_SCREEN_VALIDATION",
        "schema": "F68R2_PROCESSED_SUN_RING_WORTH_SCREEN_VALIDATION_V1",
        "status": "PASS_8_CHECK_COMPACT_RECONSTRUCTION",
        "check_count": len(checks),
        "checks": checks,
        "validated_result_sha256": sha(RESULT),
        "validated_report_sha256": sha(REPORT),
        "claim_ceiling": "Validation confirms only the bounded processed f68r2 stop and supplies no translation.",
    }
    assert len(checks) == 8
    OUT_JSON.write_bytes(canonical(validation))
    OUT_MD.write_text(
        "# f68r2 processed Sun-ring validation\n\n"
        "Status: **PASS — 8 compact reconstruction checks**.\n\n"
        "Independent code reconstructs the fixed target, exact official-to-processed mapping, no-anchor rule, counts, "
        "input bindings, decision ceiling, report bytes, and source projection. It validates only this bounded processed "
        "f68r2 stop and supplies no translation.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
