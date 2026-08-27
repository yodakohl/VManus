#!/usr/bin/env python3
"""Add short atom-history composition licenses to the GDT520 candidate score."""

from __future__ import annotations

import csv
import importlib.util
import json
import math
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt521_short_recipe_tail_license_reranker"
OUT = BASE / "artifacts"
G520_RUN = ROOT / "experiments/yolo/gdt520_renderer_boundary_license_lattice/src/run.py"

SELECTED_ORDER = 5
SELECTED_ALPHA = 0.5
SELECTED_WEIGHT = 0.5

MODEL_CONFIGS = (
    ("GDT520_BASE", 0, 0.0, 0.0),
    ("ORDER2_A05_W02", 2, 0.5, 0.2),
    ("ORDER3_A05_W02", 3, 0.5, 0.2),
    ("ORDER4_A05_W03", 4, 0.5, 0.3),
    ("ORDER5_A05_W01", 5, 0.5, 0.1),
    ("ORDER5_A05_W03", 5, 0.5, 0.3),
    ("GDT521_SELECTED", SELECTED_ORDER, SELECTED_ALPHA, SELECTED_WEIGHT),
    ("ORDER5_A05_W10", 5, 0.5, 1.0),
    ("ORDER5_A10_W05", 5, 1.0, 0.5),
)


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


G520 = load_module("gdt520_core_for_gdt521", G520_RUN)
G519 = G520.G519
G518 = G520.G518
G517 = G520.G517


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


@dataclass
class RecipeNgramModel:
    order: int
    alpha: float
    counts: Counter[tuple[str, ...]]
    histories: Counter[tuple[str, ...]]
    vocabulary: tuple[str, ...]
    training_surface_count: int

    def probability(self, history: tuple[str, ...], token: str) -> float:
        return (
            self.counts[history + (token,)] + self.alpha
        ) / (
            self.histories[history] + self.alpha * len(self.vocabulary)
        )

    def mean_nll(self, recipe: tuple[str, ...]) -> float:
        tokens = ["<S>"] * (self.order - 1) + list(recipe) + ["<E>"]
        costs = []
        for index in range(self.order - 1, len(tokens)):
            history = tuple(tokens[index - self.order + 1:index])
            costs.append(-math.log(self.probability(history, tokens[index])))
        return sum(costs) / len(costs) if costs else 0.0

    def atlas_rows(self) -> list[dict[str, object]]:
        rows = []
        for key in sorted(self.counts):
            history = key[:-1]
            token = key[-1]
            rows.append(
                {
                    "order": self.order,
                    "alpha": self.alpha,
                    "history": "+".join(history),
                    "next_atom": token,
                    "support": self.counts[key],
                    "history_total": self.histories[history],
                    "vocabulary_count": len(self.vocabulary),
                    "smoothed_probability": f"{self.probability(history, token):.9f}",
                }
            )
        return rows


def train_recipe_ngram(
    rows: list[dict[str, str]], recipe_field: str, order: int, alpha: float
) -> RecipeNgramModel:
    forms = G518.invariant_surface_recipes(rows, recipe_field)
    recipes = list(forms.values())
    vocabulary = tuple(sorted({atom for recipe in recipes for atom in recipe} | {"<E>"}))
    counts: Counter[tuple[str, ...]] = Counter()
    histories: Counter[tuple[str, ...]] = Counter()
    for recipe in recipes:
        tokens = ["<S>"] * (order - 1) + list(recipe) + ["<E>"]
        for index in range(order - 1, len(tokens)):
            history = tuple(tokens[index - order + 1:index])
            counts[history + (tokens[index],)] += 1
            histories[history] += 1
    return RecipeNgramModel(
        order, alpha, counts, histories, vocabulary, len(forms)
    )


def train_models(rows: list[dict[str, str]], recipe_field: str):
    keys = {(order, alpha) for _, order, alpha, _ in MODEL_CONFIGS if order}
    return {
        key: train_recipe_ngram(rows, recipe_field, key[0], key[1])
        for key in sorted(keys)
    }


def score_config(base_score: float, recipe: tuple[str, ...], config, models) -> tuple[float, float]:
    _, order, alpha, weight = config
    if not order:
        return base_score, 0.0
    nll = models[(order, alpha)].mean_nll(recipe)
    return base_score + weight * nll, nll


