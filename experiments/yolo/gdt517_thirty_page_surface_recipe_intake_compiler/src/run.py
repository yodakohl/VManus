#!/usr/bin/env python3
"""Compile a visible surface into finite recipe candidates, then replay the current intake."""

from __future__ import annotations

import csv
import importlib.util
import json
import math
import statistics
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt517_thirty_page_surface_recipe_intake_compiler"
OUT = BASE / "artifacts"

G407_RUNNING = ROOT / "experiments/yolo/gdt407_unified_twenty_six_page_workshop_edition/artifacts/gdt407_4576_running_event_edition.tsv"
G407_LOCAL = ROOT / "experiments/yolo/gdt407_unified_twenty_six_page_workshop_edition/artifacts/gdt407_693_local_group_edition.tsv"
G413_COMPONENTS = ROOT / "experiments/yolo/gdt413_twenty_six_page_semantic_working_edition/artifacts/gdt413_46_component_working_dictionary.tsv"
G451_INTAKE = ROOT / "experiments/yolo/gdt451_integrated_context_safe_intake/src/intake_command.py"
G473_LOCAL = ROOT / "experiments/yolo/gdt473_unified_local_address_working_edition/artifacts/gdt473_183_unified_address_working_edition.tsv"
G513_LOCAL = ROOT / "experiments/yolo/gdt513_remaining_local_group_semantic_census/artifacts/gdt513_510_remaining_local_working_edition.tsv"
G516_SELECTED = ROOT / "experiments/yolo/gdt516_thirty_page_new_surface_family_consolidation/artifacts/gdt516_597_contextualized_event_edition.tsv"
G516_UNIFIED = ROOT / "experiments/yolo/gdt516_thirty_page_new_surface_family_consolidation/artifacts/gdt516_5866_contextualized_unified_group_ledger.tsv"
G516_NEW = ROOT / "experiments/yolo/gdt516_thirty_page_new_surface_family_consolidation/artifacts/gdt516_159_new_surface_family_atlas.tsv"

MODEL_CAP = 2000
MIN_MAPPING_SHARE = 0.05
ACCEPT_SHARE = 0.75
AMBIGUITY_LOCK = ("dy", ("DY",))


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


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def atoms(recipe: str) -> tuple[str, ...]:
    return tuple(part for part in recipe.split("+") if part and part != "NONE")


def recipe_text(recipe: tuple[str, ...]) -> str:
    return "+".join(recipe) if recipe else "NONE"


@dataclass
class RecipeModel:
    name: str
    evidence: dict[str, Counter[tuple[str, ...]]]
    source_support: dict[tuple[str, tuple[str, ...]], Counter[str]]
    rounds: list[dict[str, object]]
    training_event_count: int
    training_surface_count: int
    direct_evidence: dict[str, Counter[tuple[str, ...]]]
    complete_evidence: dict[str, Counter[tuple[str, ...]]]


def counter_copy(evidence: dict[str, Counter[tuple[str, ...]]]) -> dict[str, Counter[tuple[str, ...]]]:
    return {surface: Counter(values) for surface, values in evidence.items()}


def add_evidence(
    evidence: dict[str, Counter[tuple[str, ...]]],
    source_support: dict[tuple[str, tuple[str, ...]], Counter[str]],
    surface: str,
    recipe: tuple[str, ...],
    weight: int,
    source: str,
) -> None:
    if not surface or not recipe or weight <= 0:
        return
    evidence.setdefault(surface, Counter())[recipe] += weight
    source_support.setdefault((surface, recipe), Counter())[source] += weight


