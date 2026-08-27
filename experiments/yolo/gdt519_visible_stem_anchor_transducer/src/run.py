#!/usr/bin/env python3
"""Add monotone visible-stem alignment to the GDT518 candidate ordering."""

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
from typing import Iterable


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt519_visible_stem_anchor_transducer"
OUT = BASE / "artifacts"
G518_RUN = (
    ROOT / "experiments/yolo/gdt518_context_aware_surface_recipe_reranker/src/run.py"
)

FOLD_COUNT = 4
CANDIDATE_CAP = 100
ALIAS_MIN_SUPPORT = 10
ALIAS_MIN_SHARE = 0.70
MULTI_ALIAS_MIN_SHARE = 0.60
ALIAS_MAX_EXTRA_CHARS = 2
ALIAS_LIMIT_PER_ATOM = 5
MAX_RENDERER_ATOMS = 3
ALIAS_EDIT_PENALTY = 0.25
ALIAS_EVIDENCE_PENALTY = 0.10
SELECTED_ANCHOR_WEIGHT = 1.0
WEIGHT_LADDER = (0.0, 0.25, 0.50, 0.75, 1.0, 1.25)

CANONICAL_OVERRIDES = {
    "A_ADDR": "a",
    "D_ADDR": "d",
    "AM_ADDR": "am",
    "S_ADDR": "s",
    "M_LOCAL": "m",
    "LOCAL_CHAR_I": "i",
    "LOCAL_CHAR_F": "f",
    "LOCAL_CHAR_G": "g",
    "LOCAL_CHAR_B": "b",
    "LOCAL_CHAR_J": "j",
    "LOCAL_CHAR_Z": "z",
    "D_LABEL": "d",
    "S_LABEL": "s",
    "G_LABEL": "g",
    "Z_ADDR": "z",
    "CARRIER_Q": "q",
    "RESUME_CARD": "schol",
    "LOCAL_X": "x",
    "LOCAL_C": "c",
    # CHD's dominant direct visible card is ched (178 contacts, 98% share).
    "CHD": "ched",
}


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


G518 = load_module("gdt518_core_for_gdt519", G518_RUN)
G517 = G518.G517


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


def canonical_anchor(atom: str) -> str:
    return CANONICAL_OVERRIDES.get(atom, atom.lower())


def weighted_edit_distance(surface: str, anchor: str) -> int:
    """Surface deletion=1, missing anchor insertion=2, substitution=1."""
    previous = [2 * index for index in range(len(anchor) + 1)]
    for surface_index, surface_char in enumerate(surface, 1):
        current = [surface_index]
        for anchor_index, anchor_char in enumerate(anchor, 1):
            current.append(
                min(
                    current[-1] + 2,
                    previous[anchor_index] + 1,
                    previous[anchor_index - 1] + (surface_char != anchor_char),
                )
            )
        previous = current
    return previous[-1]


@dataclass(frozen=True)
class AnchorOption:
    alias: str
    penalty: float
    support: int
    share: float
    source: str


def model_atoms(rows: list[dict[str, str]], recipe_field: str) -> set[str]:
    return {
        atom
        for row in rows
        for atom in G517.atoms(row[recipe_field])
    } | {"LOCAL_X", "LOCAL_C"}


