#!/usr/bin/env python3
"""Validate EBA001 record integrity without reacquiring or judging the TIFFs."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


BASE = Path(__file__).resolve().parent
METHOD = BASE / "EBA001_RAW_DIRECTIONAL_MSI_MARGINALIA_METHOD.md"
ACQUIRE = BASE / "acquire_eba001_raw_directional_msi.py"
RENDER = BASE / "render_eba001_raw_directional_msi.py"
PRIOR_TARGET = BASE / "results/f17r_f116v_mixed_script_native_visual_relation.json"
PRIOR_REPORT = BASE / "results/f17r_f116v_mixed_script_native_visual_relation_report.md"
INVENTORY = BASE / "results/eba001_raw_directional_msi_inventory.json"
OBSERVATIONS = BASE / "results/eba001_raw_directional_msi_observations.tsv"
RESULT = BASE / "results/eba001_raw_directional_msi_result.json"
REPORT = BASE / "results/eba001_raw_directional_msi_report.md"
VALIDATION = BASE / "results/eba001_raw_directional_msi_validation.json"


def sha256(path: Path) -> str:
    with path.open("rb") as source:
        return hashlib.file_digest(source, "sha256").hexdigest()


def strict_json(path: Path) -> object:
    def pairs(values: list[tuple[str, object]]) -> dict[str, object]:
        result: dict[str, object] = {}
        for key, value in values:
            if key in result:
                raise ValueError(f"duplicate JSON key: {key}")
            result[key] = value
        return result

    return json.loads(
        path.read_bytes(),
        object_pairs_hook=pairs,
        parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)),
    )


def canonical(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode()


def xywh(value: str) -> tuple[int, int, int, int]:
    parts = tuple(int(item) for item in value.split(","))
    if len(parts) != 4 or min(parts) < 0 or parts[2] <= 0 or parts[3] <= 0:
        raise ValueError(value)
    return parts


def main() -> None:
    inventory = strict_json(INVENTORY)
    result = strict_json(RESULT)
    rows = list(csv.DictReader(OBSERVATIONS.open(newline=""), delimiter="\t"))
    files = inventory["files"]
    keys = [(row["folio"], row["illumination_role"]) for row in files]
    by_key = {(row["folio"], row["exposure"]): row for row in rows}
    checks: dict[str, bool] = {}
    checks["six_inventory_objects"] = len(files) == 6
    checks["two_folios_three_captures"] = [row["folio"] for row in files] == ["f17r"] * 3 + ["f116v"] * 3
    checks["capture_order"] = [row["illumination_role"] for row in files] == ["EXPOSURE_007", "EXPOSURE_029", "EXPOSURE_037"] * 2
    checks["exact_tiff_geometry"] = all(
        type(row["tiff"]["width"]) is int and row["tiff"]["width"] == 8176
        and type(row["tiff"]["height"]) is int and row["tiff"]["height"] == 6132
        and type(row["tiff"]["bits_per_sample"]) is int and row["tiff"]["bits_per_sample"] == 16
        and row["tiff"]["samples_per_pixel"] == 1 and row["tiff"]["compression_tag"] == 1
        for row in files
    )
    checks["exact_total_bytes"] = sum(row["size"] for row in files) == 602385474
    checks["unique_hashes_and_ids"] = len({row["sha256"] for row in files}) == 6 and len({row["file_id"] for row in files}) == 6
    checks["six_observations"] = len(rows) == 6 and len(by_key) == 6
    checks["observation_keys_match_inventory"] = set(by_key) == set(keys)
    checks["source_hashes_and_embedded_datetimes"] = all(
        by_key[key]["source_sha256"] == row["sha256"]
        and by_key[key]["tiff_datetime"].replace("-", ":", 2).replace("T", " ") == row["tiff"]["capture_datetime"]
        for key, row in zip(keys, files, strict=True)
    )
    expected_geometry = {
        "f17r": ("800,1600,1000,4100", "ROTATE_270", "850,80,2500,300", "850,100,650,260", "900,0,2300,160"),
        "f116v": ("6200,700,1976,2900", "ROTATE_90", "1120,1170,1780,320", "1500,500,1350,350", "500,250,1900,500"),
    }
    checks["fixed_roi_geometry"] = all(
        (row["source_context_xywh"], row["orientation"], row["target_roi_xywh"], row["dark_reference_roi_xywh"], row["moving_shadow_roi_xywh"])
        == expected_geometry[row["folio"]]
        for row in rows
    )
    checks["roi_bounds"] = all(
        xywh(row[column])[0] + xywh(row[column])[2] <= (4100 if row["folio"] == "f17r" else 2900)
        and xywh(row[column])[1] + xywh(row[column])[3] <= (1000 if row["folio"] == "f17r" else 1976)
        for row in rows for column in ("target_roi_xywh", "dark_reference_roi_xywh", "moving_shadow_roi_xywh")
    )
    checks["derived_hash_format"] = all(
        len(row[column]) == 64 and set(row[column]) <= set("0123456789abcdef")
        for row in rows for column in ("context_png_sha256", "target_png_sha256", "dark_reference_png_sha256", "moving_shadow_png_sha256")
    )
    checks["all_target_and_dark_references_visible"] = all(
        row["target_state"] == "VISIBLE_DARK" and row["dark_reference_state"] == "VISIBLE_DARK" for row in rows
    )
    checks["all_shadow_controls_capture_specific"] = all(row["moving_shadow_state"] == "CAPTURE_SPECIFIC_PATTERN" for row in rows)
    expected_folio = {
        "state": "MULTI_EXPOSURE_STABLE_DARK_TRACE",
        "target_cross_capture_state": "PERSISTENT_AT_CORRESPONDING_COORDINATES",
        "gross_moving_shadow_state": "CAPTURE_SPECIFIC_PATTERN",
        "mechanism": "UNRESOLVED",
        "capture_ids": ["EXPOSURE_007", "EXPOSURE_029", "EXPOSURE_037"],
    }
    checks["conservative_folio_aggregation"] = all(
        all(result["folios"][folio][key] == value for key, value in expected_folio.items()) for folio in ("f17r", "f116v")
    )
    checks["exact_status_and_decision"] = (
        result["status"] == "PASS_THREE_CAPTURE_STABLE_DARK_TRACE_MECHANISM_UNRESOLVED"
        and result["decision"] == "ACQUIRE_AUTHENTICATED_CHEMISTRY_CHRONOLOGY_OR_LIGHTING_GEOMETRY"
    )
    expected_inputs = {
        "method": sha256(METHOD), "acquisition": sha256(ACQUIRE), "renderer": sha256(RENDER),
        "inventory": sha256(INVENTORY), "observations": sha256(OBSERVATIONS),
        "prior_target_record": sha256(PRIOR_TARGET), "prior_target_report": sha256(PRIOR_REPORT),
    }
    checks["all_input_hashes"] = result["inputs"] == expected_inputs
    checks["canonical_inventory_and_result"] = canonical(inventory) == INVENTORY.read_bytes() and canonical(result) == RESULT.read_bytes()
    checks["source_files_exist"] = all(path.is_file() for path in (METHOD, ACQUIRE, RENDER, PRIOR_TARGET, PRIOR_REPORT, INVENTORY, OBSERVATIONS, RESULT, REPORT))
    if not all(checks.values()):
        raise SystemExit({key: value for key, value in checks.items() if not value})
    validation = {
        "experiment": "EBA001_RAW_MULTI_EXPOSURE_MSI_RECORD_INTEGRITY_VALIDATION",
        "status": "PASS_RECORD_INTEGRITY_VISUAL_JUDGMENT_NOT_INDEPENDENTLY_REPEATED",
        "check_count": len(checks), "checks": checks,
        "source_result_sha256": sha256(RESULT),
        "claim_ceiling": "This validates schemas, source bindings, crop geometry, declared derived-hash string format, and conservative aggregation. It does not possess the TIFF bodies, validate derived image bytes, regenerate pixels, or independently repeat the visual judgment; it establishes no physical mechanism, reading, or translation.",
    }
    data = canonical(validation)
    if VALIDATION.exists() and VALIDATION.read_bytes() != data:
        raise SystemExit("existing validation bytes differ")
    if not VALIDATION.exists():
        VALIDATION.write_bytes(data)
    print(data.decode(), end="")


if __name__ == "__main__":
    main()
