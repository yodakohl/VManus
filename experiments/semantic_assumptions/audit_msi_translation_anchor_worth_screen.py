#!/usr/bin/env python3
"""Build the compact result for the public-MSI native-visual worth screen."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
METHOD = ROOT / "experiments/semantic_assumptions/MSI_TRANSLATION_ANCHOR_WORTH_SCREEN_METHOD.md"
OBS = ROOT / "experiments/semantic_assumptions/msi_translation_anchor_worth_screen_observations.tsv"
RESULT = ROOT / "experiments/semantic_assumptions/results/msi_translation_anchor_worth_screen.json"
REPORT = ROOT / "experiments/semantic_assumptions/results/msi_translation_anchor_worth_screen_report.md"

EXPECTED_FOLIOS = ("f8r", "f17r", "f47r", "f70v1", "f71r", "f102v1", "f116v")
BOOL_FIELDS = (
    "legibility_gain",
    "new_distinct_text_layer",
    "explicit_equivalence",
    "readable_owned_plain_legend",
    "recoverable_correction_pair",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(obj: object) -> bytes:
    return (json.dumps(obj, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode()


def load_rows() -> list[dict[str, str]]:
    with OBS.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    if tuple(row["folio"] for row in rows) != EXPECTED_FOLIOS:
        raise SystemExit("unexpected folio order")
    if len({row["folio"] for row in rows}) != len(rows):
        raise SystemExit("duplicate folio")
    for row in rows:
        for field in BOOL_FIELDS:
            if row[field] not in {"YES", "NO"}:
                raise SystemExit(f"invalid boolean {field}")
        if row["decision"] != "NO_ANCHOR":
            raise SystemExit("unexpected row decision")
        ids = [] if row["processed_file_ids"] == "NONE" else row["processed_file_ids"].split("|")
        hashes = [] if row["processed_sha256s"] == "NONE" else row["processed_sha256s"].split("|")
        if len(ids) != len(hashes) or not ids:
            raise SystemExit("processed source mismatch")
        if any(len(value) != 64 for value in hashes):
            raise SystemExit("invalid processed hash")
        cids = [] if row["comparator_file_ids"] == "NONE" else row["comparator_file_ids"].split("|")
        chashes = [] if row["comparator_sha256s"] == "NONE" else row["comparator_sha256s"].split("|")
        if len(cids) != len(chashes) or any(len(value) != 64 for value in chashes):
            raise SystemExit("comparator source mismatch")
        relation = any(row[field] == "YES" for field in BOOL_FIELDS[2:])
        passes = row["new_distinct_text_layer"] == "YES" and relation
        if passes:
            raise SystemExit("row unexpectedly meets anchor rule")
    return rows


def build() -> tuple[dict[str, object], str]:
    rows = load_rows()
    counts = {
        "folios_inspected": len(rows),
        "processed_jpegs": sum(len(row["processed_file_ids"].split("|")) for row in rows),
        "ordinary_or_psc_comparators": sum(
            0 if row["comparator_file_ids"] == "NONE" else len(row["comparator_file_ids"].split("|"))
            for row in rows
        ),
        "legibility_gains": sum(row["legibility_gain"] == "YES" for row in rows),
        "new_distinct_text_layers": sum(row["new_distinct_text_layer"] == "YES" for row in rows),
        "explicit_equivalences": sum(row["explicit_equivalence"] == "YES" for row in rows),
        "readable_owned_plain_legends": sum(row["readable_owned_plain_legend"] == "YES" for row in rows),
        "recoverable_correction_pairs": sum(row["recoverable_correction_pair"] == "YES" for row in rows),
        "translation_anchors": 0,
    }
    result: dict[str, object] = {
        "experiment": "MSI_TRANSLATION_ANCHOR_WORTH_SCREEN",
        "schema": "MSI_TRANSLATION_ANCHOR_WORTH_SCREEN_V1",
        "status": "STOP_NO_NEW_TRANSLATION_ANCHOR_IN_PUBLIC_MSI_SUBSET",
        "decision": "STOP_BOUNDED_MSI_WORTH_SCREEN_NO_ANCHOR",
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
            str(METHOD.relative_to(ROOT)): sha256(METHOD),
            str(OBS.relative_to(ROOT)): sha256(OBS),
        },
        "source_release": {
            "description_url": "https://manuscriptroadtrip.wordpress.com/2024/09/08/multispectral-imaging-and-the-voynich-manuscript/",
            "drive_folder_id": "1mNQGKQDSCR4M_c2M2JrsU5soghvYwMig",
            "credit": "The Lazarus Project and the Chester F. Carlson Center for Imaging Science at RIT; Beinecke MS 408",
        },
        "claim_ceiling": (
            "The bounded seven-folio public processed-MSI subset improves visibility but exposes no new distinct text layer "
            "with an equivalence, owned readable legend, or recoverable correction pair. It supplies no glyph, sound, word, "
            "language, cipher, plaintext, meaning, or translation."
        ),
    }
    report = (
        "# Public MSI translation-anchor worth screen\n\n"
        "Decision: **STOP — NO NEW TRANSLATION ANCHOR IN THE BOUNDED PUBLIC MSI SUBSET**.\n\n"
        f"Seven high-value folios were inspected from the public 2014 Lazarus Project release, using {counts['processed_jpegs']} "
        f"processed JPEGs and {counts['ordinary_or_psc_comparators']} ordinary-light or PSC comparators. All seven gain "
        "legibility, but none exposes a new distinct text layer, explicit equivalence, owned readable plain legend, or "
        "recoverable before/after correction pair.\n\n"
        "f17r and f116v become clearer but remain the already registered mixed-script marginal contexts without a gloss "
        "device. f70v1 and f71r add contrast to existing zodiac registers; f70v1's extra pale material is consistent with "
        "show-through or offset rather than a hidden legend. f8r, f47r, and f102v1 reveal no separate writing state.\n\n"
        "This is source-bound native AI visual inspection, not human annotation. No OCR, automated transcription, CLIP, "
        "embedding, batch recognition, proposed reading, language fit, or decoder output was used. The stop applies only "
        "to this public processed-image subset and supplies no glyph, sound, word, language, cipher, plaintext, meaning, "
        "or translation.\n"
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