def build_anchor_deck(
    compiler,
    atoms: set[str],
    model_name: str,
) -> tuple[dict[tuple[str, ...], tuple[AnchorOption, ...]], list[dict[str, object]]]:
    learned: dict[tuple[str, ...], list[tuple[str, int, float]]] = defaultdict(list)
    for visible_chunk, options in G517.retained_mappings(compiler.evidence).items():
        for option in options:
            recipe = tuple(option["recipe"])
            if not 1 <= len(recipe) <= MAX_RENDERER_ATOMS:
                continue
            if option["scope"] != "GENERAL_RUNNING_COMPILER":
                continue
            support = int(option["support"])
            share = float(option["share"])
            required_share = ALIAS_MIN_SHARE if len(recipe) == 1 else MULTI_ALIAS_MIN_SHARE
            if support < ALIAS_MIN_SUPPORT or share < required_share:
                continue
            canonical = "".join(canonical_anchor(atom) for atom in recipe)
            if len(visible_chunk) > len(canonical) + ALIAS_MAX_EXTRA_CHARS:
                continue
            learned[recipe].append((visible_chunk, support, share))

    deck: dict[tuple[str, ...], tuple[AnchorOption, ...]] = {}
    artifact: list[dict[str, object]] = []
    for atom in sorted(atoms):
        recipe = (atom,)
        canonical = canonical_anchor(atom)
        options: dict[str, AnchorOption] = {
            canonical: AnchorOption(canonical, 0.0, 0, 0.0, "CANONICAL_STEM")
        }
        selected = sorted(
            learned.get(recipe, []),
            key=lambda item: (-item[1], -item[2], len(item[0]), item[0]),
        )[:ALIAS_LIMIT_PER_ATOM]
        for alias, support, share in selected:
            if alias == canonical:
                options[alias] = AnchorOption(
                    alias, 0.0, support, share, "CANONICAL_AND_LEARNED"
                )
                continue
            penalty = (
                ALIAS_EDIT_PENALTY * weighted_edit_distance(alias, canonical)
                + ALIAS_EVIDENCE_PENALTY * -math.log(share)
            )
            candidate = AnchorOption(alias, penalty, support, share, "LEARNED_RENDERER_ALIAS")
            previous = options.get(alias)
            if previous is None or candidate.penalty < previous.penalty:
                options[alias] = candidate
        ordered = tuple(sorted(options.values(), key=lambda item: (item.penalty, item.alias)))
        deck[recipe] = ordered
        for rank, option in enumerate(ordered, 1):
            artifact.append(
                {
                    "model": model_name,
                    "atom_sequence": atom,
                    "atom_count": 1,
                    "canonical_anchor": canonical,
                    "alias_rank": rank,
                    "surface_alias": option.alias,
                    "alias_source": option.source,
                    "support": option.support,
                    "support_share": f"{option.share:.6f}",
                    "alias_penalty": f"{option.penalty:.9f}",
                }
            )
    for recipe in sorted(key for key in learned if len(key) > 1):
        canonical = "".join(canonical_anchor(atom) for atom in recipe)
        options: dict[str, AnchorOption] = {}
        selected = sorted(
            learned[recipe],
            key=lambda item: (-item[1], -item[2], len(item[0]), item[0]),
        )[:ALIAS_LIMIT_PER_ATOM]
        for alias, support, share in selected:
            penalty = (
                ALIAS_EDIT_PENALTY * weighted_edit_distance(alias, canonical)
                + ALIAS_EVIDENCE_PENALTY * -math.log(share)
            )
            candidate = AnchorOption(alias, penalty, support, share, "LEARNED_SHORT_RENDERER")
            previous = options.get(alias)
            if previous is None or candidate.penalty < previous.penalty:
                options[alias] = candidate
        if not options:
            continue
        ordered = tuple(sorted(options.values(), key=lambda item: (item.penalty, item.alias)))
        deck[recipe] = ordered
        for rank, option in enumerate(ordered, 1):
            artifact.append(
                {
                    "model": model_name,
                    "atom_sequence": G517.recipe_text(recipe),
                    "atom_count": len(recipe),
                    "canonical_anchor": canonical,
                    "alias_rank": rank,
                    "surface_alias": option.alias,
                    "alias_source": option.source,
                    "support": option.support,
                    "support_share": f"{option.share:.6f}",
                    "alias_penalty": f"{option.penalty:.9f}",
                }
            )
    return deck, artifact


@dataclass(frozen=True)
class SegmentChoice:
    total_cost: float
    alias: str
    edit_cost: int
    alias_penalty: float


