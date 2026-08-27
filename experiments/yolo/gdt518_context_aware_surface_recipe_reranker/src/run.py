#!/usr/bin/env python3
"""Rerank finite GDT517 surface parses from visible form and neighboring cards."""

from __future__ import annotations

import csv
import importlib.util
import json
import math
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt518_context_aware_surface_recipe_reranker"
OUT = BASE / "artifacts"

G517_RUN = (
    ROOT
    / "experiments/yolo/gdt517_thirty_page_surface_recipe_intake_compiler/src/run.py"
)
G407_RUNNING = (
    ROOT
    / "experiments/yolo/gdt407_unified_twenty_six_page_workshop_edition/artifacts"
    / "gdt407_4576_running_event_edition.tsv"
)
G516_SELECTED = (
    ROOT
    / "experiments/yolo/gdt516_thirty_page_new_surface_family_consolidation/artifacts"
    / "gdt516_597_contextualized_event_edition.tsv"
)
G516_NEW = (
    ROOT
    / "experiments/yolo/gdt516_thirty_page_new_surface_family_consolidation/artifacts"
    / "gdt516_159_new_surface_family_atlas.tsv"
)

RIDGE_ALPHA = 10.0
CANDIDATE_CAP = 100
BASE_RANK_WEIGHT = 1.0
CONTEXT_ALPHA = 10.0
CONTEXT_WEIGHT = 0.05


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


G517 = load_module("gdt517_core_for_gdt518", G517_RUN)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def recipe_text(recipe: tuple[str, ...]) -> str:
    return G517.recipe_text(recipe)


def surface_features(surface: str) -> Counter[str]:
    """Visible-only counts: length plus character uni-, bi-, and trigrams."""
    values: Counter[str] = Counter({"LEN": len(surface)})
    for width, prefix in ((1, "U"), (2, "B"), (3, "T")):
        for start in range(len(surface) - width + 1):
            values[f"{prefix}:{surface[start:start + width]}"] += 1
    return values


def recipe_features(recipe: tuple[str, ...]) -> Counter[str]:
    """Order-aware target signature: atom counts and adjacent atom pairs."""
    values: Counter[str] = Counter()
    for atom in recipe:
        values[f"A:{atom}"] += 1
    for left, right in zip(recipe, recipe[1:]):
        values[f"B:{left}>{right}"] += 1
    return values


@dataclass
class SurfaceRidge:
    surface_vocabulary: tuple[str, ...]
    recipe_vocabulary: tuple[str, ...]
    coefficients: np.ndarray
    training_surface_count: int
    training_fit_mse: float

    @property
    def surface_index(self) -> dict[str, int]:
        return {feature: index for index, feature in enumerate(self.surface_vocabulary)}

    @property
    def recipe_index(self) -> dict[str, int]:
        return {feature: index for index, feature in enumerate(self.recipe_vocabulary)}

    def predict(self, surface: str) -> np.ndarray:
        index = self.surface_index
        vector = np.zeros(len(index) + 1, dtype=float)
        vector[0] = 1.0
        for feature, count in surface_features(surface).items():
            if feature in index:
                vector[index[feature] + 1] = count
        return vector @ self.coefficients

    def encode_recipe(self, recipe: tuple[str, ...]) -> np.ndarray:
        index = self.recipe_index
        vector = np.zeros(len(index), dtype=float)
        for feature, count in recipe_features(recipe).items():
            if feature in index:
                vector[index[feature]] = count
        return vector

    def squared_cost(self, prediction: np.ndarray, recipe: tuple[str, ...]) -> float:
        delta = prediction - self.encode_recipe(recipe)
        return float(np.square(delta).sum())


def invariant_surface_recipes(
    rows: list[dict[str, str]], recipe_field: str
) -> dict[str, tuple[str, ...]]:
    values: dict[str, set[tuple[str, ...]]] = defaultdict(set)
    for row in rows:
        values[row["surface"]].add(G517.atoms(row[recipe_field]))
    conflicts = {surface: recipes for surface, recipes in values.items() if len(recipes) != 1}
    if conflicts:
        raise RuntimeError(f"Surface-ridge input has {len(conflicts)} non-invariant surfaces")
    return {surface: next(iter(recipes)) for surface, recipes in values.items()}


