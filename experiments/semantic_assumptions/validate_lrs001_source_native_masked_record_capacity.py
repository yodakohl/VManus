#!/usr/bin/env python3
"""Clean-room validator for the LRS001 score-blind capacity freeze.

This module does not import the producer.  It independently reparses both
frozen tables, reconstructs the complete production JSON/report, and exercises
fail-closed input mutations before emitting compact validation artifacts.
"""

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
RESULTS = HERE / "results"
SPEC = HERE / "LRS001_SOURCE_NATIVE_MASKED_RECORD_CAPACITY_SPEC.md"
PRODUCER = HERE / "audit_lrs001_source_native_masked_record_capacity.py"
SEGMENTS = RESULTS / "drawing_reset_segment_atlas.tsv"
SPLITS = RESULTS / "source_native_within_group_stage_masked.tsv"
PRODUCTION_JSON = RESULTS / "lrs001_source_native_masked_record_capacity.json"
PRODUCTION_REPORT = RESULTS / "lrs001_source_native_masked_record_capacity.md"
OUT_JSON = RESULTS / "lrs001_source_native_masked_record_capacity_validation.json"
OUT_REPORT = RESULTS / "lrs001_source_native_masked_record_capacity_validation.md"

EXPECTED_HASHES = {
    SPEC: "d58cfae130a0422a13d6d2c3c9b6fb20b113eb6b5ee992453bcd8b77897aecdf",
    PRODUCER: "e69520f3c74f5aaf5f0f75a121024c77310fb16316fb0914bfa37d4f6266261c",
    SEGMENTS: "e303f9298e5d76473e7ddd311370e3486cb9997dfb58c05df40c3fb3b4de2486",
    SPLITS: "16d7395ae0410c8fc72b5e5462d6d425cd3a2685e7ea70eee0677bd936106ae5",
    PRODUCTION_JSON: "ef3c4413321e622b0d321fd902534412265bd69c6b7bb2c90123ea1d0e89fb3a",
    PRODUCTION_REPORT: "bc052feed1b9388388a2a721f863f303f88145358bd5dbe829a140f211750c38",
}

CLAIM_CEILING = (
    "Capacity establishes only that a held source-native masked-record test is "
    "possible; it supplies no record schema, word, part of speech, recipe "
    "field, language, sound, cipher, plaintext, or translation."
)


def digest_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def digest_path(path: Path) -> str:
    return digest_bytes(path.read_bytes())


