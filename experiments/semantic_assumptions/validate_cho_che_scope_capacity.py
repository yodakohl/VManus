#!/usr/bin/env python3
"""Independent reconstruction of the outcome-blind cho/che scope panel."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import re
from collections import defaultdict
from pathlib import Path


BASE = Path(__file__).resolve().parent
RESULTS = BASE / "results"
SEPARATORS = RESULTS / "source_separator_transcription.tsv"
SEPARATOR_VALIDATION = RESULTS / "source_separator_transcription_validation.json"
ALIGNMENT = RESULTS / "source_sta_group_alignment.tsv"
ALIGNMENT_VALIDATION = RESULTS / "source_sta_group_alignment_validation.json"
PARISEL_VALIDATION = RESULTS / "parisel_cho_che_source_audit_validation.json"
SPEC = BASE / "CHO_CHE_SCOPE_CAPACITY_SPEC.md"
PRODUCER = BASE / "build_cho_che_scope_capacity.py"
PRODUCTION = RESULTS / "cho_che_scope_capacity.json"
PANEL = RESULTS / "cho_che_scope_primary_queries.tsv"
PRODUCTION_REPORT = RESULTS / "cho_che_scope_capacity_report.md"
VALIDATOR = Path(__file__).resolve()
OUT = RESULTS / "cho_che_scope_capacity_validation.json"
REPORT = RESULTS / "cho_che_scope_capacity_validation_report.md"

HASHES = {
    SEPARATORS: "4b649c8290d5afc7a5fbcc8e98db2bc123a1ceb5f3858d3befa781ce96b680f0",
    SEPARATOR_VALIDATION: "8698a2643219fd8ab00b05bba8705a1f1e8219c9b468824fbe2dc92117043deb",
    ALIGNMENT: "f23654f1d4c854db6d458b418a0d3530115731604854cf0a0495565e58341840",
    ALIGNMENT_VALIDATION: "cc53d32646b21e4135f0b23d98662e10835307ad860d021ea8c487261d7646fd",
    PARISEL_VALIDATION: "17009e151704d91f795216eed0913cfece447a396d08234df9af46624f286f3b",
    SPEC: "7e11a8a8e3c087985510e2031a087f9d44226ecf08991a78cf7a61adc1055c20",
    PRODUCER: "233c7ebd1aad45b84049c829b5fcb87cd1c6f5d0952271895c4380c3ab7534eb",
    PRODUCTION: "92ed820e81d289d9897259405ec5369c3eeaba8a0137e05b275725743348542a",
    PANEL: "b9163683ec3a7aae99633b16899b3f80f53dd2b7c23cde30260120d233c091eb",
    PRODUCTION_REPORT: "e70cf587a97635ba2968b89175424d35b19226c704a6e41f946c09cb41080548",
}
READINGS = ("ZL3b", "IT2a", "RF1b")
FIELDS = [
    "query_id", "edition", "physical_query_key", "locus",
    "source_group_index", "collapsed_page", "panel_page", "physical_folio",
    "paragraph_id", "line_quartile", "masked_template",
    "same_paragraph_training_groups", "other_paragraph_training_groups",
    "common_all_three",
]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def render(rows: list[dict]) -> bytes:
    target = io.StringIO(newline="")
    writer = csv.DictWriter(target, fieldnames=FIELDS, delimiter="\t", lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return target.getvalue().encode()


def main() -> None:
    if OUT.exists() or REPORT.exists():
        raise SystemExit("refusing to overwrite scope-capacity validation artifacts")
    checks = 0

    def require(condition: bool, label: str) -> None:
        nonlocal checks
        checks += 1
        if not condition:
            raise AssertionError(label)

    for path, expected in HASHES.items():
        require(sha(path) == expected, f"hash {path.name}")
    require(json.loads(SEPARATOR_VALIDATION.read_text())["status"] == "PASS_INDEPENDENT_SOURCE_SEPARATOR_RECONSTRUCTION", "separator status")
    require(json.loads(ALIGNMENT_VALIDATION.read_text())["status"] == "PASS_INDEPENDENT_SOURCE_STA_ALIGNMENT_RECONSTRUCTION", "alignment status")
    require(json.loads(PARISEL_VALIDATION.read_text())["status"] == "PASS_INDEPENDENT_SOURCE_AND_IMPLEMENTATION_RECONSTRUCTION", "Parisel status")

    with SEPARATORS.open(encoding="utf-8", newline="") as handle:
        metadata_rows = list(csv.DictReader(handle, delimiter="\t"))
    metadata = {}
    for row in metadata_rows:
        require(row["source_group_id"] not in metadata, "source group uniqueness")
        metadata[row["source_group_id"]] = row

    complete_panels = set()
    complete_lines = set()
    panel_lines: dict[str, list[tuple[int, str, bool, str]]] = defaultdict(list)
    for row in metadata_rows:
        if row["edition"] != "ZL3b" or row["source_group_index"] != "1":
            continue
        if row["grammar_scope"] != "CONFIRMED_PROSE" or row["kind"] != "P":
            continue
        complete_panels.add(row["page"])
        complete_lines.add(row["locus"])
        side = re.match(r"f\d+[rv]", row["page"])
        if side:
            panel_lines[row["page"]].append((
                int(row["source_row_index"]), row["locus"],
                row["paragraph_start"] == "1", side.group(),
            ))
    require(len(complete_panels) == 197, "complete panels")
    require(len(complete_lines) == 4035, "complete lines")

    owner = {}
    paragraph_set = set()
    side_lines: dict[str, list[tuple[int, str]]] = defaultdict(list)
    for panel in sorted(panel_lines):
        paragraph_number = 0
        for order, locus, starts, side in sorted(panel_lines[panel]):
            if starts or paragraph_number == 0:
                paragraph_number += 1
            paragraph = f"{panel}|P{paragraph_number:03d}"
            require(locus not in owner, "line ownership uniqueness")
            owner[locus] = (side, panel, paragraph, order)
            paragraph_set.add(paragraph)
            side_lines[side].append((order, locus))
    require(len(panel_lines) == 196, "numeric panels")
    require(len(owner) == 4024, "numeric lines")
    require(len(paragraph_set) == 709, "paragraphs")

    quartile = {}
    for side, values in side_lines.items():
        sequence = sorted(values)
        for index, (order, locus) in enumerate(sequence):
            quartile[locus] = min(3, 4 * index // len(sequence))

    events = {edition: [] for edition in READINGS}
    with ALIGNMENT.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            edition = row["edition"]
            if edition not in events or row["alternative_site_count"] != "0":
                continue
            meta = metadata.get(row["source_group_id"])
            if meta is None or meta["locus"] not in owner:
                continue
            projection = row["nearest_basic_eva_primary"]
            if re.fullmatch(r"[a-z]+", projection) is None:
                continue
            target_sites = re.findall(r"(?:ch|sh)[oe]", projection)
            if len(target_sites) != 1:
                continue
            masked = re.sub(r"((?:ch|sh))[oe]", r"\1X", projection)
            side, panel, paragraph, order = owner[meta["locus"]]
            physical = re.match(r"f\d+", side)
            require(physical is not None, "physical folio")
            events[edition].append({
                "source_group_id": row["source_group_id"],
                "locus": meta["locus"],
                "source_group_index": int(row["source_group_index"]),
                "collapsed_page": side,
                "panel_page": panel,
                "physical_folio": physical.group(),
                "paragraph_id": paragraph,
                "line_quartile": quartile[meta["locus"]],
                "masked_template": masked,
            })

    bin_functions = {
        "NO_POSITION": lambda event: 0,
        "PAGE_HALF": lambda event: event["line_quartile"] // 2,
        "PAGE_QUARTILE": lambda event: event["line_quartile"],
    }
    mode_summary = {}
    primary = {}
    for edition in READINGS:
        mode_summary[edition] = {}
        for mode, to_bin in bin_functions.items():
            strata: dict[tuple, list[dict]] = defaultdict(list)
            for event in events[edition]:
                strata[(event["collapsed_page"], event["masked_template"], to_bin(event))].append(event)
            eligible = []
            for event in events[edition]:
                candidates = strata[(event["collapsed_page"], event["masked_template"], to_bin(event))]
                same = {candidate["source_group_id"] for candidate in candidates if candidate["paragraph_id"] == event["paragraph_id"] and candidate["source_group_id"] != event["source_group_id"]}
                other = {candidate["source_group_id"] for candidate in candidates if candidate["paragraph_id"] != event["paragraph_id"]}
                if same and other:
                    value = dict(event)
                    value["same_paragraph_training_groups"] = len(same)
                    value["other_paragraph_training_groups"] = len(other)
                    eligible.append(value)
            mode_summary[edition][mode] = {
                "queries": len(eligible),
                "collapsed_pages": len({row["collapsed_page"] for row in eligible}),
                "physical_folios": len({row["physical_folio"] for row in eligible}),
                "paragraphs": len({row["paragraph_id"] for row in eligible}),
                "masked_templates": len({row["masked_template"] for row in eligible}),
            }
            if mode == "PAGE_QUARTILE":
                primary[edition] = eligible

    key_sets = {
        edition: {f"{row['locus']}|G{row['source_group_index']:03d}|{row['masked_template']}" for row in primary[edition]}
        for edition in READINGS
    }
    common = set.intersection(*(key_sets[edition] for edition in READINGS))
    panel_rows = []
    common_pages = set()
    common_folios = set()
    common_paragraphs = set()
    common_templates = set()
    for edition in READINGS:
        for row in primary[edition]:
            key = f"{row['locus']}|G{row['source_group_index']:03d}|{row['masked_template']}"
            shared = key in common
            panel_rows.append({
                "query_id": f"{edition}|{row['locus']}|G{row['source_group_index']:03d}",
                "edition": edition, "physical_query_key": key,
                "locus": row["locus"], "source_group_index": row["source_group_index"],
                "collapsed_page": row["collapsed_page"], "panel_page": row["panel_page"],
                "physical_folio": row["physical_folio"], "paragraph_id": row["paragraph_id"],
                "line_quartile": row["line_quartile"], "masked_template": row["masked_template"],
                "same_paragraph_training_groups": row["same_paragraph_training_groups"],
                "other_paragraph_training_groups": row["other_paragraph_training_groups"],
                "common_all_three": int(shared),
            })
            if edition == "ZL3b" and shared:
                common_pages.add(row["collapsed_page"])
                common_folios.add(row["physical_folio"])
                common_paragraphs.add(row["paragraph_id"])
                common_templates.add(row["masked_template"])
    panel_rows.sort(key=lambda row: (row["edition"], row["query_id"]))
    require(len({row["query_id"] for row in panel_rows}) == len(panel_rows), "query uniqueness")
    require(render(panel_rows) == PANEL.read_bytes(), "panel bytes")
    for row in panel_rows:
        require(row["same_paragraph_training_groups"] > 0, "same support")
        require(row["other_paragraph_training_groups"] > 0, "other support")
        require("o" not in FIELDS and "e" not in FIELDS and "surface" not in FIELDS, "outcome schema")

    actual = json.loads(PRODUCTION.read_text(encoding="utf-8"))
    require(actual["status"] == "PASS_SCORE_BLIND_PARAGRAPH_SCOPE_CAPACITY", "status")
    require(actual["scaffold"] == {
        "all_zl_panel_records_including_fros": len(complete_panels),
        "all_zl_lines_including_fros": len(complete_lines),
        "numeric_panel_records": len(panel_lines), "numeric_scaffold_lines": len(owner),
        "marked_paragraphs": len(paragraph_set), "collapsed_page_sides": len(side_lines),
    }, "scaffold object")
    require(actual["capacity_by_reading_and_position_control"] == mode_summary, "mode summaries")
    require(actual["strict_single_site_events"] == {
        edition: {
            "events": len(events[edition]),
            "collapsed_pages": len({row["collapsed_page"] for row in events[edition]}),
            "physical_folios": len({row["physical_folio"] for row in events[edition]}),
            "masked_templates": len({row["masked_template"] for row in events[edition]}),
        } for edition in READINGS
    }, "event summaries")
    expected_primary = {
        "position_control": "PAGE_QUARTILE", "stored_reading_queries": len(panel_rows),
        "queries_by_reading": {edition: len(primary[edition]) for edition in READINGS},
        "common_all_three_query_keys": len(common), "common_collapsed_pages": len(common_pages),
        "common_physical_folios": len(common_folios), "common_paragraphs": len(common_paragraphs),
        "common_masked_templates": len(common_templates),
        "common_key_sha256": hashlib.sha256("\n".join(sorted(common)).encode()).hexdigest(),
        "panel_sha256": sha(PANEL),
    }
    require(actual["primary_panel"] == expected_primary, "primary object")
    require(actual["inputs"] == {path.name: sha(path) for path in (*{p: None for p in (SEPARATORS, SEPARATOR_VALIDATION, ALIGNMENT, ALIGNMENT_VALIDATION, PARISEL_VALIDATION)}, SPEC, PRODUCER)}, "input bindings")
    require(all(actual["gates"].values()), "gates")
    require(actual["target_outcomes_stored"] == actual["target_scores_computed"] == actual["english_glosses"] == 0, "zero target access")
    require(expected_primary["queries_by_reading"] == {"ZL3b": 501, "IT2a": 501, "RF1b": 501}, "query vector")
    require(len(common) == 350 and len(common_folios) == 34, "common vector")

    expected_report = f"""# `cho/che` paragraph-scope capacity audit

