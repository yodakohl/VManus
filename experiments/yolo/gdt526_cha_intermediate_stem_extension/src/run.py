#!/usr/bin/env python3
"""Extend the exact old cha=CH+A_ADDR stem through licensed right edits."""

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
BASE = ROOT / "experiments/yolo/gdt526_cha_intermediate_stem_extension"
OUT = BASE / "artifacts"
G525_RUN = (
    ROOT / "experiments/yolo/gdt525_two_hop_intermediate_stem_analogy/src/run.py"
)


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


G525 = load_module("gdt525_core_for_gdt526", G525_RUN)
G524 = G525.G524
G523 = G525.G523
G522 = G525.G522
G521 = G525.G521
G520 = G525.G520
G519 = G525.G519
G518 = G525.G518
G517 = G525.G517

# stage, feature, weight
CONFIGS = (
    ("GDT525_BASE", "BASE", 0.0),
    *((f"BP1_W{int(weight * 100):03d}", "BONUS_PLUS_ONE", weight) for weight in (0.25, 0.50, 0.60, 0.70, 0.75, 0.80, 0.85, 0.90, 1.00, 1.25)),
    *((f"BON_W{int(weight * 100):03d}", "BONUS_ONLY", weight) for weight in (0.50, 0.75, 1.00, 1.25, 1.50, 2.00, 2.50)),
    *((f"BIN_W{int(weight * 100):03d}", "BINARY", weight) for weight in (0.25, 0.50, 0.75, 1.00, 1.25, 1.50)),
)
SELECTED_STAGE = "BP1_W080"
CHA_SURFACE = "cha"
CHA_RECIPE = ("CH", "A_ADDR")
WORKING_REVISIONS = dict(G525.WORKING_REVISIONS)


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


def cha_stem_features(surface, recipe, analogy, missing_cost):
    zero = {"BONUS_PLUS_ONE": 0.0, "BONUS_ONLY": 0.0, "BINARY": 0.0}
    if analogy.forms.get(CHA_SURFACE) != CHA_RECIPE:
        return zero, "CHA_STEM_NOT_AVAILABLE", None
    if not surface.startswith(CHA_SURFACE):
        return zero, "NO_CHA_PREFIX", None
    suffix = surface[len(CHA_SURFACE) :]
    if not 1 <= len(suffix) <= G522.MAX_VISIBLE_INSERT:
        return zero, "CHA_SUFFIX_OUTSIDE_EDIT_WIDTH", None
    if surface in analogy.forms and analogy.forms[surface] != recipe:
        return zero, "OLD_CHA_EXTENSION_CONTRADICTS_CANDIDATE", None
    hits = []
    for atom_insert, atom_position in G522.recipe_insertions(recipe, CHA_RECIPE):
        if atom_position != "RIGHT" or not atom_insert:
            continue
        signature = (suffix, "RIGHT", atom_insert, "RIGHT")
        stats = G525.signature_bonus(analogy, signature, missing_cost)
        if stats is None or stats[0] <= 0:
            continue
        hits.append((stats[0], stats[1], stats[2], atom_insert))
    if not hits:
        return zero, "NO_POSITIVE_RIGHT_SUFFIX_CHANNEL", None
    bonus, support, total, atoms = max(
        hits, key=lambda row: (row[0], row[1], recipe_text(row[3]))
    )
    trace = (
        f"cha={recipe_text(CHA_RECIPE)}+{suffix}=>{recipe_text(atoms)}"
        f"@RIGHT/RIGHT;n={support}/{total};b={bonus:.6f}"
    )
    return {
        "BONUS_PLUS_ONE": 1.0 + bonus,
        "BONUS_ONLY": bonus,
        "BINARY": 1.0,
    }, trace, {
        "suffix": suffix,
        "atom_insert": recipe_text(atoms),
        "support": support,
        "total": total,
        "bonus": bonus,
    }


def score_sets(surface, candidates, base_scores, analogy, missing_cost):
    features = []
    traces = []
    hits = []
    for candidate in candidates:
        values, trace, hit = cha_stem_features(
            surface, candidate.recipe, analogy, missing_cost
        )
        features.append(values)
        traces.append(trace)
        hits.append(hit)
    output = {}
    for stage, mode, weight in CONFIGS:
        output[stage] = (
            list(base_scores)
            if mode == "BASE"
            else [
                base - weight * values[mode]
                for base, values in zip(base_scores, features)
            ]
        )
    return output, features, traces, hits