def train_surface_ridge(
    rows: list[dict[str, str]], recipe_field: str, alpha: float = RIDGE_ALPHA
) -> SurfaceRidge:
    forms = invariant_surface_recipes(rows, recipe_field)
    surface_vocabulary = tuple(
        sorted({feature for surface in forms for feature in surface_features(surface)})
    )
    recipe_vocabulary = tuple(
        sorted({feature for recipe in forms.values() for feature in recipe_features(recipe)})
    )
    surface_index = {feature: index for index, feature in enumerate(surface_vocabulary)}
    recipe_index = {feature: index for index, feature in enumerate(recipe_vocabulary)}
    x = np.zeros((len(forms), len(surface_vocabulary) + 1), dtype=float)
    y = np.zeros((len(forms), len(recipe_vocabulary)), dtype=float)
    for row_index, (surface, recipe) in enumerate(sorted(forms.items())):
        x[row_index, 0] = 1.0
        for feature, count in surface_features(surface).items():
            x[row_index, surface_index[feature] + 1] = count
        for feature, count in recipe_features(recipe).items():
            y[row_index, recipe_index[feature]] = count
    regularizer = np.eye(x.shape[1], dtype=float) * alpha
    regularizer[0, 0] = 0.0
    coefficients = np.linalg.solve(x.T @ x + regularizer, x.T @ y)
    residual = x @ coefficients - y
    fit_mse = float(np.square(residual).mean())
    return SurfaceRidge(
        surface_vocabulary=surface_vocabulary,
        recipe_vocabulary=recipe_vocabulary,
        coefficients=coefficients,
        training_surface_count=len(forms),
        training_fit_mse=fit_mse,
    )


@dataclass
class NgramModel:
    order: int
    alpha: float
    counts: Counter[tuple[str, ...]]
    histories: Counter[tuple[str, ...]]
    vocabulary: tuple[str, ...]
    statement_count: int
    token_count: int

    def probability(self, history: tuple[str, ...], token: str) -> float:
        numerator = self.counts[history + (token,)] + self.alpha
        denominator = self.histories[history] + self.alpha * len(self.vocabulary)
        return numerator / denominator

    def touching_nll(
        self, tokens: list[str], target_start: int, target_end: int
    ) -> float:
        costs: list[float] = []
        for index in range(self.order - 1, len(tokens)):
            window = range(index - self.order + 1, index + 1)
            if not any(target_start <= position < target_end for position in window):
                continue
            history = tuple(tokens[index - self.order + 1:index])
            costs.append(-math.log(self.probability(history, tokens[index])))
        return sum(costs) / len(costs) if costs else 0.0


def statement_groups(
    rows: list[dict[str, str]], statement_field: str
) -> list[list[dict[str, str]]]:
    groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    order: list[str] = []
    for row in rows:
        statement = row[statement_field]
        if statement not in groups:
            order.append(statement)
        groups[statement].append(row)
    return [groups[statement] for statement in order]


def statement_tokens(rows: list[dict[str, str]], recipe_field: str) -> list[str]:
    tokens = ["<S>"]
    for index, row in enumerate(rows):
        if index:
            tokens.append("<C>")
        tokens.extend(G517.atoms(row[recipe_field]))
    tokens.append("<E>")
    return tokens


def train_ngram(
    rows: list[dict[str, str]], statement_field: str, recipe_field: str,
    order: int, alpha: float = CONTEXT_ALPHA,
) -> NgramModel:
    counts: Counter[tuple[str, ...]] = Counter()
    histories: Counter[tuple[str, ...]] = Counter()
    vocabulary: set[str] = set()
    groups = statement_groups(rows, statement_field)
    token_count = 0
    for group in groups:
        tokens = statement_tokens(group, recipe_field)
        vocabulary.update(tokens)
        token_count += len(tokens)
        for index in range(order - 1, len(tokens)):
            history = tuple(tokens[index - order + 1:index])
            counts[history + (tokens[index],)] += 1
            histories[history] += 1
    return NgramModel(
        order=order,
        alpha=alpha,
        counts=counts,
        histories=histories,
        vocabulary=tuple(sorted(vocabulary)),
        statement_count=len(groups),
        token_count=token_count,
    )


