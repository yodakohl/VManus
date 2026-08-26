#!/usr/bin/env python3
"""Find bounded second-ring targets supported by two strong prediction arms."""

from __future__ import annotations

import csv
import importlib.util
import itertools
import json
from collections import Counter, defaultdict
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt433_two_arm_second_ring_prediction_squares"
OUT = BASE / "artifacts"
CLAUSES = ROOT / "experiments/yolo/gdt416_owner_local_imperative_sentence_compiler/artifacts/gdt416_4576_imperative_clauses.tsv"
PREDICTIONS = ROOT / "experiments/yolo/gdt430_nineteen_core_paradigm_prediction_deck/artifacts/gdt430_293_absent_multi_neighbor_predictions.tsv"
STRONG_CARDS = ROOT / "experiments/yolo/gdt431_strong_prediction_reading_phrasebook/artifacts/gdt431_47_strong_prediction_phrasebook.tsv"
STRONG_EXPANSIONS = ROOT / "experiments/yolo/gdt431_strong_prediction_reading_phrasebook/artifacts/gdt431_235_register_expansion_cards.tsv"
RENDERER = ROOT / "experiments/yolo/gdt431_strong_prediction_reading_phrasebook/src/run.py"
COMPONENTS = ROOT / "experiments/yolo/gdt413_twenty_six_page_semantic_working_edition/artifacts/gdt413_46_component_working_dictionary.tsv"
ATLAS = ROOT / "experiments/yolo/gdt415_owner_local_semantic_expansion_atlas/artifacts/gdt415_95_register_expansion_atlas.tsv"

REGISTERS = ("SOURCE_SECTION_T", "HERBAL", "BIOLOGICAL", "CELESTIAL", "PHARMA")
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


def load_renderer():
    spec = importlib.util.spec_from_file_location("gdt431_renderer", RENDERER)
    if spec is None or spec.loader is None:
        raise RuntimeError("Cannot load GDT431 renderer")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def one_change(source: str, target: str) -> str:
    left = source.split("+")
    right = target.split("+")
    differences = [(index + 1, old, new) for index, (old, new) in enumerate(zip(left, right)) if old != new]
    if len(left) != len(right) or len(differences) != 1:
        raise ValueError(f"Not a one-root change: {source} -> {target}")
    index, old, new = differences[0]
    return f"{old}>{new}@{index}"


