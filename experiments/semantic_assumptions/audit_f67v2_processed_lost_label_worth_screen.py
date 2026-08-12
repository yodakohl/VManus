#!/usr/bin/env python3
"""Build the compact f67v2 processed lost-label worth-screen result."""

from __future__ import annotations

import argparse
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


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode()


def load_rows() -> list[dict[str, str]]:
    with OBS.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    if [row["target"] for row in rows] != ["SOUTHWEST_CORNER_LABEL", "GHOST_ANNULUS"]:
        raise SystemExit("unexpected target order")
    for row in rows:
        if (row["yale_manifest_item"], row["processed_image_number"], row["official_canvas_id"]) != (
            "121",
            "122",
            "1006195",
        ):
            raise SystemExit("unexpected source mapping")
        if row["stable_character_count"] != "0":
            raise SystemExit("unexpected character recovery")
        if any(row[field] != "NO" for field in ("stable_segmentation", "distinct_from_damage_or_pigment", "new_surface_recovered")):
            raise SystemExit("qualifying recovery requires a different result")
        if row["decision"] != "NO_RECOVERY":
            raise SystemExit("unexpected decision")
        if any(len(row[field]) != 64 for field in ("official_sha256", "processed_sha256")):
            raise SystemExit("invalid sha256")
    with ANNOTATIONS.open(newline="", encoding="utf-8") as handle:
        hits = [row for row in csv.DictReader(handle, delimiter="\t") if row["locus"] == "f67v2.21"]
    if len(hits) != 1 or "quite unreadable" not in hits[0]["local_comment"]:
        raise SystemExit("human target annotation mismatch")
    return rows


def build() -> tuple[dict[str, object], str]:
    rows = load_rows()
    result: dict[str, object] = {
        "experiment": "F67V2_PROCESSED_LOST_LABEL_WORTH_SCREEN",
        "schema": "F67V2_PROCESSED_LOST_LABEL_WORTH_SCREEN_V1",
        "status": "STOP_NO_RECOVERABLE_SOUTHWEST_LABEL_OR_GHOST_RING_TEXT",
        "decision": "STOP_BOUNDED_F67V2_PROCESSED_SCREEN_NO_SURFACE",
        "counts": {
            "targets_inspected": 2,
            "official_images": 1,
            "processed_images": 1,
            "stable_characters_recovered": 0,
            "stable_sequences_recovered": 0,
            "new_register_surfaces": 0,
            "translation_anchors": 0,
        },
        "targets": [
            {"target": row["target"], "locus": row["locus"], "observation": row["observation"], "decision": row["decision"]}
            for row in rows
        ],
        "inputs": {
            str(METHOD.relative_to(ROOT)): sha(METHOD),
            str(OBS.relative_to(ROOT)): sha(OBS),
            str(ANNOTATIONS.relative_to(ROOT)): sha(ANNOTATIONS),
            str(PRIOR.relative_to(ROOT)): sha(PRIOR),
        },
        "claim_ceiling": (
            "The processed f67v2 witness does not recover a stable southwest-corner label or a distinct ghost-ring text "
            "sequence. It supplies no direction, corner name, object, word, sound, language, cipher, plaintext, meaning, "
            "or translation."
        ),
    }
    report = (
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
    return result, report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    result, report = build()
    if args.write:
        RESULT.write_bytes(canonical(result))
        REPORT.write_text(report, encoding="utf-8")
    else:
        print(canonical(result).decode(), end="")


if __name__ == "__main__":
    main()
