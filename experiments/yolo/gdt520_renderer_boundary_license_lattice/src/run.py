#!/usr/bin/env python3
"""Add visible boundary licenses and a small segment economy to GDT519."""

from __future__ import annotations

import csv
import hashlib
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
BASE = ROOT / "experiments/yolo/gdt520_renderer_boundary_license_lattice"
OUT = BASE / "artifacts"
G519_RUN = (
    ROOT / "experiments/yolo/gdt519_visible_stem_anchor_transducer/src/run.py"
)

FOLD_COUNT = 4
SEGMENT_COUNT_WEIGHT = 0.10
BOUNDARY_WEIGHT = 0.10
PAIR_BACKOFF = 8.0
WINDOW_BACKOFF = 4.0
MIN_BOUNDARY_PROBABILITY = 0.02
MAX_BOUNDARY_PROBABILITY = 0.98

MODEL_CONFIGS = (
    ("GDT519_ANCHOR_BASE", 0.00, 0.00),
    ("SEGMENT_ECONOMY_005", 0.05, 0.00),
    ("SEGMENT_ECONOMY_010", 0.10, 0.00),
    ("SEGMENT_ECONOMY_015", 0.15, 0.00),
    ("SEGMENT_010_BOUNDARY_005", 0.10, 0.05),
    ("GDT520_SELECTED", SEGMENT_COUNT_WEIGHT, BOUNDARY_WEIGHT),
    ("SEGMENT_010_BOUNDARY_020", 0.10, 0.20),
    ("SEGMENT_010_BOUNDARY_050", 0.10, 0.50),
)


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


G519 = load_module("gdt519_core_for_gdt520", G519_RUN)
G518 = G519.G518
G517 = G519.G517


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


@dataclass(frozen=True)
class PathPart:
    sequence: tuple[str, ...]
    start: int
    end: int
    alias: str
    edit_cost: int
    alias_penalty: float


def alignment_path(
    surface: str,
    recipe: tuple[str, ...],
    matrix,
) -> tuple[float, tuple[PathPart, ...]]:
    """Return GDT519's minimum-cost monotone path with its visible cuts."""
    states: dict[tuple[int, int], tuple[float, tuple[PathPart, ...]]] = {
        (0, 0): (0.0, tuple())
    }
    for atom_index in range(len(recipe)):
        active = [item for item in states.items() if item[0][0] == atom_index]
        for (current_atom, start), (base_cost, path) in active:
            for width in range(1, G519.MAX_RENDERER_ATOMS + 1):
                sequence = recipe[current_atom:current_atom + width]
                if len(sequence) != width or (sequence, start, start) not in matrix:
                    continue
                for end in range(start, len(surface) + 1):
                    choice = matrix[(sequence, start, end)]
                    part = PathPart(
                        sequence,
                        start,
                        end,
                        choice.alias,
                        choice.edit_cost,
                        choice.alias_penalty,
                    )
                    value = (base_cost + choice.total_cost, path + (part,))
                    key = (current_atom + width, end)
                    previous = states.get(key)
                    path_key = tuple(
                        (G517.recipe_text(item.sequence), item.start, item.end, item.alias)
                        for item in value[1]
                    )
                    previous_key = (
                        tuple(
                            (
                                G517.recipe_text(item.sequence),
                                item.start,
                                item.end,
                                item.alias,
                            )
                            for item in previous[1]
                        )
                        if previous
                        else tuple()
                    )
                    if previous is None or (value[0], path_key) < (
                        previous[0],
                        previous_key,
                    ):
                        states[key] = value
    return states[(len(recipe), len(surface))]


def path_text(surface: str, path: tuple[PathPart, ...]) -> str:
    parts = []
    for item in path:
        segment = surface[item.start:item.end] or "∅"
        parts.append(
            f"{segment}=>{item.alias}~{G517.recipe_text(item.sequence)}"
            f"@edit{item.edit_cost}+alias{item.alias_penalty:.3f}"
        )
    return " | ".join(parts)


