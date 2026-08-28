#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent / "artifacts"
ROOT = Path(__file__).resolve().parents[4]
SOURCE = ROOT / "experiments/yolo/gdt605_multisymbol_unit_alphabet/src/separator_crossing.py"
spec = importlib.util.spec_from_file_location("gdt605_separator", SOURCE)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules[spec.name] = module
spec.loader.exec_module(module)


def row_chunks(row):
    tokens, separators = module.clean_source_line(row["ivtff_raw"])
    clean = row["eva_clean"].split()
    if tokens != clean or len(separators) != max(0, len(clean) - 1):
        return None
    if not clean:
        return []
    chunks = []
    current = module.collapse(clean[0])
    for separator, token in zip(separators, clean[1:]):
        if separator == "uncertain":
            current += module.collapse(token)
        else:
            chunks.append(current)
            current = module.collapse(token)
    chunks.append(current)
    return chunks


def main():
    rows = list(csv.DictReader((HERE / "guarded_rows.tsv").open(), delimiter="\t"))
    if any(row["page"].lower().startswith("f84") for row in rows):
        raise RuntimeError("forbidden selector")
    raw_chunks = {"train": [], "held": []}
    aligned = []
    unresolved = []
    for row in rows:
        chunks = row_chunks(row)
        if chunks is None:
            unresolved.append(row["locus"])
            continue
        aligned.append((row, chunks))
        raw_chunks[row["split"]].extend(chunks)
    rules, train_segmentations = module.learn_bpe(raw_chunks["train"], 64)
    sequences = {"train": [], "held": []}
    counts = {"train": Counter(), "held": Counter()}
    for row, chunks in aligned:
        for index, chunk in enumerate(chunks):
            units = (
                train_segmentations[chunk]
                if row["split"] == "train"
                else module.apply_bpe(chunk, rules)
            )
            counts[row["split"]].update(units)
            sequences[row["split"]].append({
                "page": row["page"],
                "physical_folio": row["physical_folio"],
                "locus": row["locus"],
                "chunk_index": index,
                "section": row["section"],
                "units": list(units),
            })
    inventory = sorted(counts["train"], key=lambda unit: (-counts["train"][unit], unit))
    if len(inventory) != 98 or set(counts["held"]) - set(inventory):
        raise RuntimeError("GDT605 inventory mismatch")
    output = {
        "schema": "gdt606-historical-secretary-unit-sequences-v1",
        "guarded_sha256": hashlib.sha256((HERE / "guarded_rows.tsv").read_bytes()).hexdigest(),
        "source_merges_sha256": "4625c9389ead390907e4ac74e65bc158236f02b439c69cf3b09157f0cd6ca539",
        "unresolved_loci": unresolved,
        "inventory": inventory,
        "frequency": {
            split: dict(counts[split]) for split in ("train", "held")
        },
        "sequences": sequences,
    }
    path = HERE / "unit_sequences.json"
    path.write_text(json.dumps(output, sort_keys=True, separators=(",", ":")) + "\n")
    print(json.dumps({
        "train_chunks": len(sequences["train"]),
        "held_chunks": len(sequences["held"]),
        "train_occurrences": sum(counts["train"].values()),
        "held_occurrences": sum(counts["held"].values()),
        "unit_types": len(inventory),
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
