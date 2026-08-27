#!/usr/bin/env python3
"""Compile one surface through GDT531's atomic renderer-block peel."""

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
G530_ALIGN = (
    ROOT / "experiments/yolo/gdt530_exact_superform_peel_revision/src/align_surface.py"
)
WORKING_REVISIONS = {"saiis": "S+A_ADDR+IIN+S"}
CERTIFICATES = {
    "saiis": {
        "old_superform": "saiisol",
        "old_superform_recipe": "S+A_ADDR+IIN+S+OL",
        "peel": "terminal ol/OL@RIGHT/RIGHT",
        "old_signature_support": "29/33",
        "old_signature_probability": 0.830985915,
        "old_signature_reliability": 0.935483871,
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
    parser.add_argument("--top", type=int, default=5)
    args = parser.parse_args()
    args.surface = args.surface.lower()
    completed = subprocess.run(
        [
            sys.executable,
            str(G530_ALIGN),
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
            str(max(1, args.top)),
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
            "selected_working_layer": "GDT531_ATOMIC_RENDERER_BLOCK_SUPERFORM_PEEL",
            "gdt530_default_selection": inherited["default_selection"],
            "gdt530_working_revision": inherited.get("working_revision", "NONE"),
            "working_revision": revision or inherited.get("working_revision", "NONE"),
            "block_superform_certificate": CERTIFICATES.get(args.surface, "NONE"),
            "selection_precedence": "GDT531_BLOCK_PEEL_REVISION>GDT530_WORKING_PRECEDENCE",
            "default_selection": revision or inherited["default_selection"],
            "working_literal_de": (
                "WÄHLEN · HIER · STUFE · WÄHLEN"
                if revision
                else inherited.get("working_literal_de", "INHERITED")
            ),
            "working_phrase_de": (
                "Wählen; hier die Stufe wählen."
                if revision
                else inherited.get("working_phrase_de", "INHERITED")
            ),
            "guard": "EXACT_OLD_SUPERFORM_ATOMIC_BLOCK_PEEL_WITH_MATCHING_POSITION_SIGNATURE__NO_GLOBAL_OL_SUFFIX__NO_CONFIRMED_PLAINTEXT",
        }
    )
    print(json.dumps(inherited, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
