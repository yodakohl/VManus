#!/usr/bin/env python3
"""Build ordered two-action pair licenses and gate GDT419 multi-head gaps."""

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
BASE = ROOT / "experiments/yolo/gdt421_ordered_action_pair_slot_license"
OUT = BASE / "artifacts"
CLAUSES = ROOT / "experiments/yolo/gdt416_owner_local_imperative_sentence_compiler/artifacts/gdt416_4576_imperative_clauses.tsv"
DICTIONARY = ROOT / "experiments/yolo/gdt413_twenty_six_page_semantic_working_edition/artifacts/gdt413_46_component_working_dictionary.tsv"
GATES = ROOT / "experiments/yolo/gdt420_action_head_slot_license_atlas/artifacts/gdt420_52_gdt419_prediction_gates.tsv"

REGISTERS = ("SOURCE_SECTION_T", "HERBAL", "BIOLOGICAL", "CELESTIAL", "PHARMA")
ACTIONS = ("OK", "CH", "SH", "K", "S", "CHD", "T", "R", "P")
GRADES = ("NONE", "E", "EE", "EEE")
ARGUMENTS = ("NONE", "Y", "AIIN", "AIN", "OR")
ENDPOINTS = ("OPEN", "CLOSE")


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    clauses = read_tsv(CLAUSES)
    meanings = {row["atom"]: row["working_value_de"] for row in read_tsv(DICTIONARY)}
    gates = read_tsv(GATES)

    by_recipe: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in clauses:
        by_recipe[row["component_recipe"]].append(row)

    pair_recipes: dict[tuple[str, str], list[tuple[str, list[dict[str, str]]]]] = defaultdict(list)
    clean_cells: dict[tuple[tuple[str, str], str, str, str], list[tuple[str, list[dict[str, str]]]]] = defaultdict(list)
    pair_grades: dict[tuple[str, str], set[str]] = defaultdict(set)
    pair_arguments: dict[tuple[str, str], set[str]] = defaultdict(set)
    pair_close: set[tuple[str, str]] = set()
    inventory_rows: list[dict[str, object]] = []

    for component_recipe, rows in sorted(by_recipe.items()):
        atoms = component_recipe.split("+")
        action_atoms = tuple(atom for atom in atoms if atom in ACTIONS)
        if len(action_atoms) != 2:
            continue
        pair = (action_atoms[0], action_atoms[1])
        grades = [atom for atom in atoms if atom in GRADES[1:]]
        arguments = [atom for atom in atoms if atom in ARGUMENTS[1:]]
        dy_count = atoms.count("DY")
        clean = len(grades) <= 1 and len(arguments) <= 1 and dy_count <= 1
        pair_recipes[pair].append((component_recipe, rows))
        pair_grades[pair].update(grades)
        pair_arguments[pair].update(arguments)
        if dy_count:
            pair_close.add(pair)
        skeleton = "NONCANONICAL_MULTISLOT"
        if clean:
            grade = grades[0] if grades else "NONE"
            argument = arguments[0] if arguments else "NONE"
            endpoint = "CLOSE" if dy_count else "OPEN"
            skeleton = f"{pair[0]}+{pair[1]}|{grade}|{argument}|{endpoint}"
            clean_cells[(pair, grade, argument, endpoint)].append((component_recipe, rows))
        registers = sorted({row["register"] for row in rows}, key=REGISTERS.index)
        inventory_rows.append({
            "component_recipe": component_recipe,
            "first_action": pair[0],
            "second_action": pair[1],
            "ordered_pair": "+".join(pair),
            "ordered_reading_de": f"{meanings[pair[0]]} → {meanings[pair[1]]}",
            "grade_atoms": "|".join(grades) if grades else "NONE",
            "argument_atoms": "|".join(arguments) if arguments else "NONE",
            "dy_count": dy_count,
            "clean_pair_slot_recipe": "YES" if clean else "NO",
            "canonical_pair_skeleton": skeleton,
            "event_count": len(rows),
            "register_count": len(registers),
            "registers": "|".join(registers),
            "page_count": len({row["physical_page"] for row in rows}),
            "surfaces": "|".join(sorted({row["surface"] for row in rows})),
            "portable_reading_de": next(iter({row["portable_back_projection_de"] for row in rows})),
        })

    pair_profile_rows: list[dict[str, object]] = []
    for first in ACTIONS:
        for second in ACTIONS:
            pair = (first, second)
            members = pair_recipes.get(pair, [])
            member_rows = [row for _, rows in members for row in rows]
            registers = sorted({row["register"] for row in member_rows}, key=REGISTERS.index)
            clean_members = [row for row in inventory_rows if row["ordered_pair"] == "+".join(pair) and row["clean_pair_slot_recipe"] == "YES"]
            pair_profile_rows.append({
                "first_action": first,
                "first_value_de": meanings[first],
                "second_action": second,
                "second_value_de": meanings[second],
                "ordered_pair": "+".join(pair),
                "ordered_reading_de": f"{meanings[first]} → {meanings[second]}",
                "status": "PAIR_ATTESTED" if members else "PAIR_ABSENT",
                "exact_recipe_type_count": len(members),
                "event_count": len(member_rows),
                "clean_recipe_type_count": len(clean_members),
                "register_count": len(registers),
                "registers": "|".join(registers) if registers else "NONE",
                "licensed_grades": "|".join(sorted(pair_grades[pair], key=GRADES.index)) if pair_grades[pair] else "NONE",
                "licensed_arguments": "|".join(sorted(pair_arguments[pair], key=ARGUMENTS.index)) if pair_arguments[pair] else "NONE",
                "endpoint_license": "CLOSE_SLOT_ATTESTED" if pair in pair_close else "NO_CLOSE_SLOT",
            })

    atlas_rows: list[dict[str, object]] = []
    for profile in pair_profile_rows:
        pair = (str(profile["first_action"]), str(profile["second_action"]))
        for grade in GRADES:
            for argument in ARGUMENTS:
                for endpoint in ENDPOINTS:
                    members = clean_cells.get((pair, grade, argument, endpoint), [])
                    member_rows = [row for _, rows in members for row in rows]
                    registers = sorted({row["register"] for row in member_rows}, key=REGISTERS.index)
                    blocked_reasons: list[str] = []
                    if profile["status"] == "PAIR_ABSENT":
                        blocked_reasons.append("ORDERED_PAIR_ABSENT")
                    else:
                        if grade != "NONE" and grade not in pair_grades[pair]:
                            blocked_reasons.append(f"PAIR_HAS_NO_{grade}_LICENSE")
                        if argument != "NONE" and argument not in pair_arguments[pair]:
                            blocked_reasons.append(f"PAIR_HAS_NO_{argument}_LICENSE")
                        if endpoint == "CLOSE" and pair not in pair_close:
                            blocked_reasons.append("PAIR_HAS_NO_CLOSE_LICENSE")
                    if members:
                        status = "ATTESTED_MULTI_REGISTER" if len(registers) >= 2 else "ATTESTED_LOCAL"
                    elif blocked_reasons:
                        status = "BLOCKED_BY_PAIR_INVENTORY"
                    else:
                        status = "OPEN_PAIR_COMBINATION_GAP"
                    reading_atoms = [pair[0], pair[1]]
                    if grade != "NONE":
                        reading_atoms.append(grade)
                    if argument != "NONE":
                        reading_atoms.append(argument)
                    if endpoint == "CLOSE":
                        reading_atoms.append("DY")
                    atlas_rows.append({
                        "ordered_pair": "+".join(pair),
                        "ordered_reading_de": f"{meanings[pair[0]]} → {meanings[pair[1]]}",
                        "grade_slot": grade,
                        "argument_slot": argument,
                        "endpoint_slot": endpoint,
                        "predicted_skeleton_reading_de": " · ".join(meanings[atom] for atom in reading_atoms),
                        "status": status,
                        "blocked_reasons": "|".join(blocked_reasons) if blocked_reasons else "NONE",
                        "exact_recipe_type_count": len(members),
                        "event_count": len(member_rows),
                        "register_count": len(registers),
                        "registers": "|".join(registers) if registers else "NONE",
                        "exact_recipes": "|".join(recipe for recipe, _ in members) if members else "NONE",
                    })

    direction_rows: list[dict[str, object]] = []
    profile_index = {str(row["ordered_pair"]): row for row in pair_profile_rows}
    for left_index, left in enumerate(ACTIONS):
        for right in ACTIONS[left_index:]:
            forward = profile_index[f"{left}+{right}"]
            reverse = profile_index[f"{right}+{left}"] if left != right else None
            forward_events = int(forward["event_count"])
            reverse_events = int(reverse["event_count"]) if reverse else 0
            if left == right:
                verdict = "SELF_ATTESTED" if forward_events else "SELF_ABSENT"
            elif forward_events and not reverse_events:
                verdict = "FORWARD_ONLY"
            elif reverse_events and not forward_events:
                verdict = "REVERSE_ONLY"
            elif not forward_events and not reverse_events:
                verdict = "BOTH_ABSENT"
            elif max(forward_events, reverse_events) >= 2 * min(forward_events, reverse_events):
                verdict = "DIRECTIONAL"
            else:
                verdict = "BALANCED"
            direction_rows.append({
                "unordered_pair": f"{left}|{right}",
                "forward_pair": f"{left}+{right}",
                "forward_reading_de": f"{meanings[left]} → {meanings[right]}",
                "forward_event_count": forward_events,
                "forward_recipe_type_count": forward["exact_recipe_type_count"],
                "reverse_pair": f"{right}+{left}" if reverse else "SELF",
                "reverse_reading_de": f"{meanings[right]} → {meanings[left]}" if reverse else "SELF",
                "reverse_event_count": reverse_events,
                "reverse_recipe_type_count": reverse["exact_recipe_type_count"] if reverse else 0,
                "direction_verdict": verdict,
            })

    atlas_index = {
        (str(row["ordered_pair"]), str(row["grade_slot"]), str(row["argument_slot"]), str(row["endpoint_slot"])): row
        for row in atlas_rows
    }
    prediction_rows: list[dict[str, object]] = []
    for row in gates:
        if row["gate_decision"] != "MULTI_HEAD_REQUIRES_SEPARATE_LICENSE":
            continue
        atoms = row["candidate_recipe"].split("+")
        actions = [atom for atom in atoms if atom in ACTIONS]
        grades = [atom for atom in atoms if atom in GRADES[1:]]
        arguments = [atom for atom in atoms if atom in ARGUMENTS[1:]]
        endpoint = "CLOSE" if "DY" in atoms else "OPEN"
        key = ("+".join(actions), grades[0] if grades else "NONE", arguments[0] if arguments else "NONE", endpoint)
        cell = atlas_index[key]
        decision = {
            "ATTESTED_MULTI_REGISTER": "SKELETON_ALREADY_ATTESTED_MULTI_REGISTER",
            "ATTESTED_LOCAL": "SKELETON_ALREADY_ATTESTED_LOCAL",
            "OPEN_PAIR_COMBINATION_GAP": "OPEN_PAIR_CONDITIONAL_READING",
            "BLOCKED_BY_PAIR_INVENTORY": "BLOCKED__DO_NOT_PREDICT_AS_REGULAR_PAIR",
        }[str(cell["status"])]
        prediction_rows.append({
            "candidate_recipe": row["candidate_recipe"],
            "predicted_reading_de": row["predicted_reading_de"],
            "ordered_pair": key[0],
            "pair_slot_skeleton": "|".join(key),
            "gate_decision": decision,
            "blocked_reasons": cell["blocked_reasons"],
            "supporting_exact_recipes": cell["exact_recipes"],
            "supporting_register_count": cell["register_count"],
        })

    write_tsv(OUT / "gdt421_356_two_head_recipe_inventory.tsv", inventory_rows, list(inventory_rows[0]))
    write_tsv(OUT / "gdt421_81_ordered_pair_profiles.tsv", pair_profile_rows, list(pair_profile_rows[0]))
    write_tsv(OUT / "gdt421_3240_pair_slot_atlas.tsv", atlas_rows, list(atlas_rows[0]))
    write_tsv(OUT / "gdt421_45_pair_directionality.tsv", direction_rows, list(direction_rows[0]))
    write_tsv(OUT / "gdt421_31_multi_head_prediction_gates.tsv", prediction_rows, list(prediction_rows[0]))

    top_pairs = sorted(
        [row for row in pair_profile_rows if row["status"] == "PAIR_ATTESTED"],
        key=lambda row: (-int(row["register_count"]), -int(row["event_count"]), str(row["ordered_pair"])),
    )
    cards = ["# Geordnete Handlungspaare", ""]
    for row in top_pairs[:20]:
        cards += [
            f"## `{row['ordered_pair']}` — {row['ordered_reading_de']}", "",
            f"- {row['event_count']} Ereignisse / {row['exact_recipe_type_count']} Rezepte / {row['register_count']} Register",
            f"- Grade: {row['licensed_grades']}; Argumente: {row['licensed_arguments']}; Ende: {row['endpoint_license']}", "",
        ]
    (OUT / "TWENTY_ORDERED_ACTION_PAIR_CARDS.md").write_text("\n".join(cards), encoding="utf-8")

    direction_counts = Counter(row["direction_verdict"] for row in direction_rows)
    gate_counts = Counter(row["gate_decision"] for row in prediction_rows)
    result = {
        "status": "ORDERED_ACTION_PAIR_SLOT_LICENSE_COMPLETE",
        "two_head_recipe_type_count": len(inventory_rows),
        "two_head_event_count": sum(int(row["event_count"]) for row in inventory_rows),
        "ordered_pair_profile_count": len(pair_profile_rows),
        "attested_ordered_pair_count": sum(row["status"] == "PAIR_ATTESTED" for row in pair_profile_rows),
        "clean_pair_recipe_type_count": sum(row["clean_pair_slot_recipe"] == "YES" for row in inventory_rows),
        "clean_pair_event_count": sum(int(row["event_count"]) for row in inventory_rows if row["clean_pair_slot_recipe"] == "YES"),
        "pair_slot_atlas_cell_count": len(atlas_rows),
        "attested_pair_slot_cell_count": sum(str(row["status"]).startswith("ATTESTED") for row in atlas_rows),
        "multi_register_pair_slot_cell_count": sum(row["status"] == "ATTESTED_MULTI_REGISTER" for row in atlas_rows),
        "directionality_counts": dict(sorted(direction_counts.items())),
        "multi_head_prediction_gate_counts": dict(sorted(gate_counts.items())),
        "new_pages": 0,
        "dictionary_revisions": 0,
    }
    (OUT / "gdt421_result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
