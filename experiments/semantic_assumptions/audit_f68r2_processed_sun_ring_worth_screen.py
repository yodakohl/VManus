#!/usr/bin/env python3
"""Build the compact f68r2 processed Sun-ring worth-screen result."""

from __future__ import annotations

import argparse
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


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode()


def build() -> tuple[dict[str, object], str]:
    with OBS.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    if len(rows) != 1:
        raise SystemExit("expected one fixed target")
    row = rows[0]
    expected = {
        "target": "SUN_RING_DISPUTED_ENDING",
        "folio": "f68r2",
        "locus": "f68r2.31",
        "yale_manifest_item": "122",
        "processed_image_number": "123",
        "official_canvas_id": "1006196",
        "orientations_inspected": "4",
        "stable_plain_character_count": "0",
        "stable_plain_segmentation": "NO",
        "separate_inscription_or_equivalence": "NO",
        "decision": "NO_NEW_ANCHOR",
    }
    if any(row[key] != value for key, value in expected.items()):
        raise SystemExit("registered observation changed")
    if any(len(row[field]) != 64 for field in ("official_sha256", "processed_sha256")):
        raise SystemExit("invalid source hash")
    result: dict[str, object] = {
        "experiment": "F68R2_PROCESSED_SUN_RING_WORTH_SCREEN",
        "schema": "F68R2_PROCESSED_SUN_RING_WORTH_SCREEN_V1",
        "status": "STOP_PROCESSED_RENDERING_NO_READABLE_PLAIN_SCRIPT_OR_EQUIVALENCE",
        "decision": "CLOSE_BOUNDED_PROCESSED_F68R2_NEAR_MISS",
        "counts": {
            "targets_inspected": 1,
            "official_images": 1,
            "processed_images": 1,
            "orientations_inspected": 4,
            "stable_plain_characters": 0,
            "separate_inscriptions_or_equivalences": 0,
            "translation_anchors": 0,
        },
        "target": {
            "locus": row["locus"],
            "observation": row["observation"],
            "decision": row["decision"],
        },
        "source_mapping": {
            "yale_manifest_item": int(row["yale_manifest_item"]),
            "processed_image_number": int(row["processed_image_number"]),
            "official_canvas_id": row["official_canvas_id"],
            "official_url": row["official_url"],
            "official_sha256": row["official_sha256"],
            "official_dimensions": row["official_dimensions"],
            "processed_url": row["processed_url"],
            "processed_sha256": row["processed_sha256"],
            "processed_dimensions": row["processed_dimensions"],
        },
        "inputs": {
            str(METHOD.relative_to(ROOT)): sha(METHOD),
            str(OBS.relative_to(ROOT)): sha(OBS),
            str(PRIOR.relative_to(ROOT)): sha(PRIOR),
            str(PLAIN_SCREEN.relative_to(ROOT)): sha(PLAIN_SCREEN),
        },
        "claim_ceiling": (
            "The public paint-removal rendering does not turn the f68r2.31 ending into a stable plain-script sequence or "
            "a separate inscription/equivalence. It supplies no SUN/Suna word, koiin preference, letter, sound, language, "
            "cipher, plaintext, meaning, or translation."
        ),
    }
    report = (
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
