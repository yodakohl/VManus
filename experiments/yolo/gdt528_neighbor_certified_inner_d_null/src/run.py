#!/usr/bin/env python3
"""Transfer a terminal d-null variant through a one-substitution neighbour."""

from __future__ import annotations

import csv
import importlib.util
import json
import math
import sys
from collections import Counter
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt528_neighbor_certified_inner_d_null"
OUT = BASE / "artifacts"
G527_RUN = (
    ROOT / "experiments/yolo/gdt527_right_edge_learned_stem_extension/src/run.py"
)


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


G527 = load_module("gdt527_core_for_gdt528", G527_RUN)
G526 = G527.G526
G522 = G527.G522
G519 = G527.G519
G518 = G527.G518
G517 = G527.G517

ORIGINAL_CONFIGS = G527.CONFIGS
ORIGINAL_SELECTED_STAGE = G527.SELECTED_STAGE
ORIGINAL_SCORE_SETS = G527.patched_score_sets
ORIGINAL_REVISIONS = G527.WORKING_REVISIONS
INTERNAL_BASE_STAGE = "GDT525_BASE"

CONFIGS = (
    (INTERNAL_BASE_STAGE, "BASE", 0.0),
    *((f"TAIL_DNULL_LOG_W{round(w * 100):03d}", "TAIL_DNULL_LOG", w)
      for w in (0.25, 0.50, 0.75, 0.90, 1.00, 1.05, 1.10, 1.15, 1.20, 1.25)),
    *((f"TAIL_DNULL_BIN_W{round(w * 100):03d}", "TAIL_DNULL_BINARY", w)
      for w in (0.50, 1.00, 1.50, 2.00, 2.50, 3.00)),
    *((f"NAIVE_TAIL_DNULL_LOG_W{round(w * 100):03d}", "NAIVE_TAIL_DNULL_LOG", w)
      for w in (0.25, 0.50, 0.75, 0.90, 1.00, 1.05, 1.10, 1.15, 1.20, 1.25)),
    *((f"BROAD_DNULL_LOG_W{round(w * 100):03d}", "BROAD_DNULL_LOG", w)
      for w in (0.10, 0.25, 0.50, 1.00)),
)
SELECTED_STAGE = "TAIL_DNULL_LOG_W115"
WORKING_REVISIONS = dict(G527.WORKING_REVISIONS)
ACTION_ROOTS = {"OK", "CH", "SH", "K", "S", "CHD", "T", "R", "P"}

PAIR_CACHE: dict[int, tuple[object, tuple[list[dict], list[dict]]]] = {}
CAPTURE_ENABLED = False
CURRENT_CAPTURE: dict[str, dict] = {}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict], fields: list[str]) -> None:
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


def one_substitution(left: str, right: str) -> bool:
    return len(left) == len(right) and sum(a != b for a, b in zip(left, right)) == 1


def action_substitution(left_recipe, right_recipe):
    left = tuple(atom for atom in left_recipe if atom != "CARRIER_Q")
    right = tuple(atom for atom in right_recipe if atom != "CARRIER_Q")
    if len(left) != len(right):
        return None
    changes = [(a, b) for a, b in zip(left, right) if a != b]
    if (
        len(changes) != 1
        or changes[0][0] not in ACTION_ROOTS
        or changes[0][1] not in ACTION_ROOTS
    ):
        return None
    return f"{changes[0][0]}>{changes[0][1]}"


def exact_d_null_pairs(analogy):
    cache_key = id(analogy)
    cached = PAIR_CACHE.get(cache_key)
    if cached is not None and cached[0] is analogy:
        return cached[1]
    broad: dict[tuple[str, str], dict] = {}
    tail: dict[tuple[str, str], dict] = {}
    for big_surface, big_recipe in analogy.forms.items():
        for index, char in enumerate(big_surface):
            if char != "d" or G522.position(index, len(big_surface), 1) != "INNER":
                continue
            base_surface = big_surface[:index] + big_surface[index + 1 :]
            if (
                base_surface not in analogy.forms
                or analogy.forms[base_surface] != big_recipe
            ):
                continue
            row = {
                "base_surface": base_surface,
                "variant_surface": big_surface,
                "recipe": recipe_text(big_recipe),
                "d_index": index,
                "terminal_before_y": (
                    "YES"
                    if index == len(big_surface) - 2 and big_surface.endswith("dy")
                    else "NO"
                ),
            }
            broad[(base_surface, big_surface)] = row
            if row["terminal_before_y"] == "YES":
                tail[(base_surface, big_surface)] = row
    result = (
        [broad[pair_key] for pair_key in sorted(broad)],
        [tail[pair_key] for pair_key in sorted(tail)],
    )
    # Retain the model alongside the result so a recycled object id cannot hit
    # a cache entry built from a different leave-one-fold training model.
    PAIR_CACHE[cache_key] = (analogy, result)
    return result


