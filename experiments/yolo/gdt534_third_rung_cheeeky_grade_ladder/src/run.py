#!/usr/bin/env python3
"""Complete dalcheeeky's local cheky/cheeky grade ladder at EEE."""

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
BASE = ROOT / "experiments/yolo/gdt534_third_rung_cheeeky_grade_ladder"
OUT = BASE / "artifacts"
OLD_RUNNING = (
    ROOT
    / "experiments/yolo/gdt407_unified_twenty_six_page_workshop_edition/artifacts"
    / "gdt407_4576_running_event_edition.tsv"
)
CURRENT_EVENTS = (
    ROOT
    / "experiments/yolo/gdt516_thirty_page_new_surface_family_consolidation/artifacts"
    / "gdt516_597_contextualized_event_edition.tsv"
)
CANDIDATES = (
    ROOT
    / "experiments/yolo/gdt529_nearest_terminal_m_square/artifacts"
    / "gdt529_candidate_score_atlas.tsv"
)
CURRENT_WORKING = (
    ROOT
    / "experiments/yolo/gdt533_nested_odas_tail_revision/artifacts"
    / "gdt533_159_working_revision.tsv"
)
CURRENT_RESULT = (
    ROOT
    / "experiments/yolo/gdt533_nested_odas_tail_revision/artifacts"
    / "gdt533_result.json"
)

SELECTED_SURFACE = "dalcheeeky"
SELECTED_EVENT = "G515-E0423"
SELECTED_RECIPE = "AL+CH+K+EEE+Y"
PREVIOUS_RECIPE = "AL+CH+EEE+K+Y"
VISIBLE_PREFIX = "dal"
VISIBLE_STEM = "cheeeky"
WORKING_LITERAL_DE = (
    "ZIELORT · NEHMEN · GEBEN · [EEE:STEUERUNG=GRAD III] · POSTEN"
)
WORKING_PHRASE_DE = "Am Zielort nehmen und geben; auf Grad III posten."


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=fields, delimiter="\t", lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows({field: row.get(field, "") for field in fields} for row in rows)


def write_json(path: Path, value: object) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def exact_inventory(rows: list[dict[str, str]]) -> dict[str, dict]:
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[row["surface"]].append(row)
    inventory = {}
    for surface, surface_rows in grouped.items():
        recipes = {row["component_recipe"] for row in surface_rows}
        if len(recipes) != 1:
            continue
        inventory[surface] = {
            "recipe": next(iter(recipes)),
            "event_count": len(surface_rows),
            "pages": "|".join(sorted({row["physical_page"] for row in surface_rows})),
            "registers": "|".join(sorted({row["register"] for row in surface_rows})),
            "event_ids": "|".join(row["global_running_event_id"] for row in surface_rows),
            "loci": "|".join(row["locus"] for row in surface_rows),
            "rows": surface_rows,
        }
    return inventory


def remove_one_visible_e(surface: str) -> set[str]:
    return {
        surface[:index] + surface[index + 1 :]
        for index, char in enumerate(surface)
        if char == "e"
    }


def grade_transition(left_recipe: str, right_recipe: str) -> tuple[str, int] | None:
    left = left_recipe.split("+")
    right = right_recipe.split("+")
    if len(left) != len(right):
        return None
    differences = [
        index for index, pair in enumerate(zip(left, right)) if pair[0] != pair[1]
    ]
    if len(differences) != 1:
        return None
    index = differences[0]
    pair = (left[index], right[index])
    if pair == ("E", "EE"):
        return "E_TO_EE", index
    if pair == ("EE", "EEE"):
        return "EE_TO_EEE", index
    return None


