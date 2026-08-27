#!/usr/bin/env python3
"""Extend certified old stems by transparent terminal s, while auditing l."""

from __future__ import annotations

import csv
import importlib.util
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt527_right_edge_learned_stem_extension"
OUT = BASE / "artifacts"
G526_RUN = (
    ROOT / "experiments/yolo/gdt526_cha_intermediate_stem_extension/src/run.py"
)


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


G526 = load_module("gdt526_core_for_gdt527", G526_RUN)
G525 = G526.G525
G524 = G526.G524
G522 = G526.G522
G519 = G526.G519
G518 = G526.G518
G517 = G526.G517

ORIGINAL_CONFIGS = G526.CONFIGS
ORIGINAL_SELECTED_STAGE = G526.SELECTED_STAGE
ORIGINAL_SCORE_SETS = G526.score_sets
ORIGINAL_REVISIONS = G526.WORKING_REVISIONS
INTERNAL_BASE_STAGE = "GDT525_BASE"  # required by G526's reusable harness

# stage, feature, weight
CONFIGS = (
    (INTERNAL_BASE_STAGE, "BASE", 0.0),
    *((f"CERT_S_BP1_W{int(w * 100):03d}", "CERT_S_BP1", w)
      for w in (0.25, 0.50, 0.75, 1.00, 1.25, 1.50, 1.75, 2.00, 2.25, 2.50)),
    *((f"CERT_L_BP1_W{int(w * 100):03d}", "CERT_L_BP1", w)
      for w in (0.50, 1.00, 1.50, 2.00, 2.25, 2.50)),
    *((f"CERT_LS_BP1_W{int(w * 100):03d}", "CERT_LS_BP1", w)
      for w in (0.50, 1.00, 1.50, 2.00, 2.25, 2.50)),
    *((f"CERT_S_BON_W{int(w * 100):03d}", "CERT_S_BONUS", w)
      for w in (0.50, 1.00, 1.50, 2.00)),
    *((f"CERT_S_BIN_W{int(w * 100):03d}", "CERT_S_BINARY", w)
      for w in (0.50, 1.00, 1.50, 2.00)),
)
SELECTED_STAGE = "CERT_S_BP1_W050"
WORKING_REVISIONS = dict(G526.WORKING_REVISIONS)
WORKING_REVISIONS["keeol"] = "K+EE+OL"

CERTIFICATE_CACHE: dict[int, tuple[Counter, dict[str, list[dict]]]] = {}
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


def stem_certificates(analogy):
    key = id(analogy)
    if key in CERTIFICATE_CACHE:
        return CERTIFICATE_CACHE[key]
    recipe_carriers = Counter(analogy.forms.values())
    children: dict[str, list[dict]] = defaultdict(list)
    for child_surface, child_recipe in analogy.forms.items():
        if len(child_surface) < 2:
            continue
        base_surface = child_surface[:-1]
        if base_surface not in analogy.forms:
            continue
        for atom_insert, atom_position in G522.recipe_insertions(
            child_recipe, analogy.forms[base_surface]
        ):
            if atom_position != "RIGHT" or not atom_insert:
                continue
            children[base_surface].append(
                {
                    "child_surface": child_surface,
                    "visible_suffix": child_surface[-1],
                    "atom_insert": recipe_text(atom_insert),
                }
            )
    result = (recipe_carriers, dict(children))
    CERTIFICATE_CACHE[key] = result
    return result


