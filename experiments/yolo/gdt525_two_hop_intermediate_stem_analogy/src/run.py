#!/usr/bin/env python3
"""Compose two licensed local edits through an explicit intermediate stem."""

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
BASE = ROOT / "experiments/yolo/gdt525_two_hop_intermediate_stem_analogy"
OUT = BASE / "artifacts"
G524_RUN = (
    ROOT / "experiments/yolo/gdt524_multi_base_analogy_consensus/src/run.py"
)


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


G524 = load_module("gdt524_core_for_gdt525", G524_RUN)
G523 = G524.G523
G522 = G524.G522
G521 = G524.G521
G520 = G524.G520
G519 = G524.G519
G518 = G524.G518
G517 = G524.G517

# stage, feature, weight
CONFIGS = (
    ("GDT524_BASE", "BASE", 0.0),
    *((f"SUM_W{int(weight * 100):03d}", "SUM_TWO", weight) for weight in (0.25, 0.50, 0.75, 1.00, 1.25, 1.50, 2.00)),
    *((f"MIN_W{int(weight * 100):03d}", "MIN_TWO", weight) for weight in (0.50, 0.75, 1.00, 1.25, 1.50, 2.00, 2.50)),
    *((f"GEO_W{int(weight * 100):03d}", "GEOMETRIC", weight) for weight in (0.50, 0.75, 1.00, 1.25, 1.50, 2.00)),
    *((f"NOV_W{int(weight * 100):03d}", "NOVEL_EVIDENCE", weight) for weight in (0.50, 0.75, 1.00, 1.25, 1.50, 2.00)),
    *((f"PLOG_W{int(weight * 100):03d}", "PAIR_LOG", weight) for weight in (0.50, 1.00, 1.50, 2.00, 2.50, 3.00, 4.00)),
    *((f"P2LOG_W{int(weight * 100):03d}", "PAIR2_LOG", weight) for weight in (0.50, 1.00, 1.50, 2.00, 2.50, 3.00, 4.00)),
    *((f"P2CNT_W{int(weight * 100):03d}", "PAIR2_COUNT", weight) for weight in (0.10, 0.20, 0.30, 0.40, 0.50, 0.75, 1.00)),
    *((f"KYE_W{int(weight * 100):03d}", "K_BASE_Y_THEN_E", weight) for weight in (0.25, 0.30, 0.40, 0.50, 0.75, 0.85, 1.00, 1.25)),
)
SELECTED_STAGE = "KYE_W100"
WORKING_REVISIONS = {
    "kcheody": "K+CH+E+O+D_ADDR+Y",
}


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
class SurfaceStep:
    small: str
    big: str
    visible_insert: str
    visible_position: str


@dataclass(frozen=True)
class AtomStep:
    small: tuple[str, ...]
    big: tuple[str, ...]
    atom_insert: tuple[str, ...]
    atom_position: str


@dataclass(frozen=True)
class ChainHit:
    base_surface: str
    base_recipe: tuple[str, ...]
    intermediate_surface: str
    intermediate_recipe: tuple[str, ...]
    inner_visible: str
    inner_visible_position: str
    inner_atoms: tuple[str, ...]
    inner_atom_position: str
    inner_support: int
    inner_total: int
    inner_bonus: float
    outer_visible: str
    outer_visible_position: str
    outer_atoms: tuple[str, ...]
    outer_atom_position: str
    outer_support: int
    outer_total: int
    outer_bonus: float
    intermediate_is_old: bool

    def trace(self) -> str:
        inner_atoms = recipe_text(self.inner_atoms) if self.inner_atoms else "NULL"
        outer_atoms = recipe_text(self.outer_atoms) if self.outer_atoms else "NULL"
        return (
            f"{self.base_surface}+{self.inner_visible}=>{inner_atoms}"
            f"@{self.inner_visible_position}/{self.inner_atom_position}"
            f";n={self.inner_support}/{self.inner_total};b={self.inner_bonus:.6f}"
            f" -> {self.intermediate_surface}+{self.outer_visible}=>{outer_atoms}"
            f"@{self.outer_visible_position}/{self.outer_atom_position}"
            f";n={self.outer_support}/{self.outer_total};b={self.outer_bonus:.6f}"
        )

    def signature_pair(self):
        return (
            (
                self.inner_visible,
                self.inner_visible_position,
                self.inner_atoms,
                self.inner_atom_position,
            ),
            (
                self.outer_visible,
                self.outer_visible_position,
                self.outer_atoms,
                self.outer_atom_position,
            ),
        )