def renderer_sequences_for_recipe(
    recipe: tuple[str, ...], deck
) -> set[tuple[str, ...]]:
    return {
        recipe[start:start + width]
        for start in range(len(recipe))
        for width in range(1, G519.MAX_RENDERER_ATOMS + 1)
        if len(recipe[start:start + width]) == width
        and recipe[start:start + width] in deck
    }


def boundary_positions(surface: str, path: tuple[PathPart, ...]) -> set[int]:
    return {
        item.end
        for item in path[:-1]
        if 0 < item.end < len(surface)
    }


def boundary_window(surface: str, position: int) -> str:
    padded = "^^" + surface + "$$"
    return padded[position:position + 4]


class BoundaryLicenseModel:
    """Visible-only hierarchy: character pair, then four-character window."""

    def __init__(self) -> None:
        self.pair_counts: dict[str, Counter[bool]] = defaultdict(Counter)
        self.window_counts: dict[str, Counter[bool]] = defaultdict(Counter)
        self.surface_count = 0
        self.boundary_slot_count = 0

    def add(self, surface: str, path: tuple[PathPart, ...]) -> None:
        boundaries = boundary_positions(surface, path)
        self.surface_count += 1
        for position in range(1, len(surface)):
            is_open = position in boundaries
            self.pair_counts[surface[position - 1:position + 1]][is_open] += 1
            self.window_counts[boundary_window(surface, position)][is_open] += 1
            self.boundary_slot_count += 1

    @property
    def base_probability(self) -> float:
        opened = sum(counts[True] for counts in self.pair_counts.values())
        return (opened + 1.0) / (self.boundary_slot_count + 2.0)

    def pair_probability(self, pair: str) -> float:
        counts = self.pair_counts[pair]
        return (
            counts[True] + PAIR_BACKOFF * self.base_probability
        ) / (sum(counts.values()) + PAIR_BACKOFF)

    def probability(self, surface: str, position: int) -> float:
        pair = surface[position - 1:position + 1]
        pair_probability = self.pair_probability(pair)
        counts = self.window_counts[boundary_window(surface, position)]
        probability = (
            counts[True] + WINDOW_BACKOFF * pair_probability
        ) / (sum(counts.values()) + WINDOW_BACKOFF)
        return min(
            MAX_BOUNDARY_PROBABILITY,
            max(MIN_BOUNDARY_PROBABILITY, probability),
        )

    def nll(self, surface: str, path: tuple[PathPart, ...]) -> float:
        boundaries = boundary_positions(surface, path)
        total = 0.0
        for position in range(1, len(surface)):
            probability = self.probability(surface, position)
            total -= math.log(
                probability if position in boundaries else 1.0 - probability
            )
        return total

    def atlas_rows(self) -> list[dict[str, object]]:
        rows: list[dict[str, object]] = []
        for pair in sorted(self.pair_counts):
            counts = self.pair_counts[pair]
            rows.append(
                {
                    "license_level": "PAIR",
                    "visible_key": pair,
                    "parent_pair": pair,
                    "contact_count": sum(counts.values()),
                    "open_boundary_count": counts[True],
                    "closed_renderer_count": counts[False],
                    "smoothed_open_probability": f"{self.pair_probability(pair):.9f}",
                }
            )
        for window in sorted(self.window_counts):
            counts = self.window_counts[window]
            pair = window[1:3]
            probability = (
                counts[True] + WINDOW_BACKOFF * self.pair_probability(pair)
            ) / (sum(counts.values()) + WINDOW_BACKOFF)
            rows.append(
                {
                    "license_level": "FOUR_CHAR_WINDOW",
                    "visible_key": window,
                    "parent_pair": pair,
                    "contact_count": sum(counts.values()),
                    "open_boundary_count": counts[True],
                    "closed_renderer_count": counts[False],
                    "smoothed_open_probability": f"{min(MAX_BOUNDARY_PROBABILITY, max(MIN_BOUNDARY_PROBABILITY, probability)):.9f}",
                }
            )
        return rows