def grade_pair_atlas(inventory: dict[str, dict]) -> list[dict]:
    pairs = {}
    for extended_surface, extended in inventory.items():
        for base_surface in remove_one_visible_e(extended_surface):
            if base_surface not in inventory:
                continue
            base = inventory[base_surface]
            transition = grade_transition(base["recipe"], extended["recipe"])
            if transition is None:
                continue
            step, atom_index = transition
            key = (base_surface, extended_surface, base["recipe"], extended["recipe"])
            pairs[key] = {
                "grade_step": step,
                "grade_atom_ordinal": atom_index + 1,
                "base_surface": base_surface,
                "extended_surface": extended_surface,
                "visible_operation": "INSERT_ONE_e",
                "base_recipe": base["recipe"],
                "extended_recipe": extended["recipe"],
                "recipe_operation": step,
                "base_event_count": base["event_count"],
                "extended_event_count": extended["event_count"],
                "base_pages": base["pages"],
                "extended_pages": extended["pages"],
                "base_registers": base["registers"],
                "extended_registers": extended["registers"],
                "is_cheky_family": (
                    "YES"
                    if base_surface == "cheky" and extended_surface == "cheeky"
                    else "NO"
                ),
            }
    return sorted(
        pairs.values(),
        key=lambda row: (
            row["grade_step"],
            row["base_surface"],
            row["extended_surface"],
        ),
    )


def complete_grade_ladders(pair_rows: list[dict]) -> list[dict]:
    lower = [row for row in pair_rows if row["grade_step"] == "E_TO_EE"]
    upper = [row for row in pair_rows if row["grade_step"] == "EE_TO_EEE"]
    ladders = {}
    for first in lower:
        for second in upper:
            if (
                first["extended_surface"] != second["base_surface"]
                or first["extended_recipe"] != second["base_recipe"]
                or first["grade_atom_ordinal"] != second["grade_atom_ordinal"]
            ):
                continue
            key = (
                first["base_surface"],
                first["extended_surface"],
                second["extended_surface"],
                first["base_recipe"],
                first["extended_recipe"],
                second["extended_recipe"],
            )
            ladders[key] = {
                "rung_I_surface": first["base_surface"],
                "rung_II_surface": first["extended_surface"],
                "rung_III_surface": second["extended_surface"],
                "visible_ladder": (
                    f"{first['base_surface']} -> {first['extended_surface']} -> "
                    f"{second['extended_surface']}"
                ),
                "rung_I_recipe": first["base_recipe"],
                "rung_II_recipe": first["extended_recipe"],
                "rung_III_recipe": second["extended_recipe"],
                "recipe_ladder": (
                    f"{first['base_recipe']} -> {first['extended_recipe']} -> "
                    f"{second['extended_recipe']}"
                ),
                "grade_atom_ordinal": first["grade_atom_ordinal"],
                "rung_I_event_count": first["base_event_count"],
                "rung_II_event_count": first["extended_event_count"],
                "rung_III_event_count": second["extended_event_count"],
                "pages_union": "|".join(
                    sorted(
                        set(first["base_pages"].split("|"))
                        | set(first["extended_pages"].split("|"))
                        | set(second["extended_pages"].split("|"))
                    )
                ),
                "registers_union": "|".join(
                    sorted(
                        set(first["base_registers"].split("|"))
                        | set(first["extended_registers"].split("|"))
                        | set(second["extended_registers"].split("|"))
                    )
                ),
            }
    return sorted(ladders.values(), key=lambda row: row["visible_ladder"])


def skeleton(recipe: str) -> str:
    return "+".join(
        "GRADE" if atom in {"E", "EE", "EEE"} else atom
        for atom in recipe.split("+")
    )