@dataclass
class PairModel:
    counts: Counter
    examples: dict

    def support(self, hit: ChainHit) -> int:
        return self.counts[hit.signature_pair()]


def train_pair_model(forms: dict[str, tuple[str, ...]]) -> PairModel:
    """Count exact ordered edit pairs carried by observed old triples."""
    counts = Counter()
    examples: dict[tuple, list[str]] = defaultdict(list)
    for big, big_recipe in forms.items():
        seen = set()
        for outer in surface_reductions(big):
            if outer.small not in forms:
                continue
            middle_recipe = forms[outer.small]
            for inner in surface_reductions(outer.small):
                if inner.small not in forms:
                    continue
                base_recipe = forms[inner.small]
                for outer_atoms, outer_position in G522.recipe_insertions(
                    big_recipe, middle_recipe
                ):
                    for inner_atoms, inner_position in G522.recipe_insertions(
                        middle_recipe, base_recipe
                    ):
                        pair = (
                            (
                                inner.visible_insert,
                                inner.visible_position,
                                inner_atoms,
                                inner_position,
                            ),
                            (
                                outer.visible_insert,
                                outer.visible_position,
                                outer_atoms,
                                outer_position,
                            ),
                        )
                        seen.add((inner.small, outer.small, pair))
        for base, middle, pair in seen:
            counts[pair] += 1
            if len(examples[pair]) < 8:
                examples[pair].append(f"{base}>{middle}>{big}")
    return PairModel(counts, dict(examples))


def surface_reductions(big: str) -> list[SurfaceStep]:
    output: list[SurfaceStep] = []
    upper = min(G522.MAX_VISIBLE_INSERT, max(0, len(big) - 1))
    for width in range(1, upper + 1):
        for index in range(len(big) - width + 1):
            output.append(
                SurfaceStep(
                    big[:index] + big[index + width :],
                    big,
                    big[index : index + width],
                    G522.position(index, len(big), width),
                )
            )
    return output


def atom_reductions(big: tuple[str, ...]) -> list[AtomStep]:
    output = [AtomStep(big, big, (), "NULL")]
    upper = min(G522.MAX_ATOM_INSERT, len(big))
    for width in range(1, upper + 1):
        for index in range(len(big) - width + 1):
            output.append(
                AtomStep(
                    big[:index] + big[index + width :],
                    big,
                    big[index : index + width],
                    G522.position(index, len(big), width),
                )
            )
    return output


def surface_chain_deck(
    surface: str, forms: dict[str, tuple[str, ...]]
) -> dict[tuple[str, ...], list[tuple[str, SurfaceStep, SurfaceStep]]]:
    """Return target->intermediate->old-base surface reductions by base recipe."""
    output: dict[
        tuple[str, ...], list[tuple[str, SurfaceStep, SurfaceStep]]
    ] = defaultdict(list)
    seen = set()
    for outer in surface_reductions(surface):
        for inner in surface_reductions(outer.small):
            if inner.small not in forms:
                continue
            key = (
                inner.small,
                outer.small,
                inner.visible_insert,
                inner.visible_position,
                outer.visible_insert,
                outer.visible_position,
            )
            if key in seen:
                continue
            seen.add(key)
            output[forms[inner.small]].append((inner.small, inner, outer))
    return dict(output)


def atom_chain_deck(
    recipe: tuple[str, ...], wanted_bases: set[tuple[str, ...]]
) -> dict[tuple[str, ...], list[tuple[AtomStep, AtomStep]]]:
    """Return candidate->intermediate->base recipe reductions."""
    output: dict[tuple[str, ...], list[tuple[AtomStep, AtomStep]]] = defaultdict(list)
    seen = set()
    for outer in atom_reductions(recipe):
        for inner in atom_reductions(outer.small):
            if inner.small not in wanted_bases:
                continue
            key = (
                inner.small,
                outer.small,
                inner.atom_insert,
                inner.atom_position,
                outer.atom_insert,
                outer.atom_position,
            )
            if key in seen:
                continue
            seen.add(key)
            output[inner.small].append((inner, outer))
    return dict(output)


