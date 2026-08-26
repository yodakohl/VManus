#!/usr/bin/env python3
"""Build a complete action-head x grade x argument x endpoint slot atlas."""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt420_action_head_slot_license_atlas"
OUT = BASE / "artifacts"
CLAUSES = ROOT / "experiments/yolo/gdt416_owner_local_imperative_sentence_compiler/artifacts/gdt416_4576_imperative_clauses.tsv"
DICTIONARY = ROOT / "experiments/yolo/gdt413_twenty_six_page_semantic_working_edition/artifacts/gdt413_46_component_working_dictionary.tsv"
PREDICTIONS = ROOT / "experiments/yolo/gdt419_one_atom_compositional_paradigm_closure/artifacts/gdt419_52_unique_missing_predictions.tsv"

REGISTERS = ("SOURCE_SECTION_T", "HERBAL", "BIOLOGICAL", "CELESTIAL", "PHARMA")
ACTIONS = ("OK", "CH", "SH", "K", "S", "CHD", "T", "R", "P")
GRADES = ("NONE", "E", "EE", "EEE")
ARGUMENTS = ("NONE", "Y", "AIIN", "AIN", "OR")
ENDPOINTS = ("OPEN", "CLOSE")
RELATIONS = {"OL", "OT", "AL", "AR", "L", "AIR"}


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
    dictionary = read_tsv(DICTIONARY)
    predictions = read_tsv(PREDICTIONS)
    meanings = {row["atom"]: row["working_value_de"] for row in dictionary}

    by_recipe: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in clauses:
        by_recipe[row["component_recipe"]].append(row)

    single_rows: list[dict[str, object]] = []
    clean_cells: dict[tuple[str, str, str, str], list[tuple[str, list[dict[str, str]]]]] = defaultdict(list)
    license_grade: dict[str, set[str]] = defaultdict(set)
    license_argument: dict[str, set[str]] = defaultdict(set)
    license_close: set[str] = set()

    for component_recipe, rows in sorted(by_recipe.items()):
        atoms = component_recipe.split("+")
        action_atoms = [atom for atom in atoms if atom in ACTIONS]
        if len(action_atoms) != 1:
            continue
        action = action_atoms[0]
        grade_atoms = [atom for atom in atoms if atom in GRADES[1:]]
        argument_atoms = [atom for atom in atoms if atom in ARGUMENTS[1:]]
        dy_count = atoms.count("DY")
        relation_atoms = [atom for atom in atoms if atom in RELATIONS]
        registers = sorted({row["register"] for row in rows}, key=REGISTERS.index)
        clean = len(grade_atoms) <= 1 and len(argument_atoms) <= 1 and dy_count <= 1

        license_grade[action].update(grade_atoms)
        license_argument[action].update(argument_atoms)
        if dy_count:
            license_close.add(action)

        skeleton = "NONCANONICAL_MULTISLOT"
        if clean:
            grade = grade_atoms[0] if grade_atoms else "NONE"
            argument = argument_atoms[0] if argument_atoms else "NONE"
            endpoint = "CLOSE" if dy_count else "OPEN"
            skeleton = f"{action}|{grade}|{argument}|{endpoint}"
            clean_cells[(action, grade, argument, endpoint)].append((component_recipe, rows))

        single_rows.append({
            "component_recipe": component_recipe,
            "action_head": action,
            "action_value_de": meanings[action],
            "grade_atoms": "|".join(grade_atoms) if grade_atoms else "NONE",
            "argument_atoms": "|".join(argument_atoms) if argument_atoms else "NONE",
            "dy_count": dy_count,
            "relation_atoms": "|".join(relation_atoms) if relation_atoms else "NONE",
            "canonical_slot_skeleton": skeleton,
            "clean_single_slot_recipe": "YES" if clean else "NO",
            "event_count": len(rows),
            "register_count": len(registers),
            "registers": "|".join(registers),
            "page_count": len({row["physical_page"] for row in rows}),
            "surfaces": "|".join(sorted({row["surface"] for row in rows})),
            "portable_reading_de": next(iter({row["portable_back_projection_de"] for row in rows})),
        })

    atlas_rows: list[dict[str, object]] = []
    for action in ACTIONS:
        for grade in GRADES:
            for argument in ARGUMENTS:
                for endpoint in ENDPOINTS:
                    cell = (action, grade, argument, endpoint)
                    members = clean_cells.get(cell, [])
                    member_rows = [row for _, rows in members for row in rows]
                    registers = sorted({row["register"] for row in member_rows}, key=REGISTERS.index)
                    blocked_reasons: list[str] = []
                    if grade != "NONE" and grade not in license_grade[action]:
                        blocked_reasons.append(f"{action}_HAS_NO_{grade}_LICENSE")
                    if argument != "NONE" and argument not in license_argument[action]:
                        blocked_reasons.append(f"{action}_HAS_NO_{argument}_LICENSE")
                    if endpoint == "CLOSE" and action not in license_close:
                        blocked_reasons.append(f"{action}_HAS_NO_CLOSE_LICENSE")
                    if members:
                        status = "ATTESTED_MULTI_REGISTER" if len(registers) >= 2 else "ATTESTED_LOCAL"
                    elif blocked_reasons:
                        status = "BLOCKED_BY_HEAD_INVENTORY"
                    else:
                        status = "OPEN_COMBINATION_GAP"
                    reading_atoms = [action]
                    if grade != "NONE":
                        reading_atoms.append(grade)
                    if argument != "NONE":
                        reading_atoms.append(argument)
                    if endpoint == "CLOSE":
                        reading_atoms.append("DY")
                    atlas_rows.append({
                        "action_head": action,
                        "action_value_de": meanings[action],
                        "grade_slot": grade,
                        "grade_value_de": meanings.get(grade, "NONE"),
                        "argument_slot": argument,
                        "argument_value_de": meanings.get(argument, "NONE"),
                        "endpoint_slot": endpoint,
                        "predicted_skeleton_reading_de": " · ".join(meanings[atom] for atom in reading_atoms),
                        "status": status,
                        "blocked_reasons": "|".join(blocked_reasons) if blocked_reasons else "NONE",
                        "exact_recipe_type_count": len(members),
                        "event_count": len(member_rows),
                        "register_count": len(registers),
                        "registers": "|".join(registers) if registers else "NONE",
                        "page_count": len({row["physical_page"] for row in member_rows}),
                        "exact_recipes": "|".join(recipe for recipe, _ in members) if members else "NONE",
                        "surfaces": "|".join(sorted({row["surface"] for row in member_rows})) if member_rows else "NONE",
                    })

    profile_rows: list[dict[str, object]] = []
    for action in ACTIONS:
        recipes = [row for row in single_rows if row["action_head"] == action]
        clean = [row for row in recipes if row["clean_single_slot_recipe"] == "YES"]
        cells = [row for row in atlas_rows if row["action_head"] == action]
        grades = sorted(license_grade[action], key=GRADES.index)
        arguments = sorted(license_argument[action], key=ARGUMENTS.index)
        grade_status = "NO_GRADE_SLOT" if not grades else "NARROW_GRADE_SLOT" if sum(int(row["event_count"]) for row in recipes if row["grade_atoms"] != "NONE") < 10 else "PRODUCTIVE_GRADE_SLOT"
        endpoint_status = "NO_CLOSE_SLOT" if action not in license_close else "CLOSE_SLOT_ATTESTED"
        profile_rows.append({
            "action_head": action,
            "action_value_de": meanings[action],
            "single_head_recipe_type_count": len(recipes),
            "single_head_event_count": sum(int(row["event_count"]) for row in recipes),
            "clean_recipe_type_count": len(clean),
            "attested_skeleton_cell_count": sum(str(row["status"]).startswith("ATTESTED") for row in cells),
            "multi_register_skeleton_cell_count": sum(row["status"] == "ATTESTED_MULTI_REGISTER" for row in cells),
            "open_gap_count": sum(row["status"] == "OPEN_COMBINATION_GAP" for row in cells),
            "blocked_cell_count": sum(row["status"] == "BLOCKED_BY_HEAD_INVENTORY" for row in cells),
            "licensed_grades": "|".join(grades) if grades else "NONE",
            "grade_license": grade_status,
            "licensed_arguments": "|".join(arguments) if arguments else "NONE",
            "endpoint_license": endpoint_status,
            "relation_recipe_type_count": sum(row["relation_atoms"] != "NONE" for row in recipes),
            "workshop_head_card_de": f"{action}={meanings[action]}; GRAD={grade_status}; ARG={('|'.join(arguments) if arguments else 'NONE')}; ENDE={endpoint_status}",
        })

    atlas_index = {
        (str(row["action_head"]), str(row["grade_slot"]), str(row["argument_slot"]), str(row["endpoint_slot"])): row
        for row in atlas_rows
    }
    prediction_gate_rows: list[dict[str, object]] = []
    for row in predictions:
        atoms = row["candidate_recipe"].split("+")
        actions = [atom for atom in atoms if atom in ACTIONS]
        grades = [atom for atom in atoms if atom in GRADES[1:]]
        arguments = [atom for atom in atoms if atom in ARGUMENTS[1:]]
        dy_count = atoms.count("DY")
        if len(actions) != 1:
            gate = "MULTI_HEAD_REQUIRES_SEPARATE_LICENSE"
            skeleton = "NONE"
            blocked = "NONE"
        elif len(grades) > 1 or len(arguments) > 1 or dy_count > 1:
            gate = "MULTISLOT_REQUIRES_SEPARATE_LICENSE"
            skeleton = "NONE"
            blocked = "NONE"
        else:
            key = (
                actions[0],
                grades[0] if grades else "NONE",
                arguments[0] if arguments else "NONE",
                "CLOSE" if dy_count else "OPEN",
            )
            cell = atlas_index[key]
            skeleton = "|".join(key)
            blocked = str(cell["blocked_reasons"])
            gate = {
                "ATTESTED_MULTI_REGISTER": "SKELETON_ALREADY_ATTESTED_MULTI_REGISTER",
                "ATTESTED_LOCAL": "SKELETON_ALREADY_ATTESTED_LOCAL",
                "OPEN_COMBINATION_GAP": "OPEN_GAP_CONDITIONAL_READING",
                "BLOCKED_BY_HEAD_INVENTORY": "BLOCKED__DO_NOT_PREDICT_AS_REGULAR_FORM",
            }[str(cell["status"])]
        prediction_gate_rows.append({
            "candidate_recipe": row["candidate_recipe"],
            "predicted_reading_de": row["predicted_reading_de"],
            "source_anchors": row["source_anchors"],
            "slot_skeleton": skeleton,
            "gate_decision": gate,
            "blocked_reasons": blocked,
        })

    write_tsv(OUT / "gdt420_547_single_head_recipe_inventory.tsv", single_rows, list(single_rows[0]))
    write_tsv(OUT / "gdt420_360_action_slot_atlas.tsv", atlas_rows, list(atlas_rows[0]))
    write_tsv(OUT / "gdt420_9_action_head_profiles.tsv", profile_rows, list(profile_rows[0]))
    write_tsv(OUT / "gdt420_52_gdt419_prediction_gates.tsv", prediction_gate_rows, list(prediction_gate_rows[0]))

    cards = [
        "# Neun Handlungskopf-Karten", "",
        "Diese Karten entscheiden zuerst, ob eine Grad-, Argument- oder",
        "Schlussschublade bei einem Handlungskopf überhaupt offen ist.", "",
    ]
    for row in profile_rows:
        cards += [
            f"## `{row['action_head']}` = {row['action_value_de']}", "",
            f"- Grad: **{row['grade_license']}** ({row['licensed_grades']})",
            f"- Argumente: **{row['licensed_arguments']}**",
            f"- Schluss: **{row['endpoint_license']}**",
            f"- Belegte reine Schubladen: {row['attested_skeleton_cell_count']}; davon registerübergreifend {row['multi_register_skeleton_cell_count']}.", "",
        ]
    (OUT / "NINE_ACTION_HEAD_CARDS.md").write_text("\n".join(cards), encoding="utf-8")

    result = {
        "status": "ACTION_HEAD_SLOT_LICENSE_ATLAS_COMPLETE",
        "action_head_count": len(ACTIONS),
        "single_head_recipe_type_count": len(single_rows),
        "single_head_event_count": sum(int(row["event_count"]) for row in single_rows),
        "clean_single_slot_recipe_type_count": sum(row["clean_single_slot_recipe"] == "YES" for row in single_rows),
        "clean_single_slot_event_count": sum(int(row["event_count"]) for row in single_rows if row["clean_single_slot_recipe"] == "YES"),
        "slot_atlas_cell_count": len(atlas_rows),
        "attested_slot_cell_count": sum(str(row["status"]).startswith("ATTESTED") for row in atlas_rows),
        "multi_register_slot_cell_count": sum(row["status"] == "ATTESTED_MULTI_REGISTER" for row in atlas_rows),
        "local_slot_cell_count": sum(row["status"] == "ATTESTED_LOCAL" for row in atlas_rows),
        "open_combination_gap_count": sum(row["status"] == "OPEN_COMBINATION_GAP" for row in atlas_rows),
        "blocked_by_head_inventory_count": sum(row["status"] == "BLOCKED_BY_HEAD_INVENTORY" for row in atlas_rows),
        "gdt419_prediction_gate_count": len(prediction_gate_rows),
        "gdt419_blocked_regular_prediction_count": sum(row["gate_decision"] == "BLOCKED__DO_NOT_PREDICT_AS_REGULAR_FORM" for row in prediction_gate_rows),
        "gdt419_open_conditional_prediction_count": sum(row["gate_decision"] == "OPEN_GAP_CONDITIONAL_READING" for row in prediction_gate_rows),
        "gdt419_structural_skeleton_already_attested_count": sum(str(row["gate_decision"]).startswith("SKELETON_ALREADY_ATTESTED") for row in prediction_gate_rows),
        "gdt419_multi_head_unresolved_count": sum(row["gate_decision"] == "MULTI_HEAD_REQUIRES_SEPARATE_LICENSE" for row in prediction_gate_rows),
        "no_grade_heads": sorted(action for action in ACTIONS if not license_grade[action]),
        "no_close_heads": sorted(action for action in ACTIONS if action not in license_close),
        "new_pages": 0,
        "dictionary_revisions": 0,
    }
    (OUT / "gdt420_result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