def build_model(name: str, rows: list[dict[str, str]], recipe_field: str) -> RecipeModel:
    frequency: Counter[tuple[str, tuple[str, ...]]] = Counter()
    surface_recipes: dict[str, set[tuple[str, ...]]] = defaultdict(set)
    for row in rows:
        recipe = atoms(row[recipe_field])
        surface = row["surface"]
        frequency[(surface, recipe)] += 1
        surface_recipes[surface].add(recipe)
    conflicts = {surface: recipes for surface, recipes in surface_recipes.items() if len(recipes) != 1}
    if conflicts:
        raise RuntimeError(f"{name}: non-invariant training surfaces: {len(conflicts)}")
    forms = {surface: next(iter(recipes)) for surface, recipes in surface_recipes.items()}

    evidence: dict[str, Counter[tuple[str, ...]]] = {}
    source_support: dict[tuple[str, tuple[str, ...]], Counter[str]] = {}
    for (surface, recipe), count in frequency.items():
        add_evidence(evidence, source_support, surface, recipe, count, "COMPLETE_RECIPE")
    complete_evidence = counter_copy(evidence)

    # Direct insertion residuals. Positional evidence is deliberately retained:
    # two independently aligned deletions are two alignment contacts.
    for big_surface, big_recipe in forms.items():
        big_count = frequency[(big_surface, big_recipe)]
        for left in range(len(big_surface)):
            for right in range(left + 1, len(big_surface) + 1):
                small_surface = big_surface[:left] + big_surface[right:]
                if not small_surface or small_surface not in forms:
                    continue
                small_recipe = forms[small_surface]
                small_count = frequency[(small_surface, small_recipe)]
                weight = min(big_count, small_count)
                for atom_left in range(len(big_recipe)):
                    for atom_right in range(atom_left + 1, len(big_recipe) + 1):
                        if big_recipe[:atom_left] + big_recipe[atom_right:] != small_recipe:
                            continue
                        add_evidence(
                            evidence,
                            source_support,
                            big_surface[left:right],
                            big_recipe[atom_left:atom_right],
                            weight,
                            "DIRECT_INSERTION_RESIDUAL",
                        )
    direct_evidence = counter_copy(evidence)

    # Prefix/suffix closure. Supports are snapshotted at the start of each
    # round, so iteration order cannot amplify a mapping inside that round.
    # dy -> DY is locked after round zero because GDT516 proves other readings.
    seen_relations: set[tuple[object, ...]] = set()
    rounds: list[dict[str, object]] = []
    for iteration in range(20):
        accepted: dict[str, tuple[tuple[str, ...], int]] = {}
        for surface, candidates in evidence.items():
            total = sum(candidates.values())
            if not total:
                continue
            top_recipe = max(candidates, key=lambda item: (candidates[item], item))
            top_support = candidates[top_recipe]
            if top_support / total >= ACCEPT_SHARE:
                accepted[surface] = (top_recipe, top_support)

        added = 0
        ambiguity_rejections = 0
        for big_surface, (big_recipe, big_support) in list(accepted.items()):
            for cut in range(1, len(big_surface)):
                options = (
                    ("PREFIX", big_surface[:cut], big_surface[cut:]),
                    ("SUFFIX", big_surface[cut:], big_surface[:cut]),
                )
                for orientation, small_surface, residual_surface in options:
                    if small_surface not in accepted:
                        continue
                    small_recipe, small_support = accepted[small_surface]
                    if orientation == "PREFIX":
                        if len(small_recipe) >= len(big_recipe) or big_recipe[: len(small_recipe)] != small_recipe:
                            continue
                        residual_recipe = big_recipe[len(small_recipe) :]
                    else:
                        if len(small_recipe) >= len(big_recipe) or big_recipe[-len(small_recipe) :] != small_recipe:
                            continue
                        residual_recipe = big_recipe[: -len(small_recipe)]
                    relation = (orientation, big_surface, big_recipe, small_surface, small_recipe)
                    if relation in seen_relations:
                        continue
                    seen_relations.add(relation)
                    if iteration >= 1 and (residual_surface, residual_recipe) == AMBIGUITY_LOCK:
                        ambiguity_rejections += 1
                        continue
                    add_evidence(
                        evidence,
                        source_support,
                        residual_surface,
                        residual_recipe,
                        min(big_support, small_support),
                        "ITERATIVE_EDGE_RESIDUAL",
                    )
                    added += 1
        rounds.append(
            {
                "iteration": iteration,
                "accepted_high_confidence_chunks": len(accepted),
                "new_residual_derivations": added,
                "ambiguity_lock_rejections": ambiguity_rejections,
                "visible_chunk_count": len(evidence),
                "mapping_count": sum(len(values) for values in evidence.values()),
            }
        )
        if added == 0:
            break

    add_evidence(evidence, source_support, "x", ("LOCAL_X",), 10_000, "GDT516_FINITE_LOCAL_POLICY")
    add_evidence(evidence, source_support, "c", ("LOCAL_C",), 10_000, "GDT516_FINITE_LOCAL_POLICY")
    return RecipeModel(
        name=name,
        evidence=evidence,
        source_support=source_support,
        rounds=rounds,
        training_event_count=len(rows),
        training_surface_count=len(forms),
        direct_evidence=direct_evidence,
        complete_evidence=complete_evidence,
    )


def retained_mappings(evidence: dict[str, Counter[tuple[str, ...]]]) -> dict[str, list[dict[str, object]]]:
    output: dict[str, list[dict[str, object]]] = {}
    for surface, candidates in evidence.items():
        total = sum(candidates.values())
        rows = []
        for recipe, support in candidates.items():
            share = support / total
            if share < MIN_MAPPING_SHARE:
                continue
            score = math.log1p(support) + 2 * math.log(share) - 0.1 * len(recipe)
            rows.append(
                {
                    "recipe": recipe,
                    "support": support,
                    "share": share,
                    "score": score,
                    "scope": (
                        "F66R_LOCAL_RECORD_ONLY"
                        if any(atom in {"LOCAL_X", "LOCAL_C"} for atom in recipe)
                        else "GENERAL_RUNNING_COMPILER"
                    ),
                }
            )
        if rows:
            output[surface] = sorted(
                rows,
                key=lambda row: (-int(row["support"]), tuple(row["recipe"])),
            )[:10]
    return output


