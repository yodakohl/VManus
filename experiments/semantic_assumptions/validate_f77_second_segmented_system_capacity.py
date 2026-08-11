#!/usr/bin/env python3
"""Independent reconstruction of the f77r second-system capacity stop."""

from __future__ import annotations

import ast
import csv
import hashlib
import json
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "experiments" / "semantic_assumptions"
RESULTS = BASE / "results"
METHOD = BASE / "F77_SECOND_SEGMENTED_SYSTEM_CAPACITY_METHOD.md"
PRODUCER = BASE / "audit_f77_second_segmented_system_capacity.py"
EXACT = RESULTS / "existing_human_exact_locus_annotations.tsv"
PAGES = RESULTS / "existing_human_page_annotations.tsv"
F77 = RESULTS / "f77r_quality_transition_bridge.json"
CIRCLES = RESULTS / "special_circle_plain_legend_native_visual_screen.json"
RESULT = RESULTS / "f77_second_segmented_system_capacity.json"
REPORT = RESULTS / "f77_second_segmented_system_capacity_report.md"
OUT = RESULTS / "f77_second_segmented_system_capacity_validation.json"
OUT_MD = RESULTS / "f77_second_segmented_system_capacity_validation_report.md"
HASHES = {
    EXACT: "79c7f06e91f90054aff4cdf27f098a5977d820acdf91f239a14c6ddf553a7f61",
    PAGES: "b358f244cbe853448dd5c32dbc04004cb8ce63d9a8c5ed5afe2a679a115d87fa",
    F77: "c27daa8d7fd1e5d89cda6ec892fda0a7ae5971ebc964e13223abbab5ad9a6700",
    CIRCLES: "e9c1f2508aa8a5615310a4fa8b95e00cf5fc32dec5f07b6bc7d5f89108456cf7",
}
IMAGES = {
    "f69r": ("1006198", "b830e74480830c0d5e8f7b56025473e051743f9ec50685b6fe316ecd493f0f01", 2793, 3763),
    "f70r1": ("1006199", "709419c3c6861c216b1746261884e08a38f1b5a2b052ad129e78cdd73697b5e9", 8886, 3876),
    "f78r": ("1006214", "0054f691ac8fddcac324fba6b385f8ad578cd0f2f9879d5498a325bab0310893", 2793, 3761),
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode()


def fetch(canvas: str) -> bytes:
    url = f"https://collections.library.yale.edu/iiif/2/{canvas}/full/full/0/default.jpg"
    request = urllib.request.Request(url, headers={"User-Agent": "VManus-native-visual-validator/1.0"})
    with urllib.request.urlopen(request, timeout=60) as response:
        return response.read()


def report(status: str) -> str:
    return (
        "# f77r second segmented-system capacity\n\n"
        f"Status: **{status}**.\n\n"
        "No second mixed-output segmented apparatus is available. f69r K1 and f70r1 X1 each "
        "place six labels between six star arms, but every boundary has an arm, so neither "
        "contains an inactive boundary. f78r X1 has six illustration labels distributed among "
        "separate pipe, junction, vat, and pond objects rather than six consecutive segments.\n\n"
        "The f77r transition construction remains post-hoc and unconfirmed. Do not score any "
        "candidate strings or reinterpret all-active wheels as replications. No quality, element, "
        "word, sound, language, cipher, plaintext, meaning, or translation follows.\n"
    )


def main() -> None:
    if OUT.exists() or OUT_MD.exists():
        raise RuntimeError("refusing to overwrite f77 second-system validation")
    checks: list[str] = []
    for path, digest in HASHES.items():
        if sha(path.read_bytes()) != digest:
            raise RuntimeError(("input hash", path))
    checks.append("frozen_local_sources")
    tree = ast.parse(PRODUCER.read_text(encoding="utf-8"))
    if any(
        isinstance(node, ast.ImportFrom) and node.module and "validate_f77_second" in node.module
        for node in ast.walk(tree)
    ):
        raise RuntimeError("producer imports validator")
    checks.append("nonimporting_independence")

    with EXACT.open(newline="", encoding="utf-8") as handle:
        annotations = list(csv.DictReader(handle, delimiter="\t"))
    units: dict[tuple[str, str], int] = {}
    for row in annotations:
        key = (row["page"], row["unit"])
        units[key] = units.get(key, 0) + 1
    required = {("f69r", "K1"): 6, ("f70r1", "X1"): 6, ("f78r", "X1"): 6}
    if any(units.get(key) != value for key, value in required.items()):
        raise RuntimeError("candidate unit counts")
    checks.append("six_label_candidate_units")

    image_records = {}
    for page, (canvas, digest, width, height) in IMAGES.items():
        if sha(fetch(canvas)) != digest:
            raise RuntimeError(("image hash", page))
        image_records[page] = {
            "canvas_id": canvas,
            "image_url": f"https://collections.library.yale.edu/iiif/2/{canvas}/full/full/0/default.jpg",
            "sha256": digest, "width": width, "height": height,
        }
    checks.append("three_live_official_images")

    candidates = [
        {"page": "f69r", "unit": "K1", "labels": 6, "topology": "SIX_CENTRAL_SECTORS_BETWEEN_SIX_STAR_ARMS", "active_boundaries": 6, "inactive_boundaries": 0, "status": "STOP_ALL_BOUNDARIES_ACTIVE"},
        {"page": "f70r1", "unit": "X1", "labels": 6, "topology": "SIX_CENTRAL_SECTORS_BETWEEN_SIX_STAR_ARMS", "active_boundaries": 6, "inactive_boundaries": 0, "status": "STOP_ALL_BOUNDARIES_ACTIVE"},
        {"page": "f78r", "unit": "X1", "labels": 6, "topology": "LABELS_DISTRIBUTED_ACROSS_SEPARATE_APPARATUS_OBJECTS", "active_boundaries": None, "inactive_boundaries": None, "status": "STOP_NOT_ONE_ORDERED_SEGMENT_SYSTEM"},
    ]
    expected_inputs = {str(METHOD.relative_to(ROOT)): sha(METHOD.read_bytes())}
    expected_inputs.update({str(path.relative_to(ROOT)): digest for path, digest in HASHES.items()})
    claim = "No source-bound candidate provides a second six-label apparatus with mixed active and inactive boundaries, so the f77r four-state transition construction remains post-hoc and unconfirmed. No quality, element, word, sound, language, cipher, plaintext, meaning, or translation follows."
    expected = {
        "experiment": "F77_SECOND_SEGMENTED_SYSTEM_CAPACITY",
        "status": "STOP_NO_SECOND_MIXED_OUTPUT_SEGMENTED_SYSTEM",
        "decision": "RETAIN_F77R_POSTHOC_UNCONFIRMED",
        "candidates": candidates,
        "official_images": image_records,
        "native_visual_observation": {
            "machine_authored_source_bound_observation": True,
            "scope": "topology only; no candidate label strings",
            "description": "Both six-sector wheels have a star arm at every segment boundary. The six f78r labels belong to multiple separate illustrated objects rather than consecutive segments of one apparatus.",
            "ocr_or_transcription_used": False,
            "automated_vision_embedding_or_similarity_used": False,
        },
        "gates": {
            "candidate_units_have_six_labels": True,
            "candidate_strings_accessed": False,
            "f69r_has_mixed_active_inactive_boundaries": False,
            "f70r1_has_mixed_active_inactive_boundaries": False,
            "f78r_is_one_ordered_segment_system": False,
            "any_second_system_admitted": False,
            "ocr_or_automated_vision_used": False,
        },
        "inputs": expected_inputs,
        "claim_ceiling": claim,
    }
    result_bytes = RESULT.read_bytes()
    if result_bytes != canonical(expected):
        raise RuntimeError("canonical result mismatch")
    checks.append("canonical_result")
    if REPORT.read_text(encoding="utf-8") != report(expected["status"]):
        raise RuntimeError("report mismatch")
    checks.append("exact_report")
    checks.append("mixed_boundary_gate_stops")

    validation = {
        "experiment": "F77_SECOND_SEGMENTED_SYSTEM_CAPACITY_VALIDATION",
        "status": "PASS_INDEPENDENT_SOURCE_AND_IMAGE_RECONSTRUCTION",
        "check_count": len(checks), "checks": checks,
        "validated_result_sha256": sha(result_bytes),
        "producer_sha256": sha(PRODUCER.read_bytes()),
        "reconstructed": {"candidate_units": 3, "admitted_second_systems": 0, "live_images": 3},
        "visual_judgment_reclassified_by_validator": False,
        "claim_ceiling": claim,
    }
    OUT.write_bytes(canonical(validation))
    OUT_MD.write_text(
        "# f77r second segmented-system capacity validation\n\n"
        "Status: **PASS_INDEPENDENT_SOURCE_AND_IMAGE_RECONSTRUCTION**.\n\n"
        f"All {len(checks)} checks pass. Independent code reconstructs the three six-label "
        "candidate units, refetches the exact official images, and reproduces the canonical "
        "topology-only stop. It binds but does not reclassify the native visual judgments.\n\n"
        "No quality, element, word, sound, language, cipher, plaintext, meaning, or translation follows.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
