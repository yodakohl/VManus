#!/usr/bin/env python3
"""Build the compact result for the remaining public-MSI plant folios."""

from __future__ import annotations

import argparse
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
BOOLS = (
    "legibility_gain",
    "new_distinct_text_layer",
    "readable_owned_caption",
    "explicit_equivalence",
    "recoverable_correction_pair",
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode()


def load_rows() -> list[dict[str, str]]:
    with OBS.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    if [row["folio"] for row in rows] != ["f26r", "f93r"]:
        raise SystemExit("unexpected folio order")
    for row in rows:
        if any(row[field] not in {"YES", "NO"} for field in BOOLS):
            raise SystemExit("invalid boolean")
        if row["decision"] != "NO_ANCHOR":
            raise SystemExit("unexpected decision")
        ids = row["processed_file_ids"].split("|")
        hashes = row["processed_sha256s"].split("|")
        if len(ids) != len(hashes) or any(len(value) != 64 for value in hashes):
            raise SystemExit("processed binding mismatch")
        cids = [] if row["comparator_file_ids"] == "NONE" else row["comparator_file_ids"].split("|")
        chashes = [] if row["comparator_sha256s"] == "NONE" else row["comparator_sha256s"].split("|")
        if len(cids) != len(chashes) or any(len(value) != 64 for value in chashes):
            raise SystemExit("comparator binding mismatch")
        if row["new_distinct_text_layer"] == "YES" and any(row[field] == "YES" for field in BOOLS[2:]):
            raise SystemExit("unexpected anchor")
    return rows


def build() -> tuple[dict[str, object], str]:
    rows = load_rows()
    counts = {
        "folios_inspected": 2,
        "processed_jpegs": sum(len(row["processed_file_ids"].split("|")) for row in rows),
        "comparators": sum(row["comparator_file_ids"] != "NONE" for row in rows),
        "legibility_gains": sum(row["legibility_gain"] == "YES" for row in rows),
        "new_distinct_text_layers": sum(row["new_distinct_text_layer"] == "YES" for row in rows),
        "readable_owned_captions": sum(row["readable_owned_caption"] == "YES" for row in rows),
        "explicit_equivalences": sum(row["explicit_equivalence"] == "YES" for row in rows),
        "recoverable_correction_pairs": sum(row["recoverable_correction_pair"] == "YES" for row in rows),
        "translation_anchors": 0,
    }
    result: dict[str, object] = {
        "experiment": "MSI_REMAINING_PLANT_FOLIOS_WORTH_SCREEN",
        "schema": "MSI_REMAINING_PLANT_FOLIOS_WORTH_SCREEN_V1",
        "status": "STOP_NO_ANCHOR_IN_REMAINING_PUBLIC_MSI_PLANT_FOLIOS",
        "decision": "STOP_BOUNDED_TWO_FOLIO_SCREEN_NO_ANCHOR",
        "counts": counts,
        "folios": [
            {
                "folio": row["folio"],
                "dominant_interpretation": row["dominant_interpretation"],
                "observation": row["observation"],
                "decision": row["decision"],
            }
            for row in rows
        ],
        "inputs": {
            str(METHOD.relative_to(ROOT)): sha(METHOD),
            str(OBS.relative_to(ROOT)): sha(OBS),
        },
        "claim_ceiling": (
            "The processed f26r and f93r witnesses improve separation of existing ink, paint, stains, and reverse-side "
            "visibility but expose no new translation relation. They supply no glyph, word, plant name, language, cipher, "
            "plaintext, meaning, or translation."
        ),
    }
    report = (
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
