#!/usr/bin/env python3
"""Compile one surface through GDT533's nested odas-tail revision."""

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
G532_ALIGN = (
    ROOT
    / "experiments/yolo/gdt532_same_owner_exact_card_tiling_revision/src"
    / "align_surface.py"
)
WORKING_REVISIONS = {"dairykodas": "D_ADDR+AIR+Y+K+O+DA+S"}
CERTIFICATES = {
    "dairykodas": {
        "surface_tiling": "dair|y|k|odas",
        "recipe_tiling": "D_ADDR+AIR | Y | K | O+DA+S",
        "tile_old_event_counts": {"dair": 9, "y": 39, "k": 4, "odas": 1},
        "nested_tail": "das=DA+S -> odas=O+DA+S",
        "left_o_O_signature": "31/37",
        "left_o_O_probability": 0.797468354,
        "left_o_O_reliability": 0.939393939,
        "candidate_rank": 1,
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
            str(G532_ALIGN),
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
            "selected_working_layer": "GDT533_NESTED_ODAS_TAIL_REVISION",
            "gdt532_default_selection": inherited["default_selection"],
            "gdt532_working_revision": inherited.get("working_revision", "NONE"),
            "working_revision": revision or inherited.get("working_revision", "NONE"),
            "nested_odas_certificate": CERTIFICATES.get(args.surface, "NONE"),
            "selection_precedence": "GDT533_NESTED_TERMINAL_WHOLE_CARD>GDT532_WORKING_PRECEDENCE",
            "default_selection": revision or inherited["default_selection"],
            "working_literal_de": (
                "[D_ADDR:STEUERUNG=HIER] · BAHN · POSTEN · GEBEN · "
                "[O:STEUERUNG=AUSFÜHRUNG] · [DA+S:STEUERUNG=STUFE II WÄHLEN]"
                if revision
                else inherited.get("working_literal_de", "INHERITED")
            ),
            "working_phrase_de": (
                "Hier entlang der Bahn posten; zur Ausführung geben und Stufe II wählen."
                if revision
                else inherited.get("working_phrase_de", "INHERITED")
            ),
            "guard": "EXACT_TERMINAL_ODAS_PLUS_NESTED_DAS_SUPERFORM__NO_GLOBAL_ODAS_OR_AS_SUFFIX__NO_CONFIRMED_PLAINTEXT",
        }
    )
    print(json.dumps(inherited, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
