#!/usr/bin/env python3
"""Nonimporting validator for the corrected LRS001-R1 capacity freeze."""

from __future__ import annotations

import copy
import csv
import hashlib
import io
import json
import math
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
R = HERE / "results"
SPEC = HERE / "LRS001R1_STRICT_MASKED_RECORD_CAPACITY_SPEC.md"
PRODUCER = HERE / "audit_lrs001r1_strict_masked_record_capacity.py"
ATLAS = R / "drawing_reset_segment_atlas.tsv"
SPLITS = R / "source_native_within_group_stage_masked.tsv"
RESULT = R / "lrs001r1_strict_masked_record_capacity.json"
REPORT = R / "lrs001r1_strict_masked_record_capacity.md"
OUT = R / "lrs001r1_strict_masked_record_capacity_validation.json"
OUT_REPORT = R / "lrs001r1_strict_masked_record_capacity_validation.md"
EXPECTED = {
    SPEC: "f3640b40340c683e5117c20a0ad5ec254a650ae9cb7537147bcd2f32d76e8d83",
    PRODUCER: "eba671536f6ed902ec0e2a8fe1e97ef49e9ef7959ca58ad40de089bc76283162",
    ATLAS: "e303f9298e5d76473e7ddd311370e3486cb9997dfb58c05df40c3fb3b4de2486",
    SPLITS: "16d7395ae0410c8fc72b5e5462d6d425cd3a2685e7ea70eee0677bd936106ae5",
    RESULT: "490a74f06760621d9abb55d8718848c4dd04fb56254755569bc96aeb68081c3b",
    REPORT: "ec7183f75387cbcbc7d674e77f720bc676879fb5d9887cb0d52dc79ff590ce5e",
}
ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ"
CELL = (
    "page", "segment_group_count", "code", "segment_count", "segment_index",
    "starts_after_drawing", "ends_before_drawing", "group_count",
)
CLAIM = (
    "Capacity establishes only that a strict held ordered-nonadjacent-content "
    "test is possible; it supplies no field, word, part of speech, sentence "
    "role, recipe, language, sound, cipher, plaintext, or translation."
)


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canon(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def rows(path: Path) -> list[dict[str, str]]:
    return [dict(row) for row in csv.DictReader(io.StringIO(path.read_text()), delimiter="\t")]


def rejects(function) -> bool:
    try:
        function()
    except (KeyError, TypeError, ValueError):
        return True
    return False


def reconstruct(
    atlas_rows: list[dict[str, str]], split_rows: list[dict[str, str]]
) -> dict[str, object]:
    split: dict[str, dict[str, str]] = {}
    for row in split_rows:
        key = row["unit_id"]
        if key in split or row["split"] not in {"TRAIN", "CAL", "TEST"}:
            raise ValueError("split table")
        split[key] = row
    if len(split) != 21_899:
        raise ValueError("split count")

    segments: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in atlas_rows:
        if row["grammar_scope"] != "CONFIRMED_PROSE":
            continue
        size = int(row["segment_group_count"])
        if not 5 <= size <= 12:
            continue
        key = row["consensus_group_id"]
        if key not in split or not row["family_surface"]:
            raise ValueError("join/surface")
        if len(row["family_surface"]) != int(row["symbol_count"]):
            raise ValueError("family length")
        if not set(row["family_surface"]) <= set(ALPHABET):
            raise ValueError("alphabet")
        segments[row["segment_id"]].append(row)
    seen: set[str] = set()
    for identifier, group in segments.items():
        group.sort(key=lambda row: int(row["segment_group_index"]))
        size = int(group[0]["segment_group_count"])
        if len(group) != size or [int(row["segment_group_index"]) for row in group] != list(range(1, size + 1)):
            raise ValueError("complete/order")
        if [row["segment_position"] for row in group] != ["FIRST"] + ["CORE"] * (size - 2) + ["LAST"]:
            raise ValueError("roles")
        if any(row["segment_id"] != identifier for row in group):
            raise ValueError("segment id")
        if any(len({row[field] for row in group}) != 1 for field in CELL):
            raise ValueError("cell drift")
        source_rows = [split[row["consensus_group_id"]] for row in group]
        if len({row["split"] for row in source_rows}) != 1 or len({row["physical_folio"] for row in source_rows}) != 1:
            raise ValueError("fold drift")
        for row, source in zip(group, source_rows):
            key = row["consensus_group_id"]
            if key in seen:
                raise ValueError("group reuse")
            for field in ("page", "section", "currier", "hand", "kind", "symbol_count"):
                if row[field] != source[field]:
                    raise ValueError("metadata drift")
            seen.add(key)

    train_counts: Counter[str] = Counter()
    train_folios: dict[str, set[str]] = defaultdict(set)
    for group in segments.values():
        source = split[group[0]["consensus_group_id"]]
        if source["split"] == "TRAIN":
            for row in group:
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
    by_length = Counter(len(surface) for surface in eligible)
    test = {
        identifier: group for identifier, group in segments.items()
        if split[group[0]["consensus_group_id"]]["split"] == "TEST"
    }
    cells: dict[tuple[str, ...], list[str]] = defaultdict(list)
    for identifier, group in test.items():
        cells[tuple(group[0][field] for field in CELL)].append(identifier)
    for members in cells.values():
        members.sort()
    mobile = {identifier for members in cells.values() if len(members) >= 2 for identifier in members}
    all_supported = [
        row for group in test.values() for row in group
        if row["segment_position"] == "CORE" and row["family_surface"] in eligible
    ]
    target_sources = [
        row for identifier in sorted(mobile) for row in test[identifier]
        if row["segment_position"] == "CORE" and row["family_surface"] in eligible
    ]
    targets: list[dict[str, str]] = []
    for row in target_sources:
        source = split[row["consensus_group_id"]]
        cell = tuple(row[field] for field in CELL)
        targets.append({
            "target_id": row["consensus_group_id"], "segment_id": row["segment_id"],
            "page": row["page"], "physical_folio": source["physical_folio"],
            "section": row["section"], "currier": row["currier"], "hand": row["hand"],
            "segment_group_count": row["segment_group_count"],
            "segment_group_index": row["segment_group_index"],
            "symbol_count": row["symbol_count"], "family_surface": row["family_surface"],
            "cell_record_count": str(len(cells[cell])),
        })
    if len({row["target_id"] for row in targets}) != len(targets):
        raise ValueError("target duplicate")
    signatures = Counter(tuple(row["family_surface"] for row in group) for group in segments.values())
    unique_segments = {
        identifier for identifier in mobile
        if signatures[tuple(row["family_surface"] for row in test[identifier])] == 1
    }
    unique_targets = [row for row in targets if row["segment_id"] in unique_segments]
    folios = Counter(row["physical_folio"] for row in targets)
    currier = Counter(row["currier"] for row in targets)
    currier_folios = {state: len({row["physical_folio"] for row in targets if row["currier"] == state}) for state in ("A", "B")}
    sections = Counter(row["section"] for row in targets)
    used_cells = {tuple(row[field] for field in CELL) for row in target_sources}
    bits = sum(math.lgamma(len(cells[cell]) + 1) / math.log(2.0) for cell in used_cells)
    mobility = len(targets) / len(all_supported)
    largest = max(folios.values()) / len(targets)
    unique_folios = len({row["physical_folio"] for row in unique_targets})
    gates = {
        "at_least_1500_targets_in_400_records": len(targets) >= 1500 and len({row["segment_id"] for row in targets}) >= 400,
        "at_least_100_cells_40_pages_20_folios": len(used_cells) >= 100 and len({row["page"] for row in targets}) >= 40 and len(folios) >= 20,
        "supported_target_mobility_at_least_075": mobility >= 0.75,
        "each_currier_at_least_250_targets_8_folios": all(currier[state] >= 250 and currier_folios[state] >= 8 for state in ("A", "B")),
        "sections_B_H_S_each_at_least_200": all(sections[state] >= 200 for state in ("B", "H", "S")),
        "largest_folio_fraction_below_020": largest < 0.20,
        "all_66_classes_and_two_per_length": len(eligible) == 66 and {row["family_surface"] for row in targets} == set(eligible) and min(by_length.values()) >= 2,
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
            str(SPEC.relative_to(HERE)): EXPECTED[SPEC], str(ATLAS.relative_to(HERE)): EXPECTED[ATLAS],
            str(SPLITS.relative_to(HERE)): EXPECTED[SPLITS],
        },
        "implementation": {str(PRODUCER.relative_to(HERE)): EXPECTED[PRODUCER]},
        "rules": {
            "grammar_scope": "CONFIRMED_PROSE", "segment_group_count_range": [5, 12],
            "target_position": "CORE", "train_core_occurrence_min": 20,
            "train_physical_folio_min": 10, "target": "exact_complete_family_surface_proper_log_score",
            "official_alphabet": ALPHABET, "exact_donor_cell_fields": list(CELL),
            "null_unit": "one_whole_donor_record_map_synchronous_for_all_targets_channels_and_views",
        },
        "capacity": {
            "all_segments": len(segments), "test_segments": len(test),
            "eligible_surface_count": len(eligible), "eligible_surfaces": eligible_rows,
            "eligible_surfaces_sha256": sha_bytes(canon(eligible_rows)),
            "class_count_by_symbol_count": {str(k): by_length[k] for k in sorted(by_length)},
            "all_supported_test_targets": len(all_supported), "movable_test_targets": len(targets),
            "supported_target_mobility_fraction": mobility,
            "target_bearing_records": len({row["segment_id"] for row in targets}),
            "used_exact_donor_cells": len(used_cells), "pages": len({row["page"] for row in targets}),
            "physical_folios": len(folios), "currier_target_counts": dict(sorted(currier.items())),
            "currier_folio_counts": currier_folios, "section_target_counts": dict(sorted(sections.items())),
            "folio_target_counts": dict(sorted(folios.items())), "largest_folio_fraction": largest,
            "log2_whole_record_permutation_capacity": bits,
            "complete_record_signature_count": len(signatures),
            "repeated_complete_record_signature_count": sum(value > 1 for value in signatures.values()),
            "unique_record_subset_targets": len(unique_targets), "unique_record_subset_folios": unique_folios,
            "target_panel_sha256": sha_bytes(canon(targets)),
        },
        "required_future_comparison": ["ORDER_minus_BAG", "ORDER_minus_NUIS"],
        "isolation": {"predictor_fitted": False, "real_context_target_association_scored": False,
                      "model_hyperparameters_selected": False, "ocr_or_automated_vision_used": False,
                      "english_glosses_present": False},
        "gates": gates, "claim_ceiling": CLAIM,
    }


