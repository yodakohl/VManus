#!/usr/bin/env python3
"""Learn nearest-neighbour surface/recipe edits and rerank GDT521 parses."""

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
BASE = ROOT / "experiments/yolo/gdt522_local_edit_analogy_license_reranker"
OUT = BASE / "artifacts"
G521_RUN = (
    ROOT
    / "experiments/yolo/gdt521_short_recipe_tail_license_reranker/src/run.py"
)

FOLD_COUNT = 4
MAX_VISIBLE_INSERT = 3
MAX_ATOM_INSERT = 3
ALPHA = 0.5
RELIABILITY_PRIOR = 2.0

# Exploratory ladder. The selected row remains an executable default, not a
# word claim.
CONFIGS = (
    ("GDT521_BASE", 0.0, 0.0),
    ("COND_C00_W03", 0.0, 0.3),
    ("COND_C00_W07", 0.0, 0.7),
    ("COND_C00_W10", 0.0, 1.0),
    ("COND_C05_W03", 0.5, 0.3),
    ("COND_C05_W05", 0.5, 0.5),
    ("COND_C05_W07", 0.5, 0.7),
    ("COND_C05_W10", 0.5, 1.0),
    ("COND_C05_W15", 0.5, 1.5),
    ("COND_C060_W025", 0.6, 0.25),
    ("COND_C060_W030", 0.6, 0.3),
    ("COND_C060_W035", 0.6, 0.35),
    ("COND_C060_W040", 0.6, 0.4),
    ("COND_C070_W025", 0.7, 0.25),
    ("COND_C070_W030", 0.7, 0.3),
    ("COND_C070_W035", 0.7, 0.35),
    ("COND_C070_W040", 0.7, 0.4),
    ("COND_C075_W03", 0.75, 0.3),
    ("COND_C075_W05", 0.75, 0.5),
    ("COND_C075_W07", 0.75, 0.7),
    ("COND_C075_W10", 0.75, 1.0),
    ("COND_C080_W025", 0.8, 0.25),
    ("COND_C080_W030", 0.8, 0.3),
    ("COND_C080_W035", 0.8, 0.35),
    ("COND_C080_W040", 0.8, 0.4),
    ("COND_C090_W025", 0.9, 0.25),
    ("COND_C090_W030", 0.9, 0.3),
    ("COND_C090_W035", 0.9, 0.35),
    ("COND_C090_W040", 0.9, 0.4),
    ("COND_C10_W02", 1.0, 0.2),
    ("COND_C10_W03", 1.0, 0.3),
    ("COND_C10_W05", 1.0, 0.5),
    ("COND_C10_W07", 1.0, 0.7),
    ("COND_C10_W10", 1.0, 1.0),
    ("COND_C110_W025", 1.1, 0.25),
    ("COND_C110_W030", 1.1, 0.3),
    ("COND_C110_W035", 1.1, 0.35),
    ("COND_C110_W040", 1.1, 0.4),
    ("COND_C120_W025", 1.2, 0.25),
    ("COND_C120_W030", 1.2, 0.3),
    ("COND_C120_W035", 1.2, 0.35),
    ("COND_C120_W040", 1.2, 0.4),
    ("COND_C125_W03", 1.25, 0.3),
    ("COND_C125_W05", 1.25, 0.5),
    ("COND_C125_W07", 1.25, 0.7),
    ("COND_C130_W025", 1.3, 0.25),
    ("COND_C130_W030", 1.3, 0.3),
    ("COND_C130_W035", 1.3, 0.35),
    ("COND_C130_W040", 1.3, 0.4),
    ("COND_C15_W02", 1.5, 0.2),
    ("COND_C15_W03", 1.5, 0.3),
    ("COND_C15_W05", 1.5, 0.5),
    ("COND_C20_W03", 2.0, 0.3),
    ("COND_C20_W05", 2.0, 0.5),
    ("COND_C20_W07", 2.0, 0.7),
    ("COND_C20_W10", 2.0, 1.0),
    ("COND_C20_W15", 2.0, 1.5),
    ("COND_C25_W07", 2.5, 0.7),
    ("COND_C25_W10", 2.5, 1.0),
    ("COND_C25_W15", 2.5, 1.5),
    ("COND_C30_W07", 3.0, 0.7),
    ("COND_C30_W10", 3.0, 1.0),
    ("COND_C30_W15", 3.0, 1.5),
)
SELECTED_STAGE = "COND_C110_W040"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


