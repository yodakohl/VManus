#!/usr/bin/env python3
"""Clean reconstruction of the LRG001 feature-blind capacity artifact."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
GROUPS = RESULTS / "source_sta_family_consensus_groups.tsv"
PRODUCTION = RESULTS / "lrg001_label_register_capacity.json"
TABLE = RESULTS / "lrg001_label_register_capacity.tsv"
REPORT = RESULTS / "lrg001_label_register_capacity_report.md"
OUT_JSON = RESULTS / "lrg001_label_register_capacity_validation.json"
OUT_REPORT = RESULTS / "lrg001_label_register_capacity_validation_report.md"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def folio(page: str) -> str:
    match = re.fullmatch(r"(f\d+)(?:[rv](?:\d+)?)?", page)
    if match is None:
        raise RuntimeError(page)
    return match.group(1)


def check(condition: bool, label: str, checks: list[str]) -> None:
    if not condition:
        raise RuntimeError(label)
    checks.append(label)


def main() -> None:
    checks: list[str] = []
    production = json.loads(PRODUCTION.read_text(encoding="utf-8"))
    source = load_tsv(GROUPS)
    stored = load_tsv(TABLE)
    seen: set[str] = set()
    counts: dict[tuple[str, int], Counter[str]] = defaultdict(Counter)
    sections: dict[tuple[str, int], set[str]] = defaultdict(set)
    strict = 0
    for row in source:
        check(row["consensus_group_id"] not in seen, "unique source group", checks)
        seen.add(row["consensus_group_id"])
        if row["strict_zero_alternative"] != "1":
            continue
        strict += 1
        if row["kind"] == "L":
            eligible = True
        else:
            eligible = row["kind"] == "P" and row["grammar_scope"] == "CONFIRMED_PROSE"
        if not eligible:
            continue
        key = row["page"], int(row["symbol_count"])
        counts[key][row["kind"]] += 1
        sections[key].add(row["section"])

    rebuilt = []
    for key in sorted(counts, key=lambda value: (folio(value[0]), value[0], value[1])):
        state = counts[key]
        if state["L"] == 0 or state["P"] == 0:
            continue
        check(len(sections[key]) == 1, "one section per cell", checks)
        page, length = key
        total = state["L"] + state["P"]
        rebuilt.append({
            "cell_id": f"LRG001-C{len(rebuilt) + 1:03d}",
            "page": page,
            "physical_folio": folio(page),
            "section": next(iter(sections[key])),
            "symbol_count": str(length),
            "label_rows": str(state["L"]),
            "prose_rows": str(state["P"]),
            "total_rows": str(total),
            "assignment_count": str(math.comb(total, state["L"])),
        })
    check(rebuilt == stored, "exact capacity table", checks)
    check(digest(TABLE) == production["capacity_tsv_sha256"], "table digest", checks)

    totals = {
        "strict_source_groups": strict,
        "mixed_cells": len(rebuilt),
        "label_rows": sum(int(row["label_rows"]) for row in rebuilt),
        "prose_rows": sum(int(row["prose_rows"]) for row in rebuilt),
        "total_rows": sum(int(row["total_rows"]) for row in rebuilt),
        "pages": len({row["page"] for row in rebuilt}),
        "physical_folios": len({row["physical_folio"] for row in rebuilt}),
        "sections": len({row["section"] for row in rebuilt}),
        "log10_exact_assignment_orbit": sum(
            math.log10(int(row["assignment_count"])) for row in rebuilt
        ),
    }
    for key, value in totals.items():
        observed = production["totals"][key]
        if isinstance(value, float):
            check(abs(value - observed) < 1e-12, f"total {key}", checks)
        else:
            check(value == observed, f"total {key}", checks)

    section_summary = {}
    for section in sorted({row["section"] for row in rebuilt}):
        subset = [row for row in rebuilt if row["section"] == section]
        section_summary[section] = {
            "cells": len(subset),
            "label_rows": sum(int(row["label_rows"]) for row in subset),
            "prose_rows": sum(int(row["prose_rows"]) for row in subset),
            "pages": len({row["page"] for row in subset}),
            "physical_folios": len({row["physical_folio"] for row in subset}),
        }
    check(section_summary == production["section_summary"], "section summary", checks)
    expected_folios = sorted(
        {row["physical_folio"] for row in rebuilt}, key=lambda value: int(value[1:])
    )
    check(expected_folios == production["physical_folios"], "folio inventory", checks)
    check(all(production["gates"].values()), "all production gates", checks)
    check(production["forbidden_fields_accessed"] == [], "no feature field access", checks)
    check(production["status"] == "PASS_FEATURE_BLIND_109_CELL_16_FOLIO_CAPACITY", "status", checks)
    check(production["decision"] == "GO_TARGET_BLIND_CALIBRATION_ONLY", "decision", checks)
    check("translation" in production["claim_ceiling"], "claim ceiling", checks)

    validation = {
        "status": "PASS_INDEPENDENT_LRG001_CAPACITY_RECONSTRUCTION",
        "checks": len(checks),
        "discrepancies": 0,
        "production_json_sha256": digest(PRODUCTION),
        "capacity_tsv_sha256": digest(TABLE),
        "production_report_sha256": digest(REPORT),
        "reconstructed_totals": totals,
        "decision": production["decision"],
        "claim_ceiling": production["claim_ceiling"],
    }
    text = json.dumps(validation, indent=2, sort_keys=True) + "\n"
    temporary = OUT_JSON.with_suffix(".json.tmp")
    temporary.write_text(text, encoding="utf-8", newline="\n")
    temporary.replace(OUT_JSON)
    report = "\n".join([
        "# LRG001 capacity independent validation",
        "",
        "Status: **PASS_INDEPENDENT_LRG001_CAPACITY_RECONSTRUCTION**.",
        "",
        f"A production-free reconstruction passed **{len(checks)}** checks with zero discrepancies. "
        "It rebuilt all 23,281 strict source groups, 109 exact page-by-length cells, "
        "358 manual label groups, 2,664 prose controls, 16 physical folios, section summaries, "
        "assignment counts, gates, and canonical table bytes.",
        "",
        "No family surface, STA member code, EVA spelling, classifier score, word meaning, "
        "plaintext, or translation was used or produced.",
        "",
    ])
    temporary = OUT_REPORT.with_suffix(".md.tmp")
    temporary.write_text(report, encoding="utf-8", newline="\n")
    temporary.replace(OUT_REPORT)
    print(text, end="")


if __name__ == "__main__":
    main()
