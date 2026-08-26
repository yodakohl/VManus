#!/usr/bin/env python3
"""Build a prospective one-core replacement deck from the nineteen meanings."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt430_nineteen_core_paradigm_prediction_deck"
OUT = BASE / "artifacts"
CLAUSES = ROOT / "experiments/yolo/gdt416_owner_local_imperative_sentence_compiler/artifacts/gdt416_4576_imperative_clauses.tsv"
DICTIONARY = ROOT / "experiments/yolo/gdt413_twenty_six_page_semantic_working_edition/artifacts/gdt413_46_component_working_dictionary.tsv"
ACTION_CONTRASTS = ROOT / "experiments/yolo/gdt428_within_class_action_semantic_contrasts/artifacts/gdt428_6_within_class_contrasts.tsv"
NONACTION_CONTRASTS = ROOT / "experiments/yolo/gdt429_nonaction_core_semantic_contrasts/artifacts/gdt429_13_nonaction_core_contrasts.tsv"

GROUPS = (
    ("ACTION_SELECT", ("CH", "S")),
    ("ACTION_MOVE_SET", ("K", "OK", "P")),
    ("ACTION_HOLD_PROCESS", ("SH", "CHD")),
    ("ARGUMENT", ("Y", "AIIN", "AIN", "OR")),
    ("RELATION", ("AL", "AR", "L", "AIR")),
    ("ORDER", ("OL", "OT")),
)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def generate_candidates(recipes: set[str]) -> dict[str, dict[str, object]]:
    candidates: dict[str, dict[str, object]] = defaultdict(
        lambda: {"sources": set(), "operations": set(), "families": set()}
    )
    for recipe in recipes:
        atoms = recipe.split("+")
        for index, atom in enumerate(atoms):
            for family, members in GROUPS:
                if atom not in members:
                    continue
                for replacement in members:
                    if replacement == atom:
                        continue
                    candidate = "+".join(atoms[:index] + [replacement] + atoms[index + 1:])
                    candidates[candidate]["sources"].add(recipe)
                    candidates[candidate]["operations"].add(f"{atom}>{replacement}@{index + 1}")
                    candidates[candidate]["families"].add(family)
    return candidates


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    clauses = read_tsv(CLAUSES)
    dictionary = read_tsv(DICTIONARY)
    action_contrasts = read_tsv(ACTION_CONTRASTS)
    nonaction_contrasts = read_tsv(NONACTION_CONTRASTS)
    meanings = {row["atom"]: row["working_value_de"] for row in dictionary}

    pair_support = {
        tuple(row["contrast_pair"].split("~")): int(row["shared_exact_substitution_frame_count"])
        for row in action_contrasts + nonaction_contrasts
    }
    pair_support.update({(right, left): count for (left, right), count in list(pair_support.items())})

    recipe_rows: dict[str, list[dict[str, str]]] = defaultdict(list)
    page_recipes: dict[str, set[str]] = defaultdict(set)
    for row in clauses:
        recipe = row["component_recipe"]
        recipe_rows[recipe].append(row)
        page_recipes[row["physical_page"]].add(recipe)
    observed_recipes = set(recipe_rows)
    candidates = generate_candidates(observed_recipes)

    all_candidate_rows: list[dict[str, object]] = []
    for candidate, data in sorted(candidates.items()):
        sources = sorted(data["sources"])
        source_rows = [row for recipe in sources for row in recipe_rows[recipe]]
        neighbor_count = len(sources)
        observed = candidate in observed_recipes
        target_rows = recipe_rows.get(candidate, [])
        all_candidate_rows.append({
            "candidate_recipe": candidate,
            "candidate_reading_de": " · ".join(meanings.get(atom, f"[{atom}]") for atom in candidate.split("+")),
            "current_status": "OBSERVED" if observed else "ABSENT",
            "source_neighbor_count": neighbor_count,
            "source_recipes": " | ".join(sources),
            "replacement_operations": " | ".join(sorted(data["operations"])),
            "replacement_families": "|".join(sorted(data["families"])),
            "source_page_count": len({row["physical_page"] for row in source_rows}),
            "source_pages": "|".join(sorted({row["physical_page"] for row in source_rows})),
            "source_register_count": len({row["register"] for row in source_rows}),
            "source_registers": "|".join(sorted({row["register"] for row in source_rows})),
            "target_event_count": len(target_rows),
            "target_page_count": len({row["physical_page"] for row in target_rows}),
            "surface_prediction": "NOT_NEEDED__ALREADY_OBSERVED" if observed else "UNASSIGNED__COMPOSITION_ONLY",
        })

    density_rows: list[dict[str, object]] = []
    max_neighbors = max(int(row["source_neighbor_count"]) for row in all_candidate_rows)
    for neighbor_count in range(1, max_neighbors + 1):
        band = [row for row in all_candidate_rows if int(row["source_neighbor_count"]) == neighbor_count]
        observed_count = sum(row["current_status"] == "OBSERVED" for row in band)
        absent_count = len(band) - observed_count
        density_rows.append({
            "source_neighbor_count": neighbor_count,
            "candidate_count": len(band),
            "observed_recipe_count": observed_count,
            "absent_recipe_count": absent_count,
            "current_occupancy_rate": f"{observed_count / len(band):.6f}",
            "future_use": "HIGH_PRIORITY" if neighbor_count >= 4 else "STRONG" if neighbor_count == 3 else "NARROW" if neighbor_count == 2 else "DO_NOT_PREDICT",
        })

    prediction_rows: list[dict[str, object]] = []
    for row in all_candidate_rows:
        neighbors = int(row["source_neighbor_count"])
        if row["current_status"] != "ABSENT" or neighbors < 2:
            continue
        status = "AMBER_HIGH_PRIORITY" if neighbors >= 4 else "AMBER_STRONG" if neighbors == 3 else "AMBER_NARROW"
        operations = str(row["replacement_operations"]).split(" | ")
        root_pair_support = []
        for operation in operations:
            pair = operation.split("@", 1)[0].split(">")
            root_pair_support.append(pair_support.get((pair[0], pair[1]), 0))
        prediction_rows.append({
            "prediction_rank": status,
            "candidate_recipe": row["candidate_recipe"],
            "fixed_reading_de": row["candidate_reading_de"],
            "source_neighbor_count": neighbors,
            "source_recipes": row["source_recipes"],
            "replacement_operations": row["replacement_operations"],
            "replacement_families": row["replacement_families"],
            "minimum_root_pair_shared_frame_support": min(root_pair_support),
            "source_page_count": row["source_page_count"],
            "source_pages": row["source_pages"],
            "source_register_count": row["source_register_count"],
            "surface_rule": "DO_NOT_INVENT_SURFACE__READ_ONLY_IF_VISIBLE_RECIPE_SEGMENTS_MATCH",
        })
    prediction_rows.sort(key=lambda row: (-int(row["source_neighbor_count"]), str(row["candidate_recipe"])))

    leaveout_rows: list[dict[str, object]] = []
    page_summary_rows: list[dict[str, object]] = []
    for page in sorted(page_recipes):
        training_recipes = set().union(*(recipes for other, recipes in page_recipes.items() if other != page))
        private_recipes = sorted(page_recipes[page] - training_recipes)
        training_candidates = generate_candidates(training_recipes)
        counts = Counter()
        for target in private_recipes:
            data = training_candidates.get(target, {"sources": set(), "operations": set(), "families": set()})
            sources = sorted(data["sources"])
            neighbors = len(sources)
            if neighbors >= 4:
                replay = "RECOVERED_HIGH_PRIORITY"
            elif neighbors == 3:
                replay = "RECOVERED_STRONG"
            elif neighbors == 2:
                replay = "RECOVERED_NARROW"
            elif neighbors == 1:
                replay = "ONE_NEIGHBOR_NOT_PREDICTED"
            else:
                replay = "NOT_RECOVERED_BY_ONE_CORE_REPLACEMENT"
            counts[replay] += 1
            source_rows = [row for recipe in sources for row in recipe_rows[recipe] if row["physical_page"] != page]
            leaveout_rows.append({
                "held_page": page,
                "private_target_recipe": target,
                "target_reading_de": " · ".join(meanings.get(atom, f"[{atom}]") for atom in target.split("+")),
                "source_neighbor_count": neighbors,
                "source_recipes": " | ".join(sources) if sources else "NONE",
                "replacement_operations": " | ".join(sorted(data["operations"])) if data["operations"] else "NONE",
                "source_pages": "|".join(sorted({row["physical_page"] for row in source_rows})) if source_rows else "NONE",
                "replay_status": replay,
            })
        page_summary_rows.append({
            "held_page": page,
            "private_recipe_count": len(private_recipes),
            "recovered_high_priority": counts["RECOVERED_HIGH_PRIORITY"],
            "recovered_strong": counts["RECOVERED_STRONG"],
            "recovered_narrow": counts["RECOVERED_NARROW"],
            "one_neighbor_not_predicted": counts["ONE_NEIGHBOR_NOT_PREDICTED"],
            "not_recovered": counts["NOT_RECOVERED_BY_ONE_CORE_REPLACEMENT"],
        })

    write_tsv(OUT / "gdt430_4938_candidate_density.tsv", all_candidate_rows, list(all_candidate_rows[0]))
    write_tsv(OUT / "gdt430_5_neighbor_support_bands.tsv", density_rows, list(density_rows[0]))
    write_tsv(OUT / "gdt430_293_absent_multi_neighbor_predictions.tsv", prediction_rows, list(prediction_rows[0]))
    write_tsv(OUT / "gdt430_861_page_private_recipe_replay.tsv", leaveout_rows, list(leaveout_rows[0]))
    write_tsv(OUT / "gdt430_24_page_leaveout_summary.tsv", page_summary_rows, list(page_summary_rows[0]))

    strongest = [row for row in prediction_rows if row["prediction_rank"] == "AMBER_HIGH_PRIORITY"]
    card = [
        "# Vier stärkste fehlende Kompositionen", "",
        "Jede dieser Kompositionen ist von vier verschiedenen vorhandenen Ein-Kern-Nachbarn aus erreichbar.", "",
    ]
    for row in strongest:
        card += [
            f"## `{row['candidate_recipe']}`", "",
            f"Lesung: **{row['fixed_reading_de']}**", "",
            f"Nachbarn: {row['source_recipes']}", "",
        ]
    card += [
        "Keine Oberfläche wird erfunden. Die Lesung gilt nur, wenn eine spätere sichtbare Karte exakt in diese Komponenten zerfällt.",
    ]
    (OUT / "FOUR_HIGHEST_PREDICTION_CARD.md").write_text("\n".join(card) + "\n", encoding="utf-8")

    leaveout_counts = Counter(row["replay_status"] for row in leaveout_rows)
    result = {
        "status": "FOUR_HIGH_AND_FORTY_THREE_STRONG_COMPONENT_PREDICTIONS_FIXED",
        "observed_recipe_type_count": len(observed_recipes),
        "generated_candidate_count": len(all_candidate_rows),
        "generated_observed_count": sum(row["current_status"] == "OBSERVED" for row in all_candidate_rows),
        "generated_absent_count": sum(row["current_status"] == "ABSENT" for row in all_candidate_rows),
        "absent_multi_neighbor_prediction_count": len(prediction_rows),
        "high_priority_prediction_count": sum(row["prediction_rank"] == "AMBER_HIGH_PRIORITY" for row in prediction_rows),
        "strong_prediction_count": sum(row["prediction_rank"] == "AMBER_STRONG" for row in prediction_rows),
        "narrow_prediction_count": sum(row["prediction_rank"] == "AMBER_NARROW" for row in prediction_rows),
        "page_count": len(page_summary_rows),
        "page_private_recipe_count": len(leaveout_rows),
        "page_private_any_neighbor_count": len(leaveout_rows) - leaveout_counts["NOT_RECOVERED_BY_ONE_CORE_REPLACEMENT"],
        "page_private_multi_neighbor_count": sum(leaveout_counts[key] for key in ("RECOVERED_HIGH_PRIORITY", "RECOVERED_STRONG", "RECOVERED_NARROW")),
        "page_private_strong_or_high_count": leaveout_counts["RECOVERED_HIGH_PRIORITY"] + leaveout_counts["RECOVERED_STRONG"],
        "surface_predictions": 0,
        "meaning_revisions": 0,
        "new_roots": 0,
        "new_pages": 0,
    }
    (OUT / "gdt430_result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
