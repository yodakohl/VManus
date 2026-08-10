#!/usr/bin/env python3
"""Independent, nonimporting validator for the frozen ETR001 capacity result.

This program deliberately does not import, execute, or inspect the producer.
It reconstructs the capacity panel directly from the six frozen inputs.  The
geometry target mask is loaded first; target family surfaces are overwritten
and discarded as each source row is parsed.
"""

from __future__ import annotations

import csv
import hashlib
import itertools
import json
import math
import os
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"

SPEC = HERE / "ETR001_EXACT_TEMPLATE_RECURRENCE_CAPACITY_SPEC.md"
GEOMETRY_TSV = RESULTS / "lrs001r1_anonymous_geometry.tsv"
GEOMETRY_JSON = RESULTS / "lrs001r1_anonymous_geometry.json"
ATLAS_TSV = RESULTS / "drawing_reset_segment_atlas.tsv"
ATLAS_JSON = RESULTS / "drawing_reset_segment_atlas.json"
CONSENSUS_TSV = RESULTS / "source_sta_family_consensus_groups.tsv"
CONSENSUS_JSON = RESULTS / "source_sta_family_consensus.json"
PRODUCER_RESULT = RESULTS / "etr001_exact_template_capacity.json"
PRODUCER_REPORT = RESULTS / "etr001_exact_template_capacity.md"
VALIDATION_JSON = RESULTS / "etr001_exact_template_capacity_validation.json"
VALIDATION_REPORT = RESULTS / "etr001_exact_template_capacity_validation.md"

EXPECTED_SPEC_SHA = "c9ce3802969cc1dd40849ec34bda3632d52fcab3f2b2032dc293478757528640"
EXPECTED_PRODUCER_SHA = "e6bb4cd2140f69a5f17ac81b414e57ffa79ee2ee22a4329afa490474e3c1ae45"
EXPECTED_RESULT_SHA = "6134b4d936d4fe94d5d918ccd1bf2a2942a490854d3bdfe5cc1d73efd41450b4"
EXPECTED_REPORT_SHA = "abb98c0d3d7805a865d101dd3706546f1cb1490b98389714922d3e2e8d663bff"

INPUT_HASHES = {
    "results/drawing_reset_segment_atlas.json": "3e7f07d1c22e331f3bde713e79250c03065e83ec5954868be545cb91287d2279",
    "results/drawing_reset_segment_atlas.tsv": "e303f9298e5d76473e7ddd311370e3486cb9997dfb58c05df40c3fb3b4de2486",
    "results/lrs001r1_anonymous_geometry.json": "0c251db4526f54a1b3bec15528f32a95c782d3a7d8f134ab49b6afb872bd1542",
    "results/lrs001r1_anonymous_geometry.tsv": "37f06364effab97140d50fd64984ee561ed84f9087866314db7fec4f059647df",
    "results/source_sta_family_consensus.json": "193ac76bd14b3967844035e8c3997f402d556c7aecf3190145c5295b4eeab3f7",
    "results/source_sta_family_consensus_groups.tsv": "a202d93498e8a350a5d7e0ca46e831dcc37ea5c0182dc404d63cb797a98b1225",
}

GEOMETRY_HEADER = (
    "anonymous_group_id", "anonymous_record_id", "split", "page",
    "physical_folio", "section", "currier", "hand", "code", "kind",
    "segment_group_count", "segment_group_index", "segment_position",
    "segment_count", "segment_index", "starts_after_drawing",
    "ends_before_drawing", "original_group_count", "symbol_count",
    "supported_class_target", "strict_test_movable", "strict_cell_id",
    "strict_cell_record_count",
)

ATLAS_HEADER = (
    "segment_id", "segment_index", "segment_count", "segment_group_index",
    "segment_group_count", "segment_position", "starts_after_drawing",
    "ends_before_drawing", "consensus_group_id", "locus", "page",
    "section", "currier", "hand", "code", "kind", "grammar_scope",
    "group_index", "group_count", "factual_position", "family_surface",
    "symbol_count", "zl_sta_codes", "it_sta_codes", "rf_sta_codes",
    "zl_basic_eva_lossy", "it_basic_eva_lossy", "rf_basic_eva_lossy",
    "left_boundary_profile", "left_boundary_support",
    "right_boundary_profile", "right_boundary_support",
    "exact_first_last_label", "exact_edge_core_label",
    "opening_feature_hits", "closing_feature_hits",
    "favored_transition_hits", "disfavored_transition_hits",
    "unresolved_transition_hits", "favored_path_hits",
    "longest_opening_path", "longest_path_anywhere",
)

