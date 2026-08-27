#!/usr/bin/env python3
"""Require two independent old bases to support one local-edit candidate."""

from __future__ import annotations

import csv
import importlib.util
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt524_multi_base_analogy_consensus"
OUT = BASE / "artifacts"
G523_RUN = (
    ROOT
    / "experiments/yolo/gdt523_path_local_null_renderer_license/src/run.py"
)

# stage, feature, weight
CONFIGS = (
    ("GDT523_BASE", "BASE", 0.0),
    ("SUM2_W010", "SUM_TWO", 0.10),
    ("SUM2_W025", "SUM_TWO", 0.25),
    ("SUM2_W050", "SUM_TWO", 0.50),
    ("SUM2_W075", "SUM_TWO", 0.75),
    ("SUM2_W100", "SUM_TWO", 1.00),
    ("SUM2_W125", "SUM_TWO", 1.25),
    ("SUM2_W150", "SUM_TWO", 1.50),
    ("SECOND_W050", "SECOND_BASE", 0.50),
    ("SECOND_W075", "SECOND_BASE", 0.75),
    ("SECOND_W100", "SECOND_BASE", 1.00),
    ("SECOND_W150", "SECOND_BASE", 1.50),
    ("SECOND_W200", "SECOND_BASE", 2.00),
    ("SECOND_W250", "SECOND_BASE", 2.50),
    ("MIN2_W050", "MIN_TWO", 0.50),
    ("MIN2_W075", "MIN_TWO", 0.75),
    ("MIN2_W100", "MIN_TWO", 1.00),
    ("MIN2_W150", "MIN_TWO", 1.50),
    ("MIN2_W200", "MIN_TWO", 2.00),
    ("MIN2_W250", "MIN_TWO", 2.50),
    ("COUNT_W050", "COUNT_PAIR", 0.50),
    ("COUNT_W100", "COUNT_PAIR", 1.00),
    ("COUNT_W150", "COUNT_PAIR", 1.50),
    ("COUNT_W200", "COUNT_PAIR", 2.00),
)
SELECTED_STAGE = "SUM2_W100"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


G523 = load_module("gdt523_core_for_gdt524", G523_RUN)
G522 = G523.G522
G521 = G523.G521
G520 = G523.G520
G519 = G523.G519
G518 = G523.G518
G517 = G523.G517


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=fields, delimiter="\t", lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)


def write_json(path: Path, value: object) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def recipe_text(recipe: tuple[str, ...]) -> str:
    return G517.recipe_text(recipe)


def selected_upstream_parameters():
    g522_missing, g522_weight = G523.gdt522_selected_config()
    _, path_mode, path_weight = next(
        row for row in G523.CONFIGS if row[0] == G523.SELECTED_STAGE
    )
    return g522_missing, g522_weight, path_mode, path_weight


def consensus_features(
    surface: str,
    recipe: tuple[str, ...],
    analogy: G522.AnalogyModel,
    missing_cost: float,
):
    best_by_base = {}
    for hit in analogy.hits(surface, recipe, missing_cost):
        previous = best_by_base.get(hit.base_surface)
        if previous is None or hit.license_bonus > previous.license_bonus:
            best_by_base[hit.base_surface] = hit
    positive = sorted(
        (hit for hit in best_by_base.values() if hit.license_bonus > 0),
        key=lambda hit: hit.license_bonus,
        reverse=True,
    )
    compatible_pairs = [
        (first, second)
        for first_index, first in enumerate(positive)
        for second in positive[first_index + 1 :]
        if (first.visible_insert, first.atom_insert)
        != (second.visible_insert, second.atom_insert)
    ]
    if not compatible_pairs:
        return {
            "SUM_TWO": 0.0,
            "SECOND_BASE": 0.0,
            "MIN_TWO": 0.0,
            "COUNT_PAIR": 0.0,
        }, "NO_TWO_DISTINCT_BASE_AND_EDIT_CHANNELS", []
    first, second = max(
        compatible_pairs,
        key=lambda pair: (
            pair[0].license_bonus + pair[1].license_bonus,
            min(pair[0].license_bonus, pair[1].license_bonus),
            pair[0].base_surface,
            pair[1].base_surface,
        ),
    )
    features = {
        "SUM_TWO": first.license_bonus + second.license_bonus,
        "SECOND_BASE": second.license_bonus,
        "MIN_TWO": min(first.license_bonus, second.license_bonus),
        "COUNT_PAIR": 1.0,
    }
    trace = f"BASE1[{first.trace()}] | BASE2[{second.trace()}]"
    return features, trace, [first, second]


