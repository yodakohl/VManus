#!/usr/bin/env python3
"""Audit the GDT609 EBNF scope against the frozen GDT612 planted world.

This is a labelled bridge diagnostic, not a new truth world and not a target
fit.  It compares the exact flattened-piece grammar with one explicitly
unregistered candidate repair: one or more adjacent complete CORE values may
occur wherever the published grammar permits one CORE.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

from fst import (
    CONNECTOR,
    CONTEXT,
    CORE_ROLES,
    LITERAL,
    NULL,
    PREFIX,
    SUFFIX,
    WHOLE,
    UnitTree,
    parse_pieces,
)


RELATIVE_INPUTS = {
    "units": Path(
        "experiments/yolo/gdt612_historical_fst34_target_attack/artifacts/units.tsv"
    ),
    "truth_primitives": Path(
        "experiments/yolo/gdt612_historical_fst34_target_attack/artifacts/"
        "synthetic_truth_primitives.tsv"
    ),
    "truth_overrides": Path(
        "experiments/yolo/gdt612_historical_fst34_target_attack/artifacts/"
        "synthetic_truth_overrides.tsv"
    ),
    "train": Path(
        "experiments/yolo/gdt612_historical_fst34_target_attack/artifacts/"
        "synthetic_train_chunks.tsv"
    ),
    "held": Path(
        "experiments/yolo/gdt612_historical_fst34_target_attack/artifacts/"
        "synthetic_held.tsv"
    ),
}

EXPECTED_HASHES = {
    "units": "8fc32a38dbe47a5d738698ccccd7289fe3d533e9e5d870624da11f0fc5d19180",
    "truth_primitives": "0529bdee6f70e54ea5b3cfabfff863e50002547e03e2509601cebaaa7cfe79ac",
    "truth_overrides": "a789a39518a50090c1c9e6c6843bf306759b295f1488e65b8dadc4510ff2de04",
    "train": "dc6a154345d82772d32d8d7f100a81b8d48af622b9b2323f44bbdcfacc3010cd",
    "held": "588d0b269102f96f7a1db3d0c9967e83a87e2c6cb8da03fa08cbb0e6fd3033de",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, fields: list[str], rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=fields, delimiter="\t", lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)


def parse_core(roles: list[str], position: int) -> int | None:
    if position >= len(roles):
        return None
    if (
        roles[position] == CONTEXT
        and position + 1 < len(roles)
        and roles[position + 1] == LITERAL
    ):
        return position + 2
    if (
        roles[position] == LITERAL
        and position + 1 < len(roles)
        and roles[position + 1] == CONTEXT
    ):
        return position + 2
    if roles[position] in CORE_ROLES:
        return position + 1
    return None


def parse_core_run(roles: list[str], position: int) -> tuple[int, int]:
    count = 0
    while True:
        following = parse_core(roles, position)
        if following is None:
            return position, count
        position = following
        count += 1


def parse_run_body(roles: list[str]) -> bool:
    if roles == [WHOLE]:
        return True
    position = 0
    prefixes = 0
    while position < len(roles) and roles[position] == PREFIX and prefixes < 2:
        position += 1
        prefixes += 1
    position, core_count = parse_core_run(roles, position)
    if core_count == 0:
        return False
    connectors = 0
    while position < len(roles) and roles[position] == CONNECTOR and connectors < 3:
        following, following_count = parse_core_run(roles, position + 1)
        if following_count == 0:
            break
        position = following
        connectors += 1
    suffixes = 0
    while position < len(roles) and roles[position] == SUFFIX and suffixes < 2:
        position += 1
        suffixes += 1
    return position == len(roles)


def parse_core_run_roles(roles: list[str]) -> tuple[bool, str]:
    left = 0
    while left < len(roles) and roles[left] == NULL:
        left += 1
    right = len(roles)
    while right > left and roles[right - 1] == NULL:
        right -= 1
    interior = roles[left:right]
    if NULL in interior:
        return False, "interior_null"
    if not interior:
        return False, "empty"
    if interior == [CONNECTOR]:
        return True, "connector_only"
    if interior == [CONNECTOR, SUFFIX]:
        return True, "boundary_compound"
    body = list(interior)
    if body and body[0] == CONNECTOR:
        body = body[1:]
    if body and body[-1] == CONNECTOR:
        body = body[:-1]
    legal = parse_run_body(body)
    return legal, "body" if legal else "illegal_body"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(
            "experiments/yolo/gdt613_observation_complete_fst34_recovery/artifacts"
        ),
    )
    args = parser.parse_args()
    repo = args.repo.resolve()
    out = args.out if args.out.is_absolute() else repo / args.out
    out.mkdir(parents=True, exist_ok=True)
    paths = {name: repo / relative for name, relative in RELATIVE_INPUTS.items()}
    actual_hashes = {name: sha256(path) for name, path in paths.items()}
    if actual_hashes != EXPECTED_HASHES:
        raise SystemExit(f"input drift: {actual_hashes}")

    primitive_mapping = {
        int(row["primitive_id"]): (
            row["role"],
            "" if row["output"] == "<EMPTY>" else row["output"],
        )
        for row in read_tsv(paths["truth_primitives"])
    }
    overrides = {
        int(row["unit_id"]): (row["type"], row["output"])
        for row in read_tsv(paths["truth_overrides"])
    }
    tree = UnitTree(paths["units"])
    summary_rows: list[dict] = []
    failure_rows: list[dict] = []
    for split_name, input_name, weight_field in (
        ("train", "train", "count"),
        ("held", "held", None),
    ):
        rows = read_tsv(paths[input_name])
        totals = {"types": len(rows), "events": 0}
        variants = {
            "GDT609_EXACT_SINGLE_CORE": Counter(),
            "DIAGNOSTIC_V2_ADJACENT_CORE_RUN": Counter(),
        }
        for row in rows:
            units = [int(value) for value in row["units"].split(",")]
            pieces = tuple(
                piece
                for uid in units
                for piece in tree.pieces(uid, primitive_mapping, overrides)
            )
            roles = [piece.role for piece in pieces if piece.output or piece.role == NULL]
            weight = int(row[weight_field]) if weight_field else 1
            totals["events"] += weight
            exact = parse_pieces(pieces)
            run_legal, run_reason = parse_core_run_roles(roles)
            for model, legal, reason in (
                ("GDT609_EXACT_SINGLE_CORE", exact.legal, exact.reason),
                ("DIAGNOSTIC_V2_ADJACENT_CORE_RUN", run_legal, run_reason),
            ):
                variants[model]["legal_types"] += int(legal)
                variants[model]["legal_events"] += weight * int(legal)
                variants[model][f"reason_types::{reason}"] += 1
                variants[model][f"reason_events::{reason}"] += weight
                if not legal:
                    failure_rows.append(
                        {
                            "split": split_name,
                            "model": model,
                            "record_id": row.get("chunk_id", row.get("record_id", "")),
                            "weight": weight,
                            "unit_ids": row["units"],
                            "unit_names": row["unit_names"],
                            "roles": ",".join(roles),
                            "reason": reason,
                        }
                    )
        for model, counts in variants.items():
            summary_rows.append(
                {
                    "split": split_name,
                    "model": model,
                    "legal_types": counts["legal_types"],
                    "total_types": totals["types"],
                    "legal_type_rate": f"{counts['legal_types'] / totals['types']:.12f}",
                    "legal_events": counts["legal_events"],
                    "total_events": totals["events"],
                    "legal_event_rate": f"{counts['legal_events'] / totals['events']:.12f}",
                    "illegal_body_events": counts["reason_events::illegal_body"],
                    "interior_null_events": counts["reason_events::interior_null"],
                }
            )

    write_tsv(
        out / "grammar_scope_bridge.tsv",
        list(summary_rows[0]),
        summary_rows,
    )
    write_tsv(
        out / "grammar_scope_failures.tsv",
        [
            "split",
            "model",
            "record_id",
            "weight",
            "unit_ids",
            "unit_names",
            "roles",
            "reason",
        ],
        failure_rows,
    )
    exact_train = next(
        row
        for row in summary_rows
        if row["split"] == "train" and row["model"] == "GDT609_EXACT_SINGLE_CORE"
    )
    run_train = next(
        row
        for row in summary_rows
        if row["split"] == "train"
        and row["model"] == "DIAGNOSTIC_V2_ADJACENT_CORE_RUN"
    )
    result = {
        "schema": "gdt613-grammar-scope-bridge-v1",
        "status": "EXACT_SCOPE_MISMATCH_ON_OLD_PLANTED_WORLD",
        "claim_ceiling": "post-run diagnostic only; no target, meaning, or model repair",
        "inputs_sha256": actual_hashes,
        "models": {
            "exact": "published GDT609 flattened-piece EBNF with one CORE per unconnected body segment",
            "diagnostic_v2": "unregistered adjacent complete CORE run at each exact CORE position",
        },
        "summary": summary_rows,
        "decision": (
            "GDT613 must solve exact-scope natural-world feasibility or stop; "
            "the diagnostic run grammar requires a new model identifier"
        ),
        "headline": {
            "exact_train_legal_events": exact_train["legal_events"],
            "exact_train_total_events": exact_train["total_events"],
            "diagnostic_run_train_legal_events": run_train["legal_events"],
            "diagnostic_run_train_total_events": run_train["total_events"],
        },
    }
    (out / "grammar_scope_bridge.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(result["headline"], sort_keys=True))


if __name__ == "__main__":
    main()
