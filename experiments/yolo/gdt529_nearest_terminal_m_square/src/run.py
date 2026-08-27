#!/usr/bin/env python3
"""Resolve terminal m through an old edit square plus an action-slot triad."""

from __future__ import annotations

import csv
import importlib.util
import json
import sys
from collections import Counter
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt529_nearest_terminal_m_square"
OUT = BASE / "artifacts"
G528_RUN = (
    ROOT / "experiments/yolo/gdt528_neighbor_certified_inner_d_null/src/run.py"
)


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


G528 = load_module("gdt528_core_for_gdt529", G528_RUN)
G527 = G528.G527
G526 = G528.G526
G522 = G528.G522
G519 = G528.G519
G518 = G528.G518
G517 = G528.G517

ORIGINAL_CONFIGS = G528.CONFIGS
ORIGINAL_SELECTED_STAGE = G528.SELECTED_STAGE
ORIGINAL_SCORE_SETS = G528.patched_score_sets
ORIGINAL_REVISIONS = G528.WORKING_REVISIONS
INTERNAL_BASE_STAGE = "GDT525_BASE"  # required by G526's reusable harness

CONFIGS = (
    (INTERNAL_BASE_STAGE, "BASE", 0.0),
    *((f"DUAL_M_SQUARE_BIN_W{round(w * 100):03d}", "DUAL_SQUARE_BINARY", w)
      for w in (0.50, 0.75, 1.00, 1.10, 1.20, 1.24, 1.25, 1.30, 1.50, 2.00)),
    *((f"NAIVE_M_SQUARE_BIN_W{round(w * 100):03d}", "NAIVE_NEAREST_BINARY", w)
      for w in (0.50, 0.75, 1.00, 1.25, 1.50, 2.00)),
)
SELECTED_STAGE = "DUAL_M_SQUARE_BIN_W125"
WORKING_REVISIONS = dict(G528.WORKING_REVISIONS)
ACTION_ROOTS = {"OK", "CH", "SH", "K", "S", "CHD", "T", "R", "P"}
M_TAGS = {"M_LOCAL", "AM_ADDR"}

PAIR_CACHE: dict[int, tuple[object, list[dict]]] = {}
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
        writer.writerows({field: row.get(field, "") for field in fields} for row in rows)


def write_json(path: Path, value: object) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def recipe_text(recipe) -> str:
    return G517.recipe_text(tuple(recipe))


def edit_distance(left: str, right: str) -> int:
    previous = list(range(len(right) + 1))
    for left_index, left_char in enumerate(left, start=1):
        current = [left_index]
        for right_index, right_char in enumerate(right, start=1):
            current.append(
                min(
                    current[-1] + 1,
                    previous[right_index] + 1,
                    previous[right_index - 1] + (left_char != right_char),
                )
            )
        previous = current
    return previous[-1]


def exact_terminal_m_pairs(analogy) -> list[dict]:
    cache_key = id(analogy)
    cached = PAIR_CACHE.get(cache_key)
    if cached is not None and cached[0] is analogy:
        return cached[1]
    rows = []
    for variant_surface, variant_recipe in analogy.forms.items():
        if not variant_surface.endswith("m") or len(variant_surface) < 2:
            continue
        base_surface = variant_surface[:-1]
        base_recipe = analogy.forms.get(base_surface)
        if base_recipe is None or len(variant_recipe) != len(base_recipe) + 1:
            continue
        if tuple(variant_recipe[:-1]) != tuple(base_recipe):
            continue
        atom = variant_recipe[-1]
        if atom not in M_TAGS:
            continue
        rows.append(
            {
                "base_surface": base_surface,
                "variant_surface": variant_surface,
                "base_recipe": recipe_text(base_recipe),
                "variant_recipe": recipe_text(variant_recipe),
                "terminal_atom": atom,
            }
        )
    rows.sort(key=lambda row: (row["base_surface"], row["variant_surface"]))
    PAIR_CACHE[cache_key] = (analogy, rows)
    return rows