@dataclass(frozen=True)
class Candidate:
    recipe: tuple[str, ...]
    chunk_count: int
    score: float
    path: tuple[tuple[str, tuple[str, ...], int, float], ...]


def parse_surface(
    surface: str,
    mappings: dict[str, list[dict[str, object]]],
    cap: int = MODEL_CAP,
    allow_f66r_local: bool = False,
) -> list[Candidate]:
    by_initial: dict[str, list[str]] = defaultdict(list)
    for chunk in mappings:
        if chunk:
            by_initial[chunk[0]].append(chunk)
    for chunks in by_initial.values():
        chunks.sort(key=lambda item: (-len(item), item))

    states: list[dict[tuple[str, ...], tuple[int, float, tuple[tuple[str, tuple[str, ...], int, float], ...]]]] = [
        {} for _ in range(len(surface) + 1)
    ]
    states[0][tuple()] = (0, 0.0, tuple())
    for position in range(len(surface)):
        if not states[position]:
            continue
        current = sorted(
            states[position].items(),
            key=lambda item: (item[1][0], -item[1][1], item[0]),
        )[:cap]
        for base_recipe, (base_chunks, base_score, base_path) in current:
            for chunk in by_initial.get(surface[position], []):
                if not surface.startswith(chunk, position):
                    continue
                destination = position + len(chunk)
                for mapping in mappings[chunk]:
                    if mapping.get("scope") == "F66R_LOCAL_RECORD_ONLY" and not allow_f66r_local:
                        continue
                    mapped_recipe = tuple(mapping["recipe"])
                    recipe = base_recipe + mapped_recipe
                    value = (
                        base_chunks + 1,
                        base_score + float(mapping["score"]),
                        base_path
                        + ((chunk, mapped_recipe, int(mapping["support"]), float(mapping["share"])),),
                    )
                    previous = states[destination].get(recipe)
                    if previous is None or (value[0], -value[1]) < (previous[0], -previous[1]):
                        states[destination][recipe] = value
        for destination in range(position + 1, len(surface) + 1):
            if len(states[destination]) > cap * 4:
                states[destination] = dict(
                    sorted(
                        states[destination].items(),
                        key=lambda item: (item[1][0], -item[1][1], item[0]),
                    )[:cap]
                )
    candidates = [
        Candidate(recipe, value[0], value[1], value[2]) for recipe, value in states[-1].items()
    ]
    return sorted(candidates, key=lambda item: (item.chunk_count, -item.score, item.recipe))[:cap]


def path_text(candidate: Candidate | None) -> str:
    if candidate is None:
        return "NONE"
    return " | ".join(
        f"{chunk}={recipe_text(recipe)}@{share:.4f}/{support}"
        for chunk, recipe, support, share in candidate.path
    )


def literal_renderer() -> dict[str, str]:
    values = {row["atom"]: row["working_value_de"] for row in read_tsv(G413_COMPONENTS)}
    values.update({"LOCAL_X": "[LOCAL_X:LOKAL]", "LOCAL_C": "[LOCAL_C:LOKAL]"})
    return values


def render_literal(recipe: tuple[str, ...], values: dict[str, str]) -> str:
    return " · ".join(values.get(atom, f"[{atom}:PAKET/LOKAL]") for atom in recipe)