def null_routes(
    surface, recipe, analogy, *, terminal_only: bool,
    require_action_substitution: bool = True,
):
    if surface in analogy.forms and analogy.forms[surface] != recipe:
        return [], "OLD_EXACT_TARGET_CONFLICT"
    broad_pairs, tail_pairs = exact_d_null_pairs(analogy)
    pairs = tail_pairs if terminal_only else broad_pairs
    routes = []
    indices = (
        [len(surface) - 2]
        if terminal_only and surface.endswith("dy") and len(surface) >= 3
        else range(1, max(1, len(surface) - 1))
    )
    for index in indices:
        if not 0 < index < len(surface) - 1 or surface[index] != "d":
            continue
        base_surface = surface[:index] + surface[index + 1 :]
        if (
            base_surface not in analogy.forms
            or analogy.forms[base_surface] != recipe
        ):
            continue
        certificates = []
        for row in pairs:
            action_change = action_substitution(
                recipe, G517.atoms(row["recipe"])
            )
            if (
                one_substitution(base_surface, row["base_surface"])
                and (not require_action_substitution or action_change is not None)
            ):
                certificates.append((row, action_change or "UNCONSTRAINED"))
        if not certificates:
            continue
        routes.append(
            {
                "base_surface": base_surface,
                "base_recipe": recipe_text(recipe),
                "d_index": index,
                "pair_support": len(pairs),
                "certificate_count": len(certificates),
                "certificate_bases": " | ".join(
                    row["base_surface"] for row, _ in certificates
                ),
                "certificate_variants": " | ".join(
                    row["variant_surface"] for row, _ in certificates
                ),
                "certificate_recipes": " | ".join(
                    row["recipe"] for row, _ in certificates
                ),
                "certificate_action_changes": " | ".join(
                    change for _, change in certificates
                ),
            }
        )
    return routes, "NO_ONE_SUBSTITUTION_EQUAL_RECIPE_D_NULL_NEIGHBOUR"


def null_features(surface, recipe, analogy):
    values = {
        "TAIL_DNULL_LOG": 0.0,
        "TAIL_DNULL_BINARY": 0.0,
        "NAIVE_TAIL_DNULL_LOG": 0.0,
        "BROAD_DNULL_LOG": 0.0,
    }
    tail_routes, tail_reason = null_routes(
        surface, recipe, analogy, terminal_only=True
    )
    broad_routes, broad_reason = null_routes(
        surface, recipe, analogy, terminal_only=False
    )
    naive_tail_routes, _ = null_routes(
        surface, recipe, analogy, terminal_only=True,
        require_action_substitution=False,
    )
    broad_pairs, tail_pairs = exact_d_null_pairs(analogy)
    if broad_routes:
        values["BROAD_DNULL_LOG"] = math.log1p(len(broad_pairs))
    if naive_tail_routes:
        values["NAIVE_TAIL_DNULL_LOG"] = math.log1p(len(tail_pairs))
    if not tail_routes:
        return values, tail_reason if tail_reason else broad_reason, None
    hit = max(
        tail_routes,
        key=lambda row: (
            row["certificate_count"],
            row["base_surface"],
            row["certificate_bases"],
        ),
    )
    feature = math.log1p(len(tail_pairs))
    values["TAIL_DNULL_LOG"] = feature
    values["TAIL_DNULL_BINARY"] = 1.0
    hit.update(
        {
            "feature": feature,
            # Compatibility names consumed by the GDT526 benchmark exporter.
            # They do not enter any score; GDT528 writes its own route atlas.
            "suffix": "d",
            "atom_insert": "NULL",
            "support": len(tail_pairs),
            "total": len(broad_pairs),
            "bonus": feature,
        }
    )
    trace = (
        f"{hit['base_surface']}=>{surface};recipe={hit['base_recipe']};"
        f"tail_d_null_pairs={len(tail_pairs)};neighbor="
        f"{hit['certificate_bases']}->{hit['certificate_variants']}"
    )
    return values, trace, hit