def right_terminal_hit(surface, recipe, analogy, missing_cost):
    if surface in analogy.forms and analogy.forms[surface] != recipe:
        return None, "OLD_EXACT_TARGET_CONFLICT"
    if not surface.endswith(("l", "s")):
        return None, "NO_TRANSPARENT_LS_SUFFIX"
    suffix = surface[-1]
    expected_atom = ("L",) if suffix == "l" else ("S",)
    base_surface = surface[:-1]
    if len(base_surface) < 3 or base_surface not in analogy.forms:
        return None, "NO_OLD_PREFIX_STEM_LENGTH3"
    recipe_carriers, children = stem_certificates(analogy)
    base_recipe = analogy.forms[base_surface]
    carrier_surfaces = sorted(
        candidate
        for candidate, candidate_recipe in analogy.forms.items()
        if candidate_recipe == base_recipe
    )
    child_rows = children.get(base_surface, [])
    if len(carrier_surfaces) < 3 and not child_rows:
        return None, "STEM_NOT_CERTIFIED"
    hits = []
    for atom_insert, atom_position in G522.recipe_insertions(recipe, base_recipe):
        if atom_position != "RIGHT" or atom_insert != expected_atom:
            continue
        stats = G525.signature_bonus(
            analogy, (suffix, "RIGHT", atom_insert, "RIGHT"), missing_cost
        )
        if stats is None or stats[0] <= 0:
            continue
        bonus, support, total = stats
        hits.append((bonus, support, total, atom_insert))
    if not hits:
        return None, "NO_POSITIVE_TRANSPARENT_SUFFIX_LICENSE"
    bonus, support, total, atom_insert = max(
        hits, key=lambda row: (row[0], row[1], recipe_text(row[3]))
    )
    if len(carrier_surfaces) >= 3 and child_rows:
        certificate = "MULTI_RECIPE_CARRIERS_AND_RIGHT_CHILD"
    elif len(carrier_surfaces) >= 3:
        certificate = "MULTI_RECIPE_CARRIERS"
    else:
        certificate = "ONE_CHAR_NON_NULL_RIGHT_CHILD"
    hit = {
        "base_surface": base_surface,
        "base_recipe": recipe_text(base_recipe),
        "suffix": suffix,
        "atom_insert": recipe_text(atom_insert),
        "support": support,
        "total": total,
        "bonus": bonus,
        "recipe_carrier_count": len(carrier_surfaces),
        "recipe_carriers": " | ".join(carrier_surfaces),
        "right_child_count": len(child_rows),
        "right_children": " | ".join(
            f"{row['child_surface']}:{row['visible_suffix']}->{row['atom_insert']}"
            for row in child_rows
        ) or "NONE",
        "certificate": certificate,
    }
    trace = (
        f"{base_surface}={recipe_text(base_recipe)}+{suffix}=>{recipe_text(atom_insert)}"
        f"@RIGHT/RIGHT;n={support}/{total};b={bonus:.6f};cert={certificate}"
    )
    return hit, trace


def stem_features(surface, recipe, analogy, missing_cost):
    values = {
        "CERT_S_BP1": 0.0,
        "CERT_L_BP1": 0.0,
        "CERT_LS_BP1": 0.0,
        "CERT_S_BONUS": 0.0,
        "CERT_S_BINARY": 0.0,
    }
    hit, trace = right_terminal_hit(
        surface, recipe, analogy, missing_cost
    )
    if hit is None:
        return values, trace, None
    bonus_plus_one = 1.0 + hit["bonus"]
    values["CERT_LS_BP1"] = bonus_plus_one
    if hit["suffix"] == "s":
        values["CERT_S_BP1"] = bonus_plus_one
        values["CERT_S_BONUS"] = hit["bonus"]
        values["CERT_S_BINARY"] = 1.0
        return values, trace, hit
    values["CERT_L_BP1"] = bonus_plus_one
    return values, "L_ROUTE_DIAGNOSTIC_ONLY__" + trace, None