def benchmark_rows(
    targets: list[dict[str, str]],
    mappings: dict[str, list[dict[str, object]]],
    allow_f66r_local: bool = False,
) -> tuple[list[dict[str, object]], dict[str, object]]:
    output: list[dict[str, object]] = []
    ranks: list[int] = []
    candidate_counts: list[int] = []
    values = literal_renderer()
    for target in targets:
        truth = atoms(target["gdt516_context_recipe"])
        candidates = parse_surface(target["surface"], mappings, allow_f66r_local=allow_f66r_local)
        rank = next((index + 1 for index, candidate in enumerate(candidates) if candidate.recipe == truth), 0)
        ranks.append(rank)
        candidate_counts.append(len(candidates))
        top = candidates[0] if candidates else None
        row: dict[str, object] = {
            "surface": target["surface"],
            "occurrence_count": target["occurrence_count"],
            "physical_pages": target["physical_pages"],
            "gdt516_context_recipe": target["gdt516_context_recipe"],
            "parsed": "YES" if candidates else "NO",
            "candidate_count_capped": len(candidates),
            "candidate_cap_reached": "YES" if len(candidates) == MODEL_CAP else "NO",
            "gdt516_recipe_rank": rank,
            "recovery_class": (
                "TOP1_EXACT"
                if rank == 1
                else "FINITE_TOP5_ALTERNATIVE"
                if 1 < rank <= 5
                else "DEEP_FINITE_ALTERNATIVE"
                if rank > 5
                else "TARGET_NOT_GENERATED"
            ),
            "top1_recipe": recipe_text(top.recipe) if top else "NONE",
            "top1_literal_de": render_literal(top.recipe, values) if top else "NONE",
            "top1_chunk_count": top.chunk_count if top else 0,
            "top1_score": f"{top.score:.6f}" if top else "NONE",
            "top1_path": path_text(top),
        }
        for index in range(5):
            candidate = candidates[index] if index < len(candidates) else None
            row[f"candidate_{index + 1}_recipe"] = recipe_text(candidate.recipe) if candidate else "NONE"
        output.append(row)
    positive_ranks = [rank for rank in ranks if rank]
    metrics: dict[str, object] = {
        "target_count": len(targets),
        "parsed_count": sum(count > 0 for count in candidate_counts),
        "truth_generated_count": len(positive_ranks),
        "top1_exact_count": ranks.count(1),
        "top2_exact_count": sum(0 < rank <= 2 for rank in ranks),
        "top3_exact_count": sum(0 < rank <= 3 for rank in ranks),
        "top5_exact_count": sum(0 < rank <= 5 for rank in ranks),
        "deepest_truth_rank": max(positive_ranks, default=0),
        "rank_sum": sum(positive_ranks),
        "median_candidate_count": statistics.median(candidate_counts),
        "max_candidate_count": max(candidate_counts, default=0),
    }
    return output, metrics


def mapping_artifact_rows(model: RecipeModel) -> list[dict[str, object]]:
    retained = retained_mappings(model.evidence)
    rows: list[dict[str, object]] = []
    for surface in sorted(retained):
        all_candidates = model.evidence[surface]
        total = sum(all_candidates.values())
        top_recipe = max(all_candidates, key=lambda item: (all_candidates[item], item))
        top_share = all_candidates[top_recipe] / total
        for rank, mapping in enumerate(retained[surface], 1):
            recipe = tuple(mapping["recipe"])
            sources = model.source_support.get((surface, recipe), Counter())
            rows.append(
                {
                    "model": model.name,
                    "surface_chunk": surface,
                    "mapping_rank": rank,
                    "recipe": recipe_text(recipe),
                    "recipe_atom_count": len(recipe),
                    "support": mapping["support"],
                    "total_surface_support": total,
                    "support_share": f"{float(mapping['share']):.6f}",
                    "derivation_score": f"{float(mapping['score']):.6f}",
                    "high_confidence_top_mapping": (
                        "YES" if recipe == top_recipe and top_share >= ACCEPT_SHARE else "NO"
                    ),
                    "evidence_sources": " | ".join(
                        f"{source}:{count}" for source, count in sorted(sources.items())
                    )
                    or "NONE",
                    "ambiguity_policy": (
                        "CONTEXT_SENSITIVE_DY_RETAIN_ALTERNATIVES"
                        if surface == "dy"
                        else "FINITE_F66R_LOCAL_TAG"
                        if surface in {"x", "c"}
                        else "NONE"
                    ),
                    "mapping_scope": mapping["scope"],
                }
            )
    return rows


def model_ladder(model: RecipeModel, targets: list[dict[str, str]]) -> list[dict[str, object]]:
    atomic = {
        surface: Counter({recipe: support for recipe, support in recipes.items() if len(recipe) == 1})
        for surface, recipes in model.complete_evidence.items()
    }
    stages = [
        ("ATOMIC_OLD_COMPLETE_FORMS_ONLY", {surface: recipes for surface, recipes in atomic.items() if recipes}),
        ("ALL_OLD_COMPLETE_RECIPE_CHUNKS", model.complete_evidence),
        ("PLUS_DIRECT_INSERTION_RESIDUALS", model.direct_evidence),
        ("PLUS_ITERATIVE_RESIDUAL_CLOSURE", model.evidence),
    ]
    output = []
    for stage, evidence in stages:
        mappings = retained_mappings(evidence)
        _, metrics = benchmark_rows(
            targets,
            mappings,
            allow_f66r_local=stage == "PLUS_ITERATIVE_RESIDUAL_CLOSURE",
        )
        output.append(
            {
                "model_stage": stage,
                "visible_chunk_count": len(mappings),
                "retained_mapping_count": sum(len(values) for values in mappings.values()),
                **metrics,
            }
        )
    return output