G521 = load_module("gdt521_core_for_gdt522", G521_RUN)
G520 = G521.G520
G519 = G521.G519
G518 = G521.G518
G517 = G521.G517


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


def position(index: int, total: int, width: int) -> str:
    if index == 0:
        return "LEFT"
    if index + width == total:
        return "RIGHT"
    return "INNER"


def recipe_insertions(
    big: tuple[str, ...], small: tuple[str, ...]
) -> set[tuple[tuple[str, ...], str]]:
    """Return local atom blocks whose removal turns big into small.

    Equal recipes explicitly encode a visible-but-null atom insertion.
    """
    if big == small:
        return {((), "NULL")}
    output: set[tuple[tuple[str, ...], str]] = set()
    for width in range(1, min(MAX_ATOM_INSERT, len(big)) + 1):
        for index in range(len(big) - width + 1):
            if big[:index] + big[index + width :] == small:
                output.add(
                    (big[index : index + width], position(index, len(big), width))
                )
    return output


Signature = tuple[str, str, tuple[str, ...], str]


@dataclass(frozen=True)
class AnalogyHit:
    base_surface: str
    visible_insert: str
    visible_position: str
    atom_insert: tuple[str, ...]
    atom_position: str
    support: int
    conditional_total: int
    conditional_option_count: int
    conditional_probability: float
    reliability: float
    license_bonus: float

    def trace(self) -> str:
        atoms = recipe_text(self.atom_insert) if self.atom_insert else "NULL"
        return (
            f"{self.base_surface}+{self.visible_insert}=>{atoms}"
            f"@{self.visible_position}/{self.atom_position}"
            f";n={self.support}/{self.conditional_total}"
            f";p={self.conditional_probability:.6f}"
            f";r={self.reliability:.6f}"
            f";b={self.license_bonus:.6f}"
        )


