#!/usr/bin/env python3
"""Independent validation for GDT549 visible routes and peer bridges."""

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
EXP = ROOT / "experiments/yolo/gdt549_default_queue_visible_peer_bridges"
ART = EXP / "artifacts"
RUN = EXP / "src/run.py"

G548 = ROOT / "experiments/yolo/gdt548_unified_145_prose_reader/artifacts"
G519 = ROOT / "experiments/yolo/gdt519_visible_stem_anchor_transducer/artifacts"
G539 = ROOT / "experiments/yolo/gdt539_four_page_contextual_statement_edition/artifacts"
G546 = ROOT / "experiments/yolo/gdt546_consolidated_fragment_reader/artifacts"

QUEUE_IN = G548 / "gdt548_23_named_default_queue.tsv"
READER_IN = G548 / "gdt548_145_unified_prose_reader.tsv"
ALIAS_IN = G519 / "gdt519_anchor_alias_lexicon.tsv"
EVENT_IN = G539 / "gdt539_546_contextual_prose_events.tsv"
FRAGMENT_IN = G546 / "gdt546_81_consolidated_fragment_reader.tsv"

VISIBLE = ART / "gdt549_23_exact_visible_default_cards.tsv"
COVERS = ART / "gdt549_96_old26_exact_cover_paths.tsv"
CONTEXT = ART / "gdt549_9_context_mismatch_peer_audit.tsv"
INTERFACES = ART / "gdt549_6_new_interface_peer_audit.tsv"
PROMOTED = ART / "gdt549_4_promoted_peer_cards.tsv"
RESIDUAL = ART / "gdt549_19_residual_support_queue.tsv"
SUMMARY = ART / "gdt549_visible_peer_summary.tsv"
BOOK = ART / "GDT549_DEFAULT_QUEUE_VISIBLE_PEER_BOOK.md"
RESULT = ART / "gdt549_result.json"
VALIDATION = ART / "gdt549_validation.json"

STATUS = "PASS_ALL_23_DEFAULTS_EXACTLY_VISIBLE__4_CURRENT_PEER_PROMOTIONS__19_SUPPORT_RESTS"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def keyed(rows: list[dict[str, str]], field: str) -> dict[str, dict[str, str]]:
    return {row[field]: row for row in rows}


def trace_parts(value: str) -> tuple[str, str]:
    surface_parts = []
    recipe_parts = []
    for part in value.split(" | "):
        left, right = part.split("→", 1)
        surface_parts.append(left)
        recipe_parts.extend(right.split("+"))
    return "".join(surface_parts), "+".join(recipe_parts)


def event_mode(event: dict[str, str]) -> str:
    action = event["inherited_action_root"] != "NONE"
    argument = event["inherited_argument_root"] != "NONE"
    if action and argument:
        return "REQUIRES_ACTIVE_ACTION_AND_ARGUMENT"
    if action:
        return "REQUIRES_ACTIVE_ACTION"
    if argument:
        return "REQUIRES_ACTIVE_ARGUMENT"
    return "SELF_CONTAINED"


def contains_sequence(recipe: str, needle: str) -> bool:
    source = recipe.split("+")
    target = needle.split("+")
    return any(source[index : index + len(target)] == target for index in range(len(source)))


