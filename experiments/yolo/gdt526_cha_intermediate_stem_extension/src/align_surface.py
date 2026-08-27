#!/usr/bin/env python3
"""Compile one surface through GDT526's licensed ``cha`` stem extension."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

import run as core


G525_ALIGN = (
    core.ROOT
    / "experiments/yolo/gdt525_two_hop_intermediate_stem_analogy/src/align_surface.py"
)


def gdt525_result(args: argparse.Namespace) -> dict[str, object]:
    command = [
        sys.executable,
        str(G525_ALIGN),
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
        "10000",
    ]
    completed = subprocess.run(
        command,
        cwd=core.ROOT,
        check=True,
        capture_output=True,
        text=True,
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

    inherited = gdt525_result(args)
    old = core.read_tsv(core.G518.G407_RUNNING)
    old_forms = core.G518.invariant_surface_recipes(old, "component_recipe")
    analogy = core.G522.train_analogy_model(old_forms)
    missing_cost = core.G524.selected_upstream_parameters()[0]
    selected_weight = next(
        weight for stage, _, weight in core.CONFIGS if stage == core.SELECTED_STAGE
    )

    scored = []
    for row in inherited["reranked_candidates"]:
        recipe = core.G517.atoms(row["recipe"])
        features, trace, hit = core.cha_stem_features(
            args.surface, recipe, analogy, missing_cost
        )
        feature = features["BONUS_PLUS_ONE"]
        scored.append(
            {
                **row,
                "cha_feature": feature,
                "cha_trace": trace,
                "cha_suffix": hit["suffix"] if hit else "NONE",
                "cha_atom_insert": hit["atom_insert"] if hit else "NONE",
                "gdt526_score": float(row["gdt525_score"])
                - selected_weight * feature,
            }
        )
    scored.sort(
        key=lambda row: (float(row["gdt526_score"]), int(row["compiler_rank"]))
    )

    exact_count = int(inherited["exact_event_match_count"])
    known_count = int(inherited["known_surface_option_count"])
    revision = core.WORKING_REVISIONS.get(args.surface)
    if revision is not None:
        default = core.recipe_text(revision)
    elif exact_count or known_count:
        default = inherited["default_selection"]
    elif scored:
        default = scored[0]["recipe"]
    else:
        default = "UNPARSED"

    output = {
        "surface": args.surface,
        "context": inherited["context"],
        "selected_cha_stage": core.SELECTED_STAGE,
        "selected_cha_feature": "BONUS_PLUS_ONE",
        "selected_cha_weight": selected_weight,
        "cha_base": "cha=CH+A_ADDR",
        "activation": "UNSEEN_RIGHT_SUFFIX_WITH_POSITIVE_RIGHT_VISIBLE_TO_ATOM_LICENSE",
        "conflict": "OLD_EXACT_CHA_EXTENSION_OVERRIDES_STEM_DEFAULT",
        "exact_event_match_count": exact_count,
        "known_surface_option_count": known_count,
        "working_revision": core.recipe_text(revision) if revision else "NONE",
        "reranked_candidates": scored[: max(1, args.top)],
        "selection_precedence": "WORKING_REVISION>EXACT_EVENT>KNOWN_SURFACE_ROLE_OPTION>GDT526_CHA_STEM_TOP1",
        "default_selection": default,
        "guard": "PRODUCTIVE_CHA_STEM_RULE__NO_CONFIRMED_LEXEME_OR_PLAINTEXT",
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
