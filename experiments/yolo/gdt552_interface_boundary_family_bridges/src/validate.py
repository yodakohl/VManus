#!/usr/bin/env python3
"""Independent validation for GDT552 interface boundary/family bridges."""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
EXP = ROOT / "experiments/yolo/gdt552_interface_boundary_family_bridges"
ART = EXP / "artifacts"
RUN = EXP / "src/run.py"

G407 = ROOT / "experiments/yolo/gdt407_unified_twenty_six_page_workshop_edition/artifacts"
G444 = ROOT / "experiments/yolo/gdt444_focus_separated_action_pair_atlas/artifacts"
G526 = ROOT / "experiments/yolo/gdt526_cha_intermediate_stem_extension/artifacts"
G539 = ROOT / "experiments/yolo/gdt539_four_page_contextual_statement_edition/artifacts"
G549 = ROOT / "experiments/yolo/gdt549_default_queue_visible_peer_bridges/artifacts"
G551 = ROOT / "experiments/yolo/gdt551_context_contract_normalization/artifacts"

OLD_IN = G407 / "gdt407_4576_running_event_edition.tsv"
FOCUS_IN = G444 / "gdt444_28_observed_separated_pair_occurrences.tsv"
CHA_IN = G526 / "gdt526_cha_route_atlas.tsv"
CURRENT_IN = G539 / "gdt539_546_contextual_prose_events.tsv"
VISIBLE_IN = G549 / "gdt549_23_exact_visible_default_cards.tsv"
RESIDUAL_IN = G551 / "gdt551_5_residual_interface_queue.tsv"

CENSUS = ART / "gdt552_5_interface_pair_census.tsv"
GAPS = ART / "gdt552_11_old_one_gap_witnesses.tsv"
BOUNDARIES = ART / "gdt552_76_old_card_boundary_witnesses.tsv"
CURRENT = ART / "gdt552_10_current_reinforcement_witnesses.tsv"
BRIDGES = ART / "gdt552_5_selected_interface_bridges.tsv"
QUEUE = ART / "gdt552_support_queue_status.tsv"
SUMMARY = ART / "gdt552_interface_bridge_summary.tsv"
BOOK = ART / "GDT552_INTERFACE_BRIDGE_BOOK.md"
RESULT = ART / "gdt552_result.json"
VALIDATION = ART / "gdt552_validation.json"