def action_slot_family(base_surface: str, analogy):
    base_recipe = analogy.forms.get(base_surface)
    if not base_surface.endswith("o") or base_recipe is None:
        return None, "BASE_NOT_EXACT_O_FORM"
    if tuple(base_recipe[-1:]) != ("O",):
        return None, "BASE_RECIPE_NOT_TERMINAL_O"
    stem_surface = base_surface[:-1]
    stem_recipe = tuple(base_recipe[:-1])
    if len(stem_recipe) < 2 or sum(atom in ACTION_ROOTS for atom in stem_recipe) < 2:
        return None, "STEM_LACKS_TWO_ACTION_ROOTS"
    ol_surface = stem_surface + "ol"
    or_surface = stem_surface + "or"
    expected_ol = stem_recipe + ("OL",)
    expected_or = stem_recipe + ("OR",)
    if analogy.forms.get(ol_surface) != expected_ol:
        return None, "NO_EXACT_OL_SIBLING"
    if analogy.forms.get(or_surface) != expected_or:
        return None, "NO_EXACT_OR_SIBLING"
    return {
        "stem_surface": stem_surface,
        "stem_recipe": recipe_text(stem_recipe),
        "o_surface": base_surface,
        "o_recipe": recipe_text(base_recipe),
        "ol_surface": ol_surface,
        "ol_recipe": recipe_text(expected_ol),
        "or_surface": or_surface,
        "or_recipe": recipe_text(expected_or),
    }, "ACTION_O_OL_OR_TRIAD"


def nearest_m_square(surface: str, recipe, analogy, *, require_family: bool):
    if not surface.endswith("m") or len(surface) < 2:
        return None, "NO_TERMINAL_M"
    if surface in analogy.forms and analogy.forms[surface] != recipe:
        return None, "OLD_EXACT_TARGET_CONFLICT"
    base_surface = surface[:-1]
    base_recipe = analogy.forms.get(base_surface)
    if base_recipe is None:
        return None, "NO_EXACT_M_LESS_BASE"
    candidate_recipe = tuple(recipe)
    if (
        len(candidate_recipe) != len(base_recipe) + 1
        or candidate_recipe[:-1] != tuple(base_recipe)
        or candidate_recipe[-1] not in M_TAGS
    ):
        return None, "CANDIDATE_NOT_BASE_PLUS_ONE_M_TAG"
    family, family_reason = action_slot_family(base_surface, analogy)
    if require_family and family is None:
        return None, family_reason
    pairs = exact_terminal_m_pairs(analogy)
    if not pairs:
        return None, "NO_EXACT_TERMINAL_M_PAIRS"
    distances = [(edit_distance(base_surface, row["base_surface"]), row) for row in pairs]
    minimum = min(distance for distance, _ in distances)
    nearest = [row for distance, row in distances if distance == minimum]
    labels = {row["terminal_atom"] for row in nearest}
    if minimum != 1:
        return None, f"NEAREST_PAIR_DISTANCE_{minimum}_NOT_ONE"
    if len(labels) != 1:
        return None, "NEAREST_PAIR_LABEL_TIE"
    predicted_atom = next(iter(labels))
    if candidate_recipe[-1] != predicted_atom:
        return None, f"NEAREST_PAIR_PREDICTS_{predicted_atom}"
    hit = {
        "surface": surface,
        "base_surface": base_surface,
        "base_recipe": recipe_text(base_recipe),
        "candidate_recipe": recipe_text(candidate_recipe),
        "predicted_terminal_atom": predicted_atom,
        "nearest_distance": minimum,
        "nearest_pair_count": len(nearest),
        "certificate_bases": " | ".join(row["base_surface"] for row in nearest),
        "certificate_variants": " | ".join(row["variant_surface"] for row in nearest),
        "certificate_recipes": " | ".join(row["variant_recipe"] for row in nearest),
        "pair_inventory_size": len(pairs),
        "family_required": "YES" if require_family else "NO",
        "family_reason": family_reason,
        "family": family,
        # Compatibility keys consumed by G526's generic current harness.
        "suffix": "m",
        "atom_insert": predicted_atom,
        "support": len(nearest),
        "total": len(pairs),
        "bonus": 1.0,
    }
    return hit, "DUAL_CERTIFIED_M_SQUARE" if require_family else "NEAREST_M_SQUARE"


