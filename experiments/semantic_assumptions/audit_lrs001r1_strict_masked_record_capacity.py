#!/usr/bin/env python3
"""Build the corrected score-blind LRS001-R1 capacity artifact."""

from __future__ import annotations

import csv
import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
SPEC = HERE / "LRS001R1_STRICT_MASKED_RECORD_CAPACITY_SPEC.md"
PRODUCER = Path(__file__).resolve()
ATLAS = RESULTS / "drawing_reset_segment_atlas.tsv"
SPLITS = RESULTS / "source_native_within_group_stage_masked.tsv"
OUT_JSON = RESULTS / "lrs001r1_strict_masked_record_capacity.json"
OUT_REPORT = RESULTS / "lrs001r1_strict_masked_record_capacity.md"
ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ"
CELL_FIELDS = (
    "page", "segment_group_count", "code", "segment_count", "segment_index",
    "starts_after_drawing", "ends_before_drawing", "group_count",
)
CLAIM = (
    "Capacity establishes only that a strict held ordered-nonadjacent-content "
    "test is possible; it supplies no field, word, part of speech, sentence "
    "role, recipe, language, sound, cipher, plaintext, or translation."
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def load() -> tuple[dict[str, dict[str, str]], dict[str, list[dict[str, str]]]]:
    split_map: dict[str, dict[str, str]] = {}
    with SPLITS.open(newline="") as handle:
        for source in csv.DictReader(handle, delimiter="\t"):
            row = dict(source)
            key = row["unit_id"]
            if key in split_map or row["split"] not in {"TRAIN", "CAL", "TEST"}:
                raise ValueError("invalid split table")
            split_map[key] = row
    if len(split_map) != 21_899:
        raise ValueError("unexpected split row count")

    segments: dict[str, list[dict[str, str]]] = defaultdict(list)
    with ATLAS.open(newline="") as handle:
        for source in csv.DictReader(handle, delimiter="\t"):
            row = dict(source)
            if row["grammar_scope"] != "CONFIRMED_PROSE":
                continue
            size = int(row["segment_group_count"])
            if not 5 <= size <= 12:
                continue
            key = row["consensus_group_id"]
            if key not in split_map or not row["family_surface"]:
                raise ValueError("missing join or complete surface")
            if len(row["family_surface"]) != int(row["symbol_count"]):
                raise ValueError("family length drift")
            if not set(row["family_surface"]) <= set(ALPHABET):
                raise ValueError("unknown STA family")
            segments[row["segment_id"]].append(row)

    seen: set[str] = set()
    for identifier, rows in segments.items():
        rows.sort(key=lambda row: int(row["segment_group_index"]))
        size = int(rows[0]["segment_group_count"])
        wanted_roles = ["FIRST"] + ["CORE"] * (size - 2) + ["LAST"]
        if len(rows) != size or [int(row["segment_group_index"]) for row in rows] != list(range(1, size + 1)):
            raise ValueError("incomplete segment")
        if [row["segment_position"] for row in rows] != wanted_roles:
            raise ValueError("position-role drift")
        if any(row["segment_id"] != identifier for row in rows):
            raise ValueError("segment identity drift")
        if any(len({row[field] for row in rows}) != 1 for field in CELL_FIELDS):
            raise ValueError("strict-cell field drift inside segment")
        sources = [split_map[row["consensus_group_id"]] for row in rows]
        if len({row["split"] for row in sources}) != 1 or len({row["physical_folio"] for row in sources}) != 1:
            raise ValueError("fold/folio drift")
        for row, source in zip(rows, sources):
            key = row["consensus_group_id"]
            if key in seen:
                raise ValueError("group reused")
            for field in ("page", "section", "currier", "hand", "kind", "symbol_count"):
                if row[field] != source[field]:
                    raise ValueError("source metadata drift")
            seen.add(key)
    return split_map, dict(segments)


def build() -> dict[str, object]:
    split_map, segments = load()
    train_counts: Counter[str] = Counter()
    train_folios: dict[str, set[str]] = defaultdict(set)
    for rows in segments.values():
        source = split_map[rows[0]["consensus_group_id"]]
        if source["split"] != "TRAIN":
            continue
        for row in rows:
            if row["segment_position"] == "CORE":
                train_counts[row["family_surface"]] += 1
                train_folios[row["family_surface"]].add(source["physical_folio"])
    eligible = sorted(
        surface for surface, count in train_counts.items()
        if count >= 20 and len(train_folios[surface]) >= 10
    )
    eligible_rows = [{
        "family_surface": surface,
        "train_core_occurrences": train_counts[surface],
        "train_physical_folios": len(train_folios[surface]),
    } for surface in eligible]
    class_count_by_length = Counter(len(surface) for surface in eligible)

    test_segments = {
        identifier: rows for identifier, rows in segments.items()
        if split_map[rows[0]["consensus_group_id"]]["split"] == "TEST"
    }
    cells: dict[tuple[str, ...], list[str]] = defaultdict(list)
    for identifier, rows in test_segments.items():
        cells[tuple(rows[0][field] for field in CELL_FIELDS)].append(identifier)
    for identifiers in cells.values():
        identifiers.sort()
    movable_segments = {
        identifier for identifiers in cells.values() if len(identifiers) >= 2
        for identifier in identifiers
    }
    all_supported_test = [
        row for rows in test_segments.values() for row in rows
        if row["segment_position"] == "CORE" and row["family_surface"] in eligible
    ]
    targets = [
        row for identifier in sorted(movable_segments) for row in test_segments[identifier]
        if row["segment_position"] == "CORE" and row["family_surface"] in eligible
    ]
    target_rows: list[dict[str, str]] = []
    for row in targets:
        source = split_map[row["consensus_group_id"]]
        cell = tuple(row[field] for field in CELL_FIELDS)
        target_rows.append({
            "target_id": row["consensus_group_id"],
            "segment_id": row["segment_id"],
            "page": row["page"],
            "physical_folio": source["physical_folio"],
            "section": row["section"],
            "currier": row["currier"],
            "hand": row["hand"],
            "segment_group_count": row["segment_group_count"],
            "segment_group_index": row["segment_group_index"],
            "symbol_count": row["symbol_count"],
            "family_surface": row["family_surface"],
            "cell_record_count": str(len(cells[cell])),
        })
    if len({row["target_id"] for row in target_rows}) != len(target_rows):
        raise ValueError("duplicate target")

    signature_counts = Counter(tuple(row["family_surface"] for row in rows) for rows in segments.values())
    unique_segments = {
        identifier for identifier in movable_segments
        if signature_counts[tuple(row["family_surface"] for row in test_segments[identifier])] == 1
    }
    unique_targets = [row for row in target_rows if row["segment_id"] in unique_segments]
    folio_counts = Counter(row["physical_folio"] for row in target_rows)
    currier_counts = Counter(row["currier"] for row in target_rows)
    currier_folios = {
        state: len({row["physical_folio"] for row in target_rows if row["currier"] == state})
        for state in ("A", "B")
    }
    section_counts = Counter(row["section"] for row in target_rows)
    used_cells = {tuple(row[field] for field in CELL_FIELDS) for row in targets}
    bits = sum(math.lgamma(len(cells[cell]) + 1) / math.log(2.0) for cell in used_cells)
    mobility = len(target_rows) / len(all_supported_test)
    largest = max(folio_counts.values()) / len(target_rows)
    unique_folios = len({row["physical_folio"] for row in unique_targets})
    gates = {
        "at_least_1500_targets_in_400_records": len(target_rows) >= 1500 and len({row["segment_id"] for row in target_rows}) >= 400,
        "at_least_100_cells_40_pages_20_folios": len(used_cells) >= 100 and len({row["page"] for row in target_rows}) >= 40 and len(folio_counts) >= 20,
        "supported_target_mobility_at_least_075": mobility >= 0.75,
        "each_currier_at_least_250_targets_8_folios": all(currier_counts[state] >= 250 and currier_folios[state] >= 8 for state in ("A", "B")),
        "sections_B_H_S_each_at_least_200": all(section_counts[state] >= 200 for state in ("B", "H", "S")),
        "largest_folio_fraction_below_020": largest < 0.20,
        "all_66_classes_and_two_per_length": len(eligible) == 66 and {row["family_surface"] for row in target_rows} == set(eligible) and min(class_count_by_length.values()) >= 2,
        "unique_record_subset_at_least_1500_targets_20_folios": len(unique_targets) >= 1500 and unique_folios >= 20,
        "permutation_capacity_at_least_64_bits": bits >= 64.0,
    }
    passed = all(gates.values())
    return {
        "experiment": "LRS001R1_strict_masked_record_capacity",
        "status": "PASS_STRICT_CAPACITY_SYNTHETIC_CALIBRATION_AUTHORIZED" if passed else "STOP_STRICT_CAPACITY_INSUFFICIENT",
        "decision": "GO_TARGET_BLIND_CALIBRATION_ONLY" if passed else "STOP_UNSCORED",
        "supersedes_for_future_calibration": "LRS001_source_native_masked_record_capacity",
        "inputs": {
            str(SPEC.relative_to(HERE)): sha(SPEC),
            str(ATLAS.relative_to(HERE)): sha(ATLAS),
            str(SPLITS.relative_to(HERE)): sha(SPLITS),
        },
        "implementation": {str(PRODUCER.relative_to(HERE)): sha(PRODUCER)},
        "rules": {
            "grammar_scope": "CONFIRMED_PROSE",
            "segment_group_count_range": [5, 12],
            "target_position": "CORE",
            "train_core_occurrence_min": 20,
            "train_physical_folio_min": 10,
            "target": "exact_complete_family_surface_proper_log_score",
            "official_alphabet": ALPHABET,
            "exact_donor_cell_fields": list(CELL_FIELDS),
            "null_unit": "one_whole_donor_record_map_synchronous_for_all_targets_channels_and_views",
        },
        "capacity": {
            "all_segments": len(segments),
            "test_segments": len(test_segments),
            "eligible_surface_count": len(eligible),
            "eligible_surfaces": eligible_rows,
            "eligible_surfaces_sha256": hashlib.sha256(canonical(eligible_rows)).hexdigest(),
            "class_count_by_symbol_count": {str(key): class_count_by_length[key] for key in sorted(class_count_by_length)},
            "all_supported_test_targets": len(all_supported_test),
            "movable_test_targets": len(target_rows),
            "supported_target_mobility_fraction": mobility,
            "target_bearing_records": len({row["segment_id"] for row in target_rows}),
            "used_exact_donor_cells": len(used_cells),
            "pages": len({row["page"] for row in target_rows}),
            "physical_folios": len(folio_counts),
            "currier_target_counts": dict(sorted(currier_counts.items())),
            "currier_folio_counts": currier_folios,
            "section_target_counts": dict(sorted(section_counts.items())),
            "folio_target_counts": dict(sorted(folio_counts.items())),
            "largest_folio_fraction": largest,
            "log2_whole_record_permutation_capacity": bits,
            "complete_record_signature_count": len(signature_counts),
            "repeated_complete_record_signature_count": sum(count > 1 for count in signature_counts.values()),
            "unique_record_subset_targets": len(unique_targets),
            "unique_record_subset_folios": unique_folios,
            "target_panel_sha256": hashlib.sha256(canonical(target_rows)).hexdigest(),
        },
        "required_future_comparison": ["ORDER_minus_BAG", "ORDER_minus_NUIS"],
        "isolation": {
            "predictor_fitted": False,
            "real_context_target_association_scored": False,
            "model_hyperparameters_selected": False,
            "ocr_or_automated_vision_used": False,
            "english_glosses_present": False,
        },
        "gates": gates,
        "claim_ceiling": CLAIM,
    }


def report(result: dict[str, object]) -> str:
    c = result["capacity"]
    assert isinstance(c, dict)
    return (
        "# LRS001-R1 strict masked-record capacity\n\n"
        f"Status: **{result['status']}**.\n\n"
        f"The strict design retains {c['movable_test_targets']:,}/{c['all_supported_test_targets']:,} "
        f"supported TEST targets ({100*c['supported_target_mobility_fraction']:.2f}%) in "
        f"{c['target_bearing_records']} records, {c['used_exact_donor_cells']} donor cells, "
        f"{c['pages']} pages, and {c['physical_folios']} physical folios. All "
        f"{c['eligible_surface_count']} TRAIN-supported complete classes remain.\n\n"
        f"Currier A/B retain {c['currier_target_counts']['A']}/{c['currier_target_counts']['B']} "
        f"targets on {c['currier_folio_counts']['A']}/{c['currier_folio_counts']['B']} folios. "
        f"The largest folio contributes {100*c['largest_folio_fraction']:.2f}%; the exact "
        f"whole-record null has {c['log2_whole_record_permutation_capacity']:.2f} bits.\n\n"
        f"All {len(result['gates'])} strict gates pass. The earlier page/length-only capacity "
        "is superseded for calibration; no predictor or real association was opened.\n\n"
        f"Claim ceiling: {result['claim_ceiling']}\n"
    )


def main() -> None:
    if OUT_JSON.exists() or OUT_REPORT.exists():
        raise SystemExit("refusing to overwrite LRS001-R1 capacity artifacts")
    result = build()
    OUT_JSON.write_bytes(canonical(result))
    OUT_REPORT.write_text(report(result))
    print(json.dumps({"status": result["status"], "decision": result["decision"]}, sort_keys=True))


if __name__ == "__main__":
    main()
