#!/usr/bin/env python3
"""Independent validation for GDT550 recurrent sequence-frame bridges."""

from __future__ import annotations

import csv
import hashlib
import itertools
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
EXP = ROOT / "experiments/yolo/gdt550_recurrent_sequence_frame_bridges"
ART = EXP / "artifacts"
RUN = EXP / "src/run.py"
G519 = ROOT / "experiments/yolo/gdt519_visible_stem_anchor_transducer/artifacts"
G548 = ROOT / "experiments/yolo/gdt548_unified_145_prose_reader/artifacts"
G549 = ROOT / "experiments/yolo/gdt549_default_queue_visible_peer_bridges/artifacts"

ALIAS_IN = G519 / "gdt519_anchor_alias_lexicon.tsv"
READER_IN = G548 / "gdt548_145_unified_prose_reader.tsv"
VISIBLE_IN = G549 / "gdt549_23_exact_visible_default_cards.tsv"
RESIDUAL_IN = G549 / "gdt549_19_residual_support_queue.tsv"

CANDIDATES = ART / "gdt550_23_candidate_recurrent_frames.tsv"
SOLUTIONS = ART / "gdt550_6_minimum_five_frame_covers.tsv"
SELECTED = ART / "gdt550_5_selected_bridge_frames.tsv"
OCCURRENCES = ART / "gdt550_31_selected_frame_occurrences.tsv"
PROMOTED = ART / "gdt550_10_promoted_sequence_cards.tsv"
RESIDUAL = ART / "gdt550_9_residual_support_queue.tsv"
SUMMARY = ART / "gdt550_recurrent_frame_summary.tsv"
BOOK = ART / "GDT550_RECURRENT_SEQUENCE_FRAME_BOOK.md"
RESULT = ART / "gdt550_result.json"
VALIDATION = ART / "gdt550_validation.json"

