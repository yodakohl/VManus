#!/usr/bin/env python3
"""Build the outcome-blind cho/che paragraph-scope capacity panel."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


BASE = Path(__file__).resolve().parent
RESULTS = BASE / "results"
SEPARATORS = RESULTS / "source_separator_transcription.tsv"
SEPARATOR_VALIDATION = RESULTS / "source_separator_transcription_validation.json"
ALIGNMENT = RESULTS / "source_sta_group_alignment.tsv"
ALIGNMENT_VALIDATION = RESULTS / "source_sta_group_alignment_validation.json"
PARISEL_VALIDATION = RESULTS / "parisel_cho_che_source_audit_validation.json"
SPEC = BASE / "CHO_CHE_SCOPE_CAPACITY_SPEC.md"
BUILDER = Path(__file__).resolve()
OUT = RESULTS / "cho_che_scope_capacity.json"
PANEL = RESULTS / "cho_che_scope_primary_queries.tsv"
REPORT = RESULTS / "cho_che_scope_capacity_report.md"

FROZEN = {
    SEPARATORS: "4b649c8290d5afc7a5fbcc8e98db2bc123a1ceb5f3858d3befa781ce96b680f0",
    SEPARATOR_VALIDATION: "8698a2643219fd8ab00b05bba8705a1f1e8219c9b468824fbe2dc92117043deb",
    ALIGNMENT: "f23654f1d4c854db6d458b418a0d3530115731604854cf0a0495565e58341840",
    ALIGNMENT_VALIDATION: "cc53d32646b21e4135f0b23d98662e10835307ad860d021ea8c487261d7646fd",
    PARISEL_VALIDATION: "17009e151704d91f795216eed0913cfece447a396d08234df9af46624f286f3b",
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


def tsv_bytes(rows: list[dict]) -> bytes:
    target = io.StringIO(newline="")
    writer = csv.DictWriter(target, fieldnames=FIELDS, delimiter="\t", lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return target.getvalue().encode("utf-8")


def main() -> None:
    if any(path.exists() for path in (OUT, PANEL, REPORT)):
        raise SystemExit("refusing to overwrite cho/che scope capacity artifacts")
    for path, expected in FROZEN.items():
        if sha(path) != expected:
            raise SystemExit(f"frozen input mismatch: {path.name}")
    if json.loads(SEPARATOR_VALIDATION.read_text())["status"] != "PASS_INDEPENDENT_SOURCE_SEPARATOR_RECONSTRUCTION":
        raise SystemExit("separator validation is not PASS")
    if json.loads(ALIGNMENT_VALIDATION.read_text())["status"] != "PASS_INDEPENDENT_SOURCE_STA_ALIGNMENT_RECONSTRUCTION":
        raise SystemExit("STA alignment validation is not PASS")
    if json.loads(PARISEL_VALIDATION.read_text())["status"] != "PASS_INDEPENDENT_SOURCE_AND_IMPLEMENTATION_RECONSTRUCTION":
        raise SystemExit("Parisel source audit validation is not PASS")

    with SEPARATORS.open(encoding="utf-8", newline="") as handle:
        separator_rows = list(csv.DictReader(handle, delimiter="\t"))
    by_group_id = {row["source_group_id"]: row for row in separator_rows}
    if len(by_group_id) != len(separator_rows):
        raise ValueError("duplicate source group ID")

    panel_lines: dict[str, list[tuple[int, str, int, str]]] = defaultdict(list)
    all_zl_panels = set()
    all_zl_lines = set()
    for row in separator_rows:
        if (
            row["edition"] == "ZL3b"
            and row["source_group_index"] == "1"
            and row["grammar_scope"] == "CONFIRMED_PROSE"
            and row["kind"] == "P"
        ):
            all_zl_panels.add(row["page"])
            all_zl_lines.add(row["locus"])
            side = re.match(r"f\d+[rv]", row["page"])
            if side:
                panel_lines[row["page"]].append((
                    int(row["source_row_index"]), row["locus"],
                    int(row["paragraph_start"]), side.group(),
                ))
    if len(all_zl_panels) != 197 or len(all_zl_lines) != 4035:
        raise ValueError("complete ZL scaffold count drift")

    ownership = {}
    side_line_order: dict[str, list[tuple[int, str]]] = defaultdict(list)
    paragraph_ids = set()
    for panel, line_rows in sorted(panel_lines.items()):
        paragraph_number = 0
        for order, locus, starts, side in sorted(line_rows):
            if starts or paragraph_number == 0:
                paragraph_number += 1
            paragraph_id = f"{panel}|P{paragraph_number:03d}"
            if locus in ownership:
                raise ValueError("duplicate ZL paragraph ownership")
            ownership[locus] = {
                "collapsed_page": side,
                "panel_page": panel,
                "paragraph_id": paragraph_id,
                "source_row_index": order,
            }
            paragraph_ids.add(paragraph_id)
            side_line_order[side].append((order, locus))
    if len(panel_lines) != 196 or len(ownership) != 4024 or len(paragraph_ids) != 709:
        raise ValueError("numeric paragraph scaffold count drift")

    quartile = {}
    for side, line_rows in side_line_order.items():
        ordered = sorted(line_rows)
        for index, (order, locus) in enumerate(ordered):
            quartile[locus] = min(3, 4 * index // len(ordered))

    events: dict[str, list[dict]] = {edition: [] for edition in READINGS}
    with ALIGNMENT.open(encoding="utf-8", newline="") as handle:
        for aligned in csv.DictReader(handle, delimiter="\t"):
            edition = aligned["edition"]
            if edition not in events or aligned["alternative_site_count"] != "0":
                continue
            metadata = by_group_id.get(aligned["source_group_id"])
            if metadata is None or metadata["locus"] not in ownership:
                continue
            surface = aligned["nearest_basic_eva_primary"]
            if not re.fullmatch(r"[a-z]+", surface):
                continue
            sites = list(re.finditer(r"(?:ch|sh)[oe]", surface))
            if len(sites) != 1:
                continue
            masked = re.sub(r"((?:ch|sh))[oe]", r"\1X", surface)
            owner = ownership[metadata["locus"]]
            folio_match = re.match(r"f\d+", owner["collapsed_page"])
            if folio_match is None:
                raise ValueError("physical folio parse failure")
            events[edition].append({
                "source_group_id": aligned["source_group_id"],
                "locus": metadata["locus"],
                "source_group_index": int(aligned["source_group_index"]),
                "collapsed_page": owner["collapsed_page"],
                "panel_page": owner["panel_page"],
                "physical_folio": folio_match.group(),
                "paragraph_id": owner["paragraph_id"],
                "line_quartile": quartile[metadata["locus"]],
                "masked_template": masked,
            })

    mode_bins = {
        "NO_POSITION": lambda event: 0,
        "PAGE_HALF": lambda event: event["line_quartile"] // 2,
        "PAGE_QUARTILE": lambda event: event["line_quartile"],
    }
    mode_summaries = {}
    primary_by_edition = {}
    for edition in READINGS:
        mode_summaries[edition] = {}
        for mode, bin_function in mode_bins.items():
            strata: dict[tuple, list[dict]] = defaultdict(list)
            for event in events[edition]:
                strata[(event["collapsed_page"], event["masked_template"], bin_function(event))].append(event)
            queries = []
            for event in events[edition]:
                stratum = strata[(event["collapsed_page"], event["masked_template"], bin_function(event))]
                same = {
                    candidate["source_group_id"] for candidate in stratum
                    if candidate["paragraph_id"] == event["paragraph_id"]
                    and candidate["source_group_id"] != event["source_group_id"]
                }
                other = {
                    candidate["source_group_id"] for candidate in stratum
                    if candidate["paragraph_id"] != event["paragraph_id"]
                }
                if same and other:
                    query = dict(event)
                    query["same_paragraph_training_groups"] = len(same)
                    query["other_paragraph_training_groups"] = len(other)
                    queries.append(query)
            mode_summaries[edition][mode] = {
                "queries": len(queries),
                "collapsed_pages": len({row["collapsed_page"] for row in queries}),
                "physical_folios": len({row["physical_folio"] for row in queries}),
                "paragraphs": len({row["paragraph_id"] for row in queries}),
                "masked_templates": len({row["masked_template"] for row in queries}),
            }
            if mode == "PAGE_QUARTILE":
                primary_by_edition[edition] = queries

    physical_keys = {
        edition: {
            f"{row['locus']}|G{row['source_group_index']:03d}|{row['masked_template']}"
            for row in primary_by_edition[edition]
        }
        for edition in READINGS
    }
    common_keys = set.intersection(*(physical_keys[edition] for edition in READINGS))
    query_rows = []
    common_pages = set()
    common_paragraphs = set()
    common_folios = set()
    common_templates = set()
    for edition in READINGS:
        for row in primary_by_edition[edition]:
            physical_key = f"{row['locus']}|G{row['source_group_index']:03d}|{row['masked_template']}"
            common = physical_key in common_keys
            query_rows.append({
                "query_id": f"{edition}|{row['locus']}|G{row['source_group_index']:03d}",
                "edition": edition,
                "physical_query_key": physical_key,
                "locus": row["locus"],
                "source_group_index": row["source_group_index"],
                "collapsed_page": row["collapsed_page"],
                "panel_page": row["panel_page"],
                "physical_folio": row["physical_folio"],
                "paragraph_id": row["paragraph_id"],
                "line_quartile": row["line_quartile"],
                "masked_template": row["masked_template"],
                "same_paragraph_training_groups": row["same_paragraph_training_groups"],
                "other_paragraph_training_groups": row["other_paragraph_training_groups"],
                "common_all_three": int(common),
            })
            if edition == "ZL3b" and common:
                common_pages.add(row["collapsed_page"])
                common_paragraphs.add(row["paragraph_id"])
                common_folios.add(row["physical_folio"])
                common_templates.add(row["masked_template"])
    query_rows.sort(key=lambda row: (row["edition"], row["query_id"]))
    if len({row["query_id"] for row in query_rows}) != len(query_rows):
        raise ValueError("duplicate query ID")
    PANEL.write_bytes(tsv_bytes(query_rows))

    result = {
        "experiment": "CHO_CHE_SCOPE_CAPACITY",
        "status": "PASS_SCORE_BLIND_PARAGRAPH_SCOPE_CAPACITY",
        "inputs": {path.name: sha(path) for path in (*FROZEN, SPEC, BUILDER)},
        "scaffold": {
            "all_zl_panel_records_including_fros": len(all_zl_panels),
            "all_zl_lines_including_fros": len(all_zl_lines),
            "numeric_panel_records": len(panel_lines),
            "numeric_scaffold_lines": len(ownership),
            "marked_paragraphs": len(paragraph_ids),
            "collapsed_page_sides": len(side_line_order),
        },
        "strict_single_site_events": {
            edition: {
                "events": len(events[edition]),
                "collapsed_pages": len({row["collapsed_page"] for row in events[edition]}),
                "physical_folios": len({row["physical_folio"] for row in events[edition]}),
                "masked_templates": len({row["masked_template"] for row in events[edition]}),
            }
            for edition in READINGS
        },
        "capacity_by_reading_and_position_control": mode_summaries,
        "primary_panel": {
            "position_control": "PAGE_QUARTILE",
            "stored_reading_queries": len(query_rows),
            "queries_by_reading": {edition: len(primary_by_edition[edition]) for edition in READINGS},
            "common_all_three_query_keys": len(common_keys),
            "common_collapsed_pages": len(common_pages),
            "common_physical_folios": len(common_folios),
            "common_paragraphs": len(common_paragraphs),
            "common_masked_templates": len(common_templates),
            "common_key_sha256": hashlib.sha256("\n".join(sorted(common_keys)).encode()).hexdigest(),
            "panel_sha256": sha(PANEL),
        },
        "gates": {
            "exact_complete_scaffold": len(all_zl_panels) == 197 and len(all_zl_lines) == 4035,
            "exact_numeric_scaffold": len(panel_lines) == 196 and len(ownership) == 4024 and len(paragraph_ids) == 709,
            "at_least_450_queries_each_reading": all(len(primary_by_edition[edition]) >= 450 for edition in READINGS),
            "at_least_30_folios_each_reading": all(mode_summaries[edition]["PAGE_QUARTILE"]["physical_folios"] >= 30 for edition in READINGS),
            "at_least_100_paragraphs_each_reading": all(mode_summaries[edition]["PAGE_QUARTILE"]["paragraphs"] >= 100 for edition in READINGS),
            "at_least_300_common_queries": len(common_keys) >= 300,
            "at_least_25_common_folios": len(common_folios) >= 25,
            "every_query_has_both_training_sources": all(
                row["same_paragraph_training_groups"] > 0 and row["other_paragraph_training_groups"] > 0
                for row in query_rows
            ),
            "outcome_columns_zero": not ({"outcome", "o", "e", "cho", "che", "surface"} & set(FIELDS)),
            "scores_and_pvalues_zero": True,
            "english_glosses_zero": True,
        },
        "target_outcomes_stored": 0,
        "target_scores_computed": 0,
        "english_glosses": 0,
        "claim_ceiling": (
            "Score-blind capacity for a conditional exact-template same-marked-paragraph versus "
            "other-marked-paragraph predictive test within collapsed page and line quartile. No "
            "authorial paragraph, regime scope, sound, word, language, cipher operation, meaning, "
            "plaintext, or translation follows."
        ),
    }
    if not all(result["gates"].values()):
        raise ValueError("cho/che scope capacity gate failure")
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report = f"""# `cho/che` paragraph-scope capacity audit

