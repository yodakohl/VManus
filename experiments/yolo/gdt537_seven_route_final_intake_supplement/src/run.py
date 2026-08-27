#!/usr/bin/env python3
"""Compile all seven post-intake revisions into one final lookup overlay."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

from intake_surface import exact_final_lookup


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt537_seven_route_final_intake_supplement"
OUT = BASE / "artifacts"
EDITION = (
    ROOT
    / "experiments/yolo/gdt536_aii_renderer_square_aiicthy_closure/artifacts"
    / "gdt536_159_working_revision.tsv"
)
G536_RESULT = (
    ROOT
    / "experiments/yolo/gdt536_aii_renderer_square_aiicthy_closure/artifacts"
    / "gdt536_result.json"
)
CERTIFICATES = {
    "GDT530": ROOT / "experiments/yolo/gdt530_exact_superform_peel_revision/artifacts/gdt530_selected_revision_atlas.tsv",
    "GDT531": ROOT / "experiments/yolo/gdt531_atomic_renderer_block_superform_peel/artifacts/gdt531_selected_revision_atlas.tsv",
    "GDT532": ROOT / "experiments/yolo/gdt532_same_owner_exact_card_tiling_revision/artifacts/gdt532_dsholdaiir_tile_certificate.tsv",
    "GDT533": ROOT / "experiments/yolo/gdt533_nested_odas_tail_revision/artifacts/gdt533_dairykodas_exact_card_certificate.tsv",
    "GDT534": ROOT / "experiments/yolo/gdt534_third_rung_cheeeky_grade_ladder/artifacts/gdt534_target_composition_certificate.tsv",
    "GDT535": ROOT / "experiments/yolo/gdt535_same_statement_q_null_qef_closure/artifacts/gdt535_qef_resolution_certificate.tsv",
    "GDT536": ROOT / "experiments/yolo/gdt536_aii_renderer_square_aiicthy_closure/artifacts/gdt536_aiicthy_resolution_certificate.tsv",
}


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
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    edition = read_tsv(EDITION)
    inherited_result = json.loads(G536_RESULT.read_text(encoding="utf-8"))
    cert = {key: read_tsv(path) for key, path in CERTIFICATES.items()}
    by_surface = {row["surface"]: row for row in edition}

    special_surfaces = {
        row["surface"]
        for row in edition
        if row["gdt536_working_recipe"] != row["revised_working_recipe"]
        or row["gdt536_resolution_status"].startswith("RESOLVED_BY_")
    }

    g530 = cert["GDT530"][0]
    g531 = cert["GDT531"][0]
    g532 = cert["GDT532"]
    g533 = [row for row in cert["GDT533"] if row["route"] == "SELECTED_NESTED_ODAS"]
    g534 = cert["GDT534"]
    g535 = cert["GDT535"]
    g536 = cert["GDT536"]

    route_specs = [
        {
            "surface": "chekchy",
            "source_experiment": "GDT530",
            "route_class": "EXACT_LEFT_SUPERFORM_PEEL",
            "visible_split": "peel y | chekchy from ychekchy",
            "recipe_split": "peel Y | CH+K+Y from Y+CH+K+Y",
            "primary_evidence": (
                f"{g530['old_superform']}={g530['old_superform_recipe']}; "
                f"left {g530['removed_visible']}/{g530['removed_atom']} "
                f"signature {g530['support_pair_count']}/{g530['visible_condition_total']}"
            ),
            "transfer_scope": "EXACT_MATCHED_ONE_CHARACTER_SUPERFORM_PEEL",
        },
        {
            "surface": "saiis",
            "source_experiment": "GDT531",
            "route_class": "EXACT_RIGHT_BLOCK_SUPERFORM_PEEL",
            "visible_split": "peel saiis | ol from saiisol",
            "recipe_split": "peel S+A_ADDR+IIN+S | OL",
            "primary_evidence": (
                f"{g531['old_superform']}={g531['old_superform_recipe']}; "
                f"right {g531['removed_visible_block']}/{g531['removed_atom_block']} "
                f"signature {g531['support_pair_count']}/{g531['visible_condition_total']}"
            ),
            "transfer_scope": "EXACT_MATCHED_CONTIGUOUS_BLOCK_SUPERFORM_PEEL",
        },
        {
            "surface": "dsholdaiir",
            "source_experiment": "GDT532",
            "route_class": "EXACT_CARD_TILING_WITH_SAME_OWNER_TAIL",
            "visible_split": "d | shol | daiir",
            "recipe_split": "D_ADDR | SH+OL | DA+IIN+R",
            "primary_evidence": (
                "old tile counts "
                + "|".join(row["old_event_count"] for row in g532)
                + "; daiir same-owner recurrence "
                + g532[-1]["same_owner_block_other_event_count"]
            ),
            "transfer_scope": "EXACT_INVARIANT_CARD_TILING_PLUS_LOCAL_TAIL_CARRIER",
        },
        {
            "surface": "dairykodas",
            "source_experiment": "GDT533",
            "route_class": "NESTED_EXACT_TERMINAL_WHOLE_CARD",
            "visible_split": "dair | y | k | odas",
            "recipe_split": "D_ADDR+AIR | Y | K | O+DA+S",
            "primary_evidence": (
                "selected old tile counts "
                + "|".join(row["old_event_count"] for row in g533)
                + "; odas exact terminal whole card"
            ),
            "transfer_scope": "EXACT_COMPLETE_TILING_WITH_NESTED_TERMINAL_PRIORITY",
        },
        {
            "surface": "dalcheeeky",
            "source_experiment": "GDT534",
            "route_class": "THIRD_GRADE_FAMILY_COMPLETION",
            "visible_split": "dal | cheeeky",
            "recipe_split": "AL | CH+K+EEE+Y",
            "primary_evidence": (
                f"dal exact {g534[0]['old_event_count']} events; "
                "cheeeky is the missing third rung after cheky/cheeky"
            ),
            "transfer_scope": "EXACT_K_FAMILY_GRADE_LADDER_ONLY",
        },
        {
            "surface": "qef",
            "source_experiment": "GDT535",
            "route_class": "SAME_STATEMENT_Q_ROLE_CONTEXT",
            "visible_split": "q | e | f",
            "recipe_split": "NULL | E | LOCAL_CHAR_F",
            "primary_evidence": (
                f"other q cards {g535[2]['support']}/{g535[2]['total']} "
                f"{g535[2]['value']}; old q-null {g535[0]['support']}/{g535[0]['total']}"
            ),
            "transfer_scope": "EXACT_SURFACE_LOCK_AND_UNANIMOUS_SAME_STATEMENT_Q_ROLE",
        },
        {
            "surface": "aiicthy",
            "source_experiment": "GDT536",
            "route_class": "AII_RENDERER_SQUARE_PLUS_EXACT_CTHY",
            "visible_split": "aii | cthy",
            "recipe_split": "AIIN | CH+T+Y",
            "primary_evidence": (
                f"{g536[0]['support']}; {g536[1]['support']}; "
                f"{g536[2]['support']}; {g536[4]['support']}"
            ),
            "transfer_scope": "EXACT_AIIN_SQUARE_AND_EXACT_CTHY_COMPOSITION",
        },
    ]
    spec_by_surface = {row["surface"]: row for row in route_specs}

    route_cards = []
    for ordinal, spec in enumerate(route_specs, 1):
        row = by_surface[spec["surface"]]
        changed = row["revised_working_recipe"] != row["gdt536_working_recipe"]
        route_cards.append(
            {
                "route_ordinal": ordinal,
                "surface": row["surface"],
                "occurrence_count": row["occurrence_count"],
                "physical_pages": row["physical_pages"],
                "baseline_recipe": row["revised_working_recipe"],
                "final_working_recipe": row["gdt536_working_recipe"],
                "recipe_changed": "YES" if changed else "NO",
                "revision_kind": "RECIPE_REVISION" if changed else "RESOLUTION_ONLY",
                "gdt529_candidate_rank": row["gdt536_gdt529_candidate_rank"],
                "route_class": spec["route_class"],
                "source_experiment": spec["source_experiment"],
                "visible_split": spec["visible_split"],
                "recipe_split": spec["recipe_split"],
                "literal_reading_de": row["gdt536_literal_reading_de"],
                "working_phrase_de": row["gdt536_short_phrase_de"],
                "resolution_status": row["gdt536_resolution_status"],
                "primary_evidence": spec["primary_evidence"],
                "transfer_scope": spec["transfer_scope"],
                "intake_action": "LOCK_FINAL_PROSE_SURFACE_AND_ATTACH_NAMED_ROUTE",
            }
        )

    dictionary_rows = []
    for ordinal, row in enumerate(sorted(edition, key=lambda item: item["surface"]), 1):
        route = spec_by_surface.get(row["surface"])
        dictionary_rows.append(
            {
                "dictionary_ordinal": ordinal,
                "lock_key": "PROSE_STREAM|" + row["surface"],
                "surface": row["surface"],
                "occurrence_count": row["occurrence_count"],
                "physical_pages": row["physical_pages"],
                "baseline_recipe": row["revised_working_recipe"],
                "final_working_recipe": row["gdt536_working_recipe"],
                "recipe_changed_after_gdt516": (
                    "YES" if row["revised_working_recipe"] != row["gdt536_working_recipe"] else "NO"
                ),
                "gdt529_candidate_rank": row["gdt536_gdt529_candidate_rank"],
                "literal_reading_de": row["gdt536_literal_reading_de"],
                "working_phrase_de": row["gdt536_short_phrase_de"],
                "resolution_status": row["gdt536_resolution_status"],
                "special_route": "YES" if route else "NO",
                "route_class": route["route_class"] if route else "ORDINARY_FINAL_SURFACE_LOCK",
                "route_source": route["source_experiment"] if route else "GDT536_FINAL_EDITION",
                "lock_scope": "PROSE_STREAM_ONLY",
                "local_record_policy": "DELEGATE_TO_GDT517_ROLE_AWARE_BASE",
            }
        )

    regression_rows = []
    route_by_surface = {row["surface"]: row for row in route_cards}
    for surface in sorted(special_surfaces):
        row = route_by_surface[surface]
        regression_rows.append(
            {
                "surface": surface,
                "gdt517_or_gdt516_baseline_recipe": row["baseline_recipe"],
                "gdt537_final_recipe": row["final_working_recipe"],
                "recipe_changed": row["recipe_changed"],
                "baseline_would_lose_final_choice": row["recipe_changed"],
                "final_candidate_rank": row["gdt529_candidate_rank"],
                "route_class": row["route_class"],
                "source_experiment": row["source_experiment"],
                "required_overlay_action": "FINAL_SURFACE_LOCK",
            }
        )

    class_counts = Counter(row["route_class"] for row in dictionary_rows)
    class_summary = [
        {
            "route_class": route_class,
            "surface_count": count,
            "surfaces": "|".join(
                row["surface"] for row in dictionary_rows if row["route_class"] == route_class
            ),
        }
        for route_class, count in sorted(class_counts.items())
    ]

    precedence_rows = [
        {"priority": 1, "condition": "PROSE surface is one of final 159", "action": "return GDT537 final recipe and reading", "fallback": "NONE", "guard": "exact surface plus prose scope"},
        {"priority": 2, "condition": "surface is one of seven revision cards", "action": "attach named route, split, evidence, and scope", "fallback": "ordinary final lock", "guard": "route never changes the frozen recipe"},
        {"priority": 3, "condition": "surface absent from final 159 or domain is LOCAL_RECORD", "action": "delegate unchanged request to GDT517", "fallback": "GDT517 known surface or compiler", "guard": "no GDT537 override"},
        {"priority": 4, "condition": "GDT517 returns an unseen compiled candidate", "action": "keep it provisional for the page worksheet", "fallback": "manual family audit", "guard": "no silent core retuning or special-route extrapolation"},
    ]

    write_tsv(
        OUT / "gdt537_159_final_surface_dictionary.tsv",
        dictionary_rows,
        list(dictionary_rows[0]),
    )
    write_tsv(
        OUT / "gdt537_7_revision_route_cards.tsv", route_cards, list(route_cards[0])
    )
    write_tsv(
        OUT / "gdt537_7_base_to_final_regression.tsv",
        regression_rows,
        list(regression_rows[0]),
    )
    write_tsv(
        OUT / "gdt537_route_class_summary.tsv", class_summary, list(class_summary[0])
    )
    write_tsv(
        OUT / "gdt537_intake_precedence.tsv", precedence_rows, list(precedence_rows[0])
    )

    replay_rows = []
    for row in dictionary_rows:
        response = exact_final_lookup(
            row["surface"], "PROSE_STREAM", dictionary_rows, route_cards
        )
        replay_rows.append(
            {
                "surface": row["surface"],
                "expected_recipe": row["final_working_recipe"],
                "returned_recipe": response["final_recipe"] if response else "NONE",
                "recipe_match": "YES" if response and response["final_recipe"] == row["final_working_recipe"] else "NO",
                "expected_special_route": row["special_route"],
                "returned_special_route": response["special_route"] if response else "NONE",
                "route_match": "YES" if response and response["special_route"] == row["special_route"] else "NO",
                "returned_status": response["status"] if response else "NONE",
                "lock_scope": response["lock_scope"] if response else "NONE",
            }
        )
    write_tsv(OUT / "gdt537_159_cli_replay.tsv", replay_rows, list(replay_rows[0]))

    recipe_changes = [row for row in route_cards if row["recipe_changed"] == "YES"]
    resolution_only = [row for row in route_cards if row["revision_kind"] == "RESOLUTION_ONLY"]
    rank_distribution = Counter(row["gdt529_candidate_rank"] for row in dictionary_rows)
    status = (
        "PASS_SEVEN_ROUTE_FINAL_INTAKE_SUPPLEMENT"
        if len(edition) == 159
        and len(by_surface) == 159
        and special_surfaces
        == {"aiicthy", "chekchy", "dairykodas", "dalcheeeky", "dsholdaiir", "qef", "saiis"}
        and len(route_cards) == 7
        and len(recipe_changes) == 6
        and len(resolution_only) == 1
        and resolution_only[0]["surface"] == "qef"
        and len(dictionary_rows) == 159
        and class_counts["ORDINARY_FINAL_SURFACE_LOCK"] == 152
        and rank_distribution == Counter({"1": 156, "2": 1, "6": 1, "UNGENERATED": 1})
        and all(row["resolution_status"] != "UNRESOLVED_NON_TOP1" for row in dictionary_rows)
        and len(replay_rows) == 159
        and all(row["recipe_match"] == "YES" and row["route_match"] == "YES" for row in replay_rows)
        and g530["surface"] == "chekchy"
        and g531["surface"] == "saiis"
        and [row["tile_surface"] for row in g532] == ["d", "shol", "daiir"]
        and [row["tile_surface"] for row in g533] == ["dair", "y", "k", "odas"]
        and [row["surface_piece"] for row in g534] == ["dal", "cheeeky"]
        and g535[2]["support"] == "6"
        and g536[-1]["recipe"] == "AIIN+CH+T+Y"
        else "FAIL_SEVEN_ROUTE_FINAL_INTAKE_GATE"
    )

    result = {
        "experiment_id": "GDT537",
        "status": status,
        "claim_ceiling": "FINAL_WORKING_PROSE_SURFACE_OVERLAY_AND_SEVEN_NAMED_ROUTE_CARDS__NO_GLOBAL_EXTENSION_OR_CONFIRMED_PLAINTEXT",
        "route_scope_correction": {
            "previous_short_route_count": 4,
            "complete_revision_route_count": 7,
            "previously_omitted_rank1_surfaces": ["chekchy", "saiis", "dairykodas"],
            "reason": "all post-GDT516 recipe revisions must survive the older exact-event compiler",
        },
        "final_dictionary": {
            "surface_count": len(dictionary_rows),
            "resolved_count": sum(row["resolution_status"] != "UNRESOLVED_NON_TOP1" for row in dictionary_rows),
            "ordinary_surface_count": class_counts["ORDINARY_FINAL_SURFACE_LOCK"],
            "special_route_surface_count": len(route_cards),
            "recipe_revision_count": len(recipe_changes),
            "resolution_only_count": len(resolution_only),
            "candidate_rank_distribution": dict(sorted(rank_distribution.items())),
        },
        "revision_surfaces": [row["surface"] for row in route_cards],
        "cli_replay": {
            "probe_count": len(replay_rows),
            "recipe_match_count": sum(row["recipe_match"] == "YES" for row in replay_rows),
            "route_match_count": sum(row["route_match"] == "YES" for row in replay_rows),
        },
        "inherited_gdt536_resolved_count": inherited_result["working_resolved_surface_count"],
        "selection_precedence": [row["action"] for row in precedence_rows],
        "next_use": "Apply this overlay before GDT517 on future PROSE_STREAM exact repeats; delegate local records and unseen surfaces.",
        "guard": "SEVEN_EXACT_ROUTE_CARDS_ONLY__NO_SPECIAL_ROUTE_EXTRAPOLATION__NO_NEW_PAGES",
    }
    write_json(OUT / "gdt537_result.json", result)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if status.startswith("PASS_") else 1


if __name__ == "__main__":
    raise SystemExit(main())
