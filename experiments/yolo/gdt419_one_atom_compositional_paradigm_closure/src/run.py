#!/usr/bin/env python3
"""Build one-atom paradigm families around seven portable anchor recipes."""

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
BASE = ROOT / "experiments/yolo/gdt419_one_atom_compositional_paradigm_closure"
OUT = BASE / "artifacts"
CLAUSES = ROOT / "experiments/yolo/gdt416_owner_local_imperative_sentence_compiler/artifacts/gdt416_4576_imperative_clauses.tsv"
DICTIONARY = ROOT / "experiments/yolo/gdt413_twenty_six_page_semantic_working_edition/artifacts/gdt413_46_component_working_dictionary.tsv"

REGISTERS = ("SOURCE_SECTION_T", "HERBAL", "BIOLOGICAL", "CELESTIAL", "PHARMA")
ANCHORS = (
    "CHD+Y",
    "OK+EE+Y",
    "OK+AIIN",
    "SH+E+Y",
    "CH+K+E+Y",
    "K+EE+Y",
    "CH+T+E+Y",
)
ACTIONS = ("OK", "CH", "SH", "K", "S", "CHD", "T", "R", "P")
ARGUMENTS = ("Y", "AIIN", "AIN", "OR")
GRADES = ("E", "EE", "EEE")
RELATIONS = ("OL", "OT", "AL", "AR", "L", "AIR")
POOLS = {
    "ACTION": ACTIONS,
    "ARGUMENT": ARGUMENTS,
    "GRADE": GRADES,
    "RELATION": RELATIONS,
}
ATOM_CLASS = {atom: role for role, atoms in POOLS.items() for atom in atoms}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def tokens(component_recipe: str) -> tuple[str, ...]:
    return tuple(component_recipe.split("+"))


def render_recipe(sequence: tuple[str, ...]) -> str:
    return "+".join(sequence)


def edit_distance(left_sequence: tuple[str, ...], right_sequence: tuple[str, ...]) -> int:
    previous = list(range(len(right_sequence) + 1))
    for row_index, left in enumerate(left_sequence, 1):
        current = [row_index] + [0] * len(right_sequence)
        for column_index, right in enumerate(right_sequence, 1):
            current[column_index] = min(
                current[column_index - 1] + 1,
                previous[column_index] + 1,
                previous[column_index - 1] + (left != right),
            )
        previous = current
    return previous[-1]


def one_edit(left: tuple[str, ...], right: tuple[str, ...]) -> tuple[str, int, str, str]:
    if len(left) == len(right):
        differences = [index for index, pair in enumerate(zip(left, right)) if pair[0] != pair[1]]
        if len(differences) != 1:
            raise ValueError((left, right))
        index = differences[0]
        return "SUBSTITUTE", index + 1, left[index], right[index]
    if len(right) == len(left) + 1:
        for index in range(len(right)):
            if left == right[:index] + right[index + 1 :]:
                return "INSERT", index + 1, "NONE", right[index]
        raise ValueError((left, right))
    if len(left) == len(right) + 1:
        for index in range(len(left)):
            if right == left[:index] + left[index + 1 :]:
                return "DELETE", index + 1, left[index], "NONE"
        raise ValueError((left, right))
    raise ValueError((left, right))


def context_mode(rows: list[dict[str, str]]) -> str:
    contextual = sum(
        row["inherited_action_root"] != "NONE" or row["inherited_argument_root"] != "NONE"
        for row in rows
    )
    if contextual == 0:
        return "FULLY_SELF_CONTAINED"
    if contextual == len(rows):
        return "FULLY_CONTEXT_BOUND"
    return "MIXED"


def recipe_info(rows: list[dict[str, str]]) -> dict[str, object]:
    readings = {row["portable_back_projection_de"] for row in rows}
    if len(readings) != 1:
        raise RuntimeError("portable reading drift")
    registers = sorted({row["register"] for row in rows}, key=REGISTERS.index)
    return {
        "event_count": len(rows),
        "register_count": len(registers),
        "registers": "|".join(registers),
        "page_count": len({row["physical_page"] for row in rows}),
        "surface_count": len({row["surface"] for row in rows}),
        "surfaces": "|".join(sorted({row["surface"] for row in rows})),
        "context_mode": context_mode(rows),
        "portable_reading": next(iter(readings)),
    }


