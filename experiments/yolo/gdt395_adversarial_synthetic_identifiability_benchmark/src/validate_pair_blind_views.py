#!/usr/bin/env python3
"""Validate GDT395 record-local pair views without reading sealed truth."""

from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
EXP = ROOT / "experiments/yolo/gdt395_adversarial_synthetic_identifiability_benchmark"
MATCHES = EXP / "artifacts/gdt395_pair_matched_records.tsv"


def read(path: Path) -> list[dict]:
    with gzip.open(path, "rt", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def recurrence(rows: list[dict]) -> tuple[float, float, float]:
    counts = Counter(row["visible_group"] for row in rows)
    return (
        len(counts) / len(rows),
        max(counts.values()) / len(rows),
        sum(value == 1 for value in counts.values()) / len(counts),
    )


def line_profile(rows: list[dict]) -> tuple[int, ...]:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        grouped[row["line_id"]].append(row)
    return tuple(len(grouped[key]) for key in sorted(grouped, key=lambda key: min(int(r["event_index"]) for r in grouped[key])))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--corpus-dir", type=Path, default=EXP / ".work/corpora")
    parser.add_argument("--pair-dir", type=Path, default=EXP / ".work/pair_blind")
    parser.add_argument("--output", type=Path, default=EXP / "artifacts/gdt395_pair_blind_validation.json")
    args = parser.parse_args()
    with MATCHES.open(newline="") as handle:
        match_rows = list(csv.DictReader(handle, delimiter="\t"))
    with (args.pair_dir / "pair_blind_manifest.tsv").open(newline="") as handle:
        manifest = list(csv.DictReader(handle, delimiter="\t"))
    choices: dict[tuple[str, int], list[dict]] = defaultdict(list)
    for row in match_rows:
        for side in ("left", "right"):
            choices[(row[f"{side}_world"], int(row["corpus_seed"]))].append({
                "pair_id": row["pair_id"],
                "pair_ordinal": int(row["pair_ordinal"]),
                "record_id": row[f"{side}_record_id"],
            })
    checks = {
        "manifest_80_views": len(manifest) == 80,
        "manifest_hashes": True,
        "selection_event_identity": True,
        "injective_equality_partition": True,
        "masked_channels": True,
        "fixed_width": True,
        "ten_complete_records": True,
        "pair_local_carrier_exact": True,
        "pair_recurrence_gate": True,
    }
    panels = {}
    for item in manifest:
        world, seed = item["world_id"], int(item["corpus_seed"])
        pair_path = args.pair_dir / item["observation_relpath"]
        checks["manifest_hashes"] &= hashlib.sha256(pair_path.read_bytes()).hexdigest() == item["observation_sha256"]
        main_path = args.corpus_dir / "blind" / world / f"seed_{seed:02d}.tsv.gz"
        source = read(main_path)
        view = read(pair_path)
        selected_ids = {choice["record_id"] for choice in choices[(world, seed)]}
        selected = [row for row in source if row["record_id"] in selected_ids]
        checks["selection_event_identity"] &= {row["event_id"] for row in selected} == {row["event_id"] for row in view}
        by_event = {row["event_id"]: row for row in view}
        forward = defaultdict(set)
        reverse = defaultdict(set)
        for row in selected:
            forward[row["visible_group"]].add(by_event[row["event_id"]]["visible_group"])
            reverse[by_event[row["event_id"]]["visible_group"]].add(row["visible_group"])
        checks["injective_equality_partition"] &= all(len(values) == 1 for values in forward.values()) and all(len(values) == 1 for values in reverse.values())
        checks["masked_channels"] &= all(
            row["page_id"] == row["paragraph_id"] == row["register_id"] == row["hand_id"] == row["layout_role"] == "NONCOMPARABLE"
            for row in view
        )
        checks["fixed_width"] &= all(len(row["visible_group"]) == 16 for row in view)
        view_records: dict[str, list[dict]] = defaultdict(list)
        for row in view:
            view_records[row["record_id"]].append(row)
        checks["ten_complete_records"] &= len(view_records) == 10
        panels[(item["pair_id"], seed, world)] = (view, view_records)
    for pair_id, left, right in (("PAIR_CODEBOOK", "W02", "W03"), ("PAIR_SEMANTIC", "W09", "W10")):
        for seed in range(20):
            left_rows, left_records = panels[(pair_id, seed, left)]
            right_rows, right_records = panels[(pair_id, seed, right)]
            for ordinal in range(10):
                lr = next(rows for rid, rows in left_records.items() if rid.endswith(f"R{ordinal:02d}"))
                rr = next(rows for rid, rows in right_records.items() if rid.endswith(f"R{ordinal:02d}"))
                left_seps = Counter(row["separator_before"] for row in lr)
                right_seps = Counter(row["separator_before"] for row in rr)
                checks["pair_local_carrier_exact"] &= (
                    len(lr) == len(rr)
                    and line_profile(lr) == line_profile(rr)
                    and left_seps == right_seps
                    and sum(row["ambiguous_boundary"] == "TRUE" for row in lr) == sum(row["ambiguous_boundary"] == "TRUE" for row in rr)
                )
            delta = [abs(a - b) for a, b in zip(recurrence(left_rows), recurrence(right_rows))]
            checks["pair_recurrence_gate"] &= max(delta) <= 0.1000001
    result = {
        "schema": "GDT395_PAIR_BLIND_VIEW_VALIDATION_V1",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "checks_passed": sum(checks.values()),
        "checks_total": len(checks),
        "pair_manifest_sha256": hashlib.sha256((args.pair_dir / "pair_blind_manifest.tsv").read_bytes()).hexdigest(),
        "oracle_files_opened": 0,
        "voynich_rows": 0,
        "f84": {"opened": False, "parsed": False, "retained": False, "scored": False},
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print({"status": result["status"], "checks": f"{result['checks_passed']}/{result['checks_total']}"})
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