def patched_score_sets(surface, candidates, base_scores, analogy, missing_cost):
    global CAPTURE_ENABLED
    G526.CONFIGS = ORIGINAL_CONFIGS
    G526.SELECTED_STAGE = ORIGINAL_SELECTED_STAGE
    try:
        g527_sets, _, _, _ = ORIGINAL_SCORE_SETS(
            surface, candidates, base_scores, analogy, missing_cost
        )
    finally:
        G526.CONFIGS = CONFIGS
        G526.SELECTED_STAGE = SELECTED_STAGE
    inherited = g527_sets[ORIGINAL_SELECTED_STAGE]
    features = []
    traces = []
    hits = []
    for candidate in candidates:
        values, trace, hit = null_features(
            surface, candidate.recipe, analogy
        )
        features.append(values)
        traces.append(trace)
        hits.append(hit)
    output = {}
    for stage, mode, weight in CONFIGS:
        output[stage] = (
            list(inherited)
            if mode == "BASE"
            else [
                score - weight * values[mode]
                for score, values in zip(inherited, features)
            ]
        )
    if CAPTURE_ENABLED:
        CURRENT_CAPTURE[surface] = {
            "candidates": candidates,
            "scores": output,
            "features": features,
            "traces": traces,
            "hits": hits,
        }
    return output, features, traces, hits


def transformed_ladder(rows):
    return [
        {
            "scope": row["scope"],
            "model_stage": (
                "GDT527_BASE"
                if row["model_stage"] == INTERNAL_BASE_STAGE
                else row["model_stage"]
            ),
            "null_feature": row["cha_feature"],
            "null_weight": row["cha_weight"],
            **{
                field: row[field]
                for field in (
                    "target_count", "truth_generated_count",
                    "top1_exact_count", "top2_exact_count",
                    "top3_exact_count", "top5_exact_count", "rank_sum",
                    "deepest_truth_rank",
                )
            },
        }
        for row in rows
    ]


def transformed_rehearsal(rows):
    return [
        {
            "fold": row["fold"],
            "surface": row["surface"],
            "truth_recipe": row["truth_recipe"],
            "truth_generated": row["truth_generated"],
            "gdt527_rank": row["gdt525_rank"],
            "gdt528_rank": row["gdt526_rank"],
            "gdt527_top1": row["gdt525_top1"],
            "gdt528_top1": row["gdt526_top1"],
            "truth_null_feature": row["truth_cha_feature"],
            "top1_null_feature": row["top1_cha_feature"],
            "truth_null_trace": row["truth_cha_trace"],
            "top1_null_trace": row["top1_cha_trace"],
        }
        for row in rows
    ]


def transformed_current(rows):
    output = []
    for row in rows:
        output.append(
            {
                "surface": row["surface"],
                "occurrence_count": row["occurrence_count"],
                "physical_pages": row["physical_pages"],
                "truth_recipe": row["truth_recipe"],
                "revised_working_recipe": row["revised_working_recipe"],
                "gdt527_rank": row["gdt525_rank"],
                "gdt527_revised_rank": row["gdt525_revised_rank"],
                "gdt527_top1": row["gdt525_top1"],
                "gdt528_rank": row["gdt526_rank"],
                "gdt528_revised_rank": row["gdt526_revised_rank"],
                "gdt528_top1": row["gdt526_top1"],
                "gdt528_top5": row["gdt526_top5"],
                "truth_gdt527_score": row["truth_gdt525_score"],
                "truth_null_feature": row["truth_cha_feature"],
                "truth_gdt528_score": row["truth_gdt526_score"],
                "truth_null_trace": row["truth_cha_trace"],
                "top1_gdt527_score": row["top1_gdt525_score"],
                "top1_null_feature": row["top1_cha_feature"],
                "top1_gdt528_score": row["top1_gdt526_score"],
                "top1_null_trace": row["top1_cha_trace"],
                "top1_alignment_trace": row["top1_alignment_trace"],
                "decision_change_class": row["decision_change_class"].replace(
                    "GDT525", "GDT527"
                ),
                "working_policy": "ONE_SUBSTITUTION_NEIGHBOR_CERTIFIED_TERMINAL_D_NULL",
            }
        )
    return output