def metric_row(scope: str, config, ranks: list[int]) -> dict[str, object]:
    stage, order, alpha, weight = config
    return {
        "scope": scope,
        "model_stage": stage,
        "ngram_order": order,
        "alpha": alpha,
        "ngram_weight": weight,
        **G519.rank_metrics(ranks),
    }


def build_base_models(training: list[dict[str, str]], recipe_field: str, name: str):
    compiler = G517.build_model(name, training, recipe_field)
    mappings = G517.retained_mappings(compiler.evidence)
    ridge = G518.train_surface_ridge(training, recipe_field)
    deck, _ = G519.build_anchor_deck(
        compiler, G519.model_atoms(training, recipe_field), name
    )
    boundaries = G520.train_boundary_model(training, recipe_field, deck)
    recipe_models = train_models(training, recipe_field)
    return mappings, ridge, deck, boundaries, recipe_models


def fold_rehearsal(old: list[dict[str, str]]):
    forms = G518.invariant_surface_recipes(old, "component_recipe")
    output: list[dict[str, object]] = []
    ranks: dict[str, list[int]] = defaultdict(list)
    for fold in range(G520.FOLD_COUNT):
        held = {surface for surface in forms if G520.stable_fold(surface) == fold}
        training = [row for row in old if row["surface"] not in held]
        mappings, ridge, deck, boundaries, recipe_models = build_base_models(
            training, "component_recipe", f"FOLD_{fold}_TRAIN"
        )
        for surface in sorted(held):
            truth = forms[surface]
            candidates = G517.parse_surface(surface, mappings, cap=G519.CANDIDATE_CAP)
            truth_index = next(
                (index for index, candidate in enumerate(candidates) if candidate.recipe == truth),
                None,
            )
            if truth_index is None:
                for stage, _, _, _ in MODEL_CONFIGS:
                    ranks[stage].append(0)
                output.append(
                    {
                        "fold": fold,
                        "surface": surface,
                        "truth_recipe": G517.recipe_text(truth),
                        "candidate_count_capped": len(candidates),
                        "truth_generated": "NO",
                        "gdt520_rank": 0,
                        "gdt521_rank": 0,
                        "gdt520_top1": G517.recipe_text(candidates[0].recipe) if candidates else "NONE",
                        "gdt521_top1": "NONE",
                        "truth_order5_nll": "NONE",
                        "top1_order5_nll": "NONE",
                    }
                )
                continue
            prediction = ridge.predict(surface)
            matrix = G519.segment_matrix(
                surface, G519.needed_renderer_sequences(candidates, deck), deck
            )
            base_scores = []
            nlls: dict[tuple[int, float], list[float]] = defaultdict(list)
            for index, candidate in enumerate(candidates):
                anchor_cost, path = G520.alignment_path(surface, candidate.recipe, matrix)
                gdt519_score = (
                    ridge.squared_cost(prediction, candidate.recipe)
                    + math.log1p(index)
                    + anchor_cost
                )
                base_scores.append(
                    G520.score_config(
                        gdt519_score,
                        len(path),
                        boundaries.nll(surface, path),
                        G520.SEGMENT_COUNT_WEIGHT,
                        G520.BOUNDARY_WEIGHT,
                    )
                )
                for key, model in recipe_models.items():
                    nlls[key].append(model.mean_nll(candidate.recipe))
            orders = {}
            for config in MODEL_CONFIGS:
                stage, order, alpha, weight = config
                scores = (
                    base_scores
                    if not order
                    else [
                        base + weight * nll
                        for base, nll in zip(base_scores, nlls[(order, alpha)])
                    ]
                )
                rank, order_indices = G519.rank_by_score(candidates, truth, scores)
                ranks[stage].append(rank)
                orders[stage] = order_indices
            selected_top = orders["GDT521_SELECTED"][0]
            output.append(
                {
                    "fold": fold,
                    "surface": surface,
                    "truth_recipe": G517.recipe_text(truth),
                    "candidate_count_capped": len(candidates),
                    "truth_generated": "YES",
                    "gdt520_rank": ranks["GDT520_BASE"][-1],
                    "gdt521_rank": ranks["GDT521_SELECTED"][-1],
                    "gdt520_top1": G517.recipe_text(candidates[orders["GDT520_BASE"][0]].recipe),
                    "gdt521_top1": G517.recipe_text(candidates[selected_top].recipe),
                    "truth_order5_nll": f"{nlls[(SELECTED_ORDER, SELECTED_ALPHA)][truth_index]:.9f}",
                    "top1_order5_nll": f"{nlls[(SELECTED_ORDER, SELECTED_ALPHA)][selected_top]:.9f}",
                }
            )
    ladder = [
        metric_row("FOUR_FOLD_OLD26_SURFACE_REHEARSAL", config, ranks[config[0]])
        for config in MODEL_CONFIGS
    ]
    return output, ladder