CONSENSUS_HEADER = (
    "consensus_group_id", "locus", "page", "section", "currier", "hand",
    "code", "kind", "grammar_scope", "strict_zero_alternative",
    "consensus_group_index", "consensus_group_count", "start_symbol_1based",
    "end_symbol_1based", "symbol_count", "family_surface", "zl_sta_codes",
    "it_sta_codes", "rf_sta_codes", "left_boundary_profile",
    "right_boundary_profile",
)

CLAIM_CEILING = (
    "Score-blind exact-template capacity only; no field, word, POS, language, "
    "meaning, plaintext, or translation."
)


class ValidationError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValidationError(message)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def canonical_json_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def load_canonical_json(path: Path) -> tuple[dict[str, Any], bytes]:
    raw = path.read_bytes()
    parsed = json.loads(raw.decode("utf-8"))
    require(isinstance(parsed, dict), f"{path.name}: top-level JSON is not an object")
    require(raw == canonical_json_bytes(parsed), f"{path.name}: JSON is not canonical")
    return parsed, raw


def load_json_object(path: Path) -> dict[str, Any]:
    parsed = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(parsed, dict), f"{path.name}: top-level JSON is not an object")
    return parsed


def exact_int(text: str, field: str, minimum: int | None = None) -> int:
    require(text != "", f"empty integer field: {field}")
    try:
        value = int(text)
    except ValueError as exc:
        raise ValidationError(f"invalid integer field: {field}") from exc
    require(str(value) == text, f"noncanonical integer field: {field}")
    if minimum is not None:
        require(value >= minimum, f"integer below minimum: {field}")
    return value