def segment_matrix(
    surface: str,
    renderer_sequences: set[tuple[str, ...]],
    deck: dict[tuple[str, ...], tuple[AnchorOption, ...]],
) -> dict[tuple[tuple[str, ...], int, int], SegmentChoice]:
    matrix: dict[tuple[tuple[str, ...], int, int], SegmentChoice] = {}
    for renderer_sequence in renderer_sequences:
        options = deck[renderer_sequence]
        for start in range(len(surface) + 1):
            for end in range(start, len(surface) + 1):
                segment = surface[start:end]
                choices = []
                for option in options:
                    edit_cost = weighted_edit_distance(segment, option.alias)
                    choices.append(
                        SegmentChoice(
                            edit_cost + option.penalty,
                            option.alias,
                            edit_cost,
                            option.penalty,
                        )
                    )
                matrix[(renderer_sequence, start, end)] = min(
                    choices,
                    key=lambda item: (
                        item.total_cost,
                        item.alias_penalty,
                        item.edit_cost,
                        item.alias,
                    ),
                )
    return matrix


def needed_renderer_sequences(
    candidates,
    deck: dict[tuple[str, ...], tuple[AnchorOption, ...]],
) -> set[tuple[str, ...]]:
    needed: set[tuple[str, ...]] = set()
    for candidate in candidates:
        recipe = candidate.recipe
        for start in range(len(recipe)):
            for width in range(1, MAX_RENDERER_ATOMS + 1):
                sequence = recipe[start:start + width]
                if len(sequence) == width and sequence in deck:
                    needed.add(sequence)
    return needed


def alignment_cost(
    surface: str,
    recipe: tuple[str, ...],
    matrix: dict[tuple[tuple[str, ...], int, int], SegmentChoice],
) -> float:
    costs = [[math.inf] * (len(surface) + 1) for _ in range(len(recipe) + 1)]
    costs[0][0] = 0.0
    for atom_index in range(len(recipe)):
        for start, base_cost in enumerate(costs[atom_index]):
            if not math.isfinite(base_cost):
                continue
            for width in range(1, MAX_RENDERER_ATOMS + 1):
                sequence = recipe[atom_index:atom_index + width]
                if len(sequence) != width or (sequence, start, start) not in matrix:
                    continue
                for end in range(start, len(surface) + 1):
                    costs[atom_index + width][end] = min(
                        costs[atom_index + width][end],
                        base_cost + matrix[(sequence, start, end)].total_cost,
                    )
    return costs[len(recipe)][len(surface)]


def alignment_trace(
    surface: str,
    recipe: tuple[str, ...],
    matrix: dict[tuple[tuple[str, ...], int, int], SegmentChoice],
) -> tuple[float, str]:
    states: dict[
        tuple[int, int],
        tuple[float, tuple[tuple[tuple[str, ...], int, int, SegmentChoice], ...]],
    ] = {
        (0, 0): (0.0, tuple())
    }
    for atom_index in range(len(recipe)):
        active = [item for item in states.items() if item[0][0] == atom_index]
        for (current_atom, start), (base_cost, path) in active:
            for width in range(1, MAX_RENDERER_ATOMS + 1):
                sequence = recipe[current_atom:current_atom + width]
                if len(sequence) != width or (sequence, start, start) not in matrix:
                    continue
                for end in range(start, len(surface) + 1):
                    choice = matrix[(sequence, start, end)]
                    value = (
                        base_cost + choice.total_cost,
                        path + ((sequence, start, end, choice),),
                    )
                    key = (current_atom + width, end)
                    previous = states.get(key)
                    path_key = tuple(
                        (G517.recipe_text(part[0]), part[1], part[2], part[3].alias)
                        for part in value[1]
                    )
                    previous_key = (
                        tuple(
                            (G517.recipe_text(part[0]), part[1], part[2], part[3].alias)
                            for part in previous[1]
                        )
                        if previous else tuple()
                    )
                    if previous is None or (value[0], path_key) < (previous[0], previous_key):
                        states[key] = value
    cost, path = states[(len(recipe), len(surface))]
    parts = []
    for sequence, start, end, choice in path:
        segment = surface[start:end] or "∅"
        parts.append(
            f"{segment}=>{choice.alias}~{G517.recipe_text(sequence)}"
            f"@edit{choice.edit_cost}+alias{choice.alias_penalty:.3f}"
        )
    return cost, " | ".join(parts)


