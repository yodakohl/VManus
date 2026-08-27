#!/usr/bin/env python3
"""Apply GDT522 null edits directly to GDT520 renderer alignment paths."""

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
BASE = ROOT / "experiments/yolo/gdt523_path_local_null_renderer_license"
OUT = BASE / "artifacts"
G522_RUN = (
    ROOT
    / "experiments/yolo/gdt522_local_edit_analogy_license_reranker/src/run.py"
)

MAX_NULL_INSERT = 3

# stage, feature mode, weight
CONFIGS = (
    ("GDT522_BASE", "BASE", 0.0),
    ("ODDS_W025", "DOMINANT_ODDS", 0.25),
    ("ODDS_W050", "DOMINANT_ODDS", 0.50),
    ("ODDS_W075", "DOMINANT_ODDS", 0.75),
    ("ODDS_W100", "DOMINANT_ODDS", 1.00),
    ("ODDS_W125", "DOMINANT_ODDS", 1.25),
    ("EDIT_W025", "DOMINANT_EDIT", 0.25),
    ("EDIT_W010", "DOMINANT_EDIT", 0.10),
    ("EDIT_W015", "DOMINANT_EDIT", 0.15),
    ("EDIT_W020", "DOMINANT_EDIT", 0.20),
    ("EDIT_W030", "DOMINANT_EDIT", 0.30),
    ("EDIT_W035", "DOMINANT_EDIT", 0.35),
    ("EDIT_W040", "DOMINANT_EDIT", 0.40),
    ("EDIT_W050", "DOMINANT_EDIT", 0.50),
    ("EDIT_W075", "DOMINANT_EDIT", 0.75),
    ("EDIT_W100", "DOMINANT_EDIT", 1.00),
    ("EDIT_W125", "DOMINANT_EDIT", 1.25),
    ("COMBINED_W025", "DOMINANT_COMBINED", 0.25),
    ("COMBINED_W050", "DOMINANT_COMBINED", 0.50),
    ("COMBINED_W075", "DOMINANT_COMBINED", 0.75),
    ("COMBINED_W085", "DOMINANT_COMBINED", 0.85),
    ("COMBINED_W100", "DOMINANT_COMBINED", 1.00),
    ("COMBINED_W125", "DOMINANT_COMBINED", 1.25),
    ("COMBINED_W150", "DOMINANT_COMBINED", 1.50),
)
SELECTED_STAGE = "EDIT_W025"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


G522 = load_module("gdt522_core_for_gdt523", G522_RUN)
G521 = G522.G521
G520 = G522.G520
G519 = G522.G519
G518 = G522.G518
G517 = G522.G517


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


@dataclass(frozen=True)
class NullPathHit:
    segment: str
    alias: str
    visible_insert: str
    visible_position: str
    support: int
    competing_support: int
    context_atom: str
    context_null_support: int
    context_competing_support: int
    reliability: float
    log_odds: float
    edit_width: int

    @property
    def odds_feature(self) -> float:
        return self.reliability * self.log_odds

    @property
    def edit_feature(self) -> float:
        return self.reliability * self.edit_width

    @property
    def combined_feature(self) -> float:
        return self.reliability * (self.edit_width + self.log_odds)

    def trace(self) -> str:
        return (
            f"{self.segment}=>{self.alias}+NULL({self.visible_insert})"
            f"@{self.visible_position};n={self.support}/{self.support + self.competing_support}"
            f";ctx={self.context_atom}:{self.context_null_support}/"
            f"{self.context_null_support + self.context_competing_support}"
            f";odds={self.log_odds:.6f};r={self.reliability:.6f}"
            f";combined={self.combined_feature:.6f}"
        )


def pure_visible_insertions(segment: str, alias: str):
    """Contiguous surface blocks whose deletion exactly recovers the alias."""
    output: set[tuple[int, str]] = set()
    upper = min(MAX_NULL_INSERT, max(0, len(segment) - len(alias)))
    for width in range(1, upper + 1):
        for index in range(len(segment) - width + 1):
            if segment[:index] + segment[index + width :] == alias:
                output.add((index, segment[index : index + width]))
    return output


@dataclass
class NullContextModel:
    counts: Counter[tuple[str, str, str, tuple[str, ...], str]]
    totals: Counter[tuple[str, str, str]]


