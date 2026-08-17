#!/usr/bin/env python3
"""Freeze the external W.73 comparator for GDT179 before target synthesis."""

from __future__ import annotations

import csv
import hashlib
import json
from datetime import date
from pathlib import Path
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parent
URL = "https://t.thedigitalwalters.org/Data/WaltersManuscripts/html/W73/description.html"
MANIFEST = ROOT / "gdt179_w73_comparator_manifest.tsv"
PROVENANCE = ROOT / "gdt179_source_provenance.json"
FREEZE = ROOT / "gdt179_source_freeze.json"


ROWS = [
    {
        "slot_order": 1,
        "page_position": "TOP",
        "element": "FIRE",
        "quality_1": "HOT",
        "quality_2": "DRY",
        "season": "SUMMER",
        "humour": "RED_OR_YELLOW_BILE",
        "source_folio": "W.73 f.7v",
        "source_status": "OFFICIAL_MANUSCRIPT_DESCRIPTION",
    },
    {
        "slot_order": 2,
        "page_position": "RIGHT",
        "element": "AIR",
        "quality_1": "HOT",
        "quality_2": "MOIST",
        "season": "SPRING",
        "humour": "BLOOD",
        "source_folio": "W.73 f.7v",
        "source_status": "OFFICIAL_MANUSCRIPT_DESCRIPTION",
    },
    {
        "slot_order": 3,
        "page_position": "BOTTOM",
        "element": "WATER",
        "quality_1": "MOIST",
        "quality_2": "COLD",
        "season": "WINTER",
        "humour": "PHLEGM",
        "source_folio": "W.73 f.7v",
        "source_status": "OFFICIAL_MANUSCRIPT_DESCRIPTION",
    },
    {
        "slot_order": 4,
        "page_position": "LEFT",
        "element": "EARTH",
        "quality_1": "COLD",
        "quality_2": "DRY",
        "season": "AUTUMN",
        "humour": "BLACK_BILE_MELANCHOLY",
        "source_folio": "W.73 f.7v",
        "source_status": "OFFICIAL_MANUSCRIPT_DESCRIPTION",
    },
]


REQUIRED_SOURCE_PHRASES = [
    "Ignis. Siccus. Calidus",
    "Aer. Calidus. Humidis",
    "Aqua. Humida. Frigida",
    "Terra. Frigida. Sicca",
    "Mundus. Homo. Annus",
]


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_json(obj: object) -> bytes:
    return (json.dumps(obj, sort_keys=True, indent=2, ensure_ascii=False) + "\n").encode()


def main() -> None:
    response = urlopen(Request(URL, headers={"User-Agent": "VManus-research/1.0"}), timeout=30)
    source_bytes = response.read()
    source_text = source_bytes.decode("utf-8", "replace")
    absent = [phrase for phrase in REQUIRED_SOURCE_PHRASES if phrase not in source_text]
    if absent:
        raise SystemExit(f"official source no longer contains required phrases: {absent}")

    fields = list(ROWS[0]) + ["source_url"]
    with MANIFEST.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for row in ROWS:
            writer.writerow({**row, "source_url": URL})

    provenance = {
        "experiment": "GDT179_F57_PAGE_TRANSLATION_SCAFFOLD",
        "freeze_stage": "EXTERNAL_COMPARATOR_BEFORE_TARGET_SYNTHESIS",
        "retrieved_utc_date": date.today().isoformat(),
        "institution": "The Walters Art Museum / Digital Walters",
        "manuscript": "Walters MS W.73, Cosmography",
        "manuscript_date_place": "England, late twelfth century",
        "source_url": URL,
        "source_sha256": sha256_bytes(source_bytes),
        "source_byte_count": len(source_bytes),
        "required_phrase_checks": {phrase: True for phrase in REQUIRED_SOURCE_PHRASES},
        "scope": (
            "Comparator fixes a historically attested four-element/four-quality phase. "
            "It is not claimed as the Voynich exemplar and supplies no Voynich lexeme."
        ),
        "target_scored_or_serialized_by_this_script": False,
        "f84r_accessed": False,
    }
    PROVENANCE.write_bytes(canonical_json(provenance))

    freeze = {
        "experiment": provenance["experiment"],
        "status": "SOURCE_COMPARATOR_FROZEN_BEFORE_TARGET_SYNTHESIS",
        "features": ROWS,
        "files": {
            MANIFEST.name: sha256_bytes(MANIFEST.read_bytes()),
            PROVENANCE.name: sha256_bytes(PROVENANCE.read_bytes()),
        },
        "source_url": URL,
        "source_sha256": provenance["source_sha256"],
        "allowed_target_inference": (
            "At most a provisional page-local role scaffold if independently inventoried "
            "f57 geometry realizes the frozen phase."
        ),
        "forbidden_inference": (
            "No Voynich word, sound, language, authorship, direct copying, plaintext, or "
            "manuscript-wide translation follows from the comparator."
        ),
        "f84r_accessed": False,
    }
    FREEZE.write_bytes(canonical_json(freeze))
    print(f"wrote {MANIFEST.name}, {PROVENANCE.name}, {FREEZE.name}")


if __name__ == "__main__":
    main()