def rank_metric(rows: list[dict], field: str) -> dict[str, int]:
    ranks = [int(row[field]) for row in rows]
    return {
        "target_count": len(ranks),
        "truth_generated_count": len(ranks),
        "top1_exact_count": sum(rank <= 1 for rank in ranks),
        "top2_exact_count": sum(rank <= 2 for rank in ranks),
        "top3_exact_count": sum(rank <= 3 for rank in ranks),
        "top5_exact_count": sum(rank <= 5 for rank in ranks),
        "rank_sum": sum(ranks),
        "deepest_truth_rank": max(ranks),
    }


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    old = read_tsv(OLD_RUNNING)
    current_events = read_tsv(CURRENT_EVENTS)
    candidate_rows = read_tsv(CANDIDATES)
    current = read_tsv(CURRENT_WORKING)
    inherited_result = json.loads(CURRENT_RESULT.read_text(encoding="utf-8"))
    inventory = exact_inventory(old)
    pair_rows = grade_pair_atlas(inventory)
    ladder_rows = complete_grade_ladders(pair_rows)

    pair_counts = Counter(row["grade_step"] for row in pair_rows)
    cheky_pair = next(
        row
        for row in pair_rows
        if row["base_surface"] == "cheky" and row["extended_surface"] == "cheeky"
    )

    family_rows = []
    for rung, surface, recipe, relation in (
        ("I", "cheky", "CH+K+E+Y", "EXACT_OLD_WHOLE_CARD"),
        ("II", "cheeky", "CH+K+EE+Y", "EXACT_OLD_WHOLE_CARD"),
    ):
        card = inventory[surface]
        family_rows.append(
            {
                "rung": rung,
                "surface_or_embedded_stem": surface,
                "recipe": recipe,
                "old_event_count": card["event_count"],
                "old_pages": card["pages"],
                "old_registers": card["registers"],
                "old_event_ids": card["event_ids"],
                "current_event_id": "NONE",
                "relation": relation,
                "status": "OBSERVED",
            }
        )
    family_rows.append(
        {
            "rung": "III",
            "surface_or_embedded_stem": VISIBLE_STEM,
            "recipe": "CH+K+EEE+Y",
            "old_event_count": 0,
            "old_pages": "NONE",
            "old_registers": "NONE",
            "old_event_ids": "NONE",
            "current_event_id": SELECTED_EVENT,
            "relation": "PREDICTED_EMBEDDED_STEM_IN_dal|cheeeky",
            "status": "WORKING_FAMILY_COMPLETION",
        }
    )

    family_context_rows = []
    for row in old:
        if row["surface"] not in {"cheky", "cheeky"}:
            continue
        family_context_rows.append(
            {
                "global_running_event_id": row["global_running_event_id"],
                "physical_page": row["physical_page"],
                "register": row["register"],
                "locus": row["locus"],
                "surface": row["surface"],
                "component_recipe": row["component_recipe"],
                "literal_core_reading_de": row["literal_core_reading_de"],
                "family_rung": "I" if row["surface"] == "cheky" else "II",
            }
        )

    long_e_rows = []
    for surface, card in sorted(inventory.items()):
        if "eee" not in surface:
            continue
        atoms = card["recipe"].split("+")
        long_e_rows.append(
            {
                "surface": surface,
                "recipe": card["recipe"],
                "old_event_count": card["event_count"],
                "old_pages": card["pages"],
                "old_registers": card["registers"],
                "contains_EEE_atom": "YES" if "EEE" in atoms else "NO",
                "contains_CH_atom": "YES" if "CH" in atoms else "NO",
                "contains_K_atom": "YES" if "K" in atoms else "NO",
                "recipe_skeleton": skeleton(card["recipe"]),
                "relation": (
                    "GLOBAL_cheee_RENDERER_CONTROL"
                    if "cheee" in surface
                    else "OTHER_LONG_e_GRADE_CONTROL"
                ),
            }
        )
    long_e_rows.append(
        {
            "surface": SELECTED_SURFACE,
            "recipe": SELECTED_RECIPE,
            "old_event_count": 0,
            "old_pages": "NONE",
            "old_registers": "NONE",
            "contains_EEE_atom": "YES",
            "contains_CH_atom": "YES",
            "contains_K_atom": "YES",
            "recipe_skeleton": skeleton(SELECTED_RECIPE),
            "relation": "TARGET_LOCAL_cheeeky_K_GRADE_FAMILY",
        }
    )

    target_block_rows = []
    target_event_row = next(
        row for row in current_events if row["event_id"] == SELECTED_EVENT
    )
    for row in current_events:
        if row["prose_block_id"] != target_event_row["prose_block_id"]:
            continue
        target_block_rows.append(
            {
                "event_id": row["event_id"],
                "physical_page": row["physical_page"],
                "locus": row["locus"],
                "line_number": row["line_number"],
                "statement_id": row["statement_id"],
                "card_ordinal_in_statement": row["card_ordinal_in_statement"],
                "prose_block_id": row["prose_block_id"],
                "owner_id": row["owner_id"],
                "surface": row["surface"],
                "gdt516_context_recipe": row["gdt516_context_recipe"],
                "gdt516_literal_reading_de": row["gdt516_literal_reading_de"],
                "relation": (
                    "TARGET"
                    if row["event_id"] == SELECTED_EVENT
                    else "SAME_STATEMENT"
                    if row["statement_id"] == target_event_row["statement_id"]
                    else "SAME_OWNER_BLOCK"
                ),
            }
        )

    target_candidates = [
        row for row in candidate_rows if row["surface"] == SELECTED_SURFACE
    ]
    comparison_rows = []
    for row in target_candidates:
        recipe = row["candidate_recipe"]
        if recipe == PREVIOUS_RECIPE:
            decision = "REPLACE_GRADE_BEFORE_K_WITH_LOCAL_K_GRADE_ORDER"
        elif row["gdt529_rank"] == "1":
            decision = "REJECT_DROPS_CH_FROM_RECURRENT_cheky_FAMILY"
        else:
            decision = "RETAIN_AS_FINITE_RIVAL"
        comparison_rows.append(
            {
                "surface": SELECTED_SURFACE,
                "candidate_recipe": recipe,
                "gdt529_rank": row["gdt529_rank"],
                "gdt529_score": row["gdt529_score"],
                "candidate_space_status": "GENERATED",
                "recipe_skeleton": skeleton(recipe),
                "matches_CH_K_GRADE_Y_order": (
                    "YES" if recipe.endswith("CH+K+EEE+Y") else "NO"
                ),
                "matches_exact_cheky_grade_frame": (
                    "YES" if skeleton(recipe) == "AL+CH+K+GRADE+Y" else "NO"
                ),
                "decision": decision,
            }
        )
    comparison_rows.append(
        {
            "surface": SELECTED_SURFACE,
            "candidate_recipe": SELECTED_RECIPE,
            "gdt529_rank": "UNGENERATED",
            "gdt529_score": "NOT_SCORED",
            "candidate_space_status": "OUTSIDE_GDT529_FINITE_SET",
            "recipe_skeleton": skeleton(SELECTED_RECIPE),
            "matches_CH_K_GRADE_Y_order": "YES",
            "matches_exact_cheky_grade_frame": "YES",
            "decision": "SELECT_THIRD_RUNG_FAMILY_COMPLETION",
        }
    )

    prefix = inventory[VISIBLE_PREFIX]
    certificate_rows = [
        {
            "ordinal": 1,
            "surface_piece": VISIBLE_PREFIX,
            "recipe_piece": "AL",
            "old_event_count": prefix["event_count"],
            "old_pages": prefix["pages"],
            "evidence": "EXACT_OLD_PREFIX_CARD",
        },
        {
            "ordinal": 2,
            "surface_piece": VISIBLE_STEM,
            "recipe_piece": "CH+K+EEE+Y",
            "old_event_count": 0,
            "old_pages": "NONE",
            "evidence": (
                "PREDICTED_FROM_cheky=CH+K+E+Y_AND_"
                "cheeky=CH+K+EE+Y_PLUS_OLD_EE_TO_EEE_LADDERS"
            ),
        },
    ]

    edition = []
    for row in current:
        surface = row["surface"]
        if surface == SELECTED_SURFACE:
            recipe = SELECTED_RECIPE
            rank = "UNGENERATED"
            candidate_status = "OUTSIDE_GDT529_FINITE_SET"
            literal = WORKING_LITERAL_DE
            phrase = WORKING_PHRASE_DE
            evidence = (
                "dal=AL exact old card; cheky=CH+K+E+Y (9) -> "
                "cheeky=CH+K+EE+Y (5); general old EE->EEE ladders license "
                "embedded cheeeky=CH+K+EEE+Y"
            )
            policy = "GDT534_THIRD_RUNG_cheeeky_FAMILY_COMPLETION"
            resolution = "RESOLVED_BY_THIRD_GRADE_FAMILY_COMPLETION"
        else:
            recipe = row["gdt533_working_recipe"]
            rank = row["gdt533_candidate_rank"]
            candidate_status = "IN_GDT529_FINITE_SET"
            literal = row["gdt533_literal_reading_de"]
            phrase = row["gdt533_short_phrase_de"]
            evidence = "NO_SELECTED_THIRD_RUNG_REVISION"
            policy = "INHERIT_GDT533_WORKING_RECIPE"
            resolution = row["gdt533_resolution_status"]
        edition.append(
            {
                **row,
                "gdt534_working_recipe": recipe,
                "gdt534_candidate_rank": rank,
                "gdt534_candidate_space_status": candidate_status,
                "gdt534_literal_reading_de": literal,
                "gdt534_short_phrase_de": phrase,
                "gdt534_evidence": evidence,
                "gdt534_policy": policy,
                "gdt534_resolution_status": resolution,
            }
        )

    unresolved = [
        row
        for row in edition
        if row["gdt534_resolution_status"] == "UNRESOLVED_NON_TOP1"
    ]
    in_space = [
        row for row in edition if row["gdt534_candidate_rank"] != "UNGENERATED"
    ]
    in_space_metrics = rank_metric(in_space, "gdt534_candidate_rank")
    inherited_metrics = inherited_result["gdt533_candidate_agreement_metrics"]
    selected_absent = all(
        row["candidate_recipe"] != SELECTED_RECIPE for row in target_candidates
    )
    complete_ladder_examples = [row["visible_ladder"] for row in ladder_rows[:12]]

    status = (
        "PASS_THIRD_RUNG_cheeeky_WORKING_REVISION"
        if len(old) == 4576
        and len(current) == 159
        and len(target_candidates) == 12
        and selected_absent
        and target_event_row["surface"] == SELECTED_SURFACE
        and target_event_row["gdt516_context_recipe"] == PREVIOUS_RECIPE
        and inventory["dal"]["recipe"] == "AL"
        and inventory["dal"]["event_count"] == 44
        and cheky_pair["base_recipe"] == "CH+K+E+Y"
        and cheky_pair["extended_recipe"] == "CH+K+EE+Y"
        and cheky_pair["base_event_count"] == 9
        and cheky_pair["extended_event_count"] == 5
        and pair_counts["E_TO_EE"] > 0
        and pair_counts["EE_TO_EEE"] > 0
        and len(ladder_rows) >= 5
        and any(
            row["surface"] == "cheeety" and row["recipe"] == "EEE+T+Y"
            for row in long_e_rows
        )
        and len(target_block_rows) == 37
        and len(unresolved) == 2
        and len(in_space) == 158
        else "FAIL_THIRD_RUNG_GATE"
    )

    result = {
        "experiment_id": "GDT534",
        "status": status,
        "claim_ceiling": (
            "EXPLORATORY_LOCAL_K_GRADE_FAMILY_COMPLETION__"
            "NO_GLOBAL_cheee_PARSE__NO_CONFIRMED_LEXEME_OR_PLAINTEXT"
        ),
        "old_running_event_count": len(old),
        "current_target_count": len(current),
        "deduplicated_grade_pair_count": len(pair_rows),
        "grade_pair_counts": dict(sorted(pair_counts.items())),
        "complete_old_three_rung_ladder_count": len(ladder_rows),
        "complete_old_three_rung_ladder_examples": complete_ladder_examples,
        "selected_revision_count": 1,
        "selected_revision": {
            "surface": SELECTED_SURFACE,
            "event_id": SELECTED_EVENT,
            "previous_working_recipe": PREVIOUS_RECIPE,
            "previous_candidate_rank": 2,
            "new_working_recipe": SELECTED_RECIPE,
            "new_candidate_rank": "UNGENERATED",
            "candidate_space_status": "OUTSIDE_GDT529_FINITE_SET",
            "surface_tiling": "dal|cheeeky",
            "recipe_tiling": "AL | CH+K+EEE+Y",
            "family_ladder": (
                "cheky=CH+K+E+Y -> cheeky=CH+K+EE+Y -> "
                "cheeeky=CH+K+EEE+Y"
            ),
            "old_family_event_counts": {"cheky": 9, "cheeky": 5},
            "exact_prefix_old_event_count": prefix["event_count"],
            "working_literal_de": WORKING_LITERAL_DE,
            "working_phrase_de": WORKING_PHRASE_DE,
        },
        "global_cheee_control": (
            "cheeety=EEE+T+Y proves cheee may collapse to EEE elsewhere; "
            "the selected parse is licensed only by the complete ...ky frame"
        ),
        "inherited_gdt533_candidate_metrics": inherited_metrics,
        "gdt534_in_space_candidate_metrics": in_space_metrics,
        "working_outside_candidate_space_count": 1,
        "working_resolved_surface_count": len(edition) - len(unresolved),
        "remaining_unresolved_surface_count": len(unresolved),
        "remaining_unresolved_surfaces": [row["surface"] for row in unresolved],
        "guard": (
            "APPLY_ONLY_TO_EXACT_cheky_cheeky_K_GRADE_FRAME_PLUS_OLD_EE_TO_EEE_"
            "LADDER_AND_EXACT_dal_PREFIX__DO_NOT_GLOBALIZE_cheee__NO_NEW_PAGES"
        ),
    }

    write_tsv(OUT / "gdt534_159_working_revision.tsv", edition, list(edition[0]))
    write_tsv(
        OUT / "gdt534_old_grade_step_pair_atlas.tsv", pair_rows, list(pair_rows[0])
    )
    write_tsv(
        OUT / "gdt534_complete_grade_ladder_atlas.tsv",
        ladder_rows,
        list(ladder_rows[0]),
    )
    write_tsv(
        OUT / "gdt534_cheky_family_ladder.tsv", family_rows, list(family_rows[0])
    )
    write_tsv(
        OUT / "gdt534_cheky_family_contexts.tsv",
        family_context_rows,
        list(family_context_rows[0]),
    )
    write_tsv(
        OUT / "gdt534_long_e_renderer_context_control.tsv",
        long_e_rows,
        list(long_e_rows[0]),
    )
    write_tsv(
        OUT / "gdt534_dalcheeeky_candidate_comparison.tsv",
        comparison_rows,
        list(comparison_rows[0]),
    )
    write_tsv(
        OUT / "gdt534_target_composition_certificate.tsv",
        certificate_rows,
        list(certificate_rows[0]),
    )
    write_tsv(
        OUT / "gdt534_target_owner_block_atlas.tsv",
        target_block_rows,
        list(target_block_rows[0]),
    )
    write_tsv(
        OUT / "gdt534_remaining_unresolved_atlas.tsv",
        unresolved,
        list(edition[0]),
    )
    write_json(OUT / "gdt534_result.json", result)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if status.startswith("PASS_") else 1


if __name__ == "__main__":
    raise SystemExit(main())
