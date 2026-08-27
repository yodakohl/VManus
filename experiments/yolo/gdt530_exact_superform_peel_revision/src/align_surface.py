#!/usr/bin/env python3
"""Compile one surface through GDT530's exact-superform working revision."""

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
G529_ALIGN = (
    ROOT / "experiments/yolo/gdt529_nearest_terminal_m_square/src/align_surface.py"
)
WORKING_REVISIONS = {"chekchy": "CH+K+Y"}
CERTIFICATES = {
    "chekchy": {
        "old_superform": "ychekchy",
        "old_superform_recipe": "Y+CH+K+Y",
        "peel": "initial y/Y@LEFT/LEFT",
        "old_signature_support": "54/59",
        "old_signature_probability": 0.886178862,
        "old_signature_reliability": 0.964285714,
        "independent_exact_old_recipe": "ckhy=CH+K+Y (2 events)",
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
        "--domain",
        choices=("AUTO", "PROSE_STREAM", "LOCAL_RECORD"),
        default="AUTO",
    )
    parser.add_argument("--top", type=int, default=5)
    args = parser.parse_args()
    args.surface = args.surface.lower()
    command = [
        sys.executable,
        str(G529_ALIGN),
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
    ]
    completed = subprocess.run(
        command, cwd=ROOT, check=True, capture_output=True, text=True
    )
    inherited = json.loads(completed.stdout)
    revision = WORKING_REVISIONS.get(args.surface)
    inherited.update(
        {
            "selected_working_layer": "GDT530_EXACT_SUPERFORM_PEEL_REVISION",
            "gdt529_default_selection": inherited["default_selection"],
            "working_revision": revision or "NONE",
            "superform_certificate": CERTIFICATES.get(args.surface, "NONE"),
            "selection_precedence": "GDT530_WORKING_REVISION>GDT529_INTAKE_PRECEDENCE",
            "default_selection": revision or inherited["default_selection"],
            "working_literal_de": (
                "NEHMEN · GEBEN · POSTEN" if revision else "INHERITED"
            ),
            "working_phrase_de": (
                "Nehmen, geben und posten." if revision else "INHERITED"
            ),
            "guard": "EXACT_OLD_SUPERFORM_PEEL_WITH_MATCHING_EDIT_SIGNATURE__CHY_REMAINS_CONTEXT_DEPENDENT__NO_CONFIRMED_PLAINTEXT",
        }
    )
    print(json.dumps(inherited, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