def score_sets_for_candidates(
    surface: str,
    candidates,
    base_scores: list[float],
    analogy: G522.AnalogyModel,
    missing_cost: float,
):
    features = []
    traces = []
    positives = []
    for candidate in candidates:
        values, trace, hits = consensus_features(
            surface, candidate.recipe, analogy, missing_cost
        )
        features.append(values)
        traces.append(trace)
        positives.append(hits)
    score_sets = {}
    for stage, mode, weight in CONFIGS:
        score_sets[stage] = (
            list(base_scores)
            if mode == "BASE"
            else [
                base - weight * feature[mode]
                for base, feature in zip(base_scores, features)
            ]
        )
    return score_sets, features, traces, positives


def metric_row(scope: str, config, ranks: list[int]):
    stage, mode, weight = config
    return {
        "scope": scope,
        "model_stage": stage,
        "consensus_feature": mode,
        "consensus_weight": weight,
        **G519.rank_metrics(ranks),
    }


def fold_rehearsal(old: list[dict[str, str]]):
    forms = G518.invariant_surface_recipes(old, "component_recipe")
    rank_sets: dict[str, list[int]] = defaultdict(list)
    output: list[dict[str, object]] = []
    g522_missing, g522_weight, path_mode, path_weight = selected_upstream_parameters()
    selected_mode = next(row[1] for row in CONFIGS if row[0] == SELECTED_STAGE)
    for fold in range(G520.FOLD_COUNT):
        held = {surface for surface in forms if G520.stable_fold(surface) == fold}
        training = [row for row in old if row["surface"] not in held]
        train_forms = G518.invariant_surface_recipes(training, "component_recipe")
        analogy = G522.train_analogy_model(train_forms)
        null_context = G523.train_null_context_model(train_forms)
        mappings, ridge, deck, boundaries, recipe_models = G521.build_base_models(
            training, "component_recipe", f"GDT524_FOLD_{fold}_TRAIN"
        )
        history = recipe_models[(G521.SELECTED_ORDER, G521.SELECTED_ALPHA)]
        for surface in sorted(held):
            truth = forms[surface]
            candidates = G517.parse_surface(
                surface, mappings, cap=G519.CANDIDATE_CAP
            )
            truth_index = next(
                (i for i, candidate in enumerate(candidates) if candidate.recipe == truth),
                None,
            )
            if truth_index is None:
                for stage, _, _ in CONFIGS:
                    rank_sets[stage].append(0)
                output.append(
                    {
                        "fold": fold,
                        "surface": surface,
                        "truth_recipe": recipe_text(truth),
                        "candidate_count_capped": len(candidates),
                        "truth_generated": "NO",
                        "gdt523_rank": 0,
                        "gdt524_rank": 0,
                        "gdt523_top1": recipe_text(candidates[0].recipe) if candidates else "NONE",
                        "gdt524_top1": "NONE",
                        "truth_consensus_feature": "NONE",
                        "top1_consensus_feature": "NONE",
                        "truth_consensus_trace": "NONE",
                        "top1_consensus_trace": "NONE",
                    }
                )
                continue
            prediction = ridge.predict(surface)
            matrix = G519.segment_matrix(
                surface, G519.needed_renderer_sequences(candidates, deck), deck
            )
            base_scores: list[float] = []
            for index, candidate in enumerate(candidates):
                anchor_cost, path = G520.alignment_path(
                    surface, candidate.recipe, matrix
                )
                gdt519_score = (
                    ridge.squared_cost(prediction, candidate.recipe)
                    + math.log1p(index)
                    + anchor_cost
                )
                gdt520_score = G520.score_config(
                    gdt519_score,
                    len(path),
                    boundaries.nll(surface, path),
                    G520.SEGMENT_COUNT_WEIGHT,
                    G520.BOUNDARY_WEIGHT,
                )
                gdt521_score = (
                    gdt520_score
                    + G521.SELECTED_WEIGHT * history.mean_nll(candidate.recipe)
                )
                analogy_bonus, _ = analogy.feature(
                    surface, candidate.recipe, g522_missing
                )
                gdt522_score = gdt521_score - g522_weight * analogy_bonus
                path_values, _ = G523.path_features(
                    surface, path, analogy, null_context
                )
                base_scores.append(
                    gdt522_score - path_weight * path_values[path_mode]
                )
            score_sets, features, traces, _ = score_sets_for_candidates(
                surface, candidates, base_scores, analogy, g522_missing
            )
            orders = {}
            for stage, _, _ in CONFIGS:
                rank, order = G519.rank_by_score(
                    candidates, truth, score_sets[stage]
                )
                rank_sets[stage].append(rank)
                orders[stage] = order
            base_top = orders["GDT523_BASE"][0]
            top = orders[SELECTED_STAGE][0]
            output.append(
                {
                    "fold": fold,
                    "surface": surface,
                    "truth_recipe": recipe_text(truth),
                    "candidate_count_capped": len(candidates),
                    "truth_generated": "YES",
                    "gdt523_rank": rank_sets["GDT523_BASE"][-1],
                    "gdt524_rank": rank_sets[SELECTED_STAGE][-1],
                    "gdt523_top1": recipe_text(candidates[base_top].recipe),
                    "gdt524_top1": recipe_text(candidates[top].recipe),
                    "truth_consensus_feature": f"{features[truth_index][selected_mode]:.9f}",
                    "top1_consensus_feature": f"{features[top][selected_mode]:.9f}",
                    "truth_consensus_trace": traces[truth_index],
                    "top1_consensus_trace": traces[top],
                }
            )
    ladder = [
        metric_row(
            "FOUR_FOLD_OLD26_SURFACE_REHEARSAL", config, rank_sets[config[0]]
        )
        for config in CONFIGS
    ]
    return output, ladder