def literal(recipe: str, meanings: dict[str, str]) -> str:
    return " · ".join(meanings[atom] for atom in recipe.split("+"))


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    clauses = read_tsv(CLAUSES)
    predictions = read_tsv(PREDICTIONS)
    strong_cards = read_tsv(STRONG_CARDS)
    strong_expansions = read_tsv(STRONG_EXPANSIONS)
    components = read_tsv(COMPONENTS)
    atlas = read_tsv(ATLAS)
    renderer = load_renderer()

    meanings = {row["atom"]: row["working_value_de"] for row in components}
    atlas_map = {(row["root"], row["register"]): row["owner_local_expansion_de"] for row in atlas}
    predicted_status = {row["candidate_recipe"]: row["prediction_rank"] for row in predictions}
    strong_map = {row["candidate_recipe"]: row for row in strong_cards}
    strong_set = set(strong_map)
    current_phrases = {row["short_workshop_phrase_de"] for row in strong_cards}
    current_register_phrases = {(row["register"], row["owner_local_workshop_phrase_de"]) for row in strong_expansions}
    group_map = {atom: (family, members) for family, members in GROUPS for atom in members}

    observed_rows: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in clauses:
        observed_rows[row["component_recipe"]].append(row)
    observed = set(observed_rows)

    squares: dict[tuple[str, str, tuple[str, str]], dict[str, object]] = {}
    for base_recipe in sorted(observed):
        atoms = base_recipe.split("+")
        arms: list[tuple[int, str, str, str, str]] = []
        for index, atom in enumerate(atoms):
            if atom not in group_map:
                continue
            family, members = group_map[atom]
            for replacement in members:
                if replacement == atom:
                    continue
                candidate_atoms = atoms.copy()
                candidate_atoms[index] = replacement
                intermediate = "+".join(candidate_atoms)
                if intermediate in strong_set:
                    arms.append((index, atom, replacement, intermediate, family))
        for left, right in itertools.combinations(arms, 2):
            if left[0] == right[0]:
                continue
            target_atoms = atoms.copy()
            target_atoms[left[0]] = left[2]
            target_atoms[right[0]] = right[2]
            target_recipe = "+".join(target_atoms)
            arm_pair = tuple(sorted((left[3], right[3])))
            key = (target_recipe, base_recipe, arm_pair)
            base_rows = observed_rows[base_recipe]
            squares[key] = {
                "target_recipe": target_recipe,
                "target_literal_de": literal(target_recipe, meanings),
                "target_workshop_phrase_de": renderer.render_recipe(target_atoms),
                "target_current_status": "OBSERVED" if target_recipe in observed else predicted_status.get(target_recipe, "OUTSIDE_GDT430_293"),
                "observed_base_recipe": base_recipe,
                "observed_base_literal_de": literal(base_recipe, meanings),
                "base_event_count": len(base_rows),
                "base_page_count": len({row["physical_page"] for row in base_rows}),
                "base_register_count": len({row["register"] for row in base_rows}),
                "base_pages": "|".join(sorted({row["physical_page"] for row in base_rows})),
                "strong_arm_a": arm_pair[0],
                "strong_arm_a_rank": strong_map[arm_pair[0]]["prediction_rank"],
                "strong_arm_b": arm_pair[1],
                "strong_arm_b_rank": strong_map[arm_pair[1]]["prediction_rank"],
                "base_to_arm_a": one_change(base_recipe, arm_pair[0]),
                "base_to_arm_b": one_change(base_recipe, arm_pair[1]),
                "arm_a_to_target": one_change(arm_pair[0], target_recipe),
                "arm_b_to_target": one_change(arm_pair[1], target_recipe),
                "changed_positions": "|".join(str(index + 1) for index in sorted((left[0], right[0]))),
                "square_status": "TWO_STRONG_ARMS_FROM_OBSERVED_BASE",
            }

    square_rows = []
    for index, row in enumerate(sorted(squares.values(), key=lambda item: (str(item["target_recipe"]), str(item["observed_base_recipe"]), str(item["strong_arm_a"]), str(item["strong_arm_b"]))), 1):
        square_rows.append({"square_id": f"SQ{index:03d}", **row})

    by_target: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in square_rows:
        by_target[str(row["target_recipe"])].append(row)
    target_rows: list[dict[str, object]] = []
    selected_targets: list[str] = []
    for recipe, rows in sorted(by_target.items()):
        bases = {str(row["observed_base_recipe"]) for row in rows}
        arms = {str(value) for row in rows for value in (row["strong_arm_a"], row["strong_arm_b"])}
        current_status = str(rows[0]["target_current_status"])
        if current_status == "OBSERVED":
            decision = "CALIBRATION_ALREADY_OBSERVED"
        elif current_status in {"AMBER_HIGH_PRIORITY", "AMBER_STRONG"}:
            decision = "CALIBRATION_ALREADY_STRONG"
        elif current_status == "AMBER_NARROW" and len(bases) >= 2 and len(arms) >= 3:
            decision = "SECOND_RING_REINFORCES_EXISTING_NARROW"
        elif current_status == "OUTSIDE_GDT430_293" and len(bases) >= 4 and len(arms) >= 4:
            decision = "SECOND_RING_AMBER_NEW"
            selected_targets.append(recipe)
        else:
            decision = "SINGLE_SQUARE_NOT_PROMOTED"
        target_rows.append({
            "target_recipe": recipe,
            "target_literal_de": rows[0]["target_literal_de"],
            "target_workshop_phrase_de": rows[0]["target_workshop_phrase_de"],
            "target_current_status": current_status,
            "square_count": len(rows),
            "distinct_observed_base_count": len(bases),
            "distinct_strong_arm_count": len(arms),
            "observed_bases": " | ".join(sorted(bases)),
            "strong_arms": " | ".join(sorted(arms)),
            "generic_phrase_collides_with_gdt431": "YES" if rows[0]["target_workshop_phrase_de"] in current_phrases else "NO",
            "decision": decision,
            "surface_rule": "DO_NOT_INVENT_SURFACE__SECOND_RING_COMPONENT_READING_ONLY",
        })

    register_rows: list[dict[str, object]] = []
    for recipe in sorted(selected_targets):
        atoms = recipe.split("+")
        for register in REGISTERS:
            phrase = renderer.render_recipe(atoms, register)
            register_rows.append({
                "target_recipe": recipe,
                "register": register,
                "portable_literal_de": literal(recipe, meanings),
                "owner_local_atom_expansion_de": " · ".join(atlas_map.get((atom, register), meanings[atom]) for atom in atoms),
                "owner_local_workshop_phrase_de": phrase,
                "collides_with_gdt431_in_register": "YES" if (register, phrase) in current_register_phrases else "NO",
                "decision": "SECOND_RING_AMBER_READING",
                "surface_rule": "DO_NOT_INVENT_SURFACE__SECOND_RING_COMPONENT_READING_ONLY",
            })

    write_tsv(OUT / "gdt433_21_two_arm_squares.tsv", square_rows, list(square_rows[0]))
    write_tsv(OUT / "gdt433_14_second_ring_targets.tsv", target_rows, list(target_rows[0]))
    write_tsv(OUT / "gdt433_10_new_second_ring_register_cards.tsv", register_rows, list(register_rows[0]))

    cards_md = [
        "# Zwei begrenzte Karten der zweiten Reihe", "",
        "Diese Karten werden nicht den 47 GDT431-Karten gleichgestellt. Jede ist eine zweite, schwächere Amber-Vorhersage aus vier beobachteten Basen und vier starken Zwischenkarten.", "",
    ]
    target_map = {row["target_recipe"]: row for row in target_rows}
    for recipe in sorted(selected_targets):
        row = target_map[recipe]
        cards_md += [
            f"## `{recipe}`", "",
            f"- Wörtlich: `{row['target_literal_de']}`",
            f"- Werkstatt: **{row['target_workshop_phrase_de']}**",
            f"- Beobachtete Basen: `{row['observed_bases']}`",
            f"- Starke Zwischenkarten: `{row['strong_arms']}`",
            "",
        ]
    cards_md += ["Keine Voynich-Oberfläche wird vorhergesagt. Ein Treffer zählt nur bei später sichtbar identischer Komponentenfolge.", ""]
    (OUT / "TWO_SECOND_RING_AMBER_CARDS.md").write_text("\n".join(cards_md), encoding="utf-8")

    decision_counts = Counter(str(row["decision"]) for row in target_rows)
    result = {
        "status": "TWO_NEW_SECOND_RING_AMBER_CARDS_FROM_FOUR_BY_FOUR_SQUARES",
        "observed_recipe_count": len(observed),
        "strong_first_ring_card_count": len(strong_set),
        "two_arm_square_count": len(square_rows),
        "second_ring_target_count": len(target_rows),
        "decision_counts": dict(sorted(decision_counts.items())),
        "selected_new_second_ring_card_count": len(selected_targets),
        "selected_new_second_ring_cards": sorted(selected_targets),
        "register_reading_count": len(register_rows),
        "surface_predictions": 0,
        "new_component_values": 0,
        "new_pages": 0,
    }
    (OUT / "gdt433_result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