def metric_row(scope: str, config, ranks: list[int]):
    stage, mode, weight = config
    return {
        "scope": scope,
        "model_stage": stage,
        "cha_feature": mode,
        "cha_weight": weight,
        **G519.rank_metrics(ranks),
    }


def fold_rehearsal(old):
    forms = G518.invariant_surface_recipes(old, "component_recipe")
    rank_sets: dict[str, list[int]] = defaultdict(list)
    output = []
    g522_missing, g522_weight, path_mode, path_weight = G524.selected_upstream_parameters()
    selected_mode = next(row[1] for row in CONFIGS if row[0] == SELECTED_STAGE)
    for fold in range(G520.FOLD_COUNT):
        held = {surface for surface in forms if G520.stable_fold(surface) == fold}
        training = [row for row in old if row["surface"] not in held]
        train_forms = G518.invariant_surface_recipes(training, "component_recipe")
        analogy = G522.train_analogy_model(train_forms)
        pair_model = G525.train_pair_model(train_forms)
        null_context = G523.train_null_context_model(train_forms)
        mappings, ridge, renderer_deck, boundaries, recipe_models = G521.build_base_models(
            training, "component_recipe", f"GDT526_FOLD_{fold}_TRAIN"
        )
        history = recipe_models[(G521.SELECTED_ORDER, G521.SELECTED_ALPHA)]
        for surface in sorted(held):
            truth = forms[surface]
            candidates = G517.parse_surface(surface, mappings, cap=G519.CANDIDATE_CAP)
            truth_index = next(
                (index for index, candidate in enumerate(candidates) if candidate.recipe == truth),
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
                        "truth_generated": "NO",
                        "gdt525_rank": 0,
                        "gdt526_rank": 0,
                        "gdt525_top1": recipe_text(candidates[0].recipe) if candidates else "NONE",
                        "gdt526_top1": "NONE",
                        "truth_cha_feature": "NONE",
                        "top1_cha_feature": "NONE",
                        "truth_cha_trace": "NONE",
                        "top1_cha_trace": "NONE",
                    }
                )
                continue
            prediction = ridge.predict(surface)
            gdt524_scores, _ = G525.gdt524_fold_scores(
                surface, candidates, prediction, ridge, renderer_deck, boundaries,
                history, analogy, null_context, g522_missing, g522_weight,
                path_mode, path_weight,
            )
            gdt525_sets, _, _, _, _ = G525.chain_score_sets(
                surface, candidates, gdt524_scores, analogy, pair_model, g522_missing
            )
            base_scores = gdt525_sets[G525.SELECTED_STAGE]
            sets, features, traces, _ = score_sets(
                surface, candidates, base_scores, analogy, g522_missing
            )
            orders = {}
            for stage, _, _ in CONFIGS:
                rank, order = G519.rank_by_score(candidates, truth, sets[stage])
                rank_sets[stage].append(rank)
                orders[stage] = order
            base_top = orders["GDT525_BASE"][0]
            top = orders[SELECTED_STAGE][0]
            output.append(
                {
                    "fold": fold,
                    "surface": surface,
                    "truth_recipe": recipe_text(truth),
                    "truth_generated": "YES",
                    "gdt525_rank": rank_sets["GDT525_BASE"][-1],
                    "gdt526_rank": rank_sets[SELECTED_STAGE][-1],
                    "gdt525_top1": recipe_text(candidates[base_top].recipe),
                    "gdt526_top1": recipe_text(candidates[top].recipe),
                    "truth_cha_feature": f"{features[truth_index][selected_mode]:.9f}",
                    "top1_cha_feature": f"{features[top][selected_mode]:.9f}",
                    "truth_cha_trace": traces[truth_index],
                    "top1_cha_trace": traces[top],
                }
            )
    ladder = [
        metric_row("FOUR_FOLD_OLD26_SURFACE_REHEARSAL", config, rank_sets[config[0]])
        for config in CONFIGS
    ]
    return output, ladder


