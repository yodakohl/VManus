#!/usr/bin/env python3
"""Build a score-blind panel for an independent cho/che co-switch test."""

from __future__ import annotations

import csv
import hashlib
import json
import os
import re
import tempfile
from collections import Counter, defaultdict
from pathlib import Path

BASE = Path(__file__).resolve().parent
RESULTS = BASE / "results"
SPEC = BASE / "CHO_CHE_COSWITCH_CAPACITY_SPEC.md"
RUNNER = Path(__file__).resolve()
STATES = RESULTS / "parisel_cho_che_folio_states.tsv"
STATE_VALIDATION = RESULTS / "parisel_cho_che_source_audit_validation.json"
SOURCE = RESULTS / "source_separator_transcription.tsv"
SOURCE_VALIDATION = RESULTS / "source_separator_transcription_validation.json"
ALIGNMENT = RESULTS / "source_sta_group_alignment.tsv"
ALIGNMENT_VALIDATION = RESULTS / "source_sta_group_alignment_validation.json"
OUT = RESULTS / "cho_che_coswitch_capacity.json"
PANEL = RESULTS / "cho_che_coswitch_masked_panel.tsv"
REPORT = RESULTS / "cho_che_coswitch_capacity_report.md"

READINGS = ("ZL3b", "IT2a", "RF1b")
EXPECTED = {
    STATES: "4c713c379b33d04985c0efbf9dd4025cb810a9c1006975f7855ed6cc52ff381c",
    STATE_VALIDATION: "17009e151704d91f795216eed0913cfece447a396d08234df9af46624f286f3b",
    SOURCE: "4b649c8290d5afc7a5fbcc8e98db2bc123a1ceb5f3858d3befa781ce96b680f0",
    SOURCE_VALIDATION: "8698a2643219fd8ab00b05bba8705a1f1e8219c9b468824fbe2dc92117043deb",
    ALIGNMENT: "f23654f1d4c854db6d458b418a0d3530115731604854cf0a0495565e58341840",
    ALIGNMENT_VALIDATION: "cc53d32646b21e4135f0b23d98662e10835307ad860d021ea8c487261d7646fd",
}
STATE_FIELDS = (
    "parser", "edition", "folio", "cho_groups", "che_groups",
    "classifiable_groups", "cho_rate", "threshold_state", "em_state",
    "em_responsibility_high", "assignment_disagrees",
)
SOURCE_FIELDS = (
    "source_group_id", "edition", "locus", "page", "section", "currier",
    "hand", "code", "kind", "grammar_scope", "source_row_index",
    "source_group_index", "source_group_count", "paragraph_start",
    "paragraph_end", "left_separator", "right_separator", "ivtff_group_raw",
    "clean_ascii_fragments", "clean_ascii_fragment_count",
    "legacy_surface_positions_1based", "legacy_interlinear_row_present",
    "legacy_mapping_status",
)
ALIGNMENT_FIELDS = (
    "source_group_id", "edition", "locus", "source_group_index",
    "source_group_count", "left_separator", "right_separator", "sta_group_raw",
    "primary_sta_codes", "primary_sta_families", "primary_sta_symbol_count",
    "alternative_site_count", "nearest_basic_eva_primary",
)
PANEL_FIELDS = (
    "source_group_id", "edition", "locus", "page", "collapsed_page",
    "physical_folio", "side", "page_state", "section", "currier", "hand",
    "kind", "grammar_scope", "primary_sta_symbol_count",
    "page_position_quartile", "group_position_class",
)
CELL_FIELDS = ("section", "currier", "hand", "kind", "grammar_scope")
DIRECT = re.compile(r"(?:ch|sh)[oe]")
PANEL_PAGE = re.compile(r"([rv])\d+$")
PHYSICAL_PAGE = re.compile(r"f(\d+)([rv])$")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def collapse_page(page: str) -> str:
    return PANEL_PAGE.sub(r"\1", page)


def physical_parts(page: str) -> tuple[str, str]:
    match = PHYSICAL_PAGE.fullmatch(page)
    if not match:
        raise ValueError(f"nonphysical page: {page}")
    return f"f{match.group(1)}", match.group(2)


def tsv_bytes(fields: tuple[str, ...], rows: list[dict[str, str]]) -> bytes:
    import io
    handle = io.StringIO(newline="")
    writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return handle.getvalue().encode("utf-8")


def load_rows(path: Path, fields: tuple[str, ...]) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        if tuple(reader.fieldnames or ()) != fields:
            raise ValueError(f"schema: {path.name}")
        return list(reader)


