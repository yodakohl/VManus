#!/usr/bin/env python3
"""Freeze the score-blind GDT338 held-field capacity panel."""

from __future__ import annotations

import csv
import hashlib
import json
import sys
from collections import defaultdict
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
sys.path.insert(0, str(ROOT))

from tools.vmanus_experiment import GuardedTSV, canonical_json_bytes, sha256_file  # noqa: E402


EXP = ROOT / "experiments/yolo/gdt338_renderer_invariant_equivalence"
INTER = ROOT / "gdt327_joint_tuple_interlinear.tsv"
DESIGN = EXP / "artifacts/gdt338_design.json"
CAPACITY = EXP / "artifacts/gdt338_capacity.tsv"
FREEZE = EXP / "artifacts/gdt338_freeze.json"


def stable_id(prefix: str, value: object) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return prefix + hashlib.sha256(payload.encode("utf-8")).hexdigest()[:20]


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError("capacity panel unexpectedly empty")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    design = json.loads(DESIGN.read_text(encoding="utf-8"))
    guard = GuardedTSV(INTER, selector_column="page", forbidden_action="error")
    source_rows = list(guard)
    if len(source_rows) != 8448 or guard.stats.skipped_forbidden:
        raise AssertionError((len(source_rows), guard.stats))

    grouped: dict[tuple[str, str, str, str, int], list[dict[str, str]]] = defaultdict(list)
    for row in source_rows:
        key = (
            row["register"],
            row["physical_folio"],
            row["page"],
            row["locus"],
            int(row["field_ordinal"]),
        )
        grouped[key].append(row)

    fields = []
    for key, rows in sorted(grouped.items()):
        rows.sort(key=lambda row: int(row["group_index"]))
        normalized = tuple(row["joint_tuple_id"] for row in rows)
        rendered = tuple((row["observed_wrapper"], row["joint_tuple_id"]) for row in rows)
        fields.append(
            {
                "key": key,
                "register": key[0],
                "folio": key[1],
                "page": key[2],
                "locus": key[3],
                "field_ordinal": key[4],
                "normalized": normalized,
                "rendered": rendered,
                "groups": len(rows),
                "powered": all(row["renderer_state"] == "EXECUTABLE_POWERED_CELL" for row in rows),
            }
        )

    capacity_rows: list[dict[str, object]] = []
    for held in fields:
        if not held["powered"]:
            continue
        training = [
            field
            for field in fields
            if field["register"] == held["register"]
            and field["folio"] != held["folio"]
            and field["powered"]
        ]
        if held["rendered"] in {field["rendered"] for field in training}:
            continue
        same = [field for field in training if field["normalized"] == held["normalized"]]
        train_folios = sorted({str(field["folio"]) for field in same})
        train_surfaces = {field["rendered"] for field in same}
        if len(train_folios) < design["eligibility"]["minimum_training_physical_folios"]:
            continue
        if len(train_surfaces) < design["eligibility"]["minimum_distinct_training_surfaces"]:
            continue
        class_id = stable_id("NEQ", held["normalized"])
        register_class_cell_id = stable_id("NRC", (held["register"], held["normalized"]))
        field_id = stable_id("FLD", held["key"])
        capacity_rows.append(
            {
                "field_id": field_id,
                "class_id": class_id,
                "register_class_cell_id": register_class_cell_id,
                "register": held["register"],
                "physical_folio": held["folio"],
                "page": held["page"],
                "locus": held["locus"],
                "field_ordinal_audit_only": held["field_ordinal"],
                "group_count": held["groups"],
                "training_physical_folios": len(train_folios),
                "training_distinct_surfaces": len(train_surfaces),
                "training_occurrences": len(same),
                "held_surface_seen_in_training": "NO",
                "semantic_state": "UNASSIGNED",
                "translation_state": "UNASSIGNED",
            }
        )

    write_tsv(CAPACITY, capacity_rows)
    counts = {
        "fields": len(capacity_rows),
        "group_events": sum(int(row["group_count"]) for row in capacity_rows),
        "physical_folios": len({row["physical_folio"] for row in capacity_rows}),
        "normalized_classes": len({row["class_id"] for row in capacity_rows}),
        "register_class_cells": len({row["register_class_cell_id"] for row in capacity_rows}),
        "registers": len({row["register"] for row in capacity_rows}),
        "one_group_fields": sum(int(row["group_count"]) == 1 for row in capacity_rows),
        "two_group_fields": sum(int(row["group_count"]) == 2 for row in capacity_rows),
    }
    expected = {
        "fields": 25,
        "group_events": 32,
        "physical_folios": 17,
        "normalized_classes": 9,
        "register_class_cells": 10,
        "registers": 3,
        "one_group_fields": 18,
        "two_group_fields": 7,
    }
    if counts != expected:
        raise AssertionError((counts, expected))
    payload = {
        "schema": "GDT338_FREEZE_V1",
        "status": "FROZEN_UNSCORED",
        "counts": counts,
        "guard": guard.stats.__dict__,
        "inputs": {
            str(INTER.relative_to(ROOT)): sha256_file(INTER),
            str(DESIGN.relative_to(ROOT)): sha256_file(DESIGN),
        },
        "outputs": {str(CAPACITY.relative_to(ROOT)): sha256_file(CAPACITY)},
        "implementation": {
            str(Path(__file__).resolve().relative_to(ROOT)): sha256_file(Path(__file__).resolve())
        },
        "f84": {"opened": False, "parsed": False, "retained": False, "joined": False, "scored": False},
        "semantic_assignments": 0,
    }
    payload["content_sha256"] = hashlib.sha256(canonical_json_bytes(payload)).hexdigest()
    FREEZE.write_bytes(canonical_json_bytes(payload))
    print(json.dumps({"status": payload["status"], "counts": counts}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