def current_benchmark(old, selected, targets):
    forms = G518.invariant_surface_recipes(old, "component_recipe")
    analogy = G522.train_analogy_model(forms)
    pair_model = G525.train_pair_model(forms)
    null_context = G523.train_null_context_model(forms)
    g522_missing, g522_weight, path_mode, path_weight = G524.selected_upstream_parameters()
    mappings, ridge, renderer_deck, boundaries, recipe_models = G521.build_base_models(
        old, "component_recipe", "GDT526_FULL_OLD26"
    )
    history = recipe_models[(G521.SELECTED_ORDER, G521.SELECTED_ALPHA)]
    bigram = G518.train_ngram(old, "source_statement_id", "component_recipe", order=2)
    trigram = G518.train_ngram(old, "source_statement_id", "component_recipe", order=3)
    occurrences = G518.selected_prose_occurrences(selected)
    rank_sets: dict[str, list[int]] = defaultdict(list)
    revised_rank_sets: dict[str, list[int]] = defaultdict(list)
    output = []
    candidate_rows = []
    route_rows = []
    selected_mode = next(row[1] for row in CONFIGS if row[0] == SELECTED_STAGE)
    for target in targets:
        surface = target["surface"]
        truth = G517.atoms(target["gdt516_context_recipe"])
        candidates = G517.parse_surface(
            surface, mappings, cap=G519.CANDIDATE_CAP, allow_f66r_local=True
        )
        prediction = ridge.predict(surface)
        matrix = G519.segment_matrix(
            surface, G519.needed_renderer_sequences(candidates, renderer_deck),
            renderer_deck,
        )
        gdt523_scores = []
        paths = []
        for index, candidate in enumerate(candidates):
            context_base, _, _, _ = G519.current_context_base_score(
                surface, candidate, index, prediction, ridge, bigram, trigram,
                occurrences,
            )
            anchor_cost, path = G520.alignment_path(surface, candidate.recipe, matrix)
            gdt520_score = G520.score_config(
                context_base + anchor_cost,
                len(path),
                boundaries.nll(surface, path),
                G520.SEGMENT_COUNT_WEIGHT,
                G520.BOUNDARY_WEIGHT,
            )
            gdt521_score = gdt520_score + G521.SELECTED_WEIGHT * history.mean_nll(
                candidate.recipe
            )
            analogy_bonus, _ = analogy.feature(surface, candidate.recipe, g522_missing)
            gdt522_score = gdt521_score - g522_weight * analogy_bonus
            path_values, _ = G523.path_features(surface, path, analogy, null_context)
            gdt523_scores.append(gdt522_score - path_weight * path_values[path_mode])
            paths.append(path)
        gdt524_sets, _, _, _ = G524.score_sets_for_candidates(
            surface, candidates, gdt523_scores, analogy, g522_missing
        )
        gdt525_sets, _, _, _, _ = G525.chain_score_sets(
            surface, candidates, gdt524_sets[G524.SELECTED_STAGE], analogy,
            pair_model, g522_missing,
        )
        base_scores = gdt525_sets[G525.SELECTED_STAGE]
        sets, features, traces, hits = score_sets(
            surface, candidates, base_scores, analogy, g522_missing
        )
        orders = {}
        for stage, _, _ in CONFIGS:
            rank, order = G519.rank_by_score(candidates, truth, sets[stage])
            rank_sets[stage].append(rank)
            orders[stage] = order
        truth_index = next(
            index for index, candidate in enumerate(candidates) if candidate.recipe == truth
        )
        revised_recipe = WORKING_REVISIONS.get(surface, recipe_text(truth))
        revised_index = next(
            index for index, candidate in enumerate(candidates)
            if recipe_text(candidate.recipe) == revised_recipe
        )
        for stage, _, _ in CONFIGS:
            revised_rank_sets[stage].append(orders[stage].index(revised_index) + 1)
        base_top = orders["GDT525_BASE"][0]
        top = orders[SELECTED_STAGE][0]
        base_rank = rank_sets["GDT525_BASE"][-1]
        selected_rank = rank_sets[SELECTED_STAGE][-1]
        if base_rank == 1 and selected_rank == 1:
            change = "GDT525_CORRECT_PRESERVED"
        elif base_rank != 1 and selected_rank == 1:
            change = "GDT525_ERROR_CORRECTED"
        elif base_rank == 1 and selected_rank != 1:
            change = "GDT525_CORRECT_LOST"
        elif candidates[base_top].recipe != candidates[top].recipe:
            change = "ERROR_CHANGED_STILL_WRONG"
        else:
            change = "GDT525_ERROR_UNCHANGED"
        output.append(
            {
                "surface": surface,
                "occurrence_count": target["occurrence_count"],
                "physical_pages": target["physical_pages"],
                "truth_recipe": recipe_text(truth),
                "revised_working_recipe": revised_recipe,
                "gdt525_rank": base_rank,
                "gdt525_revised_rank": revised_rank_sets["GDT525_BASE"][-1],
                "gdt525_top1": recipe_text(candidates[base_top].recipe),
                "gdt526_rank": selected_rank,
                "gdt526_revised_rank": revised_rank_sets[SELECTED_STAGE][-1],
                "gdt526_top1": recipe_text(candidates[top].recipe),
                "gdt526_top5": " | ".join(
                    recipe_text(candidates[index].recipe)
                    for index in orders[SELECTED_STAGE][:5]
                ),
                "truth_gdt525_score": f"{base_scores[truth_index]:.9f}",
                "truth_cha_feature": f"{features[truth_index][selected_mode]:.9f}",
                "truth_gdt526_score": f"{sets[SELECTED_STAGE][truth_index]:.9f}",
                "truth_cha_trace": traces[truth_index],
                "top1_gdt525_score": f"{base_scores[top]:.9f}",
                "top1_cha_feature": f"{features[top][selected_mode]:.9f}",
                "top1_gdt526_score": f"{sets[SELECTED_STAGE][top]:.9f}",
                "top1_cha_trace": traces[top],
                "top1_alignment_trace": G520.path_text(surface, paths[top]),
                "decision_change_class": change,
                "working_policy": "EXACT_CHA_STEM_PLUS_POSITIVE_UNSEEN_RIGHT_SUFFIX_CHANNEL",
            }
        )
        if selected_rank != 1 or candidates[base_top].recipe != candidates[top].recipe:
            for selected_candidate_rank, index in enumerate(orders[SELECTED_STAGE][:12], 1):
                candidate_rows.append(
                    {
                        "surface": surface,
                        "truth_recipe": recipe_text(truth),
                        "candidate_is_truth": "YES" if candidates[index].recipe == truth else "NO",
                        "gdt525_rank": orders["GDT525_BASE"].index(index) + 1,
                        "gdt526_rank": selected_candidate_rank,
                        "candidate_recipe": recipe_text(candidates[index].recipe),
                        "gdt525_score": f"{base_scores[index]:.9f}",
                        "cha_feature": f"{features[index][selected_mode]:.9f}",
                        "gdt526_score": f"{sets[SELECTED_STAGE][index]:.9f}",
                        "cha_trace": traces[index],
                    }
                )
        for index, hit in enumerate(hits):
            if hit is None:
                continue
            route_rows.append(
                {
                    "surface": surface,
                    "candidate_recipe": recipe_text(candidates[index].recipe),
                    "candidate_is_truth": "YES" if candidates[index].recipe == truth else "NO",
                    "gdt525_rank": orders["GDT525_BASE"].index(index) + 1,
                    "gdt526_rank": orders[SELECTED_STAGE].index(index) + 1,
                    "base_surface": CHA_SURFACE,
                    "base_recipe": recipe_text(CHA_RECIPE),
                    "suffix": hit["suffix"],
                    "atom_insert": hit["atom_insert"],
                    "signature_support": hit["support"],
                    "visible_condition_total": hit["total"],
                    "license_bonus": f"{hit['bonus']:.9f}",
                    "cha_feature": f"{features[index][selected_mode]:.9f}",
                    "trace": traces[index],
                }
            )
    ladder = [
        metric_row("CURRENT_159_OLD26_TO_NEW4", config, rank_sets[config[0]])
        for config in CONFIGS
    ]
    revised_ladder = [
        metric_row("CURRENT_159_FAMILY_REVISED", config, revised_rank_sets[config[0]])
        for config in CONFIGS
    ]
    return output, candidate_rows, route_rows, ladder, revised_ladder