def read_tsv_rows(path: Path, expected_header: tuple[str, ...]) -> Iterable[list[str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle, delimiter="\t", quoting=csv.QUOTE_NONE)
        try:
            header = tuple(next(reader))
        except StopIteration as exc:
            raise ValidationError(f"{path.name}: empty TSV") from exc
        require(header == expected_header, f"{path.name}: unexpected schema")
        for line_number, values in enumerate(reader, 2):
            require(len(values) == len(header), f"{path.name}: malformed row {line_number}")
            yield values


def pseudonym(consensus_group_id: str) -> str:
    digest = hashlib.sha256(("LRS001R1|G|" + consensus_group_id).encode("utf-8")).hexdigest()
    return "G" + digest[:20]


def load_geometry() -> tuple[list[dict[str, str]], set[str], dict[str, dict[str, str]]]:
    rows: list[dict[str, str]] = []
    by_group: dict[str, dict[str, str]] = {}
    target_ids: set[str] = set()
    for values in read_tsv_rows(GEOMETRY_TSV, GEOMETRY_HEADER):
        row = dict(zip(GEOMETRY_HEADER, values))
        gid = row["anonymous_group_id"]
        require(len(gid) == 21 and gid[0] == "G" and all(c in "0123456789abcdef" for c in gid[1:]), "invalid anonymous group ID")
        require(gid not in by_group, "duplicate anonymous group ID")
        require(row["supported_class_target"] in {"0", "1"}, "invalid supported target bit")
        require(row["strict_test_movable"] in {"0", "1"}, "invalid strict movable bit")
        length = exact_int(row["segment_group_count"], "segment_group_count", 1)
        ordinal = exact_int(row["segment_group_index"], "segment_group_index", 1)
        exact_int(row["symbol_count"], "symbol_count", 1)
        require(5 <= length <= 12 and ordinal <= length, "geometry outside frozen record geometry")
        if row["supported_class_target"] == "1":
            target_ids.add(gid)
        by_group[gid] = row
        rows.append(row)
    require(len(rows) == 18063, "geometry row count mismatch")
    require(len({row["anonymous_record_id"] for row in rows}) == 2163, "geometry record count mismatch")
    require(len(target_ids) == 8173, "supported target count mismatch")
    return rows, target_ids, by_group


def load_source_subset(
    path: Path,
    header: tuple[str, ...],
    target_ids: set[str],
    geometry_ids: set[str],
    mutation_tag: str | None,
) -> tuple[dict[str, dict[str, str]], int]:
    """Load geometry members, scrubbing a target surface before making a row dict."""
    consensus_i = header.index("consensus_group_id")
    surface_i = header.index("family_surface")
    retained: dict[str, dict[str, str]] = {}
    mutated_and_scrubbed = 0
    seen_target_ids: set[str] = set()
    seen_all_ids: set[str] = set()
    for values in read_tsv_rows(path, header):
        gid = pseudonym(values[consensus_i])
        require(gid not in seen_all_ids, f"{path.name}: duplicate pseudonymous group")
        seen_all_ids.add(gid)

        # Mask-first rule: target membership comes only from geometry.  Replace
        # the field for the mutation control, then discard it before a row dict
        # or any comparison/key/count/digest can be created.
        if gid in target_ids:
            if mutation_tag is not None:
                values[surface_i] = mutation_tag + hashlib.sha256((path.name + "|" + gid).encode("utf-8")).hexdigest()
                mutated_and_scrubbed += 1
            values[surface_i] = ""
            seen_target_ids.add(gid)

        if gid not in geometry_ids:
            continue
        if gid in target_ids:
            # Retain no source-table target content except the fields permitted
            # by the frozen mask-first contract.  Record ordinal is available
            # only in the segmented atlas; geometry remains authoritative.
            row = {"symbol_count": values[header.index("symbol_count")]}
            if "segment_group_index" in header:
                row["physical_ordinal"] = values[header.index("segment_group_index")]
        else:
            row = dict(zip(header, values))
            require(row["family_surface"] != "", f"{path.name}: missing non-target family surface")
        require(gid not in retained, f"{path.name}: repeated retained group")
        retained[gid] = row

    require(seen_target_ids == target_ids, f"{path.name}: target mask does not map one-to-one")
    require(set(retained) == geometry_ids, f"{path.name}: incomplete geometry reconstruction")
    if mutation_tag is None:
        require(mutated_and_scrubbed == 0, "baseline source load unexpectedly mutated")
    else:
        require(mutated_and_scrubbed == len(target_ids), f"{path.name}: incomplete target mutation")
    return retained, mutated_and_scrubbed


def check_group_sources(
    geometry_rows: list[dict[str, str]],
    atlas: dict[str, dict[str, str]],
    consensus: dict[str, dict[str, str]],
    target_ids: set[str],
) -> None:
    atlas_equal = (
        ("page", "page"), ("section", "section"), ("currier", "currier"),
        ("hand", "hand"), ("code", "code"), ("kind", "kind"),
        ("segment_group_count", "segment_group_count"),
        ("segment_group_index", "segment_group_index"),
        ("segment_position", "segment_position"),
        ("segment_count", "segment_count"), ("segment_index", "segment_index"),
        ("starts_after_drawing", "starts_after_drawing"),
        ("ends_before_drawing", "ends_before_drawing"),
        ("original_group_count", "group_count"), ("symbol_count", "symbol_count"),
    )
    consensus_equal = (
        "page", "section", "currier", "hand", "code", "kind", "symbol_count",
    )
    for geom in geometry_rows:
        gid = geom["anonymous_group_id"]
        arow = atlas[gid]
        crow = consensus[gid]
        require(arow["symbol_count"] == crow["symbol_count"], "source symbol-count disagreement")
        if gid in target_ids:
            require(set(arow) == {"symbol_count", "physical_ordinal"}, "atlas target row retained a forbidden source field")
            require(set(crow) == {"symbol_count"}, "consensus target row retained a forbidden source field")
            require(geom["symbol_count"] == arow["symbol_count"], "target source symbol-count mismatch")
            require(geom["segment_group_index"] == arow["physical_ordinal"], "target source ordinal mismatch")
        else:
            require(gid == pseudonym(arow["consensus_group_id"]), "atlas pseudonym mismatch")
            require(gid == pseudonym(crow["consensus_group_id"]), "consensus pseudonym mismatch")
            for gfield, afield in atlas_equal:
                require(geom[gfield] == arow[afield], f"atlas geometry mismatch: {gfield}")
            for field in consensus_equal:
                require(geom[field] == crow[field], f"consensus geometry mismatch: {field}")
            require(arow["family_surface"] == crow["family_surface"], "non-target family-surface disagreement")


def stable_stratum_payload(key: tuple[Any, ...]) -> list[Any]:
    record_length, mask, target_lengths, *rest = key
    return [record_length, list(mask), list(target_lengths), *rest[:-1], list(rest[-1])]


def derive_capacity(
    geometry_rows: list[dict[str, str]],
    target_ids: set[str],
    mutation_tag: str | None,
) -> tuple[dict[str, Any], list[dict[str, Any]], dict[str, int]]:
    geometry_ids = {row["anonymous_group_id"] for row in geometry_rows}
    atlas, atlas_mutations = load_source_subset(
        ATLAS_TSV, ATLAS_HEADER, target_ids, geometry_ids, mutation_tag
    )
    consensus, consensus_mutations = load_source_subset(
        CONSENSUS_TSV, CONSENSUS_HEADER, target_ids, geometry_ids, mutation_tag
    )
    check_group_sources(geometry_rows, atlas, consensus, target_ids)

    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in geometry_rows:
        grouped[row["anonymous_record_id"]].append(row)

    strata: dict[tuple[Any, ...], list[dict[str, Any]]] = defaultdict(list)
    target_bearing_records = 0
    invariant_fields = (
        "page", "physical_folio", "section", "currier", "hand", "code", "kind",
        "segment_group_count", "segment_count", "segment_index",
        "starts_after_drawing", "ends_before_drawing", "original_group_count",
    )
    for record_id in sorted(grouped, key=lambda s: s.encode("utf-8")):
        rows = sorted(grouped[record_id], key=lambda row: exact_int(row["segment_group_index"], "segment_group_index", 1))
        length = exact_int(rows[0]["segment_group_count"], "segment_group_count", 1)
        require(len(rows) == length, "record row count differs from record length")
        require([exact_int(row["segment_group_index"], "segment_group_index", 1) for row in rows] == list(range(1, length + 1)), "record ordinals are not contiguous")
        for field in invariant_fields:
            require(len({row[field] for row in rows}) == 1, f"record metadata is not invariant: {field}")

        mask = tuple(row["supported_class_target"] == "1" for row in rows)
        target_lengths = tuple(exact_int(row["symbol_count"], "symbol_count", 1) for row in rows if row["supported_class_target"] == "1")
        if target_lengths:
            target_bearing_records += 1
        ordered_context = tuple(
            atlas[row["anonymous_group_id"]]["family_surface"]
            for row in rows
            if row["supported_class_target"] == "0"
        )
        context_bag = tuple(sorted(ordered_context, key=lambda s: s.encode("utf-8")))
        key = (
            length, mask, target_lengths, rows[0]["section"], rows[0]["currier"],
            rows[0]["hand"], rows[0]["code"], rows[0]["segment_count"],
            rows[0]["segment_index"], rows[0]["starts_after_drawing"],
            rows[0]["ends_before_drawing"], rows[0]["original_group_count"],
            context_bag,
        )
        strata[key].append({
            "record_id": record_id,
            "folio": rows[0]["physical_folio"],
            "ordered_context": ordered_context,
            "target_count": len(target_lengths),
        })

    require(target_bearing_records == 2121, "target-bearing record count mismatch")

    informative: list[dict[str, Any]] = []
    endpoint_counts: Counter[str] = Counter()
    physical_folios: set[str] = set()
    total_identical = 0
    total_different = 0
    total_target_comparisons = 0
    orbit_log2 = 0.0

    ordered_strata = sorted(
        strata.items(),
        key=lambda item: canonical_json_bytes(stable_stratum_payload(item[0])),
    )
    for key, records in ordered_strata:
        identical: list[tuple[dict[str, Any], dict[str, Any]]] = []
        different: list[tuple[dict[str, Any], dict[str, Any]]] = []
        for left, right in itertools.combinations(records, 2):
            if left["folio"] == right["folio"]:
                continue
            if left["ordered_context"] == right["ordered_context"]:
                identical.append((left, right))
            else:
                different.append((left, right))
        if not identical or not different:
            continue

        target_count = records[0]["target_count"]
        require(all(record["target_count"] == target_count for record in records), "target mask mismatch within stratum")
        pairs = identical + different
        for left, right in pairs:
            endpoint_counts[left["folio"]] += 1
            endpoint_counts[right["folio"]] += 1
            physical_folios.update((left["folio"], right["folio"]))
        identical_count = len(identical)
        different_count = len(different)
        pair_count = identical_count + different_count
        total_identical += identical_count
        total_different += different_count
        total_target_comparisons += pair_count * target_count
        orbit_log2 += math.lgamma(len(records) + 1) / math.log(2.0)

        stratum_payload = stable_stratum_payload(key)
        informative.append({
            "stratum_sha256": sha256_bytes(canonical_json_bytes(stratum_payload)),
            "records": len(records),
            "target_slots": target_count,
            "identical_order_cross_folio_pairs": identical_count,
            "different_order_cross_folio_pairs": different_count,
            "masked_target_comparisons": pair_count * target_count,
            "capacity_orbit_log2": math.lgamma(len(records) + 1) / math.log(2.0),
        })

    endpoint_total = sum(endpoint_counts.values())
    maximum_exposure = max(endpoint_counts.values()) / endpoint_total if endpoint_total else 1.0
    counts: dict[str, Any] = {
        "capacity_orbit_log2": orbit_log2,
        "different_order_cross_folio_pairs": total_different,
        "identical_order_cross_folio_pairs": total_identical,
        "informative_strata": len(informative),
        "masked_target_bearing_records": target_bearing_records,
        "masked_target_comparisons": total_target_comparisons,
        "maximum_folio_endpoint_exposure": maximum_exposure,
        "physical_folios": len(physical_folios),
        "source_geometry_rows": len(geometry_rows),
        "source_records": len(grouped),
    }
    mutation_counts = {
        "atlas_target_surfaces_replaced_then_scrubbed": atlas_mutations,
        "consensus_target_surfaces_replaced_then_scrubbed": consensus_mutations,
    }
    return counts, informative, mutation_counts


def build_gates(counts: dict[str, Any]) -> dict[str, bool]:
    return {
        "at_least_100_masked_target_comparisons": counts["masked_target_comparisons"] >= 100,
        "at_least_12_informative_strata": counts["informative_strata"] >= 12,
        "at_least_32_different_order_pairs": counts["different_order_cross_folio_pairs"] >= 32,
        "at_least_32_identical_order_pairs": counts["identical_order_cross_folio_pairs"] >= 32,
        "at_least_8_physical_folios": counts["physical_folios"] >= 8,
        "capacity_orbit_at_least_8192": counts["capacity_orbit_log2"] >= 13.0,
        "maximum_folio_exposure_at_most_025": counts["maximum_folio_endpoint_exposure"] <= 0.25,
    }


def build_result(counts: dict[str, Any], informative: list[dict[str, Any]]) -> dict[str, Any]:
    panel_sha = sha256_bytes(canonical_json_bytes(informative))
    gates = build_gates(counts)
    return {
        "capacity_panel_sha256": panel_sha,
        "claim_ceiling": CLAIM_CEILING,
        "counts": counts,
        "decision": "STOP_ETR001_UNOPENED" if not all(gates.values()) else "GO_ETR001_TARGET_BLIND_CALIBRATION_ONLY",
        "experiment": "ETR001_EXACT_TEMPLATE_RECURRENCE_CAPACITY",
        "gates": gates,
        "implementation": {
            "ETR001_EXACT_TEMPLATE_RECURRENCE_CAPACITY_SPEC.md": EXPECTED_SPEC_SHA,
            "audit_etr001_exact_template_capacity.py": EXPECTED_PRODUCER_SHA,
        },
        "informative_summary_sha256": panel_sha,
        "inputs": dict(sorted(INPUT_HASHES.items())),
        "isolation": {
            "legacy_parser_root_or_role_used": False,
            "model_or_predictor_fitted": False,
            "ocr_or_automated_vision_used": False,
            "target_family_equality_scored": False,
            "target_family_identity_used_in_key_equality_count_or_digest": False,
        },
        "status": "STOP_SCORE_BLIND_CAPACITY" if not all(gates.values()) else "PASS_SCORE_BLIND_CAPACITY",
    }


def build_producer_report(result: dict[str, Any]) -> bytes:
    counts = result["counts"]
    gates = result["gates"]
    text = (
        "# ETR001 exact-template recurrence capacity\n\n"
        f"Status: **{result['status']}**.\n\n"
        f"Informative strata: {counts['informative_strata']}; exact-order pairs: "
        f"{counts['identical_order_cross_folio_pairs']}; different-order pairs: "
        f"{counts['different_order_cross_folio_pairs']}; masked target comparisons: "
        f"{counts['masked_target_comparisons']}; folios: {counts['physical_folios']}; "
        f"orbit: {counts['capacity_orbit_log2']:.4f} bits; maximum folio exposure: "
        f"{counts['maximum_folio_endpoint_exposure']:.4f}.\n\n"
        f"Gates passed: {sum(gates.values())}/7. Decision: **{result['decision']}**.\n\n"
        "No target-family identity or equality was used in a stratum, count, digest, or score. "
        "This result supplies no field, word, POS, language, meaning, plaintext, or translation.\n"
    )
    return text.encode("utf-8")


def validate_manifests() -> None:
    for relative, expected in INPUT_HASHES.items():
        require(sha256_file(HERE / relative) == expected, f"frozen input hash mismatch: {relative}")
    require(sha256_file(SPEC) == EXPECTED_SPEC_SHA, "frozen specification hash mismatch")
    require(sha256_file(PRODUCER_RESULT) == EXPECTED_RESULT_SHA, "producer result hash mismatch")
    require(sha256_file(PRODUCER_REPORT) == EXPECTED_REPORT_SHA, "producer report hash mismatch")

    geometry = load_json_object(GEOMETRY_JSON)
    require(geometry.get("tsv_sha256") == INPUT_HASHES["results/lrs001r1_anonymous_geometry.tsv"], "geometry manifest TSV binding mismatch")
    require(geometry.get("counts", {}).get("rows") == 18063, "geometry manifest row count mismatch")
    require(geometry.get("counts", {}).get("records") == 2163, "geometry manifest record count mismatch")

    atlas = load_json_object(ATLAS_JSON)
    require(atlas.get("atlas_sha256") == INPUT_HASHES["results/drawing_reset_segment_atlas.tsv"], "atlas manifest TSV binding mismatch")
    require(atlas.get("counts", {}).get("rows") == 23281, "atlas manifest row count mismatch")

    consensus = load_json_object(CONSENSUS_JSON)
    groups = consensus.get("outputs", {}).get("groups", {})
    require(groups.get("sha256") == INPUT_HASHES["results/source_sta_family_consensus_groups.tsv"], "consensus manifest TSV binding mismatch")
    require(groups.get("rows") == 26184, "consensus manifest group count mismatch")


def write_outputs(validation: dict[str, Any]) -> None:
    require(not VALIDATION_JSON.exists() and not VALIDATION_REPORT.exists(), "validation output already exists")
    report = (
        "# ETR001 independent capacity validation\n\n"
        "Status: **PASS_INDEPENDENT_NONIMPORTING_VALIDATION**.\n\n"
        "Independently reconstructed 18,063 geometry rows and 2,163 records. "
        "All seven frozen capacity gates fail, reproducing "
        "**STOP_SCORE_BLIND_CAPACITY / STOP_ETR001_UNOPENED**.\n\n"
        "The geometry mask was applied before either source table was retained. "
        "Replacing every target family surface in both in-memory source reads and "
        "then scrubbing it left the complete reconstructed result byte-identical. "
        "The producer was neither imported nor executed. No target identity or "
        "target equality was used.\n"
    ).encode("utf-8")
    json_bytes = canonical_json_bytes(validation)
    temp_json = VALIDATION_JSON.with_name(VALIDATION_JSON.name + f".tmp.{os.getpid()}")
    temp_report = VALIDATION_REPORT.with_name(VALIDATION_REPORT.name + f".tmp.{os.getpid()}")
    try:
        temp_json.write_bytes(json_bytes)
        temp_report.write_bytes(report)
        os.link(temp_json, VALIDATION_JSON)
        os.link(temp_report, VALIDATION_REPORT)
    finally:
        temp_json.unlink(missing_ok=True)
        temp_report.unlink(missing_ok=True)


def main() -> None:
    validate_manifests()
    geometry_rows, target_ids, _ = load_geometry()

    baseline_counts, baseline_panel, baseline_mutations = derive_capacity(
        geometry_rows, target_ids, mutation_tag=None
    )
    require(baseline_mutations == {
        "atlas_target_surfaces_replaced_then_scrubbed": 0,
        "consensus_target_surfaces_replaced_then_scrubbed": 0,
    }, "baseline mutation accounting mismatch")
    reconstructed = build_result(baseline_counts, baseline_panel)

    mutated_counts, mutated_panel, mutation_counts = derive_capacity(
        geometry_rows, target_ids, mutation_tag="ARBITRARY_TARGET_REPLACEMENT|"
    )
    mutated = build_result(mutated_counts, mutated_panel)
    require(mutation_counts == {
        "atlas_target_surfaces_replaced_then_scrubbed": len(target_ids),
        "consensus_target_surfaces_replaced_then_scrubbed": len(target_ids),
    }, "target-surface mutation control did not cover every target")
    require(canonical_json_bytes(mutated) == canonical_json_bytes(reconstructed), "target-surface mutation changed a derived result")

    require(baseline_counts == {
        "capacity_orbit_log2": 0.0,
        "different_order_cross_folio_pairs": 0,
        "identical_order_cross_folio_pairs": 0,
        "informative_strata": 0,
        "masked_target_bearing_records": 2121,
        "masked_target_comparisons": 0,
        "maximum_folio_endpoint_exposure": 1.0,
        "physical_folios": 0,
        "source_geometry_rows": 18063,
        "source_records": 2163,
    }, "independent capacity counts differ from frozen result")
    require(baseline_panel == [], "zero-capacity result unexpectedly has informative strata")
    require(sum(reconstructed["gates"].values()) == 0, "frozen seven-gate STOP not reproduced")
    require(reconstructed["status"] == "STOP_SCORE_BLIND_CAPACITY", "unexpected reconstructed status")
    require(reconstructed["decision"] == "STOP_ETR001_UNOPENED", "unexpected reconstructed decision")

    published, published_bytes = load_canonical_json(PRODUCER_RESULT)
    require(canonical_json_bytes(reconstructed) == published_bytes, "canonical producer JSON does not match independent reconstruction")
    require(published == reconstructed, "producer result object does not match independent reconstruction")
    expected_report = build_producer_report(reconstructed)
    require(PRODUCER_REPORT.read_bytes() == expected_report, "producer report does not match independent reconstruction")

    validator_sha = sha256_file(Path(__file__).resolve())
    validation = {
        "checks": {
            "canonical_producer_json_exact": True,
            "canonical_producer_report_exact": True,
            "exact_18063_rows_2163_records": True,
            "exact_2121_target_bearing_records": True,
            "exact_pair_stratum_orbit_exposure_reconstruction": True,
            "exact_seven_gates": True,
            "six_frozen_input_hashes": True,
            "target_surface_mutation_byte_invariant": True,
        },
        "decision": reconstructed["decision"],
        "experiment": "ETR001_EXACT_TEMPLATE_RECURRENCE_CAPACITY_VALIDATION",
        "hashes": {
            "producer_report_sha256": EXPECTED_REPORT_SHA,
            "producer_result_sha256": EXPECTED_RESULT_SHA,
            "spec_sha256": EXPECTED_SPEC_SHA,
            "validator_sha256": validator_sha,
        },
        "isolation": {
            "producer_imported_or_executed": False,
            "target_family_equality_scored": False,
            "target_family_identity_used_in_key_equality_count_or_digest": False,
            "target_surface_fields_retained_after_source_row_mask": False,
        },
        "mutation_control": {
            **mutation_counts,
            "derived_result_unchanged": True,
        },
        "reconstructed": {
            "capacity_panel_sha256": reconstructed["capacity_panel_sha256"],
            "counts": reconstructed["counts"],
            "gates": reconstructed["gates"],
            "informative_summary_sha256": reconstructed["informative_summary_sha256"],
            "producer_status": reconstructed["status"],
        },
        "status": "PASS_INDEPENDENT_NONIMPORTING_VALIDATION",
    }
    write_outputs(validation)
    print(json.dumps({
        "status": validation["status"],
        "validator_sha256": validator_sha,
        "validation_json_sha256": sha256_file(VALIDATION_JSON),
        "validation_report_sha256": sha256_file(VALIDATION_REPORT),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
