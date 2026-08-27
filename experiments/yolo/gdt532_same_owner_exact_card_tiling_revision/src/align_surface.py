#!/usr/bin/env python3
"""Compile one surface through GDT532's same-owner exact-card revision."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
G531_ALIGN = (
    ROOT
    / "experiments/yolo/gdt531_atomic_renderer_block_superform_peel/src"
    / "align_surface.py"
)
WORKING_REVISIONS = {"dsholdaiir": "D_ADDR+SH+OL+DA+IIN+R"}
CERTIFICATES = {
    "dsholdaiir": {
        "surface_tiling": "d|shol|daiir",
        "recipe_tiling": "D_ADDR | SH+OL | DA+IIN+R",
        "tile_old_event_counts": {"d": 11, "shol": 18, "daiir": 2},
        "cross_role_tile": "daiir=DA+IIN+R",
        "current_cross_role_events": "G515-E0211|G515-E0408",
        "same_owner_block_carrier": "G515-E0408@f66r.62/F66R_PROSE_02",
        "candidate_rank": 6,
    }
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--surface", required=True)
    parser.add_argument("--left-recipe", default="NONE")
    parser.add_argument("--right-recipe", default="NONE")
    parser.add_argument("--event-id", default="NONE")
    parser.add_argument("--page", default="AUTO")
    parser.add_argument(
        "--domain", choices=("AUTO", "PROSE_STREAM", "LOCAL_RECORD"), default="AUTO"
    )
    parser.add_argument("--top", type=int, default=6)
    args = parser.parse_args()
    args.surface = args.surface.lower()
    completed = subprocess.run(
        [
            sys.executable,
            str(G531_ALIGN),
            "--surface",
            args.surface,
            "--left-recipe",
            args.left_recipe,
            "--right-recipe",
            args.right_recipe,
            "--event-id",
            args.event_id,
            "--page",
            args.page,
            "--domain",
            args.domain,
            "--top",
            str(max(6, args.top)),
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    inherited = json.loads(completed.stdout)
    revision = WORKING_REVISIONS.get(args.surface)
    inherited.update(
        {
            "selected_working_layer": "GDT532_SAME_OWNER_EXACT_CARD_TILING_REVISION",
            "gdt531_default_selection": inherited["default_selection"],
            "gdt531_working_revision": inherited.get("working_revision", "NONE"),
            "working_revision": revision or inherited.get("working_revision", "NONE"),
            "exact_card_tiling_certificate": CERTIFICATES.get(args.surface, "NONE"),
            "selection_precedence": "GDT532_EXACT_CARD_COMPOSITION_OVERRIDE>GDT531_WORKING_PRECEDENCE",
            "default_selection": revision or inherited["default_selection"],
            "working_literal_de": (
                "[D_ADDR:STEUERUNG=HIER] · HALTEN · FORTSETZEN · "
                "[DA+IIN:STEUERUNG=STUFE II] · MARKIEREN"
                if revision
                else inherited.get("working_literal_de", "INHERITED")
            ),
            "working_phrase_de": (
                "Hier halten und fortsetzen; Stufe II markieren."
                if revision
                else inherited.get("working_phrase_de", "INHERITED")
            ),
            "guard": "UNIQUE_EXACT_CARD_RECIPE_PLUS_CROSS_ROLE_SAME_OWNER_CARRIER__NO_FREE_TILING__NO_CONFIRMED_PLAINTEXT",
        }
    )
    print(json.dumps(inherited, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
