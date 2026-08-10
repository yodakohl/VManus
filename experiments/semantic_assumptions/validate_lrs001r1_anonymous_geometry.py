#!/usr/bin/env python3
"""Clean-room reconstruction of the LRS001-R1 anonymous geometry."""

from __future__ import annotations

import copy
import csv
import hashlib
import io
import json
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
R = HERE / "results"
SPEC = HERE / "LRS001R1_ANONYMOUS_GEOMETRY_SPEC.md"
PRODUCER = HERE / "build_lrs001r1_anonymous_geometry.py"
CAPACITY = R / "lrs001r1_strict_masked_record_capacity.json"
ATLAS = R / "drawing_reset_segment_atlas.tsv"
SPLITS = R / "source_native_within_group_stage_masked.tsv"
TSV = R / "lrs001r1_anonymous_geometry.tsv"
RESULT = R / "lrs001r1_anonymous_geometry.json"
REPORT = R / "lrs001r1_anonymous_geometry.md"
OUT = R / "lrs001r1_anonymous_geometry_validation.json"
OUT_REPORT = R / "lrs001r1_anonymous_geometry_validation.md"
EXPECTED = {
    SPEC: "cc8b4217321e6d5875f1d11a6c2d300f9b16011601603aab290c97285903fbd5",
    PRODUCER: "645af92e055aa1babb5a1cbf2e6a5b9dd340aeb993ee0a6945a7685e847e1756",
    CAPACITY: "490a74f06760621d9abb55d8718848c4dd04fb56254755569bc96aeb68081c3b",
    ATLAS: "e303f9298e5d76473e7ddd311370e3486cb9997dfb58c05df40c3fb3b4de2486",
    SPLITS: "16d7395ae0410c8fc72b5e5462d6d425cd3a2685e7ea70eee0677bd936106ae5",
    TSV: "37f06364effab97140d50fd64984ee561ed84f9087866314db7fec4f059647df",
    RESULT: "0c251db4526f54a1b3bec15528f32a95c782d3a7d8f134ab49b6afb872bd1542",
    REPORT: "74686fdbabe412bfcb4e40bf531dc98924d7047d71d51465b6abde16d5239e40",
}
CELL = (
    "page", "segment_group_count", "code", "segment_count", "segment_index",
    "starts_after_drawing", "ends_before_drawing", "group_count",
)
FIELDS = (
    "anonymous_group_id", "anonymous_record_id", "split", "page", "physical_folio",
    "section", "currier", "hand", "code", "kind", "segment_group_count",
    "segment_group_index", "segment_position", "segment_count", "segment_index",
    "starts_after_drawing", "ends_before_drawing", "original_group_count",
    "symbol_count", "supported_class_target", "strict_test_movable",
    "strict_cell_id", "strict_cell_record_count",
)
FORBIDDEN = {
    "family_surface", "zl_sta_codes", "it_sta_codes", "rf_sta_codes",
    "zl_basic_eva_lossy", "it_basic_eva_lossy", "rf_basic_eva_lossy",
    "transcription", "token", "root", "role", "english_gloss", "image", "ocr",
    "automated_vision",
}
CLASS_LAYOUT = {"1": 3, "2": 8, "3": 23, "4": 19, "5": 10, "6": 3}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def table(path: Path) -> list[dict[str, str]]:
    return [dict(row) for row in csv.DictReader(io.StringIO(path.read_text()), delimiter="\t")]


def anonymous(domain: str, value: str) -> str:
    return domain + hashlib.sha256(("LRS001R1|" + domain + "|" + value).encode()).hexdigest()[:20]


def tsv_bytes(output: list[dict[str, str]]) -> bytes:
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=FIELDS, delimiter="\t", lineterminator="\n")
    writer.writeheader(); writer.writerows(output)
    return buffer.getvalue().encode()


def reject(function) -> bool:
    try:
        function()
    except (KeyError, TypeError, ValueError):
        return True
    return False


