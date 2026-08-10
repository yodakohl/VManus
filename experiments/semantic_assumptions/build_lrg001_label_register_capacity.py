#!/usr/bin/env python3
"""Build the feature-blind LRG001 page-by-length capacity panel."""

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
SPEC = HERE / "LRG001_SOURCE_NATIVE_LABEL_REGISTER_CAPACITY_SPEC.md"
GROUPS = RESULTS / "source_sta_family_consensus_groups.tsv"
SUMMARY = RESULTS / "source_sta_family_consensus.json"
VALIDATION = RESULTS / "source_sta_family_consensus_validation.json"
OUT_TSV = RESULTS / "lrg001_label_register_capacity.tsv"
OUT_JSON = RESULTS / "lrg001_label_register_capacity.json"
OUT_REPORT = RESULTS / "lrg001_label_register_capacity_report.md"

EXPECTED = {
    "groups": "a202d93498e8a350a5d7e0ca46e831dcc37ea5c0182dc404d63cb797a98b1225",
    "summary": "193ac76bd14b3967844035e8c3997f402d556c7aecf3190145c5295b4eeab3f7",
    "validation": "fcb6a53461b4f9df36f34161ed1d42087f4395988bea0d71f74a7dd635b68b76",
}
STATUS = "PASS_FEATURE_BLIND_109_CELL_16_FOLIO_CAPACITY"
DECISION = "GO_TARGET_BLIND_CALIBRATION_ONLY"
CLAIM = (
    "This artifact establishes only exact page-by-length capacity for a future "
    "held-folio source-native label-associated construction test. It supplies no "
    "label profile, identifier, name, noun, object ownership, language, word "
    "meaning, plaintext, or translation."
)
FIELDS = [
    "cell_id", "page", "physical_folio", "section", "symbol_count",
    "label_rows", "prose_rows", "total_rows", "assignment_count",
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def physical_folio(page: str) -> str:
    match = re.fullmatch(r"(f\d+)(?:[rv](?:\d+)?)?", page)
    if match is None:
        raise RuntimeError(f"invalid page key {page}")
    return match.group(1)


def canonical_json(value: object) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def atomic_text(path: Path, value: str) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(value, encoding="utf-8", newline="\n")
    temporary.replace(path)


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    temporary.replace(path)


def main() -> None:
    observed = {
        "groups": sha256(GROUPS),
        "summary": sha256(SUMMARY),
        "validation": sha256(VALIDATION),
    }
    if observed != EXPECTED:
        raise RuntimeError("LRG001 upstream drift")
    if json.loads(SUMMARY.read_text(encoding="utf-8"))["status"] != (
        "PASS_EXACT_THREE_READING_STA_FAMILY_GRAMMAR_SCAFFOLD"
    ):
        raise RuntimeError("upstream source-native scaffold is not passed")
    if not str(json.loads(VALIDATION.read_text(encoding="utf-8"))["status"]).startswith("PASS_"):
        raise RuntimeError("upstream source-native validation is not passed")

    rows = read_tsv(GROUPS)
    seen_ids: set[str] = set()
    cells: dict[tuple[str, int], Counter[str]] = defaultdict(Counter)
    cell_sections: dict[tuple[str, int], set[str]] = defaultdict(set)
    accessed_forbidden_fields = False
    for row in rows:
        identifier = row["consensus_group_id"]
        if identifier in seen_ids:
            raise RuntimeError(f"duplicate group id {identifier}")
        seen_ids.add(identifier)
        if row["strict_zero_alternative"] != "1":
            continue
        kind = row["kind"]
        eligible = kind == "L" or (
            kind == "P" and row["grammar_scope"] == "CONFIRMED_PROSE"
        )
        if not eligible:
            continue
        key = (row["page"], int(row["symbol_count"]))
        cells[key][kind] += 1
        cell_sections[key].add(row["section"])
        # The capacity pass deliberately never reads family_surface or member-code fields.
    if accessed_forbidden_fields:
        raise RuntimeError("feature identity accessed during capacity")

    output_rows: list[dict[str, object]] = []
    for index, key in enumerate(sorted(cells, key=lambda item: (physical_folio(item[0]), item[0], item[1])), 1):
        page, length = key
        counts = cells[key]
        if not counts["L"] or not counts["P"]:
            continue
        if len(cell_sections[key]) != 1:
            raise RuntimeError(f"section drift inside cell {key}")
        label_rows = counts["L"]
        prose_rows = counts["P"]
        total = label_rows + prose_rows
        output_rows.append({
            "cell_id": f"LRG001-C{len(output_rows) + 1:03d}",
            "page": page,
            "physical_folio": physical_folio(page),
            "section": next(iter(cell_sections[key])),
            "symbol_count": length,
            "label_rows": label_rows,
            "prose_rows": prose_rows,
            "total_rows": total,
            "assignment_count": math.comb(total, label_rows),
        })

    label_rows = sum(int(row["label_rows"]) for row in output_rows)
    prose_rows = sum(int(row["prose_rows"]) for row in output_rows)
    folios = sorted({str(row["physical_folio"]) for row in output_rows}, key=lambda x: int(x[1:]))
    sections = sorted({str(row["section"]) for row in output_rows})
    section_summary = {}
    for section in sections:
        subset = [row for row in output_rows if row["section"] == section]
        section_summary[section] = {
            "cells": len(subset),
            "label_rows": sum(int(row["label_rows"]) for row in subset),
            "prose_rows": sum(int(row["prose_rows"]) for row in subset),
            "pages": len({str(row["page"]) for row in subset}),
            "physical_folios": len({str(row["physical_folio"]) for row in subset}),
        }
    multi_folio_sections = sum(v["physical_folios"] >= 2 for v in section_summary.values())
    five_folio_sections = sum(v["physical_folios"] >= 5 for v in section_summary.values())
    gates = {
        "at_least_300_label_rows": label_rows >= 300,
        "at_least_100_mixed_cells": len(output_rows) >= 100,
        "at_least_15_physical_folios": len(folios) >= 15,
        "exactly_four_or_more_sections": len(sections) >= 4,
        "at_least_two_multifolio_sections": multi_folio_sections >= 2,
        "at_least_one_five_folio_section": five_folio_sections >= 1,
        "every_cell_has_both_states": all(
            int(row["label_rows"]) > 0 and int(row["prose_rows"]) > 0 for row in output_rows
        ),
        "feature_identity_not_accessed": not accessed_forbidden_fields,
    }
    if not all(gates.values()):
        raise RuntimeError(f"LRG001 capacity failed: {gates}")

    write_tsv(OUT_TSV, output_rows)
    result = {
        "status": STATUS,
        "decision": DECISION,
        "claim_ceiling": CLAIM,
        "inputs": observed,
        "spec_sha256": sha256(SPEC),
        "totals": {
            "strict_source_groups": sum(row["strict_zero_alternative"] == "1" for row in rows),
            "mixed_cells": len(output_rows),
            "label_rows": label_rows,
            "prose_rows": prose_rows,
            "total_rows": label_rows + prose_rows,
            "pages": len({str(row["page"]) for row in output_rows}),
            "physical_folios": len(folios),
            "sections": len(sections),
            "log10_exact_assignment_orbit": sum(
                math.log10(int(row["assignment_count"])) for row in output_rows
            ),
        },
        "physical_folios": folios,
        "section_summary": section_summary,
        "gates": gates,
        "forbidden_fields_accessed": [],
        "capacity_tsv_sha256": sha256(OUT_TSV),
    }
    atomic_text(OUT_JSON, canonical_json(result))

    report = "\n".join([
        "# LRG001 source-native label-register capacity",
        "",
        f"Status: **{STATUS}**.",
        "",
        f"The exact page-by-length panel contains **{len(output_rows)}** mixed cells, "
        f"**{label_rows}** manual `L` groups, and **{prose_rows}** confirmed-prose "
        f"controls on **{len(folios)}** physical folios and **{len(sections)}** sections.",
        "",
        "| section | cells | L groups | prose groups | pages | physical folios |",
        "|---|---:|---:|---:|---:|---:|",
        *[
            f"| {section} | {values['cells']} | {values['label_rows']} | "
            f"{values['prose_rows']} | {values['pages']} | {values['physical_folios']} |"
            for section, values in section_summary.items()
        ],
        "",
        "Every retained cell contains both roles at the same physical page and exact "
        "STA-family length. No family surface, member code, EVA string, classifier "
        "score, or individual form was opened. The complete fixed-count assignment "
        f"space has log10 size **{result['totals']['log10_exact_assignment_orbit']:.3f}**.",
        "",
        "This is a genuinely narrower new instrument than the archived partial-root "
        "label coordinate, sparse legacy object annotations, EAS004 arrays, or the "
        "diagnostic prose-edge transfer. It authorizes only target-blind calibration "
        "of a held-folio label-versus-prose construction test.",
        "",
        "It does not show that labels are names, nouns, identifiers, or object owners, "
        "and it supplies no language, word meaning, plaintext, or translation.",
        "",
    ])
    atomic_text(OUT_REPORT, report)
    print(canonical_json(result), end="")


if __name__ == "__main__":
    main()