STATUS = "PASS_FIVE_BOUNDED_INTERFACE_BRIDGES__ZERO_SUPPORT_RESTS"
META = {
    "aiicthy": ("AIIN", "CH", "aii", "ch"),
    "chap": ("A_ADDR", "P", "a", "p"),
    "ofaram": ("AR", "AM_ADDR", "ar", "am"),
    "rotaiin": ("R", "OT", "r", "ot"),
    "shso": ("SH", "S", "sh", "s"),
}
EXPECTED_GAPS = {"aiicthy": 0, "chap": 2, "ofaram": 1, "rotaiin": 1, "shso": 7}
EXPECTED_BOUNDARIES = {"aiicthy": 70, "chap": 0, "ofaram": 4, "rotaiin": 1, "shso": 1}
EXPECTED_VISIBLE_BOUNDARIES = {"aiicthy": 0, "chap": 0, "ofaram": 4, "rotaiin": 1, "shso": 1}
EXPECTED_BRIDGE_CLASS = {
    "aiicthy": "EXACT_TARGET_TILES_AT_OLD_CARD_BOUNDARY",
    "chap": "LEARNED_CHA_SUFFIX_PLUS_TWO_ONE_GAP_CARRIERS",
    "ofaram": "VISIBLE_OLD_CARD_BOUNDARY_PLUS_ONE_GAP_CARRIER",
    "rotaiin": "VISIBLE_OLD_CARD_BOUNDARY_PLUS_ONE_GAP_CARRIER",
    "shso": "VISIBLE_OLD_CARD_BOUNDARY_PLUS_RECURRENT_SEPARATED_CHAIN",
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def keyed(rows: list[dict[str, str]], field: str) -> dict[str, dict[str, str]]:
    result = {row[field]: row for row in rows}
    if len(result) != len(rows):
        raise RuntimeError(f"Duplicate {field}")
    return result


def atoms(recipe: str) -> tuple[str, ...]:
    return tuple(recipe.split("+"))


def direct_event_ids(
    rows: list[dict[str, str]], recipe_field: str, event_field: str, excluded: set[str]
) -> dict[str, set[str]]:
    result: dict[str, set[str]] = defaultdict(set)
    for row in rows:
        if row["surface"] in excluded:
            continue
        pairs = set(zip(atoms(row[recipe_field]), atoms(row[recipe_field])[1:]))
        for surface, (left, right, _, _) in META.items():
            if (left, right) in pairs:
                result[surface].add(row[event_field])
    return result


def gap_keys(
    rows: list[dict[str, str]], recipe_field: str, event_field: str, excluded: set[str]
) -> dict[str, set[tuple[str, int, str]]]:
    result: dict[str, set[tuple[str, int, str]]] = defaultdict(set)
    for row in rows:
        if row["surface"] in excluded:
            continue
        recipe = atoms(row[recipe_field])
        for surface, (left, right, _, _) in META.items():
            for start in range(len(recipe) - 2):
                if recipe[start] == left and recipe[start + 2] == right:
                    result[surface].add((row[event_field], start + 1, recipe[start + 1]))
    return result


def boundary_keys(
    rows: list[dict[str, str]],
    recipe_field: str,
    event_field: str,
    statement_field: str,
    order_field: str,
    excluded: set[str],
) -> dict[str, set[tuple[str, str, bool, bool]]]:
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[row[statement_field]].append(row)
    result: dict[str, set[tuple[str, str, bool, bool]]] = defaultdict(set)
    for events in grouped.values():
        ordered = sorted(events, key=lambda row: int(row[order_field]))
        for a, b in zip(ordered, ordered[1:]):
            if a["surface"] in excluded or b["surface"] in excluded:
                continue
            ar = atoms(a[recipe_field])
            br = atoms(b[recipe_field])
            for surface, (left, right, visible_left, visible_right) in META.items():
                if ar[-1] != left or br[0] != right:
                    continue
                visible = a["surface"].endswith(visible_left) and b["surface"].startswith(visible_right)
                tiles = surface == "aiicthy" and a[recipe_field] == "AIIN" and b[recipe_field] == "CH+T+Y"
                result[surface].add((a[event_field], b[event_field], visible, tiles))
    return result


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    checks: list[dict[str, Any]] = []

    def check(name: str, passed: bool, detail: Any) -> None:
        checks.append({"check": name, "passed": bool(passed), "detail": detail})

    old_rows = read_tsv(OLD_IN)
    focus_rows = read_tsv(FOCUS_IN)
    cha_rows = read_tsv(CHA_IN)
    current_rows = read_tsv(CURRENT_IN)
    visible_rows = read_tsv(VISIBLE_IN)
    residual_rows = read_tsv(RESIDUAL_IN)
    check("source_row_counts", [len(old_rows), len(focus_rows), len(current_rows), len(visible_rows), len(residual_rows)] == [4576, 28, 546, 23, 5], [len(old_rows), len(focus_rows), len(current_rows), len(visible_rows), len(residual_rows)])
    residual = keyed(residual_rows, "surface")
    visible = keyed(visible_rows, "surface")
    check("five_target_set_exact", set(residual) == set(META), sorted(residual))
    check("five_pair_labels_exact", all(residual[s]["residual_detail"] == f"{META[s][0]}>{META[s][1]}" for s in META), {s: residual[s]["residual_detail"] for s in META})

    old_direct = direct_event_ids(old_rows, "component_recipe", "global_running_event_id", set())
    current_direct = direct_event_ids(current_rows, "final_context_recipe", "event_id", set(META))
    check("zero_old_direct_target_pair_events", all(not old_direct[s] for s in META), {s: sorted(old_direct[s]) for s in META})
    check("zero_current_non_target_direct_pair_events", all(not current_direct[s] for s in META), {s: sorted(current_direct[s]) for s in META})

    expected_gaps = gap_keys(old_rows, "component_recipe", "global_running_event_id", set())
    check("old_gap_count_profile", {s: len(expected_gaps[s]) for s in META} == EXPECTED_GAPS, {s: len(expected_gaps[s]) for s in META})
    gap_rows = read_tsv(GAPS)
    output_gaps: dict[str, set[tuple[str, int, str]]] = defaultdict(set)
    for row in gap_rows:
        output_gaps[row["target_surface"]].add((row["event_id"], int(row["pair_start_atom_ordinal"]), row["separator_atom"]))
    check("eleven_old_gap_rows", len(gap_rows) == 11, len(gap_rows))
    check("old_gap_witness_set_exact", all(output_gaps[s] == expected_gaps[s] for s in META), {s: sorted(output_gaps[s] ^ expected_gaps[s]) for s in META if output_gaps[s] != expected_gaps[s]})
    focus_shs = {row["event_id"] for row in focus_rows if row["direct_red_pair"] == "SH>S"}
    output_focus = {row["event_id"] for row in gap_rows if row["gdt444_observed_focus_witness"] == "YES"}
    check("five_gdt444_shs_witnesses_exact", len(focus_shs) == 5 and output_focus == focus_shs, sorted(output_focus ^ focus_shs))

    expected_boundaries = boundary_keys(old_rows, "component_recipe", "global_running_event_id", "source_statement_id", "source_order", set())
    check("old_boundary_count_profile", {s: len(expected_boundaries[s]) for s in META} == EXPECTED_BOUNDARIES, {s: len(expected_boundaries[s]) for s in META})
    boundary_rows = read_tsv(BOUNDARIES)
    output_boundaries: dict[str, set[tuple[str, str, bool, bool]]] = defaultdict(set)
    for row in boundary_rows:
        output_boundaries[row["target_surface"]].add((row["left_event_id"], row["right_event_id"], row["visible_target_seam_exact"] == "YES", row["exact_aiicthy_target_tile_path"] == "YES"))
    check("seventy_six_old_boundary_rows", len(boundary_rows) == 76, len(boundary_rows))
    check("old_boundary_witness_set_exact", all(output_boundaries[s] == expected_boundaries[s] for s in META), {s: len(output_boundaries[s] ^ expected_boundaries[s]) for s in META if output_boundaries[s] != expected_boundaries[s]})
    visible_profile = {s: sum(item[2] for item in expected_boundaries[s]) for s in META}
    check("six_visible_seam_boundaries_profile", visible_profile == EXPECTED_VISIBLE_BOUNDARIES, visible_profile)
    tile_paths = [(s, item) for s in META for item in expected_boundaries[s] if item[3]]
    check("one_exact_aiicthy_tile_boundary", len(tile_paths) == 1 and tile_paths[0][0] == "aiicthy", tile_paths)

    current_gaps = gap_keys(current_rows, "final_context_recipe", "event_id", set(META))
    current_boundaries = boundary_keys(current_rows, "final_context_recipe", "event_id", "statement_id", "card_ordinal_in_statement", set(META))
    check("current_gap_profile", {s: len(current_gaps[s]) for s in META} == {"aiicthy": 0, "chap": 0, "ofaram": 0, "rotaiin": 0, "shso": 2}, {s: len(current_gaps[s]) for s in META})
    check("current_boundary_profile", {s: len(current_boundaries[s]) for s in META} == {"aiicthy": 8, "chap": 0, "ofaram": 0, "rotaiin": 0, "shso": 0}, {s: len(current_boundaries[s]) for s in META})
    current_output = read_tsv(CURRENT)
    output_current_ids = {row["event_or_pair_id"] for row in current_output}
    expected_current_ids = {key[0] for values in current_gaps.values() for key in values} | {f"{key[0]}>{key[1]}" for values in current_boundaries.values() for key in values}
    check("ten_current_reinforcement_rows", len(current_output) == 10, len(current_output))
    check("current_reinforcement_set_exact", output_current_ids == expected_current_ids, sorted(output_current_ids ^ expected_current_ids))

    chap = [row for row in cha_rows if row["surface"] == "chap" and row["candidate_recipe"] == "CH+A_ADDR+P"]
    chap_ok = len(chap) == 1 and chap[0]["candidate_is_truth"] == "YES" and chap[0]["gdt526_rank"] == "1" and chap[0]["base_surface"] == "cha" and chap[0]["base_recipe"] == "CH+A_ADDR" and chap[0]["suffix"] == "p" and chap[0]["atom_insert"] == "P" and chap[0]["signature_support"] == "2" and chap[0]["visible_condition_total"] == "2"
    check("gdt526_chap_family_license_exact", chap_ok, chap)

    census_rows = read_tsv(CENSUS)
    census = keyed(census_rows, "surface")
    check("five_census_rows", set(census) == set(META), sorted(census))
    census_errors = []
    for surface in META:
        row = census[surface]
        if (
            int(row["old_direct_event_count"]) != 0
            or int(row["old_one_gap_witness_count"]) != EXPECTED_GAPS[surface]
            or int(row["old_card_boundary_witness_count"]) != EXPECTED_BOUNDARIES[surface]
            or int(row["old_visible_seam_boundary_count"]) != EXPECTED_VISIBLE_BOUNDARIES[surface]
            or row["finite_gate_pass"] != "YES"
        ):
            census_errors.append(surface)
    check("census_counts_and_finite_gates_exact", not census_errors, census_errors)

    bridge_rows = read_tsv(BRIDGES)
    bridges = keyed(bridge_rows, "surface")
    check("five_selected_bridges", set(bridges) == set(META), sorted(bridges))
    bridge_errors = []
    for surface, row in bridges.items():
        source = visible[surface]
        if (
            row["final_recipe"] != source["final_recipe"]
            or row["selected_visible_trace"] != source["selected_visible_trace"]
            or row["exact_surface_reconstruction"] != "YES"
            or row["exact_recipe_reconstruction"] != "YES"
            or row["neutral_component_reading_de"] != source["neutral_component_reading_de"]
            or row["known_contextual_readings_de"] != source["known_contextual_readings_de"]
            or row["bridge_class"] != EXPECTED_BRIDGE_CLASS[surface]
            or row["direct_old_within_card_pair_status"] != "ABSENT_AND_RETAINED_AS_ABSENT"
            or not row["promotion_status"].startswith("PROMOTED_")
        ):
            bridge_errors.append(surface)
    check("bridge_routes_meanings_classes_and_guards_exact", not bridge_errors, bridge_errors)
    check("four_distinct_bridge_classes", len({row["bridge_class"] for row in bridge_rows}) == 4, Counter(row["bridge_class"] for row in bridge_rows))

    queue_rows = read_tsv(QUEUE)
    check("single_queue_status_row", len(queue_rows) == 1, len(queue_rows))
    check("support_queue_empty", queue_rows[0]["source_support_rest_count"] == "5" and queue_rows[0]["promoted_interface_card_count"] == "5" and queue_rows[0]["residual_support_rest_count"] == "0" and queue_rows[0]["residual_surfaces"] == "NONE", queue_rows[0])

    result = json.loads(RESULT.read_text(encoding="utf-8"))
    expected_result = {
        "status": STATUS,
        "source_interface_card_count": 5,
        "old_direct_target_pair_event_count": 0,
        "old_one_gap_witness_count": 11,
        "old_one_gap_supported_target_count": 4,
        "old_statement_boundary_witness_count": 76,
        "old_statement_boundary_supported_target_count": 4,
        "old_visible_target_seam_boundary_count": 6,
        "old_exact_aiicthy_tile_path_count": 1,
        "gdt444_shs_focus_witness_count": 5,
        "gdt526_chap_family_license_count": 1,
        "current_non_target_reinforcement_count": 10,
        "finite_gate_pass_count": 5,
        "selected_bridge_class_count": 4,
        "promoted_interface_card_count": 5,
        "promoted_exact_visible_route_count": 5,
        "promoted_complete_neutral_meaning_count": 5,
        "promoted_complete_context_meaning_count": 5,
        "residual_support_rest_count": 0,
        "new_pages": 0,
        "recipe_changes": 0,
        "root_meaning_changes": 0,
    }
    check("result_metrics_exact", result == expected_result, {key: result.get(key) for key in expected_result if result.get(key) != expected_result[key]})
    summary = {row["metric"]: row["value"] for row in read_tsv(SUMMARY)}
    check("summary_matches_result", all(summary.get(key) == str(value) for key, value in result.items()), len(summary))
    book = BOOK.read_text(encoding="utf-8")
    check("book_names_all_five_targets", all(f"`{surface}`" in book for surface in META), len(book))
    check("book_preserves_no_universal_pair_rule", "nicht zu einem freien Wörterbuchgesetz" in book, len(book))

    deterministic = [CENSUS, GAPS, BOUNDARIES, CURRENT, BRIDGES, QUEUE, SUMMARY, BOOK, RESULT]
    before = {path.name: sha256(path) for path in deterministic}
    replay = subprocess.run([sys.executable, str(RUN)], cwd=ROOT, text=True, capture_output=True, check=False)
    after = {path.name: sha256(path) for path in deterministic}
    check("deterministic_replay_exit", replay.returncode == 0, replay.stderr[-2000:])
    check("deterministic_artifact_hashes", before == after, {name: [before[name], after[name]] for name in before if before[name] != after[name]})

    passed = all(item["passed"] for item in checks)
    payload = {
        "status": "PASS" if passed else "FAIL",
        "check_count": len(checks),
        "passed_count": sum(item["passed"] for item in checks),
        "failed_count": sum(not item["passed"] for item in checks),
        "checks": checks,
        "input_sha256": {path.name: sha256(path) for path in [OLD_IN, FOCUS_IN, CHA_IN, CURRENT_IN, VISIBLE_IN, RESIDUAL_IN]},
        "artifact_sha256": {path.name: sha256(path) for path in deterministic},
    }
    VALIDATION.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
