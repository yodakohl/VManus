#!/usr/bin/env python3
"""Build the train-only, boundary-aware 98-unit GDT605 inventory."""
from __future__ import annotations

import argparse
import collections
import csv
import hashlib
import json
from pathlib import Path

from separator_crossing import (
    EXPECTED_GUARDED_SHA256,
    SUBSTITUTIONS,
    apply_bpe,
    clean_source_line,
    collapse,
    learn_bpe,
    sha256_path,
)


def hard_chunks(row: dict[str, str]) -> list[str] | None:
    tokens, separators = clean_source_line(row["ivtff_raw"])
    clean = row["eva_clean"].split()
    if tokens != clean or len(separators) != max(0, len(clean) - 1):
        return None
    if not clean:
        return []
    chunks = []
    current = collapse(clean[0])
    for separator, token in zip(separators, clean[1:]):
        if separator == "uncertain":
            current += collapse(token)
        else:
            chunks.append(current)
            current = collapse(token)
    chunks.append(current)
    return chunks


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--guarded-rows", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--merges", type=int, default=64)
    args = parser.parse_args()
    if sha256_path(args.guarded_rows) != EXPECTED_GUARDED_SHA256:
        raise SystemExit("guarded row hash changed")
    args.output_dir.mkdir(parents=True, exist_ok=True)

    with args.guarded_rows.open(newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    if any(row["page"].lower().startswith("f84") for row in rows):
        raise SystemExit("forbidden selector present")
    chunks = {"train": [], "held": []}
    row_counts = collections.Counter()
    unresolved = []
    for row in rows:
        values = hard_chunks(row)
        if values is None:
            unresolved.append(row["locus"])
            continue
        row_counts[row["split"]] += 1
        chunks[row["split"]].extend(values)

    rules, train_segmentations = learn_bpe(chunks["train"], args.merges)
    unit_counts = {}
    for split in ("train", "held"):
        counter = collections.Counter()
        for chunk in chunks[split]:
            units = (
                train_segmentations[chunk]
                if split == "train"
                else apply_bpe(chunk, rules)
            )
            counter.update(units)
        unit_counts[split] = counter

    fields = [
        "unit", "train_occurrences", "held_occurrences", "collapsed_glyph_length",
        "seen_in_train", "seen_in_held",
    ]
    inventory_rows = []
    all_units = sorted(
        set(unit_counts["train"]) | set(unit_counts["held"]),
        key=lambda unit: (-unit_counts["train"][unit], unit),
    )
    for unit in all_units:
        inventory_rows.append({
            "unit": unit,
            "train_occurrences": unit_counts["train"][unit],
            "held_occurrences": unit_counts["held"][unit],
            "collapsed_glyph_length": len(unit),
            "seen_in_train": int(unit in unit_counts["train"]),
            "seen_in_held": int(unit in unit_counts["held"]),
        })
    inventory_path = args.output_dir / "gdt605_unit_inventory.tsv"
    with inventory_path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(inventory_rows)

    merge_path = args.output_dir / "gdt605_bpe_merges.tsv"
    with merge_path.open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=("rank", "left", "right", "merged", "train_occurrences"),
            delimiter="\t",
            lineterminator="\n",
        )
        writer.writeheader()
        for rank, (left, right, merged, count) in enumerate(rules, 1):
            writer.writerow({
                "rank": rank, "left": left, "right": right,
                "merged": merged, "train_occurrences": count,
            })

    split_stats = {}
    for split in ("train", "held"):
        counter = unit_counts[split]
        total_units = sum(counter.values())
        glyphs = sum(map(len, chunks[split]))
        split_stats[split] = {
            "aligned_rows": row_counts[split],
            "hard_boundary_chunks": len(chunks[split]),
            "collapsed_glyphs": glyphs,
            "unit_occurrences": total_units,
            "unit_types": len(counter),
            "mean_collapsed_glyphs_per_unit": glyphs / total_units,
        }
    result = {
        "schema": "gdt605-boundary-aware-unit-inventory-v1",
        "guarded_rows_sha256": EXPECTED_GUARDED_SHA256,
        "configuration": {
            "composites": SUBSTITUTIONS,
            "bpe_merges": args.merges,
            "uncertain_separator": "JOIN_BEFORE_BPE",
            "certain_separator": "HARD_BOUNDARY",
            "drawing_interruption": "HARD_BOUNDARY",
            "training": "68 physical folios",
            "held": "23 physical folios",
        },
        "rows": len(rows),
        "unresolved_rows": len(unresolved),
        "unresolved_loci": unresolved,
        "splits": split_stats,
        "held_unseen_unit_types": sorted(
            set(unit_counts["held"]) - set(unit_counts["train"])
        ),
        "artifacts": {
            inventory_path.name: sha256_path(inventory_path),
            merge_path.name: sha256_path(merge_path),
        },
        "decision": "STABLE_98_UNIT_BOUNDARY_AWARE_ALPHABET",
        "claim_ceiling": (
            "A stable collapsed-glyph unit inventory and separator treatment only; "
            "units are not yet plaintext letters, syllables, words, sounds or meanings."
        ),
        "sealed_data": {"f84": "FORBIDDEN_AND_ABSENT", "f84r": "FORBIDDEN_AND_ABSENT"},
    }
    result_path = args.output_dir / "gdt605_unit_result.json"
    result_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({
        "decision": result["decision"],
        "splits": split_stats,
        "held_unseen_unit_types": result["held_unseen_unit_types"],
        "result_sha256": hashlib.sha256(result_path.read_bytes()).hexdigest(),
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
