#!/usr/bin/env python3
"""Nonimporting reconstruction of the masked cho/che scope universe."""

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
CAPACITY = RESULTS / "cho_che_scope_capacity.json"
CAPACITY_VALIDATION = RESULTS / "cho_che_scope_capacity_validation.json"
PRIMARY = RESULTS / "cho_che_scope_primary_queries.tsv"
SPEC = BASE / "CHO_CHE_SCOPE_MASKED_UNIVERSE_SPEC.md"
PRODUCER = BASE / "build_cho_che_scope_masked_universe.py"
PRODUCTION = RESULTS / "cho_che_scope_masked_universe.json"
EVENTS = RESULTS / "cho_che_scope_masked_events.tsv"
PRODUCTION_REPORT = RESULTS / "cho_che_scope_masked_universe_report.md"
VALIDATOR = Path(__file__).resolve()
OUT = RESULTS / "cho_che_scope_masked_universe_validation.json"
REPORT = RESULTS / "cho_che_scope_masked_universe_validation_report.md"

HASHES = {
    SEPARATORS: "4b649c8290d5afc7a5fbcc8e98db2bc123a1ceb5f3858d3befa781ce96b680f0",
    SEPARATOR_VALIDATION: "8698a2643219fd8ab00b05bba8705a1f1e8219c9b468824fbe2dc92117043deb",
    ALIGNMENT: "f23654f1d4c854db6d458b418a0d3530115731604854cf0a0495565e58341840",
    ALIGNMENT_VALIDATION: "cc53d32646b21e4135f0b23d98662e10835307ad860d021ea8c487261d7646fd",
    CAPACITY: "92ed820e81d289d9897259405ec5369c3eeaba8a0137e05b275725743348542a",
    CAPACITY_VALIDATION: "09d90bd68e5eb4dfef24c71fccb957bcfdf6abcfeecf149538a0b35e273151d1",
    PRIMARY: "b9163683ec3a7aae99633b16899b3f80f53dd2b7c23cde30260120d233c091eb",
    SPEC: "3eedb8ddd0b0ada77236714135c5fa93092119eb5c118132e6d150d9106b98d5",
    PRODUCER: "e879f981c7a734bf9dc1730a6cef49c87d86e35538a403436bca37b46cf6b9d1",
    PRODUCTION: "a3fae448bc62a753a987066fb8c4c7275b750627c00b51d8d7c32d4d6e3016fc",
    EVENTS: "41f8b517419d2215a97db9ce245c5639f383b11c41d8c1377a245dea8e37abf3",
    PRODUCTION_REPORT: "124a77430bc5c87cf50dbe7f3b8e9408da1729484887cd617ed41c15db4b99b9",
}
READINGS = ("ZL3b", "IT2a", "RF1b")
FIELDS = [
    "event_id", "edition", "source_group_id", "physical_event_key", "locus",
    "source_group_index", "source_group_count", "collapsed_page", "panel_page",
    "physical_folio", "section", "currier", "paragraph_id", "paragraph_number",
    "line_index_side", "line_count_side", "line_fraction", "line_quartile",
    "group_index_line", "group_count_line", "group_fraction", "masked_template",
    "primary_query", "common_primary_query",
]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def render(rows: list[dict]) -> bytes:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=FIELDS, delimiter="\t", lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue().encode("utf-8")


