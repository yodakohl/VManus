#!/usr/bin/env python3
"""Compile one surface through GDT527's certified terminal-s stem rule."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys

import run as core


G526_ALIGN = (
    core.ROOT
    / "experiments/yolo/gdt526_cha_intermediate_stem_extension/src/align_surface.py"
)


def inherited_result(args: argparse.Namespace) -> dict:
    command = [
        sys.executable,
        str(G526_ALIGN),
        "--surface", args.surface,
        "--left-recipe", args.left_recipe,
        "--right-recipe", args.right_recipe,
        "--event-id", args.event_id,
        "--page", args.page,
        "--domain", args.domain,
        "--top", "10000",
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

    inherited = inherited_result(args)
    old = core.read_tsv(core.G518.G407_RUNNING)
    forms = core.G518.invariant_surface_recipes(old, "component_recipe")
    analogy = core.G522.train_analogy_model(forms)
    missing_cost = core.G524.selected_upstream_parameters()[0]
    scored = []
    for row in inherited["reranked_candidates"]:
        recipe = core.G517.atoms(row["recipe"])
        features, trace, hit = core.stem_features(
            args.surface, recipe, analogy, missing_cost
        )
        feature = features["CERT_S_BP1"]
        scored.append(
            {
                **row,
                "stem_feature": feature,
                "stem_trace": trace,
                "stem_base": hit["base_surface"] if hit else "NONE",
                "stem_certificate": hit["certificate"] if hit else "NONE",
                "gdt527_score": float(row["gdt526_score"]) - 0.5 * feature,
            }
        )
    scored.sort(
        key=lambda row: (float(row["gdt527_score"]), int(row["compiler_rank"]))
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
        "selected_feature": "CERT_S_BP1",
        "selected_weight": 0.5,
        "stem_certificate": "RECIPE_HAS_AT_LEAST_3_OLD_SURFACES_OR_STEM_HAS_NON_NULL_ONE_CHAR_RIGHT_CHILD",
        "terminal_rule": "s->S",
        "l_guard": "VISIBLE_OL_DEFAULTS_TO_ATOMIC_OL_UNLESS_AN_EXACT_O_PLUS_L_CARD_EXISTS",
        "exact_event_match_count": exact_count,
        "known_surface_option_count": known_count,
        "working_revision": revision or "NONE",
        "reranked_candidates": scored[: max(1, args.top)],
        "selection_precedence": "WORKING_REVISION>EXACT_EVENT>KNOWN_SURFACE_ROLE_OPTION>GDT527_CERTIFIED_S_STEM_TOP1",
        "default_selection": default,
        "guard": "CERTIFIED_STEM_PLUS_TRANSPARENT_S__NO_CONFIRMED_LEXEME_OR_PLAINTEXT",
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
