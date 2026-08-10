#!/usr/bin/env python3
"""Score-blind capacity audit for ETR001 exact-template recurrence."""

from __future__ import annotations

import csv
import hashlib
import itertools
import json
import math
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
SPEC = HERE / "ETR001_EXACT_TEMPLATE_RECURRENCE_CAPACITY_SPEC.md"
GEOMETRY_TSV = RESULTS / "lrs001r1_anonymous_geometry.tsv"
GEOMETRY_JSON = RESULTS / "lrs001r1_anonymous_geometry.json"
ATLAS_TSV = RESULTS / "drawing_reset_segment_atlas.tsv"
ATLAS_JSON = RESULTS / "drawing_reset_segment_atlas.json"
CONSENSUS_TSV = RESULTS / "source_sta_family_consensus_groups.tsv"
CONSENSUS_JSON = RESULTS / "source_sta_family_consensus.json"
OUT_JSON = RESULTS / "etr001_exact_template_capacity.json"
OUT_REPORT = RESULTS / "etr001_exact_template_capacity.md"

EXPECTED_HASHES = {
    GEOMETRY_TSV: "37f06364effab97140d50fd64984ee561ed84f9087866314db7fec4f059647df",
    GEOMETRY_JSON: "0c251db4526f54a1b3bec15528f32a95c782d3a7d8f134ab49b6afb872bd1542",
    ATLAS_TSV: "e303f9298e5d76473e7ddd311370e3486cb9997dfb58c05df40c3fb3b4de2486",
    ATLAS_JSON: "3e7f07d1c22e331f3bde713e79250c03065e83ec5954868be545cb91287d2279",
    CONSENSUS_TSV: "a202d93498e8a350a5d7e0ca46e831dcc37ea5c0182dc404d63cb797a98b1225",
    CONSENSUS_JSON: "193ac76bd14b3967844035e8c3997f402d556c7aecf3190145c5295b4eeab3f7",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"),
                       ensure_ascii=True, allow_nan=False) + "\n").encode("utf-8")


def anonymous_group(consensus_group_id: str) -> str:
    payload = f"LRS001R1|G|{consensus_group_id}".encode("utf-8")
    return "G" + hashlib.sha256(payload).hexdigest()[:20]