def main() -> None:
    if OUT.exists() or REPORT.exists():
        raise SystemExit("refusing to overwrite masked-universe validation")
    checks = 0

    def require(condition: bool, label: str) -> None:
        nonlocal checks
        checks += 1
        if not condition:
            raise AssertionError(label)

    for path, expected in HASHES.items():
        require(sha(path) == expected, f"hash {path.name}")
    require(json.loads(SEPARATOR_VALIDATION.read_text())["status"] == "PASS_INDEPENDENT_SOURCE_SEPARATOR_RECONSTRUCTION", "separator validation")
    require(json.loads(ALIGNMENT_VALIDATION.read_text())["status"] == "PASS_INDEPENDENT_SOURCE_STA_ALIGNMENT_RECONSTRUCTION", "alignment validation")
    require(json.loads(CAPACITY_VALIDATION.read_text())["status"] == "PASS_INDEPENDENT_SCORE_BLIND_SCOPE_CAPACITY_RECONSTRUCTION", "capacity validation")

    with SEPARATORS.open(encoding="utf-8", newline="") as handle:
        metadata_rows = list(csv.DictReader(handle, delimiter="\t"))
    metadata = {}
    for row in metadata_rows:
        require(row["source_group_id"] not in metadata, "unique source group")
        metadata[row["source_group_id"]] = row

    panel_lines: dict[str, list[tuple[int, str, bool, str]]] = defaultdict(list)
    for row in metadata_rows:
        if row["edition"] == "ZL3b" and row["source_group_index"] == "1" and row["grammar_scope"] == "CONFIRMED_PROSE" and row["kind"] == "P":
            side = re.match(r"f\d+[rv]", row["page"])
            if side:
                panel_lines[row["page"]].append((int(row["source_row_index"]), row["locus"], row["paragraph_start"] == "1", side.group()))
    owner = {}
    side_lines: dict[str, list[tuple[int, str]]] = defaultdict(list)
    paragraphs = set()
    for panel in sorted(panel_lines):
        paragraph_number = 0
        for panel_index, (order, locus, starts, side) in enumerate(sorted(panel_lines[panel]), 1):
            if starts or paragraph_number == 0:
                paragraph_number += 1
            require(locus not in owner, "unique line owner")
            paragraph = f"{panel}|P{paragraph_number:03d}"
            owner[locus] = (side, panel, paragraph, paragraph_number, panel_index, order)
            paragraphs.add(paragraph)
            side_lines[side].append((order, locus))
    require(len(panel_lines) == 196 and len(owner) == 4024 and len(paragraphs) == 709, "scaffold totals")

    coordinates = {}
    for side, values in side_lines.items():
        ordered = sorted(values)
        for index, (_, locus) in enumerate(ordered):
            coordinates[locus] = (
                index + 1, len(ordered), f"{(index + 0.5) / len(ordered):.12f}",
                min(3, 4 * index // len(ordered)),
            )

    with PRIMARY.open(encoding="utf-8", newline="") as handle:
        primary_rows = list(csv.DictReader(handle, delimiter="\t"))
    primary_ids = {row["query_id"] for row in primary_rows}
    common_keys = {row["physical_query_key"] for row in primary_rows if row["common_all_three"] == "1"}
    require(len(primary_ids) == 1503 and len(common_keys) == 350, "primary binding")

    reconstructed = []
    with ALIGNMENT.open(encoding="utf-8", newline="") as handle:
        for aligned in csv.DictReader(handle, delimiter="\t"):
            if aligned["edition"] not in READINGS or aligned["alternative_site_count"] != "0":
                continue
            meta = metadata.get(aligned["source_group_id"])
            if meta is None or meta["locus"] not in owner:
                continue
            projection = aligned["nearest_basic_eva_primary"]
            if re.fullmatch(r"[a-z]+", projection) is None:
                continue
            if len(re.findall(r"(?:ch|sh)[oe]", projection)) != 1:
                continue
            masked = re.sub(r"((?:ch|sh))[oe]", r"\1X", projection)
            side, panel, paragraph, paragraph_number, panel_index, order = owner[meta["locus"]]
            physical = re.match(r"f\d+", side)
            require(physical is not None, "physical folio")
            group_index = int(aligned["source_group_index"])
            group_count = int(aligned["source_group_count"])
            physical_key = f"{meta['locus']}|G{group_index:03d}|{masked}"
            event_id = f"{aligned['edition']}|{meta['locus']}|G{group_index:03d}"
            line_index, line_count, line_fraction, quartile = coordinates[meta["locus"]]
            reconstructed.append({
                "event_id": event_id, "edition": aligned["edition"],
                "source_group_id": aligned["source_group_id"],
                "physical_event_key": physical_key, "locus": meta["locus"],
                "source_group_index": group_index, "source_group_count": group_count,
                "collapsed_page": side, "panel_page": panel,
                "physical_folio": physical.group(), "section": meta["section"],
                "currier": meta["currier"], "paragraph_id": paragraph,
                "paragraph_number": paragraph_number, "line_index_side": line_index,
                "line_count_side": line_count, "line_fraction": line_fraction,
                "line_quartile": quartile, "group_index_line": group_index,
                "group_count_line": group_count,
                "group_fraction": f"{(group_index - 0.5) / group_count:.12f}",
                "masked_template": masked, "primary_query": int(event_id in primary_ids),
                "common_primary_query": int(physical_key in common_keys and event_id in primary_ids),
            })
    reconstructed.sort(key=lambda row: (row["edition"], row["event_id"]))
    require(len({row["event_id"] for row in reconstructed}) == len(reconstructed), "event uniqueness")
    require(render(reconstructed) == EVENTS.read_bytes(), "event bytes")

    counts = {edition: sum(row["edition"] == edition for row in reconstructed) for edition in READINGS}
    require(counts == {"ZL3b": 9983, "IT2a": 10124, "RF1b": 10053}, "event counts")
    require(sum(row["primary_query"] for row in reconstructed) == 1503, "query count")
    require(sum(row["common_primary_query"] for row in reconstructed) == 1050, "common reading rows")
    for row in reconstructed:
        require(row["masked_template"].count("X") == 1, "one masked site")
        require(row["primary_query"] in (0, 1) and row["common_primary_query"] in (0, 1), "binary flags")

    production = json.loads(PRODUCTION.read_text())
    require(production["status"] == "PASS_COMPLETE_MASKED_SCOPE_UNIVERSE", "status")
    require(production["inputs"] == {path.name: sha(path) for path in (SEPARATORS, SEPARATOR_VALIDATION, ALIGNMENT, ALIGNMENT_VALIDATION, CAPACITY, CAPACITY_VALIDATION, SPEC, PRODUCER, PRIMARY)}, "inputs")
    require(production["event_counts"] == counts, "stored counts")
    require(production["events_total"] == len(reconstructed), "stored total")
    require(production["primary_queries"] == 1503 and production["common_primary_query_rows"] == 1050 and production["common_primary_physical_keys"] == 350, "stored query counts")
    require(production["events_sha256"] == sha(EVENTS), "stored event hash")
    require(production["schema"] == FIELDS, "schema")
    forbidden = {"outcome", "target_value", "raw_surface", "surface", "page_state", "score", "effect", "p_value", "english_gloss"}
    require(not forbidden.intersection(FIELDS), "forbidden schema fields")
    require(production["target_outcomes_stored"] == production["target_scores_computed"] == production["english_glosses"] == 0, "zero target outputs")
    require(all(production["gates"].values()), "gates")

    expected_report = f"""# `cho/che` masked scope universe

Status: **{production['status']}**

The outcome-masked universe contains **{len(reconstructed):,}** strict events:
**{counts['ZL3b']:,}** ZL, **{counts['IT2a']:,}** IT, and
**{counts['RF1b']:,}** RF. It reproduces all **1,503** frozen primary-query
rows and **350** common physical query keys. The selected site's `o/e` value,
unmasked surface, page state, score, effect, p-value, and English gloss are not
stored.

This artifact authorizes synthetic calibration only. It establishes no local
effect, authorial paragraph, sound, word, language, cipher operation, meaning,
plaintext, or translation.
"""
    require(PRODUCTION_REPORT.read_text() == expected_report, "report bytes")

    result = {
        "experiment": "CHO_CHE_SCOPE_MASKED_UNIVERSE_VALIDATION",
        "status": "PASS_INDEPENDENT_COMPLETE_MASKED_UNIVERSE_RECONSTRUCTION",
        "checks": checks,
        "validator_sha256": sha(VALIDATOR),
        "production_sha256": sha(PRODUCTION),
        "events_sha256": sha(EVENTS),
        "reconstructed": {"events": len(reconstructed), "event_counts": counts, "primary_queries": 1503, "common_physical_keys": 350},
        "target_outcomes_stored": 0,
        "target_scores_computed": 0,
        "failures": [],
        "claim_ceiling": production["claim_ceiling"],
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    REPORT.write_text(f"""# `cho/che` masked scope universe validation

Status: **{result['status']}**

A nonimporting implementation reconstructed all **{len(reconstructed):,}**
masked event rows, their line/group coordinates, the complete primary-query
binding, exact TSV and report bytes, and the zero-outcome schema in
**{checks:,}** checks. This validates synthetic-calibration geometry only; no
scope, language, meaning, plaintext, or translation follows.
""")
    print(json.dumps({"status": result["status"], "checks": checks}, sort_keys=True))


if __name__ == "__main__":
    main()