def train_null_context_model(
    forms: dict[str, tuple[str, ...]],
) -> NullContextModel:
    """Condition left-edge edit mappings on the first base-recipe atom."""
    counts: Counter[
        tuple[str, str, str, tuple[str, ...], str]
    ] = Counter()
    for big, big_recipe in forms.items():
        seen: set[
            tuple[str, str, str, str, tuple[str, ...], str]
        ] = set()
        upper = min(G522.MAX_VISIBLE_INSERT, max(0, len(big) - 1))
        for width in range(1, upper + 1):
            for index in range(len(big) - width + 1):
                small = big[:index] + big[index + width :]
                if small not in forms:
                    continue
                visible_pos = G522.position(index, len(big), width)
                small_recipe = forms[small]
                if visible_pos != "LEFT" or not small_recipe:
                    continue
                visible = big[index : index + width]
                context_atom = small_recipe[0]
                for atom_insert, atom_pos in G522.recipe_insertions(
                    big_recipe, small_recipe
                ):
                    seen.add(
                        (
                            small,
                            visible,
                            visible_pos,
                            context_atom,
                            atom_insert,
                            atom_pos,
                        )
                    )
        for _, visible, visible_pos, context_atom, atom_insert, atom_pos in seen:
            counts[
                (visible, visible_pos, context_atom, atom_insert, atom_pos)
            ] += 1
    totals: Counter[tuple[str, str, str]] = Counter()
    for (visible, visible_pos, context_atom, _, _), support in counts.items():
        totals[(visible, visible_pos, context_atom)] += support
    return NullContextModel(counts, totals)


def path_null_hits(
    surface: str,
    path,
    analogy: G522.AnalogyModel,
    null_context: NullContextModel,
) -> list[NullPathHit]:
    hits: list[NullPathHit] = []
    for part in path:
        segment = surface[part.start : part.end]
        choices: list[NullPathHit] = []
        for local_index, visible in pure_visible_insertions(segment, part.alias):
            global_index = part.start + local_index
            visible_pos = G522.position(global_index, len(surface), len(visible))
            if visible_pos != "LEFT" or not part.sequence:
                continue
            context_atom = part.sequence[0]
            signature = (visible, visible_pos, (), "NULL")
            support = analogy.counts[signature]
            if not support:
                continue
            total = analogy.totals[(visible, visible_pos)]
            competing = total - support
            log_odds = math.log(
                (support + G522.ALPHA) / (competing + G522.ALPHA)
            )
            if log_odds <= 0:
                continue
            context_key = (visible, visible_pos, context_atom)
            context_support = null_context.counts[
                (visible, visible_pos, context_atom, (), "NULL")
            ]
            context_competing = null_context.totals[context_key] - context_support
            context_log_odds = math.log(
                (context_support + G522.ALPHA)
                / (context_competing + G522.ALPHA)
            )
            if not context_support or context_log_odds <= 0:
                continue
            reliability = support / (support + G522.RELIABILITY_PRIOR)
            choices.append(
                NullPathHit(
                    segment,
                    part.alias,
                    visible,
                    visible_pos,
                    support,
                    competing,
                    context_atom,
                    context_support,
                    context_competing,
                    reliability,
                    log_odds,
                    len(visible),
                )
            )
        if choices:
            hits.append(
                max(
                    choices,
                    key=lambda row: (
                        row.combined_feature,
                        row.odds_feature,
                        row.visible_insert,
                    ),
                )
            )
    return hits


def path_features(
    surface: str,
    path,
    analogy: G522.AnalogyModel,
    null_context: NullContextModel,
):
    hits = path_null_hits(surface, path, analogy, null_context)
    values = {
        "DOMINANT_ODDS": sum(row.odds_feature for row in hits),
        "DOMINANT_EDIT": sum(row.edit_feature for row in hits),
        "DOMINANT_COMBINED": sum(row.combined_feature for row in hits),
    }
    trace = " | ".join(row.trace() for row in hits) if hits else "NO_DOMINANT_PATH_NULL"
    return values, trace


def gdt522_selected_config() -> tuple[float, float]:
    _, missing_cost, weight = next(
        row for row in G522.CONFIGS if row[0] == G522.SELECTED_STAGE
    )
    return missing_cost, weight