def build_exact_dictionary(
    unified: list[dict[str, str]],
    selected: list[dict[str, str]],
    old_running: list[dict[str, str]],
    g473: list[dict[str, str]],
    g513: list[dict[str, str]],
) -> list[dict[str, object]]:
    selected_by_id = {row["event_id"]: row for row in selected}
    old_running_by_id = {row["source_event_id"]: row for row in old_running}
    g473_by_id = {row["source_event_id"]: row for row in g473}
    g513_by_id = {row["source_event_id"]: row for row in g513}
    output: list[dict[str, object]] = []
    for row in unified:
        event_id = row["source_event_id"]
        common: dict[str, object] = {
            "global_group_id": row["global_group_id"],
            "source_event_id": event_id,
            "physical_page": row["physical_page"],
            "register": row["register"],
            "locus": row["locus"],
            "source_order": row["source_order"],
            "owner_de": row["owner_de"],
            "surface": row["surface"],
            "group_kind": row["group_kind"],
        }
        if row["group_kind"] == "RUNNING_EVENT":
            selected_row = selected_by_id.get(event_id)
            old_row = old_running_by_id.get(event_id)
            if selected_row:
                role = selected_row["content_role"]
                reading_prefix = selected_row["default_working_reading_de"].split(": ", 1)[0]
                reading = f"{reading_prefix}: {selected_row['gdt516_literal_reading_de']}"
                source = "GDT516_SELECTED_CONTEXT_EDITION"
            elif old_row:
                role = "RUNNING_RECIPE_CARD"
                reading = f"ABLAUF BEI {row['owner_de']}: {row['gdt516_literal_reading_de']}"
                source = "GDT407_RUNNING_RECIPE_EDITION"
            else:
                raise RuntimeError(f"Running event lacks source card: {event_id}")
            selected_local_roles = {
                "LOCAL_NAME_WITH_FUNCTION_SHELL_CARD", "LOCAL_CLASS_OR_NAME_CARD",
                "MARGINAL_LABEL_CARD", "MARGINAL_SIGN_CARD", "LATE_ADDITION_CARD",
            }
            is_selected_local_role = role in selected_local_roles
            portable_recipe = row["gdt516_context_recipe"]
            if is_selected_local_role:
                portable_atoms = [
                    atom for atom in atoms(portable_recipe) if atom not in {"LOCAL_X", "LOCAL_C"}
                ]
                portable_recipe = "+".join(portable_atoms) if portable_atoms else "NONE"
            common.update(
                {
                    "execution_domain": (
                        "LOCAL_RECORD" if is_selected_local_role else "PROSE_STREAM"
                    ),
                    "record_role": role,
                    "exact_event_recipe": row["gdt516_context_recipe"],
                    "portable_function_recipe": portable_recipe,
                    "working_reading_de": reading,
                    "semantic_source": source,
                    "package_status": (
                        "FINITE_SELECTED_LOCAL_ROLE_CARD"
                        if is_selected_local_role else "VISIBLE_COMPONENT_RECIPE"
                    ),
                    "surface_only_lookup_policy": (
                        "EVENT_CARD_WINS__SURFACE_CAN_HAVE_FINITE_LOCAL_OPTIONS"
                        if is_selected_local_role else "INVARIANT_PROSE_SURFACE_RECIPE"
                    ),
                }
            )
        elif event_id in g473_by_id:
            local = g473_by_id[event_id]
            full_formula = local["coverage_class"] == "FULL_FUNCTION_FORMULA"
            common.update(
                {
                    "execution_domain": "LOCAL_RECORD",
                    "record_role": local["content_class"],
                    "exact_event_recipe": (
                        local["working_recipe"] if full_formula else f"LOCAL_LABEL_PACKAGE::{local['edition_id']}"
                    ),
                    "portable_function_recipe": local["working_recipe"],
                    "working_reading_de": local["working_reading_de"],
                    "semantic_source": "GDT473_COMPLETE_LOCAL_ADDRESS_EDITION",
                    "package_status": local["coverage_class"],
                    "surface_only_lookup_policy": "EVENT_PACKAGE_WINS__SURFACE_CAN_HAVE_FINITE_LOCAL_OPTIONS",
                }
            )
        elif event_id in g513_by_id:
            local = g513_by_id[event_id]
            common.update(
                {
                    "execution_domain": "LOCAL_RECORD",
                    "record_role": local["record_role"],
                    "exact_event_recipe": local["component_recipe"],
                    "portable_function_recipe": local["portable_core_atoms"],
                    "working_reading_de": local["default_working_reading_de"],
                    "semantic_source": "GDT513_REMAINING_LOCAL_WORKING_EDITION",
                    "package_status": local["meaning_status"],
                    "surface_only_lookup_policy": "EVENT_CARD_WINS__SURFACE_CAN_HAVE_FINITE_LOCAL_OPTIONS",
                }
            )
        elif event_id in selected_by_id:
            local = selected_by_id[event_id]
            reading_prefix = local["default_working_reading_de"].split(": ", 1)[0]
            local_atoms = [
                atom for atom in atoms(row["gdt516_context_recipe"])
                if atom not in {"LOCAL_X", "LOCAL_C"}
            ]
            common.update(
                {
                    "execution_domain": "LOCAL_RECORD",
                    "record_role": local["content_role"],
                    "exact_event_recipe": row["gdt516_context_recipe"],
                    "portable_function_recipe": "+".join(local_atoms) if local_atoms else "NONE",
                    "working_reading_de": f"{reading_prefix}: {local['gdt516_literal_reading_de']}",
                    "semantic_source": "GDT516_SELECTED_LOCAL_CONTEXT_EDITION",
                    "package_status": "FINITE_SELECTED_PAGE_LOCAL_CARD",
                    "surface_only_lookup_policy": "EVENT_CARD_WINS__SURFACE_CAN_HAVE_FINITE_LOCAL_OPTIONS",
                }
            )
        else:
            raise RuntimeError(f"Local event lacks GDT473/GDT513/GDT516 card: {event_id}")
        output.append(common)
    return output