Status: **{actual['status']}**

The source-native panel has enough exact-template repetition for a genuinely
different scope test. After requiring one unambiguous site per source group and
conditioning on collapsed page, exact masked template, and ZL line-order
quartile, ZL/IT/RF each retain **{len(primary['ZL3b'])}/
{len(primary['IT2a'])}/{len(primary['RF1b'])}** eligible
queries on **{mode_summary['ZL3b']['PAGE_QUARTILE']['physical_folios']}/
{mode_summary['IT2a']['PAGE_QUARTILE']['physical_folios']}/
{mode_summary['RF1b']['PAGE_QUARTILE']['physical_folios']}** physical folios.
Exactly **{len(common)}** query keys on **{len(common_folios)}** folios are
present in every reading's panel.

Each query has at least one other exact-template group in the same marked
paragraph and at least one in another marked paragraph within the same page
quartile. The artifact stores masked templates and support counts only: zero
`o/e` outcomes, page states, paragraph scores, or p-values were emitted.

This authorizes preregistration and controls, not scoring. The paragraph marks
are ZL editorial layout judgments and no semantic or lexical conclusion follows.
"""
    require(PRODUCTION_REPORT.read_text(encoding="utf-8") == expected_report, "report")

    result = {
        "experiment": "CHO_CHE_SCOPE_CAPACITY_VALIDATION",
        "status": "PASS_INDEPENDENT_SCORE_BLIND_SCOPE_CAPACITY_RECONSTRUCTION",
        "checks": checks,
        "production_sha256": sha(PRODUCTION),
        "panel_sha256": sha(PANEL),
        "validator_sha256": sha(VALIDATOR),
        "reconstructed": {"queries_each_reading": 501, "common_queries": 350, "common_folios": 34},
        "target_outcomes_accessed": False,
        "target_scores_computed": 0,
        "claim_ceiling": actual["claim_ceiling"],
        "failures": [],
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    validation_report = f"""# `cho/che` paragraph-scope capacity validation

Status: **{result['status']}**

A nonimporting reconstruction verified the complete ZL paragraph scaffold,
strict single-site event masking, all three position controls, all
**{len(panel_rows):,}** stored reading-query rows, the **350** common keys on
**34** folios, exact artifact bytes, and zero stored outcomes or scores in
**{checks:,}** checks. This validates capacity only; no scope or meaning follows.
"""
    REPORT.write_text(validation_report, encoding="utf-8")
    print(json.dumps({"status": result["status"], "checks": checks}, sort_keys=True))


if __name__ == "__main__":
    main()