@dataclass
class AnalogyModel:
    forms: dict[str, tuple[str, ...]]
    counts: Counter[Signature]
    totals: Counter[tuple[str, str]]
    options: dict[tuple[str, str], set[tuple[tuple[str, ...], str]]]
    examples: dict[Signature, list[str]]
    pair_count: int

    def nearest_routes(self, surface: str) -> list[tuple[str, str, str]]:
        routes: list[tuple[int, str, str, str]] = []
        upper = min(MAX_VISIBLE_INSERT, max(0, len(surface) - 1))
        for width in range(1, upper + 1):
            for index in range(len(surface) - width + 1):
                small = surface[:index] + surface[index + width :]
                if small in self.forms:
                    routes.append(
                        (
                            width,
                            small,
                            surface[index : index + width],
                            position(index, len(surface), width),
                        )
                    )
        if not routes:
            return []
        minimum = min(row[0] for row in routes)
        return [
            (small, visible, pos)
            for width, small, visible, pos in routes
            if width == minimum
        ]

    def hits(
        self, surface: str, recipe: tuple[str, ...], missing_cost: float
    ) -> list[AnalogyHit]:
        output: list[AnalogyHit] = []
        for small, visible, visible_pos in self.nearest_routes(surface):
            for atom_insert, atom_pos in recipe_insertions(recipe, self.forms[small]):
                signature = (visible, visible_pos, atom_insert, atom_pos)
                support = self.counts[signature]
                if not support:
                    continue
                key = (visible, visible_pos)
                total = self.totals[key]
                option_count = len(self.options[key])
                probability = (support + ALPHA) / (
                    total + ALPHA * option_count
                )
                reliability = support / (support + RELIABILITY_PRIOR)
                bonus = reliability * (missing_cost + math.log(probability))
                output.append(
                    AnalogyHit(
                        small,
                        visible,
                        visible_pos,
                        atom_insert,
                        atom_pos,
                        support,
                        total,
                        option_count,
                        probability,
                        reliability,
                        bonus,
                    )
                )
        return sorted(output, key=lambda row: row.license_bonus, reverse=True)

    def feature(
        self, surface: str, recipe: tuple[str, ...], missing_cost: float
    ) -> tuple[float, str]:
        routes = self.nearest_routes(surface)
        if not routes:
            return 0.0, "NO_NEAR_OLD_BASE"
        hits = self.hits(surface, recipe, missing_cost)
        if not hits:
            bases = "|".join(sorted({row[0] for row in routes}))
            return 0.0, f"NO_SUPPORTED_TRANSFORMATION;base={bases}"
        return hits[0].license_bonus, hits[0].trace()

    def atlas_rows(self) -> list[dict[str, object]]:
        rows: list[dict[str, object]] = []
        for signature in sorted(
            self.counts,
            key=lambda item: (item[0], item[1], item[2], item[3]),
        ):
            visible, visible_pos, atom_insert, atom_pos = signature
            key = (visible, visible_pos)
            support = self.counts[signature]
            probability = (support + ALPHA) / (
                self.totals[key] + ALPHA * len(self.options[key])
            )
            rows.append(
                {
                    "visible_insert": visible,
                    "visible_position": visible_pos,
                    "atom_insert": recipe_text(atom_insert) if atom_insert else "NULL",
                    "atom_position": atom_pos,
                    "support_pair_count": support,
                    "visible_condition_total": self.totals[key],
                    "visible_condition_option_count": len(self.options[key]),
                    "conditional_probability": f"{probability:.9f}",
                    "reliability": f"{support / (support + RELIABILITY_PRIOR):.9f}",
                    "examples": " | ".join(self.examples.get(signature, [])) or "NONE",
                }
            )
        return rows


def train_analogy_model(forms: dict[str, tuple[str, ...]]) -> AnalogyModel:
    counts: Counter[Signature] = Counter()
    examples: dict[Signature, list[str]] = defaultdict(list)
    pair_count = 0
    for big, big_recipe in forms.items():
        seen: set[tuple[str, Signature]] = set()
        upper = min(MAX_VISIBLE_INSERT, max(0, len(big) - 1))
        for width in range(1, upper + 1):
            for index in range(len(big) - width + 1):
                small = big[:index] + big[index + width :]
                if small not in forms:
                    continue
                visible = big[index : index + width]
                visible_pos = position(index, len(big), width)
                for atom_insert, atom_pos in recipe_insertions(
                    big_recipe, forms[small]
                ):
                    signature = (visible, visible_pos, atom_insert, atom_pos)
                    seen.add((small, signature))
        for small, signature in seen:
            counts[signature] += 1
            pair_count += 1
            if len(examples[signature]) < 8:
                examples[signature].append(f"{small}>{big}")
    totals: Counter[tuple[str, str]] = Counter()
    options: dict[
        tuple[str, str], set[tuple[tuple[str, ...], str]]
    ] = defaultdict(set)
    for (visible, visible_pos, atom_insert, atom_pos), support in counts.items():
        key = (visible, visible_pos)
        totals[key] += support
        options[key].add((atom_insert, atom_pos))
    return AnalogyModel(forms, counts, totals, dict(options), dict(examples), pair_count)


def metrics(ranks: list[int]) -> dict[str, int]:
    return G519.rank_metrics(ranks)


def metric_row(scope: str, config, ranks: list[int]) -> dict[str, object]:
    stage, missing_cost, weight = config
    return {
        "scope": scope,
        "model_stage": stage,
        "missing_relation_cost": missing_cost,
        "analogy_weight": weight,
        **metrics(ranks),
    }


