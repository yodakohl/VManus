#!/usr/bin/env python3
"""Build the score-blind LRS001 masked-record capacity artifact."""

from __future__ import annotations

import csv
import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
SPEC = HERE / "LRS001_SOURCE_NATIVE_MASKED_RECORD_CAPACITY_SPEC.md"
SEGMENTS = RESULTS / "drawing_reset_segment_atlas.tsv"
SPLITS = RESULTS / "source_native_within_group_stage_masked.tsv"
OUT_JSON = RESULTS / "lrs001_source_native_masked_record_capacity.json"
OUT_REPORT = RESULTS / "lrs001_source_native_masked_record_capacity.md"
PRODUCER = Path(__file__).resolve()

CLAIM_CEILING = (
    "Capacity establishes only that a held source-native masked-record test is "
    "possible; it supplies no record schema, word, part of speech, recipe "
    "field, language, sound, cipher, plaintext, or translation."
)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def canonical_bytes(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def load_split_map() -> dict[str, dict[str, str]]:
    rows: dict[str, dict[str, str]] = {}
    with SPLITS.open(newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            key = row["unit_id"]
            if key in rows:
                raise ValueError(f"duplicate split unit_id: {key}")
            split = row["split"]
            if split not in {"TRAIN", "CAL", "TEST"}:
                raise ValueError(f"bad split: {split}")
            rows[key] = dict(row)
    if len(rows) != 21_899:
        raise ValueError(f"unexpected split rows: {len(rows)}")
    return rows


def load_segments(split_map: dict[str, dict[str, str]]) -> dict[str, list[dict[str, str]]]:
    segments: dict[str, list[dict[str, str]]] = defaultdict(list)
    with SEGMENTS.open(newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            if row["grammar_scope"] != "CONFIRMED_PROSE":
                continue
            length = int(row["segment_group_count"])
            if not 5 <= length <= 12:
                continue
            key = row["consensus_group_id"]
            if key not in split_map:
                raise ValueError(f"missing split join: {key}")
            if not row["family_surface"] or int(row["symbol_count"]) <= 0:
                raise ValueError(f"empty/invalid complete surface: {key}")
            segments[row["segment_id"]].append(row)

    seen_groups: set[str] = set()
    for segment_id, rows in segments.items():
        rows.sort(key=lambda row: int(row["segment_group_index"]))
        expected = int(rows[0]["segment_group_count"])
        positions = [int(row["segment_group_index"]) for row in rows]
        if len(rows) != expected or positions != list(range(1, expected + 1)):
            raise ValueError(f"noncomplete segment: {segment_id}")
        expected_positions = ["FIRST"] + ["CORE"] * (expected - 2) + ["LAST"]
        if [row["segment_position"] for row in rows] != expected_positions:
            raise ValueError(f"position-role drift: {segment_id}")
        if any(row["segment_id"] != segment_id for row in rows):
            raise ValueError(f"segment drift: {segment_id}")
        split_values = {split_map[row["consensus_group_id"]]["split"] for row in rows}
        folio_values = {split_map[row["consensus_group_id"]]["physical_folio"] for row in rows}
        if len(split_values) != 1 or len(folio_values) != 1:
            raise ValueError(f"split/folio drift inside {segment_id}")
        for row in rows:
            key = row["consensus_group_id"]
            if key in seen_groups:
                raise ValueError(f"group appears in two segments: {key}")
            split_row = split_map[key]
            for field in ("page", "section", "currier", "hand", "kind", "symbol_count"):
                if row[field] != split_row[field]:
                    raise ValueError(f"{field} join drift: {key}")
            seen_groups.add(key)
    return dict(segments)


def build() -> dict[str, object]:
    split_map = load_split_map()
    segments = load_segments(split_map)

    segment_counts = Counter()
    core_counts = Counter()
    length_counts = Counter()
    train_surface_counts = Counter()
    train_surface_folios: dict[str, set[str]] = defaultdict(set)

    for rows in segments.values():
        split_row = split_map[rows[0]["consensus_group_id"]]
        split, folio = split_row["split"], split_row["physical_folio"]
        segment_counts[split] += 1
        length_counts[int(rows[0]["segment_group_count"])] += 1
        for row in rows:
            if row["segment_position"] != "CORE":
                continue
            core_counts[split] += 1
            if split == "TRAIN":
                surface = row["family_surface"]
                train_surface_counts[surface] += 1
                train_surface_folios[surface].add(folio)

    eligible = sorted(
        surface
        for surface, count in train_surface_counts.items()
        if count >= 20 and len(train_surface_folios[surface]) >= 10
    )

    test_cells: dict[tuple[str, int], list[str]] = defaultdict(list)
    for segment_id, rows in segments.items():
        split = split_map[rows[0]["consensus_group_id"]]["split"]
        if split == "TEST":
            test_cells[(rows[0]["page"], int(rows[0]["segment_group_count"]))].append(segment_id)
    for value in test_cells.values():
        value.sort()

    target_rows: list[dict[str, str]] = []
    for segment_id, rows in sorted(segments.items()):
        split_row = split_map[rows[0]["consensus_group_id"]]
        split, folio = split_row["split"], split_row["physical_folio"]
        if split != "TEST":
            continue
        cell = (rows[0]["page"], int(rows[0]["segment_group_count"]))
        if len(test_cells[cell]) < 2:
            continue
        for row in rows:
            if row["segment_position"] == "CORE" and row["family_surface"] in eligible:
                target_rows.append(
                    {
                        "target_id": row["consensus_group_id"],
                        "segment_id": segment_id,
                        "page": row["page"],
                        "physical_folio": folio,
                        "section": row["section"],
                        "currier": row["currier"],
                        "hand": row["hand"],
                        "segment_group_count": row["segment_group_count"],
                        "segment_group_index": row["segment_group_index"],
                        "symbol_count": row["symbol_count"],
                        "family_surface": row["family_surface"],
                        "cell_record_count": str(len(test_cells[cell])),
                    }
                )

    target_ids = [row["target_id"] for row in target_rows]
    if len(target_ids) != len(set(target_ids)):
        raise ValueError("duplicate target ID")

    section_counts = Counter(row["section"] for row in target_rows)
    currier_counts = Counter(row["currier"] for row in target_rows)
    folio_counts = Counter(row["physical_folio"] for row in target_rows)
    target_surfaces = {row["family_surface"] for row in target_rows}
    used_cells = {
        (row["page"], int(row["segment_group_count"])) for row in target_rows
    }
    log2_permutation_capacity = sum(
        math.lgamma(len(test_cells[cell]) + 1) / math.log(2.0) for cell in used_cells
    )
    largest_folio_fraction = max(folio_counts.values()) / len(target_rows)

    gates = {
        "at_least_1500_movable_test_targets": len(target_rows) >= 1_500,
        "at_least_400_target_bearing_segments": len({row["segment_id"] for row in target_rows}) >= 400,
        "at_least_40_test_pages": len({row["page"] for row in target_rows}) >= 40,
        "at_least_20_test_physical_folios": len(folio_counts) >= 20,
        "at_least_250_each_currier_A_B": all(currier_counts[state] >= 250 for state in ("A", "B")),
        "at_least_250_each_section_B_H_S": all(section_counts[state] >= 250 for state in ("B", "H", "S")),
        "largest_folio_fraction_below_020": largest_folio_fraction < 0.20,
        "every_eligible_surface_in_movable_test": target_surfaces == set(eligible),
        "permutation_capacity_at_least_64_bits": log2_permutation_capacity >= 64.0,
    }
    passed = all(gates.values())

    eligible_records = [
        {
            "family_surface": surface,
            "train_core_occurrences": train_surface_counts[surface],
            "train_physical_folios": len(train_surface_folios[surface]),
        }
        for surface in eligible
    ]
    eligible_records_sha = hashlib.sha256(canonical_bytes(eligible_records)).hexdigest()
    target_panel_sha = hashlib.sha256(canonical_bytes(target_rows)).hexdigest()

    return {
        "experiment": "LRS001_source_native_masked_record_capacity",
        "status": "PASS_CAPACITY_FREEZE_SYNTHETIC_CALIBRATION_AUTHORIZED" if passed else "STOP_CAPACITY_INSUFFICIENT",
        "decision": "GO_TARGET_BLIND_CALIBRATION_ONLY" if passed else "STOP_UNSCORED",
        "inputs": {
            str(SPEC.relative_to(HERE)): sha256(SPEC),
            str(SEGMENTS.relative_to(HERE)): sha256(SEGMENTS),
            str(SPLITS.relative_to(HERE)): sha256(SPLITS),
        },
        "implementation": {
            str(PRODUCER.relative_to(HERE)): sha256(PRODUCER),
        },
        "rules": {
            "grammar_scope": "CONFIRMED_PROSE",
            "segment_group_count_min": 5,
            "segment_group_count_max": 12,
            "target_position": "CORE",
            "train_core_occurrence_min": 20,
            "train_physical_folio_min": 10,
            "null_cell": ["page", "segment_group_count"],
            "null_unit": "whole_donor_record_context_synchronous",
        },
        "capacity": {
            "segments_by_split": dict(sorted(segment_counts.items())),
            "core_targets_by_split": dict(sorted(core_counts.items())),
            "segment_length_counts": {str(k): length_counts[k] for k in sorted(length_counts)},
            "eligible_surface_count": len(eligible),
            "eligible_surfaces": eligible_records,
            "eligible_surfaces_sha256": eligible_records_sha,
            "movable_test_target_count": len(target_rows),
            "target_bearing_segment_count": len({row["segment_id"] for row in target_rows}),
            "test_page_count": len({row["page"] for row in target_rows}),
            "test_physical_folio_count": len(folio_counts),
            "used_null_cell_count": len(used_cells),
            "currier_counts": dict(sorted(currier_counts.items())),
            "section_counts": dict(sorted(section_counts.items())),
            "hand_counts": dict(sorted(Counter(row["hand"] for row in target_rows).items())),
            "length_counts": dict(sorted(Counter(row["segment_group_count"] for row in target_rows).items())),
            "position_counts": dict(sorted(Counter(row["segment_group_index"] for row in target_rows).items())),
            "folio_counts": dict(sorted(folio_counts.items())),
            "largest_folio_fraction": largest_folio_fraction,
            "log2_whole_record_permutation_capacity": log2_permutation_capacity,
            "target_panel_sha256": target_panel_sha,
        },
        "isolation": {
            "predictor_fitted": False,
            "real_context_target_association_scored": False,
            "likelihood_gain_computed": False,
            "english_glosses_present": False,
            "ocr_or_automated_vision_used": False,
        },
        "gates": gates,
        "claim_ceiling": CLAIM_CEILING,
    }


def report(result: dict[str, object]) -> str:
    c = result["capacity"]
    assert isinstance(c, dict)
    gates = result["gates"]
    assert isinstance(gates, dict)
    lines = [
        "# LRS001 source-native masked-record capacity",
        "",
        f"Status: **{result['status']}**.",
        "",
        "The corrected 5--12-group prose universe contains "
        f"{sum(c['segments_by_split'].values()):,} records.  The frozen TRAIN-core "
        f"support rule retains {c['eligible_surface_count']} complete source-family "
        "surfaces.",
        "",
        f"The held movable panel has {c['movable_test_target_count']:,} CORE targets "
        f"in {c['target_bearing_segment_count']} segments, {c['test_page_count']} pages, "
        f"and {c['test_physical_folio_count']} physical folios.  Currier A/B counts are "
        f"{c['currier_counts'].get('A', 0)}/{c['currier_counts'].get('B', 0)}; "
        f"B/H/S section counts are {c['section_counts'].get('B', 0)}/"
        f"{c['section_counts'].get('H', 0)}/{c['section_counts'].get('S', 0)}.  "
        f"The largest folio contributes {100*c['largest_folio_fraction']:.2f}% and "
        f"the exact whole-record null has {c['log2_whole_record_permutation_capacity']:.2f} bits of capacity.",
        "",
        (
            f"All {len(gates)} capacity gates pass.  This authorizes only a separately "
            "frozen target-blind synthetic calibration; no manuscript association was scored."
            if all(gates.values())
            else f"Only {sum(bool(value) for value in gates.values())}/{len(gates)} capacity "
            "gates pass.  The route stops unscored."
        ),
        "",
        f"Claim ceiling: {result['claim_ceiling']}",
    ]
    return "\n".join(lines) + "\n"


def main() -> None:
    if OUT_JSON.exists() or OUT_REPORT.exists():
        raise SystemExit("refusing to overwrite existing LRS001 capacity artifact")
    result = build()
    OUT_JSON.write_bytes(canonical_bytes(result))
    OUT_REPORT.write_text(report(result))
    print(json.dumps({"status": result["status"], "json": str(OUT_JSON), "report": str(OUT_REPORT)}, sort_keys=True))


if __name__ == "__main__":
    main()
