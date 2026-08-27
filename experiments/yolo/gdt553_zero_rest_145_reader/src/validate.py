#!/usr/bin/env python3
"""Independent validation for the GDT553 zero-rest reader."""

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
EXP = ROOT / "experiments/yolo/gdt553_zero_rest_145_reader"
ART = EXP / "artifacts"
RUN = EXP / "src/run.py"
CLI = EXP / "src/read_final.py"
G548 = ROOT / "experiments/yolo/gdt548_unified_145_prose_reader/artifacts"
G549 = ROOT / "experiments/yolo/gdt549_default_queue_visible_peer_bridges/artifacts"
G550 = ROOT / "experiments/yolo/gdt550_recurrent_sequence_frame_bridges/artifacts"
G551 = ROOT / "experiments/yolo/gdt551_context_contract_normalization/artifacts"
G552 = ROOT / "experiments/yolo/gdt552_interface_boundary_family_bridges/artifacts"

BASE_IN = G548 / "gdt548_145_unified_prose_reader.tsv"
PEER_IN = G549 / "gdt549_4_promoted_peer_cards.tsv"
FRAME_IN = G550 / "gdt550_10_promoted_sequence_cards.tsv"
CONTEXT_IN = G551 / "gdt551_4_promoted_context_cards.tsv"
INTERFACE_IN = G552 / "gdt552_5_selected_interface_bridges.tsv"

READER = ART / "gdt553_145_zero_rest_reader.tsv"
RESOLVED = ART / "gdt553_23_resolved_queue_cards.tsv"
PROVENANCE = ART / "gdt553_5_provenance_generations.tsv"
SUMMARY = ART / "gdt553_zero_rest_summary.tsv"
BOOK = ART / "GDT553_145_ZERO_REST_READER.md"
RESULT = ART / "gdt553_result.json"
VALIDATION = ART / "gdt553_validation.json"

STATUS = "PASS_ZERO_REST_145_CARD_READER__23_REPAIRS_PARTITION_EXACT"
GENERATION_COUNTS = {
    "BASE_GDT548": 122,
    "GDT549_CURRENT_PEER": 4,
    "GDT550_RECURRENT_FRAME": 10,
    "GDT551_SLOT_CONTRACT": 4,
    "GDT552_BOUNDARY_FAMILY": 5,
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def keyed(rows: list[dict[str, str]], field: str) -> dict[str, dict[str, str]]:
    result = {row[field]: row for row in rows}
    if len(result) != len(rows):
        raise RuntimeError(f"Duplicate {field}")
    return result


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, str(CLI), *args], cwd=ROOT, text=True, capture_output=True, check=False)