def scores_for_configs(
    surface: str,
    candidates,
    base_scores: list[float],
    model: AnalogyModel,
) -> tuple[dict[str, list[float]], dict[float, list[float]], dict[float, list[str]]]:
    features: dict[float, list[float]] = {}
    traces: dict[float, list[str]] = {}
    for missing_cost in sorted(
        {row[1] for row in CONFIGS if row[0] != "GDT521_BASE"}
    ):
        values = [
            model.feature(surface, candidate.recipe, missing_cost)
            for candidate in candidates
        ]
        features[missing_cost] = [row[0] for row in values]
        traces[missing_cost] = [row[1] for row in values]
    scores: dict[str, list[float]] = {}
    for stage, missing_cost, weight in CONFIGS:
        scores[stage] = (
            list(base_scores)
            if stage == "GDT521_BASE"
            else [
                base - weight * bonus
                for base, bonus in zip(base_scores, features[missing_cost])
            ]
        )
    return scores, features, traces


def fold_rehearsal(old: list[dict[str, str]]):
    forms = G518.invariant_surface_recipes(old, "component_recipe")
    output: list[dict[str, object]] = []
    rank_sets: dict[str, list[int]] = defaultdict(list)
    fold_model_rows: list[dict[str, object]] = []
    selected_missing = next(row[1] for row in CONFIGS if row[0] == SELECTED_STAGE)
    for fold in range(FOLD_COUNT):
        held = {surface for surface in forms if G520.stable_fold(surface) == fold}
        training = [row for row in old if row["surface"] not in held]
        train_forms = G518.invariant_surface_recipes(training, "component_recipe")
        analogy = train_analogy_model(train_forms)
        mappings, ridge, deck, boundaries, recipe_models = G521.build_base_models(
            training, "component_recipe", f"GDT522_FOLD_{fold}_TRAIN"
        )
        history = recipe_models[(G521.SELECTED_ORDER, G521.SELECTED_ALPHA)]
        fold_model_rows.append(
            {
                "fold": fold,
                "training_surface_count": len(train_forms),
                "analogy_signature_count": len(analogy.counts),
                "analogy_pair_signature_count": analogy.pair_count,
                "visible_condition_count": len(analogy.totals),
                "nullable_signature_count": sum(not key[2] for key in analogy.counts),
            }
        )
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
                        "gdt521_rank": 0,
                        "gdt522_rank": 0,
                        "gdt521_top1": recipe_text(candidates[0].recipe) if candidates else "NONE",
                        "gdt522_top1": "NONE",
                        "truth_analogy_bonus": "NONE",
                        "top1_analogy_bonus": "NONE",
                        "truth_analogy_trace": "NONE",
                        "top1_analogy_trace": "NONE",
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
                base_scores.append(
                    gdt520_score
                    + G521.SELECTED_WEIGHT * history.mean_nll(candidate.recipe)
                )
            score_sets, features, traces = scores_for_configs(
                surface, candidates, base_scores, analogy
            )
            orders: dict[str, list[int]] = {}
            for stage, _, _ in CONFIGS:
                rank, order = G519.rank_by_score(
                    candidates, truth, score_sets[stage]
                )
                rank_sets[stage].append(rank)
                orders[stage] = order
            base_top = orders["GDT521_BASE"][0]
            selected_top = orders[SELECTED_STAGE][0]
            output.append(
                {
                    "fold": fold,
                    "surface": surface,
                    "truth_recipe": recipe_text(truth),
                    "candidate_count_capped": len(candidates),
                    "truth_generated": "YES",
                    "gdt521_rank": rank_sets["GDT521_BASE"][-1],
                    "gdt522_rank": rank_sets[SELECTED_STAGE][-1],
                    "gdt521_top1": recipe_text(candidates[base_top].recipe),
                    "gdt522_top1": recipe_text(candidates[selected_top].recipe),
                    "truth_analogy_bonus": f"{features[selected_missing][truth_index]:.9f}",
                    "top1_analogy_bonus": f"{features[selected_missing][selected_top]:.9f}",
                    "truth_analogy_trace": traces[selected_missing][truth_index],
                    "top1_analogy_trace": traces[selected_missing][selected_top],
                }
            )
    ladder = [
        metric_row(
            "FOUR_FOLD_OLD26_SURFACE_REHEARSAL", config, rank_sets[config[0]]
        )
        for config in CONFIGS
    ]
    return output, ladder, fold_model_rows


