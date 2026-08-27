#!/usr/bin/env python3
"""Compile and boundary-license a known or future surface."""

from __future__ import annotations

import argparse
import json

import run as core


EVENT_DICTIONARY = (
    core.ROOT
    / "experiments/yolo/gdt517_thirty_page_surface_recipe_intake_compiler/artifacts"
    / "gdt517_5866_exact_event_dictionary.tsv"
)
SURFACE_INDEX = (
    core.ROOT
    / "experiments/yolo/gdt517_thirty_page_surface_recipe_intake_compiler/artifacts"
    / "gdt517_current30_surface_role_index.tsv"
)


def explicit_context_nll(model, candidate, left, right) -> float:
    tokens = ["<S>"]
    if left:
        tokens.extend(left)
        tokens.append("<C>")
    target_start = len(tokens)
    tokens.extend(candidate)
    target_end = len(tokens)
    if right:
        tokens.append("<C>")
        tokens.extend(right)
    tokens.append("<E>")
    return model.touching_nll(tokens, target_start, target_end)


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

    surface = args.surface.lower()
    unified = core.read_tsv(core.G519.G517.G516_UNIFIED)
    running = [row for row in unified if row["group_kind"] == "RUNNING_EVENT"]
    recipe_field = "gdt516_context_recipe"
    compiler = core.G517.build_model("CURRENT30_RUNNING", running, recipe_field)
    mappings = core.G517.retained_mappings(compiler.evidence)
    ridge = core.G518.train_surface_ridge(running, recipe_field)
    bigram = core.G518.train_ngram(
        running, "source_statement_id", recipe_field, order=2
    )
    trigram = core.G518.train_ngram(
        running, "source_statement_id", recipe_field, order=3
    )
    deck, _ = core.G519.build_anchor_deck(
        compiler,
        core.G519.model_atoms(running, recipe_field),
        "CURRENT30_RUNNING",
    )
    boundary_model = core.train_boundary_model(running, recipe_field, deck)
    left = core.G517.atoms(args.left_recipe)
    right = core.G517.atoms(args.right_recipe)
    allow_f66r_local = args.page == "f66r" and args.domain == "LOCAL_RECORD"
    candidates = core.G517.parse_surface(
        surface,
        mappings,
        cap=core.G519.CANDIDATE_CAP,
        allow_f66r_local=allow_f66r_local,
    )
    prediction = ridge.predict(surface)
    matrix = core.G519.segment_matrix(
        surface, core.G519.needed_renderer_sequences(candidates, deck), deck
    )
    scored = []
    for base_index, candidate in enumerate(candidates):
        structural = ridge.squared_cost(prediction, candidate.recipe)
        bigram_nll = explicit_context_nll(bigram, candidate.recipe, left, right)
        trigram_nll = explicit_context_nll(trigram, candidate.recipe, left, right)
        context_base = (
            structural
            + core.math.log1p(base_index)
            + (core.G518.CONTEXT_WEIGHT / 2.0) * (bigram_nll + trigram_nll)
        )
        anchor_cost, path = core.alignment_path(surface, candidate.recipe, matrix)
        gdt519_score = context_base + anchor_cost
        boundary_nll = boundary_model.nll(surface, path)
        gdt520_score = core.score_config(
            gdt519_score,
            len(path),
            boundary_nll,
            core.SEGMENT_COUNT_WEIGHT,
            core.BOUNDARY_WEIGHT,
        )
        scored.append(
            {
                "compiler_rank": base_index + 1,
                "recipe": core.G517.recipe_text(candidate.recipe),
                "gdt519_score": gdt519_score,
                "renderer_segment_count": len(path),
                "boundary_license_nll": boundary_nll,
                "gdt520_score": gdt520_score,
                "alignment_trace": core.path_text(surface, path),
                "derivation": core.G517.path_text(candidate),
            }
        )
    scored.sort(key=lambda row: (float(row["gdt520_score"]), int(row["compiler_rank"])))

    exact = [row for row in core.read_tsv(EVENT_DICTIONARY) if row["surface"] == surface]
    if args.event_id != "NONE":
        exact = [row for row in exact if row["source_event_id"] == args.event_id]
    if args.page != "AUTO":
        exact = [row for row in exact if row["physical_page"] == args.page]
    if args.domain != "AUTO":
        exact = [row for row in exact if row["execution_domain"] == args.domain]
    known = [row for row in core.read_tsv(SURFACE_INDEX) if row["surface"] == surface]
    if args.domain != "AUTO":
        known = [row for row in known if row["execution_domain"] == args.domain]
    default = (
        exact[0]["exact_event_recipe"]
        if len(exact) == 1
        else known[0]["exact_event_recipe"]
        if len(known) == 1
        else scored[0]["recipe"]
        if scored
        else "UNPARSED"
    )
    result = {
        "surface": surface,
        "context": {
            "left_recipe": args.left_recipe,
            "right_recipe": args.right_recipe,
            "page": args.page,
            "domain": args.domain,
        },
        "current_renderer_sequence_count": len(deck),
        "current_renderer_option_count": sum(len(options) for options in deck.values()),
        "boundary_training_surface_count": boundary_model.surface_count,
        "boundary_license_pair_count": len(boundary_model.pair_counts),
        "boundary_license_window_count": len(boundary_model.window_counts),
        "exact_event_match_count": len(exact),
        "known_surface_option_count": len(known),
        "reranked_candidates": scored[: max(1, args.top)],
        "selection_precedence": "EXACT_EVENT>KNOWN_SURFACE_ROLE_OPTION>GDT520_BOUNDARY_LICENSED_TOP1",
        "default_selection": default,
        "guard": "VISIBLE_BOUNDARY_RECIPE_DEFAULT__NO_CONFIRMED_LEXEME_OR_PLAINTEXT",
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
