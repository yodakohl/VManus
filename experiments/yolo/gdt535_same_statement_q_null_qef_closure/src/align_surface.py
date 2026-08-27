#!/usr/bin/env python3
"""Compile one surface through GDT535's same-statement q-role closure."""

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
G534_ALIGN = (
    ROOT
    / "experiments/yolo/gdt534_third_rung_cheeeky_grade_ladder/src/align_surface.py"
)
WORKING_REVISIONS = {"qef": "E+LOCAL_CHAR_F"}
CERTIFICATES = {
    "qef": {
        "event_id": "G515-E0165",
        "statement_id": "G515-S010",
        "path_trace": "qe=>e~E",
        "old_global_q_null_signature": "75/84",
        "old_E_edge_q_null_context": "1/1",
        "other_q_event_count": 6,
        "other_q_role_vote": "NONCARRIER_Q",
        "other_q_surfaces": [
            "qokees",
            "qokeey",
            "qokeey",
            "qotar",
            "qokey",
            "qokeor",
        ],
        "global_candidate_rank": 2,
        "same_statement_context_rank": 1,
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
            str(G534_ALIGN),
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
            "selected_working_layer": "GDT535_SAME_STATEMENT_Q_NULL_CLOSURE",
            "gdt534_default_selection": inherited["default_selection"],
            "gdt534_working_revision": inherited.get("working_revision", "NONE"),
            "working_revision": revision or inherited.get("working_revision", "NONE"),
            "same_statement_q_certificate": CERTIFICATES.get(args.surface, "NONE"),
            "selection_precedence": (
                "GDT535_UNANIMOUS_SAME_STATEMENT_Q_ROLE>GDT534_WORKING_PRECEDENCE"
            ),
            "default_selection": revision or inherited["default_selection"],
            "working_literal_de": (
                "[E:STEUERUNG=GRAD I] · [LOCAL_CHAR_F:STEUERUNG=HIER]"
                if revision
                else inherited.get("working_literal_de", "INHERITED")
            ),
            "working_phrase_de": (
                "Hier auf Grad I."
                if revision
                else inherited.get("working_phrase_de", "INHERITED")
            ),
            "guard": (
                "EXACT_G515-S010_OTHER_Q_UNANIMITY_PLUS_OLD_q_NULL_AND_E_EDGE_"
                "CONTEXT__NO_GLOBAL_q_NULL__NO_CONFIRMED_PLAINTEXT"
            ),
        }
    )
    print(json.dumps(inherited, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