Status: **{result['status']}**

The source-native panel has enough exact-template repetition for a genuinely
different scope test. After requiring one unambiguous site per source group and
conditioning on collapsed page, exact masked template, and ZL line-order
quartile, ZL/IT/RF each retain **{len(primary_by_edition['ZL3b'])}/
{len(primary_by_edition['IT2a'])}/{len(primary_by_edition['RF1b'])}** eligible
queries on **{mode_summaries['ZL3b']['PAGE_QUARTILE']['physical_folios']}/
{mode_summaries['IT2a']['PAGE_QUARTILE']['physical_folios']}/
{mode_summaries['RF1b']['PAGE_QUARTILE']['physical_folios']}** physical folios.
Exactly **{len(common_keys)}** query keys on **{len(common_folios)}** folios are
present in every reading's panel.

Each query has at least one other exact-template group in the same marked
paragraph and at least one in another marked paragraph within the same page
quartile. The artifact stores masked templates and support counts only: zero
`o/e` outcomes, page states, paragraph scores, or p-values were emitted.

This authorizes preregistration and controls, not scoring. The paragraph marks
are ZL editorial layout judgments and no semantic or lexical conclusion follows.
"""
    REPORT.write_text(report, encoding="utf-8")
    print(json.dumps({
        "status": result["status"],
        "queries": result["primary_panel"]["queries_by_reading"],
        "common": len(common_keys),
        "common_folios": len(common_folios),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