def build() -> dict[str, object]:
    for path, expected in EXPECTED_HASHES.items():
        if sha(path) != expected:
            raise ValueError(f"input hash drift: {path.name}")

    geometry_source_rows: list[dict[str, str]] = []
    target_mask: dict[str, bool] = {}
    with GEOMETRY_TSV.open(newline="", encoding="utf-8") as handle:
        for source in csv.DictReader(handle, delimiter="\t"):
            row = dict(source)
            identifier = row["anonymous_group_id"]
            if identifier in target_mask:
                raise ValueError(f"duplicate geometry group: {identifier}")
            if row["supported_class_target"] not in {"0", "1"}:
                raise ValueError("nonbinary target mask")
            target_mask[identifier] = row["supported_class_target"] == "1"
            geometry_source_rows.append(row)
    if len(geometry_source_rows) != 18_063:
        raise ValueError("geometry cardinality drift")

    # Target family identities are discarded as each source row is read.  The
    # raw input hashes above are provenance bindings, never feature payloads.
    consensus: dict[str, dict[str, str | None]] = {}
    with CONSENSUS_TSV.open(newline="", encoding="utf-8") as handle:
        for source in csv.DictReader(handle, delimiter="\t"):
            row: dict[str, str | None] = dict(source)
            source_id = str(row["consensus_group_id"])
            identifier = anonymous_group(source_id)
            if identifier not in target_mask:
                continue
            if source_id in consensus:
                raise ValueError(f"duplicate consensus group: {source_id}")
            if target_mask[identifier]:
                row["family_surface"] = None
            consensus[source_id] = row

    atlas_by_anonymous: dict[str, dict[str, str | None]] = {}
    with ATLAS_TSV.open(newline="", encoding="utf-8") as handle:
        for source in csv.DictReader(handle, delimiter="\t"):
            row = dict(source)
            identifier = anonymous_group(row["consensus_group_id"])
            if identifier not in target_mask:
                continue
            if identifier in atlas_by_anonymous:
                raise ValueError(f"duplicate atlas anonymous group: {identifier}")
            comparison = consensus.get(row["consensus_group_id"])
            common_fields = ("symbol_count", "locus", "page", "section",
                             "currier", "hand", "code", "kind")
            if comparison is None or any(row[field] != comparison[field]
                                         for field in common_fields):
                raise ValueError("atlas/consensus source-native drift")
            if target_mask[identifier]:
                row["family_surface"] = None
            elif row["family_surface"] != comparison["family_surface"]:
                raise ValueError("atlas/consensus non-target family drift")
            atlas_by_anonymous[identifier] = row
    if set(atlas_by_anonymous) != set(target_mask):
        raise ValueError("geometry/source group coverage drift")

    records: dict[str, list[dict[str, object]]] = defaultdict(list)
    record_metadata: dict[str, tuple[str, ...]] = {}
    for row in geometry_source_rows:
        atlas = atlas_by_anonymous.get(row["anonymous_group_id"])
        if atlas is None:
            raise ValueError("geometry group missing from source atlas")
        checks = {
            "page": "page", "section": "section", "currier": "currier",
            "hand": "hand", "code": "code", "kind": "kind",
            "segment_group_count": "segment_group_count",
            "segment_group_index": "segment_group_index",
            "segment_count": "segment_count", "segment_index": "segment_index",
            "starts_after_drawing": "starts_after_drawing",
            "ends_before_drawing": "ends_before_drawing",
            "original_group_count": "group_count", "symbol_count": "symbol_count",
        }
        if any(row[left] != atlas[right] for left, right in checks.items()):
            raise ValueError("geometry/atlas field drift")
        record_id = row["anonymous_record_id"]
        metadata = (
            row["physical_folio"], row["section"], row["currier"], row["hand"],
            row["code"], row["segment_count"], row["segment_index"],
            row["starts_after_drawing"], row["ends_before_drawing"],
            row["original_group_count"], row["segment_group_count"],
        )
        if record_id in record_metadata and record_metadata[record_id] != metadata:
            raise ValueError("record metadata drift")
        record_metadata[record_id] = metadata
        target = target_mask[row["anonymous_group_id"]]
        if target and atlas["family_surface"] is not None:
            raise ValueError("target surface was not scrubbed")
        records[record_id].append({
            "ordinal": int(row["segment_group_index"]),
            "symbol_count": int(row["symbol_count"]),
            "target": target,
            "context_surface": None if target else atlas["family_surface"],
        })
    if len(records) != 2_163:
        raise ValueError("geometry cardinality drift")

    strata: dict[tuple[object, ...], list[dict[str, object]]] = defaultdict(list)
    for record_id in sorted(records, key=lambda value: value.encode("utf-8")):
        rows = sorted(records[record_id], key=lambda value: int(value["ordinal"]))
        size = int(record_metadata[record_id][-1])
        if len(rows) != size or [int(row["ordinal"]) for row in rows] != list(range(1, size + 1)):
            raise ValueError("incomplete record")
        target_positions = tuple(int(row["ordinal"]) for row in rows if row["target"])
        if not target_positions:
            continue
        target_lengths = tuple(int(row["symbol_count"]) for row in rows if row["target"])
        context_order = tuple(str(row["context_surface"]) for row in rows if not row["target"])
        if any(value == "None" for value in context_order):
            raise ValueError("target identity entered context")
        context_bag = tuple(sorted(context_order, key=lambda value: value.encode("utf-8")))
        folio, section, currier, hand, code, segment_count, segment_index, \
            starts_after, ends_before, original_count, _ = record_metadata[record_id]
        stratum_key = (
            size, target_positions, target_lengths, section, currier, hand, code,
            segment_count, segment_index, starts_after, ends_before,
            original_count, context_bag,
        )
        strata[stratum_key].append({
            "record_id": record_id, "folio": folio,
            "target_slots": len(target_positions), "context_order": context_order,
        })

    informative: list[dict[str, object]] = []
    panel_rows: list[dict[str, object]] = []
    identical_pairs = different_pairs = masked_comparisons = 0
    endpoint_folios: Counter[str] = Counter()
    orbit_bits = 0.0
    for key in sorted(strata, key=canonical):
        members = strata[key]
        orders: dict[tuple[str, ...], list[dict[str, object]]] = defaultdict(list)
        for member in members:
            orders[member["context_order"]].append(member)
        same: list[tuple[dict[str, object], dict[str, object]]] = []
        for order_members in orders.values():
            same.extend((left, right) for left, right in itertools.combinations(order_members, 2)
                        if left["folio"] != right["folio"])
        different = [
            (left, right)
            for left, right in itertools.combinations(members, 2)
            if left["folio"] != right["folio"] and
            left["context_order"] != right["context_order"]
        ]
        if not same or not different:
            continue
        orbit_bits += math.lgamma(len(members) + 1.0) / math.log(2.0)
        slots = int(members[0]["target_slots"])
        identical_pairs += len(same)
        different_pairs += len(different)
        masked_comparisons += (len(same) + len(different)) * slots
        for left, right in (*same, *different):
            endpoint_folios[str(left["folio"])] += 1
            endpoint_folios[str(right["folio"])] += 1
        stratum_hash = hashlib.sha256(canonical(key)).hexdigest()
        informative.append({
            "stratum_sha256": stratum_hash, "records": len(members),
            "orders": len(orders), "target_slots": slots,
            "identical_pairs": len(same), "different_pairs": len(different),
        })
        panel_rows.extend({
            "stratum_sha256": stratum_hash,
            "record_id": str(member["record_id"]), "folio": str(member["folio"]),
            "order_sha256": hashlib.sha256(canonical(member["context_order"])).hexdigest(),
            "target_slots": slots,
        } for member in members)

    total_endpoints = sum(endpoint_folios.values())
    maximum_exposure = (max(endpoint_folios.values()) / total_endpoints
                        if total_endpoints else 1.0)
    counts = {
        "source_geometry_rows": len(geometry_source_rows),
        "source_records": len(records),
        "masked_target_bearing_records": sum(len(values) for values in strata.values()),
        "informative_strata": len(informative),
        "identical_order_cross_folio_pairs": identical_pairs,
        "different_order_cross_folio_pairs": different_pairs,
        "masked_target_comparisons": masked_comparisons,
        "physical_folios": len(endpoint_folios),
        "maximum_folio_endpoint_exposure": maximum_exposure,
        "capacity_orbit_log2": orbit_bits,
    }
    gates = {
        "at_least_12_informative_strata": len(informative) >= 12,
        "at_least_100_masked_target_comparisons": masked_comparisons >= 100,
        "at_least_8_physical_folios": len(endpoint_folios) >= 8,
        "at_least_32_identical_order_pairs": identical_pairs >= 32,
        "at_least_32_different_order_pairs": different_pairs >= 32,
        "capacity_orbit_at_least_8192": orbit_bits >= 13.0,
        "maximum_folio_exposure_at_most_025": maximum_exposure <= 0.25,
    }
    passed = all(gates.values())
    return {
        "experiment": "ETR001_EXACT_TEMPLATE_RECURRENCE_CAPACITY",
        "status": ("PASS_SCORE_BLIND_CAPACITY" if passed else "STOP_SCORE_BLIND_CAPACITY"),
        "decision": ("GO_TARGET_BLIND_SYNTHETIC_CALIBRATION_ONLY" if passed else
                     "STOP_ETR001_UNOPENED"),
        "inputs": {str(path.relative_to(HERE)): expected
                   for path, expected in EXPECTED_HASHES.items()},
        "implementation": {
            str(SPEC.relative_to(HERE)): sha(SPEC),
            str(Path(__file__).resolve().relative_to(HERE)): sha(Path(__file__).resolve()),
        },
        "counts": counts, "gates": gates,
        "capacity_panel_sha256": hashlib.sha256(canonical(panel_rows)).hexdigest(),
        "informative_summary_sha256": hashlib.sha256(canonical(informative)).hexdigest(),
        "isolation": {
            "target_family_identity_used_in_key_equality_count_or_digest": False,
            "target_family_equality_scored": False,
            "model_or_predictor_fitted": False,
            "legacy_parser_root_or_role_used": False,
            "ocr_or_automated_vision_used": False,
        },
        "claim_ceiling": (
            "Score-blind exact-template capacity only; no field, word, POS, language, "
            "meaning, plaintext, or translation."
        ),
    }


