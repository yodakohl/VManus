#!/usr/bin/env python3
"""Independent source-only validator for the GDT391 normalization freeze."""
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path


def root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("repository root not found")


ROOT = root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt391_local_object_relation_normalization"
ART = BASE / "artifacts"
SOURCE = ROOT / "experiments/yolo/gdt360_existing_annotation_joint_grounding/artifacts/gdt360_annotation_inventory.tsv"
FRAME = ART / "gdt391_complete_unit_frame.tsv"
FREEZE = ART / "gdt391_pre_normalization_freeze.json"
OUT = ART / "gdt391_pre_normalization_freeze_validation.json"
CHANNELS = {"HUMAN_REL_ATTACHMENT", "HUMAN_REL_CONTACT", "HUMAN_REL_ENCLOSURE", "HUMAN_REL_ARRAY_GROUP"}
STRONG = {"REL_EXPLICIT_ATTACHMENT", "REL_OVERLAP_OR_CONTACT", "REL_ENCLOSURE", "REL_ARRAY_OR_GROUP"}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(payload: dict) -> str:
    clone = dict(payload)
    clone.pop("content_hash", None)
    return hashlib.sha256(json.dumps(clone, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> int:
    checks: list[dict[str, object]] = []

    def check(name: str, passed: bool, detail: object) -> None:
        checks.append({"check": name, "pass": bool(passed), "detail": detail})
        if not passed:
            raise AssertionError(f"{name}: {detail}")

    with SOURCE.open(encoding="utf-8", newline="") as handle:
        source_rows = [row for row in csv.DictReader(handle, delimiter="\t") if row["channel"] in CHANNELS]
    check("source_relation_rows", len(source_rows) == 1059, len(source_rows))
    check("source_no_forbidden_selector", all(not row["page"].lower().startswith("f84") for row in source_rows), "zero f84")
    by_locus: dict[str, dict[str, object]] = {}
    consistent_locus_units = True
    for row in source_rows:
        entry = by_locus.setdefault(row["locus"], {"unit": row["array_id"], "page": row["page"], "folio": row["physical_folio"], "states": set()})
        consistent_locus_units = consistent_locus_units and entry["unit"] == row["array_id"]
        entry["states"].add(row["visual_state"])
    check("consistent_locus_units", consistent_locus_units, len(by_locus))
    strong_loci = {locus for locus, row in by_locus.items() if row["states"] & STRONG}
    units = {str(by_locus[locus]["unit"]) for locus in strong_loci}
    expected = {locus: row for locus, row in by_locus.items() if row["unit"] in units}
    frame = tsv(FRAME)
    freeze = json.loads(FREEZE.read_text(encoding="utf-8"))
    check("unique_source_loci", len(by_locus) == 335, len(by_locus))
    check("positive_loci", len(strong_loci) == 94, len(strong_loci))
    check("positive_units", len(units) == 44, len(units))
    check("complete_frame_180", len(frame) == len({row["locus"] for row in frame}) == len(expected) == 180, len(frame))
    check("frame_exact_loci", {row["locus"] for row in frame} == set(expected), len(expected))
    check("frame_exact_units", {row["array_id"] for row in frame} == units, len(units))
    check("frame_pages_folios", len({row["page"] for row in frame}) == 21 and len({row["physical_folio"] for row in frame}) == 12, "21/12")
    check("frame_no_forbidden_selector", all(not row["page"].lower().startswith("f84") for row in frame), "zero f84")
    check("frame_formal_seal", {row["formal_identity_access_state"] for row in frame} == {"SEALED"}, "SEALED")
    check("locus_order", [row["locus"] for row in frame] == freeze["frame"]["locus_review_order"], frame[:2])
    check("locus_order_hash_rule", freeze["frame"]["locus_review_order"] == sorted(expected, key=lambda value: hashlib.sha256(("GDT391_LOCUS_ORDER_V1|" + value).encode()).hexdigest()), "exact")
    check("unit_order_hash_rule", freeze["frame"]["unit_review_order"] == sorted(units, key=lambda value: hashlib.sha256(("GDT391_UNIT_ORDER_V1|" + value).encode()).hexdigest()), freeze["frame"]["unit_review_order"][:2])
    unit_counts = Counter(row["array_id"] for row in frame)
    unit_positive = Counter(str(expected[locus]["unit"]) for locus in strong_loci)
    mixed = {unit for unit in units if 0 < unit_positive[unit] < unit_counts[unit]}
    check("mixed_unit_capacity", len(mixed) == 23, len(mixed))
    check("mixed_folio_capacity", len({row["physical_folio"] for row in frame if row["array_id"] in mixed}) == 8, "8")
    check("freeze_content_hash", freeze["content_hash"] == digest(freeze), freeze["content_hash"])
    check("freeze_counts", freeze["frame"]["source_relation_rows"] == 1059 and freeze["frame"]["unique_source_loci"] == 335 and freeze["frame"]["positive_unique_loci"] == 94 and freeze["frame"]["positive_source_units"] == 44 and freeze["frame"]["complete_unit_loci"] == 180, freeze["frame"])
    check("freeze_not_scored", freeze["scoring_authorized"] is False, False)
    check("freeze_access", freeze["access"]["voynich_surface_or_formal_identity_access"] is False and freeze["access"]["image_access_after_this_freeze"] is False and freeze["access"]["f84_access"] is False, freeze["access"])
    for path, expected_hash in freeze["inputs"].items():
        check("input_hash_" + Path(path).name, sha(ROOT / path) == expected_hash, expected_hash)
    for path, expected_hash in freeze["outputs"].items():
        check("output_hash_" + Path(path).name, sha(ROOT / path) == expected_hash, expected_hash)
    for path, expected_hash in freeze["implementation"].items():
        check("implementation_hash_" + Path(path).name, sha(ROOT / path) == expected_hash, expected_hash)

    payload = {
        "schema": "GDT391_PRE_NORMALIZATION_FREEZE_VALIDATION_V1",
        "status": "PASS",
        "scope": "INDEPENDENT_SOURCE_FRAME_SELECTION_ORDER_HASH_ACCESS_AND_CAPACITY_VALIDATION",
        "checks_passed": len(checks),
        "checks_total": len(checks),
        "freeze_content_hash": freeze["content_hash"],
        "checks": checks,
    }
    payload["content_hash"] = digest(payload)
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(f"PASS {len(checks)}/{len(checks)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