def stable_fold(surface: str) -> int:
    digest = hashlib.sha256(surface.encode("utf-8")).digest()
    return int.from_bytes(digest[:2], "big") % FOLD_COUNT


def rank_by_score(
    candidates,
    truth: tuple[str, ...],
    scores: list[float],
) -> tuple[int, list[int]]:
    order = sorted(range(len(candidates)), key=lambda index: (scores[index], index))
    rank = next(
        (position + 1 for position, index in enumerate(order) if candidates[index].recipe == truth),
        0,
    )
    return rank, order


def rank_metrics(ranks: Iterable[int], target_count: int | None = None) -> dict[str, int]:
    values = list(ranks)
    positive = [rank for rank in values if rank]
    return {
        "target_count": target_count if target_count is not None else len(values),
        "truth_generated_count": len(positive),
        "top1_exact_count": sum(rank == 1 for rank in values),
        "top2_exact_count": sum(0 < rank <= 2 for rank in values),
        "top3_exact_count": sum(0 < rank <= 3 for rank in values),
        "top5_exact_count": sum(0 < rank <= 5 for rank in values),
        "rank_sum": sum(positive),
        "deepest_truth_rank": max(positive, default=0),
    }


def fold_rehearsal(
    old: list[dict[str, str]],
) -> tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, object]]]:
    forms = G518.invariant_surface_recipes(old, "component_recipe")
    rows: list[dict[str, object]] = []
    alias_rows: list[dict[str, object]] = []
    ranks: dict[str, list[int]] = defaultdict(list)
    weight_ranks: dict[float, list[int]] = defaultdict(list)
    for fold in range(FOLD_COUNT):
        held = {surface for surface in forms if stable_fold(surface) == fold}
        training = [row for row in old if row["surface"] not in held]
        compiler = G517.build_model(f"FOLD_{fold}_TRAIN", training, "component_recipe")
        mappings = G517.retained_mappings(compiler.evidence)
        ridge = G518.train_surface_ridge(training, "component_recipe")
        deck, fold_alias_rows = build_anchor_deck(
            compiler, model_atoms(training, "component_recipe"), f"FOLD_{fold}_TRAIN"
        )
        alias_rows.extend(fold_alias_rows)
        for surface in sorted(held):
            truth = forms[surface]
            candidates = G517.parse_surface(surface, mappings, cap=CANDIDATE_CAP)
            compiler_rank = next(
                (index + 1 for index, candidate in enumerate(candidates) if candidate.recipe == truth),
                0,
            )
            ranks["FOLD_COMPILER_ORDER"].append(compiler_rank)
            if not compiler_rank:
                rows.append(
                    {
                        "fold": fold,
                        "surface": surface,
                        "truth_recipe": G517.recipe_text(truth),
                        "candidate_count_capped": len(candidates),
                        "truth_generated": "NO",
                        "compiler_rank": 0,
                        "form_decoder_rank": 0,
                        "anchor_rank": 0,
                        "compiler_top1": G517.recipe_text(candidates[0].recipe) if candidates else "NONE",
                        "form_decoder_top1": "NONE",
                        "anchor_top1": "NONE",
                        "truth_anchor_cost": "NONE",
                        "anchor_top1_cost": "NONE",
                    }
                )
                ranks["FOLD_FORM_DECODER"].append(0)
                ranks["FOLD_ANCHOR_SELECTED"].append(0)
                for weight in WEIGHT_LADDER:
                    weight_ranks[weight].append(0)
                continue
            prediction = ridge.predict(surface)
            matrix = segment_matrix(
                surface, needed_renderer_sequences(candidates, deck), deck
            )
            form_scores = [
                ridge.squared_cost(prediction, candidate.recipe) + math.log1p(index)
                for index, candidate in enumerate(candidates)
            ]
            anchor_costs = [
                alignment_cost(surface, candidate.recipe, matrix) for candidate in candidates
            ]
            form_rank, form_order = rank_by_score(candidates, truth, form_scores)
            anchor_scores = [
                score + SELECTED_ANCHOR_WEIGHT * cost
                for score, cost in zip(form_scores, anchor_costs)
            ]
            anchor_rank, anchor_order = rank_by_score(candidates, truth, anchor_scores)
            ranks["FOLD_FORM_DECODER"].append(form_rank)
            ranks["FOLD_ANCHOR_SELECTED"].append(anchor_rank)
            for weight in WEIGHT_LADDER:
                weighted = [score + weight * cost for score, cost in zip(form_scores, anchor_costs)]
                rank, _ = rank_by_score(candidates, truth, weighted)
                weight_ranks[weight].append(rank)
            truth_index = compiler_rank - 1
            rows.append(
                {
                    "fold": fold,
                    "surface": surface,
                    "truth_recipe": G517.recipe_text(truth),
                    "candidate_count_capped": len(candidates),
                    "truth_generated": "YES",
                    "compiler_rank": compiler_rank,
                    "form_decoder_rank": form_rank,
                    "anchor_rank": anchor_rank,
                    "compiler_top1": G517.recipe_text(candidates[0].recipe),
                    "form_decoder_top1": G517.recipe_text(candidates[form_order[0]].recipe),
                    "anchor_top1": G517.recipe_text(candidates[anchor_order[0]].recipe),
                    "truth_anchor_cost": f"{anchor_costs[truth_index]:.9f}",
                    "anchor_top1_cost": f"{anchor_costs[anchor_order[0]]:.9f}",
                }
            )

    ladder = []
    for stage in ("FOLD_COMPILER_ORDER", "FOLD_FORM_DECODER", "FOLD_ANCHOR_SELECTED"):
        ladder.append(
            {
                "scope": "FOUR_FOLD_OLD26_SURFACE_REHEARSAL",
                "model_stage": stage,
                "anchor_weight": SELECTED_ANCHOR_WEIGHT if stage.endswith("SELECTED") else 0,
                **rank_metrics(ranks[stage], target_count=len(forms)),
            }
        )
    for weight in WEIGHT_LADDER:
        ladder.append(
            {
                "scope": "FOUR_FOLD_OLD26_WEIGHT_LADDER",
                "model_stage": "FORM_PLUS_MONOTONE_ANCHOR",
                "anchor_weight": weight,
                **rank_metrics(weight_ranks[weight], target_count=len(forms)),
            }
        )
    return rows, alias_rows, ladder


