#!/usr/bin/env python3
"""Build the V81 target packet only after all four source-first freezes."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
V80 = HERE.parent / "sidequest_theory_candidates_v80"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, fields: list[str], rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


freeze_specs = {
    "R1": (HERE / "V81_R1_SOURCE_FREEZE.json", HERE / "V81_R1_SOURCE_INVENTORY.tsv"),
    "R2": (HERE / "V81_R2_SOURCE_FREEZE.json", HERE / "V81_R2_PHASE1_SOURCE_INVENTORY.tsv"),
    "R3": (HERE / "V81_R3_SOURCE_FREEZE.json", HERE / "V81_R3_SOURCE_INVENTORY.tsv"),
    "R4": (HERE / "V81_R4_SOURCE_FREEZE.json", HERE / "V81_R4_SOURCE_FIRST_INVENTORY.tsv"),
}
freezes: dict[str, dict[str, object]] = {}
for role, (freeze_path, inventory_path) in freeze_specs.items():
    if not freeze_path.exists() or not inventory_path.exists():
        raise SystemExit(f"MISSING_SOURCE_FREEZE::{role}")
    freeze = json.loads(freeze_path.read_text(encoding="utf-8"))
    if freeze.get("status") != "FROZEN_BEFORE_V81_TARGET_MANIFEST":
        raise SystemExit(f"BAD_SOURCE_FREEZE_STATUS::{role}")
    if freeze.get("target_manifest_opened") is not False:
        raise SystemExit(f"SOURCE_FREEZE_NOT_BLIND::{role}")
    if role in {"R1", "R3"}:
        declared_hash = str(freeze["inventory"]["sha256"])
    else:
        declared_hash = str(freeze["inventory_sha256"])
    if sha256(inventory_path) != declared_hash:
        raise SystemExit(f"SOURCE_INVENTORY_HASH_MISMATCH::{role}")
    freezes[role] = freeze

dictionary_path = V80 / "V80_CANONICAL_173_CARD_DICTIONARY.tsv"
events_path = V80 / "V80_CANONICAL_381_PROSE_EVENT_INTERLINEAR.tsv"
statements_path = V80 / "V80_CANONICAL_116_STATEMENT_EDITION.tsv"
dictionary = read_tsv(dictionary_path)
events = read_tsv(events_path)
statements = read_tsv(statements_path)

selected_cards = sorted(
    (row for row in dictionary if int(row["independent_source_positions"]) >= 3),
    key=lambda row: (-int(row["independent_source_positions"]), row["joint_tuple_id"]),
)
target_id = {row["joint_tuple_id"]: f"T{index:03d}" for index, row in enumerate(selected_cards, start=1)}
events_by_card: dict[str, list[dict[str, str]]] = defaultdict(list)
for row in events:
    if row["joint_tuple_id"] in target_id:
        events_by_card[row["joint_tuple_id"]].append(row)

manifest_rows: list[dict[str, object]] = []
for rank, card in enumerate(selected_cards, start=1):
    card_events = events_by_card[card["joint_tuple_id"]]
    manifest_rows.append(
        {
            "target_rank": rank,
            "anonymous_target_id": target_id[card["joint_tuple_id"]],
            "joint_tuple_id": card["joint_tuple_id"],
            "visible_occurrences": len(card_events),
            "independent_source_positions": sum(int(row["source_position_contribution"]) for row in card_events),
            "distinct_pages": len({row["page"] for row in card_events}),
            "distinct_records": len({row["record_unit_id"] for row in card_events}),
            "page_ids": "|".join(sorted({row["page"] for row in card_events})),
            "record_ids": "|".join(sorted({row["record_unit_id"] for row in card_events})),
            "surface_channel": "WITHHELD__NO_SURFACE_OR_COMPONENT_SELECTION",
            "selection_rule": "V80_INDEPENDENT_SOURCE_POSITIONS_GE_3__RANK_NEG_FREQUENCY_THEN_ID",
        }
    )

occurrence_rows: list[dict[str, object]] = []
ordinal: dict[str, int] = defaultdict(int)
for row in events:
    if row["joint_tuple_id"] not in target_id:
        continue
    tid = target_id[row["joint_tuple_id"]]
    ordinal[tid] += 1
    occurrence_rows.append(
        {
            "anonymous_target_id": tid,
            "occurrence_ordinal": ordinal[tid],
            "event_serial": row["event_serial"],
            "event_id": row["event_id"],
            "page": row["page"],
            "record_unit_id": row["record_unit_id"],
            "locus": row["locus"],
            "field_id": row["field_id"],
            "statement_id": row["statement_id"],
            "joint_tuple_id": row["joint_tuple_id"],
            "image_owner_id": row["image_owner_id"],
            "owner_break_before": row["owner_break_before"],
            "source_position_id": row["source_position_id"],
            "source_position_contribution": row["source_position_contribution"],
            "autonomous_operational_readback": row["autonomous_operational_readback"],
            "formal_nonword_channel": row["formal_nonword_channel"],
            "master_memorized_selected_token": row["master_memorized_selected_token"],
            "master_memorized_source_expansion_de": row["master_memorized_source_expansion_de"],
            "terminal_status": row["terminal_status"],
            "line_crossing": row["line_crossing"],
            "strongest_contradiction": row["strongest_contradiction"],
            "surface_channel": "WITHHELD__NO_SURFACE_OR_COMPONENT_SELECTION",
        }
    )

affected_statement_ids = {row["statement_id"] for row in occurrence_rows}
statement_rows: list[dict[str, object]] = []
for row in statements:
    if row["statement_id"] not in affected_statement_ids:
        continue
    selected_in_statement = [
        target_id[card]
        for card in row["exact_card_order"].split("|")
        if card in target_id
    ]
    statement_rows.append(
        {
            "statement_id": row["statement_id"],
            "record_unit_id": row["record_unit_id"],
            "page": row["page"],
            "constituent_fields": row["constituent_fields"],
            "physical_lines": row["physical_lines"],
            "visible_event_count": row["visible_event_count"],
            "target_occurrences": len(selected_in_statement),
            "anonymous_targets_in_order": "|".join(selected_in_statement),
            "operational_formal_order": row["operational_formal_order"],
            "optional_master_gloss_order": row["optional_master_gloss_order"],
            "master_memorized_statement_content": row["master_memorized_statement_content"],
            "rival_statement_content": row["rival_statement_content"],
            "strongest_contradiction": row["strongest_contradiction"],
            "semantic_ceiling": row["canonical_ceiling"],
        }
    )

manifest_path = HERE / "V81_TARGET_MANIFEST.tsv"
occurrence_path = HERE / "V81_TARGET_OCCURRENCE_PACKET.tsv"
statement_path = HERE / "V81_TARGET_AFFECTED_STATEMENTS.tsv"
write_tsv(manifest_path, list(manifest_rows[0]), manifest_rows)
write_tsv(occurrence_path, list(occurrence_rows[0]), occurrence_rows)
write_tsv(statement_path, list(statement_rows[0]), statement_rows)

checks = {
    "four_source_freezes": len(freezes) == 4,
    "target_cards_30": len(manifest_rows) == 30,
    "visible_occurrences_217": len(occurrence_rows) == 217,
    "independent_source_positions_216": sum(int(row["source_position_contribution"]) for row in occurrence_rows) == 216,
    "all_targets_ge_3": all(int(row["independent_source_positions"]) >= 3 for row in manifest_rows),
    "selection_order_exact": selected_cards == sorted(selected_cards, key=lambda row: (-int(row["independent_source_positions"]), row["joint_tuple_id"])),
    "surface_withheld": all(row["surface_channel"].startswith("WITHHELD") for row in manifest_rows + occurrence_rows),
    "fixed_pages_only": {row["page"] for row in occurrence_rows} <= {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"},
    "sealed_pages_absent": not any(row["page"].startswith("f84") for row in occurrence_rows),
    "affected_statements_complete": affected_statement_ids == {row["statement_id"] for row in statement_rows},
}

freeze_result = {
    "schema": "SIDEQUEST_V81_TARGET_PACKET_FREEZE_V1",
    "status": "PASS__FROZEN_AFTER_FOUR_SOURCE_FIRST_FREEZES" if all(checks.values()) else "FAIL",
    "checks": checks,
    "passed": sum(checks.values()),
    "total": len(checks),
    "counts": {
        "target_cards": len(manifest_rows),
        "visible_occurrences": len(occurrence_rows),
        "independent_source_positions": sum(int(row["source_position_contribution"]) for row in occurrence_rows),
        "affected_statements": len(statement_rows),
    },
    "selection": "V80_INDEPENDENT_SOURCE_POSITIONS_GE_3__RANK_NEG_FREQUENCY_THEN_ID",
    "source_freeze_hashes": {role: sha256(path) for role, (path, _) in freeze_specs.items()},
    "source_inventory_hashes": {role: sha256(path) for role, (_, path) in freeze_specs.items()},
    "input_hashes": {
        dictionary_path.name: sha256(dictionary_path),
        events_path.name: sha256(events_path),
        statements_path.name: sha256(statements_path),
        "SIDEQUEST_V81_ATOMIC_CODEBOOK_VOCABULARY_PROTOCOL.md": sha256(ROOT / "experiments/yolo/SIDEQUEST_V81_ATOMIC_CODEBOOK_VOCABULARY_PROTOCOL.md"),
    },
    "output_hashes": {
        manifest_path.name: sha256(manifest_path),
        occurrence_path.name: sha256(occurrence_path),
        statement_path.name: sha256(statement_path),
    },
    "blinding": {
        "source_inventories_frozen_before_target": True,
        "surface_spelling_withheld": True,
        "component_coordinates_withheld": True,
        "r3_old_v77_line_incident": "DISCLOSED__DOCUMENTARY_SOURCE_ELIGIBLE__STRICT_INDEPENDENCE_ADVISORY",
        "r4_prior_v80_context": "DISCLOSED__LOWER_BLINDNESS_WEIGHT",
    },
    "seals": {"f84": "SEALED_NOT_ACCESSED", "f84r": "SEALED_NOT_ACCESSED"},
    "next": "PHASE2_FOUR_INDEPENDENT_ATOMIC_MAPPING_AUDITS__NO_TARGET_EXPANSION",
}
(HERE / "V81_TARGET_FREEZE.json").write_text(
    json.dumps(freeze_result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)
print(f"{freeze_result['status']} {freeze_result['passed']}/{freeze_result['total']}")
raise SystemExit(0 if freeze_result["status"].startswith("PASS") else 1)
