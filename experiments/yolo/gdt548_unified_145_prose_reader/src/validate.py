#!/usr/bin/env python3
"""Independent validation for the unified GDT548 145-surface reader."""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import Any


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
EXP = ROOT / "experiments/yolo/gdt548_unified_145_prose_reader"
ART = EXP / "artifacts"
READER = ART / "gdt548_145_unified_prose_reader.tsv"
QUEUE = ART / "gdt548_23_named_default_queue.tsv"
SUMMARY = ART / "gdt548_unified_reader_summary.tsv"
BOOK = ART / "GDT548_145_UNIFIED_PROSE_READER.md"
RESULT = ART / "gdt548_result.json"
VALIDATION = ART / "gdt548_validation.json"
RUN = EXP / "src/run.py"
CLI = EXP / "src/read_prose.py"

CONTEXT = (
    ROOT
    / "experiments/yolo/gdt540_target_surface_context_requirement_contract/artifacts"
    / "gdt540_145_surface_context_contract.tsv"
)
EXACT = (
    ROOT
    / "experiments/yolo/gdt541_old_prefix_exact_recipe_context_replay/artifacts"
    / "gdt541_11_recipe_context_profile_transfer.tsv"
)
TIERS = (
    ROOT
    / "experiments/yolo/gdt542_full_old_tile_context_bridge/artifacts"
    / "gdt542_145_final_support_tiers.tsv"
)
TILES = (
    ROOT
    / "experiments/yolo/gdt542_full_old_tile_context_bridge/artifacts"
    / "gdt542_29_full_tile_context_bridges.tsv"
)
FRAGMENTS = (
    ROOT
    / "experiments/yolo/gdt546_consolidated_fragment_reader/artifacts"
    / "gdt546_81_consolidated_fragment_reader.tsv"
)
ATOMS = (
    ROOT
    / "experiments/yolo/gdt547_atomic_factor_visible_reader/artifacts"
    / "gdt547_24_atomic_factor_reader_cards.tsv"
)

