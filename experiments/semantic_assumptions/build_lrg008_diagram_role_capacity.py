#!/usr/bin/env python3
"""Build association-unopened LRG008 label-versus-diagram capacity."""

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
SPEC = HERE / "LRG008_DIAGRAM_ROLE_CAPACITY_SPEC.md"
GROUPS = RESULTS / "source_sta_family_consensus_groups.tsv"
LRG001 = RESULTS / "lrg001_label_register_target_recovered.json"
LRG001_VALIDATION = RESULTS / "lrg001_label_register_target_recovered_validation.json"
PANEL = RESULTS / "lrg008_diagram_role_capacity.tsv"
OUT = RESULTS / "lrg008_diagram_role_capacity.json"
REPORT = RESULTS / "lrg008_diagram_role_capacity_report.md"
EXPECTED = {
    GROUPS: "a202d93498e8a350a5d7e0ca46e831dcc37ea5c0182dc404d63cb797a98b1225",
    LRG001: "3dd6d292863acf08c0728846c824c6256a672550b1814c61c8eb7e3b34adbc4d",
    LRG001_VALIDATION: "b062d9fdac267aa2f1660a9a34291e99c7e3dce7d094f8533848f96a22224556",
}
FIELDS = (
    "consensus_group_id", "locus", "page", "section", "kind",
    "grammar_scope", "strict_zero_alternative", "symbol_count",
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def folio(page: str) -> str:
    match = re.match(r"^f\d+", page)
    if match is None:
        raise RuntimeError(f"bad page {page}")
    return match.group(0)


def projected_rows(path: Path):
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle, delimiter="\t")
        header = next(reader)
        indexes = [header.index(field) for field in FIELDS]
        for values in reader:
            yield {field: values[index] for field, index in zip(FIELDS, indexes, strict=True)}