def canonical(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def read_tsv(path: Path) -> list[dict[str, str]]:
    return [dict(row) for row in csv.DictReader(io.StringIO(path.read_text()), delimiter="\t")]


def reject(callable_object) -> bool:
    try:
        callable_object()
    except (KeyError, TypeError, ValueError):
        return True
    return False


def reconstruct(
    atlas_rows: list[dict[str, str]], split_rows: list[dict[str, str]]
) -> dict[str, object]:
    split_map: dict[str, dict[str, str]] = {}
    for row in split_rows:
        key = row["unit_id"]
        if key in split_map:
            raise ValueError(f"duplicate split unit_id: {key}")
        if row["split"] not in {"TRAIN", "CAL", "TEST"}:
            raise ValueError("invalid split")
        split_map[key] = row
    if len(split_map) != 21_899:
        raise ValueError("wrong split row count")

    segments: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in atlas_rows:
        if row["grammar_scope"] != "CONFIRMED_PROSE":
            continue
        length = int(row["segment_group_count"])
        if not 5 <= length <= 12:
            continue
        key = row["consensus_group_id"]
        if key not in split_map:
            raise ValueError(f"missing split join: {key}")
        if not row["family_surface"] or int(row["symbol_count"]) <= 0:
            raise ValueError("invalid complete surface")
        segments[row["segment_id"]].append(row)

    seen: set[str] = set()
    for segment_id, rows in segments.items():
        rows.sort(key=lambda item: int(item["segment_group_index"]))
        size = int(rows[0]["segment_group_count"])
        if len(rows) != size:
            raise ValueError("incomplete segment")
        if [int(row["segment_group_index"]) for row in rows] != list(range(1, size + 1)):
            raise ValueError("bad segment ordering")
        wanted_roles = ["FIRST"] + ["CORE"] * (size - 2) + ["LAST"]
        if [row["segment_position"] for row in rows] != wanted_roles:
            raise ValueError("bad segment roles")
        if any(row["segment_id"] != segment_id for row in rows):
            raise ValueError("segment identity drift")
        splits = {split_map[row["consensus_group_id"]]["split"] for row in rows}
        folios = {split_map[row["consensus_group_id"]]["physical_folio"] for row in rows}
        if len(splits) != 1 or len(folios) != 1:
            raise ValueError("within-segment split/folio drift")
        for row in rows:
            key = row["consensus_group_id"]
            if key in seen:
                raise ValueError("group reused")
            source = split_map[key]
            for field in ("page", "section", "currier", "hand", "kind", "symbol_count"):
                if row[field] != source[field]:
                    raise ValueError(f"metadata drift: {field}")
            seen.add(key)

    segment_counts: Counter[str] = Counter()
    core_counts: Counter[str] = Counter()
    length_counts: Counter[int] = Counter()
    train_counts: Counter[str] = Counter()
    train_folios: dict[str, set[str]] = defaultdict(set)
    for rows in segments.values():
        source = split_map[rows[0]["consensus_group_id"]]
        split, folio = source["split"], source["physical_folio"]
        segment_counts[split] += 1
        length_counts[int(rows[0]["segment_group_count"])] += 1
        for row in rows:
            if row["segment_position"] != "CORE":
                continue
            core_counts[split] += 1
            if split == "TRAIN":
                train_counts[row["family_surface"]] += 1
                train_folios[row["family_surface"]].add(folio)

    eligible = sorted(
        surface for surface, count in train_counts.items()
        if count >= 20 and len(train_folios[surface]) >= 10
    )
    test_cells: dict[tuple[str, int], list[str]] = defaultdict(list)
    for segment_id, rows in segments.items():
        source = split_map[rows[0]["consensus_group_id"]]
        if source["split"] == "TEST":
            test_cells[(rows[0]["page"], int(rows[0]["segment_group_count"]))].append(segment_id)
    for members in test_cells.values():
        members.sort()

    targets: list[dict[str, str]] = []
    for segment_id, rows in sorted(segments.items()):
        source = split_map[rows[0]["consensus_group_id"]]
        if source["split"] != "TEST":
            continue
        cell = (rows[0]["page"], int(rows[0]["segment_group_count"]))
        if len(test_cells[cell]) < 2:
            continue
        for row in rows:
            if row["segment_position"] == "CORE" and row["family_surface"] in eligible:
                targets.append({
                    "target_id": row["consensus_group_id"],
                    "segment_id": segment_id,
                    "page": row["page"],
                    "physical_folio": source["physical_folio"],
                    "section": row["section"],
                    "currier": row["currier"],
                    "hand": row["hand"],
                    "segment_group_count": row["segment_group_count"],
                    "segment_group_index": row["segment_group_index"],
                    "symbol_count": row["symbol_count"],
                    "family_surface": row["family_surface"],
                    "cell_record_count": str(len(test_cells[cell])),
                })
    ids = [row["target_id"] for row in targets]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate target")

    section_counts = Counter(row["section"] for row in targets)
    currier_counts = Counter(row["currier"] for row in targets)
    folio_counts = Counter(row["physical_folio"] for row in targets)
    used_cells = {(row["page"], int(row["segment_group_count"])) for row in targets}
    log2_space = sum(
        math.lgamma(len(test_cells[cell]) + 1) / math.log(2.0) for cell in used_cells
    )
    largest = max(folio_counts.values()) / len(targets)
    gates = {
        "at_least_1500_movable_test_targets": len(targets) >= 1500,
        "at_least_400_target_bearing_segments": len({row["segment_id"] for row in targets}) >= 400,
        "at_least_40_test_pages": len({row["page"] for row in targets}) >= 40,
        "at_least_20_test_physical_folios": len(folio_counts) >= 20,
        "at_least_250_each_currier_A_B": all(currier_counts[x] >= 250 for x in ("A", "B")),
        "at_least_250_each_section_B_H_S": all(section_counts[x] >= 250 for x in ("B", "H", "S")),
        "largest_folio_fraction_below_020": largest < 0.20,
        "every_eligible_surface_in_movable_test": {row["family_surface"] for row in targets} == set(eligible),
        "permutation_capacity_at_least_64_bits": log2_space >= 64.0,
    }
    eligible_rows = [{
        "family_surface": surface,
        "train_core_occurrences": train_counts[surface],
        "train_physical_folios": len(train_folios[surface]),
    } for surface in eligible]
    passed = all(gates.values())
    return {
        "experiment": "LRS001_source_native_masked_record_capacity",
        "status": "PASS_CAPACITY_FREEZE_SYNTHETIC_CALIBRATION_AUTHORIZED" if passed else "STOP_CAPACITY_INSUFFICIENT",
        "decision": "GO_TARGET_BLIND_CALIBRATION_ONLY" if passed else "STOP_UNSCORED",
        "inputs": {
            str(SPEC.relative_to(HERE)): EXPECTED_HASHES[SPEC],
            str(SEGMENTS.relative_to(HERE)): EXPECTED_HASHES[SEGMENTS],
            str(SPLITS.relative_to(HERE)): EXPECTED_HASHES[SPLITS],
        },
        "implementation": {str(PRODUCER.relative_to(HERE)): EXPECTED_HASHES[PRODUCER]},
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
            "eligible_surfaces": eligible_rows,
            "eligible_surfaces_sha256": digest_bytes(canonical(eligible_rows)),
            "movable_test_target_count": len(targets),
            "target_bearing_segment_count": len({row["segment_id"] for row in targets}),
            "test_page_count": len({row["page"] for row in targets}),
            "test_physical_folio_count": len(folio_counts),
            "used_null_cell_count": len(used_cells),
            "currier_counts": dict(sorted(currier_counts.items())),
            "section_counts": dict(sorted(section_counts.items())),
            "hand_counts": dict(sorted(Counter(row["hand"] for row in targets).items())),
            "length_counts": dict(sorted(Counter(row["segment_group_count"] for row in targets).items())),
            "position_counts": dict(sorted(Counter(row["segment_group_index"] for row in targets).items())),
            "folio_counts": dict(sorted(folio_counts.items())),
            "largest_folio_fraction": largest,
            "log2_whole_record_permutation_capacity": log2_space,
            "target_panel_sha256": digest_bytes(canonical(targets)),
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


def expected_report(result: dict[str, object]) -> str:
    c = result["capacity"]
    gates = result["gates"]
    assert isinstance(c, dict) and isinstance(gates, dict)
    return "\n".join([
        "# LRS001 source-native masked-record capacity", "",
        f"Status: **{result['status']}**.", "",
        f"The corrected 5--12-group prose universe contains {sum(c['segments_by_split'].values()):,} records.  The frozen TRAIN-core support rule retains {c['eligible_surface_count']} complete source-family surfaces.", "",
        f"The held movable panel has {c['movable_test_target_count']:,} CORE targets in {c['target_bearing_segment_count']} segments, {c['test_page_count']} pages, and {c['test_physical_folio_count']} physical folios.  Currier A/B counts are {c['currier_counts'].get('A', 0)}/{c['currier_counts'].get('B', 0)}; B/H/S section counts are {c['section_counts'].get('B', 0)}/{c['section_counts'].get('H', 0)}/{c['section_counts'].get('S', 0)}.  The largest folio contributes {100*c['largest_folio_fraction']:.2f}% and the exact whole-record null has {c['log2_whole_record_permutation_capacity']:.2f} bits of capacity.", "",
        f"All {len(gates)} capacity gates pass.  This authorizes only a separately frozen target-blind synthetic calibration; no manuscript association was scored.", "",
        f"Claim ceiling: {result['claim_ceiling']}",
    ]) + "\n"


def main() -> None:
    if OUT_JSON.exists() or OUT_REPORT.exists():
        raise SystemExit("refusing to overwrite existing LRS001 validation artifacts")
    checks: list[str] = []
    for path, expected in EXPECTED_HASHES.items():
        if digest_path(path) != expected:
            raise SystemExit(f"frozen hash mismatch: {path}")
        checks.append(f"sha256:{path.name}")

    atlas_rows = read_tsv(SEGMENTS)
    split_rows = read_tsv(SPLITS)
    rebuilt = reconstruct(atlas_rows, split_rows)
    if canonical(rebuilt) != PRODUCTION_JSON.read_bytes():
        raise SystemExit("production JSON differs from clean-room reconstruction")
    checks.append("exact_production_json_reconstruction")
    if expected_report(rebuilt) != PRODUCTION_REPORT.read_text():
        raise SystemExit("production report differs from clean-room reconstruction")
    checks.append("exact_production_report_reconstruction")

    mutations: dict[str, bool] = {}
    altered = copy.deepcopy(split_rows)
    altered.append(dict(altered[0]))
    mutations["duplicate_split_unit_rejected"] = reject(lambda: reconstruct(atlas_rows, altered))
    altered = copy.deepcopy(split_rows)
    admitted = next(row["consensus_group_id"] for row in atlas_rows if row["grammar_scope"] == "CONFIRMED_PROSE" and 5 <= int(row["segment_group_count"]) <= 12)
    altered = [row for row in altered if row["unit_id"] != admitted]
    mutations["missing_split_join_rejected"] = reject(lambda: reconstruct(atlas_rows, altered))
    altered_atlas = copy.deepcopy(atlas_rows)
    row = next(row for row in altered_atlas if row["grammar_scope"] == "CONFIRMED_PROSE" and 5 <= int(row["segment_group_count"]) <= 12)
    row["segment_group_index"] = "99"
    mutations["bad_segment_position_rejected"] = reject(lambda: reconstruct(altered_atlas, split_rows))
    altered_atlas = copy.deepcopy(atlas_rows)
    row = next(row for row in altered_atlas if row["grammar_scope"] == "CONFIRMED_PROSE" and 5 <= int(row["segment_group_count"]) <= 12)
    row["page"] = "f999x"
    mutations["metadata_drift_rejected"] = reject(lambda: reconstruct(altered_atlas, split_rows))
    altered_atlas = copy.deepcopy(atlas_rows)
    row = next(row for row in altered_atlas if row["grammar_scope"] == "CONFIRMED_PROSE" and 5 <= int(row["segment_group_count"]) <= 12)
    row["grammar_scope"] = "DIAGNOSTIC_NONPROSE"
    mutations["incomplete_scope_mutation_rejected"] = reject(lambda: reconstruct(altered_atlas, split_rows))
    if not all(mutations.values()):
        raise SystemExit(f"mutation guard failed: {mutations}")
    checks.extend(sorted(mutations))

    artifact = {
        "experiment": "LRS001_source_native_masked_record_capacity_validation",
        "status": "PASS",
        "decision": rebuilt["decision"],
        "check_count": len(checks),
        "checks": checks,
        "mutations": mutations,
        "reconstructed": {
            "segments": sum(rebuilt["capacity"]["segments_by_split"].values()),
            "eligible_surfaces": rebuilt["capacity"]["eligible_surface_count"],
            "movable_test_targets": rebuilt["capacity"]["movable_test_target_count"],
            "target_bearing_segments": rebuilt["capacity"]["target_bearing_segment_count"],
            "pages": rebuilt["capacity"]["test_page_count"],
            "physical_folios": rebuilt["capacity"]["test_physical_folio_count"],
            "target_panel_sha256": rebuilt["capacity"]["target_panel_sha256"],
        },
        "bound_hashes": {str(path.relative_to(HERE)): value for path, value in EXPECTED_HASHES.items()},
        "claim_ceiling": CLAIM_CEILING,
    }
    OUT_JSON.write_bytes(canonical(artifact))
    OUT_REPORT.write_text(
        "# LRS001 capacity clean-room validation\n\n"
        "Status: **PASS**.\n\n"
        f"A nonimporting reconstruction passed {len(checks)} hash, content, report, and mutation checks. "
        f"It independently recovered {artifact['reconstructed']['movable_test_targets']:,} movable held targets in "
        f"{artifact['reconstructed']['target_bearing_segments']} records across {artifact['reconstructed']['physical_folios']} physical folios.\n\n"
        f"Decision retained: **{artifact['decision']}**. No predictor or real context/target association was opened.\n\n"
        f"Claim ceiling: {CLAIM_CEILING}\n"
    )
    print(json.dumps({"status": "PASS", "checks": len(checks)}, sort_keys=True))


if __name__ == "__main__":
    main()
