#!/usr/bin/env python3
"""Build the association-unopened LRG005 exact-D1-extension capacity panel."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import os
import re
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RESULTS = HERE / "results"
SPEC = HERE / "LRG005_D1_EXTENSION_CAPACITY_SPEC.md"
GROUPS = RESULTS / "source_sta_family_consensus_groups.tsv"
LRG001 = RESULTS / "lrg001_label_register_capacity.tsv"
LRG004 = RESULTS / "lrg004_initial_family_target.json"
LRG004_VALIDATION = RESULTS / "lrg004_initial_family_target_validation.json"
OUT_PANEL = RESULTS / "lrg005_d1_extension_capacity.tsv"
OUT_QUOTAS = RESULTS / "lrg005_d1_extension_quotas.tsv"
OUT_JSON = RESULTS / "lrg005_d1_extension_capacity.json"
OUT_REPORT = RESULTS / "lrg005_d1_extension_capacity_report.md"

EXPECTED = {
    "groups": "a202d93498e8a350a5d7e0ca46e831dcc37ea5c0182dc404d63cb797a98b1225",
    "lrg001": "abec3385838cf9218db34bda108288f680a9b8482c7b7e47d3fb83c711998536",
    "lrg004": "81da7ec6b1a69c9b19b8d18982905d21a441f63364e9555eddf08d333c3059bd",
    "lrg004_validation": "e9273c21f4b02762925672bf46110510b99ec68f0e1ff5ea3e350c40854e8532",
}
MEMBER_FIELDS = ("zl_sta_codes", "it_sta_codes", "rf_sta_codes")
PANEL_FIELDS = ("unit_id", "cell_id", "physical_folio", "section")
QUOTA_FIELDS = ("cell_id", "label_rows", "prose_rows", "total_rows")
STATUS = "PASS_ASSOCIATION_UNOPENED_EXACT_D1_EXTENSION_CAPACITY"
DECISION = "GO_TARGET_FREE_CALIBRATION_ONLY"
CLAIM = (
    "This establishes only capacity for a held-folio comparison of an exact "
    "D1-extended versus bare prose ratio inside the confirmed A-initial label "
    "register. No label/prose score contrast was computed, and no prefix, "
    "classifier, morpheme, word, POS, sound, meaning, plaintext, or translation follows."
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def table(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def physical_folio(page: str) -> str:
    match = re.fullmatch(r"(f\d+)(?:[rv](?:\d+)?)?", page)
    if match is None:
        raise RuntimeError(f"invalid page {page}")
    return match.group(1)


def exact_sequence(row: dict[str, str]) -> tuple[str, str, str]:
    values = tuple(row[field] for field in MEMBER_FIELDS)
    if any(not value or len(value.split()) != int(row["symbol_count"]) for value in values):
        raise RuntimeError("member sequence length drift")
    return values  # type: ignore[return-value]


def initial_triplet(row: dict[str, str]) -> tuple[str, str, str]:
    return tuple(value.split()[0] for value in exact_sequence(row))  # type: ignore[return-value]


def prepend_d1(sequence: tuple[str, str, str]) -> tuple[str, str, str]:
    return tuple("D1 " + value for value in sequence)  # type: ignore[return-value]


def opaque_unit(identifier: str) -> str:
    return "LRG005-U" + hashlib.sha256(("LRG005-D1|" + identifier).encode()).hexdigest()[:20]


def canonical_json(value: object) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def tsv_text(fields: tuple[str, ...], rows: list[dict[str, object]]) -> str:
    from io import StringIO
    handle = StringIO(newline="")
    writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return handle.getvalue()


def atomic_new(path: Path, value: str) -> None:
    if path.exists():
        raise RuntimeError(f"output exists {path.name}")
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(value, encoding="utf-8", newline="\n")
    os.link(temporary, path)
    temporary.unlink()


def main() -> None:
    outputs = (OUT_PANEL, OUT_QUOTAS, OUT_JSON, OUT_REPORT)
    if any(path.exists() for path in outputs):
        raise RuntimeError("capacity output exists")
    observed = {
        "groups": sha256(GROUPS), "lrg001": sha256(LRG001),
        "lrg004": sha256(LRG004), "lrg004_validation": sha256(LRG004_VALIDATION),
    }
    if observed != EXPECTED:
        raise RuntimeError("LRG005 input drift")
    lrg004 = json.loads(LRG004.read_text(encoding="utf-8"))
    registered = {(row["family"], row["direction"]) for row in lrg004["evaluation"]["registered"]}
    if registered != {("A", "POSITIVE"), ("D", "NEGATIVE")}:
        raise RuntimeError("LRG004 register drift")
    if not str(json.loads(LRG004_VALIDATION.read_text(encoding="utf-8"))["status"]).startswith("PASS_"):
        raise RuntimeError("LRG004 validation drift")

    eligible_lrg001 = {
        (row["page"], int(row["symbol_count"]))
        for row in table(LRG001) if row["section"] in {"B", "P"}
    }
    groups = table(GROUPS)
    if len(groups) != 26184 or len({row["consensus_group_id"] for row in groups}) != len(groups):
        raise RuntimeError("source group identity drift")
    candidates: list[tuple[dict[str, str], str, tuple[object, ...]]] = []
    for row in groups:
        if row["strict_zero_alternative"] != "1" or not row["family_surface"].startswith("A"):
            continue
        if (row["page"], int(row["symbol_count"])) not in eligible_lrg001:
            continue
        role = "L" if row["kind"] == "L" else (
            "P" if row["kind"] == "P" and row["grammar_scope"] == "CONFIRMED_PROSE" else ""
        )
        if not role:
            continue
        cell_key = (row["page"], int(row["symbol_count"]), initial_triplet(row))
        candidates.append((row, role, cell_key))
    by_cell: dict[tuple[object, ...], list[tuple[dict[str, str], str]]] = defaultdict(list)
    for row, role, key in candidates:
        by_cell[key].append((row, role))
    retained = {key: values for key, values in by_cell.items() if {role for _, role in values} == {"L", "P"}}

    prose = [
        row for row in groups
        if row["strict_zero_alternative"] == "1"
        and row["kind"] == "P" and row["grammar_scope"] == "CONFIRMED_PROSE"
    ]
    by_folio_sequence: Counter[tuple[str, tuple[str, str, str]]] = Counter(
        (physical_folio(row["page"]), exact_sequence(row)) for row in prose
    )
    total_sequence: Counter[tuple[str, str, str]] = Counter()
    for (_, sequence), count in by_folio_sequence.items():
        total_sequence[sequence] += count
    if sum(by_folio_sequence.values()) != len(prose) or sum(total_sequence.values()) != len(prose):
        raise RuntimeError("background count reconstruction")

    ordered_keys = sorted(retained, key=lambda key: (physical_folio(str(key[0])), str(key[0]), int(key[1]), key[2]))
    panel_rows: list[dict[str, object]] = []
    quota_rows: list[dict[str, object]] = []
    cell_scores: dict[str, list[float]] = {}
    extension_support = bare_support = both_support = 0
    label_total = prose_total = 0
    seen_units: set[str] = set()
    for cell_number, key in enumerate(ordered_keys, 1):
        cell_id = f"LRG005-C{cell_number:03d}"
        values = sorted(retained[key], key=lambda item: opaque_unit(item[0]["consensus_group_id"]))
        roles = Counter(role for _, role in values)
        quota_rows.append({
            "cell_id": cell_id, "label_rows": roles["L"], "prose_rows": roles["P"],
            "total_rows": len(values),
        })
        label_total += roles["L"]
        prose_total += roles["P"]
        scores: list[float] = []
        for row, _role in values:
            unit = opaque_unit(row["consensus_group_id"])
            if unit in seen_units:
                raise RuntimeError("opaque unit collision")
            seen_units.add(unit)
            folio = physical_folio(row["page"])
            sequence = exact_sequence(row)
            extended = prepend_d1(sequence)
            bare_count = total_sequence[sequence] - by_folio_sequence[folio, sequence]
            extended_count = total_sequence[extended] - by_folio_sequence[folio, extended]
            if bare_count < 0 or extended_count < 0:
                raise RuntimeError("negative held-folio count")
            score = math.log((extended_count + 0.5) / (bare_count + 0.5))
            if not math.isfinite(score):
                raise RuntimeError("nonfinite capacity score")
            scores.append(score)
            extension_support += extended_count > 0
            bare_support += bare_count > 0
            both_support += extended_count > 0 and bare_count > 0
            panel_rows.append({
                "unit_id": unit, "cell_id": cell_id, "physical_folio": folio,
                "section": row["section"],
            })
        cell_scores[cell_id] = scores

    variable_cells = {
        cell for cell, scores in cell_scores.items() if max(scores) - min(scores) > 1e-12
    }
    quota_by_cell = {row["cell_id"]: row for row in quota_rows}
    variable_rows = sum(int(quota_by_cell[cell]["total_rows"]) for cell in variable_cells)
    variable_sections = Counter(
        next(str(row["section"]) for row in panel_rows if row["cell_id"] == cell)
        for cell in variable_cells
    )
    variable_folios = {
        str(row["physical_folio"]) for row in panel_rows if row["cell_id"] in variable_cells
    }
    unique_scores = len({score for scores in cell_scores.values() for score in scores})
    gates = {
        "at_least_500_rows": len(panel_rows) >= 500,
        "at_least_60_cells": len(quota_rows) >= 60,
        "exactly_13_physical_folios": len({row["physical_folio"] for row in panel_rows}) == 13,
        "at_least_100_label_rows": label_total >= 100,
        "at_least_300_prose_rows": prose_total >= 300,
        "at_least_50_variable_cells": len(variable_cells) >= 50,
        "at_least_500_rows_in_variable_cells": variable_rows >= 500,
        "at_least_300_rows_with_extension_support": extension_support >= 300,
        "at_least_25_variable_cells_each_B_P": min(variable_sections["B"], variable_sections["P"]) >= 25,
        "no_role_or_sequence_in_masked_panel": set(PANEL_FIELDS) == {"unit_id", "cell_id", "physical_folio", "section"},
        "association_not_computed": True,
    }
    if not all(gates.values()):
        raise RuntimeError(f"LRG005 capacity failure {gates}")

    panel_text = tsv_text(PANEL_FIELDS, panel_rows)
    quota_text = tsv_text(QUOTA_FIELDS, quota_rows)
    result = {
        "status": STATUS, "decision": DECISION, "claim_ceiling": CLAIM,
        "inputs": observed, "spec_sha256": sha256(SPEC),
        "counts": {
            "source_groups": len(groups), "strict_confirmed_prose_background": len(prose),
            "rows": len(panel_rows), "label_rows_aggregate_only": label_total,
            "prose_rows_aggregate_only": prose_total, "cells": len(quota_rows),
            "physical_folios": len({row["physical_folio"] for row in panel_rows}),
            "sections": dict(Counter(str(row["section"]) for row in panel_rows)),
            "initial_member_triplet_states": len({key[2] for key in retained}),
            "unique_held_folio_scores": unique_scores,
            "rows_with_extension_support": extension_support,
            "rows_with_bare_support": bare_support, "rows_with_both_support": both_support,
            "variable_cells": len(variable_cells), "rows_in_variable_cells": variable_rows,
            "folios_with_variable_cells": len(variable_folios),
            "variable_cells_by_section": dict(sorted(variable_sections.items())),
        },
        "gates": gates, "label_prose_score_contrast_computed": False,
        "forbidden_outputs": {"locus": False, "page": False, "surface": False,
                              "family_sequence": False, "member_code": False,
                              "score": False, "row_role": False},
    }
    atomic_new(OUT_PANEL, panel_text)
    try:
        atomic_new(OUT_QUOTAS, quota_text)
        result["panel_sha256"] = sha256(OUT_PANEL)
        result["quotas_sha256"] = sha256(OUT_QUOTAS)
        atomic_new(OUT_JSON, canonical_json(result))
        report = "\n".join([
            "# LRG005 exact D1-extension capacity", "", f"Status: **{STATUS}**.", "",
            f"Exact page, length, and first-member conditioning retains **{len(panel_rows)}** A-initial rows in **{len(quota_rows)}** mixed cells on **13** physical folios (**{label_total}** label / **{prose_total}** prose aggregate quotas).",
            "",
            f"The label-blind held-folio D1-extension ratio has **{unique_scores}** distinct values. It varies in **{len(variable_cells)}** cells containing **{variable_rows}** rows on all **{len(variable_folios)}** folios; **{extension_support}** rows have held-folio extension support and **{both_support}** have both extended and bare support.",
            "",
            "No label-versus-prose score contrast was computed. The public panel emits no locus, page, sequence, member code, score, or row role.",
            "",
            "Decision: **GO_TARGET_FREE_CALIBRATION_ONLY**.", "",
            "This is capacity for one new cross-register transformed-counterpart test. It supplies no prefix, classifier, morpheme, word, POS, sound, meaning, plaintext, or translation.", "",
        ])
        atomic_new(OUT_REPORT, report)
    except Exception:
        for path in outputs:
            path.unlink(missing_ok=True)
        raise
    print(canonical_json(result), end="")


if __name__ == "__main__":
    main()
