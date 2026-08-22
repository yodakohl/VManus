#!/usr/bin/env python3
"""Validate the bounded V70 image-first sidequest release."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
PAGES = {
    "f10r", "f11r", "f55v", "f56r", "f81v",
    "f82r", "f83r", "f67r2", "f68r1", "f69v",
}


def rows(name: str) -> list[dict[str, str]]:
    with (ROOT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    checks: dict[str, bool] = {}
    manifest = rows("V70_IMAGE_MANIFEST.tsv")
    checks["manifest_exact_ten_pages"] = len(manifest) == 10 and {
        row["page"] for row in manifest
    } == PAGES
    checks["manifest_no_absolute_paths"] = all(
        not row["inspection_filename"].startswith("/") for row in manifest
    )
    checks["manifest_hashes_well_formed"] = all(
        len(row["sha256"]) == 64 and int(row["sha256"], 16) >= 0
        for row in manifest
    )

    inventory_names = [
        f"V70_R{role}_TEN_PAGE_VISUAL_INVENTORY.tsv" for role in range(1, 5)
    ]
    for name in inventory_names:
        data = rows(name)
        checks[f"{name}_exact_scope"] = (
            len(data) == 10 and {row["page"] for row in data} == PAGES
        )

    for role in range(1, 5):
        connections = rows(f"V70_R{role}_OBJECT_CONNECTIONS.tsv")
        pressure = rows(f"V70_R{role}_V69_PRESSURE_MATRIX.tsv")
        checks[f"R{role}_connections_nonempty"] = len(connections) >= 20
        checks[f"R{role}_pressure_nonempty"] = len(pressure) >= 15

    selected = rows("V70_SELECTED_TEN_PAGE_IMAGE_REVISION.tsv")
    checks["selection_exact_scope"] = (
        len(selected) == 10 and {row["page"] for row in selected} == PAGES
    )
    checks["selection_no_blank_fields"] = all(
        all(value.strip() for value in row.values()) for row in selected
    )
    checks["selection_f69_preserves_local_28_only"] = any(
        row["page"] == "f69v"
        and "approximately 28" in row["selected_geometry"]
        and "three-wheel" in row["v69_revision"]
        for row in selected
    )

    text_files = list(ROOT.glob("V70_*.md")) + list(ROOT.glob("V70_*.tsv"))
    checks["no_sealed_page_rows"] = all(
        "\nf84\t" not in path.read_text(encoding="utf-8")
        and "\nf84r\t" not in path.read_text(encoding="utf-8")
        for path in text_files
    )
    checks["four_role_reports_present"] = all(
        (ROOT / name).exists()
        for name in [
            "V70_R1_IMAGE_FIRST_WORKSHOP_REPORT.md",
            "V70_R2_HISTORICAL_IMAGE_REPORT.md",
            "V70_R3_TECHNICAL_IMAGE_REPORT.md",
            "V70_R4_IMAGE_CORRECTOR_REPORT.md",
        ]
    )

    result = {
        "schema": "V70_IMAGE_ROUND_VALIDATION_V1",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "counts": {
            "manifest_pages": len(manifest),
            "selected_pages": len(selected),
            "role_connection_rows": {
                f"R{role}": len(rows(f"V70_R{role}_OBJECT_CONNECTIONS.tsv"))
                for role in range(1, 5)
            },
            "role_pressure_rows": {
                f"R{role}": len(rows(f"V70_R{role}_V69_PRESSURE_MATRIX.tsv"))
                for role in range(1, 5)
            },
        },
        "bindings": {
            name: sha256(ROOT / name)
            for name in inventory_names
            + [
                "V70_IMAGE_MANIFEST.tsv",
                "V70_SELECTED_TEN_PAGE_IMAGE_REVISION.tsv",
                "V70_FOUR_ROLE_IMAGE_SELECTION.md",
            ]
        },
    }
    output = ROOT / "V70_VALIDATION.json"
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(result["status"], sum(checks.values()), "/", len(checks))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
