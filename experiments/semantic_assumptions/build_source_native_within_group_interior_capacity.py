#!/usr/bin/env python3
"""Derive the score-blind interior-only capacity from the frozen stage panel."""

from __future__ import annotations

import csv
import hashlib
import io
import json
from collections import Counter
from pathlib import Path


BASE = Path(__file__).resolve().parent
RESULTS = BASE / "results"
SOURCE = RESULTS / "source_native_within_group_stage_masked.tsv"
SOURCE_VALIDATION = RESULTS / "source_native_within_group_stage_capacity_validation.json"
SPEC = BASE / "SOURCE_NATIVE_WITHIN_GROUP_INTERIOR_CAPACITY_SPEC.md"
BUILDER = Path(__file__).resolve()
PANEL = RESULTS / "source_native_within_group_interior_masked.tsv"
OUT = RESULTS / "source_native_within_group_interior_capacity.json"
REPORT = RESULTS / "source_native_within_group_interior_capacity_report.md"
FROZEN = {
    SOURCE: "16d7395ae0410c8fc72b5e5462d6d425cd3a2685e7ea70eee0677bd936106ae5",
    SOURCE_VALIDATION: "2a95ce3183b72540f39a8ef0f68129d1f7ccf2e688683a9f2989360f84c20007",
}
SOURCE_FIELDS = ("unit_id", "locus", "page", "physical_folio", "section", "currier", "hand", "kind", "symbol_count", "split")
FIELDS = ("unit_id", "locus", "page", "physical_folio", "section", "currier", "hand", "kind", "original_symbol_count", "interior_symbol_count", "split")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def render(rows: list[dict]) -> bytes:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=FIELDS, delimiter="\t", lineterminator="\n")
    writer.writeheader(); writer.writerows(rows)
    return stream.getvalue().encode()


def main() -> None:
    if any(path.exists() for path in (PANEL, OUT, REPORT)):
        raise SystemExit("refusing to overwrite within-group interior capacity")
    for path, expected in FROZEN.items():
        if sha(path) != expected:
            raise SystemExit(f"frozen interior-capacity input mismatch: {path.name}")
    if json.loads(SOURCE_VALIDATION.read_text())["status"] != "PASS_INDEPENDENT_SCORE_BLIND_STAGE_CAPACITY_RECONSTRUCTION":
        raise SystemExit("stage capacity validation is not PASS")
    with SOURCE.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        if tuple(reader.fieldnames or ()) != SOURCE_FIELDS:
            raise ValueError("stage masked-panel schema drift")
        source_rows = list(reader)
    rows = []
    for source in source_rows:
        length = int(source["symbol_count"])
        if length < 3:
            continue
        rows.append({
            "unit_id": source["unit_id"], "locus": source["locus"], "page": source["page"],
            "physical_folio": source["physical_folio"], "section": source["section"],
            "currier": source["currier"], "hand": source["hand"], "kind": source["kind"],
            "original_symbol_count": str(length), "interior_symbol_count": str(length - 2),
            "split": source["split"],
        })
    if len(rows) != len({row["unit_id"] for row in rows}):
        raise ValueError("duplicate interior capacity unit")
    panel_bytes = render(rows)
    PANEL.write_bytes(panel_bytes)
    split_groups = Counter(row["split"] for row in rows)
    split_symbols = Counter()
    split_folios = {}
    split_currier = {}
    for split in ("TRAIN", "CAL", "TEST"):
        selected = [row for row in rows if row["split"] == split]
        split_symbols[split] = sum(int(row["interior_symbol_count"]) for row in selected)
        split_folios[split] = len({row["physical_folio"] for row in selected})
        split_currier[split] = dict(sorted(Counter(row["currier"] for row in selected).items()))
    lengths = Counter(int(row["original_symbol_count"]) for row in rows)
    gates = {
        "exact_19203_groups": len(rows) == 19203,
        "exact_45867_interior_symbols": sum(int(row["interior_symbol_count"]) for row in rows) == 45867,
        "exact_94_folios": len({row["physical_folio"] for row in rows}) == 94,
        "exact_split_groups": split_groups == {"TRAIN": 9364, "CAL": 4887, "TEST": 4952},
        "exact_split_symbols": split_symbols == {"TRAIN": 22260, "CAL": 11693, "TEST": 11914},
        "exact_split_folios": split_folios == {"TRAIN": 47, "CAL": 23, "TEST": 24},
        "both_curriers_each_split": all(set(split_currier[split]) == {"A", "B"} and min(split_currier[split].values()) >= 1000 for split in split_currier),
        "original_length_range_3_to_11": min(lengths) == 3 and max(lengths) == 11,
        "target_fields_absent": not ({"family_surface", "interior_surface", "member_codes", "position", "score", "stage", "english_gloss"} & set(FIELDS)),
    }
    if not all(gates.values()):
        raise ValueError("within-group interior capacity gate failure")
    result = {
        "experiment": "SOURCE_NATIVE_WITHIN_GROUP_INTERIOR_CAPACITY",
        "status": "PASS_SCORE_BLIND_WITHIN_GROUP_INTERIOR_CAPACITY",
        "inputs": {path.name: sha(path) for path in (*FROZEN, SPEC, BUILDER)},
        "groups": len(rows), "interior_symbols": sum(int(row["interior_symbol_count"]) for row in rows),
        "physical_folios": len({row["physical_folio"] for row in rows}),
        "split_group_counts": dict(sorted(split_groups.items())),
        "split_interior_symbol_counts": dict(sorted(split_symbols.items())),
        "split_folio_counts": split_folios, "split_currier_counts": split_currier,
        "original_length_distribution": {str(key): lengths[key] for key in sorted(lengths)},
        "schema": list(FIELDS), "panel_sha256": hashlib.sha256(panel_bytes).hexdigest(), "gates": gates,
        "target_sequences_stored": 0, "target_scores_computed": 0, "english_glosses": 0,
        "claim_ceiling": "Score-blind capacity for an endpoint-free, exact-length-conditioned interior-position test. No morphology, sound, word, language, meaning, plaintext, cipher, or translation follows.",
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    REPORT.write_text(f"""# Source-native within-group interior-position capacity

Status: **{result['status']}**

After removing groups too short to have an interior, the masked panel retains
**{len(rows):,} groups**, **{result['interior_symbols']:,} interior symbols**,
and all **94** physical folios. TRAIN/CAL/TEST contain
**{split_groups['TRAIN']:,}/{split_groups['CAL']:,}/{split_groups['TEST']:,}**
groups and **{split_symbols['TRAIN']:,}/{split_symbols['CAL']:,}/{split_symbols['TEST']:,}**
interior symbols.

The panel contains identity, metadata, original/interior length, and split
only. It stores zero endpoint or interior family values, scores, stages, or
glosses. This authorizes only target-free calibration of an endpoint-free,
exact-length-conditioned positional model.
""")
    print(json.dumps({"status": result["status"], "groups": len(rows), "interior_symbols": result["interior_symbols"]}, sort_keys=True))


if __name__ == "__main__":
    main()