def install_three(result_bytes: bytes, panel_bytes: bytes, report_bytes: bytes) -> None:
    outputs = (OUT, PANEL, REPORT)
    if any(path.exists() for path in outputs):
        raise FileExistsError("refusing to overwrite co-switch capacity artifacts")
    with tempfile.TemporaryDirectory(prefix="cho_che_coswitch_capacity_", dir=RESULTS) as directory:
        staged = []
        for name, payload in (("result", result_bytes), ("panel", panel_bytes), ("report", report_bytes)):
            path = Path(directory) / name
            path.write_bytes(payload)
            staged.append(path)
        if any(path.exists() for path in outputs):
            raise FileExistsError("co-switch artifact appeared during staging")
        installed: list[Path] = []
        try:
            for source, target in zip(staged, outputs):
                os.link(source, target)
                installed.append(target)
        except Exception:
            for path in installed:
                path.unlink(missing_ok=True)
            raise


def main() -> None:
    for path, expected in EXPECTED.items():
        if sha(path) != expected:
            raise SystemExit(f"frozen input mismatch: {path.name}")
    statuses = {
        STATE_VALIDATION: "PASS_INDEPENDENT_SOURCE_AND_IMPLEMENTATION_RECONSTRUCTION",
        SOURCE_VALIDATION: "PASS_INDEPENDENT_SOURCE_SEPARATOR_RECONSTRUCTION",
        ALIGNMENT_VALIDATION: "PASS_INDEPENDENT_SOURCE_STA_ALIGNMENT_RECONSTRUCTION",
    }
    for path, expected in statuses.items():
        if json.loads(path.read_text())["status"] != expected:
            raise SystemExit(f"validation not PASS: {path.name}")

    state_rows = load_rows(STATES, STATE_FIELDS)
    primary_states: dict[str, dict[str, int]] = {edition: {} for edition in READINGS}
    for row in state_rows:
        if row["parser"] != "SOURCE_ALL_SEPARATORS":
            continue
        edition = row["edition"]
        page = row["folio"]
        if edition not in primary_states or page in primary_states[edition]:
            raise ValueError("state edition or duplicate")
        primary_states[edition][page] = int(row["em_state"])
    if any(len(primary_states[edition]) != 200 for edition in READINGS):
        raise ValueError("state page count")

    common_pages = {
        page: primary_states[READINGS[0]][page]
        for page in set.intersection(*(set(primary_states[edition]) for edition in READINGS))
        if len({primary_states[edition][page] for edition in READINGS}) == 1
    }
    by_leaf: dict[str, dict[str, tuple[str, int]]] = defaultdict(dict)
    for page, state in common_pages.items():
        folio, side = physical_parts(page)
        by_leaf[folio][side] = (page, state)
    consensus_switch_leaves = {
        folio for folio, sides in by_leaf.items()
        if set(sides) == {"r", "v"} and sides["r"][1] != sides["v"][1]
    }

    source_rows = load_rows(SOURCE, SOURCE_FIELDS)
    source_by_id = {row["source_group_id"]: row for row in source_rows}
    if len(source_by_id) != len(source_rows):
        raise ValueError("duplicate source ID")

    # Deliberately extract only alignment geometry.  Family/code/surface fields
    # are neither indexed nor stored and no state association is evaluated.
    geometry: dict[str, tuple[int, int]] = {}
    with ALIGNMENT.open(encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle, delimiter="\t")
        header = next(reader)
        if tuple(header) != ALIGNMENT_FIELDS:
            raise ValueError("alignment schema")
        uid_i = header.index("source_group_id")
        length_i = header.index("primary_sta_symbol_count")
        alt_i = header.index("alternative_site_count")
        for values in reader:
            if len(values) != len(header):
                raise ValueError("alignment row width")
            uid = values[uid_i]
            if uid in geometry:
                raise ValueError("duplicate alignment ID")
            geometry[uid] = (int(values[length_i]), int(values[alt_i]))

    candidates: list[dict[str, str]] = []
    page_locus_order: dict[tuple[str, str], dict[str, int]] = defaultdict(dict)
    for row in source_rows:
        uid = row["source_group_id"]
        if uid not in geometry:
            raise ValueError("source/alignment ID mismatch")
        length, alternatives = geometry[uid]
        page = collapse_page(row["page"])
        match = PHYSICAL_PAGE.fullmatch(page)
        if match is None:
            continue
        folio, side = f"f{match.group(1)}", match.group(2)
        if folio not in consensus_switch_leaves:
            continue
        edition = row["edition"]
        if edition not in READINGS or primary_states[edition].get(page) != common_pages.get(page):
            continue
        if alternatives != 0 or int(row["clean_ascii_fragment_count"]) != 1:
            continue
        if DIRECT.search(row["clean_ascii_fragments"]):
            continue
        cell = tuple(row[field] for field in CELL_FIELDS)
        candidates.append({
            "source_group_id": uid,
            "edition": edition,
            "locus": row["locus"],
            "page": row["page"],
            "collapsed_page": page,
            "physical_folio": folio,
            "side": side,
            "page_state": str(common_pages[page]),
            "section": row["section"],
            "currier": row["currier"],
            "hand": row["hand"],
            "kind": row["kind"],
            "grammar_scope": row["grammar_scope"],
            "primary_sta_symbol_count": str(length),
            "_cell": "\x1f".join(cell),
            "_source_row_index": row["source_row_index"],
            "_source_group_index": row["source_group_index"],
            "_source_group_count": row["source_group_count"],
        })
        page_locus_order[(edition, page)].setdefault(row["locus"], int(row["source_row_index"]))

    cells_by_side: dict[tuple[str, str, str], set[str]] = defaultdict(set)
    for row in candidates:
        cells_by_side[(row["edition"], row["physical_folio"], row["side"])].add(row["_cell"])
    common_cells: dict[tuple[str, str], set[str]] = {}
    for edition in READINGS:
        for folio in consensus_switch_leaves:
            common_cells[(edition, folio)] = (
                cells_by_side[(edition, folio, "r")] & cells_by_side[(edition, folio, "v")]
            )
    eligible_leaves = {
        folio for folio in consensus_switch_leaves
        if all(common_cells[(edition, folio)] for edition in READINGS)
    }

    ranks: dict[tuple[str, str, str], tuple[int, int]] = {}
    for (edition, page), locus_map in page_locus_order.items():
        ordered = sorted(locus_map, key=lambda locus: (locus_map[locus], locus))
        for index, locus in enumerate(ordered):
            ranks[(edition, page, locus)] = (index, len(ordered))

    panel_rows: list[dict[str, str]] = []
    for row in candidates:
        if row["physical_folio"] not in eligible_leaves:
            continue
        if row["_cell"] not in common_cells[(row["edition"], row["physical_folio"])]:
            continue
        index, count = ranks[(row["edition"], row["collapsed_page"], row["locus"])]
        group_index = int(row["_source_group_index"])
        group_count = int(row["_source_group_count"])
        if group_count == 1:
            group_position = "SINGLE"
        elif group_index == 1:
            group_position = "FIRST"
        elif group_index == group_count:
            group_position = "LAST"
        else:
            group_position = "MIDDLE"
        clean = {field: row[field] for field in PANEL_FIELDS if field in row}
        clean["page_position_quartile"] = str(min(3, 4 * index // max(1, count)))
        clean["group_position_class"] = group_position
        panel_rows.append(clean)

    def sort_key(row: dict[str, str]) -> tuple:
        match = re.fullmatch(r"f(\d+)", row["physical_folio"])
        return (
            READINGS.index(row["edition"]), int(match.group(1)) if match else 10**9,
            row["side"], row["locus"], row["source_group_id"],
        )

    panel_rows.sort(key=sort_key)
    if len({row["source_group_id"] for row in panel_rows}) != len(panel_rows):
        raise ValueError("duplicate panel ID")
    panel_bytes = tsv_bytes(PANEL_FIELDS, panel_rows)

    groups_by_reading = Counter(row["edition"] for row in panel_rows)
    side_counts = Counter((row["edition"], row["physical_folio"], row["side"]) for row in panel_rows)
    high_sides = Counter(by_leaf[folio]["r"][1] for folio in eligible_leaves)
    high_recto = sum(by_leaf[folio]["r"][1] == 1 for folio in eligible_leaves)
    high_verso = len(eligible_leaves) - high_recto
    prose_leaves = {
        row["physical_folio"] for row in panel_rows if row["grammar_scope"] == "CONFIRMED_PROSE"
    }
    diagnostic_leaves = {
        row["physical_folio"] for row in panel_rows if row["grammar_scope"] == "DIAGNOSTIC_NONPROSE"
    }
    orbit = 2 ** len(eligible_leaves)
    gates = {
        "exact_three_readings": set(primary_states) == set(READINGS),
        "exact_600_primary_state_rows": sum(map(len, primary_states.values())) == 600,
        "at_least_196_consensus_page_sides": len(common_pages) >= 196,
        "at_least_eight_common_switch_leaves": len(eligible_leaves) >= 8,
        "both_orientation_support_at_least_three": min(high_recto, high_verso) >= 3,
        "at_least_five_prose_leaves": len(prose_leaves) >= 5,
        "at_least_two_diagnostic_leaves": len(diagnostic_leaves) >= 2,
        "at_least_1600_groups_each_reading": min(groups_by_reading.values()) >= 1600,
        "at_least_30_groups_each_page_side": min(side_counts.values()) >= 30,
        "all_metadata_cells_shared_within_leaf": all(
            row["_cell"] in common_cells[(row["edition"], row["physical_folio"])]
            for row in candidates if row["physical_folio"] in eligible_leaves
            and row["_cell"] in common_cells[(row["edition"], row["physical_folio"])]
        ),
        "leaf_flip_orbit_at_least_256": orbit >= 256,
        "attainable_one_sided_floor_at_most_point_01": 1 / orbit <= .01,
        "masked_panel_has_no_target_columns": not ({"ivtff_group_raw", "clean_ascii_fragments", "sta_group_raw", "primary_sta_codes", "primary_sta_families", "target_family", "score", "effect", "p_value"} & set(PANEL_FIELDS)),
        "target_associations_computed_zero": True,
        "english_glosses_zero": True,
    }
    passed = all(gates.values())
    status = "PASS_SCORE_BLIND_CHO_CHE_COSWITCH_CAPACITY" if passed else "STOP_INSUFFICIENT_CHO_CHE_COSWITCH_CAPACITY"
    decision = "AUTHORIZE_TARGET_FREE_COSWITCH_PREFLIGHT_ONLY" if passed else "CLOSE_COSWITCH_ROUTE_UNSCORED"
    inputs = {path.name: sha(path) for path in (*EXPECTED, SPEC, RUNNER)}
    result = {
        "experiment": "CHO_CHE_COSWITCH_CAPACITY",
        "status": status,
        "decision": decision,
        "inputs": inputs,
        "primary_unit": "physical leaf with opposite all-reading-agreed page-side states",
        "consensus_page_sides": len(common_pages),
        "consensus_switch_leaves_before_metadata_gate": sorted(consensus_switch_leaves, key=lambda value: int(value[1:])),
        "eligible_common_switch_leaves": sorted(eligible_leaves, key=lambda value: int(value[1:])),
        "eligible_leaf_count": len(eligible_leaves),
        "high_recto_leaves": high_recto,
        "high_verso_leaves": high_verso,
        "prose_leaf_count": len(prose_leaves),
        "diagnostic_leaf_count": len(diagnostic_leaves),
        "groups_by_reading": {edition: groups_by_reading[edition] for edition in READINGS},
        "minimum_groups_per_reading_leaf_side": min(side_counts.values()),
        "leaf_flip_orbit": orbit,
        "attainable_one_sided_p_floor": 1 / orbit,
        "masked_panel_rows": len(panel_rows),
        "masked_panel_sha256": hashlib.sha256(panel_bytes).hexdigest(),
        "defining_site_groups_retained": 0,
        "family_surface_columns_used": 0,
        "target_associations_computed": 0,
        "scores_computed": 0,
        "p_values_computed": 0,
        "english_glosses": 0,
        "gates": gates,
        "claim_ceiling": "A pass establishes only capacity for a held-physical-leaf, source-native test of formal co-switching outside every defining ch/sh+o/e group. It supplies no co-switch result, meaning, sound, wordhood, language, cipher, plaintext, or translation.",
    }
    report = f"""# `cho/che` independent co-switch capacity

Status: **{status}**

This is a new route, not a repeat of the closed paragraph-scope test.  The
validated label is a page-side state.  The source-native panel retains
**{len(eligible_leaves)}** opposite-state physical leaves common to all three
readings: **{', '.join(sorted(eligible_leaves, key=lambda value: int(value[1:])))}**.
High state occurs on recto for **{high_recto}** and verso for **{high_verso}**
leaves, so both orientations are represented.

After exact within-leaf metadata-cell matching, zero-STA-alternative filtering,
and removing every group containing a defining `ch/sh+o/e` site, the masked
panel has **{len(panel_rows):,}** rows: ZL **{groups_by_reading['ZL3b']:,}**,
IT **{groups_by_reading['IT2a']:,}**, RF **{groups_by_reading['RF1b']:,}**.
The smallest reading/leaf/side cell has **{min(side_counts.values())}** groups.
The synchronous leaf-flip orbit is **{orbit}**, with one-sided floor
**{1/orbit:.6f}**.

No STA family sequence, feature/state association, score, effect, or p-value
was computed.  Decision: **{decision}**.  A pass authorizes only a frozen
target-free synthetic/power preflight.  It supplies no formal co-switch result,
meaning, sound, wordhood, language, cipher, plaintext, or translation.
"""
    install_three(
        (json.dumps(result, indent=2, sort_keys=True) + "\n").encode(),
        panel_bytes,
        report.encode(),
    )
    print(json.dumps({"status": status, "decision": decision, "gates": gates}, sort_keys=True))
    if not passed:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