def current_benchmark(old, selected, targets):
    forms = G518.invariant_surface_recipes(old, "component_recipe")
    analogy = G522.train_analogy_model(forms)
    null_context = G523.train_null_context_model(forms)
    g522_missing, g522_weight, path_mode, path_weight = selected_upstream_parameters()
    mappings, ridge, deck, boundaries, recipe_models = G521.build_base_models(
        old, "component_recipe", "GDT524_FULL_OLD26"
    )
    history = recipe_models[(G521.SELECTED_ORDER, G521.SELECTED_ALPHA)]
    bigram = G518.train_ngram(
        old, "source_statement_id", "component_recipe", order=2
    )
    trigram = G518.train_ngram(
        old, "source_statement_id", "component_recipe", order=3
    )
    occurrences = G518.selected_prose_occurrences(selected)
    rank_sets: dict[str, list[int]] = defaultdict(list)
    output: list[dict[str, object]] = []
    candidate_rows: list[dict[str, object]] = []
    route_rows: list[dict[str, object]] = []
    selected_mode = next(row[1] for row in CONFIGS if row[0] == SELECTED_STAGE)
    selected_weight = next(row[2] for row in CONFIGS if row[0] == SELECTED_STAGE)
    for target in targets:
        surface = target["surface"]
        truth = G517.atoms(target["gdt516_context_recipe"])
        candidates = G517.parse_surface(
            surface,
            mappings,
            cap=G519.CANDIDATE_CAP,
            allow_f66r_local=True,
        )
        prediction = ridge.predict(surface)
        matrix = G519.segment_matrix(
            surface, G519.needed_renderer_sequences(candidates, deck), deck
        )
        base_scores: list[float] = []
        paths = []
        for index, candidate in enumerate(candidates):
            context_base, _, _, _ = G519.current_context_base_score(
                surface,
                candidate,
                index,
                prediction,
                ridge,
                bigram,
                trigram,
                occurrences,
            )
            anchor_cost, path = G520.alignment_path(
                surface, candidate.recipe, matrix
            )
            gdt520_score = G520.score_config(
                context_base + anchor_cost,
                len(path),
                boundaries.nll(surface, path),
                G520.SEGMENT_COUNT_WEIGHT,
                G520.BOUNDARY_WEIGHT,
            )
            gdt521_score = (
                gdt520_score
                + G521.SELECTED_WEIGHT * history.mean_nll(candidate.recipe)
            )
            analogy_bonus, _ = analogy.feature(
                surface, candidate.recipe, g522_missing
            )
            gdt522_score = gdt521_score - g522_weight * analogy_bonus
            path_values, _ = G523.path_features(
                surface, path, analogy, null_context
            )
            base_scores.append(gdt522_score - path_weight * path_values[path_mode])
            paths.append(path)
        score_sets, features, traces, positives = score_sets_for_candidates(
            surface, candidates, base_scores, analogy, g522_missing
        )
        orders = {}
        for stage, _, _ in CONFIGS:
            rank, order = G519.rank_by_score(candidates, truth, score_sets[stage])
            rank_sets[stage].append(rank)
            orders[stage] = order
        truth_index = next(
            index for index, candidate in enumerate(candidates) if candidate.recipe == truth
        )
        base_top = orders["GDT523_BASE"][0]
        top = orders[SELECTED_STAGE][0]
        base_rank = rank_sets["GDT523_BASE"][-1]
        selected_rank = rank_sets[SELECTED_STAGE][-1]
        if base_rank == 1 and selected_rank == 1:
            change = "GDT523_CORRECT_PRESERVED"
        elif base_rank != 1 and selected_rank == 1:
            change = "GDT523_ERROR_CORRECTED"
        elif base_rank == 1 and selected_rank != 1:
            change = "GDT523_CORRECT_LOST"
        elif candidates[base_top].recipe != candidates[top].recipe:
            change = "ERROR_CHANGED_STILL_WRONG"
        else:
            change = "GDT523_ERROR_UNCHANGED"
        output.append(
            {
                "surface": surface,
                "occurrence_count": target["occurrence_count"],
                "physical_pages": target["physical_pages"],
                "truth_recipe": recipe_text(truth),
                "candidate_count_capped": len(candidates),
                "gdt523_rank": base_rank,
                "gdt523_top1": recipe_text(candidates[base_top].recipe),
                "gdt524_rank": selected_rank,
                "gdt524_top1": recipe_text(candidates[top].recipe),
                "gdt524_top5": " | ".join(
                    recipe_text(candidates[index].recipe)
                    for index in orders[SELECTED_STAGE][:5]
                ),
                "truth_gdt523_score": f"{base_scores[truth_index]:.9f}",
                "truth_consensus_feature": f"{features[truth_index][selected_mode]:.9f}",
                "truth_gdt524_score": f"{score_sets[SELECTED_STAGE][truth_index]:.9f}",
                "truth_consensus_trace": traces[truth_index],
                "top1_gdt523_score": f"{base_scores[top]:.9f}",
                "top1_consensus_feature": f"{features[top][selected_mode]:.9f}",
                "top1_gdt524_score": f"{score_sets[SELECTED_STAGE][top]:.9f}",
                "top1_consensus_trace": traces[top],
                "top1_alignment_trace": G520.path_text(surface, paths[top]),
                "decision_change_class": change,
                "working_policy": "KNOWN_EVENT_OR_SURFACE_RECIPE_STILL_WINS__TWO_DISTINCT_OLD_BASES_MUST_POSITIVELY_SUPPORT_THE_SAME_CANDIDATE",
            }
        )
        if selected_rank != 1 or candidates[base_top].recipe != candidates[top].recipe:
            for selected_candidate_rank, index in enumerate(
                orders[SELECTED_STAGE][:12], 1
            ):
                candidate_rows.append(
                    {
                        "surface": surface,
                        "truth_recipe": recipe_text(truth),
                        "candidate_is_truth": "YES" if candidates[index].recipe == truth else "NO",
                        "gdt517_compiler_rank": index + 1,
                        "gdt523_rank": orders["GDT523_BASE"].index(index) + 1,
                        "gdt524_rank": selected_candidate_rank,
                        "candidate_recipe": recipe_text(candidates[index].recipe),
                        "gdt523_score": f"{base_scores[index]:.9f}",
                        "consensus_feature": f"{features[index][selected_mode]:.9f}",
                        "gdt524_score": f"{score_sets[SELECTED_STAGE][index]:.9f}",
                        "positive_independent_base_count": len(positives[index]),
                        "consensus_trace": traces[index],
                    }
                )
        for index, hits in enumerate(positives):
            if len(hits) < 2:
                continue
            for base_rank_index, hit in enumerate(hits, 1):
                route_rows.append(
                    {
                        "surface": surface,
                        "candidate_recipe": recipe_text(candidates[index].recipe),
                        "candidate_is_truth": "YES" if candidates[index].recipe == truth else "NO",
                        "gdt523_rank": orders["GDT523_BASE"].index(index) + 1,
                        "gdt524_rank": orders[SELECTED_STAGE].index(index) + 1,
                        "positive_base_count": len(hits),
                        "base_support_rank": base_rank_index,
                        "base_surface": hit.base_surface,
                        "visible_insert": hit.visible_insert,
                        "atom_insert": recipe_text(hit.atom_insert) if hit.atom_insert else "NULL",
                        "signature_support": hit.support,
                        "license_bonus": f"{hit.license_bonus:.9f}",
                        "route_trace": hit.trace(),
                    }
                )
    ladder = [
        metric_row("CURRENT_159_OLD26_TO_NEW4", config, rank_sets[config[0]])
        for config in CONFIGS
    ]
    return output, candidate_rows, route_rows, ladder


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    old = read_tsv(G518.G407_RUNNING)
    selected = read_tsv(G518.G516_SELECTED)
    targets = read_tsv(G518.G516_NEW)
    rehearsal, old_ladder = fold_rehearsal(old)
    current, candidates, routes, current_ladder = current_benchmark(
        old, selected, targets
    )

    rehearsal_fields = [
        "fold", "surface", "truth_recipe", "candidate_count_capped",
        "truth_generated", "gdt523_rank", "gdt524_rank", "gdt523_top1",
        "gdt524_top1", "truth_consensus_feature", "top1_consensus_feature",
        "truth_consensus_trace", "top1_consensus_trace",
    ]
    current_fields = [
        "surface", "occurrence_count", "physical_pages", "truth_recipe",
        "candidate_count_capped", "gdt523_rank", "gdt523_top1", "gdt524_rank",
        "gdt524_top1", "gdt524_top5", "truth_gdt523_score",
        "truth_consensus_feature", "truth_gdt524_score",
        "truth_consensus_trace", "top1_gdt523_score",
        "top1_consensus_feature", "top1_gdt524_score", "top1_consensus_trace",
        "top1_alignment_trace", "decision_change_class", "working_policy",
    ]
    write_tsv(
        OUT / "gdt524_1558_four_fold_multi_base_rehearsal.tsv",
        rehearsal,
        rehearsal_fields,
    )
    write_tsv(OUT / "gdt524_159_multi_base_rerank.tsv", current, current_fields)
    write_tsv(
        OUT / "gdt524_changed_decision_atlas.tsv",
        [row for row in current if row["gdt523_top1"] != row["gdt524_top1"]],
        current_fields,
    )
    write_tsv(
        OUT / "gdt524_remaining_top1_error_atlas.tsv",
        [row for row in current if int(row["gdt524_rank"]) != 1],
        current_fields,
    )
    write_tsv(
        OUT / "gdt524_candidate_score_atlas.tsv",
        candidates,
        [
            "surface", "truth_recipe", "candidate_is_truth",
            "gdt517_compiler_rank", "gdt523_rank", "gdt524_rank",
            "candidate_recipe", "gdt523_score", "consensus_feature",
            "gdt524_score", "positive_independent_base_count",
            "consensus_trace",
        ],
    )
    write_tsv(
        OUT / "gdt524_multi_base_route_atlas.tsv",
        routes,
        [
            "surface", "candidate_recipe", "candidate_is_truth",
            "gdt523_rank", "gdt524_rank", "positive_base_count",
            "base_support_rank", "base_surface", "visible_insert",
            "atom_insert", "signature_support", "license_bonus", "route_trace",
        ],
    )
    ladder = old_ladder + current_ladder
    write_tsv(
        OUT / "gdt524_model_ladder.tsv",
        ladder,
        [
            "scope", "model_stage", "consensus_feature", "consensus_weight",
            "target_count", "truth_generated_count", "top1_exact_count",
            "top2_exact_count", "top3_exact_count", "top5_exact_count",
            "rank_sum", "deepest_truth_rank",
        ],
    )

    old_base = G519.rank_metrics([int(row["gdt523_rank"]) for row in rehearsal])
    old_selected = G519.rank_metrics([int(row["gdt524_rank"]) for row in rehearsal])
    current_base = G519.rank_metrics([int(row["gdt523_rank"]) for row in current])
    current_selected = G519.rank_metrics([int(row["gdt524_rank"]) for row in current])
    selected_config = next(row for row in CONFIGS if row[0] == SELECTED_STAGE)
    classes = Counter(row["decision_change_class"] for row in current)
    result = {
        "experiment_id": "GDT524",
        "status": "PASS_TWO_INDEPENDENT_BASE_ANALOGY_CONSENSUS",
        "claim_ceiling": "EXPLORATORY_MULTI_BASE_LOCAL_EDIT_CONSENSUS__NO_CONFIRMED_LEXEME_OR_PLAINTEXT",
        "selected_policy": {
            "stage": selected_config[0],
            "feature": selected_config[1],
            "weight": selected_config[2],
            "independence_unit": "DISTINCT_OLD_BASE_SURFACE_AND_DISTINCT_VISIBLE_TO_ATOM_EDIT_CHANNEL",
            "activation": "AT_LEAST_TWO_POSITIVE_GDT522_LICENSE_BONUSES_WITH_DIFFERENT_NORMALIZED_CHANNELS",
            "aggregation": "SUM_OF_TWO_STRONGEST_DISTINCT_BASE_BONUSES",
        },
        "old26_four_fold_gdt523_metrics": old_base,
        "old26_four_fold_gdt524_metrics": old_selected,
        "current_gdt523_metrics": current_base,
        "current_gdt524_metrics": current_selected,
        "current_net_top1_gain": current_selected["top1_exact_count"] - current_base["top1_exact_count"],
        "current_rank_sum_reduction": current_base["rank_sum"] - current_selected["rank_sum"],
        "current_decision_change_classes": dict(sorted(classes.items())),
        "current_multi_base_candidate_count": len(
            {(row["surface"], row["candidate_recipe"]) for row in routes}
        ),
        "remaining_top1_error_count": sum(int(row["gdt524_rank"]) != 1 for row in current),
        "guard": "CONSENSUS_REQUIRES_TWO_DISTINCT_OLD_BASES__KNOWN_EVENT_AND_SURFACE_CARDS_KEEP_PRECEDENCE",
    }
    write_json(OUT / "gdt524_result.json", result)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