def rebuild(atlas_rows: list[dict[str, str]], split_rows: list[dict[str, str]]) -> tuple[list[dict[str, str]], dict[str, object]]:
    capacity = json.loads(CAPACITY.read_text())
    if capacity["decision"] != "GO_TARGET_BLIND_CALIBRATION_ONLY":
        raise ValueError("capacity")
    eligible = {row["family_surface"] for row in capacity["capacity"]["eligible_surfaces"]}
    if len(eligible) != 66:
        raise ValueError("classes")
    split: dict[str, dict[str, str]] = {}
    for row in split_rows:
        if row["unit_id"] in split:
            raise ValueError("duplicate split")
        split[row["unit_id"]] = row
    if len(split) != 21_899:
        raise ValueError("split count")
    segments: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in atlas_rows:
        if row["grammar_scope"] == "CONFIRMED_PROSE" and 5 <= int(row["segment_group_count"]) <= 12:
            if row["consensus_group_id"] not in split:
                raise ValueError("missing join")
            segments[row["segment_id"]].append(row)
    for identifier, group in segments.items():
        group.sort(key=lambda row: int(row["segment_group_index"]))
        size = int(group[0]["segment_group_count"])
        if len(group) != size or [int(row["segment_group_index"]) for row in group] != list(range(1, size + 1)):
            raise ValueError("incomplete")
        if any(len({row[field] for row in group}) != 1 for field in CELL):
            raise ValueError("cell drift")
        sources = [split[row["consensus_group_id"]] for row in group]
        if len({row["split"] for row in sources}) != 1 or len({row["physical_folio"] for row in sources}) != 1:
            raise ValueError("fold drift")
    cells: dict[tuple[str, ...], list[str]] = defaultdict(list)
    for identifier, group in segments.items():
        if split[group[0]["consensus_group_id"]]["split"] == "TEST":
            cells[tuple(group[0][field] for field in CELL)].append(identifier)
    for members in cells.values():
        members.sort()
    output: list[dict[str, str]] = []
    for identifier, group in sorted(segments.items()):
        source = split[group[0]["consensus_group_id"]]
        cell = tuple(group[0][field] for field in CELL)
        count = len(cells[cell]) if source["split"] == "TEST" else 0
        cell_id = anonymous("C", "\x1f".join(cell)) if source["split"] == "TEST" else ""
        for row in group:
            joined = split[row["consensus_group_id"]]
            for field in ("page", "section", "currier", "hand", "kind", "symbol_count"):
                if row[field] != joined[field]:
                    raise ValueError("metadata")
            output.append({
                "anonymous_group_id": anonymous("G", row["consensus_group_id"]),
                "anonymous_record_id": anonymous("R", identifier), "split": source["split"],
                "page": row["page"], "physical_folio": source["physical_folio"],
                "section": row["section"], "currier": row["currier"], "hand": row["hand"],
                "code": row["code"], "kind": row["kind"],
                "segment_group_count": row["segment_group_count"],
                "segment_group_index": row["segment_group_index"],
                "segment_position": row["segment_position"], "segment_count": row["segment_count"],
                "segment_index": row["segment_index"], "starts_after_drawing": row["starts_after_drawing"],
                "ends_before_drawing": row["ends_before_drawing"],
                "original_group_count": row["group_count"], "symbol_count": row["symbol_count"],
                "supported_class_target": str(int(row["segment_position"] == "CORE" and row["family_surface"] in eligible)),
                "strict_test_movable": str(int(source["split"] == "TEST" and count >= 2)),
                "strict_cell_id": cell_id, "strict_cell_record_count": str(count),
            })
    if len({row["anonymous_group_id"] for row in output}) != len(output):
        raise ValueError("hash collision")
    if set(FIELDS) & FORBIDDEN:
        raise ValueError("forbidden schema")
    targets = [row for row in output if row["supported_class_target"] == "1"]
    movable = [row for row in targets if row["split"] == "TEST" and row["strict_test_movable"] == "1"]
    counts = Counter(row["split"] for row in targets)
    manifest = {
        "experiment": "LRS001R1_label_free_pseudonymous_geometry",
        "status": "PASS_LABEL_FREE_PSEUDONYMOUS_GEOMETRY",
        "decision": "GO_TARGET_BLIND_SYNTHETIC_CALIBRATION_ONLY",
        "inputs": {
            str(SPEC.relative_to(HERE)): EXPECTED[SPEC], str(CAPACITY.relative_to(HERE)): EXPECTED[CAPACITY],
            str(ATLAS.relative_to(HERE)): EXPECTED[ATLAS], str(SPLITS.relative_to(HERE)): EXPECTED[SPLITS],
        },
        "implementation": {str(PRODUCER.relative_to(HERE)): EXPECTED[PRODUCER]},
        "schema": list(FIELDS),
        "opaque_class_count_by_symbol_count": CLASS_LAYOUT,
        "counts": {"rows": len(output), "records": len(segments),
                   "supported_targets_by_split": dict(sorted(counts.items())),
                   "strict_movable_test_targets": len(movable),
                   "strict_movable_test_records": len({row["anonymous_record_id"] for row in movable}),
                   "strict_test_cells": len({row["strict_cell_id"] for row in movable})},
        "geometry_sha256": sha(canonical(output)),
        "isolation": {"real_class_identity_or_family_surface_emitted": False,
                      "surface_derived_target_eligibility_emitted": True,
                      "identifiers_claimed_information_secure_anonymous": False,
                      "real_context_target_association_scored": False, "predictor_fitted": False,
                      "ocr_or_automated_vision_used": False},
        "claim_ceiling": "Label-free pseudonymous geometry supplies no schema, field, word, meaning, plaintext, or translation.",
    }
    manifest["tsv_sha256"] = sha(tsv_bytes(output))
    return output, manifest