def report(result: dict[str, object]) -> str:
    counts = result["counts"]
    gates = result["gates"]
    return (
        "# ETR001 exact-template recurrence capacity\n\n"
        f"Status: **{result['status']}**.\n\n"
        f"Informative strata: {counts['informative_strata']}; exact-order pairs: "
        f"{counts['identical_order_cross_folio_pairs']}; different-order pairs: "
        f"{counts['different_order_cross_folio_pairs']}; masked target comparisons: "
        f"{counts['masked_target_comparisons']}; folios: {counts['physical_folios']}; "
        f"orbit: {counts['capacity_orbit_log2']:.4f} bits; maximum folio exposure: "
        f"{counts['maximum_folio_endpoint_exposure']:.4f}.\n\n"
        f"Gates passed: {sum(bool(value) for value in gates.values())}/{len(gates)}. "
        f"Decision: **{result['decision']}**.\n\n"
        "No target-family identity or equality was used in a stratum, count, digest, "
        "or score. This result supplies no field, word, POS, language, meaning, "
        "plaintext, or translation.\n"
    )


def main() -> None:
    if OUT_JSON.exists() or OUT_REPORT.exists():
        raise SystemExit("refusing to overwrite ETR001 capacity outputs")
    result = build()
    OUT_JSON.write_bytes(canonical(result))
    OUT_REPORT.write_text(report(result), encoding="utf-8")
    print(json.dumps({"status": result["status"], "decision": result["decision"]},
                     sort_keys=True))


if __name__ == "__main__":
    main()