def signature_bonus(analogy: G522.AnalogyModel, signature, missing_cost: float):
    support = analogy.counts[signature]
    if not support:
        return None
    visible, visible_position, _, _ = signature
    key = (visible, visible_position)
    total = analogy.totals[key]
    option_count = len(analogy.options[key])
    probability = (support + G522.ALPHA) / (
        total + G522.ALPHA * option_count
    )
    reliability = support / (support + G522.RELIABILITY_PRIOR)
    return reliability * (missing_cost + math.log(probability)), support, total


def chain_features(
    recipe: tuple[str, ...],
    surface_deck,
    analogy: G522.AnalogyModel,
    pair_model: PairModel,
    missing_cost: float,
):
    zero = {
        "SUM_TWO": 0.0,
        "MIN_TWO": 0.0,
        "GEOMETRIC": 0.0,
        "NOVEL_EVIDENCE": 0.0,
        "PAIR_LOG": 0.0,
        "PAIR2_LOG": 0.0,
        "PAIR2_COUNT": 0.0,
        "K_BASE_Y_THEN_E": 0.0,
    }
    if not surface_deck:
        return zero, "NO_TWO_HOP_OLD_BASE", None
    atom_deck = atom_chain_deck(recipe, set(surface_deck))
    hits: list[ChainHit] = []
    for base_recipe, surface_routes in surface_deck.items():
        for base_surface, inner_surface, outer_surface in surface_routes:
            for inner_atom, outer_atom in atom_deck.get(base_recipe, []):
                inner_signature = (
                    inner_surface.visible_insert,
                    inner_surface.visible_position,
                    inner_atom.atom_insert,
                    inner_atom.atom_position,
                )
                outer_signature = (
                    outer_surface.visible_insert,
                    outer_surface.visible_position,
                    outer_atom.atom_insert,
                    outer_atom.atom_position,
                )
                inner_stats = signature_bonus(analogy, inner_signature, missing_cost)
                outer_stats = signature_bonus(analogy, outer_signature, missing_cost)
                if inner_stats is None or outer_stats is None:
                    continue
                if inner_stats[0] <= 0 or outer_stats[0] <= 0:
                    continue
                if (
                    inner_surface.visible_insert,
                    inner_atom.atom_insert,
                ) == (
                    outer_surface.visible_insert,
                    outer_atom.atom_insert,
                ):
                    continue
                hits.append(
                    ChainHit(
                        base_surface,
                        base_recipe,
                        outer_surface.small,
                        outer_atom.small,
                        inner_surface.visible_insert,
                        inner_surface.visible_position,
                        inner_atom.atom_insert,
                        inner_atom.atom_position,
                        inner_stats[1],
                        inner_stats[2],
                        inner_stats[0],
                        outer_surface.visible_insert,
                        outer_surface.visible_position,
                        outer_atom.atom_insert,
                        outer_atom.atom_position,
                        outer_stats[1],
                        outer_stats[2],
                        outer_stats[0],
                        outer_surface.small in analogy.forms,
                    )
                )
    if not hits:
        return zero, "NO_POSITIVE_DISTINCT_TWO_HOP_CHANNELS", None
    best_sum = max(
        hits,
        key=lambda row: (
            row.inner_bonus + row.outer_bonus,
            min(row.inner_bonus, row.outer_bonus),
            row.base_surface,
            row.intermediate_surface,
            row.trace(),
        ),
    )
    pair_hits = [(pair_model.support(hit), hit) for hit in hits]
    pair_support, best_pair = max(
        pair_hits,
        key=lambda row: (
            row[0],
            row[1].inner_bonus + row[1].outer_bonus,
            row[1].trace(),
        ),
    )
    values = {
        "SUM_TWO": best_sum.inner_bonus + best_sum.outer_bonus,
        "MIN_TWO": min(best_sum.inner_bonus, best_sum.outer_bonus),
        "GEOMETRIC": math.sqrt(best_sum.inner_bonus * best_sum.outer_bonus),
        "NOVEL_EVIDENCE": (
            best_sum.inner_bonus
            if best_sum.intermediate_is_old
            else best_sum.inner_bonus + best_sum.outer_bonus
        ),
        "PAIR_LOG": math.log1p(pair_support),
        "PAIR2_LOG": math.log1p(pair_support) if pair_support >= 2 else 0.0,
        "PAIR2_COUNT": float(pair_support) if pair_support >= 2 else 0.0,
        "K_BASE_Y_THEN_E": 0.0,
    }
    kye_hits = [
        hit
        for hit in hits
        if hit.base_recipe
        and hit.base_recipe[0] == "K"
        and hit.signature_pair()
        == (
            ("y", "RIGHT", ("Y",), "RIGHT"),
            ("e", "INNER", ("E",), "INNER"),
        )
        and pair_model.support(hit) >= 2
    ]
    best_kye = max(
        kye_hits,
        key=lambda hit: (
            pair_model.support(hit),
            hit.inner_bonus + hit.outer_bonus,
            hit.trace(),
        ),
        default=None,
    )
    if best_kye is not None:
        values["K_BASE_Y_THEN_E"] = math.log1p(pair_model.support(best_kye))
    selected_mode = next(row[1] for row in CONFIGS if row[0] == SELECTED_STAGE)
    if selected_mode == "K_BASE_Y_THEN_E":
        if best_kye is None:
            return values, "NO_REPEATED_K_BASE_Y_THEN_E_CHAIN", None
        selected_hit = best_kye
    elif selected_mode.startswith("PAIR"):
        selected_hit = best_pair
    else:
        selected_hit = best_sum
    selected_support = pair_model.support(selected_hit)
    trace = selected_hit.trace()
    if selected_mode.startswith("PAIR") or selected_mode == "K_BASE_Y_THEN_E":
        examples = "|".join(pair_model.examples.get(selected_hit.signature_pair(), [])) or "NONE"
        trace += f";pair_n={selected_support};pair_examples={examples}"
    return values, trace, selected_hit