STATUS = "PASS_FIVE_RECURRENT_FRAMES_BRIDGE_ALL_10_SEQUENCE_DEFAULTS__NINE_SUPPORT_RESTS"
EXPECTED_SELECTED = {
    ("chor", "CH+OR"),
    ("ko", "K+O"),
    ("she", "SH+E"),
    ("shy", "SH+Y"),
    ("ches", "CH+E+S"),
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def keyed(rows: list[dict[str, str]], field: str) -> dict[str, dict[str, str]]:
    return {row[field]: row for row in rows}


def modes(row: dict[str, str]) -> set[str]:
    return set(row["observed_requirement_modes"].split("|"))


def enumerate_covers(
    surface: str,
    recipe: tuple[str, ...],
    options: dict[tuple[str, ...], set[str]],
) -> set[tuple[tuple[str, tuple[str, ...]], ...]]:
    states: dict[
        tuple[int, int], set[tuple[tuple[str, tuple[str, ...]], ...]]
    ] = {(0, 0): {tuple()}}
    for atom_index in range(len(recipe) + 1):
        for char_index in range(len(surface) + 1):
            for path in states.get((atom_index, char_index), set()):
                for width in range(1, 4):
                    sequence = recipe[atom_index : atom_index + width]
                    if len(sequence) != width:
                        continue
                    for alias in options.get(sequence, set()):
                        if surface.startswith(alias, char_index):
                            destination = atom_index + width, char_index + len(alias)
                            states.setdefault(destination, set()).add(
                                path + ((alias, sequence),)
                            )
    return states.get((len(recipe), len(surface)), set())


def frame_occurrences(
    reader_rows: list[dict[str, str]],
    options: dict[tuple[str, ...], set[str]],
) -> tuple[
    dict[str, set[tuple[tuple[str, tuple[str, ...]], ...]]],
    dict[tuple[str, str], set[str]],
]:
    paths_by_surface = {}
    occurrences: dict[tuple[str, str], set[str]] = defaultdict(set)
    for row in reader_rows:
        paths = enumerate_covers(
            row["surface"], tuple(row["final_recipe"].split("+")), options
        )
        paths_by_surface[row["surface"]] = paths
        for path in paths:
            for start in range(len(path)):
                for end in range(start + 1, min(len(path), start + 3) + 1):
                    chain = path[start:end]
                    visible = "".join(part[0] for part in chain)
                    atoms = sum((part[1] for part in chain), tuple())
                    if len(visible) >= 2 and len(atoms) >= 2:
                        occurrences[(visible, "+".join(atoms))].add(row["surface"])
    return paths_by_surface, occurrences


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    checks: list[dict[str, Any]] = []

    def check(name: str, passed: bool, detail: Any) -> None:
        checks.append({"check": name, "passed": bool(passed), "detail": detail})

    reader_rows = read_tsv(READER_IN)
    readers = keyed(reader_rows, "surface")
    visible = keyed(read_tsv(VISIBLE_IN), "surface")
    source_residual = read_tsv(RESIDUAL_IN)
    targets = {
        row["surface"]
        for row in source_residual
        if row["residual_dimension"] == "HIGHER_ORDER_SEQUENCE_CONTEXT"
    }
    check("source_sequence_target_count", len(targets) == 10, sorted(targets))

    options: dict[tuple[str, ...], set[str]] = defaultdict(set)
    for row in read_tsv(ALIAS_IN):
        if row["model"] == "FULL_OLD26":
            options[tuple(row["atom_sequence"].split("+"))].add(row["surface_alias"])
    paths_by_surface, all_occurrences = frame_occurrences(reader_rows, options)
    check(
        "all_ten_targets_have_old_exact_cover",
        all(paths_by_surface[surface] for surface in targets),
        {surface: len(paths_by_surface[surface]) for surface in sorted(targets)},
    )

    expected_candidates: dict[tuple[str, str], dict[str, Any]] = {}
    for frame, surfaces in all_occurrences.items():
        target_hits = surfaces & targets
        strong_peers = {
            surface
            for surface in surfaces - targets
            if readers[surface]["weak_queue_candidate"] == "NO"
        }
        if not target_hits or not strong_peers:
            continue
        peer_map = {
            target: {
                peer
                for peer in strong_peers
                if modes(readers[target]) & modes(readers[peer])
            }
            for target in target_hits
        }
        expected_candidates[frame] = {
            "targets": target_hits,
            "peers": strong_peers,
            "peer_map": peer_map,
            "compatible": all(peer_map.values()),
        }

    candidate_rows = read_tsv(CANDIDATES)
    candidate_map = {
        (row["visible_frame"], row["recipe_frame"]): row for row in candidate_rows
    }
    check("candidate_frame_count", len(candidate_rows) == 23, len(candidate_rows))
    check(
        "candidate_frame_set_exact",
        set(candidate_map) == set(expected_candidates),
        sorted(set(candidate_map) ^ set(expected_candidates)),
    )
    candidate_errors = []
    for frame, expected in expected_candidates.items():
        row = candidate_map[frame]
        if (
            int(row["sequence_target_count"]) != len(expected["targets"])
            or set(row["sequence_targets"].split("|")) != expected["targets"]
            or int(row["strong_peer_count"]) != len(expected["peers"])
            or set(row["strong_peers"].split("|")) != expected["peers"]
            or int(row["target_mode_coverage_count"])
            != sum(bool(peers) for peers in expected["peer_map"].values())
            or int(row["same_mode_peer_contact_count"])
            != sum(len(peers) for peers in expected["peer_map"].values())
            or (row["all_targets_have_same_mode_peer"] == "YES")
            != expected["compatible"]
        ):
            candidate_errors.append(frame)
    check("all_candidate_counts_and_modes_replay", not candidate_errors, candidate_errors)
    check(
        "context_compatible_candidate_count",
        sum(expected["compatible"] for expected in expected_candidates.values()) == 20,
        sum(expected["compatible"] for expected in expected_candidates.values()),
    )

    eligible = [frame for frame, value in expected_candidates.items() if value["compatible"]]
    minimum_solutions: list[tuple[tuple[str, str], ...]] = []
    for width in range(1, len(eligible) + 1):
        minimum_solutions = [
            combination
            for combination in itertools.combinations(eligible, width)
            if set().union(
                *(expected_candidates[frame]["targets"] for frame in combination)
            )
            == targets
        ]
        if minimum_solutions:
            break
    check(
        "minimum_cover_is_five_with_six_solutions",
        len(minimum_solutions) == 6 and len(minimum_solutions[0]) == 5,
        [len(minimum_solutions), len(minimum_solutions[0]) if minimum_solutions else 0],
    )

    solution_rows = read_tsv(SOLUTIONS)
    output_solution_sets = {
        frozenset(
            (part.split("→", 1)[0], part.split("→", 1)[1])
            for part in row["frame_traces"].split(" | ")
        )
        for row in solution_rows
    }
    expected_solution_sets = {frozenset(solution) for solution in minimum_solutions}
    check("all_six_minimum_solutions_exact", len(solution_rows) == 6 and output_solution_sets == expected_solution_sets, len(output_solution_sets))
    selected_solution_rows = [row for row in solution_rows if row["selected_solution"] == "YES"]
    check(
        "one_selected_solution",
        len(selected_solution_rows) == 1
        and int(selected_solution_rows[0]["total_mapped_atom_count"]) == 11,
        selected_solution_rows,
    )

    selected_rows = read_tsv(SELECTED)
    selected_map = {
        (row["visible_frame"], row["recipe_frame"]): row for row in selected_rows
    }
    check("selected_frame_count", len(selected_rows) == 5, len(selected_rows))
    check("selected_frame_set_exact", set(selected_map) == EXPECTED_SELECTED, sorted(set(selected_map) ^ EXPECTED_SELECTED))
    check(
        "selected_frames_all_context_compatible",
        all(expected_candidates[frame]["compatible"] for frame in EXPECTED_SELECTED),
        {
            str(frame): expected_candidates[frame]["compatible"]
            for frame in sorted(EXPECTED_SELECTED)
        },
    )
    selected_target_union = set().union(
        *(expected_candidates[frame]["targets"] for frame in EXPECTED_SELECTED)
    )
    selected_peer_union = set().union(
        *(expected_candidates[frame]["peers"] for frame in EXPECTED_SELECTED)
    )
    selected_contacts = sum(
        sum(len(peers) for peers in expected_candidates[frame]["peer_map"].values())
        for frame in EXPECTED_SELECTED
    )
    check("selected_frames_cover_all_ten", selected_target_union == targets, sorted(selected_target_union))
    check("selected_strong_peer_union_count", len(selected_peer_union) == 21, sorted(selected_peer_union))
    check("selected_same_mode_contact_count", selected_contacts == 27, selected_contacts)

    expected_frame_counts = {
        ("chor", "CH+OR"): (1, 2, 2),
        ("ko", "K+O"): (2, 2, 4),
        ("she", "SH+E"): (4, 14, 16),
        ("shy", "SH+Y"): (2, 2, 4),
        ("ches", "CH+E+S"): (1, 1, 1),
    }
    check(
        "selected_frame_counts_exact",
        all(
            (
                int(selected_map[frame]["sequence_target_count"]),
                int(selected_map[frame]["strong_peer_count"]),
                int(selected_map[frame]["same_mode_peer_contact_count"]),
            )
            == counts
            for frame, counts in expected_frame_counts.items()
        ),
        {
            str(frame): [
                selected_map[frame]["sequence_target_count"],
                selected_map[frame]["strong_peer_count"],
                selected_map[frame]["same_mode_peer_contact_count"],
            ]
            for frame in sorted(EXPECTED_SELECTED)
        },
    )

    occurrence_rows = read_tsv(OCCURRENCES)
    check("selected_occurrence_count", len(occurrence_rows) == 31, len(occurrence_rows))
    occurrence_pairs = {(row["visible_frame"], row["recipe_frame"], row["surface"]) for row in occurrence_rows}
    expected_occurrence_pairs = {
        (frame[0], frame[1], surface)
        for frame in EXPECTED_SELECTED
        for surface in expected_candidates[frame]["targets"] | expected_candidates[frame]["peers"]
    }
    check("selected_occurrence_set_exact", occurrence_pairs == expected_occurrence_pairs, sorted(occurrence_pairs ^ expected_occurrence_pairs))
    occurrence_role_errors = [
        row["surface"]
        for row in occurrence_rows
        if row["occurrence_role"]
        != ("SEQUENCE_TARGET" if row["surface"] in targets else "STRONG_PEER")
    ]
    check("occurrence_roles_exact", not occurrence_role_errors, occurrence_role_errors)

    promoted_rows = read_tsv(PROMOTED)
    promoted_map = keyed(promoted_rows, "surface")
    check("promoted_sequence_count", len(promoted_rows) == 10, len(promoted_rows))
    check("promoted_sequence_set_exact", set(promoted_map) == targets, sorted(set(promoted_map) ^ targets))
    promotion_errors = []
    for surface, row in promoted_map.items():
        frame = row["visible_frame"], row["recipe_frame"]
        expected_peers = expected_candidates[frame]["peer_map"][surface]
        if (
            frame not in EXPECTED_SELECTED
            or int(row["same_mode_peer_count"]) != len(expected_peers)
            or set(row["same_mode_peer_surfaces"].split("|")) != expected_peers
            or row["exact_visible_route"] != visible[surface]["selected_visible_trace"]
            or row["neutral_component_reading_de"]
            != readers[surface]["neutral_component_reading_de"]
            or row["known_contextual_readings_de"]
            != readers[surface]["known_contextual_readings_de"]
        ):
            promotion_errors.append(surface)
    check("all_ten_promotions_replay", not promotion_errors, promotion_errors)
    check(
        "all_promotions_keep_old_tile_evidence",
        all("old_seams=" in row["old_tile_and_seam_evidence"] for row in promoted_rows),
        [row["surface"] for row in promoted_rows if "old_seams=" not in row["old_tile_and_seam_evidence"]],
    )

    residual_rows = read_tsv(RESIDUAL)
    expected_residual = {
        row["surface"]
        for row in source_residual
        if row["residual_dimension"] != "HIGHER_ORDER_SEQUENCE_CONTEXT"
    }
    check("post_bridge_residual_count", len(residual_rows) == 9, len(residual_rows))
    check("post_bridge_residual_set_exact", {row["surface"] for row in residual_rows} == expected_residual, sorted({row["surface"] for row in residual_rows} ^ expected_residual))
    residual_distribution = Counter(row["residual_dimension"] for row in residual_rows)
    check("post_bridge_residual_distribution_4_5", residual_distribution == {"ANCHOR_CONTEXT": 4, "DIRECT_INTERFACE": 5}, dict(residual_distribution))
    check("promoted_and_residual_are_disjoint", targets.isdisjoint(expected_residual), sorted(targets & expected_residual))

    expected_result: dict[str, Any] = {
        "all_target_modes_peer_compatible_frame_count": 20,
        "candidate_recurrent_frame_count": 23,
        "complete_context_meaning_count": 10,
        "complete_neutral_meaning_count": 10,
        "minimum_frame_cover_size": 5,
        "minimum_frame_cover_solution_count": 6,
        "new_pages": 0,
        "promoted_sequence_card_count": 10,
        "recipe_changes": 0,
        "residual_anchor_context_count": 4,
        "residual_direct_interface_count": 5,
        "residual_support_card_count": 9,
        "root_meaning_changes": 0,
        "selected_frame_count": 5,
        "selected_frame_occurrence_count": 31,
        "selected_frame_strong_peer_count": 21,
        "selected_frame_target_count": 10,
        "selected_same_mode_peer_contact_count": 27,
        "source_sequence_card_count": 10,
        "source_sequence_exact_old_cover_count": 10,
        "status": STATUS,
    }
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    check("result_exact", result == expected_result, result)
    summary = {row["metric"]: row["value"] for row in read_tsv(SUMMARY)}
    check("summary_replays_result", summary == {key: str(value) for key, value in expected_result.items()}, summary)

    book = BOOK.read_text(encoding="utf-8")
    check("book_status", STATUS in book, STATUS)
    check("book_has_five_frames", book.count("\n### `") >= 15, book.count("\n### `"))
    check("book_names_all_selected_frames", all(f"`{frame[0]}→{frame[1]}`" in book for frame in EXPECTED_SELECTED), sorted(EXPECTED_SELECTED))

    deterministic = [CANDIDATES, SOLUTIONS, SELECTED, OCCURRENCES, PROMOTED, RESIDUAL, SUMMARY, BOOK, RESULT]
    before = {path.name: sha256(path) for path in deterministic}
    rerun = subprocess.run(
        [sys.executable, str(RUN)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    after = {path.name: sha256(path) for path in deterministic}
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
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