def train_boundary_model(
    rows: list[dict[str, str]], recipe_field: str, deck
) -> BoundaryLicenseModel:
    forms = G518.invariant_surface_recipes(rows, recipe_field)
    model = BoundaryLicenseModel()
    for surface, recipe in forms.items():
        sequences = renderer_sequences_for_recipe(recipe, deck)
        matrix = G519.segment_matrix(surface, sequences, deck)
        alignment_cost, path = alignment_path(surface, recipe, matrix)
        direct_cost = G519.alignment_cost(surface, recipe, matrix)
        if abs(alignment_cost - direct_cost) > 1e-9:
            raise RuntimeError(f"alignment parity failed for {surface}")
        model.add(surface, path)
    return model


def stable_fold(surface: str) -> int:
    digest = hashlib.sha256(surface.encode("utf-8")).digest()
    return int.from_bytes(digest[:2], "big") % FOLD_COUNT


def score_config(
    base_score: float,
    segment_count: int,
    boundary_nll: float,
    segment_weight: float,
    boundary_weight: float,
) -> float:
    return (
        base_score
        + segment_weight * segment_count
        + boundary_weight * boundary_nll
    )


def metric_row(
    scope: str,
    stage: str,
    segment_weight: float,
    boundary_weight: float,
    ranks: list[int],
) -> dict[str, object]:
    return {
        "scope": scope,
        "model_stage": stage,
        "segment_weight": segment_weight,
        "boundary_weight": boundary_weight,
        **G519.rank_metrics(ranks),
    }


def fold_rehearsal(old: list[dict[str, str]]):
    forms = G518.invariant_surface_recipes(old, "component_recipe")
    output: list[dict[str, object]] = []
    ranks: dict[str, list[int]] = defaultdict(list)
    for fold in range(FOLD_COUNT):
        held = {surface for surface in forms if stable_fold(surface) == fold}
        training = [row for row in old if row["surface"] not in held]
        compiler = G517.build_model(f"FOLD_{fold}_TRAIN", training, "component_recipe")
        mappings = G517.retained_mappings(compiler.evidence)
        ridge = G518.train_surface_ridge(training, "component_recipe")
        deck, _ = G519.build_anchor_deck(
            compiler,
            G519.model_atoms(training, "component_recipe"),
            f"FOLD_{fold}_TRAIN",
        )
        boundary_model = train_boundary_model(training, "component_recipe", deck)
        for surface in sorted(held):
            truth = forms[surface]
            candidates = G517.parse_surface(surface, mappings, cap=G519.CANDIDATE_CAP)
            truth_index = next(
                (index for index, candidate in enumerate(candidates) if candidate.recipe == truth),
                None,
            )
            if truth_index is None:
                for stage, _, _ in MODEL_CONFIGS:
                    ranks[stage].append(0)
                output.append(
                    {
                        "fold": fold,
                        "surface": surface,
                        "truth_recipe": G517.recipe_text(truth),
                        "candidate_count_capped": len(candidates),
                        "truth_generated": "NO",
                        "gdt519_rank": 0,
                        "gdt520_rank": 0,
                        "gdt519_top1": G517.recipe_text(candidates[0].recipe) if candidates else "NONE",
                        "gdt520_top1": "NONE",
                        "truth_segment_count": 0,
                        "truth_boundary_nll": "NONE",
                        "selected_top_segment_count": 0,
                        "selected_top_boundary_nll": "NONE",
                    }
                )
                continue
            prediction = ridge.predict(surface)
            matrix = G519.segment_matrix(
                surface, G519.needed_renderer_sequences(candidates, deck), deck
            )
            values = []
            for index, candidate in enumerate(candidates):
                anchor_cost, path = alignment_path(surface, candidate.recipe, matrix)
                base_score = (
                    ridge.squared_cost(prediction, candidate.recipe)
                    + math.log1p(index)
                    + anchor_cost
                )
                values.append(
                    {
                        "base_score": base_score,
                        "path": path,
                        "segment_count": len(path),
                        "boundary_nll": boundary_model.nll(surface, path),
                    }
                )
            orders = {}
            for stage, segment_weight, boundary_weight in MODEL_CONFIGS:
                scores = [
                    score_config(
                        float(value["base_score"]),
                        int(value["segment_count"]),
                        float(value["boundary_nll"]),
                        segment_weight,
                        boundary_weight,
                    )
                    for value in values
                ]
                rank, order = G519.rank_by_score(candidates, truth, scores)
                ranks[stage].append(rank)
                orders[stage] = order
            selected_order = orders["GDT520_SELECTED"]
            selected_top = selected_order[0]
            output.append(
                {
                    "fold": fold,
                    "surface": surface,
                    "truth_recipe": G517.recipe_text(truth),
                    "candidate_count_capped": len(candidates),
                    "truth_generated": "YES",
                    "gdt519_rank": ranks["GDT519_ANCHOR_BASE"][-1],
                    "gdt520_rank": ranks["GDT520_SELECTED"][-1],
                    "gdt519_top1": G517.recipe_text(candidates[orders["GDT519_ANCHOR_BASE"][0]].recipe),
                    "gdt520_top1": G517.recipe_text(candidates[selected_top].recipe),
                    "truth_segment_count": values[truth_index]["segment_count"],
                    "truth_boundary_nll": f"{float(values[truth_index]['boundary_nll']):.9f}",
                    "selected_top_segment_count": values[selected_top]["segment_count"],
                    "selected_top_boundary_nll": f"{float(values[selected_top]['boundary_nll']):.9f}",
                }
            )
    ladder = [
        metric_row(
            "FOUR_FOLD_OLD26_SURFACE_REHEARSAL",
            stage,
            segment_weight,
            boundary_weight,
            ranks[stage],
        )
        for stage, segment_weight, boundary_weight in MODEL_CONFIGS
    ]
    return output, ladder


