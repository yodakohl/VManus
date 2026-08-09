#!/usr/bin/env python3
"""Build the complete outcome-masked cho/che scope event universe."""

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
BUILDER = Path(__file__).resolve()
OUT = RESULTS / "cho_che_scope_masked_universe.json"
EVENTS = RESULTS / "cho_che_scope_masked_events.tsv"
REPORT = RESULTS / "cho_che_scope_masked_universe_report.md"

FROZEN = {
    SEPARATORS: "4b649c8290d5afc7a5fbcc8e98db2bc123a1ceb5f3858d3befa781ce96b680f0",
    SEPARATOR_VALIDATION: "8698a2643219fd8ab00b05bba8705a1f1e8219c9b468824fbe2dc92117043deb",
    ALIGNMENT: "f23654f1d4c854db6d458b418a0d3530115731604854cf0a0495565e58341840",
    ALIGNMENT_VALIDATION: "cc53d32646b21e4135f0b23d98662e10835307ad860d021ea8c487261d7646fd",
    CAPACITY: "92ed820e81d289d9897259405ec5369c3eeaba8a0137e05b275725743348542a",
    CAPACITY_VALIDATION: "09d90bd68e5eb4dfef24c71fccb957bcfdf6abcfeecf149538a0b35e273151d1",
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


def table_bytes(rows: list[dict]) -> bytes:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=FIELDS, delimiter="\t", lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue().encode("utf-8")


def main() -> None:
    if any(path.exists() for path in (OUT, EVENTS, REPORT)):
        raise SystemExit("refusing to overwrite masked scope universe")
    for path, expected in FROZEN.items():
        if sha(path) != expected:
            raise SystemExit(f"frozen input mismatch: {path.name}")
    if json.loads(SEPARATOR_VALIDATION.read_text())["status"] != "PASS_INDEPENDENT_SOURCE_SEPARATOR_RECONSTRUCTION":
        raise SystemExit("separator validation is not PASS")
    if json.loads(ALIGNMENT_VALIDATION.read_text())["status"] != "PASS_INDEPENDENT_SOURCE_STA_ALIGNMENT_RECONSTRUCTION":
        raise SystemExit("alignment validation is not PASS")
    if json.loads(CAPACITY_VALIDATION.read_text())["status"] != "PASS_INDEPENDENT_SCORE_BLIND_SCOPE_CAPACITY_RECONSTRUCTION":
        raise SystemExit("capacity validation is not PASS")

    with SEPARATORS.open(encoding="utf-8", newline="") as handle:
        metadata_rows = list(csv.DictReader(handle, delimiter="\t"))
    metadata = {row["source_group_id"]: row for row in metadata_rows}
    if len(metadata) != len(metadata_rows):
        raise ValueError("duplicate source group ID")

    panel_lines: dict[str, list[tuple[int, str, bool, str]]] = defaultdict(list)
    for row in metadata_rows:
        if row["edition"] != "ZL3b" or row["source_group_index"] != "1":
            continue
        if row["grammar_scope"] != "CONFIRMED_PROSE" or row["kind"] != "P":
            continue
        side = re.match(r"f\d+[rv]", row["page"])
        if side:
            panel_lines[row["page"]].append((
                int(row["source_row_index"]), row["locus"],
                row["paragraph_start"] == "1", side.group(),
            ))

    ownership = {}
    side_lines: dict[str, list[tuple[int, str]]] = defaultdict(list)
    for panel, lines in sorted(panel_lines.items()):
        paragraph_number = 0
        panel_index = 0
        for order, locus, starts, side in sorted(lines):
            panel_index += 1
            if starts or paragraph_number == 0:
                paragraph_number += 1
            if locus in ownership:
                raise ValueError("duplicate paragraph ownership")
            ownership[locus] = {
                "collapsed_page": side, "panel_page": panel,
                "paragraph_id": f"{panel}|P{paragraph_number:03d}",
                "paragraph_number": paragraph_number, "panel_line_index": panel_index,
                "source_row_index": order,
            }
            side_lines[side].append((order, locus))
    if len(panel_lines) != 196 or len(ownership) != 4024:
        raise ValueError("paragraph scaffold drift")

    line_coordinate = {}
    for side, values in side_lines.items():
        ordered = sorted(values)
        n = len(ordered)
        for index, (_, locus) in enumerate(ordered):
            line_coordinate[locus] = {
                "line_index_side": index + 1,
                "line_count_side": n,
                "line_fraction": f"{(index + 0.5) / n:.12f}",
                "line_quartile": min(3, 4 * index // n),
            }

    with PRIMARY.open(encoding="utf-8", newline="") as handle:
        primary_rows = list(csv.DictReader(handle, delimiter="\t"))
    primary_ids = {row["query_id"] for row in primary_rows}
    common_keys = {row["physical_query_key"] for row in primary_rows if row["common_all_three"] == "1"}
    if len(primary_ids) != 1503 or len(common_keys) != 350:
        raise ValueError("primary capacity binding drift")

    rows = []
    with ALIGNMENT.open(encoding="utf-8", newline="") as handle:
        for aligned in csv.DictReader(handle, delimiter="\t"):
            if aligned["edition"] not in READINGS or aligned["alternative_site_count"] != "0":
                continue
            meta = metadata.get(aligned["source_group_id"])
            if meta is None or meta["locus"] not in ownership:
                continue
            surface = aligned["nearest_basic_eva_primary"]
            if re.fullmatch(r"[a-z]+", surface) is None:
                continue
            sites = list(re.finditer(r"(?:ch|sh)[oe]", surface))
            if len(sites) != 1:
                continue
            masked = re.sub(r"((?:ch|sh))[oe]", r"\1X", surface)
            owner = ownership[meta["locus"]]
            side = owner["collapsed_page"]
            physical = re.match(r"f\d+", side)
            if physical is None:
                raise ValueError("physical folio parse failure")
            physical_key = f"{meta['locus']}|G{int(aligned['source_group_index']):03d}|{masked}"
            query_id = f"{aligned['edition']}|{meta['locus']}|G{int(aligned['source_group_index']):03d}"
            group_index = int(aligned["source_group_index"])
            group_count = int(aligned["source_group_count"])
            row = {
                "event_id": query_id,
                "edition": aligned["edition"],
                "source_group_id": aligned["source_group_id"],
                "physical_event_key": physical_key,
                "locus": meta["locus"],
                "source_group_index": group_index,
                "source_group_count": group_count,
                "collapsed_page": side,
                "panel_page": owner["panel_page"],
                "physical_folio": physical.group(),
                "section": meta["section"],
                "currier": meta["currier"],
                "paragraph_id": owner["paragraph_id"],
                "paragraph_number": owner["paragraph_number"],
                **line_coordinate[meta["locus"]],
                "group_index_line": group_index,
                "group_count_line": group_count,
                "group_fraction": f"{(group_index - 0.5) / group_count:.12f}",
                "masked_template": masked,
                "primary_query": int(query_id in primary_ids),
                "common_primary_query": int(physical_key in common_keys and query_id in primary_ids),
            }
            rows.append(row)
    rows.sort(key=lambda row: (row["edition"], row["event_id"]))
    if len({row["event_id"] for row in rows}) != len(rows):
        raise ValueError("duplicate event ID")
    counts = {edition: sum(row["edition"] == edition for row in rows) for edition in READINGS}
    if counts != {"ZL3b": 9983, "IT2a": 10124, "RF1b": 10053}:
        raise ValueError(f"strict event count drift: {counts}")
    if sum(row["primary_query"] for row in rows) != 1503:
        raise ValueError("primary query coverage drift")
    EVENTS.write_bytes(table_bytes(rows))

    result = {
        "experiment": "CHO_CHE_SCOPE_MASKED_UNIVERSE",
        "status": "PASS_COMPLETE_MASKED_SCOPE_UNIVERSE",
        "inputs": {path.name: sha(path) for path in (*FROZEN, SPEC, BUILDER, PRIMARY)},
        "event_counts": counts,
        "events_total": len(rows),
        "primary_queries": sum(row["primary_query"] for row in rows),
        "common_primary_query_rows": sum(row["common_primary_query"] for row in rows),
        "common_primary_physical_keys": len(common_keys),
        "events_sha256": sha(EVENTS),
        "schema": FIELDS,
        "target_outcomes_stored": 0,
        "target_scores_computed": 0,
        "english_glosses": 0,
        "gates": {
            "exact_event_counts": counts == {"ZL3b": 9983, "IT2a": 10124, "RF1b": 10053},
            "exact_primary_query_rows": sum(row["primary_query"] for row in rows) == 1503,
            "exact_common_query_keys": len(common_keys) == 350,
            "target_value_fields_absent": not ({"outcome", "target_value", "raw_surface", "surface", "page_state", "score", "effect", "p_value", "english_gloss"} & set(FIELDS)),
        },
        "claim_ceiling": (
            "Complete outcome-masked geometry for synthetic scope-test calibration only. "
            "No paragraph effect, authorial paragraph, sound, wordhood, language, cipher "
            "operation, meaning, plaintext, or translation follows."
        ),
    }
    if not all(result["gates"].values()):
        raise ValueError("masked universe gate failure")
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT.write_text(f"""# `cho/che` masked scope universe

Status: **{result['status']}**

The outcome-masked universe contains **{len(rows):,}** strict events:
**{counts['ZL3b']:,}** ZL, **{counts['IT2a']:,}** IT, and
**{counts['RF1b']:,}** RF. It reproduces all **1,503** frozen primary-query
rows and **350** common physical query keys. The selected site's `o/e` value,
unmasked surface, page state, score, effect, p-value, and English gloss are not
stored.

This artifact authorizes synthetic calibration only. It establishes no local
effect, authorial paragraph, sound, word, language, cipher operation, meaning,
plaintext, or translation.
""", encoding="utf-8")
    print(json.dumps({"status": result["status"], "counts": counts, "rows": len(rows)}, sort_keys=True))


if __name__ == "__main__":
    main()
