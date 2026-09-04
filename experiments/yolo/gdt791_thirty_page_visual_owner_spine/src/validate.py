#!/usr/bin/env python3
"""Validate GDT791 cardinalities, boundary decisions and clean byte replay."""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path

sys.dont_write_bytecode = True


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt791_thirty_page_visual_owner_spine"
ART = BASE / "artifacts"
RUNNER = BASE / "src/run.py"
VALIDATION = ART / "VALIDATION.json"
EXPECTED_FILES = (
    "GDT791_30_PAGE_EVIDENCE_REGISTRY.tsv",
    "GDT791_1007_LINE_OWNER_ATLAS.tsv",
    "GDT791_5866_OCCURRENCE_SPINE.tsv",
    "GDT791_240_RECORD_LOCAL_STATEMENT_FRAGMENTS.tsv",
    "GDT791_5_CROSS_RECORD_STATEMENTS.tsv",
    "GDT791_745_DEEP_ALIAS_BINDINGS.tsv",
    "GDT791_3_RAW_BOUNDARY_LINK_REPAIRS.tsv",
    "GDT791_10_EXACT_STRING_REFERENCE_EDGES.tsv",
    "GDT791_6_FORM_RUNNING_CENSUS.tsv",
    "GDT791_5_TOPOLOGY_FAMILY_SUMMARY.tsv",
    "GDT791_GUARDED_SOURCE_STATS.tsv",
    "RESULT.json",
)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def main() -> int:
    checks = 0

    def require(condition: bool, message: str) -> None:
        nonlocal checks
        checks += 1
        if not condition:
            raise AssertionError(message)

    result = json.loads((ART / "RESULT.json").read_text(encoding="utf-8"))
    require(result["experiment_id"] == "GDT791", "wrong experiment id")
    require(result["status"].startswith("PASS__30_VISUALLY_REVIEWED_PAGES"), "wrong status")
    require(result["decision"] == "PANEL_THEN_RECORD_THEN_LEGACY_STATEMENT__LOSSLESS_30_PAGE_SPINE_SELECTED", "wrong decision")
    expected_counts = {
        "physical_pages": 30, "source_selectors": 35, "visually_reviewed_page_contexts": 30,
        "deep_panel_pages": 3, "deep_panels": 10, "deep_records": 13, "source_lines": 1007,
        "source_tokens": 5866, "running_prose_lines": 612, "local_label_or_marker_lines": 392,
        "empty_transcription_lines": 3, "running_events": 5122, "local_cards": 744,
        "deep_legacy_statements": 235, "record_local_statement_fragments": 240,
        "cross_record_statements": 5, "cross_panel_statements": 4,
        "same_panel_cross_record_statements": 1, "deep_aliases": 745,
        "same_record_aliases_retained": 460, "owner_default_aliases_reparented": 283,
        "cross_record_aliases_quarantined": 2, "raw_primary_governor_crossings_clipped": 1,
        "effective_grammar_host_crossings": 0, "exact_string_reference_edges": 10,
        "exact_string_reference_semantic_credit": 0, "token_semantics_changed": 0,
        "component_exports": 0, "sealed_rows_materialized": 0,
    }
    for key, value in expected_counts.items():
        require(result["counts"].get(key) == value, f"count changed: {key}")
    require(result["boundary_repair"]["precedence"] == ["PANEL", "RECORD", "LEGACY_STATEMENT"], "wrong precedence")
    require("Remove the inherited CH action and Y object" in result["boundary_repair"]["f77r_otedy"], "otedy repair absent")

    pages = read_tsv(ART / EXPECTED_FILES[0])
    lines = read_tsv(ART / EXPECTED_FILES[1])
    occurrences = read_tsv(ART / EXPECTED_FILES[2])
    fragments = read_tsv(ART / EXPECTED_FILES[3])
    crossings = read_tsv(ART / EXPECTED_FILES[4])
    aliases = read_tsv(ART / EXPECTED_FILES[5])
    repairs = read_tsv(ART / EXPECTED_FILES[6])
    bridges = read_tsv(ART / EXPECTED_FILES[7])
    forms = read_tsv(ART / EXPECTED_FILES[8])
    topology = read_tsv(ART / EXPECTED_FILES[9])
    guard = read_tsv(ART / EXPECTED_FILES[10])

    require(len(pages) == 30, "page row count")
    require(len({row["physical_page"] for row in pages}) == 30, "page uniqueness")
    require(all(not row["physical_page"].startswith("f84") for row in pages), "sealed page in registry")
    require(sum(len(row["source_selectors"].split("|")) for row in pages) == 35, "selector count")
    require(sum(row["visual_annotation_tier"] == "DEEP_PANEL_COMPONENT" for row in pages) == 3, "deep tier count")
    require(sum(row["visual_annotation_tier"] == "DIRECT_PAGE_CONTEXT" for row in pages) == 27, "page-context tier count")
    require(all((ROOT / row["visual_source_path"]).is_file() for row in pages), "visual evidence path missing")
    require({row["topology_family"] for row in pages} == {
        "TEXT_BLOCK", "WHOLE_PLANT_ARTICLE", "RADIAL_ARRAY", "POOL_APPARATUS_NETWORK", "MATERIAL_REGISTER"
    }, "topology family set")
    for row in pages:
        require(int(row["raw_token_count"]) == int(row["running_event_count"]) + int(row["local_card_count"]), f"page token split {row['physical_page']}")
        require(int(row["raw_line_count"]) == int(row["running_prose_line_count"]) + int(row["local_label_line_count"]) + int(row["empty_line_count"]), f"page line split {row['physical_page']}")

    require(len(lines) == 1007, "line row count")
    require(sum(int(row["token_count"]) for row in lines) == 5866, "line token count")
    require(Counter(row["line_kind"] for row in lines) == Counter({
        "RUNNING_PROSE": 612, "LOCAL_LABEL_OR_MARKER": 392, "EMPTY_TRANSCRIPTION_LINE": 3
    }), "line type partition")
    require(all(not row["source_selector"].startswith("f84") for row in lines), "sealed line materialized")
    require(all(row["semantic_export_credit"] == "ZERO__STRUCTURAL_CROSSWALK_ONLY" for row in lines), "line semantic credit")
    for row in lines:
        require(int(row["token_count"]) == len(row["eva_clean"].split()), f"line token replay {row['locus']}")
        if row["line_kind"] == "RUNNING_PROSE":
            require(int(row["running_event_count"]) == int(row["token_count"]), f"running line partition {row['locus']}")
        elif row["line_kind"] == "LOCAL_LABEL_OR_MARKER":
            require(int(row["local_card_count"]) == int(row["token_count"]), f"local line partition {row['locus']}")
        else:
            require(int(row["token_count"]) == 0, f"empty line nonempty {row['locus']}")

    require(len(occurrences) == 5866, "occurrence row count")
    require(Counter(row["occurrence_kind"] for row in occurrences) == Counter({
        "RUNNING_EVENT": 5122, "LOCAL_ADDRESS_OR_LABEL": 744
    }), "occurrence partition")
    require(all(not row["source_selector"].startswith("f84") for row in occurrences), "sealed occurrence")
    require(all(row["semantic_export_credit"] == "ZERO__STRUCTURAL_CROSSWALK_ONLY" for row in occurrences), "occurrence semantic credit")
    require(sum(row["context_scope"] == "DEEP_PANEL_RECORD" for row in occurrences) == 940, "deep prose occurrence count")
    require(sum(row["context_scope"] == "DEEP_PANEL_COMPONENT_LABEL" for row in occurrences) == 28, "deep label occurrence count")

    require(len(fragments) == 240, "fragment count")
    require(len({row["legacy_statement_id"] for row in fragments}) == 235, "fragment legacy statement count")
    require(sum(row["record_boundary_action"] == "SPLIT_LEGACY_STATEMENT" for row in fragments) == 10, "split fragment count")
    require(all(row["semantic_export_credit"] == "ZERO__BOUNDARY_REPAIR_ONLY" for row in fragments), "fragment semantic credit")
    require(len(crossings) == 5, "crossing statement count")
    require(Counter(row["crossing_class"] for row in crossings) == Counter({"PANEL_CROSS": 4, "RECORD_CROSS_SAME_PANEL": 1}), "crossing classes")
    require({row["legacy_end_mode"] for row in crossings} == {"LICENSED_DY_CLOSE"}, "crossing close modes")
    require({row["legacy_statement_id"] for row in crossings} == {"G407-S357", "G407-S527", "G407-S576", "G407-S597", "G407-S631"}, "crossing identities")

    require(len(aliases) == 745, "deep alias count")
    require(Counter(row["selected_boundary_action"] for row in aliases) == Counter({
        "RETAIN_SAME_RECORD_ALIAS": 460,
        "REPARENT_OWNER_DEFAULT_TO_LOCAL_RECORD_OWNER": 283,
        "QUARANTINE_CROSS_RECORD_ALIAS": 2,
    }), "alias action partition")
    quarantined = [row for row in aliases if row["selected_boundary_action"] == "QUARANTINE_CROSS_RECORD_ALIAS"]
    require({row["alias_id"] for row in quarantined} == {"GDT581-I0926", "GDT581-I2727"}, "quarantine ids")
    require({row["target_event_id"] for row in quarantined} == {"G407-E2535"}, "quarantine target")
    require({row["target_surface"] for row in quarantined} == {"otedy"}, "quarantine target surface")
    require({row["source_surface"] for row in quarantined} == {"qolchy"}, "quarantine source surface")

    require(len(repairs) == 3, "repair row count")
    require({row["link_id"] for row in repairs} == {"GDT581-I0926", "GDT581-I2727", "G407-A02721"}, "repair ids")
    require(Counter(row["link_kind"] for row in repairs) == Counter({"ACTION_ALIAS": 1, "OBJECT_ALIAS": 1, "RAW_PRIMARY_GOVERNOR": 1}), "repair classes")
    require(all(row["source_record_id"] == "F77_P1" and row["target_record_id"] == "F77_P2" for row in repairs), "repair record edge")
    focus = next(row for row in repairs if row["link_kind"] == "RAW_PRIMARY_GOVERNOR")
    require(focus["effective_local_host"] == "CONTROL:G407-E2535:OT>G<DY", "effective local control host")

    require(len(bridges) == 10, "bridge count")
    require(all(row["cross_panel"] == "YES" for row in bridges), "bridge cross-panel flag")
    require(all(row["graph_edge_class"] == "EXACT_STRING_REFERENCE" for row in bridges), "bridge graph type")
    require(all(row["semantic_credit"] == "ZERO__STRING_REUSE_ONLY" for row in bridges), "bridge source credit")
    require(all(row["record_merge_credit"] == "ZERO" and row["meaning_transfer_credit"] == "ZERO" for row in bridges), "bridge integration credit")

    expected_forms = {
        "otedy": (18, 9, 8, 5), "okal": (16, 11, 4, 2), "otchdy": (3, 3, 1, 1),
        "olaiin": (11, 8, 1, 1), "darol": (0, 0, 0, 0), "darolsy": (0, 0, 0, 0),
    }
    require(len(forms) == 6, "form count")
    for row in forms:
        expected = expected_forms[row["surface"]]
        observed = tuple(int(row[key]) for key in (
            "running_occurrence_count", "running_physical_page_count",
            "statement_first_occurrence_count", "deep_running_occurrence_count"
        ))
        require(observed == expected, f"form census changed: {row['surface']}")
        require(row["portable_meaning_selected"] == "NO", f"form meaning leaked: {row['surface']}")
    require(len(topology) == 5, "topology summary rows")
    require(sum(int(row["physical_page_count"]) for row in topology) == 30, "topology page total")
    require(sum(int(row["raw_token_count"]) for row in topology) == 5866, "topology token total")
    require(sum(int(row["running_event_count"]) for row in topology) == 5122, "topology running total")
    require(sum(int(row["local_card_count"]) for row in topology) == 744, "topology local total")
    require(len(guard) == 1 and guard[0]["selected_rows"] == "1007", "guard selected rows")
    require(guard[0]["skipped_forbidden_rows"] == "98", "guard forbidden rows")
    require(guard[0]["materialized_f84_rows"] == "0" and guard[0]["materialized_f84r_rows"] == "0", "sealed materialization")

    with tempfile.TemporaryDirectory(prefix="gdt791_a_") as first, tempfile.TemporaryDirectory(prefix="gdt791_b_") as second:
        for target in (first, second):
            completed = subprocess.run(
                [sys.executable, str(RUNNER), "--output-dir", target], cwd=ROOT,
                text=True, capture_output=True, check=False,
            )
            require(completed.returncode == 0, f"clean runner failed: {completed.stderr}")
        for name in EXPECTED_FILES:
            checked = ART / name
            one, two = Path(first) / name, Path(second) / name
            require(checked.is_file() and one.is_file() and two.is_file(), f"missing replay file {name}")
            require(checked.read_bytes() == one.read_bytes() == two.read_bytes(), f"byte replay failed: {name}")

    payload = {
        "experiment_id": "GDT791",
        "status": "PASS",
        "checks": checks,
        "byte_replayed_outputs": len(EXPECTED_FILES),
        "source_lock_verified_by_runner": True,
        "sealed_rows_materialized": 0,
        "checked_result_sha256": sha256(ART / "RESULT.json"),
    }
    VALIDATION.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"PASS GDT791 validation: {checks} checks; {len(EXPECTED_FILES)} outputs byte-replayed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