def current_benchmark(
    old: list[dict[str, str]],
    selected: list[dict[str, str]],
    targets: list[dict[str, str]],
):
    compiler = G517.build_model("FULL_OLD26", old, "component_recipe")
    mappings = G517.retained_mappings(compiler.evidence)
    ridge = G518.train_surface_ridge(old, "component_recipe")
    bigram = G518.train_ngram(old, "source_statement_id", "component_recipe", order=2)
    trigram = G518.train_ngram(old, "source_statement_id", "component_recipe", order=3)
    occurrences = G518.selected_prose_occurrences(selected)
    deck, _ = G519.build_anchor_deck(
        compiler, G519.model_atoms(old, "component_recipe"), "FULL_OLD26"
    )
    boundary_model = train_boundary_model(old, "component_recipe", deck)

    output: list[dict[str, object]] = []
    candidate_rows: list[dict[str, object]] = []
    contested_rows: list[dict[str, object]] = []
    ranks: dict[str, list[int]] = defaultdict(list)
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
        values = []
        for index, candidate in enumerate(candidates):
            context_base, structural, bigram_nll, trigram_nll = (
                G519.current_context_base_score(
                    surface,
                    candidate,
                    index,
                    prediction,
                    ridge,
                    bigram,
                    trigram,
                    occurrences,
                )
            )
            anchor_cost, path = alignment_path(surface, candidate.recipe, matrix)
            values.append(
                {
                    "candidate": candidate,
                    "compiler_rank": index + 1,
                    "context_base": context_base,
                    "structural": structural,
                    "bigram_nll": bigram_nll,
                    "trigram_nll": trigram_nll,
                    "anchor_cost": anchor_cost,
                    "gdt519_score": context_base + anchor_cost,
                    "path": path,
                    "segment_count": len(path),
                    "boundary_nll": boundary_model.nll(surface, path),
                }
            )
        orders = {}
        scores_by_stage = {}
        for stage, segment_weight, boundary_weight in MODEL_CONFIGS:
            scores = [
                score_config(
                    float(value["gdt519_score"]),
                    int(value["segment_count"]),
                    float(value["boundary_nll"]),
                    segment_weight,
                    boundary_weight,
                )
                for value in values
            ]
            rank, order = G519.rank_by_score(candidates, truth, scores)
            ranks[stage].append(rank)
            orders[stage] = order
            scores_by_stage[stage] = scores
        truth_index = next(
            index for index, candidate in enumerate(candidates) if candidate.recipe == truth
        )
        base_top_index = orders["GDT519_ANCHOR_BASE"][0]
        top_index = orders["GDT520_SELECTED"][0]
        base_correct = ranks["GDT519_ANCHOR_BASE"][-1] == 1
        selected_correct = ranks["GDT520_SELECTED"][-1] == 1
        if base_correct and selected_correct:
            change = "GDT519_CORRECT_PRESERVED"
        elif not base_correct and selected_correct:
            change = "GDT519_ERROR_CORRECTED"
        elif base_correct and not selected_correct:
            change = "GDT519_CORRECT_LOST"
        elif candidates[base_top_index].recipe != candidates[top_index].recipe:
            change = "ERROR_CHANGED_STILL_WRONG"
        else:
            change = "GDT519_ERROR_UNCHANGED"
        truth_value = values[truth_index]
        top_value = values[top_index]
        output.append(
            {
                "surface": surface,
                "occurrence_count": target["occurrence_count"],
                "physical_pages": target["physical_pages"],
                "truth_recipe": G517.recipe_text(truth),
                "candidate_count_capped": len(candidates),
                "gdt519_rank": ranks["GDT519_ANCHOR_BASE"][-1],
                "gdt519_top1": G517.recipe_text(candidates[base_top_index].recipe),
                "gdt520_rank": ranks["GDT520_SELECTED"][-1],
                "gdt520_top1": G517.recipe_text(candidates[top_index].recipe),
                "gdt520_top5": " | ".join(
                    G517.recipe_text(candidates[index].recipe)
                    for index in orders["GDT520_SELECTED"][:5]
                ),
                "truth_gdt519_score": f"{float(truth_value['gdt519_score']):.9f}",
                "truth_segment_count": truth_value["segment_count"],
                "truth_boundary_nll": f"{float(truth_value['boundary_nll']):.9f}",
                "truth_gdt520_score": f"{scores_by_stage['GDT520_SELECTED'][truth_index]:.9f}",
                "truth_alignment_trace": path_text(surface, truth_value["path"]),
                "top1_gdt519_score": f"{float(top_value['gdt519_score']):.9f}",
                "top1_segment_count": top_value["segment_count"],
                "top1_boundary_nll": f"{float(top_value['boundary_nll']):.9f}",
                "top1_gdt520_score": f"{scores_by_stage['GDT520_SELECTED'][top_index]:.9f}",
                "top1_alignment_trace": path_text(surface, top_value["path"]),
                "decision_change_class": change,
                "working_policy": "KNOWN_EVENT_OR_SURFACE_RECIPE_STILL_WINS__BOUNDARY_LATTICE_RERANKS_ONLY_FINITE_UNKNOWN_CANDIDATES",
            }
        )

        if (
            ranks["GDT520_SELECTED"][-1] != 1
            or candidates[base_top_index].recipe != candidates[top_index].recipe
        ):
            for selected_rank, index in enumerate(orders["GDT520_SELECTED"][:12], 1):
                value = values[index]
                candidate = value["candidate"]
                candidate_rows.append(
                    {
                        "surface": surface,
                        "truth_recipe": G517.recipe_text(truth),
                        "candidate_is_truth": "YES" if candidate.recipe == truth else "NO",
                        "gdt517_compiler_rank": value["compiler_rank"],
                        "gdt519_rank": orders["GDT519_ANCHOR_BASE"].index(index) + 1,
                        "gdt520_rank": selected_rank,
                        "candidate_recipe": G517.recipe_text(candidate.recipe),
                        "gdt519_score": f"{float(value['gdt519_score']):.9f}",
                        "segment_count": value["segment_count"],
                        "boundary_nll": f"{float(value['boundary_nll']):.9f}",
                        "gdt520_score": f"{scores_by_stage['GDT520_SELECTED'][index]:.9f}",
                        "alignment_trace": path_text(surface, value["path"]),
                    }
                )

        truth_boundaries = boundary_positions(surface, truth_value["path"])
        top_boundaries = boundary_positions(surface, top_value["path"])
        for position in sorted(truth_boundaries ^ top_boundaries):
            pair = surface[position - 1:position + 1]
            window = boundary_window(surface, position)
            pair_counts = boundary_model.pair_counts[pair]
            window_counts = boundary_model.window_counts[window]
            contested_rows.append(
                {
                    "surface": surface,
                    "truth_recipe": G517.recipe_text(truth),
                    "gdt520_top1": G517.recipe_text(candidates[top_index].recipe),
                    "boundary_position": position,
                    "visible_pair": pair,
                    "visible_window": window,
                    "truth_open": "YES" if position in truth_boundaries else "NO",
                    "top1_open": "YES" if position in top_boundaries else "NO",
                    "pair_open_count": pair_counts[True],
                    "pair_closed_count": pair_counts[False],
                    "window_open_count": window_counts[True],
                    "window_closed_count": window_counts[False],
                    "smoothed_open_probability": f"{boundary_model.probability(surface, position):.9f}",
                }
            )

    ladder = [
        metric_row(
            "CURRENT_159_OLD26_TO_NEW4",
            stage,
            segment_weight,
            boundary_weight,
            ranks[stage],
        )
        for stage, segment_weight, boundary_weight in MODEL_CONFIGS
    ]
    return output, candidate_rows, contested_rows, ladder, boundary_model


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    old = read_tsv(G518.G407_RUNNING)
    selected = read_tsv(G518.G516_SELECTED)
    targets = read_tsv(G518.G516_NEW)
    rehearsal, rehearsal_ladder = fold_rehearsal(old)
    current, candidates, contested, current_ladder, boundary_model = current_benchmark(
        old, selected, targets
    )

    rehearsal_fields = [
        "fold", "surface", "truth_recipe", "candidate_count_capped",
        "truth_generated", "gdt519_rank", "gdt520_rank", "gdt519_top1",
        "gdt520_top1", "truth_segment_count", "truth_boundary_nll",
        "selected_top_segment_count", "selected_top_boundary_nll",
    ]
    current_fields = [
        "surface", "occurrence_count", "physical_pages", "truth_recipe",
        "candidate_count_capped", "gdt519_rank", "gdt519_top1", "gdt520_rank",
        "gdt520_top1", "gdt520_top5", "truth_gdt519_score",
        "truth_segment_count", "truth_boundary_nll", "truth_gdt520_score",
        "truth_alignment_trace", "top1_gdt519_score", "top1_segment_count",
        "top1_boundary_nll", "top1_gdt520_score", "top1_alignment_trace",
        "decision_change_class", "working_policy",
    ]
    write_tsv(
        OUT / "gdt520_1558_four_fold_boundary_rehearsal.tsv",
        rehearsal,
        rehearsal_fields,
    )
    write_tsv(OUT / "gdt520_159_boundary_rerank.tsv", current, current_fields)
    write_tsv(
        OUT / "gdt520_remaining_top1_error_atlas.tsv",
        [row for row in current if int(row["gdt520_rank"]) != 1],
        current_fields,
    )
    write_tsv(
        OUT / "gdt520_changed_decision_atlas.tsv",
        [row for row in current if row["gdt519_top1"] != row["gdt520_top1"]],
        current_fields,
    )
    write_tsv(
        OUT / "gdt520_candidate_score_atlas.tsv",
        candidates,
        [
            "surface", "truth_recipe", "candidate_is_truth", "gdt517_compiler_rank",
            "gdt519_rank", "gdt520_rank", "candidate_recipe", "gdt519_score",
            "segment_count", "boundary_nll", "gdt520_score", "alignment_trace",
        ],
    )
    write_tsv(
        OUT / "gdt520_contested_boundary_atlas.tsv",
        contested,
        [
            "surface", "truth_recipe", "gdt520_top1", "boundary_position",
            "visible_pair", "visible_window", "truth_open", "top1_open",
            "pair_open_count", "pair_closed_count", "window_open_count",
            "window_closed_count", "smoothed_open_probability",
        ],
    )
    write_tsv(
        OUT / "gdt520_visible_boundary_license_atlas.tsv",
        boundary_model.atlas_rows(),
        [
            "license_level", "visible_key", "parent_pair", "contact_count",
            "open_boundary_count", "closed_renderer_count",
            "smoothed_open_probability",
        ],
    )
    ladder = rehearsal_ladder + current_ladder
    write_tsv(
        OUT / "gdt520_model_ladder.tsv",
        ladder,
        [
            "scope", "model_stage", "segment_weight", "boundary_weight",
            "target_count", "truth_generated_count", "top1_exact_count",
            "top2_exact_count", "top3_exact_count", "top5_exact_count",
            "rank_sum", "deepest_truth_rank",
        ],
    )

    old_base = G519.rank_metrics([int(row["gdt519_rank"]) for row in rehearsal])
    old_selected = G519.rank_metrics([int(row["gdt520_rank"]) for row in rehearsal])
    current_base = G519.rank_metrics([int(row["gdt519_rank"]) for row in current])
    current_selected = G519.rank_metrics([int(row["gdt520_rank"]) for row in current])
    change_counts = Counter(str(row["decision_change_class"]) for row in current)
    result = {
        "experiment_id": "GDT520",
        "status": "PASS_RENDERER_BOUNDARY_LICENSE_LATTICE",
        "claim_ceiling": "EXPLORATORY_VISIBLE_BOUNDARY_AND_COMPOSITION_DEFAULT__NO_CONFIRMED_LEXEME_OR_PLAINTEXT",
        "selected_policy": {
            "segment_count_weight": SEGMENT_COUNT_WEIGHT,
            "boundary_weight": BOUNDARY_WEIGHT,
            "pair_backoff": PAIR_BACKOFF,
            "window_backoff": WINDOW_BACKOFF,
            "minimum_boundary_probability": MIN_BOUNDARY_PROBABILITY,
            "maximum_boundary_probability": MAX_BOUNDARY_PROBABILITY,
            "old26_training_surface_count": boundary_model.surface_count,
            "old26_boundary_slot_count": boundary_model.boundary_slot_count,
            "visible_pair_license_count": len(boundary_model.pair_counts),
            "visible_window_license_count": len(boundary_model.window_counts),
        },
        "old26_four_fold_gdt519_metrics": old_base,
        "old26_four_fold_gdt520_metrics": old_selected,
        "current_gdt519_metrics": current_base,
        "current_gdt520_metrics": current_selected,
        "current_net_top1_gain": current_selected["top1_exact_count"] - current_base["top1_exact_count"],
        "current_rank_sum_reduction": current_base["rank_sum"] - current_selected["rank_sum"],
        "current_decision_change_classes": dict(sorted(change_counts.items())),
        "remaining_top1_error_count": sum(int(row["gdt520_rank"]) != 1 for row in current),
        "guard": "VISIBLE_BOUNDARIES_LICENSE_RENDERER_SEGMENTATION_ONLY__KNOWN_EVENT_AND_SURFACE_CARDS_KEEP_PRECEDENCE",
    }
    write_json(OUT / "gdt520_result.json", result)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
