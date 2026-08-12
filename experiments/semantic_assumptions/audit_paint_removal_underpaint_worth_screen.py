#!/usr/bin/env python3
"""Build the compact processed paint-removal worth-screen result."""

from __future__ import annotations

import argparse
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
BOOLS = (
    "target_legibility_gain",
    "new_stable_character_sequence",
    "new_distinct_text_layer",
    "physical_layer_order_resolved",
    "explicit_equivalence",
)
PUBLIC_BINDINGS = {
    "gallery_url": "https://www.voynich.nu/gallery.html",
    "gallery_sha256": "afbe0eee6e5b7cdf54534b402f953c18f665881b3da10a1889dbf49ace36dfc5",
    "processed_index_url": "https://oshfdkbw.pages.dev/",
    "processed_index_sha256": "332a4bee845104b7f30a1e85a325c320c6895b8e56aedc080c7f96e3dc092b96",
    "yale_manifest_url": "https://collections.library.yale.edu/manifests/2002046",
    "yale_manifest_sha256": "317d58fd9ea90392a83d9858a91eada3d0b41416a3c835857dc0154bd123a309",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode()


def load_rows() -> list[dict[str, str]]:
    with OBS.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    if [(row["folio"], row["target_locus"]) for row in rows] != [
        ("f2r", "f2r.15"),
        ("f99v", "f99v.45"),
    ]:
        raise SystemExit("unexpected target order")
    if [(row["yale_manifest_item"], row["processed_image_number"]) for row in rows] != [
        ("4", "005"),
        ("175", "176"),
    ]:
        raise SystemExit("unexpected manifest/image mapping")
    for row in rows:
        if any(row[field] not in {"YES", "NO"} for field in BOOLS):
            raise SystemExit("invalid boolean")
        if row["decision"] != "NO_NEW_ANCHOR":
            raise SystemExit("unexpected decision")
        if any(row[field] != "NO" for field in BOOLS[1:]):
            raise SystemExit("qualifying relation would require a different decision")
        if any(len(row[field]) != 64 for field in ("processed_sha256", "prior_result_sha256")):
            raise SystemExit("invalid sha256")
        prior = ROOT / row["prior_result_path"]
        if not prior.is_file() or sha(prior) != row["prior_result_sha256"]:
            raise SystemExit("prior source-bound result mismatch")
    return rows


def build() -> tuple[dict[str, object], str]:
    rows = load_rows()
    counts = {
        "targets_inspected": len(rows),
        "processed_jpegs": len(rows),
        "target_legibility_gains": sum(row["target_legibility_gain"] == "YES" for row in rows),
        "new_stable_character_sequences": 0,
        "new_distinct_text_layers": 0,
        "resolved_physical_layer_orders": 0,
        "explicit_equivalences": 0,
        "translation_anchors": 0,
    }
    result: dict[str, object] = {
        "experiment": "PAINT_REMOVAL_UNDERPAINT_WORTH_SCREEN",
        "schema": "PAINT_REMOVAL_UNDERPAINT_WORTH_SCREEN_V1",
        "status": "STOP_PROCESSED_PAINT_REMOVAL_NO_NEW_LAYER_OR_SCRIPT_ANCHOR",
        "decision": "STOP_BOUNDED_TWO_TARGET_SCREEN_NO_ANCHOR",
        "counts": counts,
        "targets": [
            {
                "folio": row["folio"],
                "target_locus": row["target_locus"],
                "target_legibility_gain": row["target_legibility_gain"],
                "observation": row["observation"],
                "decision": row["decision"],
            }
            for row in rows
        ],
        "public_bindings": PUBLIC_BINDINGS,
        "inputs": {
            str(METHOD.relative_to(ROOT)): sha(METHOD),
            str(OBS.relative_to(ROOT)): sha(OBS),
        },
        "claim_ceiling": (
            "The public paint-removal transform clarifies the already known f2r.15 note but does not resolve its ink/paint "
            "order, and it does not turn f99v.45 into a stable character sequence. Algorithmic paint suppression is not "
            "physical layer evidence. These two witnesses supply no character value, colour gloss, word, sound, language, "
            "cipher, plaintext, meaning, or translation."
        ),
    }
    report = (
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
