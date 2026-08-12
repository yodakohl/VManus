#!/usr/bin/env python3
"""Build the source-only F69VSD001 selection before image inspection."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent
METHOD = BASE / "F69VSD001_AUTHOR_VISIBLE_START_DIRECTION_METHOD.md"
PRIOR = BASE / "results/special_circle_plain_legend_native_visual_screen.json"
OUT = BASE / "results/f69vsd001_start_direction_selection.json"
REPORT = BASE / "results/f69vsd001_start_direction_selection_report.md"

METHOD_SHA = "677c1468618781dcc6416015b2f917f8accd62cecc2d53b7dae309c9bd0d892b"
CANVAS_ID = "1006199"
IMAGE_SHA = "99d824d8d5491a2f4511a0c0f719f9f165063335f53540c63d12b3bbe6c73edf"
URL = "https://collections.library.yale.edu/catalog/2002046?child_oid=1006199"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()


def main() -> None:
    if OUT.exists() or REPORT.exists():
        raise SystemExit("refusing overwrite")
    if sha(METHOD) != METHOD_SHA:
        raise SystemExit("method hash mismatch")
    prior = json.loads(PRIOR.read_text())
    if prior["canvas_panels"].get(CANVAS_ID) != ["f69v", "f70r1", "f70r2"]:
        raise SystemExit("canvas mapping mismatch")
    if prior["inputs"].get(f"yale_iiif_2000px_canvas_{CANVAS_ID}_sha256") != IMAGE_SHA:
        raise SystemExit("image hash mismatch")
    result = {
        "experiment": "F69VSD001_AUTHOR_VISIBLE_START_DIRECTION",
        "status": "FROZEN_SOURCE_BOUND_IMAGE_UNOPENED",
        "decision": "AUTHORIZE_ONE_F69V_IMAGE_INSPECTION_ONLY",
        "method_sha256": METHOD_SHA,
        "source": {
            "canvas_id": CANVAS_ID,
            "canvas_panels": ["f69v", "f70r1", "f70r2"],
            "selected_panel": "f69v",
            "official_catalogue_url": URL,
            "frozen_2000px_image_sha256": IMAGE_SHA,
            "prior_source_binding_sha256": sha(PRIOR),
        },
        "allowed_outcomes": [
            "START_AND_DIRECTION", "START_ONLY", "DIRECTION_ONLY", "NONE", "UNCERTAIN"
        ],
        "qualifying_device_count": 5,
        "gates": {
            "single_preselected_canvas": True,
            "official_source_binding_reconstructed": True,
            "rubric_frozen_before_image_reopen": True,
            "image_body_opened_by_builder": False,
            "voynich_text_or_formal_features_opened": False,
        },
        "claim_ceiling": (
            "A positive could fix only a physical start or direction coordinate; it cannot identify any slot "
            "value, roster, word, sound, language, cipher, plaintext, meaning, or translation."
        ),
    }
    OUT.write_bytes(canonical(result))
    REPORT.write_text(
        "# F69VSD001 source-only selection\n\n"
        "Status: **FROZEN_SOURCE_BOUND_IMAGE_UNOPENED**\n\n"
        "The exact official Yale canvas and the f69v panel were selected before reopening the image. "
        "The rubric asks only for an author-visible physical start/direction device; Grove's ordering, "
        "clock position, long/short alternation, and every text identity are excluded.\n\n"
        f"Claim ceiling: {result['claim_ceiling']}\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
