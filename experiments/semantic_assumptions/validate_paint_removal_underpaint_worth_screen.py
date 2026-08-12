#!/usr/bin/env python3
"""Independent compact reconstruction of the paint-removal worth screen."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "experiments/semantic_assumptions"
METHOD = BASE / "PAINT_REMOVAL_UNDERPAINT_WORTH_SCREEN_METHOD.md"
OBS = BASE / "paint_removal_underpaint_worth_screen_observations.tsv"
RESULT = BASE / "results/paint_removal_underpaint_worth_screen.json"
REPORT = BASE / "results/paint_removal_underpaint_worth_screen_report.md"
OUT_JSON = BASE / "results/paint_removal_underpaint_worth_screen_validation.json"
OUT_MD = BASE / "results/paint_removal_underpaint_worth_screen_validation_report.md"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode()


def main() -> None:
    checks: list[str] = []
    with OBS.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    assert [(row["folio"], row["target_locus"]) for row in rows] == [
        ("f2r", "f2r.15"),
        ("f99v", "f99v.45"),
    ]
    checks.append("exact_two_target_order")
    assert [(row["yale_manifest_item"], row["processed_image_number"], row["official_canvas_id"]) for row in rows] == [
        ("4", "005", "1006078"),
        ("175", "176", "1006247"),
    ]
    checks.append("exact_yale_to_processed_mapping")
    for row in rows:
        assert len(row["processed_sha256"]) == 64
        assert row["processed_url"].endswith(f"image.{row['processed_image_number']}.jpg")
        assert sha(ROOT / row["prior_result_path"]) == row["prior_result_sha256"]
    checks.append("source_and_prior_bindings")
    assert rows[0]["target_legibility_gain"] == "YES"
    assert rows[1]["target_legibility_gain"] == "NO"
    for row in rows:
        assert row["new_stable_character_sequence"] == "NO"
        assert row["new_distinct_text_layer"] == "NO"
        assert row["physical_layer_order_resolved"] == "NO"
        assert row["explicit_equivalence"] == "NO"
        assert row["decision"] == "NO_NEW_ANCHOR"
    checks.append("all_rows_fail_anchor_rule")
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    assert result["counts"] == {
        "explicit_equivalences": 0,
        "new_distinct_text_layers": 0,
        "new_stable_character_sequences": 0,
        "processed_jpegs": 2,
        "resolved_physical_layer_orders": 0,
        "target_legibility_gains": 1,
        "targets_inspected": 2,
        "translation_anchors": 0,
    }
    checks.append("aggregate_counts_reconstructed")
    assert result["public_bindings"] == {
        "gallery_sha256": "afbe0eee6e5b7cdf54534b402f953c18f665881b3da10a1889dbf49ace36dfc5",
        "gallery_url": "https://www.voynich.nu/gallery.html",
        "processed_index_sha256": "332a4bee845104b7f30a1e85a325c320c6895b8e56aedc080c7f96e3dc092b96",
        "processed_index_url": "https://oshfdkbw.pages.dev/",
        "yale_manifest_sha256": "317d58fd9ea90392a83d9858a91eada3d0b41416a3c835857dc0154bd123a309",
        "yale_manifest_url": "https://collections.library.yale.edu/manifests/2002046",
    }
    assert result["inputs"] == {
        "experiments/semantic_assumptions/PAINT_REMOVAL_UNDERPAINT_WORTH_SCREEN_METHOD.md": sha(METHOD),
        "experiments/semantic_assumptions/paint_removal_underpaint_worth_screen_observations.tsv": sha(OBS),
    }
    checks.append("public_and_local_bindings")
    assert result["status"] == "STOP_PROCESSED_PAINT_REMOVAL_NO_NEW_LAYER_OR_SCRIPT_ANCHOR"
    assert result["decision"] == "STOP_BOUNDED_TWO_TARGET_SCREEN_NO_ANCHOR"
    assert "Algorithmic paint suppression is not physical layer evidence" in result["claim_ceiling"]
    checks.append("status_decision_ceiling")
    expected_report = (
        "# Processed paint-removal under-paint worth screen\n\n"
        "Decision: **STOP — NO NEW SCRIPT OR LAYER ANCHOR**.\n\n"
        "The public 2024 paint-removal rendering makes the already transcribed f2r.15 note easier to see after much of "
        "the leaf wash is suppressed. It reveals no additional group or second writing state and cannot establish whether "
        "the ink preceded the paint. On f99v, the alleged trace on the west tuber of plant `[3,4]` remains diffuse tonal "
        "variation without stable character segmentation and is not authenticated as writing.\n\n"
        "The transform is algorithmic display processing, not multispectral or physical layer imaging. This source-bound "
        "native AI assessment is machine-authored, not human annotation, and used no OCR, automated transcription, glyph "
        "classifier, CLIP, embedding, image-similarity score, plant identification, proposed reading, decoder, or language "
        "fit. It closes only these two processed witnesses and supplies no character value, colour gloss, word, sound, "
        "language, cipher, plaintext, meaning, or translation.\n"
    )
    assert REPORT.read_text(encoding="utf-8") == expected_report
    checks.append("report_bytes_reconstructed")
    validation = {
        "experiment": "PAINT_REMOVAL_UNDERPAINT_WORTH_SCREEN_VALIDATION",
        "schema": "PAINT_REMOVAL_UNDERPAINT_WORTH_SCREEN_VALIDATION_V1",
        "status": "PASS_8_CHECK_COMPACT_RECONSTRUCTION",
        "check_count": len(checks),
        "checks": checks,
        "validated_result_sha256": sha(RESULT),
        "validated_report_sha256": sha(REPORT),
        "claim_ceiling": "Validation confirms only the bounded f2r/f99v processed-image stop and supplies no translation.",
    }
    assert len(checks) == 8
    OUT_JSON.write_bytes(canonical(validation))
    OUT_MD.write_text(
        "# Processed paint-removal worth-screen validation\n\n"
        "Status: **PASS — 8 compact reconstruction checks**.\n\n"
        "Independent code reconstructs the two targets, Yale-to-processed mapping, source bindings, no-anchor rule, "
        "aggregate counts, public/local bindings, decision ceiling, and exact report bytes. It validates only this "
        "processed-image stop and supplies no translation.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