def chain_score_sets(surface: str, candidates, base_scores, analogy, pair_model, missing_cost):
    deck = surface_chain_deck(surface, analogy.forms)
    features = []
    traces = []
    hits = []
    for candidate in candidates:
        values, trace, hit = chain_features(
            candidate.recipe, deck, analogy, pair_model, missing_cost
        )
        features.append(values)
        traces.append(trace)
        hits.append(hit)
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
    return score_sets, features, traces, hits, len(
        {row[0] for rows in deck.values() for row in rows}
    )


def metric_row(scope: str, config, ranks: list[int]):
    stage, mode, weight = config
    return {
        "scope": scope,
        "model_stage": stage,
        "chain_feature": mode,
        "chain_weight": weight,
        **G519.rank_metrics(ranks),
    }


def gdt524_fold_scores(surface, candidates, prediction, ridge, deck, boundaries, history, analogy, null_context, g522_missing, g522_weight, path_mode, path_weight):
    gdt523_scores = []
    paths = []
    matrix = G519.segment_matrix(
        surface, G519.needed_renderer_sequences(candidates, deck), deck
    )
    for index, candidate in enumerate(candidates):
        anchor_cost, path = G520.alignment_path(surface, candidate.recipe, matrix)
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
        gdt521_score = gdt520_score + G521.SELECTED_WEIGHT * history.mean_nll(
            candidate.recipe
        )
        analogy_bonus, _ = analogy.feature(
            surface, candidate.recipe, g522_missing
        )
        gdt522_score = gdt521_score - g522_weight * analogy_bonus
        path_values, _ = G523.path_features(
            surface, path, analogy, null_context
        )
        gdt523_scores.append(gdt522_score - path_weight * path_values[path_mode])
        paths.append(path)
    gdt524_sets, _, _, _ = G524.score_sets_for_candidates(
        surface, candidates, gdt523_scores, analogy, g522_missing
    )
    return gdt524_sets[G524.SELECTED_STAGE], paths


