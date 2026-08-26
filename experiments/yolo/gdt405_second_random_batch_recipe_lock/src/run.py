#!/usr/bin/env python3
"""Freeze the complete GDT404 dictionary before a second random batch."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
HERE = Path(__file__).resolve().parent.parent
OUT = HERE / "artifacts"
G404 = ROOT / "experiments/yolo/gdt404_random_four_page_factorized_admission/artifacts"
EVENTS = G404 / "gdt404_688_event_first_pass.tsv"
NOVEL = G404 / "gdt404_211_new_surface_audit.tsv"
CORES = G404 / "gdt404_core_transfer_summary.tsv"
AXES = ROOT / "experiments/yolo/gdt402_factorized_scope_selector_head_license/artifacts/gdt402_axis_inventory.tsv"
DECISIONS = ROOT / "experiments/yolo/gdt403_four_page_factorized_admission_worksheet/artifacts/gdt403_decision_catalog.tsv"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise RuntimeError(f"empty output {path.name}")
    fields = list(rows[0])
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows({field: row.get(field, "") for field in fields} for row in rows)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    events = read_tsv(EVENTS)
    novel = read_tsv(NOVEL)
    cores = read_tsv(CORES)
    axes = read_tsv(AXES)
    decisions = read_tsv(DECISIONS)
    if [len(events), len(novel), len(cores), len(axes), len(decisions)] != [688, 211, 46, 31, 19]:
        raise RuntimeError("upstream inventory mismatch")

    novel_by_surface = {row["surface"]: row for row in novel}
    by_surface: dict[str, list[dict[str, str]]] = defaultdict(list)
    for event in events:
        by_surface[event["surface"]].append(event)
    if len(by_surface) != 426:
        raise RuntimeError("GDT404 surface inventory mismatch")

    dictionary: list[dict[str, object]] = []
    for ordinal, (surface, selected) in enumerate(sorted(by_surface.items()), 1):
        recipes = {row["visible_recipe"] for row in selected}
        statuses = {row["surface_status"] for row in selected}
        if len(recipes) != 1 or len(statuses) != 1:
            raise RuntimeError(f"non-deterministic GDT404 surface: {surface}")
        status = next(iter(statuses))
        audit = novel_by_surface.get(surface)
        amber = status == "NEW_MICROFORM_OLD_FACTORS"
        dictionary.append({
            "lock_id": f"G405-W{ordinal:04d}",
            "surface": surface,
            "locked_recipe": next(iter(recipes)),
            "gdt404_surface_status": status,
            "gdt404_event_count": len(selected),
            "gdt404_physical_page_count": len({row["physical_page"] for row in selected}),
            "gdt404_physical_pages": "|".join(sorted({row["physical_page"] for row in selected})),
            "gdt404_first_event_id": selected[0]["event_id"],
            "amber_boundary": "YES" if amber else "NO",
            "locked_candidate_recipes": audit["candidate_recipes_by_weight"] if audit else next(iter(recipes)),
            "next_batch_exact_surface_rule": (
                "REPLAY_PRIMARY_RECIPE__KEEP_AMBER_BOUNDARY_VISIBLE"
                if amber else "REPLAY_LOCKED_RECIPE_WITHOUT_EDIT"
            ),
            "allowed_change": "BOUNDARY_PROMOTION_BY_VISIBLE_RECURRENCE_ONLY" if amber else "NONE",
            "forbidden_change": "NEW_ATOM|CORE_RETUNE|INVISIBLE_COMPONENT|POSTHOC_RESEGMENTATION",
        })
    write_tsv(OUT / "gdt405_426_locked_surface_dictionary.tsv", dictionary)

    atom_rows: list[dict[str, object]] = []
    for core in cores:
        atom_rows.append({
            "atom": core["atom"],
            "locked_working_value_de": core["working_value_de"],
            "factor_family": core["factor_family"],
            "gdt404_event_count": core["event_count"],
            "gdt404_physical_pages": core["physical_pages"],
            "next_batch_policy": "VALUE_LOCKED__NEW_VISIBLE_COMPOSITIONS_ALLOWED",
            "retuning_allowed": "NO",
        })
    write_tsv(OUT / "gdt405_46_locked_atom_dictionary.tsv", atom_rows)

    amber_rows: list[dict[str, object]] = []
    for ordinal, row in enumerate((row for row in novel if row["selection_status"] == "NEW_MICROFORM_OLD_FACTORS"), 1):
        amber_rows.append({
            "amber_id": f"G405-M{ordinal:03d}",
            "surface": row["surface"],
            "primary_locked_recipe": row["selected_recipe"],
            "one_edit_candidate_recipes": row["candidate_recipes_by_weight"],
            "primary_seen_among_one_edit_candidates": row["manual_recipe_seen_in_one_edit_candidates"],
            "future_exact_recurrence_action": "READ_PRIMARY_AND_AUDIT_VISIBLE_PACKAGE_CONTEXT",
            "promotion_gate": "SAME_VISIBLE_BOUNDARY_IN_AT_LEAST_ONE_NEW_OCCURRENCE",
            "failure_gate": "REQUIRES_NEW_ATOM_OR_CHANGES_A_LOCKED_CORE_VALUE",
            "status": "AMBER_BOUNDARY_LOCKED",
        })
    write_tsv(OUT / "gdt405_49_amber_microform_lock.tsv", amber_rows)

    axis_rows: list[dict[str, object]] = []
    for row in axes:
        axis_rows.append({
            "axis": row["axis"], "value": row["value"],
            "gdt402_occurrences": row["occurrences"],
            "gdt402_page_count": row["page_count"],
            "gdt402_register_count": row["register_count"],
            "next_batch_policy": "LOCKED_ALLOWED_FACTOR",
            "new_value_allowed": "NO",
        })
    write_tsv(OUT / "gdt405_31_locked_parser_factors.tsv", axis_rows)

    slots = [
        {
            "slot": f"SECOND_BATCH_PAGE_{index}", "release_status": "UNRELEASED",
            "physical_page": "PENDING", "source_values": "PENDING",
            "image_owner_freeze": "PENDING", "event_count": "PENDING",
            "exact_gdt405_surface_count": "PENDING", "new_surface_count": "PENDING",
            "amber_recurrence_count": "PENDING", "factorized_result": "PENDING",
        }
        for index in range(1, 5)
    ]
    write_tsv(OUT / "gdt405_second_batch_slots.tsv", slots)

    protocol = [
        (1, "SELECT_ONCE", "draw or accept exactly four physical pages; no resampling"),
        (2, "GUARD_SOURCE", "query only explicitly released selector values"),
        (3, "FREEZE_IMAGE_OWNER", "record visible owners before text parsing"),
        (4, "EXACT_SURFACE_FIRST", "replay every GDT405 surface byte-for-byte"),
        (5, "AMBER_EXACT_SURFACE", "use primary recipe and separately audit its package boundary"),
        (6, "NEW_SURFACE", "compose only from visibly present locked atoms"),
        (7, "NO_ONE_EDIT_IMPORT", "a neighbour never supplies an invisible atom"),
        (8, "SEGMENT_STATEMENTS", "licensed close or real prose-owner boundary only"),
        (9, "RUN_FACTORIZED_SCOPE", "use only the thirty-one locked factors"),
        (10, "MAX_LOOKAHEAD_ONE", "never skip more than one card forward"),
        (11, "STOP_ON_BOUNDARY", "owner or statement crossing fails the batch"),
        (12, "STOP_ON_RETUNE", "do not change any of the forty-six working values"),
    ]
    write_tsv(
        OUT / "gdt405_second_batch_protocol.tsv",
        [{"step": step, "operation": operation, "rule": rule} for step, operation, rule in protocol],
    )

    result = {
        "experiment_id": "GDT405",
        "status": "SECOND_RANDOM_BATCH_LOCK_READY",
        "locked_surface_count": len(dictionary),
        "locked_atom_count": len(atom_rows),
        "locked_parser_factor_count": len(axis_rows),
        "amber_microform_count": len(amber_rows),
        "unreleased_page_slot_count": len(slots),
        "protocol_step_count": len(protocol),
        "gdt404_event_count": len(events),
        "input_hashes": {
            str(EVENTS.relative_to(ROOT)): sha256(EVENTS),
            str(NOVEL.relative_to(ROOT)): sha256(NOVEL),
            str(CORES.relative_to(ROOT)): sha256(CORES),
            str(AXES.relative_to(ROOT)): sha256(AXES),
            str(DECISIONS.relative_to(ROOT)): sha256(DECISIONS),
        },
    }
    (OUT / "gdt405_result.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