EXPECTED_STATUS = "PASS_ONE_EXACT_KEY_READER_FOR_145_PROSE_SURFACES__23_NAMED_DEFAULTS"
EXPECTED_TIERS = {
    "FULL_OLD_RECIPE_CARRIER": 11,
    "FULLY_TILED_BY_OLD_MULTICOMPONENT_RECIPES": 29,
    "OLD_COMPLETE_RECIPE_FRAGMENT_PLUS_ATOMS": 81,
    "ATOMS_AND_FACTORS_ONLY": 24,
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def keyed(rows: list[dict[str, str]], field: str) -> dict[str, dict[str, str]]:
    return {row[field]: row for row in rows}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CLI), *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def main() -> int:
    checks: list[dict[str, Any]] = []

    def check(name: str, passed: bool, detail: Any) -> None:
        checks.append({"check": name, "passed": bool(passed), "detail": detail})

    cards = read_tsv(READER)
    queue = read_tsv(QUEUE)
    context_rows = read_tsv(CONTEXT)
    tier_rows = read_tsv(TIERS)
    exact_rows = read_tsv(EXACT)
    tile_rows = read_tsv(TILES)
    fragment_rows = read_tsv(FRAGMENTS)
    atom_rows = read_tsv(ATOMS)

    card_map = keyed(cards, "surface")
    contexts = keyed(context_rows, "surface")
    tiers = keyed(tier_rows, "surface")
    exacts = keyed(exact_rows, "target_surface")
    tiles = keyed(tile_rows, "target_surface")
    fragments = keyed(fragment_rows, "surface")
    atoms = keyed(atom_rows, "surface")

    check("reader_card_count", len(cards) == 145, len(cards))
    check("reader_unique_surface_count", len(card_map) == 145, len(card_map))
    check(
        "reader_surface_set_exact",
        set(card_map) == set(contexts) == set(tiers),
        sorted((set(contexts) ^ set(card_map)) | (set(tiers) ^ set(card_map))),
    )
    check(
        "reader_ordinals_exact",
        [int(row["target_ordinal"]) for row in cards] == list(range(1, 146)),
        [cards[0]["target_ordinal"], cards[-1]["target_ordinal"]],
    )

    tier_counts = Counter(row["support_tier"] for row in cards)
    check("support_tier_distribution", dict(tier_counts) == EXPECTED_TIERS, dict(tier_counts))
    rank_map = {
        "FULL_OLD_RECIPE_CARRIER": "1",
        "FULLY_TILED_BY_OLD_MULTICOMPONENT_RECIPES": "2",
        "OLD_COMPLETE_RECIPE_FRAGMENT_PLUS_ATOMS": "3",
        "ATOMS_AND_FACTORS_ONLY": "4",
    }
    check(
        "support_ranks_exact",
        all(row["support_rank"] == rank_map[row["support_tier"]] for row in cards),
        Counter(row["support_rank"] for row in cards),
    )

    tier_source_sets = {
        "FULL_OLD_RECIPE_CARRIER": set(exacts),
        "FULLY_TILED_BY_OLD_MULTICOMPONENT_RECIPES": set(tiles),
        "OLD_COMPLETE_RECIPE_FRAGMENT_PLUS_ATOMS": set(fragments),
        "ATOMS_AND_FACTORS_ONLY": set(atoms),
    }
    set_errors: dict[str, list[str]] = {}
    for tier, expected in tier_source_sets.items():
        observed = {row["surface"] for row in cards if row["support_tier"] == tier}
        if observed != expected:
            set_errors[tier] = sorted(observed ^ expected)
    check("all_four_source_decks_join_exactly", not set_errors, set_errors)

    context_errors = []
    for card in cards:
        source = contexts[card["surface"]]
        comparisons = {
            "final_recipe": "final_recipe",
            "target_event_count": "event_count",
            "target_physical_pages": "physical_pages",
            "observed_requirement_modes": "observed_requirement_modes",
            "visible_action_roots": "visible_action_roots",
            "visible_argument_roots": "visible_argument_roots",
            "future_action_contract": "future_action_contract",
            "future_argument_contract": "future_argument_contract",
            "minimum_future_state_for_verbal_clause": "minimum_future_state_for_verbal_clause",
            "neutral_component_reading_de": "neutral_surface_phrase_de",
            "known_contextual_readings_de": "known_contextual_readings_de",
        }
        for target_field, source_field in comparisons.items():
            if card[target_field] != source[source_field]:
                context_errors.append(f"{card['surface']}:{target_field}")
    check("all_gdt540_meaning_and_context_fields_exact", not context_errors, context_errors)

    recipe_errors = [
        row["surface"]
        for row in cards
        if row["final_recipe"] != tiers[row["surface"]]["final_recipe"]
    ]
    check("all_gdt542_final_recipes_exact", not recipe_errors, recipe_errors)

    exact_errors = [
        surface
        for surface, source in exacts.items()
        if card_map[surface]["tier_route_class"] != source["replication_kind"]
        or source["target_recipe"] != card_map[surface]["final_recipe"]
        or source["old_surfaces"] not in card_map[surface]["tier_trace"]
    ]
    check("tier1_exact_profile_replay", not exact_errors, exact_errors)

    tile_errors = [
        surface
        for surface, source in tiles.items()
        if card_map[surface]["tier_route_class"] != source["support_class"]
        or source["complete_old_tiles"] not in card_map[surface]["tier_trace"]
        or source["target_recipe"] != card_map[surface]["final_recipe"]
    ]
    check("tier2_tile_bridge_replay", not tile_errors, tile_errors)

    fragment_errors = [
        surface
        for surface, source in fragments.items()
        if card_map[surface]["tier_route_class"]
        != source["primary_structural_support_class"]
        or source["primary_visible_formula"] not in card_map[surface]["tier_trace"]
        or source["final_recipe"] != card_map[surface]["final_recipe"]
    ]
    check("tier3_fragment_reader_replay", not fragment_errors, fragment_errors)

    atom_errors = [
        surface
        for surface, source in atoms.items()
        if card_map[surface]["tier_route_class"] != source["visible_route_class"]
        or source["visible_trace"] != card_map[surface]["tier_trace"]
        or source["final_recipe"] != card_map[surface]["final_recipe"]
    ]
    check("tier4_atomic_reader_replay", not atom_errors, atom_errors)

    required_fields = [
        "final_recipe",
        "neutral_component_reading_de",
        "known_contextual_readings_de",
        "tier_route_class",
        "tier_trace",
        "tier_evidence",
        "tier_context_relation",
        "tier_caution",
    ]
    missing = [
        f"{row['surface']}:{field}"
        for row in cards
        for field in required_fields
        if not row[field]
    ]
    check("every_card_has_complete_reading_and_support", not missing, missing)
    check(
        "reader_decision_and_guard",
        {row["reader_decision"] for row in cards}
        == {"READ_KNOWN_145_PROSE_WORKING_CARD"}
        and {row["guard"] for row in cards}
        == {"EXACT_145_SURFACE_KEY_ONLY__NO_FUZZY_INHERITANCE_OR_NEW_MEANING"},
        [sorted({row["reader_decision"] for row in cards}), sorted({row["guard"] for row in cards})],
    )
    check(
        "reading_scope_constant",
        {row["reading_scope"] for row in cards}
        == {"GERMAN_WORKING_READING__NOT_PLAINTEXT"},
        sorted({row["reading_scope"] for row in cards}),
    )

    expected_weak_tiles = {
        surface
        for surface, source in tiles.items()
        if source["support_class"] == "COMPLETE_TILES_AND_OLD_SEAMS_ONLY"
    }
    expected_weak_fragments = {
        surface
        for surface, source in fragments.items()
        if source["flag_resolution"].startswith("EXPLICIT_WORKING_DEFAULT")
    }
    expected_weak = expected_weak_tiles | expected_weak_fragments | {"shso"}
    observed_weak = {
        row["surface"] for row in cards if row["weak_queue_candidate"] == "YES"
    }
    check("weak_queue_inventory_exact", observed_weak == expected_weak, sorted(observed_weak ^ expected_weak))
    check(
        "weak_queue_partition_10_12_1",
        (len(expected_weak_tiles), len(expected_weak_fragments), int("shso" in observed_weak))
        == (10, 12, 1),
        [len(expected_weak_tiles), len(expected_weak_fragments), int("shso" in observed_weak)],
    )
    check("weak_queue_artifact_count", len(queue) == 23, len(queue))
    check(
        "weak_queue_artifact_surface_set",
        {row["surface"] for row in queue} == expected_weak,
        sorted({row["surface"] for row in queue} ^ expected_weak),
    )
    check(
        "all_nonweak_cards_named",
        sum(row["weak_queue_candidate"] == "NO" for row in cards) == 122,
        sum(row["weak_queue_candidate"] == "NO" for row in cards),
    )

    mode_counts = Counter(row["observed_requirement_modes"] for row in cards)
    expected_modes = {
        "SELF_CONTAINED": 88,
        "REQUIRES_ACTIVE_ACTION": 5,
        "REQUIRES_ACTIVE_ARGUMENT": 40,
        "REQUIRES_ACTIVE_ACTION_AND_ARGUMENT": 11,
        "SELF_CONTAINED|REQUIRES_ACTIVE_ARGUMENT": 1,
    }
    check("context_mode_distribution", dict(mode_counts) == expected_modes, dict(mode_counts))

    summary_rows = read_tsv(SUMMARY)
    summary = {row["metric"]: row["value"] for row in summary_rows}
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    expected_result: dict[str, Any] = {
        "active_action_and_argument_surface_count": 11,
        "active_action_surface_count": 5,
        "active_argument_surface_count": 40,
        "atomic_factor_reader_count": 24,
        "complete_context_reading_count": 145,
        "complete_neutral_reading_count": 145,
        "exact_old_recipe_count": 11,
        "fragment_reader_count": 81,
        "full_tile_count": 29,
        "multi_mode_surface_count": 1,
        "new_pages": 0,
        "nonweak_card_count": 122,
        "recipe_changes": 0,
        "root_meaning_changes": 0,
        "self_contained_only_surface_count": 88,
        "status": EXPECTED_STATUS,
        "target_surface_count": 145,
        "tier_1_count": 11,
        "tier_2_count": 29,
        "tier_3_count": 81,
        "tier_4_count": 24,
        "unique_surface_count": 145,
        "unknown_surface_policy": "STOP_UNKNOWN_145_PROSE_SURFACE",
        "weak_atomic_pair_default_count": 1,
        "weak_fragment_default_count": 12,
        "weak_queue_count": 23,
        "weak_tile_default_count": 10,
    }
    check("result_exact", result == expected_result, result)
    check(
        "summary_replays_result",
        summary == {key: str(value) for key, value in expected_result.items()},
        summary,
    )

    book = BOOK.read_text(encoding="utf-8")
    check("book_status", EXPECTED_STATUS in book, EXPECTED_STATUS)
    check("book_has_all_145_cards", book.count("\n### `") == 145, book.count("\n### `"))
    check("book_names_weak_queue", "**23** Karten" in book, "**23** Karten")

    tier_probes = ["dalol", "choraly", "aiicthy", "shso"]
    probe_details = []
    probe_ok = True
    for surface in tier_probes:
        probe = run_cli("--surface", surface, "--format", "json")
        try:
            payload = json.loads(probe.stdout)
        except json.JSONDecodeError:
            payload = {}
        ok = (
            probe.returncode == 0
            and payload.get("card", {}).get("surface") == surface
            and payload.get("card", {}).get("support_tier") == card_map[surface]["support_tier"]
        )
        probe_ok &= ok
        probe_details.append([surface, probe.returncode, payload.get("card", {}).get("support_tier")])
    check("cli_one_probe_per_tier", probe_ok, probe_details)

    unknown = run_cli("--surface", "unknown_prose_card", "--format", "json")
    unknown_payload = json.loads(unknown.stdout)
    check(
        "unknown_cli_stops",
        unknown.returncode == 2
        and unknown_payload.get("status") == "STOP_UNKNOWN_145_PROSE_SURFACE",
        {"returncode": unknown.returncode, "payload": unknown_payload},
    )

    listed = run_cli("--list-surfaces")
    listed_surfaces = listed.stdout.splitlines()
    check(
        "cli_lists_exact_145",
        listed.returncode == 0
        and listed_surfaces == [row["surface"] for row in cards],
        len(listed_surfaces),
    )

    empty_context = run_cli("--surface", "dalol", "--format", "json")
    empty_payload = json.loads(empty_context.stdout)
    filled_context = run_cli(
        "--surface",
        "dalol",
        "--active-action",
        "CH",
        "--active-argument",
        "Y",
        "--format",
        "json",
    )
    filled_payload = json.loads(filled_context.stdout)
    check(
        "cli_context_state_switch",
        empty_payload["context_resolution"]["context_status"]
        == "NEUTRAL_DEFAULT_ONLY__MISSING_ACTIVE_ACTION"
        and filled_payload["context_resolution"]["context_status"]
        == "READY_FOR_CONTEXTUAL_WORKING_READING"
        and filled_payload["context_resolution"]["resolved_action_root"] == "CH"
        and filled_payload["context_resolution"]["resolved_argument_root"] == "Y",
        [empty_payload["context_resolution"], filled_payload["context_resolution"]],
    )
    visible_context = run_cli("--surface", "shso", "--format", "json")
    visible_payload = json.loads(visible_context.stdout)
    check(
        "cli_visible_action_precedes_state",
        visible_payload["context_resolution"]["resolved_action_root"] == "S"
        and visible_payload["context_resolution"]["action_source"] == "VISIBLE_SURFACE",
        visible_payload["context_resolution"],
    )

    deterministic_paths = [READER, QUEUE, SUMMARY, BOOK, RESULT]
    before = {path.name: sha256(path) for path in deterministic_paths}
    rerun = subprocess.run(
        [sys.executable, str(RUN)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    after = {path.name: sha256(path) for path in deterministic_paths}
    check("generator_rerun_exit", rerun.returncode == 0, rerun.stdout + rerun.stderr)
    check("generator_byte_determinism", before == after, after)

    passed = sum(item["passed"] for item in checks)
    payload = {
        "status": "PASS" if passed == len(checks) else "FAIL",
        "check_count": len(checks),
        "passed_count": passed,
        "failed_count": len(checks) - passed,
        "checks": checks,
    }
    VALIDATION.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=False))
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