def main() -> int:
    if any(path.exists() for path in (PANEL, OUT, REPORT)):
        raise RuntimeError("LRG008 capacity output exists")
    for path, expected in EXPECTED.items():
        if sha(path) != expected:
            raise RuntimeError(f"input hash mismatch: {path.name}")
    lrg001 = json.loads(LRG001.read_text(encoding="utf-8"))
    validation = json.loads(LRG001_VALIDATION.read_text(encoding="utf-8"))
    if lrg001["status"] != "RECOVERED_CONFIRMED_TRANSFERABLE_SOURCE_NATIVE_LABEL_PROFILE":
        raise RuntimeError("LRG001 status drift")
    if validation["status"] != "PASS_RECIPROCAL_LRG001_RECOVERY_RECONSTRUCTION":
        raise RuntimeError("LRG001 validation drift")

    selected_source = []
    ids = set()
    for row in projected_rows(GROUPS):
        if row["strict_zero_alternative"] != "1" or row["kind"] not in {"L", "C", "R"}:
            continue
        identifier = row["consensus_group_id"]
        if identifier in ids:
            raise RuntimeError(f"duplicate group {identifier}")
        ids.add(identifier)
        count = int(row["symbol_count"])
        if count < 1:
            raise RuntimeError(f"invalid symbol count {identifier}")
        row = dict(row)
        row["symbol_count"] = count
        row["physical_folio"] = folio(row["page"])
        selected_source.append(row)

    cells = defaultdict(list)
    for row in selected_source:
        cells[(row["page"], row["symbol_count"])].append(row)
    mixed = {
        key: rows for key, rows in cells.items()
        if any(row["kind"] == "L" for row in rows)
        and any(row["kind"] in {"C", "R"} for row in rows)
    }
    folio_stats = defaultdict(lambda: Counter(cells=0, rows=0, labels=0, controls=0))
    for rows in mixed.values():
        physical = rows[0]["physical_folio"]
        folio_stats[physical]["cells"] += 1
        folio_stats[physical]["rows"] += len(rows)
        folio_stats[physical]["labels"] += sum(row["kind"] == "L" for row in rows)
        folio_stats[physical]["controls"] += sum(row["kind"] in {"C", "R"} for row in rows)
    eligible_folios = {
        physical for physical, value in folio_stats.items()
        if value["cells"] >= 3 and value["rows"] >= 8
        and value["labels"] >= 3 and value["controls"] >= 3
    }
    retained = {
        key: rows for key, rows in mixed.items()
        if rows[0]["physical_folio"] in eligible_folios
    }

    panel_rows = []
    per_cell = []
    log_orbit = 0.0
    for cell_index, (key, rows) in enumerate(sorted(retained.items()), 1):
        rows = sorted(rows, key=lambda row: (0 if row["kind"] == "L" else 1, row["consensus_group_id"]))
        label_count = sum(row["kind"] == "L" for row in rows)
        control_count = len(rows) - label_count
        ways = math.comb(len(rows), label_count)
        log_orbit += math.log(ways)
        cell_id = f"LRG008-C{cell_index:03d}"
        per_cell.append({
            "cell_id": cell_id, "page": key[0], "physical_folio": rows[0]["physical_folio"],
            "section": rows[0]["section"], "symbol_count": key[1],
            "label_rows": label_count, "diagram_rows": control_count,
            "C_rows": sum(row["kind"] == "C" for row in rows),
            "R_rows": sum(row["kind"] == "R" for row in rows),
            "total_rows": len(rows), "cell_assignment_count": ways,
        })
        for row_index, row in enumerate(rows, 1):
            panel_rows.append({
                "panel_row_id": f"{cell_id}|R{row_index:03d}",
                "cell_id": cell_id,
                "consensus_group_id": row["consensus_group_id"],
                "locus": row["locus"],
                "page": row["page"],
                "physical_folio": row["physical_folio"],
                "section": row["section"],
                "symbol_count": row["symbol_count"],
                "manual_role": row["kind"],
                "target_class": "LABEL" if row["kind"] == "L" else "DIAGRAM",
            })

    fieldnames = list(panel_rows[0])
    with PANEL.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(panel_rows)

    role_counts = Counter(row["manual_role"] for row in panel_rows)
    section_counts = Counter(row["section"] for row in panel_rows)
    pages = sorted({row["page"] for row in panel_rows})
    folios = sorted({row["physical_folio"] for row in panel_rows}, key=lambda value: int(value[1:]))
    role_folios = {
        role: sorted({row["physical_folio"] for row in panel_rows if row["manual_role"] == role}, key=lambda value: int(value[1:]))
        for role in ("C", "R")
    }
    parities = Counter("ODD" if int(value[1:]) % 2 else "EVEN" for value in folios)
    gates = {
        "LRG001_confirmed_and_cleanly_reconstructed": True,
        "exact_projected_field_reader_excludes_family_surface": True,
        "at_least_40_mixed_cells": len(per_cell) >= 40,
        "at_least_280_rows": len(panel_rows) >= 280,
        "at_least_140_label_rows": role_counts["L"] >= 140,
        "at_least_140_diagram_rows": role_counts["C"] + role_counts["R"] >= 140,
        "at_least_10_pages": len(pages) >= 10,
        "at_least_6_physical_folios": len(folios) >= 6,
        "at_least_3_sections": len(section_counts) >= 3,
        "both_C_and_R_controls_present": role_counts["C"] > 0 and role_counts["R"] > 0,
        "each_control_role_on_3_folios": all(len(role_folios[role]) >= 3 for role in ("C", "R")),
        "at_least_2_folios_each_parity": parities["ODD"] >= 2 and parities["EVEN"] >= 2,
        "complete_assignment_log_size_at_least_100": log_orbit >= 100.0,
        "target_profile_scores_absent": True,
        "zero_English_glosses": True,
    }
    passed = all(gates.values())
    decision = "AUTHORIZE_TARGET_BLIND_LRG008_CALIBRATION" if passed else "STOP_UNSCORED_LRG008_CAPACITY"
    result = {
        "experiment": "LRG008_DIAGRAM_ROLE_CAPACITY",
        "status": "PASS_ASSOCIATION_UNOPENED_DIAGRAM_ROLE_CAPACITY" if passed else "STOP_DIAGRAM_ROLE_CAPACITY",
        "inputs": {str(path.relative_to(HERE)): sha(path) for path in EXPECTED} | {
            SPEC.name: sha(SPEC), Path(__file__).name: sha(Path(__file__)),
        },
        "counts": {
            "rows": len(panel_rows), "cells": len(per_cell), "pages": len(pages),
            "physical_folios": len(folios), "sections": len(section_counts),
            "labels": role_counts["L"], "diagram": role_counts["C"] + role_counts["R"],
            "C": role_counts["C"], "R": role_counts["R"],
        },
        "pages": pages,
        "physical_folios": folios,
        "role_folios": role_folios,
        "parity_folio_counts": dict(sorted(parities.items())),
        "section_row_counts": dict(sorted(section_counts.items())),
        "excluded_low_capacity_folios": sorted(set(folio_stats) - eligible_folios, key=lambda value: int(value[1:])),
        "per_cell": per_cell,
        "complete_assignment_log_size": log_orbit,
        "panel_sha256": sha(PANEL),
        "gates": gates,
        "decision": decision,
        "claim_ceiling": "Association-unopened capacity for projecting the already confirmed LRG001 profile from labels to other diagram roles; no identifier, name, noun, owner, object, word, sound, language, meaning, plaintext, or translation.",
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    REPORT.write_text(
        "# LRG008 diagram-role capacity\n\n"
        f"Status: **{result['status']}**.\n\n"
        f"The fixed metadata-only gate retains **{len(panel_rows)}** rows in **{len(per_cell)}** exact page-by-length cells, "
        f"**{len(pages)}** pages, **{len(folios)}** physical folios, and **{len(section_counts)}** sections. "
        f"The roles are L={role_counts['L']}, C={role_counts['C']}, and R={role_counts['R']}. "
        f"The low-capacity folio exclusion is {', '.join(sorted(set(folio_stats) - eligible_folios))}.\n\n"
        f"Decision: **{decision}**. No family surface, profile score, role association, identifier, name, noun, owner, object, word, meaning, plaintext, or translation was opened.\n",
        encoding="utf-8", newline="\n",
    )
    print(json.dumps({"status": result["status"], "counts": result["counts"], "decision": decision}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