def patched_score_sets(surface, candidates, base_scores, analogy, missing_cost):
    global CAPTURE_ENABLED
    G526.CONFIGS = ORIGINAL_CONFIGS
    G526.SELECTED_STAGE = ORIGINAL_SELECTED_STAGE
    try:
        g526_sets, _, _, _ = ORIGINAL_SCORE_SETS(
            surface, candidates, base_scores, analogy, missing_cost
        )
    finally:
        G526.CONFIGS = CONFIGS
        G526.SELECTED_STAGE = SELECTED_STAGE
    inherited = g526_sets[ORIGINAL_SELECTED_STAGE]
    features = []
    traces = []
    hits = []
    for candidate in candidates:
        values, trace, hit = stem_features(
            surface, candidate.recipe, analogy, missing_cost
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
    output = []
    for row in rows:
        output.append(
            {
                "scope": row["scope"],
                "model_stage": (
                    "GDT526_BASE"
                    if row["model_stage"] == INTERNAL_BASE_STAGE
                    else row["model_stage"]
                ),
                "stem_feature": row["cha_feature"],
                "stem_weight": row["cha_weight"],
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
        )
    return output


def transformed_rehearsal(rows):
    return [
        {
            "fold": row["fold"],
            "surface": row["surface"],
            "truth_recipe": row["truth_recipe"],
            "truth_generated": row["truth_generated"],
            "gdt526_rank": row["gdt525_rank"],
            "gdt527_rank": row["gdt526_rank"],
            "gdt526_top1": row["gdt525_top1"],
            "gdt527_top1": row["gdt526_top1"],
            "truth_stem_feature": row["truth_cha_feature"],
            "top1_stem_feature": row["top1_cha_feature"],
            "truth_stem_trace": row["truth_cha_trace"],
            "top1_stem_trace": row["top1_cha_trace"],
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
                "gdt526_rank": row["gdt525_rank"],
                "gdt526_revised_rank": row["gdt525_revised_rank"],
                "gdt526_top1": row["gdt525_top1"],
                "gdt527_rank": row["gdt526_rank"],
                "gdt527_revised_rank": row["gdt526_revised_rank"],
                "gdt527_top1": row["gdt526_top1"],
                "gdt527_top5": row["gdt526_top5"],
                "truth_gdt526_score": row["truth_gdt525_score"],
                "truth_stem_feature": row["truth_cha_feature"],
                "truth_gdt527_score": row["truth_gdt526_score"],
                "truth_stem_trace": row["truth_cha_trace"],
                "top1_gdt526_score": row["top1_gdt525_score"],
                "top1_stem_feature": row["top1_cha_feature"],
                "top1_gdt527_score": row["top1_gdt526_score"],
                "top1_stem_trace": row["top1_cha_trace"],
                "top1_alignment_trace": row["top1_alignment_trace"],
                "decision_change_class": row["decision_change_class"].replace(
                    "GDT525", "GDT526"
                ),
                "working_policy": "CERTIFIED_OLD_STEM_PLUS_TRANSPARENT_RIGHT_S",
            }
        )
    return output


def transformed_candidates(rows):
    return [
        {
            "surface": row["surface"],
            "truth_recipe": row["truth_recipe"],
            "candidate_is_truth": row["candidate_is_truth"],
            "gdt526_rank": row["gdt525_rank"],
            "gdt527_rank": row["gdt526_rank"],
            "candidate_recipe": row["candidate_recipe"],
            "gdt526_score": row["gdt525_score"],
            "stem_feature": row["cha_feature"],
            "gdt527_score": row["gdt526_score"],
            "stem_trace": row["cha_trace"],
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


def ol_census(forms):
    rows = []
    for surface, recipe in forms.items():
        if not surface.endswith("ol"):
            continue
        if len(recipe) >= 2 and recipe[-2:] == ("O", "L"):
            category = "O_PLUS_L"
        elif recipe and recipe[-1] == "OL":
            category = "ATOMIC_OL"
        else:
            category = "OTHER"
        rows.append(
            {
                "surface": surface,
                "recipe": recipe_text(recipe),
                "terminal_class": category,
            }
        )
    return sorted(rows, key=lambda row: (row["terminal_class"], row["surface"]))


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
        G526.CONFIGS = ORIGINAL_CONFIGS
        G526.SELECTED_STAGE = ORIGINAL_SELECTED_STAGE
        G526.score_sets = ORIGINAL_SCORE_SETS
        G526.WORKING_REVISIONS = ORIGINAL_REVISIONS

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
                    "gdt526_rank": base_order.index(index) + 1,
                    "gdt527_rank": new_order.index(index) + 1,
                    **hit,
                    "stem_feature": f"{captured['features'][index]['CERT_S_BP1']:.9f}",
                    "trace": captured["traces"][index],
                }
            )

    changed = [
        row for row in current
        if row["gdt526_top1"] != row["gdt527_top1"]
    ]
    remaining = [
        row for row in current if int(row["gdt527_revised_rank"]) != 1
    ]
    forms = G518.invariant_surface_recipes(old, "component_recipe")
    ol_rows = ol_census(forms)
    ol_counts = Counter(row["terminal_class"] for row in ol_rows)
    revision_rows = [
        {
            "surface": "keeol",
            "inherited_recipe": "K+EE+O+L",
            "revised_recipe": "K+EE+OL",
            "gdt526_top1": next(
                row["gdt526_top1"] for row in current if row["surface"] == "keeol"
            ),
            "old_atomic_ol_surface_count": ol_counts["ATOMIC_OL"],
            "old_o_plus_l_surface_count": ol_counts["O_PLUS_L"],
            "reason": "ATOMIC_OL_PRECEDENCE_OVER_PRODUCTIVE_L",
        }
    ]

    old_scope = "FOUR_FOLD_OLD26_SURFACE_REHEARSAL"
    inherited_scope = "CURRENT_159_OLD26_TO_NEW4"
    revised_scope = "CURRENT_159_FAMILY_REVISED"
    old_base = metric_for(ladder, old_scope, "GDT526_BASE")
    old_new = metric_for(ladder, old_scope, SELECTED_STAGE)
    inherited_base = metric_for(ladder, inherited_scope, "GDT526_BASE")
    inherited_new = metric_for(ladder, inherited_scope, SELECTED_STAGE)
    revised_base = metric_for(ladder, revised_scope, "GDT526_BASE")
    revised_new = metric_for(ladder, revised_scope, SELECTED_STAGE)
    changes = Counter(row["decision_change_class"] for row in current)
    losses = changes["GDT526_CORRECT_LOST"]
    status = (
        "PASS_CERTIFIED_S_STEM_AND_ATOMIC_OL_REVISION"
        if old_new == old_base
        and inherited_new["top1_exact_count"] > inherited_base["top1_exact_count"]
        and losses == 0
        and ol_counts["ATOMIC_OL"] > ol_counts["O_PLUS_L"]
        else "FAIL_SELECTION_GATE"
    )
    result = {
        "experiment_id": "GDT527",
        "status": status,
        "claim_ceiling": "EXPLORATORY_CERTIFIED_STEM_EXTENSION_AND_WORKING_OL_REVISION__NO_CONFIRMED_LEXEME_OR_PLAINTEXT",
        "selected_policy": {
            "stage": SELECTED_STAGE,
            "feature": "CERT_S_BP1",
            "weight": 0.5,
            "suffix": "s->S",
            "stem_certificate": "RECIPE_HAS_AT_LEAST_3_OLD_SURFACES_OR_STEM_HAS_NON_NULL_ONE_CHAR_RIGHT_CHILD",
            "conflict": "OLD_EXACT_TARGET_RECIPE_OVERRIDES_STEM_DEFAULT",
        },
        "rejected_l_policy": {
            "reason": "VISIBLE_OL_IS_PREDOMINANTLY_ATOMIC_NOT_O_PLUS_L",
            "old_atomic_ol_surface_count": ol_counts["ATOMIC_OL"],
            "old_o_plus_l_surface_count": ol_counts["O_PLUS_L"],
            "working_revision": "keeol=K+EE+OL",
        },
        "old26_four_fold_gdt526_metrics": old_base,
        "old26_four_fold_gdt527_metrics": old_new,
        "current_inherited_gdt526_metrics": inherited_base,
        "current_inherited_gdt527_metrics": inherited_new,
        "current_revised_gdt526_metrics": revised_base,
        "current_revised_gdt527_metrics": revised_new,
        "current_decision_change_classes": dict(sorted(changes.items())),
        "changed_surfaces": [row["surface"] for row in changed],
        "working_revision_surfaces": ["keeol"],
        "revised_remaining_top1_error_count": len(remaining),
        "guard": "CERTIFIED_STEM_PLUS_TRANSPARENT_S__ATOMIC_OL_BLOCKS_PRODUCTIVE_L__NO_TARGET_WHOLE_FORM_SCORE_CARD",
    }

    write_tsv(
        OUT / "gdt527_1558_four_fold_right_stem_rehearsal.tsv",
        rehearsal,
        [
            "fold", "surface", "truth_recipe", "truth_generated",
            "gdt526_rank", "gdt527_rank", "gdt526_top1", "gdt527_top1",
            "truth_stem_feature", "top1_stem_feature", "truth_stem_trace",
            "top1_stem_trace",
        ],
    )
    write_tsv(
        OUT / "gdt527_159_right_stem_rerank.tsv",
        current,
        list(current[0]),
    )
    write_tsv(
        OUT / "gdt527_candidate_score_atlas.tsv",
        candidates,
        list(candidates[0]),
    )
    write_tsv(
        OUT / "gdt527_right_stem_route_atlas.tsv",
        route_rows,
        [
            "surface", "candidate_recipe", "candidate_is_truth",
            "gdt526_rank", "gdt527_rank", "base_surface", "base_recipe",
            "suffix", "atom_insert", "support", "total", "bonus",
            "recipe_carrier_count", "recipe_carriers", "right_child_count",
            "right_children", "certificate", "stem_feature", "trace",
        ],
    )
    write_tsv(
        OUT / "gdt527_changed_decision_atlas.tsv",
        changed,
        list(current[0]),
    )
    write_tsv(
        OUT / "gdt527_model_ladder.tsv",
        ladder,
        list(ladder[0]),
    )
    write_tsv(
        OUT / "gdt527_working_revision_atlas.tsv",
        revision_rows,
        list(revision_rows[0]),
    )
    write_tsv(
        OUT / "gdt527_old_ol_terminal_census.tsv",
        ol_rows,
        ["surface", "recipe", "terminal_class"],
    )
    write_tsv(
        OUT / "gdt527_revised_remaining_top1_error_atlas.tsv",
        remaining,
        list(current[0]),
    )
    write_json(OUT / "gdt527_result.json", result)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if status.startswith("PASS_") else 1


if __name__ == "__main__":
    raise SystemExit(main())