def metric_row(scope: str, config, ranks: list[int]) -> dict[str, object]:
    stage, mode, weight = config
    return {
        "scope": scope,
        "model_stage": stage,
        "null_feature_mode": mode,
        "null_feature_weight": weight,
        **G519.rank_metrics(ranks),
    }


def candidate_score_sets(
    surface: str,
    candidates,
    gdt522_scores: list[float],
    paths,
    analogy: G522.AnalogyModel,
    null_context: NullContextModel,
):
    features = []
    traces = []
    for path in paths:
        values, trace = path_features(surface, path, analogy, null_context)
        features.append(values)
        traces.append(trace)
    score_sets: dict[str, list[float]] = {}
    for stage, mode, weight in CONFIGS:
        score_sets[stage] = (
            list(gdt522_scores)
            if mode == "BASE"
            else [
                score - weight * feature[mode]
                for score, feature in zip(gdt522_scores, features)
            ]
        )
    return score_sets, features, traces


def fold_rehearsal(old: list[dict[str, str]]):
    forms = G518.invariant_surface_recipes(old, "component_recipe")
    rank_sets: dict[str, list[int]] = defaultdict(list)
    output: list[dict[str, object]] = []
    missing_cost, analogy_weight = gdt522_selected_config()
    selected_mode = next(row[1] for row in CONFIGS if row[0] == SELECTED_STAGE)
    for fold in range(G520.FOLD_COUNT):
        held = {surface for surface in forms if G520.stable_fold(surface) == fold}
        training = [row for row in old if row["surface"] not in held]
        train_forms = G518.invariant_surface_recipes(training, "component_recipe")
        analogy = G522.train_analogy_model(train_forms)
        null_context = train_null_context_model(train_forms)
        mappings, ridge, deck, boundaries, recipe_models = G521.build_base_models(
            training, "component_recipe", f"GDT523_FOLD_{fold}_TRAIN"
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
                        "gdt522_rank": 0,
                        "gdt523_rank": 0,
                        "gdt522_top1": recipe_text(candidates[0].recipe) if candidates else "NONE",
                        "gdt523_top1": "NONE",
                        "truth_null_feature": "NONE",
                        "top1_null_feature": "NONE",
                        "truth_null_trace": "NONE",
                        "top1_null_trace": "NONE",
                    }
                )
                continue
            prediction = ridge.predict(surface)
            matrix = G519.segment_matrix(
                surface, G519.needed_renderer_sequences(candidates, deck), deck
            )
            gdt522_scores: list[float] = []
            paths = []
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
                    surface, candidate.recipe, missing_cost
                )
                gdt522_scores.append(
                    gdt521_score - analogy_weight * analogy_bonus
                )
                paths.append(path)
            score_sets, features, traces = candidate_score_sets(
                surface,
                candidates,
                gdt522_scores,
                paths,
                analogy,
                null_context,
            )
            orders: dict[str, list[int]] = {}
            for stage, _, _ in CONFIGS:
                rank, order = G519.rank_by_score(
                    candidates, truth, score_sets[stage]
                )
                rank_sets[stage].append(rank)
                orders[stage] = order
            base_top = orders["GDT522_BASE"][0]
            top = orders[SELECTED_STAGE][0]
            output.append(
                {
                    "fold": fold,
                    "surface": surface,
                    "truth_recipe": recipe_text(truth),
                    "candidate_count_capped": len(candidates),
                    "truth_generated": "YES",
                    "gdt522_rank": rank_sets["GDT522_BASE"][-1],
                    "gdt523_rank": rank_sets[SELECTED_STAGE][-1],
                    "gdt522_top1": recipe_text(candidates[base_top].recipe),
                    "gdt523_top1": recipe_text(candidates[top].recipe),
                    "truth_null_feature": f"{features[truth_index][selected_mode]:.9f}",
                    "top1_null_feature": f"{features[top][selected_mode]:.9f}",
                    "truth_null_trace": traces[truth_index],
                    "top1_null_trace": traces[top],
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
    null_context = train_null_context_model(forms)
    missing_cost, analogy_weight = gdt522_selected_config()
    mappings, ridge, deck, boundaries, recipe_models = G521.build_base_models(
        old, "component_recipe", "GDT523_FULL_OLD26"
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
    tradeoff_rows: list[dict[str, object]] = []
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
        gdt522_scores: list[float] = []
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
                surface, candidate.recipe, missing_cost
            )
            gdt522_scores.append(gdt521_score - analogy_weight * analogy_bonus)
            paths.append(path)
        score_sets, features, traces = candidate_score_sets(
            surface,
            candidates,
            gdt522_scores,
            paths,
            analogy,
            null_context,
        )
        orders: dict[str, list[int]] = {}
        for stage, _, _ in CONFIGS:
            rank, order = G519.rank_by_score(candidates, truth, score_sets[stage])
            rank_sets[stage].append(rank)
            orders[stage] = order
        truth_index = next(
            index for index, candidate in enumerate(candidates) if candidate.recipe == truth
        )
        base_top = orders["GDT522_BASE"][0]
        top = orders[SELECTED_STAGE][0]
        base_rank = rank_sets["GDT522_BASE"][-1]
        selected_rank = rank_sets[SELECTED_STAGE][-1]
        if base_rank == 1 and selected_rank == 1:
            change = "GDT522_CORRECT_PRESERVED"
        elif base_rank != 1 and selected_rank == 1:
            change = "GDT522_ERROR_CORRECTED"
        elif base_rank == 1 and selected_rank != 1:
            change = "GDT522_CORRECT_LOST"
        elif candidates[base_top].recipe != candidates[top].recipe:
            change = "ERROR_CHANGED_STILL_WRONG"
        else:
            change = "GDT522_ERROR_UNCHANGED"
        output.append(
            {
                "surface": surface,
                "occurrence_count": target["occurrence_count"],
                "physical_pages": target["physical_pages"],
                "truth_recipe": recipe_text(truth),
                "candidate_count_capped": len(candidates),
                "gdt522_rank": base_rank,
                "gdt522_top1": recipe_text(candidates[base_top].recipe),
                "gdt523_rank": selected_rank,
                "gdt523_top1": recipe_text(candidates[top].recipe),
                "gdt523_top5": " | ".join(
                    recipe_text(candidates[index].recipe)
                    for index in orders[SELECTED_STAGE][:5]
                ),
                "truth_gdt522_score": f"{gdt522_scores[truth_index]:.9f}",
                "truth_null_feature": f"{features[truth_index][selected_mode]:.9f}",
                "truth_gdt523_score": f"{score_sets[SELECTED_STAGE][truth_index]:.9f}",
                "truth_null_trace": traces[truth_index],
                "top1_gdt522_score": f"{gdt522_scores[top]:.9f}",
                "top1_null_feature": f"{features[top][selected_mode]:.9f}",
                "top1_gdt523_score": f"{score_sets[SELECTED_STAGE][top]:.9f}",
                "top1_null_trace": traces[top],
                "top1_alignment_trace": G520.path_text(surface, paths[top]),
                "decision_change_class": change,
                "working_policy": "KNOWN_EVENT_OR_SURFACE_RECIPE_STILL_WINS__DOMINANT_NULL_EDIT_DISCOUNTS_ONLY_EXPLICIT_RENDERER_PATH_INSERTIONS",
            }
        )
        if surface in {"qef", "qocthedy", "qoekedy", "qopaiin"}:
            for stage, mode, weight in CONFIGS:
                config_top = orders[stage][0]
                tradeoff_rows.append(
                    {
                        "surface": surface,
                        "truth_recipe": recipe_text(truth),
                        "model_stage": stage,
                        "null_feature_mode": mode,
                        "null_feature_weight": weight,
                        "truth_rank": rank_sets[stage][-1],
                        "top1_recipe": recipe_text(candidates[config_top].recipe),
                        "truth_null_feature": (
                            "0.000000000"
                            if mode == "BASE"
                            else f"{features[truth_index][mode]:.9f}"
                        ),
                        "top1_null_feature": (
                            "0.000000000"
                            if mode == "BASE"
                            else f"{features[config_top][mode]:.9f}"
                        ),
                        "truth_score": f"{score_sets[stage][truth_index]:.9f}",
                        "top1_score": f"{score_sets[stage][config_top]:.9f}",
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
                        "gdt522_rank": orders["GDT522_BASE"].index(index) + 1,
                        "gdt523_rank": selected_candidate_rank,
                        "candidate_recipe": recipe_text(candidates[index].recipe),
                        "gdt522_score": f"{gdt522_scores[index]:.9f}",
                        "null_feature": f"{features[index][selected_mode]:.9f}",
                        "gdt523_score": f"{score_sets[SELECTED_STAGE][index]:.9f}",
                        "null_trace": traces[index],
                        "alignment_trace": G520.path_text(surface, paths[index]),
                    }
                )
    ladder = [
        metric_row("CURRENT_159_OLD26_TO_NEW4", config, rank_sets[config[0]])
        for config in CONFIGS
    ]
    return output, candidate_rows, tradeoff_rows, ladder, analogy, null_context


def null_signature_rows(analogy: G522.AnalogyModel):
    output = []
    for signature in sorted(analogy.counts):
        visible, visible_pos, atom_insert, atom_pos = signature
        if atom_insert or atom_pos != "NULL":
            continue
        support = analogy.counts[signature]
        total = analogy.totals[(visible, visible_pos)]
        competing = total - support
        reliability = support / (support + G522.RELIABILITY_PRIOR)
        log_odds = math.log(
            (support + G522.ALPHA) / (competing + G522.ALPHA)
        )
        output.append(
            {
                "visible_insert": visible,
                "visible_position": visible_pos,
                "null_support": support,
                "competing_support": competing,
                "conditional_total": total,
                "null_log_odds": f"{log_odds:.9f}",
                "reliability": f"{reliability:.9f}",
                "dominant_null": "YES" if log_odds > 0 else "NO",
                "one_char_combined_feature": f"{reliability * (1 + log_odds):.9f}",
            }
        )
    return output


def null_context_rows(model: NullContextModel):
    output = []
    for visible, visible_pos, context_atom in sorted(model.totals):
        support = model.counts[
            (visible, visible_pos, context_atom, (), "NULL")
        ]
        total = model.totals[(visible, visible_pos, context_atom)]
        competing = total - support
        log_odds = math.log(
            (support + G522.ALPHA) / (competing + G522.ALPHA)
        )
        output.append(
            {
                "visible_insert": visible,
                "visible_position": visible_pos,
                "base_edge_atom": context_atom,
                "null_support": support,
                "competing_support": competing,
                "conditional_total": total,
                "context_null_log_odds": f"{log_odds:.9f}",
                "context_dominant_null": "YES" if support and log_odds > 0 else "NO",
            }
        )
    return output


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    old = read_tsv(G518.G407_RUNNING)
    selected = read_tsv(G518.G516_SELECTED)
    targets = read_tsv(G518.G516_NEW)
    rehearsal, old_ladder = fold_rehearsal(old)
    (
        current,
        candidates,
        tradeoffs,
        current_ladder,
        analogy,
        null_context,
    ) = current_benchmark(old, selected, targets)

    rehearsal_fields = [
        "fold", "surface", "truth_recipe", "candidate_count_capped",
        "truth_generated", "gdt522_rank", "gdt523_rank", "gdt522_top1",
        "gdt523_top1", "truth_null_feature", "top1_null_feature",
        "truth_null_trace", "top1_null_trace",
    ]
    current_fields = [
        "surface", "occurrence_count", "physical_pages", "truth_recipe",
        "candidate_count_capped", "gdt522_rank", "gdt522_top1", "gdt523_rank",
        "gdt523_top1", "gdt523_top5", "truth_gdt522_score",
        "truth_null_feature", "truth_gdt523_score", "truth_null_trace",
        "top1_gdt522_score", "top1_null_feature", "top1_gdt523_score",
        "top1_null_trace", "top1_alignment_trace", "decision_change_class",
        "working_policy",
    ]
    write_tsv(
        OUT / "gdt523_1558_four_fold_path_null_rehearsal.tsv",
        rehearsal,
        rehearsal_fields,
    )
    write_tsv(OUT / "gdt523_159_path_null_rerank.tsv", current, current_fields)
    write_tsv(
        OUT / "gdt523_changed_decision_atlas.tsv",
        [row for row in current if row["gdt522_top1"] != row["gdt523_top1"]],
        current_fields,
    )
    write_tsv(
        OUT / "gdt523_remaining_top1_error_atlas.tsv",
        [row for row in current if int(row["gdt523_rank"]) != 1],
        current_fields,
    )
    write_tsv(
        OUT / "gdt523_candidate_score_atlas.tsv",
        candidates,
        [
            "surface", "truth_recipe", "candidate_is_truth",
            "gdt517_compiler_rank", "gdt522_rank", "gdt523_rank",
            "candidate_recipe", "gdt522_score", "null_feature",
            "gdt523_score", "null_trace", "alignment_trace",
        ],
    )
    write_tsv(
        OUT / "gdt523_q_path_tradeoff_atlas.tsv",
        tradeoffs,
        [
            "surface", "truth_recipe", "model_stage", "null_feature_mode",
            "null_feature_weight", "truth_rank", "top1_recipe",
            "truth_null_feature", "top1_null_feature", "truth_score",
            "top1_score",
        ],
    )
    null_rows = null_signature_rows(analogy)
    write_tsv(
        OUT / "gdt523_path_null_license_atlas.tsv",
        null_rows,
        [
            "visible_insert", "visible_position", "null_support",
            "competing_support", "conditional_total", "null_log_odds",
            "reliability", "dominant_null", "one_char_combined_feature",
        ],
    )
    context_rows = null_context_rows(null_context)
    write_tsv(
        OUT / "gdt523_left_null_atom_context_atlas.tsv",
        context_rows,
        [
            "visible_insert", "visible_position", "base_edge_atom",
            "null_support", "competing_support", "conditional_total",
            "context_null_log_odds", "context_dominant_null",
        ],
    )
    ladder = old_ladder + current_ladder
    write_tsv(
        OUT / "gdt523_model_ladder.tsv",
        ladder,
        [
            "scope", "model_stage", "null_feature_mode", "null_feature_weight",
            "target_count", "truth_generated_count", "top1_exact_count",
            "top2_exact_count", "top3_exact_count", "top5_exact_count",
            "rank_sum", "deepest_truth_rank",
        ],
    )

    old_base = G519.rank_metrics([int(row["gdt522_rank"]) for row in rehearsal])
    old_selected = G519.rank_metrics([int(row["gdt523_rank"]) for row in rehearsal])
    current_base = G519.rank_metrics([int(row["gdt522_rank"]) for row in current])
    current_selected = G519.rank_metrics([int(row["gdt523_rank"]) for row in current])
    selected_config = next(row for row in CONFIGS if row[0] == SELECTED_STAGE)
    classes = Counter(row["decision_change_class"] for row in current)
    result = {
        "experiment_id": "GDT523",
        "status": "PASS_PATH_LOCAL_DOMINANT_NULL_LICENSE",
        "claim_ceiling": "EXPLORATORY_RENDERER_PATH_NULL_EDIT_LICENSE__NO_CONFIRMED_LEXEME_OR_PLAINTEXT",
        "selected_policy": {
            "stage": selected_config[0],
            "feature_mode": selected_config[1],
            "feature_weight": selected_config[2],
            "max_visible_null_insert": MAX_NULL_INSERT,
            "activation": "PURE_LEFT_CONTIGUOUS_SURFACE_INSERTION_RELATIVE_TO_SELECTED_RENDERER_ALIAS",
            "dominance_gate": "GLOBAL_AND_BASE_FIRST_ATOM_NULL_LOG_ODDS_GT_ZERO",
            "feature": "RELIABILITY_TIMES_VISIBLE_EDIT_WIDTH",
        },
        "license_inventory": {
            "nullable_signature_count": len(null_rows),
            "dominant_nullable_signature_count": sum(
                row["dominant_null"] == "YES" for row in null_rows
            ),
            "left_atom_context_count": len(context_rows),
            "dominant_left_atom_context_count": sum(
                row["context_dominant_null"] == "YES" for row in context_rows
            ),
        },
        "old26_four_fold_gdt522_metrics": old_base,
        "old26_four_fold_gdt523_metrics": old_selected,
        "current_gdt522_metrics": current_base,
        "current_gdt523_metrics": current_selected,
        "current_net_top1_gain": current_selected["top1_exact_count"] - current_base["top1_exact_count"],
        "current_rank_sum_reduction": current_base["rank_sum"] - current_selected["rank_sum"],
        "current_decision_change_classes": dict(sorted(classes.items())),
        "remaining_top1_error_count": sum(int(row["gdt523_rank"]) != 1 for row in current),
        "guard": "PATH_NULL_LICENSE_DISCOUNTS_ONLY_EXPLICIT_VISIBLE_INSERTIONS__KNOWN_EVENT_AND_SURFACE_CARDS_KEEP_PRECEDENCE",
    }
    write_json(OUT / "gdt523_result.json", result)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