def transformed_candidates(rows):
    return [
        {
            "surface": row["surface"],
            "truth_recipe": row["truth_recipe"],
            "candidate_is_truth": row["candidate_is_truth"],
            "gdt527_rank": row["gdt525_rank"],
            "gdt528_rank": row["gdt526_rank"],
            "candidate_recipe": row["candidate_recipe"],
            "gdt527_score": row["gdt525_score"],
            "null_feature": row["cha_feature"],
            "gdt528_score": row["gdt526_score"],
            "null_trace": row["cha_trace"],
        }
        for row in rows
    ]


def metric_for(ladder, scope, stage):
    return next(
        {
            key: row[key]
            for key in (
                "target_count", "truth_generated_count", "top1_exact_count",
                "top2_exact_count", "top3_exact_count", "top5_exact_count",
                "rank_sum", "deepest_truth_rank",
            )
        }
        for row in ladder
        if row["scope"] == scope and row["model_stage"] == stage
    )


def current_d_route_audit(targets, forms, tail_pairs, broad_pairs):
    rows = []
    for target in targets:
        surface = target["surface"]
        truth = G517.atoms(target["gdt516_context_recipe"])
        for index, char in enumerate(surface):
            if char != "d" or G522.position(index, len(surface), 1) != "INNER":
                continue
            base = surface[:index] + surface[index + 1 :]
            if base not in forms:
                continue
            broad_cert = [
                row for row in broad_pairs
                if one_substitution(base, row["base_surface"])
            ]
            tail_cert = [
                row for row in tail_pairs
                if one_substitution(base, row["base_surface"])
            ]
            terminal = index == len(surface) - 2 and surface.endswith("dy")
            truth_equal = truth == forms[base]
            eligible = terminal and truth_equal and bool(tail_cert)
            rows.append(
                {
                    "surface": surface,
                    "base_surface": base,
                    "truth_recipe": recipe_text(truth),
                    "base_recipe": recipe_text(forms[base]),
                    "truth_equals_base": "YES" if truth_equal else "NO",
                    "d_before_terminal_y": "YES" if terminal else "NO",
                    "broad_neighbor_certificates": " | ".join(
                        row["base_surface"] for row in broad_cert
                    ) or "NONE",
                    "tail_neighbor_certificates": " | ".join(
                        row["base_surface"] for row in tail_cert
                    ) or "NONE",
                    "selected_eligible": "YES" if eligible else "NO",
                }
            )
    unique = {
        (row["surface"], row["base_surface"]): row for row in rows
    }
    return [unique[key] for key in sorted(unique)]