def current_benchmark(old, selected, targets):
    mappings, ridge, deck, boundaries, recipe_models = build_base_models(
        old, "component_recipe", "FULL_OLD26"
    )
    bigram = G518.train_ngram(old, "source_statement_id", "component_recipe", order=2)
    trigram = G518.train_ngram(old, "source_statement_id", "component_recipe", order=3)
    occurrences = G518.selected_prose_occurrences(selected)
    output: list[dict[str, object]] = []
    candidate_rows: list[dict[str, object]] = []
    ranks: dict[str, list[int]] = defaultdict(list)
    for target in targets:
        surface = target["surface"]
        truth = G517.atoms(target["gdt516_context_recipe"])
        candidates = G517.parse_surface(
            surface, mappings, cap=G519.CANDIDATE_CAP, allow_f66r_local=True
        )
        prediction = ridge.predict(surface)
        matrix = G519.segment_matrix(
            surface, G519.needed_renderer_sequences(candidates, deck), deck
        )
        values = []
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
            anchor_cost, path = G520.alignment_path(surface, candidate.recipe, matrix)
            gdt520_score = G520.score_config(
                context_base + anchor_cost,
                len(path),
                boundaries.nll(surface, path),
                G520.SEGMENT_COUNT_WEIGHT,
                G520.BOUNDARY_WEIGHT,
            )
            values.append(
                {
                    "candidate": candidate,
                    "compiler_rank": index + 1,
                    "gdt520_score": gdt520_score,
                    "path": path,
                    "selected_nll": recipe_models[(SELECTED_ORDER, SELECTED_ALPHA)].mean_nll(candidate.recipe),
                    "all_nll": {
                        key: model.mean_nll(candidate.recipe)
                        for key, model in recipe_models.items()
                    },
                }
            )
        orders = {}
        scores_by_stage = {}
        for config in MODEL_CONFIGS:
            stage, order, alpha, weight = config
            scores = [
                float(value["gdt520_score"])
                + (weight * float(value["all_nll"][(order, alpha)]) if order else 0.0)
                for value in values
            ]
            rank, order_indices = G519.rank_by_score(candidates, truth, scores)
            ranks[stage].append(rank)
            orders[stage] = order_indices
            scores_by_stage[stage] = scores
        truth_index = next(
            index for index, candidate in enumerate(candidates) if candidate.recipe == truth
        )
        base_top = orders["GDT520_BASE"][0]
        top = orders["GDT521_SELECTED"][0]
        base_correct = ranks["GDT520_BASE"][-1] == 1
        selected_correct = ranks["GDT521_SELECTED"][-1] == 1
        if base_correct and selected_correct:
            change = "GDT520_CORRECT_PRESERVED"
        elif not base_correct and selected_correct:
            change = "GDT520_ERROR_CORRECTED"
        elif base_correct and not selected_correct:
            change = "GDT520_CORRECT_LOST"
        elif candidates[base_top].recipe != candidates[top].recipe:
            change = "ERROR_CHANGED_STILL_WRONG"
        else:
            change = "GDT520_ERROR_UNCHANGED"
        truth_value = values[truth_index]
        top_value = values[top]
        output.append(
            {
                "surface": surface,
                "occurrence_count": target["occurrence_count"],
                "physical_pages": target["physical_pages"],
                "truth_recipe": G517.recipe_text(truth),
                "candidate_count_capped": len(candidates),
                "gdt520_rank": ranks["GDT520_BASE"][-1],
                "gdt520_top1": G517.recipe_text(candidates[base_top].recipe),
                "gdt521_rank": ranks["GDT521_SELECTED"][-1],
                "gdt521_top1": G517.recipe_text(candidates[top].recipe),
                "gdt521_top5": " | ".join(
                    G517.recipe_text(candidates[index].recipe)
                    for index in orders["GDT521_SELECTED"][:5]
                ),
                "truth_gdt520_score": f"{float(truth_value['gdt520_score']):.9f}",
                "truth_order5_nll": f"{float(truth_value['selected_nll']):.9f}",
                "truth_gdt521_score": f"{scores_by_stage['GDT521_SELECTED'][truth_index]:.9f}",
                "truth_alignment_trace": G520.path_text(surface, truth_value["path"]),
                "top1_gdt520_score": f"{float(top_value['gdt520_score']):.9f}",
                "top1_order5_nll": f"{float(top_value['selected_nll']):.9f}",
                "top1_gdt521_score": f"{scores_by_stage['GDT521_SELECTED'][top]:.9f}",
                "top1_alignment_trace": G520.path_text(surface, top_value["path"]),
                "decision_change_class": change,
                "working_policy": "KNOWN_EVENT_OR_SURFACE_RECIPE_STILL_WINS__SHORT_ATOM_HISTORY_RERANKS_ONLY_FINITE_UNKNOWN_CANDIDATES",
            }
        )
        if ranks["GDT521_SELECTED"][-1] != 1 or candidates[base_top].recipe != candidates[top].recipe:
            for selected_rank, index in enumerate(orders["GDT521_SELECTED"][:12], 1):
                value = values[index]
                candidate_rows.append(
                    {
                        "surface": surface,
                        "truth_recipe": G517.recipe_text(truth),
                        "candidate_is_truth": "YES" if candidates[index].recipe == truth else "NO",
                        "gdt517_compiler_rank": value["compiler_rank"],
                        "gdt520_rank": orders["GDT520_BASE"].index(index) + 1,
                        "gdt521_rank": selected_rank,
                        "candidate_recipe": G517.recipe_text(candidates[index].recipe),
                        "gdt520_score": f"{float(value['gdt520_score']):.9f}",
                        "order5_nll": f"{float(value['selected_nll']):.9f}",
                        "gdt521_score": f"{scores_by_stage['GDT521_SELECTED'][index]:.9f}",
                        "alignment_trace": G520.path_text(surface, value["path"]),
                    }
                )
    ladder = [
        metric_row("CURRENT_159_OLD26_TO_NEW4", config, ranks[config[0]])
        for config in MODEL_CONFIGS
    ]
    return output, candidate_rows, ladder, recipe_models[(SELECTED_ORDER, SELECTED_ALPHA)]


