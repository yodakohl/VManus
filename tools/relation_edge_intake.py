"""Validate provenance-clean relation-edge acquisition packets.

This is infrastructure, not a semantic scorer.  It operationalizes the frozen
GDT388 acquisition gates and rejects f84 selectors before parsing row payloads.
The optional null-candidate packet makes target mobility independently
checkable instead of trusting an ``eligibility_status`` assertion.
"""

from __future__ import annotations

import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

from tools.vmanus_experiment import SealedDataError, _raw_tsv_field


EDGE_COLUMNS = (
    "edge_id",
    "batch_id",
    "page",
    "physical_folio",
    "diagram_unit_id",
    "pivot_visual_id",
    "pivot_locus",
    "target_visual_id",
    "target_locus",
    "relation_type",
    "direction_basis",
    "ownership_basis",
    "geometry_only_selection",
    "source_manifest_id",
    "page_crop_sha256",
    "pivot_crop_sha256",
    "target_crop_sha256",
    "source_aware_localizer",
    "relation_reviewer",
    "relation_confidence",
    "ambiguity_state",
    "formal_access_state",
    "fold_assignment",
    "eligibility_status",
)

NULL_COLUMNS = (
    "edge_id",
    "candidate_target_locus",
    "is_observed_target",
    "matched_topology",
    "eligible_under_null",
)

ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:-]*$")
STATE_RE = re.compile(r"^[A-Z][A-Z0-9_]*$")
LOCUS_RE = re.compile(r"^(f(?:\d+|Ros)[rv]?\d*)\.[A-Za-z0-9@+*=-]+$")
SHA_RE = re.compile(r"^[0-9a-f]{64}$")

SCORE_DIRECTIONS = {
    "AUTHORIAL_POINTER",
    "EXTERNALLY_FIXED_ORDER",
    "SOURCE_AUTHORED_OWNERSHIP_RULE",
}
SCORE_OWNERSHIP = {"SINGULAR_EXACT"}


def _read_guarded_rows(
    path: Path,
    required_columns: tuple[str, ...],
    selector_columns: tuple[str, ...],
) -> list[dict[str, str]]:
    """Read rows only after every raw selector has passed the f84 guard."""

    rows: list[dict[str, str]] = []
    with path.open(encoding="utf-8", newline="") as handle:
        header_line = handle.readline()
        if not header_line:
            raise ValueError(f"empty TSV: {path}")
        header = next(csv.reader([header_line], delimiter="\t"))
        if tuple(header) != required_columns:
            raise ValueError(
                f"unexpected TSV schema in {path}; expected exactly "
                + ",".join(required_columns)
            )
        selector_indices = [header.index(column) for column in selector_columns]
        for line_number, raw_line in enumerate(handle, start=2):
            for index in selector_indices:
                raw_value = _raw_tsv_field(raw_line, index)
                if raw_value is None:
                    raise ValueError(f"short TSV row {path}:{line_number}")
                values = next(csv.reader([raw_value], delimiter="\t"))
                if len(values) != 1:
                    raise ValueError(f"invalid selector field {path}:{line_number}")
                if values[0].startswith("f84"):
                    raise SealedDataError(
                        f"forbidden f84 selector rejected before row parse: {path}:{line_number}"
                    )
            values = next(csv.reader([raw_line], delimiter="\t"))
            if len(values) != len(header):
                raise ValueError(f"TSV width mismatch {path}:{line_number}")
            rows.append(dict(zip(header, values)))
    return rows


def _locus_page(locus: str) -> str | None:
    match = LOCUS_RE.fullmatch(locus)
    return match.group(1) if match else None


def _physical_folio(page: str) -> str:
    if page.startswith("fRos"):
        return "fRos"
    match = re.match(r"^(f\d+)", page)
    return match.group(1) if match else ""


def _validate_edge_rows(rows: list[dict[str, str]]) -> tuple[list[str], list[dict[str, str]]]:
    errors: list[str] = []
    eligible: list[dict[str, str]] = []
    seen_ids: set[str] = set()
    seen_pairs: set[tuple[str, str]] = set()
    for number, row in enumerate(rows, start=2):
        label = f"edge row {number}"
        edge_id = row["edge_id"]
        if not ID_RE.fullmatch(edge_id):
            errors.append(f"{label}: invalid edge_id")
        elif edge_id in seen_ids:
            errors.append(f"{label}: duplicate edge_id {edge_id}")
        seen_ids.add(edge_id)

        for column in (
            "batch_id",
            "diagram_unit_id",
            "pivot_visual_id",
            "target_visual_id",
            "source_manifest_id",
            "source_aware_localizer",
            "relation_reviewer",
        ):
            if not ID_RE.fullmatch(row[column]):
                errors.append(f"{label}: invalid {column}")
        for column in (
            "relation_type",
            "direction_basis",
            "ownership_basis",
            "geometry_only_selection",
            "relation_confidence",
            "ambiguity_state",
            "formal_access_state",
            "fold_assignment",
            "eligibility_status",
        ):
            if not STATE_RE.fullmatch(row[column]):
                errors.append(f"{label}: invalid {column}")

        pivot_page = _locus_page(row["pivot_locus"])
        target_page = _locus_page(row["target_locus"])
        if pivot_page is None:
            errors.append(f"{label}: invalid pivot_locus")
        if target_page is None:
            errors.append(f"{label}: invalid target_locus")
        if pivot_page and pivot_page != row["page"]:
            errors.append(f"{label}: pivot_locus is not on page")
        if target_page and target_page != row["page"]:
            errors.append(f"{label}: target_locus is not on page")
        if _physical_folio(row["page"]) != row["physical_folio"]:
            errors.append(f"{label}: physical_folio does not match page")
        if row["pivot_locus"] == row["target_locus"]:
            errors.append(f"{label}: pivot and target loci must differ")
        pair = (row["pivot_locus"], row["target_locus"])
        if pair in seen_pairs:
            errors.append(f"{label}: duplicate ordered locus pair")
        seen_pairs.add(pair)

        if row["formal_access_state"] not in {"SEALED", "SEALED_NOT_ACCESSED"}:
            errors.append(f"{label}: formal access is not sealed")
        if row["eligibility_status"] == "ELIGIBLE":
            eligible.append(row)
            if row["direction_basis"] not in SCORE_DIRECTIONS:
                errors.append(f"{label}: eligible edge lacks admissible direction")
            if row["ownership_basis"] not in SCORE_OWNERSHIP:
                errors.append(f"{label}: eligible edge lacks singular ownership")
            if row["geometry_only_selection"] != "TRUE":
                errors.append(f"{label}: eligible edge was not geometry-only selected")
            if row["ambiguity_state"] != "RESOLVED":
                errors.append(f"{label}: eligible edge remains ambiguous")
            if row["fold_assignment"] not in {"DISCOVERY", "HOLDOUT"}:
                errors.append(f"{label}: eligible edge lacks frozen fold")
            if row["source_aware_localizer"] == row["relation_reviewer"]:
                errors.append(f"{label}: eligible localizer and reviewer are not independent")
            for column in ("page_crop_sha256", "pivot_crop_sha256", "target_crop_sha256"):
                if not SHA_RE.fullmatch(row[column]):
                    errors.append(f"{label}: eligible edge lacks valid {column}")
    return errors, eligible


