#!/usr/bin/env python3
"""Compile one surface through GDT534's local cheeeky grade ladder."""

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
G533_ALIGN = (
    ROOT
    / "experiments/yolo/gdt533_nested_odas_tail_revision/src/align_surface.py"
)
WORKING_REVISIONS = {"dalcheeeky": "AL+CH+K+EEE+Y"}
CERTIFICATES = {
    "dalcheeeky": {
        "surface_tiling": "dal|cheeeky",
        "recipe_tiling": "AL | CH+K+EEE+Y",
        "exact_prefix": {"surface": "dal", "recipe": "AL", "old_event_count": 44},
        "family_ladder": [
            {"surface": "cheky", "recipe": "CH+K+E+Y", "old_event_count": 9},
            {"surface": "cheeky", "recipe": "CH+K+EE+Y", "old_event_count": 5},
            {
                "surface": "cheeeky",
                "recipe": "CH+K+EEE+Y",
                "status": "PREDICTED_EMBEDDED_THIRD_RUNG",
            },
        ],
        "old_grade_pair_counts": {"E_TO_EE": 49, "EE_TO_EEE": 8},
        "complete_old_three_rung_ladder_count": 5,
        "candidate_rank": "UNGENERATED",
        "candidate_space_status": "OUTSIDE_GDT529_FINITE_SET",
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
            str(G533_ALIGN),
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
            str(max(12, args.top)),
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
            "selected_working_layer": "GDT534_THIRD_RUNG_cheeeky_GRADE_LADDER",
            "gdt533_default_selection": inherited["default_selection"],
            "gdt533_working_revision": inherited.get("working_revision", "NONE"),
            "working_revision": revision or inherited.get("working_revision", "NONE"),
            "grade_ladder_certificate": CERTIFICATES.get(args.surface, "NONE"),
            "selection_precedence": (
                "GDT534_EXACT_LOCAL_K_GRADE_LADDER>GDT533_WORKING_PRECEDENCE"
            ),
            "default_selection": revision or inherited["default_selection"],
            "working_literal_de": (
                "ZIELORT · NEHMEN · GEBEN · [EEE:STEUERUNG=GRAD III] · POSTEN"
                if revision
                else inherited.get("working_literal_de", "INHERITED")
            ),
            "working_phrase_de": (
                "Am Zielort nehmen und geben; auf Grad III posten."
                if revision
                else inherited.get("working_phrase_de", "INHERITED")
            ),
            "guard": (
                "EXACT_cheky_cheeky_K_GRADE_FRAME_PLUS_GENERAL_EE_TO_EEE_"
                "LADDER_AND_EXACT_dal_PREFIX__NO_GLOBAL_cheee_PARSE__"
                "NO_CONFIRMED_PLAINTEXT"
            ),
        }
    )
    print(json.dumps(inherited, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