def contains_pair(recipe: str, pair: str) -> bool:
    left, right = pair.split(">")
    atoms = recipe.split("+")
    return any(a == left and b == right for a, b in zip(atoms, atoms[1:]))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    checks: list[dict[str, Any]] = []

    def check(name: str, passed: bool, detail: Any) -> None:
        checks.append({"check": name, "passed": bool(passed), "detail": detail})

    queue = read_tsv(QUEUE_IN)
    readers = keyed(read_tsv(READER_IN), "surface")
    fragments = keyed(read_tsv(FRAGMENT_IN), "surface")
    events = read_tsv(EVENT_IN)
    aliases = [row for row in read_tsv(ALIAS_IN) if row["model"] == "FULL_OLD26"]
    alias_keys = {
        (row["surface_alias"], row["atom_sequence"], row["alias_source"], row["support"])
        for row in aliases
    }
    visible = read_tsv(VISIBLE)
    covers = read_tsv(COVERS)
    contexts = read_tsv(CONTEXT)
    interfaces = read_tsv(INTERFACES)
    promoted = read_tsv(PROMOTED)
    residual = read_tsv(RESIDUAL)
    visible_map = keyed(visible, "surface")

    queue_set = {row["surface"] for row in queue}
    check("source_queue_count", len(queue) == 23, len(queue))
    check("visible_card_count", len(visible) == 23, len(visible))
    check("visible_surface_set_exact", set(visible_map) == queue_set, sorted(set(visible_map) ^ queue_set))
    check(
        "all_visible_routes_reconstruct",
        all(
            trace_parts(row["selected_visible_trace"])
            == (row["surface"], row["final_recipe"])
            for row in visible
        ),
        [
            row["surface"]
            for row in visible
            if trace_parts(row["selected_visible_trace"])
            != (row["surface"], row["final_recipe"])
        ],
    )
    check(
        "all_visible_status_exact",
        {row["exact_surface_reconstruction"] for row in visible} == {"YES"}
        and {row["exact_recipe_reconstruction"] for row in visible} == {"YES"}
        and {row["lexical_visible_status"] for row in visible}
        == {"EXACT_VISIBLE_COMPOSITION__NO_OPAQUE_WHOLE_GLOSS"},
        Counter(row["lexical_visible_status"] for row in visible),
    )
    meaning_errors = [
        row["surface"]
        for row in visible
        if row["neutral_component_reading_de"]
        != readers[row["surface"]]["neutral_component_reading_de"]
        or row["known_contextual_readings_de"]
        != readers[row["surface"]]["known_contextual_readings_de"]
    ]
    check("all_meanings_inherited_exactly", not meaning_errors, meaning_errors)

    cover_targets = {row["surface"] for row in covers}
    check("old_cover_path_count", len(covers) == 96, len(covers))
    check("old_cover_target_count", len(cover_targets) == 20, len(cover_targets))
    check(
        "old_cover_missing_set",
        queue_set - cover_targets == {"aiicthy", "saiis", "shokaiir"},
        sorted(queue_set - cover_targets),
    )
    cover_replay_errors = [
        f"{row['surface']}:{row['compressed_cover_rank']}"
        for row in covers
        if trace_parts(row["visible_trace"])
        != (row["surface"], row["final_recipe"])
    ]
    check("all_96_cover_paths_reconstruct", not cover_replay_errors, cover_replay_errors)

    alias_errors = []
    for row in covers:
        evidence_parts = row["evidence_trace"].split(" | ")
        trace_values = row["visible_trace"].split(" | ")
        if len(evidence_parts) != len(trace_values):
            alias_errors.append(f"{row['surface']}:length")
            continue
        for visible_part, evidence_part in zip(trace_values, evidence_parts):
            alias, atoms = visible_part.split("→", 1)
            bits = evidence_part.split(":")
            source = bits[1]
            support = bits[2][1:]
            if (alias, atoms, source, support) not in alias_keys:
                alias_errors.append(f"{row['surface']}:{alias}:{atoms}")
    check("every_cover_segment_is_old_alias_row", not alias_errors, alias_errors)

    grouped_covers: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in covers:
        grouped_covers[row["surface"]].append(row)
    rank_errors = []
    for surface, rows in grouped_covers.items():
        ranks = sorted(int(row["compressed_cover_rank"]) for row in rows)
        selected_rows = [row for row in rows if row["selected_compressed_cover"] == "YES"]
        if ranks != list(range(1, len(rows) + 1)) or len(selected_rows) != 1:
            rank_errors.append(surface)
            continue
        if int(selected_rows[0]["segment_count"]) != min(int(row["segment_count"]) for row in rows):
            rank_errors.append(surface)
    check("compressed_cover_ranks_and_selection", not rank_errors, rank_errors)
    selected_distribution = Counter(int(row["selected_segment_count"]) for row in visible)
    check("selected_segment_distribution_13_8_2", selected_distribution == {2: 13, 3: 8, 4: 2}, dict(selected_distribution))
    route_distribution = Counter(row["visible_route_class"] for row in visible)
    check(
        "visible_route_distribution_20_plus_3",
        route_distribution
        == {
            "OLD26_EXACT_ALIAS_COVER": 20,
            "GDT546_SINGLETON_EXTENSION_PLUS_EXACT_OLD_STEM": 1,
            "GDT547_PREFIX_CONDITIONED_AIIS_ROUTE": 1,
            "GDT546_EXACT_OLD_STEM_PLUS_RECURRENT_EXTENSION": 1,
        },
        dict(route_distribution),
    )

    expected_context_targets = {
        row["surface"]
        for row in queue
        if "ANCHOR_CONTEXT_MODE_DIFFERENCE" in readers[row["surface"]]["tier_caution"]
    }
    context_map = keyed(contexts, "surface")
    check("context_audit_count", len(contexts) == 9, len(contexts))
    check("context_target_set_exact", set(context_map) == expected_context_targets, sorted(set(context_map) ^ expected_context_targets))
    context_errors = []
    for surface, row in context_map.items():
        target_modes = set(readers[surface]["observed_requirement_modes"].split("|"))
        anchor = fragments[surface]["primary_anchor_recipe"]
        peers = [
            event
            for event in events
            if event["surface"] != surface
            and contains_sequence(event["final_context_recipe"], anchor)
            and event_mode(event) in target_modes
        ]
        expected_status = "CURRENT_PEER_CONTEXT_BRIDGE" if peers else "NO_CURRENT_PEER_CONTEXT_BRIDGE"
        if (
            row["anchor_recipe"] != anchor
            or int(row["current_peer_event_count"]) != len(peers)
            or int(row["current_peer_surface_count"])
            != len({event["surface"] for event in peers})
            or row["peer_context_status"] != expected_status
        ):
            context_errors.append(surface)
    check("all_context_peer_rows_replay", not context_errors, context_errors)
    context_repaired = {
        row["surface"]
        for row in contexts
        if row["peer_context_status"] == "CURRENT_PEER_CONTEXT_BRIDGE"
    }
    check(
        "context_peer_result_5_of_9_and_8_events",
        len(context_repaired) == 5
        and sum(int(row["current_peer_event_count"]) for row in contexts) == 8,
        [sorted(context_repaired), sum(int(row["current_peer_event_count"]) for row in contexts)],
    )

    expected_pairs: dict[str, str] = {}
    for surface in queue_set & set(fragments):
        source = fragments[surface]
        if "NEW_ATOM_INTERFACE" not in source["current_caution"]:
            continue
        candidates = []
        if source["left_interface_pair"] != "NONE" and source["left_interface_old_event_count"] == "0":
            candidates.append(source["left_interface_pair"])
        if source["right_interface_pair"] != "NONE" and source["right_interface_old_event_count"] == "0":
            candidates.append(source["right_interface_pair"])
        if len(candidates) == 1:
            expected_pairs[surface] = candidates[0]
    expected_pairs["shso"] = "SH>S"
    interface_map = keyed(interfaces, "surface")
    check("interface_audit_count", len(interfaces) == 6, len(interfaces))
    check(
        "interface_target_pairs_exact",
        {surface: row["interface_pair"] for surface, row in interface_map.items()}
        == expected_pairs,
        {surface: row["interface_pair"] for surface, row in interface_map.items()},
    )
    interface_errors = []
    for surface, pair in expected_pairs.items():
        all_current = [event for event in events if contains_pair(event["final_context_recipe"], pair)]
        peers = [event for event in all_current if event["surface"] != surface]
        row = interface_map[surface]
        expected_status = "CURRENT_PEER_INTERFACE_BRIDGE" if peers else "CURRENT_SINGLETON_INTERFACE"
        if (
            int(row["current_total_event_count"]) != len(all_current)
            or int(row["current_peer_event_count"]) != len(peers)
            or row["peer_interface_status"] != expected_status
        ):
            interface_errors.append(surface)
    check("all_interface_peer_rows_replay", not interface_errors, interface_errors)
    interface_repaired = {
        row["surface"]
        for row in interfaces
        if row["peer_interface_status"] == "CURRENT_PEER_INTERFACE_BRIDGE"
    }
    check(
        "interface_peer_result_1_of_6_and_2_events",
        interface_repaired == {"chady"}
        and sum(int(row["current_peer_event_count"]) for row in interfaces) == 2,
        [sorted(interface_repaired), sum(int(row["current_peer_event_count"]) for row in interfaces)],
    )

    promoted_set = {row["surface"] for row in promoted}
    expected_promoted = {"chady", "kody", "qoekedy", "qokshd"}
    check("promoted_card_count", len(promoted) == 4, len(promoted))
    check("promoted_card_set_exact", promoted_set == expected_promoted, sorted(promoted_set ^ expected_promoted))
    check(
        "promoted_context_support_present",
        promoted_set <= context_repaired and "chady" in interface_repaired,
        [sorted(context_repaired), sorted(interface_repaired)],
    )

    residual_set = {row["surface"] for row in residual}
    check("residual_card_count", len(residual) == 19, len(residual))
    check("promoted_residual_partition", promoted_set.isdisjoint(residual_set) and promoted_set | residual_set == queue_set, sorted((promoted_set | residual_set) ^ queue_set))
    residual_distribution = Counter(row["residual_dimension"] for row in residual)
    check(
        "residual_distribution_10_4_5",
        residual_distribution
        == {
            "HIGHER_ORDER_SEQUENCE_CONTEXT": 10,
            "ANCHOR_CONTEXT": 4,
            "DIRECT_INTERFACE": 5,
        },
        dict(residual_distribution),
    )
    check(
        "residual_context_set_exact",
        {row["surface"] for row in residual if row["residual_dimension"] == "ANCHOR_CONTEXT"}
        == {"folchol", "qoteeod", "saiis", "shokaiir"},
        sorted(row["surface"] for row in residual if row["residual_dimension"] == "ANCHOR_CONTEXT"),
    )
    check(
        "residual_interface_set_exact",
        {row["surface"] for row in residual if row["residual_dimension"] == "DIRECT_INTERFACE"}
        == {"aiicthy", "chap", "ofaram", "rotaiin", "shso"},
        sorted(row["surface"] for row in residual if row["residual_dimension"] == "DIRECT_INTERFACE"),
    )
    check(
        "all_residual_cards_remain_visibly_complete",
        {row["visible_status"] for row in residual} == {"EXACT_VISIBLE_COMPOSITION"},
        Counter(row["visible_status"] for row in residual),
    )

    expected_result: dict[str, Any] = {
        "bounded_current_visible_route_count": 3,
        "complete_context_meaning_count": 23,
        "complete_neutral_meaning_count": 23,
        "context_mismatch_source_count": 9,
        "context_peer_event_count": 8,
        "context_peer_repaired_count": 5,
        "context_unresolved_count": 4,
        "exact_visible_composition_count": 23,
        "four_segment_selected_route_count": 2,
        "interface_peer_event_count": 2,
        "interface_peer_repaired_count": 1,
        "interface_unresolved_count": 5,
        "new_interface_source_count": 6,
        "new_pages": 0,
        "old26_exact_cover_path_count": 96,
        "old26_exact_cover_target_count": 20,
        "opaque_whole_gloss_count": 0,
        "promoted_card_count": 4,
        "recipe_changes": 0,
        "residual_anchor_context_count": 4,
        "residual_card_count": 19,
        "residual_direct_interface_count": 5,
        "residual_higher_order_sequence_count": 10,
        "root_meaning_changes": 0,
        "source_default_count": 23,
        "status": STATUS,
        "three_segment_selected_route_count": 8,
        "two_segment_selected_route_count": 13,
    }
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    check("result_exact", result == expected_result, result)
    summary = {row["metric"]: row["value"] for row in read_tsv(SUMMARY)}
    check("summary_replays_result", summary == {key: str(value) for key, value in expected_result.items()}, summary)

    book = BOOK.read_text(encoding="utf-8")
    check("book_status", STATUS in book, STATUS)
    check("book_has_23_cards", book.count("\n### `") == 23, book.count("\n### `"))
    check("book_names_four_promotions", all(surface in book for surface in expected_promoted), sorted(expected_promoted))

    deterministic = [VISIBLE, COVERS, CONTEXT, INTERFACES, PROMOTED, RESIDUAL, SUMMARY, BOOK, RESULT]
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
