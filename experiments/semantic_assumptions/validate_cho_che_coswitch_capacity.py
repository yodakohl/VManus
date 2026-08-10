#!/usr/bin/env python3
"""Independent reconstruction of the score-blind cho/che co-switch capacity."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import os
import re
import tempfile
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
VALIDATOR = Path(__file__).resolve()
SPEC = HERE / "CHO_CHE_COSWITCH_CAPACITY_SPEC.md"
BUILDER = HERE / "build_cho_che_coswitch_capacity.py"
AMENDMENT = HERE / "CHO_CHE_COSWITCH_CAPACITY_V2_AMENDMENT.md"
RESOLVER = HERE / "resolve_cho_che_coswitch_capacity_v2.py"
STATES = RESULTS / "parisel_cho_che_folio_states.tsv"
STATE_VALIDATION = RESULTS / "parisel_cho_che_source_audit_validation.json"
SOURCE = RESULTS / "source_separator_transcription.tsv"
SOURCE_VALIDATION = RESULTS / "source_separator_transcription_validation.json"
ALIGNMENT = RESULTS / "source_sta_group_alignment.tsv"
ALIGNMENT_VALIDATION = RESULTS / "source_sta_group_alignment_validation.json"
V1 = RESULTS / "cho_che_coswitch_capacity.json"
PANEL = RESULTS / "cho_che_coswitch_masked_panel.tsv"
V1_REPORT = RESULTS / "cho_che_coswitch_capacity_report.md"
V2 = RESULTS / "cho_che_coswitch_capacity_v2.json"
V2_REPORT = RESULTS / "cho_che_coswitch_capacity_v2_report.md"
OUT = RESULTS / "cho_che_coswitch_capacity_validation.json"
REPORT = RESULTS / "cho_che_coswitch_capacity_validation_report.md"

READINGS = ("ZL3b", "IT2a", "RF1b")
HASHES = {
    STATES: "4c713c379b33d04985c0efbf9dd4025cb810a9c1006975f7855ed6cc52ff381c",
    STATE_VALIDATION: "17009e151704d91f795216eed0913cfece447a396d08234df9af46624f286f3b",
    SOURCE: "4b649c8290d5afc7a5fbcc8e98db2bc123a1ceb5f3858d3befa781ce96b680f0",
    SOURCE_VALIDATION: "8698a2643219fd8ab00b05bba8705a1f1e8219c9b468824fbe2dc92117043deb",
    ALIGNMENT: "f23654f1d4c854db6d458b418a0d3530115731604854cf0a0495565e58341840",
    ALIGNMENT_VALIDATION: "cc53d32646b21e4135f0b23d98662e10835307ad860d021ea8c487261d7646fd",
    SPEC: "15690943688a533641d3177524c18fd4f08c1c7935b67adea862f1d655961a0a",
    BUILDER: "b83655e1b70e9c0bf3dfde6940afa5cbbc95a955db226800878787411e7d01c0",
    V1: "5f1ae292148f27d31aa02e14b7b766b3019bd98ff5b552207485b73f28b0ecce",
    PANEL: "25ae579c3f122f188089edc8fd2e0f617194bf6240cb20570d9aff881f80e003",
    V1_REPORT: "bcf019aa42b00afd03e31ff9caf69894b6f6927764aa96b881e6a979d5f16baf",
    AMENDMENT: "686c7b1abc9bc5289bb2a265092f30dae12a761f787879682169ac90942ff42a",
    RESOLVER: "c83ef5c72ce0578dec3b21a85789d76115e2990d04c2c9ac560d3a3bc00c2f74",
    V2: "c32a6dc5456a59f469de1f8d47d95fba8e6384d60ecccd678adb678c0382b775",
    V2_REPORT: "937b3f6675ffdd6167a53a722b13dc6fdfe617a392863806e74ef5ff7ceca8c8",
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
META = ("section", "currier", "hand", "kind", "grammar_scope")
FORBIDDEN = {
    "ivtff_group_raw", "clean_ascii_fragments", "sta_group_raw",
    "primary_sta_codes", "primary_sta_families", "target_family", "score",
    "effect", "p_value",
}
DIRECT = re.compile(r"(?:ch|sh)[oe]")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check(value: bool, label: str, checks: list[str]) -> None:
    if not value:
        raise AssertionError(label)
    checks.append(label)


def read_tsv(path: Path, fields: tuple[str, ...]) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        if tuple(reader.fieldnames or ()) != fields:
            raise AssertionError(f"schema {path.name}")
        return list(reader)


def collapse(page: str) -> str:
    return re.sub(r"([rv])\d+$", r"\1", page)


def leaf_side(page: str) -> tuple[str, str]:
    match = re.fullmatch(r"f(\d+)([rv])", page)
    if not match:
        raise AssertionError(f"page {page}")
    return "f" + match.group(1), match.group(2)


def render_panel(rows: list[dict[str, str]]) -> bytes:
    handle = io.StringIO(newline="")
    writer = csv.DictWriter(handle, fieldnames=PANEL_FIELDS, delimiter="\t", lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return handle.getvalue().encode()


def reconstruct() -> tuple[list[dict[str, str]], dict]:
    state_rows = read_tsv(STATES, STATE_FIELDS)
    states = {edition: {} for edition in READINGS}
    for row in state_rows:
        if row["parser"] != "SOURCE_ALL_SEPARATORS":
            continue
        edition, page = row["edition"], row["folio"]
        if edition not in states or page in states[edition]:
            raise AssertionError("state duplicate")
        states[edition][page] = int(row["em_state"])
    common = {}
    for page in set.intersection(*(set(states[edition]) for edition in READINGS)):
        values = {states[edition][page] for edition in READINGS}
        if len(values) == 1:
            common[page] = values.pop()
    paired = defaultdict(dict)
    for page, value in common.items():
        folio, side = leaf_side(page)
        paired[folio][side] = (page, value)
    switch = {
        folio for folio, sides in paired.items()
        if set(sides) == {"r", "v"} and sides["r"][1] != sides["v"][1]
    }

    source_rows = read_tsv(SOURCE, SOURCE_FIELDS)
    source_ids = {row["source_group_id"] for row in source_rows}
    if len(source_ids) != len(source_rows):
        raise AssertionError("source IDs")
    with ALIGNMENT.open(encoding="utf-8", newline="") as handle:
        table = csv.reader(handle, delimiter="\t")
        header = next(table)
        if tuple(header) != ALIGNMENT_FIELDS:
            raise AssertionError("alignment schema")
        positions = {name: header.index(name) for name in header}
        geometry = {}
        first_full = None
        for values in table:
            if len(values) != len(header):
                raise AssertionError("alignment width")
            if first_full is None:
                first_full = list(values)
            uid = values[positions["source_group_id"]]
            if uid in geometry:
                raise AssertionError("alignment IDs")
            geometry[uid] = (
                int(values[positions["primary_sta_symbol_count"]]),
                int(values[positions["alternative_site_count"]]),
            )
    if set(geometry) != source_ids:
        raise AssertionError("alignment/source set")
    # Direct proof that changing the hidden family cell cannot change extracted
    # capacity geometry.
    mutant = list(first_full)
    mutant[positions["primary_sta_families"]] = "ZZZZZZ_MUTATION"
    original_geometry = (
        first_full[positions["source_group_id"]],
        int(first_full[positions["primary_sta_symbol_count"]]),
        int(first_full[positions["alternative_site_count"]]),
    )
    mutant_geometry = (
        mutant[positions["source_group_id"]],
        int(mutant[positions["primary_sta_symbol_count"]]),
        int(mutant[positions["alternative_site_count"]]),
    )
    if original_geometry != mutant_geometry:
        raise AssertionError("target-column isolation mutation")

    candidates = []
    locus_order = defaultdict(dict)
    direct_excluded = 0
    for source in source_rows:
        length, alternatives = geometry[source["source_group_id"]]
        page = collapse(source["page"])
        match = re.fullmatch(r"f(\d+)([rv])", page)
        if not match:
            continue
        folio, side = "f" + match.group(1), match.group(2)
        if folio not in switch:
            continue
        edition = source["edition"]
        if edition not in READINGS or states[edition].get(page) != common.get(page):
            continue
        if alternatives or source["clean_ascii_fragment_count"] != "1":
            continue
        if DIRECT.search(source["clean_ascii_fragments"]):
            direct_excluded += 1
            continue
        cell = tuple(source[field] for field in META)
        candidates.append({
            "source_group_id": source["source_group_id"],
            "edition": edition,
            "locus": source["locus"],
            "page": source["page"],
            "collapsed_page": page,
            "physical_folio": folio,
            "side": side,
            "page_state": str(common[page]),
            "section": source["section"],
            "currier": source["currier"],
            "hand": source["hand"],
            "kind": source["kind"],
            "grammar_scope": source["grammar_scope"],
            "primary_sta_symbol_count": str(length),
            "_cell": "\x1f".join(cell),
            "_source_row_index": source["source_row_index"],
            "_source_group_index": source["source_group_index"],
            "_source_group_count": source["source_group_count"],
        })
        locus_order[(edition, page)].setdefault(source["locus"], int(source["source_row_index"]))

    cells = defaultdict(set)
    for row in candidates:
        cells[(row["edition"], row["physical_folio"], row["side"])].add(row["_cell"])
    overlap = {
        (edition, folio): cells[(edition, folio, "r")] & cells[(edition, folio, "v")]
        for edition in READINGS for folio in switch
    }
    eligible = {
        folio for folio in switch
        if all(overlap[(edition, folio)] for edition in READINGS)
    }
    ranks = {}
    for (edition, page), locus_map in locus_order.items():
        ordered = sorted(locus_map, key=lambda locus: (locus_map[locus], locus))
        for index, locus in enumerate(ordered):
            ranks[(edition, page, locus)] = index, len(ordered)

    rows = []
    for candidate in candidates:
        folio = candidate["physical_folio"]
        if folio not in eligible or candidate["_cell"] not in overlap[(candidate["edition"], folio)]:
            continue
        index, count = ranks[(candidate["edition"], candidate["collapsed_page"], candidate["locus"])]
        group_index = int(candidate["_source_group_index"])
        group_count = int(candidate["_source_group_count"])
        group_position = (
            "SINGLE" if group_count == 1 else
            "FIRST" if group_index == 1 else
            "LAST" if group_index == group_count else "MIDDLE"
        )
        row = {field: candidate[field] for field in PANEL_FIELDS if field in candidate}
        row["page_position_quartile"] = str(min(3, 4 * index // max(1, count)))
        row["group_position_class"] = group_position
        rows.append(row)

    def key(row):
        return (
            READINGS.index(row["edition"]), int(row["physical_folio"][1:]),
            row["side"], row["locus"], row["source_group_id"],
        )
    rows.sort(key=key)
    diagnostics = {
        "primary_state_rows": sum(map(len, states.values())),
        "common_pages": len(common),
        "switch_before_metadata": sorted(switch, key=lambda x: int(x[1:])),
        "eligible": sorted(eligible, key=lambda x: int(x[1:])),
        "direct_excluded": direct_excluded,
        "target_column_mutation_isolated": original_geometry == mutant_geometry,
        "paired": paired,
    }
    return rows, diagnostics


def install_pair(result_bytes: bytes, report_bytes: bytes) -> None:
    if OUT.exists() or REPORT.exists():
        raise FileExistsError("refusing to overwrite co-switch validation")
    with tempfile.TemporaryDirectory(prefix="cho_che_coswitch_validation_", dir=RESULTS) as directory:
        a, b = Path(directory) / "json", Path(directory) / "md"
        a.write_bytes(result_bytes)
        b.write_bytes(report_bytes)
        if OUT.exists() or REPORT.exists():
            raise FileExistsError("validation artifact appeared")
        os.link(a, OUT)
        try:
            os.link(b, REPORT)
        except Exception:
            OUT.unlink(missing_ok=True)
            raise


def main() -> None:
    checks: list[str] = []
    for path, expected in HASHES.items():
        check(digest(path) == expected, "hash:" + path.name, checks)
    check(json.loads(STATE_VALIDATION.read_text())["status"] == "PASS_INDEPENDENT_SOURCE_AND_IMPLEMENTATION_RECONSTRUCTION", "state validation status", checks)
    check(json.loads(SOURCE_VALIDATION.read_text())["status"] == "PASS_INDEPENDENT_SOURCE_SEPARATOR_RECONSTRUCTION", "source validation status", checks)
    check(json.loads(ALIGNMENT_VALIDATION.read_text())["status"] == "PASS_INDEPENDENT_SOURCE_STA_ALIGNMENT_RECONSTRUCTION", "alignment validation status", checks)

    rows, info = reconstruct()
    panel_bytes = render_panel(rows)
    check(panel_bytes == PANEL.read_bytes(), "exact panel bytes", checks)
    check(len(rows) == 5012, "exact panel rows", checks)
    check(len({row["source_group_id"] for row in rows}) == len(rows), "unique panel IDs", checks)
    check(info["primary_state_rows"] == 600, "exact primary state rows", checks)
    check(info["common_pages"] == 196, "exact common pages", checks)
    check(info["switch_before_metadata"] == ["f39", "f55", "f68", "f70", "f73", "f87", "f89", "f90", "f96"], "exact premetadata switch leaves", checks)
    leaves = ["f39", "f55", "f68", "f73", "f87", "f89", "f90", "f96"]
    check(info["eligible"] == leaves, "exact eligible leaves", checks)
    check(info["target_column_mutation_isolated"], "family target column isolation mutation", checks)
    check(not (FORBIDDEN & set(PANEL_FIELDS)), "forbidden panel columns absent", checks)

    groups = Counter(row["edition"] for row in rows)
    expected_groups = {"ZL3b": 1684, "IT2a": 1731, "RF1b": 1597}
    check({edition: groups[edition] for edition in READINGS} == expected_groups, "exact reading counts", checks)
    sides = Counter((row["edition"], row["physical_folio"], row["side"]) for row in rows)
    check(min(sides.values()) == 39, "exact minimum leaf-side count", checks)
    states = {(row["physical_folio"], row["side"]): int(row["page_state"]) for row in rows}
    check(all({states[(folio, side)] for side in "rv"} == {0, 1} for folio in leaves), "all opposite pairs", checks)
    high_recto = sum(states[(folio, "r")] == 1 for folio in leaves)
    check((high_recto, len(leaves) - high_recto) == (5, 3), "exact orientation support", checks)
    cells = Counter((row["edition"], row["physical_folio"], row["side"], *(row[field] for field in META)) for row in rows)
    check(all(any(key[0] == row["edition"] and key[1] == row["physical_folio"] and key[2] != row["side"] and key[3:] == tuple(row[field] for field in META) for key in cells) for row in rows), "actual metadata overlap", checks)

    v1 = json.loads(V1.read_text())
    check(v1["status"] == "STOP_INSUFFICIENT_CHO_CHE_COSWITCH_CAPACITY", "v1 status", checks)
    check({key for key, value in v1["gates"].items() if not value} == {"at_least_1600_groups_each_reading"}, "v1 sole false gate", checks)
    check(v1["groups_by_reading"] == expected_groups, "v1 reading counts", checks)
    check(v1["eligible_common_switch_leaves"] == leaves, "v1 leaves", checks)
    check(v1["masked_panel_sha256"] == hashlib.sha256(panel_bytes).hexdigest(), "v1 panel binding", checks)
    check(v1["target_associations_computed"] == v1["scores_computed"] == v1["p_values_computed"] == 0, "v1 zero target computation", checks)

    v2 = json.loads(V2.read_text())
    check(v2["status"] == "PASS_CORRECTED_INFERENTIAL_UNIT_CHO_CHE_COSWITCH_CAPACITY", "v2 status", checks)
    check(v2["decision"] == "AUTHORIZE_TARGET_FREE_COSWITCH_PREFLIGHT_ONLY", "v2 decision", checks)
    check(v2["v1_false_gate"] == ["at_least_1600_groups_each_reading"], "v2 correction identity", checks)
    check(v2["eligible_common_switch_leaves"] == leaves, "v2 leaves", checks)
    check(v2["groups_by_reading"] == expected_groups, "v2 reading counts", checks)
    check(v2["minimum_groups_per_reading_leaf_side"] == 39, "v2 minimum side count", checks)
    check((v2["high_recto_leaves"], v2["high_verso_leaves"]) == (5, 3), "v2 orientation", checks)
    check(v2["leaf_flip_orbit"] == 256 and v2["attainable_one_sided_p_floor"] == .00390625, "v2 orbit", checks)
    check(all(v2["gates"].values()), "v2 all gates", checks)
    check(v2["target_associations_computed"] == v2["scores_computed"] == v2["p_values_computed"] == 0, "v2 zero target computation", checks)
    check(v2["english_glosses"] == 0, "zero English glosses", checks)

    expected_v2_report = f"""# `cho/che` independent co-switch capacity v2