def report(result: dict[str, object]) -> str:
    c = result["capacity"]
    assert isinstance(c, dict)
    return (
        "# LRS001-R1 strict masked-record capacity\n\n"
        f"Status: **{result['status']}**.\n\n"
        f"The strict design retains {c['movable_test_targets']:,}/{c['all_supported_test_targets']:,} supported TEST targets ({100*c['supported_target_mobility_fraction']:.2f}%) in {c['target_bearing_records']} records, {c['used_exact_donor_cells']} donor cells, {c['pages']} pages, and {c['physical_folios']} physical folios. All {c['eligible_surface_count']} TRAIN-supported complete classes remain.\n\n"
        f"Currier A/B retain {c['currier_target_counts']['A']}/{c['currier_target_counts']['B']} targets on {c['currier_folio_counts']['A']}/{c['currier_folio_counts']['B']} folios. The largest folio contributes {100*c['largest_folio_fraction']:.2f}%; the exact whole-record null has {c['log2_whole_record_permutation_capacity']:.2f} bits.\n\n"
        f"All {len(result['gates'])} strict gates pass. The earlier page/length-only capacity is superseded for calibration; no predictor or real association was opened.\n\n"
        f"Claim ceiling: {result['claim_ceiling']}\n"
    )


def main() -> None:
    if OUT.exists() or OUT_REPORT.exists():
        raise SystemExit("refusing to overwrite validation")
    checks: list[str] = []
    for path, expected in EXPECTED.items():
        if sha_bytes(path.read_bytes()) != expected:
            raise SystemExit(f"hash mismatch: {path}")
        checks.append("sha256:" + path.name)
    atlas_rows, split_rows = rows(ATLAS), rows(SPLITS)
    rebuilt = reconstruct(atlas_rows, split_rows)
    if canon(rebuilt) != RESULT.read_bytes():
        raise SystemExit("JSON reconstruction mismatch")
    checks.append("exact_json_reconstruction")
    if report(rebuilt) != REPORT.read_text():
        raise SystemExit("report reconstruction mismatch")
    checks.append("exact_report_reconstruction")

    mutations: dict[str, bool] = {}
    changed = copy.deepcopy(split_rows); changed.append(dict(changed[0]))
    mutations["duplicate_split_rejected"] = rejects(lambda: reconstruct(atlas_rows, changed))
    admitted = next(row["consensus_group_id"] for row in atlas_rows if row["grammar_scope"] == "CONFIRMED_PROSE" and 5 <= int(row["segment_group_count"]) <= 12)
    changed = [row for row in split_rows if row["unit_id"] != admitted]
    mutations["missing_join_rejected"] = rejects(lambda: reconstruct(atlas_rows, changed))
    changed_atlas = copy.deepcopy(atlas_rows)
    row = next(row for row in changed_atlas if row["consensus_group_id"] == admitted)
    row["segment_group_index"] = "99"
    mutations["position_mutation_rejected"] = rejects(lambda: reconstruct(changed_atlas, split_rows))
    changed_atlas = copy.deepcopy(atlas_rows)
    row = next(row for row in changed_atlas if row["consensus_group_id"] == admitted)
    row["code"] = "MUTATED"
    mutations["within_record_cell_drift_rejected"] = rejects(lambda: reconstruct(changed_atlas, split_rows))
    changed_atlas = copy.deepcopy(atlas_rows)
    row = next(row for row in changed_atlas if row["consensus_group_id"] == admitted)
    row["page"] = "f999x"
    mutations["source_metadata_drift_rejected"] = rejects(lambda: reconstruct(changed_atlas, split_rows))
    changed_atlas = copy.deepcopy(atlas_rows)
    row = next(row for row in changed_atlas if row["consensus_group_id"] == admitted)
    row["family_surface"] += "I"
    mutations["invalid_family_rejected"] = rejects(lambda: reconstruct(changed_atlas, split_rows))
    if not all(mutations.values()):
        raise SystemExit(f"mutation failure: {mutations}")
    checks.extend(sorted(mutations))
    output = {
        "experiment": "LRS001R1_strict_masked_record_capacity_validation",
        "status": "PASS", "decision": rebuilt["decision"], "check_count": len(checks),
        "checks": checks, "mutations": mutations,
        "reconstructed": {
            "eligible_surfaces": rebuilt["capacity"]["eligible_surface_count"],
            "movable_test_targets": rebuilt["capacity"]["movable_test_targets"],
            "target_bearing_records": rebuilt["capacity"]["target_bearing_records"],
            "exact_cells": rebuilt["capacity"]["used_exact_donor_cells"],
            "physical_folios": rebuilt["capacity"]["physical_folios"],
            "target_panel_sha256": rebuilt["capacity"]["target_panel_sha256"],
        },
        "bound_hashes": {str(path.relative_to(HERE)): value for path, value in EXPECTED.items()},
        "claim_ceiling": CLAIM,
    }
    OUT.write_bytes(canon(output))
    OUT_REPORT.write_text(
        "# LRS001-R1 strict capacity validation\n\nStatus: **PASS**.\n\n"
        f"A nonimporting reconstruction passed {len(checks)} binding, content, report, and mutation checks. "
        f"It recovered {output['reconstructed']['movable_test_targets']:,} targets in "
        f"{output['reconstructed']['target_bearing_records']} records and {output['reconstructed']['exact_cells']} strict donor cells.\n\n"
        f"Decision retained: **{output['decision']}**. No predictor or real association was opened.\n\n"
        f"Claim ceiling: {CLAIM}\n"
    )
    print(json.dumps({"status": "PASS", "checks": len(checks)}, sort_keys=True))


if __name__ == "__main__":
    main()