def role_safe_candidates(anchor: tuple[str, ...]) -> dict[tuple[str, ...], tuple[str, int, str, str]]:
    candidates: dict[tuple[str, ...], tuple[str, int, str, str]] = {}
    for index, atom in enumerate(anchor):
        role = ATOM_CLASS.get(atom)
        for replacement in POOLS.get(role, ()):
            if replacement == atom:
                continue
            candidate = anchor[:index] + (replacement,) + anchor[index + 1 :]
            candidates[candidate] = (f"SUBSTITUTE_{role}", index + 1, atom, replacement)

    if anchor[-1] == "Y":
        candidates[anchor[:-1] + ("DY",)] = ("OPEN_TO_CLOSE", len(anchor), "Y", "DY")

    grade_indices = [index for index, atom in enumerate(anchor) if atom in GRADES]
    for index in grade_indices:
        candidates[anchor[:index] + anchor[index + 1 :]] = (
            "DELETE_GRADE", index + 1, anchor[index], "NONE"
        )
    if not grade_indices and anchor[-1] in ARGUMENTS:
        for grade in GRADES:
            candidate = anchor[:-1] + (grade, anchor[-1])
            candidates[candidate] = ("INSERT_GRADE", len(anchor), "NONE", grade)
    return candidates


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    clauses = read_tsv(CLAUSES)
    dictionary = read_tsv(DICTIONARY)
    meanings = {row["atom"]: row["working_value_de"] for row in dictionary}

    by_recipe: dict[tuple[str, ...], list[dict[str, str]]] = defaultdict(list)
    for row in clauses:
        by_recipe[tokens(row["component_recipe"])].append(row)

    anchor_sequences = [tokens(anchor) for anchor in ANCHORS]
    missing_anchors = [render_recipe(anchor) for anchor in anchor_sequences if anchor not in by_recipe]
    if missing_anchors:
        raise RuntimeError(f"missing anchors: {missing_anchors}")

    all_neighbor_rows: list[dict[str, object]] = []
    role_rows: list[dict[str, object]] = []
    summary_rows: list[dict[str, object]] = []

    for anchor in anchor_sequences:
        anchor_rows = by_recipe[anchor]
        anchor_info = recipe_info(anchor_rows)
        anchor_owners = {(row["physical_page"], row["owner_de"]) for row in anchor_rows}
        anchor_statements = {row["global_statement_id"] for row in anchor_rows}
        neighbors = [candidate for candidate in by_recipe if candidate != anchor and edit_distance(anchor, candidate) == 1]

        for candidate in sorted(neighbors):
            candidate_rows = by_recipe[candidate]
            info = recipe_info(candidate_rows)
            edit_kind, position, old_atom, new_atom = one_edit(anchor, candidate)
            candidate_owners = {(row["physical_page"], row["owner_de"]) for row in candidate_rows}
            candidate_statements = {row["global_statement_id"] for row in candidate_rows}
            all_neighbor_rows.append({
                "anchor_recipe": render_recipe(anchor),
                "anchor_reading_de": anchor_info["portable_reading"],
                "neighbor_recipe": render_recipe(candidate),
                "neighbor_reading_de": info["portable_reading"],
                "edit_kind": edit_kind,
                "edit_position": position,
                "old_atom": old_atom,
                "old_value_de": meanings.get(old_atom, "NONE") if old_atom != "NONE" else "NONE",
                "new_atom": new_atom,
                "new_value_de": meanings.get(new_atom, "NONE") if new_atom != "NONE" else "NONE",
                "neighbor_event_count": info["event_count"],
                "neighbor_register_count": info["register_count"],
                "neighbor_registers": info["registers"],
                "neighbor_page_count": info["page_count"],
                "neighbor_surface_count": info["surface_count"],
                "neighbor_surfaces": info["surfaces"],
                "neighbor_context_mode": info["context_mode"],
                "shared_page_owner_count": len(anchor_owners & candidate_owners),
                "shared_statement_count": len(anchor_statements & candidate_statements),
                "role_safe_edit": "YES" if candidate in role_safe_candidates(anchor) else "NO",
            })

        candidates = role_safe_candidates(anchor)
        for candidate, (change_kind, position, old_atom, new_atom) in sorted(candidates.items()):
            candidate_rows = by_recipe.get(candidate, [])
            if candidate_rows:
                info = recipe_info(candidate_rows)
                candidate_owners = {(row["physical_page"], row["owner_de"]) for row in candidate_rows}
                candidate_statements = {row["global_statement_id"] for row in candidate_rows}
                observed_reading = info["portable_reading"]
                status = (
                    "ATTESTED_SAME_OWNER" if anchor_owners & candidate_owners
                    else "ATTESTED_CROSS_REGISTER" if int(info["register_count"]) >= 2
                    else "ATTESTED_LOCAL"
                )
            else:
                info = {
                    "event_count": 0,
                    "register_count": 0,
                    "registers": "NONE",
                    "page_count": 0,
                    "surface_count": 0,
                    "surfaces": "NONE",
                    "context_mode": "UNATTESTED",
                }
                candidate_owners = set()
                candidate_statements = set()
                observed_reading = "UNATTESTED"
                status = "MISSING_FUTURE_PREDICTION"

            predicted_reading = " · ".join(meanings[atom] for atom in candidate)
            role_rows.append({
                "anchor_recipe": render_recipe(anchor),
                "anchor_event_count": anchor_info["event_count"],
                "anchor_reading_de": anchor_info["portable_reading"],
                "candidate_recipe": render_recipe(candidate),
                "change_kind": change_kind,
                "edit_position": position,
                "old_atom": old_atom,
                "old_value_de": meanings.get(old_atom, "NONE") if old_atom != "NONE" else "NONE",
                "new_atom": new_atom,
                "new_value_de": meanings.get(new_atom, "NONE") if new_atom != "NONE" else "NONE",
                "predicted_reading_de": predicted_reading,
                "attested": "YES" if candidate_rows else "NO",
                "observed_reading_de": observed_reading,
                "reading_matches_prediction": "YES" if observed_reading == predicted_reading else "NA" if not candidate_rows else "NO",
                "event_count": info["event_count"],
                "register_count": info["register_count"],
                "registers": info["registers"],
                "page_count": info["page_count"],
                "surface_count": info["surface_count"],
                "surfaces": info["surfaces"],
                "context_mode": info["context_mode"],
                "shared_page_owner_count": len(anchor_owners & candidate_owners),
                "shared_statement_count": len(anchor_statements & candidate_statements),
                "decision": status,
            })

        safe_for_anchor = [row for row in role_rows if row["anchor_recipe"] == render_recipe(anchor)]
        all_for_anchor = [row for row in all_neighbor_rows if row["anchor_recipe"] == render_recipe(anchor)]
        summary_rows.append({
            "anchor_recipe": render_recipe(anchor),
            "anchor_reading_de": anchor_info["portable_reading"],
            "anchor_event_count": anchor_info["event_count"],
            "anchor_register_count": anchor_info["register_count"],
            "anchor_page_count": anchor_info["page_count"],
            "all_one_edit_neighbor_count": len(all_for_anchor),
            "all_one_edit_neighbor_event_count": sum(int(row["neighbor_event_count"]) for row in all_for_anchor),
            "all_neighbor_same_owner_count": sum(int(row["shared_page_owner_count"]) > 0 for row in all_for_anchor),
            "role_safe_candidate_count": len(safe_for_anchor),
            "role_safe_attested_count": sum(row["attested"] == "YES" for row in safe_for_anchor),
            "role_safe_missing_count": sum(row["attested"] == "NO" for row in safe_for_anchor),
            "role_safe_cross_register_count": sum(int(row["register_count"]) >= 2 for row in safe_for_anchor),
            "role_safe_same_owner_count": sum(int(row["shared_page_owner_count"]) > 0 for row in safe_for_anchor),
        })

    write_tsv(OUT / "gdt419_199_attested_one_atom_neighbors.tsv", all_neighbor_rows, list(all_neighbor_rows[0]))
    write_tsv(OUT / "gdt419_120_role_safe_paradigm_cells.tsv", role_rows, list(role_rows[0]))
    write_tsv(OUT / "gdt419_7_anchor_paradigm_summary.tsv", summary_rows, list(summary_rows[0]))

    change_rows: list[dict[str, object]] = []
    for change_kind in sorted({str(row["change_kind"]) for row in role_rows}):
        rows = [row for row in role_rows if row["change_kind"] == change_kind]
        attested = [row for row in rows if row["attested"] == "YES"]
        change_rows.append({
            "change_kind": change_kind,
            "candidate_cell_count": len(rows),
            "attested_cell_count": len(attested),
            "missing_cell_count": len(rows) - len(attested),
            "attested_share": f"{len(attested) / len(rows):.6f}",
            "same_owner_cell_count": sum(int(row["shared_page_owner_count"]) > 0 for row in attested),
            "cross_register_cell_count": sum(int(row["register_count"]) >= 2 for row in attested),
            "workshop_rule_de": {
                "DELETE_GRADE": "GRAD DARF IN LIZENZIERTER REIHE FEHLEN",
                "INSERT_GRADE": "GRAD NICHT FREI EINSCHIEBBAR",
                "OPEN_TO_CLOSE": "OFFENE REIHE KANN GELERNTEN SCHLUSS ERHALTEN",
                "SUBSTITUTE_ACTION": "HANDLUNGSKOPF IN PASSENDER SCHUBLADE AUSTAUSCHBAR",
                "SUBSTITUTE_ARGUMENT": "ARGUMENTSLOT TEILWEISE AUSTAUSCHBAR",
                "SUBSTITUTE_GRADE": "GRAD INNERHALB LIZENZIERTER REIHE AUSTAUSCHBAR",
            }[change_kind],
        })
    write_tsv(OUT / "gdt419_6_change_family_summary.tsv", change_rows, list(change_rows[0]))

    missing_rows = [row for row in role_rows if row["attested"] == "NO"]
    missing_by_recipe: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in missing_rows:
        missing_by_recipe[str(row["candidate_recipe"])].append(row)
    unique_missing_rows: list[dict[str, object]] = []
    for candidate_recipe, rows in sorted(missing_by_recipe.items()):
        readings = {str(row["predicted_reading_de"]) for row in rows}
        if len(readings) != 1:
            raise RuntimeError(f"prediction drift for {candidate_recipe}")
        unique_missing_rows.append({
            "candidate_recipe": candidate_recipe,
            "predicted_reading_de": next(iter(readings)),
            "source_anchor_count": len({str(row["anchor_recipe"]) for row in rows}),
            "source_anchors": "|".join(sorted({str(row["anchor_recipe"]) for row in rows})),
            "change_kinds": "|".join(sorted({str(row["change_kind"]) for row in rows})),
            "largest_anchor_event_count": max(int(row["anchor_event_count"]) for row in rows),
            "future_rule": "READ_BY_EXISTING_ATOMS_ONLY__NO_RESCUE_MEANING",
        })
    unique_missing_rows.sort(
        key=lambda row: (-int(row["source_anchor_count"]), -int(row["largest_anchor_event_count"]), str(row["candidate_recipe"]))
    )
    write_tsv(
        OUT / "gdt419_52_unique_missing_predictions.tsv",
        unique_missing_rows,
        list(unique_missing_rows[0]),
    )
    cards = [
        "# Ein-Atom-Vorhersagekarten", "",
        "Diese Formen sind auf den 26 Seiten **nicht belegt**. Falls eine davon",
        "später sichtbar komponiert erscheint, steht ihre Lesung schon jetzt fest.", "",
    ]
    for index, row in enumerate(unique_missing_rows[:20], 1):
        cards += [
            f"## {index}. `{row['candidate_recipe']}`", "",
            f"- Ausgangsfamilie(n): `{row['source_anchors']}`",
            f"- Ein-Atom-Wechsel: {row['change_kinds']}",
            f"- Vorhergesagte Kernlesung: **{row['predicted_reading_de']}**",
            "- Rote Linie: kein neuer Stamm und keine zweite Bedeutung zur Rettung.", "",
        ]
    (OUT / "TWENTY_MISSING_COMPOSITION_PREDICTIONS.md").write_text("\n".join(cards), encoding="utf-8")

    result = {
        "status": "SEVEN_ANCHOR_ONE_ATOM_PARADIGMS_COMPLETE",
        "anchor_count": len(anchor_sequences),
        "all_recipe_count": len(by_recipe),
        "all_one_edit_anchor_neighbor_pair_count": len(all_neighbor_rows),
        "unique_one_edit_neighbor_recipe_count": len({row["neighbor_recipe"] for row in all_neighbor_rows}),
        "role_safe_paradigm_cell_count": len(role_rows),
        "role_safe_attested_cell_count": sum(row["attested"] == "YES" for row in role_rows),
        "role_safe_missing_prediction_count": sum(row["attested"] == "NO" for row in role_rows),
        "unique_missing_prediction_recipe_count": len(unique_missing_rows),
        "unique_attested_role_safe_recipe_count": len({row["candidate_recipe"] for row in role_rows if row["attested"] == "YES"}),
        "change_family_count": len(change_rows),
        "attested_role_safe_same_owner_cell_count": sum(int(row["shared_page_owner_count"]) > 0 for row in role_rows),
        "attested_role_safe_cross_register_cell_count": sum(int(row["register_count"]) >= 2 for row in role_rows),
        "attested_prediction_mismatch_count": sum(row["reading_matches_prediction"] == "NO" for row in role_rows),
        "new_pages": 0,
        "dictionary_revisions": 0,
    }
    (OUT / "gdt419_result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