def build_surface_index(exact_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    groups: dict[tuple[str, str, str], list[dict[str, object]]] = defaultdict(list)
    for row in exact_rows:
        key = (
            str(row["surface"]), str(row["execution_domain"]), str(row["exact_event_recipe"]),
        )
        groups[key].append(row)
    option_counts = Counter((key[0], key[1]) for key in groups)
    output = []
    for ordinal, (key, rows) in enumerate(sorted(groups.items()), 1):
        surface, domain, recipe = key
        roles = sorted({str(row["record_role"]) for row in rows})
        readings = sorted({str(row["working_reading_de"]) for row in rows})
        output.append(
            {
                "surface_option_id": f"G517-S{ordinal:04d}",
                "surface": surface,
                "execution_domain": domain,
                "finite_recipe_option_count_for_surface_domain": option_counts[(surface, domain)],
                "record_roles": "|".join(roles),
                "exact_event_recipe": recipe,
                "reading_variant_count": len(readings),
                "surface_default_reading_de": (
                    readings[0]
                    if len(readings) == 1
                    else f"EREIGNISKONTEXT_WAEHLT_AUS_{len(readings)}_LESARTEN"
                ),
                "event_count": len(rows),
                "physical_pages": "|".join(sorted({str(row["physical_page"]) for row in rows})),
                "owners_de": " | ".join(sorted({str(row["owner_de"]) for row in rows})),
                "source_event_ids": "|".join(str(row["source_event_id"]) for row in rows),
                "lookup_policy": rows[0]["surface_only_lookup_policy"],
            }
        )
    return output


def replay_selected_prose(selected: list[dict[str, str]]) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    intake = load_module("gdt451_intake_for_gdt517", G451_INTAKE)
    groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    statement_order: list[str] = []
    for row in selected:
        if row["source_kind"] != "P":
            continue
        statement = row["statement_id"]
        if statement not in groups:
            statement_order.append(statement)
        groups[statement].append(row)

    output: list[dict[str, object]] = []
    repairs: list[dict[str, object]] = []
    ordinal = 0
    for statement in statement_order:
        cards = groups[statement]
        incoming_action = "NONE"
        incoming_argument = "NONE"
        for index, row in enumerate(cards):
            ordinal += 1
            recipe = row["gdt516_context_recipe"]
            next_recipe = cards[index + 1]["gdt516_context_recipe"] if index + 1 < len(cards) else "NONE"
            certificate = intake.issue_integrated_certificate(
                recipe, incoming_action, incoming_argument, None, next_recipe
            )
            raw_decision = str(certificate["final_execution_decision"])
            raw_route = str(certificate["final_execution_route"])
            final_decision = raw_decision
            final_route = raw_route
            override = "NONE"
            if raw_decision == "STOP" and row["content_role"] == "ITINERARY_OR_ADDRESS_CARD":
                final_decision = "READ_ROLE_CONTAINER"
                final_route = "ROLE_CONTAINER_DOES_NOT_EXECUTE_CLOSE"
                override = "ROLE_SEPARATION"
            elif raw_decision == "STOP" and row["content_role"] in {
                "LOCAL_NAME_WITH_FUNCTION_SHELL_CARD", "LOCAL_CLASS_OR_NAME_CARD",
                "MARGINAL_LABEL_CARD", "MARGINAL_SIGN_CARD", "LATE_ADDITION_CARD",
            }:
                final_decision = "READ_LOCAL_SHELL"
                final_route = "LOCAL_RECORD_DOES_NOT_ENTER_PORTABLE_ACTION_GATE"
                override = "ROLE_SEPARATION"
            elif raw_decision == "STOP" and row["surface"] == "shso" and recipe == "SH+S+O":
                final_decision = "READ_AMBER"
                final_route = "FINITE_SELECTED_SH_GT_S_DIRECT_PAIR_LICENSE"
                override = "ONE_SELECTED_DIRECT_PAIR"

            outgoing_action = incoming_action
            outgoing_argument = incoming_argument
            if raw_decision in {"READ", "READ_AMBER"}:
                outgoing_action = str(certificate["outgoing_action_v2"])
                outgoing_argument = str(certificate["outgoing_argument_v2"])
            elif override == "ONE_SELECTED_DIRECT_PAIR":
                actions = str(certificate["explicit_action_roots"])
                arguments = str(certificate["explicit_argument_roots"])
                if actions != "NONE":
                    outgoing_action = actions.split("|")[-1]
                if arguments != "NONE":
                    outgoing_argument = arguments.split("|")[-1]

            result = {
                "replay_ordinal": ordinal,
                "source_event_id": row["event_id"],
                "physical_page": row["physical_page"],
                "statement_id": statement,
                "card_ordinal_in_statement": row["card_ordinal_in_statement"],
                "surface": row["surface"],
                "content_role": row["content_role"],
                "recipe": recipe,
                "incoming_action": incoming_action,
                "incoming_argument": incoming_argument,
                "raw_gdt451_decision": raw_decision,
                "raw_gdt451_route": raw_route,
                "blocked_factor_rules": certificate["blocked_factor_rules"],
                "gdt517_final_decision": final_decision,
                "gdt517_final_route": final_route,
                "finite_override": override,
                "outgoing_action": outgoing_action,
                "outgoing_argument": outgoing_argument,
                "state_policy": (
                    "ROLE_CARD_PRESERVES_STREAM_STATE"
                    if override == "ROLE_SEPARATION"
                    else "ACCEPTED_CARD_ADVANCES_STATE"
                    if final_decision in {"READ", "READ_AMBER"}
                    else "STOP_PRESERVES_STATE"
                ),
            }
            output.append(result)
            if raw_decision != "READ":
                repairs.append(result)
            incoming_action = outgoing_action
            incoming_argument = outgoing_argument
    return output, repairs


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    old_running = read_tsv(G407_RUNNING)
    old_local = read_tsv(G407_LOCAL)
    selected = read_tsv(G516_SELECTED)
    unified = read_tsv(G516_UNIFIED)
    targets = read_tsv(G516_NEW)
    g473 = read_tsv(G473_LOCAL)
    g513 = read_tsv(G513_LOCAL)

    old_model = build_model("OLD26_RUNNING", old_running, "component_recipe")
    thirty_running = [row for row in unified if row["group_kind"] == "RUNNING_EVENT"]
    current_model = build_model("CURRENT30_RUNNING", thirty_running, "gdt516_context_recipe")

    old_mapping_rows = mapping_artifact_rows(old_model)
    current_mapping_rows = mapping_artifact_rows(current_model)
    mapping_fields = [
        "model", "surface_chunk", "mapping_rank", "recipe", "recipe_atom_count", "support",
        "total_surface_support", "support_share", "derivation_score", "high_confidence_top_mapping",
        "evidence_sources", "ambiguity_policy", "mapping_scope",
    ]
    write_tsv(OUT / "gdt517_old26_chunk_mapping_lexicon.tsv", old_mapping_rows, mapping_fields)
    write_tsv(OUT / "gdt517_current30_chunk_mapping_lexicon.tsv", current_mapping_rows, mapping_fields)

    round_rows = [{"model": old_model.name, **row} for row in old_model.rounds] + [
        {"model": current_model.name, **row} for row in current_model.rounds
    ]
    write_tsv(
        OUT / "gdt517_residual_closure_iterations.tsv", round_rows,
        ["model", "iteration", "accepted_high_confidence_chunks", "new_residual_derivations",
         "ambiguity_lock_rejections", "visible_chunk_count", "mapping_count"],
    )

    recovery, recovery_metrics = benchmark_rows(
        targets, retained_mappings(old_model.evidence), allow_f66r_local=True
    )
    recovery_fields = [
        "surface", "occurrence_count", "physical_pages", "gdt516_context_recipe", "parsed",
        "candidate_count_capped", "candidate_cap_reached", "gdt516_recipe_rank", "recovery_class",
        "top1_recipe", "top1_literal_de", "top1_chunk_count", "top1_score", "top1_path",
        "candidate_1_recipe", "candidate_2_recipe", "candidate_3_recipe", "candidate_4_recipe",
        "candidate_5_recipe",
    ]
    write_tsv(OUT / "gdt517_159_new_surface_recovery.tsv", recovery, recovery_fields)
    disagreements = [row for row in recovery if row["recovery_class"] != "TOP1_EXACT"]
    write_tsv(OUT / "gdt517_top1_disagreement_atlas.tsv", disagreements, recovery_fields)

    ladder = model_ladder(old_model, targets)
    write_tsv(
        OUT / "gdt517_model_ladder.tsv", ladder,
        ["model_stage", "visible_chunk_count", "retained_mapping_count", "target_count", "parsed_count",
         "truth_generated_count", "top1_exact_count", "top2_exact_count", "top3_exact_count",
         "top5_exact_count", "deepest_truth_rank", "rank_sum", "median_candidate_count",
         "max_candidate_count"],
    )

    exact_rows = build_exact_dictionary(unified, selected, old_running, g473, g513)
    write_tsv(
        OUT / "gdt517_5866_exact_event_dictionary.tsv", exact_rows,
        ["global_group_id", "source_event_id", "physical_page", "register", "locus", "source_order",
         "owner_de", "surface", "group_kind", "execution_domain", "record_role", "exact_event_recipe",
         "portable_function_recipe", "working_reading_de", "semantic_source", "package_status",
         "surface_only_lookup_policy"],
    )
    surface_index = build_surface_index(exact_rows)
    write_tsv(
        OUT / "gdt517_current30_surface_role_index.tsv", surface_index,
        ["surface_option_id", "surface", "execution_domain", "finite_recipe_option_count_for_surface_domain",
         "record_roles", "exact_event_recipe", "reading_variant_count", "surface_default_reading_de",
         "event_count", "physical_pages", "owners_de", "source_event_ids", "lookup_policy"],
    )

    replay, repairs = replay_selected_prose(selected)
    replay_fields = [
        "replay_ordinal", "source_event_id", "physical_page", "statement_id", "card_ordinal_in_statement",
        "surface", "content_role", "recipe", "incoming_action", "incoming_argument",
        "raw_gdt451_decision", "raw_gdt451_route", "blocked_factor_rules", "gdt517_final_decision",
        "gdt517_final_route", "finite_override", "outgoing_action", "outgoing_argument", "state_policy",
    ]
    write_tsv(OUT / "gdt517_546_selected_prose_execution_replay.tsv", replay, replay_fields)
    write_tsv(OUT / "gdt517_non_green_and_role_repair_atlas.tsv", repairs, replay_fields)

    old_dy = next(
        row for row in old_mapping_rows if row["surface_chunk"] == "dy" and row["mapping_rank"] == 1
    )
    result = {
        "experiment_id": "GDT517",
        "status": "PASS_EXECUTABLE_SURFACE_TO_RECIPE_INTAKE",
        "claim_ceiling": "EXPLORATORY_WORKING_COMPILER__NO_CONFIRMED_LEXEME_OR_PLAINTEXT",
        "old26_training_events": len(old_running),
        "old26_training_surfaces": old_model.training_surface_count,
        "current30_running_events": len(thirty_running),
        "current30_running_surfaces": current_model.training_surface_count,
        "old26_retained_chunk_forms": len(retained_mappings(old_model.evidence)),
        "old26_retained_mappings": len(old_mapping_rows),
        "current30_retained_chunk_forms": len(retained_mappings(current_model.evidence)),
        "current30_retained_mappings": len(current_mapping_rows),
        "old26_closure_rounds": len(old_model.rounds),
        "current30_closure_rounds": len(current_model.rounds),
        "new_surface_recovery": recovery_metrics,
        "top1_disagreement_count": len(disagreements),
        "exact_event_dictionary_count": len(exact_rows),
        "surface_role_option_count": len(surface_index),
        "local_old_coverage": {
            "gdt407_local": len(old_local), "gdt473_complete": len(g473), "gdt513_complete": len(g513),
            "union_complete": len({row["source_event_id"] for row in g473 + g513}),
        },
        "selected_prose_replay_count": len(replay),
        "raw_execution_decisions": dict(Counter(str(row["raw_gdt451_decision"]) for row in replay)),
        "final_execution_decisions": dict(Counter(str(row["gdt517_final_decision"]) for row in replay)),
        "non_green_or_repair_count": len(repairs),
        "unresolved_final_stop_count": sum(row["gdt517_final_decision"] == "STOP" for row in replay),
        "dy_top_mapping_after_ambiguity_lock": old_dy,
        "guard": "DEFAULT_TOP1_ALWAYS_EMITTED_WHEN_TILEABLE__FINITE_ALTERNATIVES_PRESERVED",
    }
    write_json(OUT / "gdt517_result.json", result)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
