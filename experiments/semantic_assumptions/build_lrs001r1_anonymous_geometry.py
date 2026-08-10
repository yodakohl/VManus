#!/usr/bin/env python3
"""Build label-free record geometry for LRS001-R1 synthetic calibration."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
R = HERE / "results"
SPEC = HERE / "LRS001R1_ANONYMOUS_GEOMETRY_SPEC.md"
CAPACITY = R / "lrs001r1_strict_masked_record_capacity.json"
ATLAS = R / "drawing_reset_segment_atlas.tsv"
SPLITS = R / "source_native_within_group_stage_masked.tsv"
OUT_TSV = R / "lrs001r1_anonymous_geometry.tsv"
OUT_JSON = R / "lrs001r1_anonymous_geometry.json"
OUT_REPORT = R / "lrs001r1_anonymous_geometry.md"
PRODUCER = Path(__file__).resolve()
CELL_FIELDS = (
    "page", "segment_group_count", "code", "segment_count", "segment_index",
    "starts_after_drawing", "ends_before_drawing", "group_count",
)
FIELDS = (
    "anonymous_group_id", "anonymous_record_id", "split", "page",
    "physical_folio", "section", "currier", "hand", "code", "kind",
    "segment_group_count", "segment_group_index", "segment_position",
    "segment_count", "segment_index", "starts_after_drawing",
    "ends_before_drawing", "original_group_count", "symbol_count",
    "supported_class_target", "strict_test_movable", "strict_cell_id",
    "strict_cell_record_count",
)
FORBIDDEN_FIELDS = {
    "family_surface", "zl_sta_codes", "it_sta_codes", "rf_sta_codes",
    "zl_basic_eva_lossy", "it_basic_eva_lossy", "rf_basic_eva_lossy",
    "transcription", "token", "root", "role", "english_gloss", "image",
    "ocr", "automated_vision",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def anon(domain: str, value: str) -> str:
    return domain + hashlib.sha256(("LRS001R1|" + domain + "|" + value).encode()).hexdigest()[:20]


def build() -> tuple[list[dict[str, str]], dict[str, object]]:
    capacity = json.loads(CAPACITY.read_text())
    if capacity["decision"] != "GO_TARGET_BLIND_CALIBRATION_ONLY":
        raise ValueError("capacity not authorized")
    eligible = {row["family_surface"] for row in capacity["capacity"]["eligible_surfaces"]}
    if len(eligible) != 66:
        raise ValueError("eligible class drift")

    split_map: dict[str, dict[str, str]] = {}
    with SPLITS.open(newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            if row["unit_id"] in split_map:
                raise ValueError("duplicate split")
            split_map[row["unit_id"]] = dict(row)
    if len(split_map) != 21_899:
        raise ValueError("split count")

    segments: dict[str, list[dict[str, str]]] = defaultdict(list)
    with ATLAS.open(newline="") as handle:
        for source in csv.DictReader(handle, delimiter="\t"):
            row = dict(source)
            if row["grammar_scope"] == "CONFIRMED_PROSE" and 5 <= int(row["segment_group_count"]) <= 12:
                segments[row["segment_id"]].append(row)
    for identifier, rows in segments.items():
        rows.sort(key=lambda row: int(row["segment_group_index"]))
        size = int(rows[0]["segment_group_count"])
        if len(rows) != size or [int(row["segment_group_index"]) for row in rows] != list(range(1, size + 1)):
            raise ValueError("incomplete record")
        if any(len({row[field] for row in rows}) != 1 for field in CELL_FIELDS):
            raise ValueError("cell drift")
        sources = [split_map[row["consensus_group_id"]] for row in rows]
        if len({row["split"] for row in sources}) != 1 or len({row["physical_folio"] for row in sources}) != 1:
            raise ValueError("fold drift")

    test_cells: dict[tuple[str, ...], list[str]] = defaultdict(list)
    for identifier, rows in segments.items():
        if split_map[rows[0]["consensus_group_id"]]["split"] == "TEST":
            test_cells[tuple(rows[0][field] for field in CELL_FIELDS)].append(identifier)
    for identifiers in test_cells.values():
        identifiers.sort()

    output: list[dict[str, str]] = []
    for identifier, rows in sorted(segments.items()):
        source = split_map[rows[0]["consensus_group_id"]]
        cell = tuple(rows[0][field] for field in CELL_FIELDS)
        cell_count = len(test_cells[cell]) if source["split"] == "TEST" else 0
        cell_id = anon("C", "\x1f".join(cell)) if source["split"] == "TEST" else ""
        for row in rows:
            joined = split_map[row["consensus_group_id"]]
            for field in ("page", "section", "currier", "hand", "kind", "symbol_count"):
                if row[field] != joined[field]:
                    raise ValueError("metadata drift")
            output.append({
                "anonymous_group_id": anon("G", row["consensus_group_id"]),
                "anonymous_record_id": anon("R", identifier),
                "split": source["split"], "page": row["page"],
                "physical_folio": source["physical_folio"], "section": row["section"],
                "currier": row["currier"], "hand": row["hand"], "code": row["code"],
                "kind": row["kind"], "segment_group_count": row["segment_group_count"],
                "segment_group_index": row["segment_group_index"],
                "segment_position": row["segment_position"], "segment_count": row["segment_count"],
                "segment_index": row["segment_index"],
                "starts_after_drawing": row["starts_after_drawing"],
                "ends_before_drawing": row["ends_before_drawing"],
                "original_group_count": row["group_count"], "symbol_count": row["symbol_count"],
                "supported_class_target": str(int(row["segment_position"] == "CORE" and row["family_surface"] in eligible)),
                "strict_test_movable": str(int(source["split"] == "TEST" and cell_count >= 2)),
                "strict_cell_id": cell_id, "strict_cell_record_count": str(cell_count),
            })
    if len({row["anonymous_group_id"] for row in output}) != len(output):
        raise ValueError("anonymous group collision")
    if set(FIELDS) & FORBIDDEN_FIELDS:
        raise ValueError("forbidden output field")
    targets = [row for row in output if row["supported_class_target"] == "1"]
    movable = [row for row in targets if row["split"] == "TEST" and row["strict_test_movable"] == "1"]
    counts = Counter(row["split"] for row in targets)
    manifest = {
        "experiment": "LRS001R1_anonymous_geometry",
        "status": "PASS_LABEL_FREE_GEOMETRY",
        "decision": "GO_TARGET_BLIND_SYNTHETIC_CALIBRATION_ONLY",
        "inputs": {str(path.relative_to(HERE)): sha(path) for path in (SPEC, CAPACITY, ATLAS, SPLITS)},
        "implementation": {str(PRODUCER.relative_to(HERE)): sha(PRODUCER)},
        "schema": list(FIELDS),
        "counts": {
            "rows": len(output), "records": len(segments),
            "supported_targets_by_split": dict(sorted(counts.items())),
            "strict_movable_test_targets": len(movable),
            "strict_movable_test_records": len({row["anonymous_record_id"] for row in movable}),
            "strict_test_cells": len({row["strict_cell_id"] for row in movable}),
        },
        "geometry_sha256": hashlib.sha256(canonical(output)).hexdigest(),
        "isolation": {
            "real_family_surface_field_emitted": False,
            "real_context_target_association_scored": False,
            "predictor_fitted": False,
            "ocr_or_automated_vision_used": False,
        },
        "claim_ceiling": "Anonymous geometry supplies no schema, field, word, meaning, plaintext, or translation.",
    }
    return output, manifest


def main() -> None:
    if any(path.exists() for path in (OUT_TSV, OUT_JSON, OUT_REPORT)):
        raise SystemExit("refusing to overwrite anonymous geometry artifacts")
    output, manifest = build()
    with OUT_TSV.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, delimiter="\t", lineterminator="\n")
        writer.writeheader(); writer.writerows(output)
    manifest["tsv_sha256"] = sha(OUT_TSV)
    OUT_JSON.write_bytes(canonical(manifest))
    c = manifest["counts"]
    OUT_REPORT.write_text(
        "# LRS001-R1 anonymous calibration geometry\n\nStatus: **PASS_LABEL_FREE_GEOMETRY**.\n\n"
        f"The label-free artifact contains {c['rows']:,} groups in {c['records']:,} records. "
        f"Supported target geometry is TRAIN/CAL/TEST {c['supported_targets_by_split']['TRAIN']}/"
        f"{c['supported_targets_by_split']['CAL']}/{c['supported_targets_by_split']['TEST']}; "
        f"the strict movable TEST panel is {c['strict_movable_test_targets']:,} targets in "
        f"{c['strict_movable_test_records']} records and {c['strict_test_cells']} cells.\n\n"
        "No family surface, member code, EVA, transcription token, parser root/role, image, OCR, gloss, predictor, or real association is present.\n\n"
        f"Claim ceiling: {manifest['claim_ceiling']}\n"
    )
    print(json.dumps({"status": manifest["status"], "rows": len(output)}, sort_keys=True))


if __name__ == "__main__":
    main()