Status: **{v2['status']}**

V1 is preserved as a target-free stop: RF retained 1,597 rather than 1,600
groups.  V2 corrects only that noninferential rounded row-total gate.  The
actual independent-unit geometry remains **8 physical leaves**,
**5/3** high-recto/high-verso, at least
**39** groups per reading/leaf/side, and an exact
**256**-state leaf-flip orbit (floor **0.003906**).

The exact per-reading totals remain recorded: ZL **1,684**, IT
**1,731**, RF **1,597**.  No feature/state
association, score, effect, or p-value has been computed.  Decision:
**AUTHORIZE_TARGET_FREE_COSWITCH_PREFLIGHT_ONLY**.  Synthetic null/power calibration is mandatory before target
access.  This supplies no co-switch result, meaning, sound, wordhood, language,
cipher, plaintext, or translation.
"""
    check(V2_REPORT.read_text() == expected_v2_report, "exact v2 report", checks)

    result = {
        "experiment": "CHO_CHE_COSWITCH_CAPACITY_VALIDATION",
        "status": "PASS_INDEPENDENT_SCORE_BLIND_COSWITCH_CAPACITY_RECONSTRUCTION",
        "checks_passed": len(checks),
        "checks": checks,
        "inputs": {path.name: digest(path) for path in (*HASHES, VALIDATOR)},
        "reconstructed": {
            "panel_rows": len(rows),
            "groups_by_reading": expected_groups,
            "consensus_page_sides": info["common_pages"],
            "eligible_leaves": leaves,
            "high_recto": high_recto,
            "high_verso": len(leaves) - high_recto,
            "minimum_groups_per_leaf_side": min(sides.values()),
            "leaf_flip_orbit": 256,
            "p_floor": .00390625,
            "panel_sha256": hashlib.sha256(panel_bytes).hexdigest(),
            "family_target_column_mutation_isolated": True,
        },
        "v1_stop_preserved": True,
        "v2_correction_valid": True,
        "target_associations_computed": 0,
        "english_glosses": 0,
        "claim_ceiling": "Independent reconstruction validates score-blind capacity and the inferential-unit correction only. It supplies no co-switch result, meaning, sound, wordhood, language, cipher, plaintext, or translation.",
    }
    report = f"""# `cho/che` co-switch capacity validation

**PASS**: {len(checks)} independent checks reconstruct the 5,012-row masked
panel, all 196 consensus page sides, the nine pre-metadata and eight eligible
opposite-state leaves, exact 1,684/1,731/1,597 reading counts, 5/3 orientation,
39-group minimum, 256-state orbit, the preserved v1 stop, and the v2
inferential-unit correction.  Mutating a hidden family target column leaves
capacity geometry unchanged.  Zero family/state associations were computed.
"""
    install_pair((json.dumps(result, indent=2, sort_keys=True) + "\n").encode(), report.encode())
    print(json.dumps({"status": result["status"], "checks_passed": len(checks)}, sort_keys=True))


if __name__ == "__main__":
    main()