def square_features(surface, recipe, analogy):
    values = {"DUAL_SQUARE_BINARY": 0.0, "NAIVE_NEAREST_BINARY": 0.0}
    naive_hit, naive_reason = nearest_m_square(
        surface, recipe, analogy, require_family=False
    )
    dual_hit, dual_reason = nearest_m_square(
        surface, recipe, analogy, require_family=True
    )
    if naive_hit is not None:
        values["NAIVE_NEAREST_BINARY"] = 1.0
    if dual_hit is None:
        return values, dual_reason or naive_reason, None
    values["DUAL_SQUARE_BINARY"] = 1.0
    family = dual_hit["family"]
    trace = (
        f"{family['stem_surface']}={family['stem_recipe']}"
        f"[{family['o_surface']}/{family['ol_surface']}/{family['or_surface']}];"
        f"{dual_hit['certificate_bases']}->{dual_hit['certificate_variants']}"
        f" adds {dual_hit['predicted_terminal_atom']};"
        f"{dual_hit['base_surface']}->{surface}"
    )
    return values, trace, dual_hit


def patched_score_sets(surface, candidates, base_scores, analogy, missing_cost):
    global CAPTURE_ENABLED
    G526.CONFIGS = ORIGINAL_CONFIGS
    G526.SELECTED_STAGE = ORIGINAL_SELECTED_STAGE
    try:
        g528_sets, _, _, _ = ORIGINAL_SCORE_SETS(
            surface, candidates, base_scores, analogy, missing_cost
        )
    finally:
        G526.CONFIGS = CONFIGS
        G526.SELECTED_STAGE = SELECTED_STAGE
    inherited = g528_sets[ORIGINAL_SELECTED_STAGE]
    features = []
    traces = []
    hits = []
    for candidate in candidates:
        values, trace, hit = square_features(surface, candidate.recipe, analogy)
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
                "GDT528_BASE"
                if row["model_stage"] == INTERNAL_BASE_STAGE
                else row["model_stage"]
            ),
            "square_feature": row["cha_feature"],
            "square_weight": row["cha_weight"],
            **{
                field: row[field]
                for field in (
                    "target_count", "truth_generated_count", "top1_exact_count",
                    "top2_exact_count", "top3_exact_count", "top5_exact_count",
                    "rank_sum", "deepest_truth_rank",
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
            "gdt528_rank": row["gdt525_rank"],
            "gdt529_rank": row["gdt526_rank"],
            "gdt528_top1": row["gdt525_top1"],
            "gdt529_top1": row["gdt526_top1"],
            "truth_square_feature": row["truth_cha_feature"],
            "top1_square_feature": row["top1_cha_feature"],
            "truth_square_trace": row["truth_cha_trace"],
            "top1_square_trace": row["top1_cha_trace"],
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
                "gdt528_rank": row["gdt525_rank"],
                "gdt528_revised_rank": row["gdt525_revised_rank"],
                "gdt528_top1": row["gdt525_top1"],
                "gdt529_rank": row["gdt526_rank"],
                "gdt529_revised_rank": row["gdt526_revised_rank"],
                "gdt529_top1": row["gdt526_top1"],
                "gdt529_top5": row["gdt526_top5"],
                "truth_gdt528_score": row["truth_gdt525_score"],
                "truth_square_feature": row["truth_cha_feature"],
                "truth_gdt529_score": row["truth_gdt526_score"],
                "truth_square_trace": row["truth_cha_trace"],
                "top1_gdt528_score": row["top1_gdt525_score"],
                "top1_square_feature": row["top1_cha_feature"],
                "top1_gdt529_score": row["top1_gdt526_score"],
                "top1_square_trace": row["top1_cha_trace"],
                "top1_alignment_trace": row["top1_alignment_trace"],
                "decision_change_class": row["decision_change_class"].replace(
                    "GDT525", "GDT528"
                ),
                "working_policy": "ACTION_SLOT_TRIAD_PLUS_NEAREST_TERMINAL_M_EDIT_SQUARE",
            }
        )
    return output


