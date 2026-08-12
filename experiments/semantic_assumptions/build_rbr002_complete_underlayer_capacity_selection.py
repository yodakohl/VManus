#!/usr/bin/env python3
"""Freeze all twelve f67r2.T1 records for an exposure-aware capacity audit."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

BASE = Path(__file__).resolve().parent
METHOD = BASE / "RBR002_F67R2_COMPLETE_UNDERLAYER_CAPACITY_METHOD.md"
HUMAN = BASE.parent.parent / "transcription/sources/Stolfi_text25e1-52.evt"
OUT = BASE / "results/rbr002_complete_underlayer_capacity_selection.json"
REPORT = BASE / "results/rbr002_complete_underlayer_capacity_selection_report.md"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    if OUT.exists() or REPORT.exists():
        raise SystemExit("refusing overwrite")
    text = HUMAN.read_text(encoding="utf-8", errors="replace")
    unit = text.split("# Unit <f67r2.T1>", 1)[1].split("# Unit <f67r2.Q1>", 1)[0]
    positions: list[tuple[str, str]] = []
    clock = None
    for line in unit.splitlines():
        match = re.fullmatch(r"# At (\d\d:\d\d)\.", line)
        if match:
            clock = match.group(1)
        match = re.match(r"<(f67r2\.\d+);U>", line)
        if match:
            if clock is None:
                raise SystemExit("missing clock")
            positions.append((match.group(1), clock))
            clock = None
    expected = [("f67r2.12", "08:30")] + [(f"f67r2.{i}", f"{(i+8)%12:02d}:30") for i in range(1, 12)]
    if positions != expected:
        raise SystemExit(f"inventory mismatch: {positions}")
    exposed = {"f67r2.3", "f67r2.7", "f67r2.10"}
    result = {
        "experiment": "RBR002_COMPLETE_UNDERLAYER_CAPACITY_SELECTION",
        "status": "FROZEN_TWELVE_RECORD_CENSUS_NINE_NEW_REGIONS_UNOPENED",
        "decision": "AUTHORIZE_COMPLETE_EXPOSURE_AWARE_NATIVE_VISUAL_CAPACITY_AUDIT",
        "inputs": {"method_sha256": sha(METHOD), "human_source_sha256": sha(HUMAN)},
        "records": [
            {"ring_ordinal": i + 1, "locus": locus, "clock_position": clock,
             "previously_exposed_for_underlayer_question": locus in exposed}
            for i, (locus, clock) in enumerate(positions)
        ],
        "source": {
            "canvas_id": "1006194",
            "official_full_image_sha256": "0518312a566ee713a46c9887d8b8b9d7141d14095e360661789c1dad9b5c0d1c",
            "official_full_image_dimensions": [4972, 3738],
        },
        "capacity_gates": {
            "minimum_records_with_recovery": 8,
            "minimum_previously_unexamined_records_with_recovery": 4,
            "minimum_records_with_multiple_recoverable_positions": 3,
        },
        "access": {
            "official_full_canvas_previously_opened": True,
            "three_rbr001_regions_previously_opened": True,
            "nine_other_sector_regions_opened_before_freeze": False,
            "character_identities_or_corrected_text_scored": False,
            "ocr_clip_embedding_or_automated_recognition_used": False,
        },
        "claim_ceiling": (
            "This freeze authorizes a complete source-only recovery-capacity census. It does not authorize "
            "character naming, corrected transcription, correction intent, sound, word, language, cipher, "
            "plaintext, meaning, or translation."
        ),
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT.write_text(
        "# RBR002 complete underlayer capacity selection\n\n"
        "Status: **FROZEN_TWELVE_RECORD_CENSUS_NINE_NEW_REGIONS_UNOPENED**\n\n"
        "All twelve f67r2.T1 records are fixed in clock order. Three RBR001 sectors are disclosed as exposed; "
        "nine other sector regions remain unopened for this question. Thresholds are frozen before those nine "
        "regions are inspected. No character identities or corrected text may be produced.\n\n"
        f"Claim ceiling: {result['claim_ceiling']}\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