def selected_prose_occurrences(
    selected: list[dict[str, str]],
) -> dict[str, list[tuple[list[dict[str, str]], int]]]:
    prose = [row for row in selected if row["source_kind"] == "P"]
    occurrences: dict[str, list[tuple[list[dict[str, str]], int]]] = defaultdict(list)
    for group in statement_groups(prose, "statement_id"):
        for index, row in enumerate(group):
            occurrences[row["surface"]].append((group, index))
    return occurrences


def occurrence_tokens(
    group: list[dict[str, str]], target_index: int, candidate: tuple[str, ...]
) -> tuple[list[str], int, int]:
    tokens = ["<S>"]
    target_start = target_end = -1
    for index, row in enumerate(group):
        if index:
            tokens.append("<C>")
        start = len(tokens)
        recipe = candidate if index == target_index else G517.atoms(row["gdt516_context_recipe"])
        tokens.extend(recipe)
        if index == target_index:
            target_start, target_end = start, len(tokens)
    tokens.append("<E>")
    return tokens, target_start, target_end


def aggregate_context_nll(
    model: NgramModel,
    occurrences: list[tuple[list[dict[str, str]], int]],
    candidate: tuple[str, ...],
) -> float:
    costs = []
    for group, target_index in occurrences:
        tokens, target_start, target_end = occurrence_tokens(group, target_index, candidate)
        costs.append(model.touching_nll(tokens, target_start, target_end))
    return sum(costs) / len(costs) if costs else 0.0


def rank_metrics(ranks: Iterable[int]) -> dict[str, int]:
    values = list(ranks)
    positive = [rank for rank in values if rank]
    return {
        "target_count": len(values),
        "truth_generated_count": len(positive),
        "top1_exact_count": sum(rank == 1 for rank in values),
        "top2_exact_count": sum(0 < rank <= 2 for rank in values),
        "top3_exact_count": sum(0 < rank <= 3 for rank in values),
        "top5_exact_count": sum(0 < rank <= 5 for rank in values),
        "rank_sum": sum(positive),
        "deepest_truth_rank": max(positive, default=0),
    }


def candidate_rank(
    scored: list[dict[str, object]], truth: tuple[str, ...], score_field: str
) -> tuple[int, list[dict[str, object]]]:
    ordered = sorted(scored, key=lambda row: (float(row[score_field]), int(row["base_index"])))
    rank = next(
        (index + 1 for index, row in enumerate(ordered) if row["recipe"] == truth), 0
    )
    return rank, ordered


def change_class(baseline_correct: bool, selected_correct: bool, top_changed: bool) -> str:
    if baseline_correct and selected_correct:
        return "BASELINE_CORRECT_PRESERVED"
    if not baseline_correct and selected_correct:
        return "BASELINE_ERROR_CORRECTED"
    if baseline_correct and not selected_correct:
        return "BASELINE_CORRECT_LOST"
    if top_changed:
        return "ERROR_CHANGED_STILL_WRONG"
    return "BASELINE_ERROR_UNCHANGED"


