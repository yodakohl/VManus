#!/usr/bin/env python3
"""Compile and stem-align a known or future surface with the current 30-page model."""

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
    parser.add_argument("--domain", choices=("AUTO", "PROSE_STREAM", "LOCAL_RECORD"), default="AUTO")
    parser.add_argument("--top", type=int, default=5)
    args = parser.parse_args()

    surface = args.surface.lower()
    unified = core.read_tsv(core.G517.G516_UNIFIED)
    running = [row for row in unified if row["group_kind"] == "RUNNING_EVENT"]
    compiler = core.G517.build_model("CURRENT30_RUNNING", running, "gdt516_context_recipe")
    mappings = core.G517.retained_mappings(compiler.evidence)
    ridge = core.G518.train_surface_ridge(running, "gdt516_context_recipe")
    bigram = core.G518.train_ngram(
        running, "source_statement_id", "gdt516_context_recipe", order=2
    )
    trigram = core.G518.train_ngram(
        running, "source_statement_id", "gdt516_context_recipe", order=3
    )
    deck, _ = core.build_anchor_deck(
        compiler,
        core.model_atoms(running, "gdt516_context_recipe"),
        "CURRENT30_RUNNING",
    )
    left = core.G517.atoms(args.left_recipe)
    right = core.G517.atoms(args.right_recipe)
    allow_f66r_local = args.page == "f66r" and args.domain == "LOCAL_RECORD"
    candidates = core.G517.parse_surface(
        surface,
        mappings,
        cap=core.CANDIDATE_CAP,
        allow_f66r_local=allow_f66r_local,
    )
    prediction = ridge.predict(surface)
    matrix = core.segment_matrix(
        surface, core.needed_renderer_sequences(candidates, deck), deck
    )
    scored = []
    for base_index, candidate in enumerate(candidates):
        structural = ridge.squared_cost(prediction, candidate.recipe)
        bigram_nll = explicit_context_nll(bigram, candidate.recipe, left, right)
        trigram_nll = explicit_context_nll(trigram, candidate.recipe, left, right)
        base_score = (
            structural
            + core.math.log1p(base_index)
            + (core.G518.CONTEXT_WEIGHT / 2.0) * (bigram_nll + trigram_nll)
        )
        anchor_cost, trace = core.alignment_trace(surface, candidate.recipe, matrix)
        scored.append(
            {
                "compiler_rank": base_index + 1,
                "recipe": core.G517.recipe_text(candidate.recipe),
                "gdt518_base_score": base_score,
                "stem_anchor_cost": anchor_cost,
                "gdt519_score": base_score + core.SELECTED_ANCHOR_WEIGHT * anchor_cost,
                "alignment_trace": trace,
                "derivation": core.G517.path_text(candidate),
            }
        )
    scored.sort(key=lambda row: (float(row["gdt519_score"]), int(row["compiler_rank"])))

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
        "exact_event_match_count": len(exact),
        "known_surface_option_count": len(known),
        "reranked_candidates": scored[: max(1, args.top)],
        "selection_precedence": "EXACT_EVENT>KNOWN_SURFACE_ROLE_OPTION>GDT519_STEM_ALIGNED_TOP1",
        "default_selection": default,
        "guard": "VISIBLE_STRUCTURAL_STEM_RECIPE__NO_CONFIRMED_LEXEME_OR_PLAINTEXT",
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