TAIL_FAMILIES = {
    "O_CLOSE": (
        ("O", "DY"),
        ("O", "D_ADDR", "Y"),
        ("O", "Y"),
    ),
    "OL_CLOSE": (("OL",), ("O", "L")),
    "D_IIN_R": (("D_ADDR", "IIN", "R"), ("D_ADDR", "AIIN", "R")),
    "S_IIN_S": (
        ("S", "IIN", "S"),
        ("S", "A_ADDR", "IIN", "S"),
        ("S", "AIIN", "S"),
    ),
}


def tail_family_rows(old: list[dict[str, str]]) -> list[dict[str, object]]:
    forms = G518.invariant_surface_recipes(old, "component_recipe")
    event_counts = Counter(
        (row["surface"], G517.atoms(row["component_recipe"])) for row in old
    )
    output = []
    for family, options in TAIL_FAMILIES.items():
        for option in options:
            surfaces = [
                surface for surface, recipe in forms.items()
                if len(recipe) >= len(option) and recipe[-len(option):] == option
            ]
            output.append(
                {
                    "family": family,
                    "tail_recipe": G517.recipe_text(option),
                    "old_surface_type_count": len(surfaces),
                    "old_event_count": sum(
                        event_counts[(surface, forms[surface])] for surface in surfaces
                    ),
                    "example_surfaces": " | ".join(sorted(surfaces)[:12]) or "NONE",
                }
            )
    return output


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    old = read_tsv(G518.G407_RUNNING)
    selected = read_tsv(G518.G516_SELECTED)
    targets = read_tsv(G518.G516_NEW)
    rehearsal, rehearsal_ladder = fold_rehearsal(old)
    current, candidates, current_ladder, selected_model = current_benchmark(
        old, selected, targets
    )

    rehearsal_fields = [
        "fold", "surface", "truth_recipe", "candidate_count_capped",
        "truth_generated", "gdt520_rank", "gdt521_rank", "gdt520_top1",
        "gdt521_top1", "truth_order5_nll", "top1_order5_nll",
    ]
    current_fields = [
        "surface", "occurrence_count", "physical_pages", "truth_recipe",
        "candidate_count_capped", "gdt520_rank", "gdt520_top1", "gdt521_rank",
        "gdt521_top1", "gdt521_top5", "truth_gdt520_score",
        "truth_order5_nll", "truth_gdt521_score", "truth_alignment_trace",
        "top1_gdt520_score", "top1_order5_nll", "top1_gdt521_score",
        "top1_alignment_trace", "decision_change_class", "working_policy",
    ]
    write_tsv(OUT / "gdt521_1558_four_fold_tail_rehearsal.tsv", rehearsal, rehearsal_fields)
    write_tsv(OUT / "gdt521_159_tail_rerank.tsv", current, current_fields)
    write_tsv(
        OUT / "gdt521_remaining_top1_error_atlas.tsv",
        [row for row in current if int(row["gdt521_rank"]) != 1],
        current_fields,
    )
    write_tsv(
        OUT / "gdt521_changed_decision_atlas.tsv",
        [row for row in current if row["gdt520_top1"] != row["gdt521_top1"]],
        current_fields,
    )
    write_tsv(
        OUT / "gdt521_candidate_score_atlas.tsv",
        candidates,
        [
            "surface", "truth_recipe", "candidate_is_truth", "gdt517_compiler_rank",
            "gdt520_rank", "gdt521_rank", "candidate_recipe", "gdt520_score",
            "order5_nll", "gdt521_score", "alignment_trace",
        ],
    )
    write_tsv(
        OUT / "gdt521_order5_history_atlas.tsv",
        selected_model.atlas_rows(),
        [
            "order", "alpha", "history", "next_atom", "support",
            "history_total", "vocabulary_count", "smoothed_probability",
        ],
    )
    write_tsv(
        OUT / "gdt521_ambiguity_tail_family_atlas.tsv",
        tail_family_rows(old),
        [
            "family", "tail_recipe", "old_surface_type_count", "old_event_count",
            "example_surfaces",
        ],
    )
    ladder = rehearsal_ladder + current_ladder
    write_tsv(
        OUT / "gdt521_model_ladder.tsv",
        ladder,
        [
            "scope", "model_stage", "ngram_order", "alpha", "ngram_weight",
            "target_count", "truth_generated_count", "top1_exact_count",
            "top2_exact_count", "top3_exact_count", "top5_exact_count",
            "rank_sum", "deepest_truth_rank",
        ],
    )

    old_base = G519.rank_metrics([int(row["gdt520_rank"]) for row in rehearsal])
    old_selected = G519.rank_metrics([int(row["gdt521_rank"]) for row in rehearsal])
    current_base = G519.rank_metrics([int(row["gdt520_rank"]) for row in current])
    current_selected = G519.rank_metrics([int(row["gdt521_rank"]) for row in current])
    classes = Counter(str(row["decision_change_class"]) for row in current)
    result = {
        "experiment_id": "GDT521",
        "status": "PASS_SHORT_RECIPE_TAIL_LICENSE_RERANKER",
        "claim_ceiling": "EXPLORATORY_SHORT_ATOM_HISTORY_COMPOSITION_DEFAULT__NO_CONFIRMED_LEXEME_OR_PLAINTEXT",
        "selected_policy": {
            "order": SELECTED_ORDER,
            "history_atom_count": SELECTED_ORDER - 1,
            "alpha": SELECTED_ALPHA,
            "weight": SELECTED_WEIGHT,
            "normalization": "MEAN_NLL_PER_RECIPE_ATOM_PLUS_END",
            "training_unit": "INVARIANT_SURFACE_TYPE",
            "old26_training_surface_count": selected_model.training_surface_count,
            "history_count": len(selected_model.histories),
            "observed_transition_count": len(selected_model.counts),
            "vocabulary_count": len(selected_model.vocabulary),
        },
        "old26_four_fold_gdt520_metrics": old_base,
        "old26_four_fold_gdt521_metrics": old_selected,
        "current_gdt520_metrics": current_base,
        "current_gdt521_metrics": current_selected,
        "current_net_top1_gain": current_selected["top1_exact_count"] - current_base["top1_exact_count"],
        "current_rank_sum_reduction": current_base["rank_sum"] - current_selected["rank_sum"],
        "current_decision_change_classes": dict(sorted(classes.items())),
        "remaining_top1_error_count": sum(int(row["gdt521_rank"]) != 1 for row in current),
        "guard": "SHORT_RECIPE_HISTORY_IS_A_COMPOSITION_PRIOR_ONLY__KNOWN_EVENT_AND_SURFACE_CARDS_KEEP_PRECEDENCE",
    }
    write_json(OUT / "gdt521_result.json", result)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