def _validate_null_rows(
    rows: list[dict[str, str]],
    eligible: list[dict[str, str]],
) -> tuple[list[str], set[str]]:
    errors: list[str] = []
    by_edge: dict[str, list[dict[str, str]]] = defaultdict(list)
    eligible_by_id = {row["edge_id"]: row for row in eligible}
    for number, row in enumerate(rows, start=2):
        label = f"null row {number}"
        if row["edge_id"] not in eligible_by_id:
            errors.append(f"{label}: edge_id is not an eligible packet edge")
            continue
        if _locus_page(row["candidate_target_locus"]) is None:
            errors.append(f"{label}: invalid candidate_target_locus")
        elif _locus_page(row["candidate_target_locus"]) != eligible_by_id[row["edge_id"]]["page"]:
            errors.append(f"{label}: candidate target is not on edge page")
        for column in ("is_observed_target", "matched_topology", "eligible_under_null"):
            if row[column] not in {"TRUE", "FALSE"}:
                errors.append(f"{label}: {column} must be TRUE or FALSE")
        by_edge[row["edge_id"]].append(row)

    mobile: set[str] = set()
    for edge_id, edge in eligible_by_id.items():
        candidates = by_edge.get(edge_id, [])
        observed = [row for row in candidates if row["is_observed_target"] == "TRUE"]
        if len(observed) != 1 or observed[0]["candidate_target_locus"] != edge["target_locus"]:
            errors.append(f"null candidates {edge_id}: require one matching observed target")
        alternatives = {
            row["candidate_target_locus"]
            for row in candidates
            if row["is_observed_target"] == "FALSE"
            and row["matched_topology"] == "TRUE"
            and row["eligible_under_null"] == "TRUE"
            and row["candidate_target_locus"] != edge["target_locus"]
            and row["candidate_target_locus"] != edge["pivot_locus"]
        }
        if alternatives:
            mobile.add(edge_id)
        else:
            errors.append(f"null candidates {edge_id}: no mobile matched alternative")
    return errors, mobile


def validate_relation_edge_packet(
    packet_path: Path,
    null_candidates_path: Path | None = None,
) -> dict[str, object]:
    rows = _read_guarded_rows(
        packet_path,
        EDGE_COLUMNS,
        ("page", "physical_folio", "pivot_locus", "target_locus"),
    )
    errors, eligible = _validate_edge_rows(rows)
    mobile: set[str] = set()
    if null_candidates_path is not None:
        null_rows = _read_guarded_rows(
            null_candidates_path,
            NULL_COLUMNS,
            ("candidate_target_locus",),
        )
        null_errors, mobile = _validate_null_rows(null_rows, eligible)
        errors.extend(null_errors)

    folios = {row["physical_folio"] for row in eligible}
    folds = Counter(row["fold_assignment"] for row in eligible)
    capacity_pass = len(eligible) >= 50 and len(folios) >= 5
    null_pass = null_candidates_path is not None and len(mobile) == len(eligible)
    holdout_pass = bool(folds["DISCOVERY"] and folds["HOLDOUT"])
    score_ready = not errors and capacity_pass and null_pass and holdout_pass
    if errors:
        status = "INVALID_PACKET"
    elif score_ready:
        status = "SCORE_READY"
    else:
        status = "VALID_ACQUISITION_NOT_SCORE_READY"
    return {
        "status": status,
        "packet_rows": len(rows),
        "eligible_edges": len(eligible),
        "eligible_folios": len(folios),
        "discovery_edges": folds["DISCOVERY"],
        "holdout_edges": folds["HOLDOUT"],
        "mobile_edges": len(mobile),
        "capacity_gate_50_edges_5_folios": capacity_pass,
        "holdout_gate": holdout_pass,
        "mobile_null_gate": null_pass,
        "score_ready": score_ready,
        "errors": errors,
    }


def render_report(report: dict[str, object]) -> str:
    return json.dumps(report, sort_keys=True, indent=2) + "\n"