def rank_metrics(rows, field):
    return G519.rank_metrics([int(row[field]) for row in rows])


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    old = read_tsv(G518.G407_RUNNING)
    selected = read_tsv(G518.G516_SELECTED)
    targets = read_tsv(G518.G516_NEW)
    rehearsal, old_ladder = fold_rehearsal(old)
    current, candidates, routes, current_ladder, revised_ladder = current_benchmark(
        old, selected, targets
    )
    rehearsal_fields = [
        "fold", "surface", "truth_recipe", "truth_generated", "gdt525_rank",
        "gdt526_rank", "gdt525_top1", "gdt526_top1", "truth_cha_feature",
        "top1_cha_feature", "truth_cha_trace", "top1_cha_trace",
    ]
    current_fields = [
        "surface", "occurrence_count", "physical_pages", "truth_recipe",
        "revised_working_recipe", "gdt525_rank", "gdt525_revised_rank",
        "gdt525_top1", "gdt526_rank", "gdt526_revised_rank", "gdt526_top1",
        "gdt526_top5", "truth_gdt525_score", "truth_cha_feature",
        "truth_gdt526_score", "truth_cha_trace", "top1_gdt525_score",
        "top1_cha_feature", "top1_gdt526_score", "top1_cha_trace",
        "top1_alignment_trace", "decision_change_class", "working_policy",
    ]
    write_tsv(OUT / "gdt526_1558_four_fold_cha_rehearsal.tsv", rehearsal, rehearsal_fields)
    write_tsv(OUT / "gdt526_159_cha_rerank.tsv", current, current_fields)
    write_tsv(
        OUT / "gdt526_candidate_score_atlas.tsv", candidates,
        [
            "surface", "truth_recipe", "candidate_is_truth", "gdt525_rank",
            "gdt526_rank", "candidate_recipe", "gdt525_score", "cha_feature",
            "gdt526_score", "cha_trace",
        ],
    )
    write_tsv(
        OUT / "gdt526_cha_route_atlas.tsv", routes,
        [
            "surface", "candidate_recipe", "candidate_is_truth", "gdt525_rank",
            "gdt526_rank", "base_surface", "base_recipe", "suffix",
            "atom_insert", "signature_support", "visible_condition_total",
            "license_bonus", "cha_feature", "trace",
        ],
    )
    write_tsv(
        OUT / "gdt526_model_ladder.tsv", old_ladder + current_ladder + revised_ladder,
        [
            "scope", "model_stage", "cha_feature", "cha_weight", "target_count",
            "truth_generated_count", "top1_exact_count", "top2_exact_count",
            "top3_exact_count", "top5_exact_count", "rank_sum",
            "deepest_truth_rank",
        ],
    )
    changed = [row for row in current if row["gdt525_top1"] != row["gdt526_top1"]]
    revised_remaining = [row for row in current if int(row["gdt526_revised_rank"]) != 1]
    write_tsv(OUT / "gdt526_changed_decision_atlas.tsv", changed, current_fields)
    write_tsv(OUT / "gdt526_revised_remaining_top1_error_atlas.tsv", revised_remaining, current_fields)
    transitions = Counter(row["decision_change_class"] for row in current)
    result = {
        "experiment_id": "GDT526",
        "status": "PASS_CHA_STEM_UNSEEN_RIGHT_EXTENSION_LICENSE",
        "claim_ceiling": "EXPLORATORY_CHA_STEM_EXTENSION__NO_CONFIRMED_LEXEME_OR_PLAINTEXT",
        "selected_policy": {
            "stage": SELECTED_STAGE,
            "feature": next(row[1] for row in CONFIGS if row[0] == SELECTED_STAGE),
            "weight": next(row[2] for row in CONFIGS if row[0] == SELECTED_STAGE),
            "base": "cha=CH+A_ADDR",
            "activation": "UNSEEN_RIGHT_SUFFIX_WITH_POSITIVE_RIGHT_VISIBLE_TO_ATOM_LICENSE",
            "conflict": "OLD_EXACT_CHA_EXTENSION_OVERRIDES_STEM_DEFAULT",
        },
        "old26_four_fold_gdt525_metrics": rank_metrics(rehearsal, "gdt525_rank"),
        "old26_four_fold_gdt526_metrics": rank_metrics(rehearsal, "gdt526_rank"),
        "current_inherited_gdt525_metrics": rank_metrics(current, "gdt525_rank"),
        "current_inherited_gdt526_metrics": rank_metrics(current, "gdt526_rank"),
        "current_revised_gdt525_metrics": rank_metrics(current, "gdt525_revised_rank"),
        "current_revised_gdt526_metrics": rank_metrics(current, "gdt526_revised_rank"),
        "current_decision_change_classes": dict(sorted(transitions.items())),
        "current_route_count": len(routes),
        "changed_surfaces": sorted(row["surface"] for row in changed),
        "revised_remaining_top1_error_count": len(revised_remaining),
        "guard": "LEARNED_CHA_STEM_DEFAULT__OLD_CONTRARY_EXTENSION_WINS__NO_TARGET_WHOLE_FORM_CARD",
    }
    write_json(OUT / "gdt526_result.json", result)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