def current_context_base_score(
    surface: str,
    candidate,
    base_index: int,
    prediction,
    ridge,
    bigram,
    trigram,
    occurrences,
) -> tuple[float, float, float, float]:
    structural = ridge.squared_cost(prediction, candidate.recipe)
    bigram_nll = G518.aggregate_context_nll(
        bigram, occurrences.get(surface, []), candidate.recipe
    )
    trigram_nll = G518.aggregate_context_nll(
        trigram, occurrences.get(surface, []), candidate.recipe
    )
    score = (
        structural
        + math.log1p(base_index)
        + (G518.CONTEXT_WEIGHT / 2.0) * (bigram_nll + trigram_nll)
    )
    return score, structural, bigram_nll, trigram_nll


def current_benchmark(
    old: list[dict[str, str]],
    selected: list[dict[str, str]],
    targets: list[dict[str, str]],
) -> tuple[
    list[dict[str, object]],
    list[dict[str, object]],
    list[dict[str, object]],
    list[dict[str, object]],
    dict[str, object],
]:
    compiler = G517.build_model("FULL_OLD26", old, "component_recipe")
    mappings = G517.retained_mappings(compiler.evidence)
    ridge = G518.train_surface_ridge(old, "component_recipe")
    bigram = G518.train_ngram(old, "source_statement_id", "component_recipe", order=2)
    trigram = G518.train_ngram(old, "source_statement_id", "component_recipe", order=3)
    occurrences = G518.selected_prose_occurrences(selected)
    deck, alias_rows = build_anchor_deck(
        compiler, model_atoms(old, "component_recipe"), "FULL_OLD26"
    )

    output: list[dict[str, object]] = []
    candidate_rows: list[dict[str, object]] = []
    base_ranks: list[int] = []
    selected_ranks: list[int] = []
    weight_ranks: dict[float, list[int]] = defaultdict(list)
    for target in targets:
        surface = target["surface"]
        truth = G517.atoms(target["gdt516_context_recipe"])
        candidates = G517.parse_surface(
            surface, mappings, cap=CANDIDATE_CAP, allow_f66r_local=True
        )
        prediction = ridge.predict(surface)
        matrix = segment_matrix(
            surface, needed_renderer_sequences(candidates, deck), deck
        )
        candidate_values = []
        for index, candidate in enumerate(candidates):
            base_score, structural, bigram_nll, trigram_nll = current_context_base_score(
                surface,
                candidate,
                index,
                prediction,
                ridge,
                bigram,
                trigram,
                occurrences,
            )
            anchor_cost = alignment_cost(surface, candidate.recipe, matrix)
            candidate_values.append(
                {
                    "candidate": candidate,
                    "base_index": index,
                    "base_score": base_score,
                    "structural_cost": structural,
                    "bigram_nll": bigram_nll,
                    "trigram_nll": trigram_nll,
                    "anchor_cost": anchor_cost,
                    "selected_score": base_score + SELECTED_ANCHOR_WEIGHT * anchor_cost,
                }
            )
        base_scores = [float(row["base_score"]) for row in candidate_values]
        selected_scores = [float(row["selected_score"]) for row in candidate_values]
        base_rank, base_order = rank_by_score(candidates, truth, base_scores)
        selected_rank, selected_order = rank_by_score(candidates, truth, selected_scores)
        base_ranks.append(base_rank)
        selected_ranks.append(selected_rank)
        for weight in WEIGHT_LADDER:
            scores = [
                float(row["base_score"]) + weight * float(row["anchor_cost"])
                for row in candidate_values
            ]
            rank, _ = rank_by_score(candidates, truth, scores)
            weight_ranks[weight].append(rank)

        truth_index = next(
            index for index, candidate in enumerate(candidates) if candidate.recipe == truth
        )
        top_index = selected_order[0]
        base_top_index = base_order[0]
        truth_alignment_cost, truth_trace = alignment_trace(surface, truth, matrix)
        top_alignment_cost, top_trace = alignment_trace(
            surface, candidates[top_index].recipe, matrix
        )
        base_correct = base_rank == 1
        selected_correct = selected_rank == 1
        if base_correct and selected_correct:
            change = "GDT518_CORRECT_PRESERVED"
        elif not base_correct and selected_correct:
            change = "GDT518_ERROR_CORRECTED"
        elif base_correct and not selected_correct:
            change = "GDT518_CORRECT_LOST"
        elif candidates[base_top_index].recipe != candidates[top_index].recipe:
            change = "ERROR_CHANGED_STILL_WRONG"
        else:
            change = "GDT518_ERROR_UNCHANGED"
        output.append(
            {
                "surface": surface,
                "occurrence_count": target["occurrence_count"],
                "physical_pages": target["physical_pages"],
                "truth_recipe": G517.recipe_text(truth),
                "candidate_count_capped": len(candidates),
                "gdt518_rank": base_rank,
                "gdt518_top1": G517.recipe_text(candidates[base_top_index].recipe),
                "gdt519_rank": selected_rank,
                "gdt519_top1": G517.recipe_text(candidates[top_index].recipe),
                "gdt519_top5": " | ".join(
                    G517.recipe_text(candidates[index].recipe) for index in selected_order[:5]
                ),
                "truth_base_score": f"{float(candidate_values[truth_index]['base_score']):.9f}",
                "truth_anchor_cost": f"{truth_alignment_cost:.9f}",
                "truth_selected_score": f"{float(candidate_values[truth_index]['selected_score']):.9f}",
                "truth_alignment_trace": truth_trace,
                "top1_base_score": f"{float(candidate_values[top_index]['base_score']):.9f}",
                "top1_anchor_cost": f"{top_alignment_cost:.9f}",
                "top1_selected_score": f"{float(candidate_values[top_index]['selected_score']):.9f}",
                "top1_alignment_trace": top_trace,
                "decision_change_class": change,
                "working_policy": "KNOWN_EVENT_OR_SURFACE_RECIPE_STILL_WINS__ANCHOR_RERANKS_ONLY_FINITE_UNKNOWN_CANDIDATES",
            }
        )
        if selected_rank != 1 or base_rank != selected_rank:
            for selected_position, index in enumerate(selected_order[:12], 1):
                row = candidate_values[index]
                candidate = row["candidate"]
                _, trace = alignment_trace(surface, candidate.recipe, matrix)
                candidate_rows.append(
                    {
                        "surface": surface,
                        "truth_recipe": G517.recipe_text(truth),
                        "candidate_is_truth": "YES" if candidate.recipe == truth else "NO",
                        "gdt517_compiler_rank": int(row["base_index"]) + 1,
                        "gdt519_rank": selected_position,
                        "candidate_recipe": G517.recipe_text(candidate.recipe),
                        "gdt518_base_score": f"{float(row['base_score']):.9f}",
                        "anchor_cost": f"{float(row['anchor_cost']):.9f}",
                        "gdt519_score": f"{float(row['selected_score']):.9f}",
                        "alignment_trace": trace,
                    }
                )

    ladder = []
    for weight in WEIGHT_LADDER:
        ladder.append(
            {
                "scope": "CURRENT_159_OLD26_TO_NEW4",
                "model_stage": "GDT518_PLUS_MONOTONE_ANCHOR",
                "anchor_weight": weight,
                **rank_metrics(weight_ranks[weight]),
            }
        )
    base_metrics = rank_metrics(base_ranks)
    selected_metrics = rank_metrics(selected_ranks)
    class_counts = Counter(str(row["decision_change_class"]) for row in output)
    result = {
        "experiment_id": "GDT519",
        "status": "PASS_VISIBLE_STEM_ANCHOR_TRANSDUCER",
        "claim_ceiling": "EXPLORATORY_VISIBLE_STEM_ALIGNMENT__NO_CONFIRMED_LEXEME_OR_PLAINTEXT",
        "anchor_policy": {
            "canonical_atom_count": sum(len(sequence) == 1 for sequence in deck),
            "full_old26_renderer_sequence_count": len(deck),
            "full_old26_multi_atom_renderer_sequence_count": sum(
                len(sequence) > 1 for sequence in deck
            ),
            "full_old26_anchor_option_count": sum(len(options) for options in deck.values()),
            "alias_min_support": ALIAS_MIN_SUPPORT,
            "single_atom_alias_min_share": ALIAS_MIN_SHARE,
            "multi_atom_alias_min_share": MULTI_ALIAS_MIN_SHARE,
            "max_renderer_atoms": MAX_RENDERER_ATOMS,
            "alias_limit_per_atom": ALIAS_LIMIT_PER_ATOM,
            "alias_edit_penalty": ALIAS_EDIT_PENALTY,
            "alias_evidence_penalty": ALIAS_EVIDENCE_PENALTY,
            "surface_deletion_cost": 1,
            "missing_anchor_insertion_cost": 2,
            "substitution_cost": 1,
            "selected_anchor_weight": SELECTED_ANCHOR_WEIGHT,
        },
        "current_gdt518_metrics": base_metrics,
        "current_gdt519_metrics": selected_metrics,
        "current_net_top1_gain": (
            selected_metrics["top1_exact_count"] - base_metrics["top1_exact_count"]
        ),
        "current_rank_sum_reduction": base_metrics["rank_sum"] - selected_metrics["rank_sum"],
        "current_decision_change_classes": dict(sorted(class_counts.items())),
        "guard": "STRUCTURAL_ATOM_ANCHORS_ARE_VISIBLE_SPELLING_HANDLES_NOT_ENGLISH_WORD_MEANINGS__KNOWN_CARDS_KEEP_PRECEDENCE",
    }
    return output, candidate_rows, alias_rows, ladder, result


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    old = read_tsv(G518.G407_RUNNING)
    selected = read_tsv(G518.G516_SELECTED)
    targets = read_tsv(G518.G516_NEW)
    rehearsal_rows, rehearsal_aliases, rehearsal_ladder = fold_rehearsal(old)
    current_rows, candidate_rows, full_aliases, current_ladder, result = current_benchmark(
        old, selected, targets
    )
    result["old26_four_fold_rehearsal"] = next(
        {
            "selected_anchor_metrics": {
                key: int(value)
                for key, value in row.items()
                if key not in {"scope", "model_stage", "anchor_weight"}
            }
        }
        for row in rehearsal_ladder
        if row["model_stage"] == "FOLD_ANCHOR_SELECTED"
    )

    write_tsv(
        OUT / "gdt519_1558_four_fold_surface_rehearsal.tsv",
        rehearsal_rows,
        [
            "fold", "surface", "truth_recipe", "candidate_count_capped", "truth_generated",
            "compiler_rank", "form_decoder_rank", "anchor_rank", "compiler_top1",
            "form_decoder_top1", "anchor_top1", "truth_anchor_cost", "anchor_top1_cost",
        ],
    )
    write_tsv(
        OUT / "gdt519_anchor_alias_lexicon.tsv",
        rehearsal_aliases + full_aliases,
        [
            "model", "atom_sequence", "atom_count", "canonical_anchor", "alias_rank",
            "surface_alias", "alias_source", "support", "support_share", "alias_penalty",
        ],
    )
    current_fields = [
        "surface", "occurrence_count", "physical_pages", "truth_recipe",
        "candidate_count_capped", "gdt518_rank", "gdt518_top1", "gdt519_rank",
        "gdt519_top1", "gdt519_top5", "truth_base_score", "truth_anchor_cost",
        "truth_selected_score", "truth_alignment_trace", "top1_base_score",
        "top1_anchor_cost", "top1_selected_score", "top1_alignment_trace",
        "decision_change_class", "working_policy",
    ]
    write_tsv(OUT / "gdt519_159_anchor_rerank.tsv", current_rows, current_fields)
    write_tsv(
        OUT / "gdt519_remaining_top1_error_atlas.tsv",
        [row for row in current_rows if int(row["gdt519_rank"]) != 1],
        current_fields,
    )
    write_tsv(
        OUT / "gdt519_changed_decision_atlas.tsv",
        [row for row in current_rows if row["gdt518_top1"] != row["gdt519_top1"]],
        current_fields,
    )
    write_tsv(
        OUT / "gdt519_candidate_alignment_atlas.tsv",
        candidate_rows,
        [
            "surface", "truth_recipe", "candidate_is_truth", "gdt517_compiler_rank",
            "gdt519_rank", "candidate_recipe", "gdt518_base_score", "anchor_cost",
            "gdt519_score", "alignment_trace",
        ],
    )
    ladder = rehearsal_ladder + current_ladder
    write_tsv(
        OUT / "gdt519_model_ladder.tsv",
        ladder,
        [
            "scope", "model_stage", "anchor_weight", "target_count",
            "truth_generated_count", "top1_exact_count", "top2_exact_count",
            "top3_exact_count", "top5_exact_count", "rank_sum", "deepest_truth_rank",
        ],
    )
    write_json(OUT / "gdt519_result.json", result)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
