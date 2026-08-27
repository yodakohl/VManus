#!/usr/bin/env python3
"""Compile one surface through GDT529's dual-certified terminal-m square."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys

import run as core


G528_ALIGN = (
    core.ROOT
    / "experiments/yolo/gdt528_neighbor_certified_inner_d_null/src/align_surface.py"
)


def inherited_result(args: argparse.Namespace) -> dict:
    command = [
        sys.executable, str(G528_ALIGN),
        "--surface", args.surface,
        "--left-recipe", args.left_recipe,
        "--right-recipe", args.right_recipe,
        "--event-id", args.event_id,
        "--page", args.page,
        "--domain", args.domain,
        "--top", "10000",
    ]
    completed = subprocess.run(
        command, cwd=core.ROOT, check=True, capture_output=True, text=True
    )
    return json.loads(completed.stdout)


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

    inherited = inherited_result(args)
    old = core.read_tsv(core.G518.G407_RUNNING)
    forms = core.G518.invariant_surface_recipes(old, "component_recipe")
    analogy = core.G522.train_analogy_model(forms)
    scored = []
    for row in inherited["reranked_candidates"]:
        recipe = core.G517.atoms(row["recipe"])
        features, trace, hit = core.square_features(args.surface, recipe, analogy)
        feature = features["DUAL_SQUARE_BINARY"]
        scored.append(
            {
                **row,
                "m_square_feature": feature,
                "m_square_trace": trace,
                "m_square_base": hit["base_surface"] if hit else "NONE",
                "m_square_family": (
                    hit["family"]["stem_surface"] if hit else "NONE"
                ),
                "m_square_certificate": (
                    f"{hit['certificate_bases']}->{hit['certificate_variants']}"
                    if hit else "NONE"
                ),
                "m_square_terminal_atom": (
                    hit["predicted_terminal_atom"] if hit else "NONE"
                ),
                "gdt529_score": float(row["gdt528_score"]) - 1.25 * feature,
            }
        )
    scored.sort(
        key=lambda row: (float(row["gdt529_score"]), int(row["compiler_rank"]))
    )

    exact_count = int(inherited["exact_event_match_count"])
    known_count = int(inherited["known_surface_option_count"])
    revision = core.WORKING_REVISIONS.get(args.surface)
    if revision is not None:
        default = revision
    elif exact_count or known_count:
        default = inherited["default_selection"]
    elif scored:
        default = scored[0]["recipe"]
    else:
        default = "UNPARSED"
    result = {
        "surface": args.surface,
        "context": inherited["context"],
        "selected_stage": core.SELECTED_STAGE,
        "selected_feature": "DUAL_SQUARE_BINARY",
        "selected_weight": 1.25,
        "family_certificate": "TWO_ACTION_STEM_WITH_EXACT_O_OL_OR_RIGHT_SLOT_TRIAD",
        "edit_certificate": "UNANIMOUS_NEAREST_EXACT_TERMINAL_M_PAIR_AT_DISTANCE_ONE",
        "exact_event_match_count": exact_count,
        "known_surface_option_count": known_count,
        "working_revision": revision or "NONE",
        "reranked_candidates": scored[: max(1, args.top)],
        "selection_precedence": "WORKING_REVISION>EXACT_EVENT>KNOWN_SURFACE_ROLE_OPTION>GDT529_DUAL_M_SQUARE_TOP1",
        "default_selection": default,
        "guard": "TWO_ACTION_O_OL_OR_TRIAD_AND_ONE_EDIT_M_PAIR_REQUIRED__NO_GLOBAL_M_LOCAL_DEFAULT__NO_CONFIRMED_LEXEME_OR_PLAINTEXT",
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
