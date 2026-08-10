#!/usr/bin/env python3
"""Single hash-frozen target invocation for ZLA001."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import os
from pathlib import Path

import zla001_core as core


BASE = Path(__file__).resolve().parent
ROOT = BASE.parent.parent
R = BASE / "results"
FREEZE = ROOT / "ZLA001_TARGET_FREEZE.json"
PANEL = R / "zodiac_label_cycle_capacity.tsv"
STA = R / "source_sta_group_alignment.tsv"
STA_STATUS = R / "source_sta_group_alignment.json"
STA_VALIDATION = R / "source_sta_group_alignment_validation.json"
OUT = R / "zla001_target.json"
REPORT = R / "zla001_target.md"
VALIDATION_OUT = R / "zla001_target_validation.json"
VALIDATION_REPORT = R / "zla001_target_validation.md"
READINGS = core.READINGS
EXPECTED_FROZEN_FILES = {
    "ZODIAC_LABEL_ADJACENCY_METHOD.md",
    "experiments/semantic_assumptions/results/zodiac_label_cycle_capacity.tsv",
    "experiments/semantic_assumptions/results/zodiac_label_cycle_capacity.json",
    "experiments/semantic_assumptions/results/zodiac_label_cycle_capacity_validation.json",
    "experiments/semantic_assumptions/results/source_sta_group_alignment.tsv",
    "experiments/semantic_assumptions/results/source_sta_group_alignment.json",
    "experiments/semantic_assumptions/results/source_sta_group_alignment_validation.json",
    "experiments/semantic_assumptions/zla001_core.py",
    "experiments/semantic_assumptions/run_zla001_controls.py",
    "experiments/semantic_assumptions/validate_zla001_controls.py",
    "experiments/semantic_assumptions/results/zla001_controls_attempt1.json",
    "experiments/semantic_assumptions/results/zla001_controls_attempt1.md",
    "experiments/semantic_assumptions/results/zla001_controls.json",
    "experiments/semantic_assumptions/results/zla001_controls.md",
    "experiments/semantic_assumptions/results/zla001_controls_validation.json",
    "experiments/semantic_assumptions/results/zla001_controls_validation.md",
    "experiments/semantic_assumptions/run_zla001_target.py",
    "experiments/semantic_assumptions/validate_zla001_target.py",
    "experiments/semantic_assumptions/freeze_zla001_target.py",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False) + "\n").encode()


def verify_freeze() -> dict[str, object]:
    if not FREEZE.is_file():
        raise AssertionError("freeze absent")
    frozen = json.loads(FREEZE.read_text(encoding="utf-8"))
    if frozen.get("status") != "FROZEN_TARGET_AND_VALIDATION_ABSENT":
        raise AssertionError("freeze status")
    if set(frozen.get("files", {})) != EXPECTED_FROZEN_FILES:
        raise AssertionError("freeze file allowlist")
    for relative, expected in frozen["files"].items():
        path = ROOT / relative
        if not path.is_file() or sha(path) != expected:
            raise AssertionError(f"freeze hash drift: {relative}")
    expected_absence = {
        str(path.relative_to(ROOT)): True
        for path in (OUT, REPORT, VALIDATION_OUT, VALIDATION_REPORT)
    }
    if frozen.get("target_absence") != expected_absence:
        raise AssertionError("freeze absence schema")
    if any(path.exists() for path in (OUT, REPORT, VALIDATION_OUT, VALIDATION_REPORT)):
        raise AssertionError("target or validation artifact already exists")
    return frozen


def load_sequences(geometry: core.Geometry) -> tuple[dict, dict[str, object]]:
    status = json.loads(STA_STATUS.read_text(encoding="utf-8"))
    validation = json.loads(STA_VALIDATION.read_text(encoding="utf-8"))
    if status.get("status") != "PASS_LOSSLESS_SOURCE_SEPARATOR_PRESERVING_STA_ALIGNMENT":
        raise AssertionError("STA status drift")
    if validation.get("status") != "PASS_INDEPENDENT_SOURCE_STA_ALIGNMENT_RECONSTRUCTION":
        raise AssertionError("STA validation drift")
    target_loci = {locus for ring in geometry.rings for locus in ring.loci}
    grouped: dict[tuple[str, str], list[dict[str, str]]] = {}
    with STA.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            if row["edition"] in READINGS and row["locus"] in target_loci:
                grouped.setdefault((row["edition"], row["locus"]), []).append(row)
    if len(grouped) != len(READINGS) * len(target_loci):
        raise AssertionError("reading-locus join coverage")

    sequences = {reading: {view: [] for view in core.VIEWS} for reading in READINGS}
    group_total = 0
    payload = bytearray()
    for reading in READINGS:
        for ring in geometry.rings:
            family_ring = []
            boundary_ring = []
            for locus in ring.loci:
                rows = sorted(grouped[(reading, locus)], key=lambda row: int(row["source_group_index"]))
                expected_count = int(rows[0]["source_group_count"])
                if len(rows) != expected_count or [int(row["source_group_index"]) for row in rows] != list(range(1, expected_count + 1)):
                    raise AssertionError("source group sequence contract")
                groups = [tuple(row["primary_sta_families"]) for row in rows]
                if any(not group for group in groups):
                    raise AssertionError("empty STA family group")
                family = tuple(token for group in groups for token in group)
                boundary: tuple[str, ...] = tuple()
                for index, group in enumerate(groups):
                    if index:
                        boundary += ("|",)
                    boundary += group
                family_ring.append(family)
                boundary_ring.append(boundary)
                group_total += len(rows)
                payload.extend(f"{reading}\t{ring.ring_id}\t{locus}\t{''.join(family)}\t{''.join(boundary)}\n".encode())
            sequences[reading]["FAMILY_ONLY"].append(family_ring)
            sequences[reading]["BOUNDARY_AWARE"].append(boundary_ring)
    return sequences, {
        "reading_slots": len(READINGS) * len(target_loci),
        "physical_slots": len(target_loci),
        "source_groups": group_total,
        "sequence_payload_sha256": hashlib.sha256(payload).hexdigest(),
    }


def numeric_leaves(value: object, prefix: str = "") -> dict[str, float]:
    output = {}
    if isinstance(value, dict):
        for key, item in value.items():
            if "sha256" in str(key):
                continue
            output.update(numeric_leaves(item, f"{prefix}.{key}" if prefix else str(key)))
    elif isinstance(value, (int, float)) and not isinstance(value, bool):
        output[prefix] = float(value)
    return output


def invariant(left: dict[str, object], right: dict[str, object]) -> dict[str, object]:
    a = numeric_leaves(left); b = numeric_leaves(right)
    if set(a) != set(b):
        return {"pass": False, "max_abs": None, "same_logic": False}
    maximum = max(abs(a[key] - b[key]) for key in a) if a else 0.0
    same_logic = left["gates"] == right["gates"] and left["confirmed"] == right["confirmed"]
    return {"pass": maximum <= core.TOL and same_logic, "max_abs": maximum, "same_logic": same_logic}


def report_text(result: dict[str, object]) -> str:
    evaluation = result["evaluation"]
    primary = evaluation["primary"]
    noexact = evaluation["noexact"]
    components = evaluation["components"]
    return (
        "# ZLA001 zodiac label cyclic adjacency target\n\n"
        f"Status: **{result['status']}**. Decision: **{result['decision']}**.\n\n"
        f"The fixed weakest-reading composite effect is `{primary['minimum_effect']:.6f}` with "
        f"joint `p={primary['p_plus_one']:.6f}`. Component minimum effects are "
        f"`FAMILY_ONLY={components['FAMILY_ONLY']['minimum_effect']:.6f}` and "
        f"`BOUNDARY_AWARE={components['BOUNDARY_AWARE']['minimum_effect']:.6f}`. "
        f"After removing exact complete-record pairs, the minimum effect is "
        f"`{noexact['minimum_effect']:.6f}` with `p={noexact['p_plus_one']:.6f}`.\n\n"
        f"Positive-folio counts by alternate reading are `{evaluation['positive_folio_counts']}`. "
        "All 21 rings, all 235 physical slots, and the complete frozen 65,536-world distance orbit "
        "were scored once. No individual label sequence, family identity, favorable ring, object "
        "assignment, or English gloss is emitted.\n\n"
        "A confirmation would establish only a local length-adjusted construction signal among adjacent "
        "public zodiac labels. A nonconfirmation closes only this representation. Neither outcome can "
        "establish ownership, a serial code, number, degree, sign name, word, meaning, plaintext, or translation.\n"
    )


def main() -> None:
    frozen = verify_freeze()
    geometry = core.load_geometry(PANEL)
    assignments, orbit = core.assignment_matrix(geometry)
    if orbit != frozen["orbit"]:
        raise AssertionError("orbit freeze drift")
    sequences, source_join = load_sequences(geometry)
    evaluation = core.evaluate(geometry, assignments, sequences)
    shifts = [int.from_bytes(hashlib.sha256(f"ZLA001|TARGET_ROTATE|{ring.ring_id}".encode()).digest()[:2], "big") for ring in geometry.rings]
    rotation = invariant(evaluation, core.evaluate(geometry, assignments, core.rotate_sequences(sequences, shifts)))
    reflection = invariant(evaluation, core.evaluate(geometry, assignments, core.reflect_sequences(sequences)))
    execution_gates = {
        "all_scientific_gates": all(evaluation["gates"].values()),
        "rotation_invariance": bool(rotation["pass"]),
        "reflection_invariance": bool(reflection["pass"]),
        "exact_source_join": source_join["physical_slots"] == 235 and source_join["reading_slots"] == 705,
        "freeze_hashes_and_absence_verified": True,
        "no_individual_sequence_or_favorable_ring_emitted": True,
        "no_image_OCR_neural_vision_or_English_gloss": True,
    }
    confirmed = all(execution_gates.values())
    result = {
        "experiment": "ZLA001_ZODIAC_LABEL_CYCLIC_ADJACENCY_TARGET",
        "status": "CONFIRMED_LOCAL_ZODIAC_LABEL_ADJACENCY_CONSTRUCTION" if confirmed else "FINAL_NONCONFIRMATION_ZODIAC_LABEL_ADJACENCY",
        "decision": "RETAIN_LOCAL_ORDERED_LABEL_REGISTER" if confirmed else "CLOSE_FIXED_ZLA001_REPRESENTATION",
        "freeze_sha256": sha(FREEZE),
        "orbit": orbit,
        "source_join": source_join,
        "evaluation": evaluation,
        "invariances": {"rotation": rotation, "reflection": reflection},
        "execution_gates": execution_gates,
        "target_access": {
            "manual_STA_rows_accessed": True,
            "parser_roots_accessed": False,
            "object_attributes_accessed": False,
            "images_OCR_or_neural_vision_accessed": False,
            "English_glosses_emitted": 0,
        },
        "claim_ceiling": "At most a local length-adjusted STA-family construction signal among adjacent public zodiac-label records; no ownership, serial code, number, degree, sign name, word, meaning, plaintext, or translation.",
    }
    report = report_text(result)
    # Recheck no-clobber immediately before installing either artifact.
    if any(path.exists() for path in (OUT, REPORT, VALIDATION_OUT, VALIDATION_REPORT)):
        raise AssertionError("artifact appeared during target run")
    temp_json = OUT.with_suffix(".json.tmp")
    temp_md = REPORT.with_suffix(".md.tmp")
    temp_json.write_bytes(canonical(result)); temp_md.write_text(report, encoding="utf-8")
    try:
        os.link(temp_json, OUT); os.link(temp_md, REPORT)
    except Exception:
        if OUT.exists(): OUT.unlink()
        if REPORT.exists(): REPORT.unlink()
        raise
    finally:
        if temp_json.exists(): temp_json.unlink()
        if temp_md.exists(): temp_md.unlink()
    print(json.dumps({"status": result["status"], "decision": result["decision"], "primary": evaluation["primary"], "gates": execution_gates}, sort_keys=True))


if __name__ == "__main__":
    main()
