#!/usr/bin/env python3
"""Freeze the three recoverable-state f67r2 red/brown comments."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from pathlib import Path

BASE = Path(__file__).resolve().parent
METHOD = BASE / "RBR001_F67R2_RED_BROWN_RETRACING_METHOD.md"
HUMAN = BASE.parent.parent / "transcription/sources/Stolfi_text25e1-52.evt"
SOURCE = BASE / "results/source_sta_group_alignment.tsv"
OUT = BASE / "results/rbr001_f67r2_red_brown_selection.json"
REPORT = BASE / "results/rbr001_f67r2_red_brown_selection_report.md"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def target_blocks() -> dict[str, str]:
    text = HUMAN.read_text(encoding="utf-8", errors="replace")
    page = text.split("@@ f67r2", 1)[1].split("@@ f67v1", 1)[0]
    unit = page.split("# Unit <f67r2.T1>", 1)[1].split("# Unit <f67r2.Q1>", 1)[0]
    pending: list[str] = []
    blocks: dict[str, str] = {}
    for line in unit.splitlines():
        if line.startswith("#"):
            pending.append(line[1:].strip())
            continue
        match = re.match(r"<(f67r2\.\d+);U>", line)
        if match:
            blocks[match.group(1)] = " ".join(pending)
            pending = []
        elif line.strip():
            pending = []
    return blocks


def main() -> None:
    if OUT.exists() or REPORT.exists():
        raise SystemExit("refusing overwrite")
    blocks = target_blocks()
    selected = {
        locus: comment for locus, comment in blocks.items()
        if (("red retracing" in comment and ("became" in comment or "made the left side" in comment))
            or ("looks like @a in red" in comment and "visible in brown" in comment))
    }
    if list(selected) != ["f67r2.3", "f67r2.7", "f67r2.10"]:
        raise SystemExit(f"selection mismatch: {list(selected)}")
    readings: dict[str, dict[str, list[str]]] = {locus: {} for locus in selected}
    with SOURCE.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            if row["locus"] in readings:
                readings[row["locus"]].setdefault(row["edition"], []).append(row["nearest_basic_eva_primary"])
    if any(set(per_locus) != {"ZL3b", "IT2a", "RF1b"} for per_locus in readings.values()):
        raise SystemExit("reading coverage mismatch")
    result = {
        "experiment": "RBR001_F67R2_RED_BROWN_SELECTION",
        "status": "FROZEN_THREE_RECOVERABLE_STATE_COMMENTS_TARGET_REGIONS_UNOPENED",
        "decision": "AUTHORIZE_THREE_NATIVE_VISUAL_SOURCE_INSPECTIONS",
        "inputs": {
            "method_sha256": sha(METHOD),
            "human_source_sha256": sha(HUMAN),
            "source_sta_group_alignment_sha256": sha(SOURCE),
        },
        "selection_rule": {
            "scope": "f67r2.T1 immediate preceding comment blocks",
            "rule_1": "red retracing AND (became OR made the left side)",
            "rule_2": "looks like @a in red AND visible in brown",
        },
        "selected": [
            {"locus": locus, "human_comment": selected[locus], "alternate_reading_witnesses": readings[locus]}
            for locus in selected
        ],
        "excluded_nonrecoverable_comments": [
            {"locus": "f67r2.6", "reason": "unrecognizable with inferred must-have-been state"},
            {"locus": "f67r2.11", "reason": "unreadable with no directly visible before-state"},
        ],
        "source": {
            "canvas_id": "1006194",
            "official_full_image_sha256": "0518312a566ee713a46c9887d8b8b9d7141d14095e360661789c1dad9b5c0d1c",
            "official_full_image_dimensions": [4972, 3738],
        },
        "prior_overlap": {
            "page_viewed_for_structure_and_lunar_alignment": True,
            "target_regions_previously_inspected_for_red_brown_shape_state": False,
            "formal_or_semantic_target_scored": False,
        },
        "allowed_locus_outcomes": [
            "RECOVERABLE_RED_OVER_BROWN_SHAPE_CHANGE",
            "VISIBLE_LAYERING_NO_RECOVERABLE_SHAPE_PAIR",
            "UNRESOLVED_SOURCE_IMAGE",
        ],
        "panel_pass_minimum_positive_loci": 2,
        "access": {
            "target_regions_opened_before_freeze": False,
            "formal_associations_scored": False,
            "ocr_clip_embedding_or_automated_recognition_used": False,
        },
        "claim_ceiling": (
            "Selection authorizes three source-bound physical-state inspections. A pass can establish multiple "
            "recoverable brown-under/red-retraced shapes, but no correction intent, correct transcription, "
            "character identity or equivalence, sound, word, language, cipher, plaintext, meaning, or translation."
        ),
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT.write_text(
        "# RBR001 f67r2 red/brown selection\n\n"
        "Status: **FROZEN_THREE_RECOVERABLE_STATE_COMMENTS_TARGET_REGIONS_UNOPENED**\n\n"
        "Literal rules select f67r2.3, f67r2.7, and f67r2.10 from the outer red ring. f67r2.6 and .11 are "
        "excluded because their comments say only unrecognizable or unreadable and do not expose a directly "
        "visible before-state. Alternate readings are localization witnesses, not replications.\n\n"
        f"Claim ceiling: {result['claim_ceiling']}\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