def main() -> int:
    checks: list[dict[str, Any]] = []

    def check(name: str, passed: bool, detail: Any) -> None:
        checks.append({"check": name, "passed": bool(passed), "detail": detail})

    base_rows = read_tsv(BASE_IN)
    peer_rows = read_tsv(PEER_IN)
    frame_rows = read_tsv(FRAME_IN)
    context_rows = read_tsv(CONTEXT_IN)
    interface_rows = read_tsv(INTERFACE_IN)
    check("source_row_counts", [len(base_rows), len(peer_rows), len(frame_rows), len(context_rows), len(interface_rows)] == [145, 4, 10, 4, 5], [len(base_rows), len(peer_rows), len(frame_rows), len(context_rows), len(interface_rows)])
    base = keyed(base_rows, "surface")
    peer = keyed(peer_rows, "surface")
    frame = keyed(frame_rows, "surface")
    context = keyed(context_rows, "surface")
    interface = keyed(interface_rows, "surface")
    groups = [set(peer), set(frame), set(context), set(interface)]
    union = set().union(*groups)
    queue = {row["surface"] for row in base_rows if row["weak_queue_candidate"] == "YES"}
    check("source_queue_count", len(queue) == 23, sorted(queue))
    check("promotion_sets_pairwise_disjoint", sum(map(len, groups)) == len(union), [len(group) for group in groups])
    check("promotion_union_equals_source_queue", union == queue, sorted(union ^ queue))

    reader_rows = read_tsv(READER)
    reader = keyed(reader_rows, "surface")
    check("reader_145_exact_keys", len(reader_rows) == len(reader) == 145 and set(reader) == set(base), len(reader))
    check("reader_source_order_exact", [row["surface"] for row in reader_rows] == [row["surface"] for row in base_rows], len(reader_rows))
    preserved_fields = [
        "target_ordinal",
        "support_tier",
        "support_rank",
        "support_band",
        "final_recipe",
        "target_event_count",
        "target_physical_pages",
        "observed_requirement_modes",
        "visible_action_roots",
        "visible_argument_roots",
        "future_action_contract",
        "future_argument_contract",
        "minimum_future_state_for_verbal_clause",
        "neutral_component_reading_de",
        "known_contextual_readings_de",
    ]
    preservation_errors = [
        surface
        for surface in base
        if any(reader[surface][field] != base[surface][field] for field in preserved_fields)
    ]
    check("all_semantic_context_fields_byte_preserved", not preservation_errors, preservation_errors)
    check("all_reader_decisions_current", all(row["reader_decision"] == "READ_KNOWN_ZERO_REST_145_WORKING_CARD" for row in reader_rows), Counter(row["reader_decision"] for row in reader_rows))
    check("all_support_rests_zero", all(row["support_rest_status"] == "NONE__BOUNDED_WORKING_ROUTE_DOCUMENTED" for row in reader_rows), Counter(row["support_rest_status"] for row in reader_rows))
    check("all_meanings_complete", all(row["neutral_component_reading_de"] and row["known_contextual_readings_de"] for row in reader_rows), len(reader_rows))
    generations = Counter(row["resolution_generation"] for row in reader_rows)
    check("generation_counts_exact", dict(generations) == GENERATION_COUNTS, dict(generations))

    base_errors = []
    for surface in set(base) - queue:
        row = reader[surface]
        source = base[surface]
        if (
            row["resolution_generation"] != "BASE_GDT548"
            or row["current_route_trace_scope"] != "BASE_TIER_TRACE"
            or row["current_route_trace"] != source["tier_trace"]
            or row["current_evidence_trace"] != source["tier_evidence"]
            or row["retained_scope_limit"] != source["tier_caution"]
        ):
            base_errors.append(surface)
    check("all_122_base_cards_exact", not base_errors, base_errors)

    peer_errors = []
    for surface, source in peer.items():
        row = reader[surface]
        expected_evidence = f"context={source['context_bridge']};interface={source['interface_bridge']}"
        if (
            row["resolution_generation"] != "GDT549_CURRENT_PEER"
            or row["current_route_trace"] != source["visible_route"]
            or row["current_evidence_trace"] != expected_evidence
            or row["strongest_current_provenance"] != "CURRENT_EXACT_CONTEXT_AND_OR_INTERFACE_PEER"
        ):
            peer_errors.append(surface)
    check("four_gdt549_resolutions_exact", not peer_errors, peer_errors)

    frame_errors = []
    for surface, source in frame.items():
        row = reader[surface]
        if (
            row["resolution_generation"] != "GDT550_RECURRENT_FRAME"
            or row["current_route_trace"] != source["exact_visible_route"]
            or source["frame_id"] not in row["current_evidence_trace"]
            or row["retained_scope_limit"] != source["retained_caution"]
        ):
            frame_errors.append(surface)
    check("ten_gdt550_resolutions_exact", not frame_errors, frame_errors)

    context_errors = []
    for surface, source in context.items():
        row = reader[surface]
        if (
            row["resolution_generation"] != "GDT551_SLOT_CONTRACT"
            or row["current_route_trace"] != source["selected_visible_trace"]
            or source["contract_relation"] not in row["current_evidence_trace"]
            or row["retained_scope_limit"] != "INSTANCE_MODE_IS_INCOMING_STATE__NO_LEXICAL_CONTEXT_SWITCH"
        ):
            context_errors.append(surface)
    check("four_gdt551_resolutions_exact", not context_errors, context_errors)

    interface_errors = []
    for surface, source in interface.items():
        row = reader[surface]
        if (
            row["resolution_generation"] != "GDT552_BOUNDARY_FAMILY"
            or row["current_route_trace"] != source["selected_visible_trace"]
            or row["current_evidence_trace"] != source["gate_trace"]
            or row["strongest_current_provenance"] != source["bridge_class"]
            or not row["retained_scope_limit"].startswith("OLD_DIRECT_WITHIN_CARD_PAIR_ABSENT")
        ):
            interface_errors.append(surface)
    check("five_gdt552_resolutions_exact", not interface_errors, interface_errors)

    resolved_rows = read_tsv(RESOLVED)
    resolved = keyed(resolved_rows, "surface")
    check("resolved_queue_set_exact", len(resolved) == 23 and set(resolved) == queue, sorted(set(resolved) ^ queue))
    check("resolved_rows_equal_reader_subset", all(resolved[s] == reader[s] for s in resolved), len(resolved))

    provenance_rows = read_tsv(PROVENANCE)
    provenance = keyed(provenance_rows, "resolution_generation")
    check("five_provenance_rows", set(provenance) == set(GENERATION_COUNTS), sorted(provenance))
    check("provenance_counts_exact", all(int(provenance[key]["card_count"]) == count and provenance[key]["support_rest_count"] == "0" for key, count in GENERATION_COUNTS.items()), {key: provenance[key]["card_count"] for key in provenance})

    result = json.loads(RESULT.read_text(encoding="utf-8"))
    expected_result = {
        "status": STATUS,
        "reader_card_count": 145,
        "exact_surface_key_count": 145,
        "base_outside_queue_count": 122,
        "gdt549_peer_resolution_count": 4,
        "gdt550_frame_resolution_count": 10,
        "gdt551_contract_resolution_count": 4,
        "gdt552_boundary_resolution_count": 5,
        "resolved_former_queue_count": 23,
        "resolution_generation_count": 5,
        "full_recipe_tier_count": 11,
        "fully_tiled_tier_count": 29,
        "fragment_tier_count": 81,
        "atomic_tier_count": 24,
        "complete_neutral_meaning_count": 145,
        "complete_context_meaning_count": 145,
        "support_rest_count": 0,
        "new_pages": 0,
        "recipe_changes": 0,
        "root_meaning_changes": 0,
    }
    check("result_metrics_exact", result == expected_result, {key: result.get(key) for key in expected_result if result.get(key) != expected_result[key]})
    summary = {row["metric"]: row["value"] for row in read_tsv(SUMMARY)}
    check("summary_matches_result", all(summary.get(key) == str(value) for key, value in result.items()), len(summary))
    book = BOOK.read_text(encoding="utf-8")
    check("book_contains_all_145_surfaces", all(f"`{surface}`" in book for surface in base), len(book))
    check("book_states_zero_rest_limit", "does not mean plaintext" in book, len(book))

    listed = run_cli("--list-surfaces")
    check("cli_lists_145", listed.returncode == 0 and len(listed.stdout.splitlines()) == 145, [listed.returncode, len(listed.stdout.splitlines())])
    probes = {
        "chekchy": "BASE_GDT548",
        "chady": "GDT549_CURRENT_PEER",
        "choraly": "GDT550_RECURRENT_FRAME",
        "folchol": "GDT551_SLOT_CONTRACT",
        "aiicthy": "GDT552_BOUNDARY_FAMILY",
    }
    probe_errors = []
    for surface, generation in probes.items():
        probe = run_cli("--surface", surface, "--active-action", "CH", "--active-argument", "Y", "--format", "json")
        try:
            payload = json.loads(probe.stdout)
        except json.JSONDecodeError:
            payload = {}
        if probe.returncode != 0 or payload.get("card", {}).get("resolution_generation") != generation or payload.get("card", {}).get("support_rest_status") != "NONE__BOUNDED_WORKING_ROUTE_DOCUMENTED":
            probe_errors.append(surface)
    check("cli_one_probe_per_generation", not probe_errors, probe_errors)
    folchol = run_cli("--surface", "folchol", "--active-action", "CH", "--active-argument", "Y", "--format", "json")
    fol_payload = json.loads(folchol.stdout)
    check("cli_context_state_resolution", fol_payload["context_resolution"]["resolved_action_root"] == "CH" and fol_payload["context_resolution"]["resolved_argument_root"] == "Y", fol_payload["context_resolution"])
    unknown = run_cli("--surface", "not_a_known_surface", "--format", "json")
    unknown_payload = json.loads(unknown.stdout)
    check("cli_unknown_stops", unknown.returncode == 2 and unknown_payload["status"] == "STOP_UNKNOWN_ZERO_REST_145_SURFACE", unknown_payload)

    deterministic = [READER, RESOLVED, PROVENANCE, SUMMARY, BOOK, RESULT]
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
        "input_sha256": {path.name: sha256(path) for path in [BASE_IN, PEER_IN, FRAME_IN, CONTEXT_IN, INTERFACE_IN]},
        "artifact_sha256": {path.name: sha256(path) for path in deterministic},
    }
    VALIDATION.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
