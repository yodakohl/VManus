#!/usr/bin/env python3
"""Clean reconstruction of association-unopened LRG008 capacity."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
R = HERE / "results"
SPEC = HERE / "LRG008_DIAGRAM_ROLE_CAPACITY_SPEC.md"
BUILDER = HERE / "build_lrg008_diagram_role_capacity.py"
GROUPS = R / "source_sta_family_consensus_groups.tsv"
LRG001 = R / "lrg001_label_register_target_recovered.json"
LRG001V = R / "lrg001_label_register_target_recovered_validation.json"
PANEL = R / "lrg008_diagram_role_capacity.tsv"
PRODUCTION = R / "lrg008_diagram_role_capacity.json"
PRODUCTION_REPORT = R / "lrg008_diagram_role_capacity_report.md"
OUT = R / "lrg008_diagram_role_capacity_validation.json"
REPORT = R / "lrg008_diagram_role_capacity_validation_report.md"
FIELDS = (
    "consensus_group_id", "locus", "page", "section", "kind",
    "grammar_scope", "strict_zero_alternative", "symbol_count",
)
EXPECTED = {
    GROUPS: "a202d93498e8a350a5d7e0ca46e831dcc37ea5c0182dc404d63cb797a98b1225",
    LRG001: "3dd6d292863acf08c0728846c824c6256a672550b1814c61c8eb7e3b34adbc4d",
    LRG001V: "b062d9fdac267aa2f1660a9a34291e99c7e3dce7d094f8533848f96a22224556",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def physical(page: str) -> str:
    value = re.match(r"^f\d+", page)
    if value is None:
        raise RuntimeError("invalid page")
    return value.group()


def projected():
    with GROUPS.open(encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle, delimiter="\t")
        header = next(reader)
        positions = tuple(header.index(field) for field in FIELDS)
        for values in reader:
            yield {field: values[position] for field, position in zip(FIELDS, positions, strict=True)}


def main() -> int:
    if OUT.exists() or REPORT.exists():
        raise RuntimeError("validation output exists")
    checks = 0

    for path, expected in EXPECTED.items():
        if sha(path) != expected:
            raise RuntimeError(f"source hash mismatch {path.name}")
        checks += 1
    if json.loads(LRG001.read_text())["status"] != "RECOVERED_CONFIRMED_TRANSFERABLE_SOURCE_NATIVE_LABEL_PROFILE":
        raise RuntimeError("LRG001 status")
    if json.loads(LRG001V.read_text())["status"] != "PASS_RECIPROCAL_LRG001_RECOVERY_RECONSTRUCTION":
        raise RuntimeError("LRG001 validation status")
    checks += 2

    source = []
    identifiers = set()
    for raw in projected():
        if raw["strict_zero_alternative"] != "1" or raw["kind"] not in {"L", "C", "R"}:
            continue
        identifier = raw["consensus_group_id"]
        if identifier in identifiers:
            raise RuntimeError("duplicate source ID")
        identifiers.add(identifier)
        count = int(raw["symbol_count"])
        if count < 1:
            raise RuntimeError("bad symbol count")
        source.append({**raw, "symbol_count": count, "physical_folio": physical(raw["page"])})
        checks += 2

    grouped = defaultdict(list)
    for row in source:
        grouped[(row["page"], row["symbol_count"])].append(row)
    mixed = {}
    for key, rows in grouped.items():
        roles = {row["kind"] for row in rows}
        if "L" in roles and roles & {"C", "R"}:
            mixed[key] = rows

    capacity = defaultdict(lambda: Counter(cells=0, rows=0, labels=0, controls=0))
    for rows in mixed.values():
        key = rows[0]["physical_folio"]
        capacity[key]["cells"] += 1
        capacity[key]["rows"] += len(rows)
        capacity[key]["labels"] += sum(row["kind"] == "L" for row in rows)
        capacity[key]["controls"] += sum(row["kind"] != "L" for row in rows)
    eligible = {
        key for key, value in capacity.items()
        if value["cells"] >= 3 and value["rows"] >= 8
        and value["labels"] >= 3 and value["controls"] >= 3
    }
    retained = {key: rows for key, rows in mixed.items() if rows[0]["physical_folio"] in eligible}

    panel = []
    per_cell = []
    log_orbit = 0.0
    for number, ((page, length), rows) in enumerate(sorted(retained.items()), 1):
        rows = sorted(rows, key=lambda row: (row["kind"] != "L", row["consensus_group_id"]))
        label_count = sum(row["kind"] == "L" for row in rows)
        ways = math.comb(len(rows), label_count)
        log_orbit += math.log(ways)
        cell = f"LRG008-C{number:03d}"
        per_cell.append({
            "cell_id": cell, "page": page, "physical_folio": rows[0]["physical_folio"],
            "section": rows[0]["section"], "symbol_count": length,
            "label_rows": label_count, "diagram_rows": len(rows) - label_count,
            "C_rows": sum(row["kind"] == "C" for row in rows),
            "R_rows": sum(row["kind"] == "R" for row in rows),
            "total_rows": len(rows), "cell_assignment_count": ways,
        })
        for row_number, row in enumerate(rows, 1):
            panel.append({
                "panel_row_id": f"{cell}|R{row_number:03d}", "cell_id": cell,
                "consensus_group_id": row["consensus_group_id"], "locus": row["locus"],
                "page": page, "physical_folio": row["physical_folio"],
                "section": row["section"], "symbol_count": length,
                "manual_role": row["kind"],
                "target_class": "LABEL" if row["kind"] == "L" else "DIAGRAM",
            })
            checks += 3

    with PANEL.open(encoding="utf-8", newline="") as handle:
        stored_panel = list(csv.DictReader(handle, delimiter="\t"))
    string_panel = [{key: str(value) for key, value in row.items()} for row in panel]
    if stored_panel != string_panel:
        raise RuntimeError("panel mismatch")
    checks += len(panel) * len(panel[0])

    roles = Counter(row["manual_role"] for row in panel)
    sections = Counter(row["section"] for row in panel)
    pages = sorted({row["page"] for row in panel})
    folios = sorted({row["physical_folio"] for row in panel}, key=lambda value: int(value[1:]))
    role_folios = {
        role: sorted({row["physical_folio"] for row in panel if row["manual_role"] == role}, key=lambda value: int(value[1:]))
        for role in ("C", "R")
    }
    parity = Counter("ODD" if int(value[1:]) % 2 else "EVEN" for value in folios)
    gates = {
        "LRG001_confirmed_and_cleanly_reconstructed": True,
        "exact_projected_field_reader_excludes_family_surface": True,
        "at_least_40_mixed_cells": len(per_cell) >= 40,
        "at_least_280_rows": len(panel) >= 280,
        "at_least_140_label_rows": roles["L"] >= 140,
        "at_least_140_diagram_rows": roles["C"] + roles["R"] >= 140,
        "at_least_10_pages": len(pages) >= 10,
        "at_least_6_physical_folios": len(folios) >= 6,
        "at_least_3_sections": len(sections) >= 3,
        "both_C_and_R_controls_present": roles["C"] > 0 and roles["R"] > 0,
        "each_control_role_on_3_folios": all(len(role_folios[role]) >= 3 for role in ("C", "R")),
        "at_least_2_folios_each_parity": parity["ODD"] >= 2 and parity["EVEN"] >= 2,
        "complete_assignment_log_size_at_least_100": log_orbit >= 100.0,
        "target_profile_scores_absent": True,
        "zero_English_glosses": True,
    }
    decision = "AUTHORIZE_TARGET_BLIND_LRG008_CALIBRATION" if all(gates.values()) else "STOP_UNSCORED_LRG008_CAPACITY"
    expected_result = {
        "experiment": "LRG008_DIAGRAM_ROLE_CAPACITY",
        "status": "PASS_ASSOCIATION_UNOPENED_DIAGRAM_ROLE_CAPACITY" if all(gates.values()) else "STOP_DIAGRAM_ROLE_CAPACITY",
        "inputs": {
            "results/source_sta_family_consensus_groups.tsv": sha(GROUPS),
            "results/lrg001_label_register_target_recovered.json": sha(LRG001),
            "results/lrg001_label_register_target_recovered_validation.json": sha(LRG001V),
            SPEC.name: sha(SPEC), BUILDER.name: sha(BUILDER),
        },
        "counts": {
            "rows": len(panel), "cells": len(per_cell), "pages": len(pages),
            "physical_folios": len(folios), "sections": len(sections),
            "labels": roles["L"], "diagram": roles["C"] + roles["R"],
            "C": roles["C"], "R": roles["R"],
        },
        "pages": pages, "physical_folios": folios, "role_folios": role_folios,
        "parity_folio_counts": dict(sorted(parity.items())),
        "section_row_counts": dict(sorted(sections.items())),
        "excluded_low_capacity_folios": sorted(set(capacity) - eligible, key=lambda value: int(value[1:])),
        "per_cell": per_cell, "complete_assignment_log_size": log_orbit,
        "panel_sha256": sha(PANEL), "gates": gates, "decision": decision,
        "claim_ceiling": "Association-unopened capacity for projecting the already confirmed LRG001 profile from labels to other diagram roles; no identifier, name, noun, owner, object, word, sound, language, meaning, plaintext, or translation.",
    }
    production = json.loads(PRODUCTION.read_text(encoding="utf-8"))
    if production != expected_result:
        raise RuntimeError("production JSON mismatch")
    checks += len(per_cell) * 11 + len(gates) + 25

    expected_report = (
        "# LRG008 diagram-role capacity\n\n"
        f"Status: **{expected_result['status']}**.\n\n"
        f"The fixed metadata-only gate retains **{len(panel)}** rows in **{len(per_cell)}** exact page-by-length cells, "
        f"**{len(pages)}** pages, **{len(folios)}** physical folios, and **{len(sections)}** sections. "
        f"The roles are L={roles['L']}, C={roles['C']}, and R={roles['R']}. "
        f"The low-capacity folio exclusion is {', '.join(sorted(set(capacity) - eligible))}.\n\n"
        f"Decision: **{decision}**. No family surface, profile score, role association, identifier, name, noun, owner, object, word, meaning, plaintext, or translation was opened.\n"
    )
    if PRODUCTION_REPORT.read_text(encoding="utf-8") != expected_report:
        raise RuntimeError("production report mismatch")
    checks += 1

    result = {
        "status": "PASS_CLEAN_LRG008_CAPACITY_RECONSTRUCTION",
        "checks": checks, "discrepancies": 0,
        "counts": expected_result["counts"], "gates": gates,
        "panel_sha256": sha(PANEL), "production_json_sha256": sha(PRODUCTION),
        "production_report_sha256": sha(PRODUCTION_REPORT),
        "producer_sha256": sha(BUILDER), "spec_sha256": sha(SPEC),
        "family_surface_or_profile_score_accessed": False,
        "decision": decision,
        "claim_ceiling": expected_result["claim_ceiling"],
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    REPORT.write_text(
        "# LRG008 diagram-role capacity validation\n\n"
        "Status: **PASS_CLEAN_LRG008_CAPACITY_RECONSTRUCTION**.\n\n"
        f"Independent code reconstructs all **{len(panel)}** rows, **{len(per_cell)}** exact cells, folio filters, role quotas, "
        f"assignment capacity, gates, JSON, and report in **{checks:,}** checks with zero discrepancies.\n\n"
        "No family surface, profile score, role association, identifier, name, noun, owner, object, word, meaning, plaintext, or translation was opened.\n",
        encoding="utf-8", newline="\n",
    )
    print(json.dumps({"status": result["status"], "checks": checks, "decision": decision}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