def main() -> int:
    global CAPTURE_ENABLED
    OUT.mkdir(parents=True, exist_ok=True)
    old = read_tsv(G518.G407_RUNNING)
    selected = read_tsv(G518.G516_SELECTED)
    targets = read_tsv(G518.G516_NEW)

    G526.CONFIGS = CONFIGS
    G526.SELECTED_STAGE = SELECTED_STAGE
    G526.score_sets = patched_score_sets
    G526.WORKING_REVISIONS = WORKING_REVISIONS
    try:
        rehearsal_raw, old_ladder_raw = G526.fold_rehearsal(old)
        CURRENT_CAPTURE.clear()
        CAPTURE_ENABLED = True
        (
            current_raw,
            candidates_raw,
            _,
            current_ladder_raw,
            revised_ladder_raw,
        ) = G526.current_benchmark(old, selected, targets)
    finally:
        CAPTURE_ENABLED = False
        G526.CONFIGS = G527.ORIGINAL_CONFIGS
        G526.SELECTED_STAGE = G527.ORIGINAL_SELECTED_STAGE
        G526.score_sets = G527.ORIGINAL_SCORE_SETS
        G526.WORKING_REVISIONS = G527.ORIGINAL_REVISIONS

    rehearsal = transformed_rehearsal(rehearsal_raw)
    current = transformed_current(current_raw)
    candidates = transformed_candidates(candidates_raw)
    ladder = transformed_ladder(
        old_ladder_raw + current_ladder_raw + revised_ladder_raw
    )
    truth_by_surface = {
        row["surface"]: G517.atoms(row["gdt516_context_recipe"])
        for row in targets
    }
    route_rows = []
    for surface, captured in sorted(CURRENT_CAPTURE.items()):
        candidate_list = captured["candidates"]
        base_scores = captured["scores"][INTERNAL_BASE_STAGE]
        new_scores = captured["scores"][SELECTED_STAGE]
        base_order = sorted(
            range(len(candidate_list)), key=lambda i: (base_scores[i], i)
        )
        new_order = sorted(
            range(len(candidate_list)), key=lambda i: (new_scores[i], i)
        )
        for index, hit in enumerate(captured["hits"]):
            if hit is None:
                continue
            route_rows.append(
                {
                    "surface": surface,
                    "candidate_recipe": recipe_text(candidate_list[index].recipe),
                    "candidate_is_truth": (
                        "YES"
                        if candidate_list[index].recipe == truth_by_surface[surface]
                        else "NO"
                    ),
                    "gdt527_rank": base_order.index(index) + 1,
                    "gdt528_rank": new_order.index(index) + 1,
                    **{
                        key: value
                        for key, value in hit.items()
                        if key not in {
                            "suffix", "atom_insert", "support", "total", "bonus"
                        }
                    },
                    "null_feature": f"{captured['features'][index]['TAIL_DNULL_LOG']:.9f}",
                    "trace": captured["traces"][index],
                }
            )

    changed = [
        row for row in current
        if row["gdt527_top1"] != row["gdt528_top1"]
    ]
    remaining = [
        row for row in current if int(row["gdt528_revised_rank"]) != 1
    ]
    forms = G518.invariant_surface_recipes(old, "component_recipe")
    full_analogy = G522.train_analogy_model(forms)
    broad_pairs, tail_pairs = exact_d_null_pairs(full_analogy)
    d_audit = current_d_route_audit(targets, forms, tail_pairs, broad_pairs)

    old_scope = "FOUR_FOLD_OLD26_SURFACE_REHEARSAL"
    inherited_scope = "CURRENT_159_OLD26_TO_NEW4"
    revised_scope = "CURRENT_159_FAMILY_REVISED"
    old_base = metric_for(ladder, old_scope, "GDT527_BASE")
    old_new = metric_for(ladder, old_scope, SELECTED_STAGE)
    inherited_base = metric_for(ladder, inherited_scope, "GDT527_BASE")
    inherited_new = metric_for(ladder, inherited_scope, SELECTED_STAGE)
    revised_base = metric_for(ladder, revised_scope, "GDT527_BASE")
    revised_new = metric_for(ladder, revised_scope, SELECTED_STAGE)
    naive_old = metric_for(
        ladder, old_scope, "NAIVE_TAIL_DNULL_LOG_W115"
    )
    naive_current = metric_for(
        ladder, inherited_scope, "NAIVE_TAIL_DNULL_LOG_W115"
    )
    changes = Counter(row["decision_change_class"] for row in current)
    status = (
        "PASS_NEIGHBOR_CERTIFIED_TERMINAL_D_NULL"
        if old_new == old_base
        and inherited_new["top1_exact_count"] > inherited_base["top1_exact_count"]
        and changes["GDT527_CORRECT_LOST"] == 0
        and [row["surface"] for row in changed] == ["qocthedy"]
        else "FAIL_SELECTION_GATE"
    )
    result = {
        "experiment_id": "GDT528",
        "status": status,
        "claim_ceiling": "EXPLORATORY_NEIGHBOR_CERTIFIED_TERMINAL_D_NULL_VARIANT__NO_CONFIRMED_LEXEME_OR_PLAINTEXT",
        "selected_policy": {
            "stage": SELECTED_STAGE,
            "feature": "TAIL_DNULL_LOG",
            "weight": 1.15,
            "visible_frame": "BASE_ENDING_Y_TO_VARIANT_ENDING_DY",
            "recipe_relation": "EXACT_EQUAL_RECIPE",
            "certificate": "AN_OLD_EXACT_EQUAL_RECIPE_D_NULL_BASE_DIFFERS_BY_EXACTLY_ONE_SUBSTITUTION",
            "recipe_neighbor": "AFTER_REMOVING_CARRIER_Q_THE_RECIPES_DIFFER_BY_EXACTLY_ONE_KNOWN_ACTION_ROOT",
            "conflict": "OLD_EXACT_TARGET_RECIPE_OVERRIDES_VARIANT_DEFAULT",
        },
        "rejected_naive_visible_neighbor": {
            "stage": "NAIVE_TAIL_DNULL_LOG_W115",
            "missing_condition": "NO_RECIPE_LEVEL_ACTION_SUBSTITUTION_REQUIRED",
            "old26_metrics": naive_old,
            "current_metrics": naive_current,
            "reason": "CURRENT_GAIN_COSTS_ONE_OLD_TOP2_SLOT_AND_ONE_RANK_SUM_POINT",
        },
        "old_exact_inner_d_null_pair_count": len(broad_pairs),
        "old_exact_terminal_d_null_pair_count": len(tail_pairs),
        "old26_four_fold_gdt527_metrics": old_base,
        "old26_four_fold_gdt528_metrics": old_new,
        "current_inherited_gdt527_metrics": inherited_base,
        "current_inherited_gdt528_metrics": inherited_new,
        "current_revised_gdt527_metrics": revised_base,
        "current_revised_gdt528_metrics": revised_new,
        "current_decision_change_classes": dict(sorted(changes.items())),
        "changed_surfaces": [row["surface"] for row in changed],
        "current_selected_route_count": len(route_rows),
        "revised_remaining_top1_error_count": len(remaining),
        "guard": "TERMINAL_D_NULL_VARIANT_ONLY__ONE_SUBSTITUTION_OLD_NEIGHBOR_REQUIRED__NO_GLOBAL_D_OR_Q_NULL",
    }

    write_tsv(
        OUT / "gdt528_1558_four_fold_d_null_rehearsal.tsv",
        rehearsal,
        list(rehearsal[0]),
    )
    write_tsv(
        OUT / "gdt528_159_d_null_rerank.tsv",
        current,
        list(current[0]),
    )
    write_tsv(
        OUT / "gdt528_candidate_score_atlas.tsv",
        candidates,
        list(candidates[0]),
    )
    write_tsv(
        OUT / "gdt528_d_null_route_atlas.tsv",
        route_rows,
        [
            "surface", "candidate_recipe", "candidate_is_truth",
            "gdt527_rank", "gdt528_rank", "base_surface", "base_recipe",
            "d_index", "pair_support", "certificate_count",
            "certificate_bases", "certificate_variants",
            "certificate_recipes", "certificate_action_changes", "feature",
            "null_feature", "trace",
        ],
    )
    write_tsv(
        OUT / "gdt528_old_exact_d_null_pair_atlas.tsv",
        broad_pairs,
        ["base_surface", "variant_surface", "recipe", "d_index", "terminal_before_y"],
    )
    write_tsv(
        OUT / "gdt528_current_d_route_audit.tsv",
        d_audit,
        list(d_audit[0]),
    )
    write_tsv(
        OUT / "gdt528_changed_decision_atlas.tsv",
        changed,
        list(current[0]),
    )
    write_tsv(
        OUT / "gdt528_model_ladder.tsv",
        ladder,
        list(ladder[0]),
    )
    write_tsv(
        OUT / "gdt528_revised_remaining_top1_error_atlas.tsv",
        remaining,
        list(current[0]),
    )
    write_json(OUT / "gdt528_result.json", result)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if status.startswith("PASS_") else 1


if __name__ == "__main__":
    raise SystemExit(main())
