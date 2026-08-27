#!/usr/bin/env python3
"""Compile one surface through GDT528's certified terminal-d null variant."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys

import run as core


G527_ALIGN = (
    core.ROOT
    / "experiments/yolo/gdt527_right_edge_learned_stem_extension/src/align_surface.py"
)


def inherited_result(args: argparse.Namespace) -> dict:
    command = [
        sys.executable, str(G527_ALIGN),
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
        features, trace, hit = core.null_features(args.surface, recipe, analogy)
        feature = features["TAIL_DNULL_LOG"]
        scored.append(
            {
                **row,
                "d_null_feature": feature,
                "d_null_trace": trace,
                "d_null_base": hit["base_surface"] if hit else "NONE",
                "d_null_certificate": (
                    f"{hit['certificate_bases']}->{hit['certificate_variants']}"
                    if hit else "NONE"
                ),
                "d_null_action_change": (
                    hit["certificate_action_changes"] if hit else "NONE"
                ),
                "gdt528_score": float(row["gdt527_score"]) - 1.15 * feature,
            }
        )
    scored.sort(
        key=lambda row: (float(row["gdt528_score"]), int(row["compiler_rank"]))
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
        "selected_feature": "TAIL_DNULL_LOG",
        "selected_weight": 1.15,
        "visible_frame": "BASE_ENDING_Y_TO_VARIANT_ENDING_DY",
        "recipe_relation": "EXACT_EQUAL_RECIPE",
        "neighbor_certificate": "ONE_VISIBLE_SUBSTITUTION_PLUS_ONE_KNOWN_ACTION_ROOT_SUBSTITUTION_AFTER_CARRIER_Q_NORMALIZATION",
        "exact_event_match_count": exact_count,
        "known_surface_option_count": known_count,
        "working_revision": revision or "NONE",
        "reranked_candidates": scored[: max(1, args.top)],
        "selection_precedence": "WORKING_REVISION>EXACT_EVENT>KNOWN_SURFACE_ROLE_OPTION>GDT528_CERTIFIED_D_NULL_TOP1",
        "default_selection": default,
        "guard": "BOUNDED_TERMINAL_D_NULL_VARIANT__NO_GLOBAL_D_OR_Q_NULL__NO_CONFIRMED_LEXEME_OR_PLAINTEXT",
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
