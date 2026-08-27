#!/usr/bin/env python3
"""Validate GDT517's compiler, exact dictionary, and role-aware execution replay."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt517_thirty_page_surface_recipe_intake_compiler"
OUT = BASE / "artifacts"


def read_tsv(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> int:
    result = json.loads((OUT / "gdt517_result.json").read_text(encoding="utf-8"))
    recovery = read_tsv("gdt517_159_new_surface_recovery.tsv")
    disagreements = read_tsv("gdt517_top1_disagreement_atlas.tsv")
    ladder = read_tsv("gdt517_model_ladder.tsv")
    old_lexicon = read_tsv("gdt517_old26_chunk_mapping_lexicon.tsv")
    current_lexicon = read_tsv("gdt517_current30_chunk_mapping_lexicon.tsv")
    rounds = read_tsv("gdt517_residual_closure_iterations.tsv")
    exact = read_tsv("gdt517_5866_exact_event_dictionary.tsv")
    surface = read_tsv("gdt517_current30_surface_role_index.tsv")
    replay = read_tsv("gdt517_546_selected_prose_execution_replay.tsv")
    repairs = read_tsv("gdt517_non_green_and_role_repair_atlas.tsv")

    ranks = [int(row["gdt516_recipe_rank"]) for row in recovery]
    stage = {row["model_stage"]: row for row in ladder}
    raw = Counter(row["raw_gdt451_decision"] for row in replay)
    final = Counter(row["gdt517_final_decision"] for row in replay)
    exact_sources = Counter(row["semantic_source"] for row in exact)
    old_rounds = [row for row in rounds if row["model"] == "OLD26_RUNNING"]
    checks = {
        "status_pass": result["status"] == "PASS_EXECUTABLE_SURFACE_TO_RECIPE_INTAKE",
        "old_training_4576": result["old26_training_events"] == 4576,
        "old_surfaces_1558": result["old26_training_surfaces"] == 1558,
        "current_running_5122": result["current30_running_events"] == 5122,
        "current_surfaces_1711": result["current30_running_surfaces"] == 1711,
        "recovery_159": len(recovery) == 159,
        "all_surfaces_parsed": all(row["parsed"] == "YES" for row in recovery),
        "all_truth_recipes_generated": all(rank > 0 for rank in ranks),
        "top1_at_least_110": sum(rank == 1 for rank in ranks) >= 110,
        "top5_at_least_155": sum(0 < rank <= 5 for rank in ranks) >= 155,
        "only_two_deep_cases": sum(rank > 5 for rank in ranks) == 2,
        "disagreement_count_matches": len(disagreements) == sum(rank != 1 for rank in ranks),
        "model_ladder_four_stages": len(ladder) == 4,
        "ladder_parse_monotone": [int(row["parsed_count"]) for row in ladder] == sorted(
            int(row["parsed_count"]) for row in ladder
        ),
        "closure_beats_complete_top1": int(stage["PLUS_ITERATIVE_RESIDUAL_CLOSURE"]["top1_exact_count"])
        > int(stage["ALL_OLD_COMPLETE_RECIPE_CHUNKS"]["top1_exact_count"]),
        "old_lexicon_count_matches": len(old_lexicon) == result["old26_retained_mappings"],
        "current_lexicon_count_matches": len(current_lexicon) == result["current30_retained_mappings"],
        "old_closure_converged": old_rounds[-1]["new_residual_derivations"] == "0",
        "finite_x_mapping": any(row["surface_chunk"] == "x" and row["recipe"] == "LOCAL_X" for row in old_lexicon),
        "finite_c_mapping": any(row["surface_chunk"] == "c" and row["recipe"] == "LOCAL_C" for row in old_lexicon),
        "dy_three_main_options": {"DY", "D_ADDR+Y", "Y"}.issubset(
            {row["recipe"] for row in old_lexicon if row["surface_chunk"] == "dy"}
        ),
        "dy_not_high_confidence": all(
            row["high_confidence_top_mapping"] == "NO"
            for row in old_lexicon if row["surface_chunk"] == "dy"
        ),
        "exact_dictionary_5866": len(exact) == 5866,
        "exact_global_ids_unique": len({row["global_group_id"] for row in exact}) == 5866,
        "exact_source_ids_unique": len({row["source_event_id"] for row in exact}) == 5866,
        "group_kind_5122_744": Counter(row["group_kind"] for row in exact)
        == {"RUNNING_EVENT": 5122, "LOCAL_ADDRESS_OR_LABEL": 744},
        "gdt473_all_183_integrated": exact_sources["GDT473_COMPLETE_LOCAL_ADDRESS_EDITION"] == 183,
        "gdt513_all_510_integrated": exact_sources["GDT513_REMAINING_LOCAL_WORKING_EDITION"] == 510,
        "no_stale_local_address_recipe": all(row["exact_event_recipe"] != "LOCAL_ADDRESS" for row in exact),
        "learned_labels_are_packages": all(
            "LOCAL_LABEL_PACKAGE::" in row["exact_event_recipe"]
            for row in exact
            if row["semantic_source"] == "GDT473_COMPLETE_LOCAL_ADDRESS_EDITION"
            and row["package_status"] != "FULL_FUNCTION_FORMULA"
        ),
        "surface_index_nonempty": len(surface) > 2000,
        "prose_surface_recipe_invariant": all(
            row["finite_recipe_option_count_for_surface_domain"] == "1"
            for row in surface if row["execution_domain"] == "PROSE_STREAM"
        ),
        "local_surface_options_finite": max(
            int(row["finite_recipe_option_count_for_surface_domain"])
            for row in surface if row["execution_domain"] == "LOCAL_RECORD"
        ) <= 5,
        "replay_546": len(replay) == 546,
        "raw_539_1_6": raw == {"READ": 539, "READ_AMBER": 1, "STOP": 6},
        "repair_atlas_seven": len(repairs) == 7,
        "three_role_container_repairs": final["READ_ROLE_CONTAINER"] == 3,
        "two_local_shell_repairs": final["READ_LOCAL_SHELL"] == 2,
        "two_amber_reads": final["READ_AMBER"] == 2,
        "zero_final_stops": final["STOP"] == 0,
        "role_repairs_preserve_state": all(
            row["incoming_action"] == row["outgoing_action"]
            and row["incoming_argument"] == row["outgoing_argument"]
            for row in repairs if row["finite_override"] == "ROLE_SEPARATION"
        ),
        "no_plaintext_claim": "NO_CONFIRMED_LEXEME_OR_PLAINTEXT" in result["claim_ceiling"],
    }
    payload = {
        "experiment_id": "GDT517",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "passed": sum(checks.values()),
        "total": len(checks),
        "checks": checks,
    }
    (OUT / "gdt517_validation.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