def report(manifest: dict[str, object]) -> str:
    c = manifest["counts"]
    assert isinstance(c, dict)
    return (
        "# LRS001-R1 label-free pseudonymous calibration geometry\n\nStatus: **PASS_LABEL_FREE_PSEUDONYMOUS_GEOMETRY**.\n\n"
        f"The label-free artifact contains {c['rows']:,} groups in {c['records']:,} records. Supported target geometry is TRAIN/CAL/TEST {c['supported_targets_by_split']['TRAIN']}/{c['supported_targets_by_split']['CAL']}/{c['supported_targets_by_split']['TEST']}; the strict movable TEST panel is {c['strict_movable_test_targets']:,} targets in {c['strict_movable_test_records']} records and {c['strict_test_cells']} cells.\n\n"
        "No family surface, class identity, member code, EVA, transcription token, parser root/role, image, OCR, gloss, predictor, or real association is present. The deterministic public-row hashes are pseudonymous, not information-secure anonymous; the target-eligibility bit is surface-derived.\n\n"
        f"Claim ceiling: {manifest['claim_ceiling']}\n"
    )


def main() -> None:
    if OUT.exists() or OUT_REPORT.exists():
        raise SystemExit("refusing overwrite")
    checks: list[str] = []
    for path, expected in EXPECTED.items():
        if sha(path.read_bytes()) != expected:
            raise SystemExit(f"hash mismatch: {path}")
        checks.append("sha256:" + path.name)
    atlas_rows, split_rows = table(ATLAS), table(SPLITS)
    output, manifest = rebuild(atlas_rows, split_rows)
    if tsv_bytes(output) != TSV.read_bytes():
        raise SystemExit("TSV reconstruction")
    checks.append("exact_tsv_reconstruction")
    if canonical(manifest) != RESULT.read_bytes():
        raise SystemExit("JSON reconstruction")
    checks.append("exact_json_reconstruction")
    if report(manifest) != REPORT.read_text():
        raise SystemExit("report reconstruction")
    checks.append("exact_report_reconstruction")
    stored = table(TSV)
    if tuple(stored[0]) != FIELDS or any(set(row) != set(FIELDS) for row in stored):
        raise SystemExit("schema order/drift")
    if set(FIELDS) & FORBIDDEN:
        raise SystemExit("forbidden field")
    checks.extend(["exact_schema", "forbidden_field_absence"])
    mutations: dict[str, bool] = {}
    changed = copy.deepcopy(split_rows); changed.append(dict(changed[0]))
    mutations["duplicate_split_rejected"] = reject(lambda: rebuild(atlas_rows, changed))
    changed_atlas = copy.deepcopy(atlas_rows)
    row = next(row for row in changed_atlas if row["grammar_scope"] == "CONFIRMED_PROSE" and 5 <= int(row["segment_group_count"]) <= 12)
    row["code"] = "MUTATED"
    mutations["within_record_cell_drift_rejected"] = reject(lambda: rebuild(changed_atlas, split_rows))
    changed_atlas = copy.deepcopy(atlas_rows)
    row = next(row for row in changed_atlas if row["grammar_scope"] == "CONFIRMED_PROSE" and 5 <= int(row["segment_group_count"]) <= 12)
    row["page"] = "f999x"
    mutations["metadata_drift_rejected"] = reject(lambda: rebuild(changed_atlas, split_rows))
    if not all(mutations.values()):
        raise SystemExit(f"mutation failure: {mutations}")
    checks.extend(sorted(mutations))
    validation = {
        "experiment": "LRS001R1_anonymous_geometry_validation", "status": "PASS",
        "decision": manifest["decision"], "check_count": len(checks), "checks": checks,
        "mutations": mutations, "reconstructed_counts": manifest["counts"],
        "bound_hashes": {str(path.relative_to(HERE)): value for path, value in EXPECTED.items()},
        "isolation": manifest["isolation"], "claim_ceiling": manifest["claim_ceiling"],
    }
    OUT.write_bytes(canonical(validation))
    OUT_REPORT.write_text(
        "# LRS001-R1 label-free pseudonymous geometry validation\n\nStatus: **PASS**.\n\n"
        f"A clean-room nonimporting reconstruction passed {len(checks)} hash, content, schema, isolation, and mutation checks and recovered all {manifest['counts']['rows']:,} rows exactly.\n\n"
        "The synthetic-calibration geometry contains no class identity, family surface, or real context/target pairing. Its public-row hashes are pseudonymous and its eligibility bit is target-derived.\n\n"
        f"Claim ceiling: {manifest['claim_ceiling']}\n"
    )
    print(json.dumps({"status": "PASS", "checks": len(checks)}, sort_keys=True))


if __name__ == "__main__":
    main()