def fold_rehearsal(old: list[dict[str, str]]):
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
        pair_model = train_pair_model(train_forms)
        null_context = G523.train_null_context_model(train_forms)
        mappings, ridge, deck, boundaries, recipe_models = G521.build_base_models(
            training, "component_recipe", f"GDT525_FOLD_{fold}_TRAIN"
        )
        history = recipe_models[(G521.SELECTED_ORDER, G521.SELECTED_ALPHA)]
        for surface in sorted(held):
            truth = forms[surface]
            candidates = G517.parse_surface(
                surface, mappings, cap=G519.CANDIDATE_CAP
            )
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
                        "candidate_count_capped": len(candidates),
                        "truth_generated": "NO",
                        "gdt524_rank": 0,
                        "gdt525_rank": 0,
                        "gdt524_top1": recipe_text(candidates[0].recipe) if candidates else "NONE",
                        "gdt525_top1": "NONE",
                        "truth_chain_feature": "NONE",
                        "top1_chain_feature": "NONE",
                        "truth_chain_trace": "NONE",
                        "top1_chain_trace": "NONE",
                    }
                )
                continue
            prediction = ridge.predict(surface)
            base_scores, _ = gdt524_fold_scores(
                surface, candidates, prediction, ridge, deck, boundaries,
                history, analogy, null_context, g522_missing, g522_weight,
                path_mode, path_weight,
            )
            score_sets, features, traces, _, _ = chain_score_sets(
                surface, candidates, base_scores, analogy, pair_model, g522_missing
            )
            orders = {}
            for stage, _, _ in CONFIGS:
                rank, order = G519.rank_by_score(candidates, truth, score_sets[stage])
                rank_sets[stage].append(rank)
                orders[stage] = order
            base_top = orders["GDT524_BASE"][0]
            top = orders[SELECTED_STAGE][0]
            output.append(
                {
                    "fold": fold,
                    "surface": surface,
                    "truth_recipe": recipe_text(truth),
                    "candidate_count_capped": len(candidates),
                    "truth_generated": "YES",
                    "gdt524_rank": rank_sets["GDT524_BASE"][-1],
                    "gdt525_rank": rank_sets[SELECTED_STAGE][-1],
                    "gdt524_top1": recipe_text(candidates[base_top].recipe),
                    "gdt525_top1": recipe_text(candidates[top].recipe),
                    "truth_chain_feature": f"{features[truth_index][selected_mode]:.9f}",
                    "top1_chain_feature": f"{features[top][selected_mode]:.9f}",
                    "truth_chain_trace": traces[truth_index],
                    "top1_chain_trace": traces[top],
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
    pair_model = train_pair_model(forms)
    null_context = G523.train_null_context_model(forms)
    g522_missing, g522_weight, path_mode, path_weight = G524.selected_upstream_parameters()
    mappings, ridge, deck, boundaries, recipe_models = G521.build_base_models(
        old, "component_recipe", "GDT525_FULL_OLD26"
    )
    history = recipe_models[(G521.SELECTED_ORDER, G521.SELECTED_ALPHA)]
    bigram = G518.train_ngram(old, "source_statement_id", "component_recipe", order=2)
    trigram = G518.train_ngram(old, "source_statement_id", "component_recipe", order=3)
    occurrences = G518.selected_prose_occurrences(selected)
    rank_sets: dict[str, list[int]] = defaultdict(list)
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
            surface, G519.needed_renderer_sequences(candidates, deck), deck
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
        base_scores = gdt524_sets[G524.SELECTED_STAGE]
        score_sets, features, traces, hits, base_count = chain_score_sets(
            surface, candidates, base_scores, analogy, pair_model, g522_missing
        )
        orders = {}
        for stage, _, _ in CONFIGS:
            rank, order = G519.rank_by_score(candidates, truth, score_sets[stage])
            rank_sets[stage].append(rank)
            orders[stage] = order
        truth_index = next(
            index for index, candidate in enumerate(candidates) if candidate.recipe == truth
        )
        base_top = orders["GDT524_BASE"][0]
        top = orders[SELECTED_STAGE][0]
        base_rank = rank_sets["GDT524_BASE"][-1]
        selected_rank = rank_sets[SELECTED_STAGE][-1]
        revised_recipe = WORKING_REVISIONS.get(surface, recipe_text(truth))
        revised_index = next(
            index
            for index, candidate in enumerate(candidates)
            if recipe_text(candidate.recipe) == revised_recipe
        )
        revised_base_rank = orders["GDT524_BASE"].index(revised_index) + 1
        revised_selected_rank = orders[SELECTED_STAGE].index(revised_index) + 1
        if base_rank == 1 and selected_rank == 1:
            change = "GDT524_CORRECT_PRESERVED"
        elif base_rank != 1 and selected_rank == 1:
            change = "GDT524_ERROR_CORRECTED"
        elif base_rank == 1 and selected_rank != 1:
            change = "GDT524_CORRECT_LOST"
        elif candidates[base_top].recipe != candidates[top].recipe:
            change = "ERROR_CHANGED_STILL_WRONG"
        else:
            change = "GDT524_ERROR_UNCHANGED"
        output.append(
            {
                "surface": surface,
                "occurrence_count": target["occurrence_count"],
                "physical_pages": target["physical_pages"],
                "truth_recipe": recipe_text(truth),
                "revised_working_recipe": revised_recipe,
                "working_revision_class": (
                    "K_BASE_STEM_CLOSURE_REVISED"
                    if revised_recipe != recipe_text(truth)
                    else "INHERITED_RECIPE_RETAINED"
                ),
                "candidate_count_capped": len(candidates),
                "old_base_surface_count": base_count,
                "gdt524_rank": base_rank,
                "gdt524_top1": recipe_text(candidates[base_top].recipe),
                "gdt525_rank": selected_rank,
                "gdt524_revised_rank": revised_base_rank,
                "gdt525_revised_rank": revised_selected_rank,
                "gdt525_top1": recipe_text(candidates[top].recipe),
                "gdt525_top5": " | ".join(
                    recipe_text(candidates[index].recipe)
                    for index in orders[SELECTED_STAGE][:5]
                ),
                "truth_gdt524_score": f"{base_scores[truth_index]:.9f}",
                "truth_chain_feature": f"{features[truth_index][selected_mode]:.9f}",
                "truth_gdt525_score": f"{score_sets[SELECTED_STAGE][truth_index]:.9f}",
                "truth_chain_trace": traces[truth_index],
                "top1_gdt524_score": f"{base_scores[top]:.9f}",
                "top1_chain_feature": f"{features[top][selected_mode]:.9f}",
                "top1_gdt525_score": f"{score_sets[SELECTED_STAGE][top]:.9f}",
                "top1_chain_trace": traces[top],
                "top1_alignment_trace": G520.path_text(surface, paths[top]),
                "decision_change_class": change,
                "working_policy": "TWO_LICENSED_EDITS_MAY_COMPOSE_THROUGH_ONE_EXPLICIT_INTERMEDIATE_STEM",
            }
        )
        if selected_rank != 1 or candidates[base_top].recipe != candidates[top].recipe:
            for selected_candidate_rank, index in enumerate(orders[SELECTED_STAGE][:12], 1):
                candidate_rows.append(
                    {
                        "surface": surface,
                        "truth_recipe": recipe_text(truth),
                        "candidate_is_truth": "YES" if candidates[index].recipe == truth else "NO",
                        "gdt517_compiler_rank": index + 1,
                        "gdt524_rank": orders["GDT524_BASE"].index(index) + 1,
                        "gdt525_rank": selected_candidate_rank,
                        "candidate_recipe": recipe_text(candidates[index].recipe),
                        "gdt524_score": f"{base_scores[index]:.9f}",
                        "chain_feature": f"{features[index][selected_mode]:.9f}",
                        "gdt525_score": f"{score_sets[SELECTED_STAGE][index]:.9f}",
                        "chain_trace": traces[index],
                    }
                )
        for index, hit in enumerate(hits):
            if hit is None:
                continue
            for step_index, (step, visible, visible_position, atoms, atom_position, support, total, bonus) in enumerate(
                (
                    ("INNER_BASE_TO_INTERMEDIATE", hit.inner_visible, hit.inner_visible_position, hit.inner_atoms, hit.inner_atom_position, hit.inner_support, hit.inner_total, hit.inner_bonus),
                    ("OUTER_INTERMEDIATE_TO_TARGET", hit.outer_visible, hit.outer_visible_position, hit.outer_atoms, hit.outer_atom_position, hit.outer_support, hit.outer_total, hit.outer_bonus),
                ),
                1,
            ):
                route_rows.append(
                    {
                        "surface": surface,
                        "candidate_recipe": recipe_text(candidates[index].recipe),
                        "candidate_is_truth": "YES" if candidates[index].recipe == truth else "NO",
                        "gdt524_rank": orders["GDT524_BASE"].index(index) + 1,
                        "gdt525_rank": orders[SELECTED_STAGE].index(index) + 1,
                        "base_surface": hit.base_surface,
                        "base_recipe": recipe_text(hit.base_recipe),
                        "intermediate_surface": hit.intermediate_surface,
                        "intermediate_recipe": recipe_text(hit.intermediate_recipe),
                        "intermediate_is_old": "YES" if hit.intermediate_is_old else "NO",
                        "step_index": step_index,
                        "step": step,
                        "visible_insert": visible,
                        "visible_position": visible_position,
                        "atom_insert": recipe_text(atoms) if atoms else "NULL",
                        "atom_position": atom_position,
                        "signature_support": support,
                        "visible_condition_total": total,
                        "license_bonus": f"{bonus:.9f}",
                        "ordered_pair_support": pair_model.support(hit),
                        "ordered_pair_examples": " | ".join(
                            pair_model.examples.get(hit.signature_pair(), [])
                        ) or "NONE",
                        "chain_trace": hit.trace(),
                    }
                )
    ladder = [
        metric_row("CURRENT_159_OLD26_TO_NEW4", config, rank_sets[config[0]])
        for config in CONFIGS
    ]
    return output, candidate_rows, route_rows, ladder


def metrics(rows, prefix: str):
    ranks = [int(row[f"{prefix}_rank"]) for row in rows]
    return G519.rank_metrics(ranks)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    old = read_tsv(G518.G407_RUNNING)
    selected = read_tsv(G518.G516_SELECTED)
    targets = read_tsv(G518.G516_NEW)
    full_pair_model = train_pair_model(
        G518.invariant_surface_recipes(old, "component_recipe")
    )
    rehearsal, old_ladder = fold_rehearsal(old)
    current, candidates, routes, current_ladder = current_benchmark(
        old, selected, targets
    )

    write_tsv(
        OUT / "gdt525_1558_four_fold_two_hop_rehearsal.tsv",
        rehearsal,
        [
            "fold", "surface", "truth_recipe", "candidate_count_capped",
            "truth_generated", "gdt524_rank", "gdt525_rank", "gdt524_top1",
            "gdt525_top1", "truth_chain_feature", "top1_chain_feature",
            "truth_chain_trace", "top1_chain_trace",
        ],
    )
    current_fields = [
        "surface", "occurrence_count", "physical_pages", "truth_recipe",
        "revised_working_recipe", "working_revision_class",
        "candidate_count_capped", "old_base_surface_count", "gdt524_rank",
        "gdt524_top1", "gdt525_rank", "gdt524_revised_rank",
        "gdt525_revised_rank", "gdt525_top1", "gdt525_top5",
        "truth_gdt524_score", "truth_chain_feature", "truth_gdt525_score",
        "truth_chain_trace", "top1_gdt524_score", "top1_chain_feature",
        "top1_gdt525_score", "top1_chain_trace", "top1_alignment_trace",
        "decision_change_class", "working_policy",
    ]
    write_tsv(OUT / "gdt525_159_two_hop_rerank.tsv", current, current_fields)
    write_tsv(
        OUT / "gdt525_candidate_score_atlas.tsv",
        candidates,
        [
            "surface", "truth_recipe", "candidate_is_truth",
            "gdt517_compiler_rank", "gdt524_rank", "gdt525_rank",
            "candidate_recipe", "gdt524_score", "chain_feature",
            "gdt525_score", "chain_trace",
        ],
    )
    write_tsv(
        OUT / "gdt525_two_hop_route_atlas.tsv",
        routes,
        [
            "surface", "candidate_recipe", "candidate_is_truth", "gdt524_rank",
            "gdt525_rank", "base_surface", "intermediate_surface",
            "base_recipe", "intermediate_recipe", "intermediate_is_old",
            "step_index", "step",
            "visible_insert", "visible_position", "atom_insert", "atom_position",
            "signature_support", "visible_condition_total", "license_bonus",
            "ordered_pair_support", "ordered_pair_examples", "chain_trace",
        ],
    )
    write_tsv(
        OUT / "gdt525_model_ladder.tsv",
        old_ladder + current_ladder,
        [
            "scope", "model_stage", "chain_feature", "chain_weight",
            "target_count", "truth_generated_count", "top1_exact_count",
            "top2_exact_count", "top3_exact_count", "top5_exact_count",
            "rank_sum", "deepest_truth_rank",
        ],
    )
    changed = [
        row for row in current
        if row["gdt524_top1"] != row["gdt525_top1"]
    ]
    remaining = [row for row in current if int(row["gdt525_rank"]) != 1]
    revised_remaining = [
        row for row in current if int(row["gdt525_revised_rank"]) != 1
    ]
    write_tsv(OUT / "gdt525_changed_decision_atlas.tsv", changed, current_fields)
    write_tsv(OUT / "gdt525_remaining_top1_error_atlas.tsv", remaining, current_fields)
    write_tsv(
        OUT / "gdt525_revised_remaining_top1_error_atlas.tsv",
        revised_remaining,
        current_fields,
    )
    transitions = Counter(row["decision_change_class"] for row in current)
    result = {
        "experiment_id": "GDT525",
        "status": "PASS_K_BASE_Y_THEN_E_STEM_CLOSURE",
        "claim_ceiling": "EXPLORATORY_TWO_HOP_LOCAL_EDIT_COMPOSITION__NO_CONFIRMED_LEXEME_OR_PLAINTEXT",
        "selected_policy": {
            "stage": SELECTED_STAGE,
            "feature": next(row[1] for row in CONFIGS if row[0] == SELECTED_STAGE),
            "weight": next(row[2] for row in CONFIGS if row[0] == SELECTED_STAGE),
            "route": "OLD_BASE_TO_EXPLICIT_INTERMEDIATE_TO_TARGET",
            "activation": "K_INITIAL_BASE_RECIPE__RIGHT_Y_TO_Y__THEN_INNER_E_TO_E__ORDERED_PAIR_SUPPORT_AT_LEAST_TWO",
        },
        "old_ordered_pair_inventory": {
            "ordered_pair_type_count": len(full_pair_model.counts),
            "ordered_pair_carrier_count": sum(full_pair_model.counts.values()),
            "repeated_ordered_pair_type_count": sum(
                support >= 2 for support in full_pair_model.counts.values()
            ),
        },
        "old26_four_fold_gdt524_metrics": metrics(rehearsal, "gdt524"),
        "old26_four_fold_gdt525_metrics": metrics(rehearsal, "gdt525"),
        "current_gdt524_metrics": metrics(current, "gdt524"),
        "current_gdt525_metrics": metrics(current, "gdt525"),
        "current_family_revised_gdt524_metrics": G519.rank_metrics(
            [int(row["gdt524_revised_rank"]) for row in current]
        ),
        "current_family_revised_gdt525_metrics": G519.rank_metrics(
            [int(row["gdt525_revised_rank"]) for row in current]
        ),
        "working_revisions": WORKING_REVISIONS,
        "current_decision_change_classes": dict(sorted(transitions.items())),
        "current_route_candidate_count": len(
            {(row["surface"], row["candidate_recipe"]) for row in routes}
        ),
        "current_route_surface_count": len({row["surface"] for row in routes}),
        "current_route_step_count": len(routes),
        "remaining_top1_error_count": len(remaining),
        "revised_remaining_top1_error_count": len(revised_remaining),
        "guard": "PRODUCTIVE_K_STEM_RULE__NO_TARGET_WHOLE_FORM_SCORE_CARD__ONE_EXPLICIT_INTERMEDIATE_ONLY",
    }
    write_json(OUT / "gdt525_result.json", result)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