def transformed_candidates(rows):
    return [
        {
            "surface": row["surface"],
            "truth_recipe": row["truth_recipe"],
            "candidate_is_truth": row["candidate_is_truth"],
            "gdt528_rank": row["gdt525_rank"],
            "gdt529_rank": row["gdt526_rank"],
            "candidate_recipe": row["candidate_recipe"],
            "gdt528_score": row["gdt525_score"],
            "square_feature": row["cha_feature"],
            "gdt529_score": row["gdt526_score"],
            "square_trace": row["cha_trace"],
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


def terminal_m_target_audit(targets, analogy):
    rows = []
    for target in targets:
        surface = target["surface"]
        if not surface.endswith("m"):
            continue
        truth = G517.atoms(target["gdt516_context_recipe"])
        base_surface = surface[:-1]
        base_recipe = analogy.forms.get(base_surface)
        family, family_reason = action_slot_family(base_surface, analogy)
        matching = []
        if base_recipe is not None:
            for atom in sorted(M_TAGS):
                candidate = tuple(base_recipe) + (atom,)
                hit, reason = nearest_m_square(
                    surface, candidate, analogy, require_family=True
                )
                if hit is not None:
                    matching.append((atom, hit, reason))
        rows.append(
            {
                "surface": surface,
                "truth_recipe": recipe_text(truth),
                "base_surface": base_surface,
                "base_recipe": recipe_text(base_recipe) if base_recipe else "NONE",
                "action_slot_family": "YES" if family else "NO",
                "family_reason": family_reason,
                "family_stem": family["stem_surface"] if family else "NONE",
                "licensed_atoms": " | ".join(atom for atom, _, _ in matching) or "NONE",
                "certificate_pairs": " | ".join(
                    f"{hit['certificate_bases']}->{hit['certificate_variants']}"
                    for _, hit, _ in matching
                ) or "NONE",
                "truth_licensed": (
                    "YES" if matching and truth[-1] in {atom for atom, _, _ in matching}
                    and tuple(truth[:-1]) == tuple(base_recipe or ()) else "NO"
                ),
            }
        )
    return rows


def prospective_action_slot_rows(analogy, current_surfaces: set[str]):
    rows = []
    for base_surface in sorted(analogy.forms):
        family, reason = action_slot_family(base_surface, analogy)
        if family is None:
            continue
        target_surface = base_surface + "m"
        base_recipe = analogy.forms[base_surface]
        matches = []
        for atom in sorted(M_TAGS):
            candidate = tuple(base_recipe) + (atom,)
            hit, _ = nearest_m_square(
                target_surface, candidate, analogy, require_family=True
            )
            if hit is not None:
                matches.append((atom, hit))
        rows.append(
            {
                "stem_surface": family["stem_surface"],
                "stem_recipe": family["stem_recipe"],
                "o_surface": family["o_surface"],
                "o_recipe": family["o_recipe"],
                "ol_surface": family["ol_surface"],
                "ol_recipe": family["ol_recipe"],
                "or_surface": family["or_surface"],
                "or_recipe": family["or_recipe"],
                "terminal_m_surface": target_surface,
                "current30_status": (
                    "VISIBLE_CURRENT30" if target_surface in current_surfaces else "ABSENT_CURRENT30"
                ),
                "predicted_terminal_atom": matches[0][0] if len(matches) == 1 else "UNRESOLVED",
                "predicted_recipe": (
                    recipe_text(tuple(base_recipe) + (matches[0][0],))
                    if len(matches) == 1 else "UNRESOLVED"
                ),
                "nearest_pair_bases": (
                    matches[0][1]["certificate_bases"] if len(matches) == 1 else "NONE"
                ),
                "nearest_pair_variants": (
                    matches[0][1]["certificate_variants"] if len(matches) == 1 else "NONE"
                ),
                "decision": "LICENSED" if len(matches) == 1 else "NO_ONE_EDIT_PAIR_CERTIFICATE",
                "family_reason": reason,
            }
        )
    return rows


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
        current_raw, candidates_raw, _, current_ladder_raw, revised_ladder_raw = (
            G526.current_benchmark(old, selected, targets)
        )
    finally:
        CAPTURE_ENABLED = False
        G526.CONFIGS = G527.ORIGINAL_CONFIGS
        G526.SELECTED_STAGE = G527.ORIGINAL_SELECTED_STAGE
        G526.score_sets = G527.ORIGINAL_SCORE_SETS
        G526.WORKING_REVISIONS = G527.ORIGINAL_REVISIONS

    rehearsal = transformed_rehearsal(rehearsal_raw)
    current = transformed_current(current_raw)
    candidates = transformed_candidates(candidates_raw)
    ladder = transformed_ladder(old_ladder_raw + current_ladder_raw + revised_ladder_raw)
    truth_by_surface = {
        row["surface"]: G517.atoms(row["gdt516_context_recipe"])
        for row in targets
    }
    route_rows = []
    for surface, captured in sorted(CURRENT_CAPTURE.items()):
        candidate_list = captured["candidates"]
        base_scores = captured["scores"][INTERNAL_BASE_STAGE]
        new_scores = captured["scores"][SELECTED_STAGE]
        base_order = sorted(range(len(candidate_list)), key=lambda i: (base_scores[i], i))
        new_order = sorted(range(len(candidate_list)), key=lambda i: (new_scores[i], i))
        for index, hit in enumerate(captured["hits"]):
            if hit is None:
                continue
            family = hit["family"]
            route_rows.append(
                {
                    "surface": surface,
                    "candidate_recipe": recipe_text(candidate_list[index].recipe),
                    "candidate_is_truth": (
                        "YES" if candidate_list[index].recipe == truth_by_surface[surface] else "NO"
                    ),
                    "gdt528_rank": base_order.index(index) + 1,
                    "gdt529_rank": new_order.index(index) + 1,
                    "base_surface": hit["base_surface"],
                    "base_recipe": hit["base_recipe"],
                    "stem_surface": family["stem_surface"],
                    "stem_recipe": family["stem_recipe"],
                    "o_surface": family["o_surface"],
                    "ol_surface": family["ol_surface"],
                    "or_surface": family["or_surface"],
                    "predicted_terminal_atom": hit["predicted_terminal_atom"],
                    "nearest_distance": hit["nearest_distance"],
                    "certificate_bases": hit["certificate_bases"],
                    "certificate_variants": hit["certificate_variants"],
                    "certificate_recipes": hit["certificate_recipes"],
                    "pair_inventory_size": hit["pair_inventory_size"],
                    "square_feature": f"{captured['features'][index]['DUAL_SQUARE_BINARY']:.9f}",
                    "trace": captured["traces"][index],
                }
            )

    changed = [row for row in current if row["gdt528_top1"] != row["gdt529_top1"]]
    remaining = [row for row in current if int(row["gdt529_revised_rank"]) != 1]
    forms = G518.invariant_surface_recipes(old, "component_recipe")
    full_analogy = G522.train_analogy_model(forms)
    pairs = exact_terminal_m_pairs(full_analogy)
    m_audit = terminal_m_target_audit(targets, full_analogy)
    current_surfaces = {row["surface"] for row in selected} | {row["surface"] for row in targets}
    prospective = prospective_action_slot_rows(full_analogy, current_surfaces)

    old_scope = "FOUR_FOLD_OLD26_SURFACE_REHEARSAL"
    inherited_scope = "CURRENT_159_OLD26_TO_NEW4"
    revised_scope = "CURRENT_159_FAMILY_REVISED"
    old_base = metric_for(ladder, old_scope, "GDT528_BASE")
    old_new = metric_for(ladder, old_scope, SELECTED_STAGE)
    inherited_base = metric_for(ladder, inherited_scope, "GDT528_BASE")
    inherited_new = metric_for(ladder, inherited_scope, SELECTED_STAGE)
    revised_base = metric_for(ladder, revised_scope, "GDT528_BASE")
    revised_new = metric_for(ladder, revised_scope, SELECTED_STAGE)
    naive_old = metric_for(ladder, old_scope, "NAIVE_M_SQUARE_BIN_W125")
    naive_current = metric_for(ladder, inherited_scope, "NAIVE_M_SQUARE_BIN_W125")
    changes = Counter(row["decision_change_class"] for row in current)
    status = (
        "PASS_ACTION_SLOT_TERMINAL_M_SQUARE"
        if old_new == old_base
        and inherited_new["top1_exact_count"] > inherited_base["top1_exact_count"]
        and changes["GDT528_CORRECT_LOST"] == 0
        and [row["surface"] for row in changed] == ["cthom"]
        and len(route_rows) == 1
        else "FAIL_SELECTION_GATE"
    )
    result = {
        "experiment_id": "GDT529",
        "status": status,
        "claim_ceiling": "EXPLORATORY_ACTION_SLOT_TERMINAL_M_SQUARE__NO_CONFIRMED_LEXEME_OR_PLAINTEXT",
        "selected_policy": {
            "stage": SELECTED_STAGE,
            "feature": "DUAL_SQUARE_BINARY",
            "weight": 1.25,
            "base": "EXACT_M_LESS_TERMINAL_O_FORM",
            "family_certificate": "TWO_ACTION_STEM_HAS_EXACT_O_OL_OR_RIGHT_SLOT_TRIAD",
            "edit_certificate": "NEAREST_EXACT_BASE_TO_BASE_PLUS_M_PAIR_IS_ONE_VISIBLE_EDIT_AWAY_AND_LABEL_UNANIMOUS",
            "candidate_relation": "BASE_RECIPE_PLUS_THE_CERTIFIED_M_TAG",
            "conflict": "OLD_EXACT_TARGET_RECIPE_OVERRIDES_SQUARE",
        },
        "naive_nearest_pair_comparator": {
            "stage": "NAIVE_M_SQUARE_BIN_W125",
            "missing_condition": "NO_TWO_ACTION_O_OL_OR_FAMILY_REQUIRED",
            "old26_metrics": naive_old,
            "current_metrics": naive_current,
        },
        "old_exact_terminal_m_pair_count": len(pairs),
        "old_action_slot_family_count": len(prospective),
        "licensed_action_slot_m_prediction_count": sum(
            row["decision"] == "LICENSED" for row in prospective
        ),
        "old26_four_fold_gdt528_metrics": old_base,
        "old26_four_fold_gdt529_metrics": old_new,
        "current_inherited_gdt528_metrics": inherited_base,
        "current_inherited_gdt529_metrics": inherited_new,
        "current_revised_gdt528_metrics": revised_base,
        "current_revised_gdt529_metrics": revised_new,
        "current_decision_change_classes": dict(sorted(changes.items())),
        "changed_surfaces": [row["surface"] for row in changed],
        "current_selected_route_count": len(route_rows),
        "revised_remaining_top1_error_count": len(remaining),
        "guard": "TWO_ACTION_O_OL_OR_TRIAD_AND_ONE_EDIT_TERMINAL_M_PAIR_REQUIRED__NO_GLOBAL_M_LOCAL_DEFAULT",
    }

    write_tsv(
        OUT / "gdt529_1558_four_fold_m_square_rehearsal.tsv",
        rehearsal,
        list(rehearsal[0]),
    )
    write_tsv(
        OUT / "gdt529_159_m_square_rerank.tsv", current, list(current[0])
    )
    write_tsv(
        OUT / "gdt529_candidate_score_atlas.tsv", candidates, list(candidates[0])
    )
    write_tsv(
        OUT / "gdt529_m_square_route_atlas.tsv",
        route_rows,
        [
            "surface", "candidate_recipe", "candidate_is_truth", "gdt528_rank",
            "gdt529_rank", "base_surface", "base_recipe", "stem_surface",
            "stem_recipe", "o_surface", "ol_surface", "or_surface",
            "predicted_terminal_atom", "nearest_distance", "certificate_bases",
            "certificate_variants", "certificate_recipes", "pair_inventory_size",
            "square_feature", "trace",
        ],
    )
    write_tsv(
        OUT / "gdt529_old_exact_terminal_m_pair_atlas.tsv",
        pairs,
        [
            "base_surface", "variant_surface", "base_recipe", "variant_recipe",
            "terminal_atom",
        ],
    )
    write_tsv(
        OUT / "gdt529_current_terminal_m_audit.tsv", m_audit, list(m_audit[0])
    )
    write_tsv(
        OUT / "gdt529_action_slot_prediction_atlas.tsv",
        prospective,
        list(prospective[0]),
    )
    write_tsv(
        OUT / "gdt529_changed_decision_atlas.tsv", changed, list(current[0])
    )
    write_tsv(
        OUT / "gdt529_model_ladder.tsv", ladder, list(ladder[0])
    )
    write_tsv(
        OUT / "gdt529_revised_remaining_top1_error_atlas.tsv",
        remaining,
        list(current[0]),
    )
    write_json(OUT / "gdt529_result.json", result)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if status.startswith("PASS_") else 1


if __name__ == "__main__":
    raise SystemExit(main())