def benchmark() -> tuple[list[dict[str, object]], list[dict[str, object]], dict[str, object]]:
    old = read_tsv(G407_RUNNING)
    selected = read_tsv(G516_SELECTED)
    targets = read_tsv(G516_NEW)
    compiler = G517.build_model("OLD26_RUNNING", old, "component_recipe")
    mappings = G517.retained_mappings(compiler.evidence)
    ridge = train_surface_ridge(old, "component_recipe")
    bigram = train_ngram(old, "source_statement_id", "component_recipe", order=2)
    trigram = train_ngram(old, "source_statement_id", "component_recipe", order=3)
    occurrences = selected_prose_occurrences(selected)

    output: list[dict[str, object]] = []
    candidate_output: list[dict[str, object]] = []
    stage_ranks: dict[str, list[int]] = defaultdict(list)
    for target in targets:
        surface = target["surface"]
        truth = G517.atoms(target["gdt516_context_recipe"])
        candidates = G517.parse_surface(
            surface, mappings, cap=CANDIDATE_CAP, allow_f66r_local=True
        )
        prediction = ridge.predict(surface)
        scored: list[dict[str, object]] = []
        for base_index, candidate in enumerate(candidates):
            structural_cost = ridge.squared_cost(prediction, candidate.recipe)
            base_rank_cost = BASE_RANK_WEIGHT * math.log1p(base_index)
            bigram_nll = aggregate_context_nll(
                bigram, occurrences.get(surface, []), candidate.recipe
            )
            trigram_nll = aggregate_context_nll(
                trigram, occurrences.get(surface, []), candidate.recipe
            )
            row: dict[str, object] = {
                "surface": surface,
                "recipe": candidate.recipe,
                "recipe_text": recipe_text(candidate.recipe),
                "base_index": base_index,
                "base_rank": base_index + 1,
                "structural_cost": structural_cost,
                "base_rank_cost": base_rank_cost,
                "bigram_nll": bigram_nll,
                "trigram_nll": trigram_nll,
                "score_structure_only": structural_cost,
                "score_surface": structural_cost + base_rank_cost,
                "score_bigram": structural_cost + base_rank_cost + CONTEXT_WEIGHT * bigram_nll,
                "score_trigram": structural_cost + base_rank_cost + CONTEXT_WEIGHT * trigram_nll,
                "score_selected": structural_cost + base_rank_cost
                + (CONTEXT_WEIGHT / 2.0) * (bigram_nll + trigram_nll),
            }
            scored.append(row)

        rankings: dict[str, tuple[int, list[dict[str, object]]]] = {
            "GDT517_ORIGINAL": (
                next(
                    (index + 1 for index, candidate in enumerate(candidates)
                     if candidate.recipe == truth),
                    0,
                ),
                scored,
            ),
            "RIDGE_STRUCTURE_ONLY": candidate_rank(scored, truth, "score_structure_only"),
            "RIDGE_PLUS_BASE_RANK": candidate_rank(scored, truth, "score_surface"),
            "PLUS_BIGRAM_CONTEXT": candidate_rank(scored, truth, "score_bigram"),
            "PLUS_TRIGRAM_CONTEXT": candidate_rank(scored, truth, "score_trigram"),
            "SELECTED_BIGRAM_TRIGRAM_MEAN": candidate_rank(scored, truth, "score_selected"),
        }
        for stage, (rank, _) in rankings.items():
            stage_ranks[stage].append(rank)

        baseline_rank, baseline_ordered = rankings["GDT517_ORIGINAL"]
        surface_rank, surface_ordered = rankings["RIDGE_PLUS_BASE_RANK"]
        selected_rank, selected_ordered = rankings["SELECTED_BIGRAM_TRIGRAM_MEAN"]
        baseline_top = baseline_ordered[0]
        surface_top = surface_ordered[0]
        selected_top = selected_ordered[0]
        truth_row = next(row for row in scored if row["recipe"] == truth)
        classification = change_class(
            baseline_rank == 1,
            selected_rank == 1,
            baseline_top["recipe"] != selected_top["recipe"],
        )
        result_row: dict[str, object] = {
            "surface": surface,
            "occurrence_count": target["occurrence_count"],
            "physical_pages": target["physical_pages"],
            "truth_recipe": recipe_text(truth),
            "prose_context_occurrence_count": len(occurrences.get(surface, [])),
            "candidate_count_capped": len(candidates),
            "baseline_rank": baseline_rank,
            "baseline_top1": baseline_top["recipe_text"],
            "surface_ridge_rank": surface_rank,
            "surface_ridge_top1": surface_top["recipe_text"],
            "selected_rank": selected_rank,
            "selected_top1": selected_top["recipe_text"],
            "selected_top5": " | ".join(str(row["recipe_text"]) for row in selected_ordered[:5]),
            "truth_structural_cost": f"{float(truth_row['structural_cost']):.9f}",
            "truth_bigram_nll": f"{float(truth_row['bigram_nll']):.9f}",
            "truth_trigram_nll": f"{float(truth_row['trigram_nll']):.9f}",
            "truth_selected_score": f"{float(truth_row['score_selected']):.9f}",
            "top1_structural_cost": f"{float(selected_top['structural_cost']):.9f}",
            "top1_bigram_nll": f"{float(selected_top['bigram_nll']):.9f}",
            "top1_trigram_nll": f"{float(selected_top['trigram_nll']):.9f}",
            "top1_selected_score": f"{float(selected_top['score_selected']):.9f}",
            "decision_change_class": classification,
            "working_policy": (
                "EXACT_EVENT_OR_KNOWN_SURFACE_STILL_WINS__RERANK_ONLY_FUTURE_UNKNOWN"
            ),
        }
        output.append(result_row)

        if selected_rank != 1 or baseline_rank != selected_rank:
            for selected_position, candidate_row in enumerate(selected_ordered[:15], 1):
                candidate_output.append(
                    {
                        "surface": surface,
                        "truth_recipe": recipe_text(truth),
                        "candidate_is_truth": "YES" if candidate_row["recipe"] == truth else "NO",
                        "baseline_rank": int(candidate_row["base_rank"]),
                        "selected_rank": selected_position,
                        "candidate_recipe": candidate_row["recipe_text"],
                        "structural_cost": f"{float(candidate_row['structural_cost']):.9f}",
                        "base_rank_cost": f"{float(candidate_row['base_rank_cost']):.9f}",
                        "bigram_nll": f"{float(candidate_row['bigram_nll']):.9f}",
                        "trigram_nll": f"{float(candidate_row['trigram_nll']):.9f}",
                        "selected_score": f"{float(candidate_row['score_selected']):.9f}",
                    }
                )

    ladder: list[dict[str, object]] = []
    descriptions = {
        "GDT517_ORIGINAL": "chunk count, evidence score, lexical tuple",
        "RIDGE_STRUCTURE_ONLY": "visible character ngrams predict atom and atom-pair counts",
        "RIDGE_PLUS_BASE_RANK": "surface ridge plus logarithmic GDT517 rank prior",
        "PLUS_BIGRAM_CONTEXT": "surface score plus positive bigram neighbor NLL",
        "PLUS_TRIGRAM_CONTEXT": "surface score plus positive trigram neighbor NLL",
        "SELECTED_BIGRAM_TRIGRAM_MEAN": "surface score plus mean bigram/trigram neighbor NLL",
    }
    baseline_tops = [row["baseline_top1"] for row in output]
    for stage, ranks in stage_ranks.items():
        metrics = rank_metrics(ranks)
        if stage == "GDT517_ORIGINAL":
            changed = 0
        else:
            field = {
                "RIDGE_PLUS_BASE_RANK": "surface_ridge_top1",
                "SELECTED_BIGRAM_TRIGRAM_MEAN": "selected_top1",
            }.get(stage)
            changed = (
                sum(row[field] != baseline for row, baseline in zip(output, baseline_tops))
                if field else -1
            )
        ladder.append(
            {
                "model_stage": stage,
                "description": descriptions[stage],
                **metrics,
                "top1_changed_from_baseline": changed,
            }
        )

    class_counts = Counter(str(row["decision_change_class"]) for row in output)
    selected_metrics = rank_metrics(stage_ranks["SELECTED_BIGRAM_TRIGRAM_MEAN"])
    baseline_metrics = rank_metrics(stage_ranks["GDT517_ORIGINAL"])
    diagnostics: dict[str, object] = {
        "experiment_id": "GDT518",
        "status": "PASS_CONTEXT_AWARE_SURFACE_RECIPE_RERANKER",
        "claim_ceiling": "EXPLORATORY_WORKING_RERANKER__NO_CONFIRMED_LEXEME_OR_PLAINTEXT",
        "training": {
            "old26_running_events": len(old),
            "old26_invariant_surfaces": ridge.training_surface_count,
            "surface_feature_count": len(ridge.surface_vocabulary),
            "recipe_feature_count": len(ridge.recipe_vocabulary),
            "ridge_alpha": RIDGE_ALPHA,
            "ridge_training_fit_mse": ridge.training_fit_mse,
            "bigram_statement_count": bigram.statement_count,
            "bigram_distinct_ngram_count": len(bigram.counts),
            "trigram_distinct_ngram_count": len(trigram.counts),
            "context_vocabulary_count": len(bigram.vocabulary),
            "context_alpha": CONTEXT_ALPHA,
        },
        "selection": {
            "candidate_cap": CANDIDATE_CAP,
            "base_rank_weight": BASE_RANK_WEIGHT,
            "context_weight": CONTEXT_WEIGHT,
            "context_formula": "0.05 * mean(bigram_touching_nll, trigram_touching_nll)",
        },
        "baseline_metrics": baseline_metrics,
        "selected_metrics": selected_metrics,
        "net_top1_gain": (
            selected_metrics["top1_exact_count"] - baseline_metrics["top1_exact_count"]
        ),
        "decision_change_classes": dict(sorted(class_counts.items())),
        "selected_remaining_top1_error_count": sum(
            row["selected_rank"] != 1 for row in output
        ),
        "no_prose_context_surface_count": sum(
            int(row["prose_context_occurrence_count"]) == 0 for row in output
        ),
        "guard": "KNOWN_EVENT_RECIPE_PRECEDENCE_UNCHANGED__RERANKER_ONLY_ORDERS_FINITE_UNKNOWN_SURFACE_CANDIDATES",
    }
    return output, candidate_output, {"ladder": ladder, "diagnostics": diagnostics}


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    rows, candidates, summary = benchmark()
    fields = [
        "surface", "occurrence_count", "physical_pages", "truth_recipe",
        "prose_context_occurrence_count", "candidate_count_capped", "baseline_rank",
        "baseline_top1", "surface_ridge_rank", "surface_ridge_top1", "selected_rank",
        "selected_top1", "selected_top5", "truth_structural_cost", "truth_bigram_nll",
        "truth_trigram_nll", "truth_selected_score", "top1_structural_cost",
        "top1_bigram_nll", "top1_trigram_nll", "top1_selected_score",
        "decision_change_class", "working_policy",
    ]
    write_tsv(OUT / "gdt518_159_context_rerank.tsv", rows, fields)
    write_tsv(
        OUT / "gdt518_42_baseline_disagreement_atlas.tsv",
        [row for row in rows if int(row["baseline_rank"]) != 1],
        fields,
    )
    write_tsv(
        OUT / "gdt518_remaining_top1_error_atlas.tsv",
        [row for row in rows if int(row["selected_rank"]) != 1],
        fields,
    )
    write_tsv(
        OUT / "gdt518_changed_decision_atlas.tsv",
        [row for row in rows if row["baseline_top1"] != row["selected_top1"]],
        fields,
    )
    write_tsv(
        OUT / "gdt518_candidate_cost_atlas.tsv",
        candidates,
        [
            "surface", "truth_recipe", "candidate_is_truth", "baseline_rank", "selected_rank",
            "candidate_recipe", "structural_cost", "base_rank_cost", "bigram_nll",
            "trigram_nll", "selected_score",
        ],
    )
    write_tsv(
        OUT / "gdt518_model_ladder.tsv",
        summary["ladder"],
        [
            "model_stage", "description", "target_count", "truth_generated_count",
            "top1_exact_count", "top2_exact_count", "top3_exact_count", "top5_exact_count",
            "rank_sum", "deepest_truth_rank", "top1_changed_from_baseline",
        ],
    )
    write_json(OUT / "gdt518_result.json", summary["diagnostics"])
    print(json.dumps(summary["diagnostics"], ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
