#!/usr/bin/env python3
"""Compile a surface through GDT525's K-base two-hop stem closure."""

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
    unified = core.read_tsv(core.G517.G516_UNIFIED)
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
    renderer_deck, _ = core.G519.build_anchor_deck(
        compiler, core.G519.model_atoms(running, recipe_field), "CURRENT30_RUNNING"
    )
    boundary_model = core.G520.train_boundary_model(
        running, recipe_field, renderer_deck
    )
    history = core.G521.train_recipe_ngram(
        running, recipe_field, core.G521.SELECTED_ORDER, core.G521.SELECTED_ALPHA
    )
    old = core.read_tsv(core.G518.G407_RUNNING)
    old_forms = core.G518.invariant_surface_recipes(old, "component_recipe")
    analogy = core.G522.train_analogy_model(old_forms)
    pair_model = core.train_pair_model(old_forms)
    null_context = core.G523.train_null_context_model(old_forms)
    g522_missing, g522_weight, path_mode, path_weight = (
        core.G524.selected_upstream_parameters()
    )
    _, consensus_mode, consensus_weight = next(
        row for row in core.G524.CONFIGS if row[0] == core.G524.SELECTED_STAGE
    )
    _, chain_mode, chain_weight = next(
        row for row in core.CONFIGS if row[0] == core.SELECTED_STAGE
    )
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
        surface,
        core.G519.needed_renderer_sequences(candidates, renderer_deck),
        renderer_deck,
    )
    gdt524_scores = []
    partial = []
    for base_index, candidate in enumerate(candidates):
        structural = ridge.squared_cost(prediction, candidate.recipe)
        bigram_nll = explicit_context_nll(bigram, candidate.recipe, left, right)
        trigram_nll = explicit_context_nll(trigram, candidate.recipe, left, right)
        context_base = (
            structural
            + core.math.log1p(base_index)
            + (core.G518.CONTEXT_WEIGHT / 2.0) * (bigram_nll + trigram_nll)
        )
        anchor_cost, path = core.G520.alignment_path(
            surface, candidate.recipe, matrix
        )
        gdt520_score = core.G520.score_config(
            context_base + anchor_cost,
            len(path),
            boundary_model.nll(surface, path),
            core.G520.SEGMENT_COUNT_WEIGHT,
            core.G520.BOUNDARY_WEIGHT,
        )
        gdt521_score = (
            gdt520_score
            + core.G521.SELECTED_WEIGHT * history.mean_nll(candidate.recipe)
        )
        analogy_bonus, analogy_trace = analogy.feature(
            surface, candidate.recipe, g522_missing
        )
        gdt522_score = gdt521_score - g522_weight * analogy_bonus
        path_values, path_null_trace = core.G523.path_features(
            surface, path, analogy, null_context
        )
        gdt523_score = gdt522_score - path_weight * path_values[path_mode]
        consensus, consensus_trace, bases = core.G524.consensus_features(
            surface, candidate.recipe, analogy, g522_missing
        )
        gdt524_score = gdt523_score - consensus_weight * consensus[consensus_mode]
        gdt524_scores.append(gdt524_score)
        partial.append(
            {
                "compiler_rank": base_index + 1,
                "recipe": core.recipe_text(candidate.recipe),
                "gdt524_score": gdt524_score,
                "nearest_analogy_trace": analogy_trace,
                "path_null_trace": path_null_trace,
                "consensus_trace": consensus_trace,
                "independent_base_count": len(bases),
                "alignment_trace": core.G520.path_text(surface, path),
                "derivation": core.G517.path_text(candidate),
            }
        )
    score_sets, features, traces, hits, _ = core.chain_score_sets(
        surface, candidates, gdt524_scores, analogy, pair_model, g522_missing
    )
    selected_scores = score_sets[core.SELECTED_STAGE]
    scored = []
    for index, row in enumerate(partial):
        hit = hits[index]
        scored.append(
            {
                **row,
                "chain_feature": features[index][chain_mode],
                "gdt525_score": selected_scores[index],
                "chain_trace": traces[index],
                "ordered_pair_support": pair_model.support(hit) if hit else 0,
            }
        )
    scored.sort(
        key=lambda row: (float(row["gdt525_score"]), int(row["compiler_rank"]))
    )

    exact = [
        row for row in core.read_tsv(EVENT_DICTIONARY) if row["surface"] == surface
    ]
    if args.event_id != "NONE":
        exact = [row for row in exact if row["source_event_id"] == args.event_id]
    if args.page != "AUTO":
        exact = [row for row in exact if row["physical_page"] == args.page]
    if args.domain != "AUTO":
        exact = [row for row in exact if row["execution_domain"] == args.domain]
    known = [
        row for row in core.read_tsv(SURFACE_INDEX) if row["surface"] == surface
    ]
    if args.domain != "AUTO":
        known = [row for row in known if row["execution_domain"] == args.domain]
    revision = core.WORKING_REVISIONS.get(surface)
    default = (
        revision
        if revision is not None
        else exact[0]["exact_event_recipe"]
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
        "selected_chain_stage": core.SELECTED_STAGE,
        "selected_chain_feature": chain_mode,
        "selected_chain_weight": chain_weight,
        "old_analogy_training_surface_count": len(old_forms),
        "old_ordered_pair_type_count": len(pair_model.counts),
        "exact_event_match_count": len(exact),
        "known_surface_option_count": len(known),
        "working_revision": revision or "NONE",
        "reranked_candidates": scored[: max(1, args.top)],
        "selection_precedence": "GDT525_WORKING_REVISION>EXACT_EVENT>KNOWN_SURFACE_ROLE_OPTION>GDT525_K_STEM_TOP1",
        "default_selection": default,
        "guard": "PRODUCTIVE_K_STEM_RULE__NO_CONFIRMED_LEXEME_OR_PLAINTEXT",
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