def current_benchmark(
    old: list[dict[str, str]],
    selected: list[dict[str, str]],
    targets: list[dict[str, str]],
):
    forms = G518.invariant_surface_recipes(old, "component_recipe")
    analogy = train_analogy_model(forms)
    mappings, ridge, deck, boundaries, recipe_models = G521.build_base_models(
        old, "component_recipe", "GDT522_FULL_OLD26"
    )
    history = recipe_models[(G521.SELECTED_ORDER, G521.SELECTED_ALPHA)]
    bigram = G518.train_ngram(
        old, "source_statement_id", "component_recipe", order=2
    )
    trigram = G518.train_ngram(
        old, "source_statement_id", "component_recipe", order=3
    )
    occurrences = G518.selected_prose_occurrences(selected)
    output: list[dict[str, object]] = []
    candidate_rows: list[dict[str, object]] = []
    rank_sets: dict[str, list[int]] = defaultdict(list)
    selected_missing = next(row[1] for row in CONFIGS if row[0] == SELECTED_STAGE)
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
            base_scores.append(
                gdt520_score
                + G521.SELECTED_WEIGHT * history.mean_nll(candidate.recipe)
            )
            paths.append(path)
        score_sets, features, traces = scores_for_configs(
            surface, candidates, base_scores, analogy
        )
        orders: dict[str, list[int]] = {}
        for stage, _, _ in CONFIGS:
            rank, order = G519.rank_by_score(candidates, truth, score_sets[stage])
            rank_sets[stage].append(rank)
            orders[stage] = order
        truth_index = next(
            index
            for index, candidate in enumerate(candidates)
            if candidate.recipe == truth
        )
        base_top = orders["GDT521_BASE"][0]
        top = orders[SELECTED_STAGE][0]
        if rank_sets["GDT521_BASE"][-1] == 1 and rank_sets[SELECTED_STAGE][-1] == 1:
            change = "GDT521_CORRECT_PRESERVED"
        elif rank_sets["GDT521_BASE"][-1] != 1 and rank_sets[SELECTED_STAGE][-1] == 1:
            change = "GDT521_ERROR_CORRECTED"
        elif rank_sets["GDT521_BASE"][-1] == 1 and rank_sets[SELECTED_STAGE][-1] != 1:
            change = "GDT521_CORRECT_LOST"
        elif candidates[base_top].recipe != candidates[top].recipe:
            change = "ERROR_CHANGED_STILL_WRONG"
        else:
            change = "GDT521_ERROR_UNCHANGED"
        output.append(
            {
                "surface": surface,
                "occurrence_count": target["occurrence_count"],
                "physical_pages": target["physical_pages"],
                "truth_recipe": recipe_text(truth),
                "candidate_count_capped": len(candidates),
                "gdt521_rank": rank_sets["GDT521_BASE"][-1],
                "gdt521_top1": recipe_text(candidates[base_top].recipe),
                "gdt522_rank": rank_sets[SELECTED_STAGE][-1],
                "gdt522_top1": recipe_text(candidates[top].recipe),
                "gdt522_top5": " | ".join(
                    recipe_text(candidates[index].recipe)
                    for index in orders[SELECTED_STAGE][:5]
                ),
                "truth_gdt521_score": f"{base_scores[truth_index]:.9f}",
                "truth_analogy_bonus": f"{features[selected_missing][truth_index]:.9f}",
                "truth_gdt522_score": f"{score_sets[SELECTED_STAGE][truth_index]:.9f}",
                "truth_analogy_trace": traces[selected_missing][truth_index],
                "top1_gdt521_score": f"{base_scores[top]:.9f}",
                "top1_analogy_bonus": f"{features[selected_missing][top]:.9f}",
                "top1_gdt522_score": f"{score_sets[SELECTED_STAGE][top]:.9f}",
                "top1_analogy_trace": traces[selected_missing][top],
                "top1_alignment_trace": G520.path_text(surface, paths[top]),
                "decision_change_class": change,
                "working_policy": "KNOWN_EVENT_OR_SURFACE_RECIPE_STILL_WINS__NEAREST_LOCAL_ANALOGY_RERANKS_ONLY_FINITE_UNKNOWN_CANDIDATES",
            }
        )
        if (
            rank_sets[SELECTED_STAGE][-1] != 1
            or candidates[base_top].recipe != candidates[top].recipe
        ):
            for selected_rank, index in enumerate(orders[SELECTED_STAGE][:12], 1):
                candidate_rows.append(
                    {
                        "surface": surface,
                        "truth_recipe": recipe_text(truth),
                        "candidate_is_truth": "YES" if candidates[index].recipe == truth else "NO",
                        "gdt517_compiler_rank": index + 1,
                        "gdt521_rank": orders["GDT521_BASE"].index(index) + 1,
                        "gdt522_rank": selected_rank,
                        "candidate_recipe": recipe_text(candidates[index].recipe),
                        "gdt521_score": f"{base_scores[index]:.9f}",
                        "analogy_bonus": f"{features[selected_missing][index]:.9f}",
                        "gdt522_score": f"{score_sets[SELECTED_STAGE][index]:.9f}",
                        "analogy_trace": traces[selected_missing][index],
                    }
                )
    ladder = [
        metric_row("CURRENT_159_OLD26_TO_NEW4", config, rank_sets[config[0]])
        for config in CONFIGS
    ]
    return output, candidate_rows, ladder, analogy


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    old = read_tsv(G518.G407_RUNNING)
    selected = read_tsv(G518.G516_SELECTED)
    targets = read_tsv(G518.G516_NEW)
    rehearsal, rehearsal_ladder, fold_models = fold_rehearsal(old)
    current, candidates, current_ladder, analogy = current_benchmark(
        old, selected, targets
    )

    rehearsal_fields = [
        "fold", "surface", "truth_recipe", "candidate_count_capped",
        "truth_generated", "gdt521_rank", "gdt522_rank", "gdt521_top1",
        "gdt522_top1", "truth_analogy_bonus", "top1_analogy_bonus",
        "truth_analogy_trace", "top1_analogy_trace",
    ]
    current_fields = [
        "surface", "occurrence_count", "physical_pages", "truth_recipe",
        "candidate_count_capped", "gdt521_rank", "gdt521_top1", "gdt522_rank",
        "gdt522_top1", "gdt522_top5", "truth_gdt521_score",
        "truth_analogy_bonus", "truth_gdt522_score", "truth_analogy_trace",
        "top1_gdt521_score", "top1_analogy_bonus", "top1_gdt522_score",
        "top1_analogy_trace", "top1_alignment_trace", "decision_change_class",
        "working_policy",
    ]
    write_tsv(
        OUT / "gdt522_1558_four_fold_local_analogy_rehearsal.tsv",
        rehearsal,
        rehearsal_fields,
    )
    write_tsv(
        OUT / "gdt522_159_local_analogy_rerank.tsv", current, current_fields
    )
    write_tsv(
        OUT / "gdt522_remaining_top1_error_atlas.tsv",
        [row for row in current if int(row["gdt522_rank"]) != 1],
        current_fields,
    )
    write_tsv(
        OUT / "gdt522_changed_decision_atlas.tsv",
        [row for row in current if row["gdt521_top1"] != row["gdt522_top1"]],
        current_fields,
    )
    write_tsv(
        OUT / "gdt522_candidate_score_atlas.tsv",
        candidates,
        [
            "surface", "truth_recipe", "candidate_is_truth",
            "gdt517_compiler_rank", "gdt521_rank", "gdt522_rank",
            "candidate_recipe", "gdt521_score", "analogy_bonus",
            "gdt522_score", "analogy_trace",
        ],
    )
    analogy_rows = analogy.atlas_rows()
    analogy_fields = [
        "visible_insert", "visible_position", "atom_insert", "atom_position",
        "support_pair_count", "visible_condition_total",
        "visible_condition_option_count", "conditional_probability",
        "reliability", "examples",
    ]
    write_tsv(
        OUT / "gdt522_local_edit_analogy_atlas.tsv",
        analogy_rows,
        analogy_fields,
    )
    write_tsv(
        OUT / "gdt522_nullable_visible_edit_atlas.tsv",
        [row for row in analogy_rows if row["atom_insert"] == "NULL"],
        analogy_fields,
    )
    write_tsv(
        OUT / "gdt522_fold_model_inventory.tsv",
        fold_models,
        [
            "fold", "training_surface_count", "analogy_signature_count",
            "analogy_pair_signature_count", "visible_condition_count",
            "nullable_signature_count",
        ],
    )
    ladder = rehearsal_ladder + current_ladder
    write_tsv(
        OUT / "gdt522_model_ladder.tsv",
        ladder,
        [
            "scope", "model_stage", "missing_relation_cost", "analogy_weight",
            "target_count", "truth_generated_count", "top1_exact_count",
            "top2_exact_count", "top3_exact_count", "top5_exact_count",
            "rank_sum", "deepest_truth_rank",
        ],
    )

    old_base = metrics([int(row["gdt521_rank"]) for row in rehearsal])
    old_selected = metrics([int(row["gdt522_rank"]) for row in rehearsal])
    current_base = metrics([int(row["gdt521_rank"]) for row in current])
    current_selected = metrics([int(row["gdt522_rank"]) for row in current])
    selected_config = next(row for row in CONFIGS if row[0] == SELECTED_STAGE)
    classes = Counter(str(row["decision_change_class"]) for row in current)
    result = {
        "experiment_id": "GDT522",
        "status": "PASS_NEAREST_LOCAL_EDIT_ANALOGY_LICENSE",
        "claim_ceiling": "EXPLORATORY_NEAREST_SURFACE_RECIPE_EDIT_LICENSE__NO_CONFIRMED_LEXEME_OR_PLAINTEXT",
        "selected_policy": {
            "stage": selected_config[0],
            "missing_relation_cost": selected_config[1],
            "analogy_weight": selected_config[2],
            "max_visible_insert": MAX_VISIBLE_INSERT,
            "max_atom_insert": MAX_ATOM_INSERT,
            "conditional_alpha": ALPHA,
            "reliability_prior": RELIABILITY_PRIOR,
            "target_orientation": "TARGET_IS_BIG_FORM_ONLY",
            "base_selection": "MINIMUM_VISIBLE_DELETION_LENGTH",
            "pair_counting": "UNIQUE_BIG_SMALL_SIGNATURE",
            "equal_recipe_policy": "VISIBLE_INSERT_MAPS_TO_NULL_ATOM_INSERT",
        },
        "full_old26_model": {
            "training_surface_count": len(analogy.forms),
            "analogy_signature_count": len(analogy.counts),
            "analogy_pair_signature_count": analogy.pair_count,
            "visible_condition_count": len(analogy.totals),
            "nullable_signature_count": sum(not key[2] for key in analogy.counts),
        },
        "old26_four_fold_gdt521_metrics": old_base,
        "old26_four_fold_gdt522_metrics": old_selected,
        "current_gdt521_metrics": current_base,
        "current_gdt522_metrics": current_selected,
        "current_net_top1_gain": current_selected["top1_exact_count"] - current_base["top1_exact_count"],
        "current_rank_sum_reduction": current_base["rank_sum"] - current_selected["rank_sum"],
        "current_decision_change_classes": dict(sorted(classes.items())),
        "remaining_top1_error_count": sum(
            int(row["gdt522_rank"]) != 1 for row in current
        ),
        "guard": "LOCAL_EDIT_ANALOGIES_ARE_RENDERER_COMPOSITION_LICENSES_ONLY__KNOWN_EVENT_AND_SURFACE_CARDS_KEEP_PRECEDENCE",
    }
    write_json(OUT / "gdt522_result.json", result)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
