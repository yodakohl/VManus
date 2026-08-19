#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
EXP = ROOT / "experiments/yolo/gdt349_zodiac_facing_orientation_acquisition"
SRC = ROOT / "experiments/semantic_assumptions/results/zodiac_label_cycle_capacity.tsv"
PRIOR = ROOT / "experiments/semantic_assumptions/results/public_zodiac_label_attribute_capacity.json"
OUT = EXP / "artifacts/gdt349_selection.tsv"
FREEZE = EXP / "artifacts/gdt349_freeze.json"

FIELDS = [
    "target_id", "page", "physical_folio", "ring_scope", "grove_ordinal",
    "source_record_id", "current_locus", "review_state", "review_confidence",
    "review_provenance", "official_canvas_id", "official_image_sha256",
    "neutral_note",
]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def stable_id(row: dict[str, str]) -> str:
    key = "|".join((row["page"], row["ring_scope"], row["grove_ordinal"], row["current_locus"]))
    return "G349" + hashlib.sha256(key.encode()).hexdigest()[:12].upper()


def main() -> None:
    with SRC.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f, delimiter="\t"))
    assert len(rows) == 235
    assert not any(r["page"].lower().startswith("f84") for r in rows)
    assert len({(r["page"], r["ring_scope"], r["grove_ordinal"]) for r in rows}) == 235
    out = []
    for r in rows:
        out.append({
            "target_id": stable_id(r),
            "page": r["page"],
            "physical_folio": r["physical_folio"],
            "ring_scope": r["ring_scope"],
            "grove_ordinal": r["grove_ordinal"],
            "source_record_id": r["source_record_id"],
            "current_locus": r["current_locus"],
            "review_state": "SEALED_UNREVIEWED",
            "review_confidence": "NOT_REVIEWED",
            "review_provenance": "PENDING_AI_DIRECT_VISUAL_OBSERVATION",
            "official_canvas_id": "PENDING",
            "official_image_sha256": "PENDING",
            "neutral_note": "PENDING_COMPLETE_CENSUS",
        })
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, delimiter="\t", fieldnames=FIELDS, lineterminator="\n")
        w.writeheader(); w.writerows(out)
    freeze = {
        "experiment": "GDT349_ZODIAC_FACING_ORIENTATION_ACQUISITION",
        "status": "FROZEN_BEFORE_NEW_IMAGE_REVIEW",
        "panel_rows": 235,
        "pages": sorted({r["page"] for r in out}),
        "physical_folios": sorted({r["physical_folio"] for r in out}),
        "allowed_states": ["PROFILE_LEFT", "PROFILE_RIGHT", "FRONTAL_OR_NON_DIRECTIONAL", "UNCERTAIN"],
        "capacity_gates": {
            "minimum_each_direction": 12,
            "minimum_folios_each_direction": 2,
            "minimum_mixed_page_ring_strata": 3,
            "minimum_folios_with_mixed_strata": 2,
            "maximum_uncertain_fraction": 0.20,
            "complete_census_rows": 235,
        },
        "inputs": {
            str(SRC.relative_to(ROOT)): sha(SRC),
            str(PRIOR.relative_to(ROOT)): sha(PRIOR),
            "experiments/yolo/gdt349_zodiac_facing_orientation_acquisition/METHOD.md": sha(EXP / "METHOD.md"),
            "experiments/yolo/gdt349_zodiac_facing_orientation_acquisition/SOURCE_AUDIT.md": sha(EXP / "SOURCE_AUDIT.md"),
            "experiments/yolo/gdt349_zodiac_facing_orientation_acquisition/CORRECTION.md": sha(EXP / "CORRECTION.md"),
        },
        "selection_sha256": sha(OUT),
        "f84": {"eligible": False, "rows_retained": 0, "access_authorized": False},
        "claim_ceiling": "Text-blind visual-capacity acquisition only; no label ownership, direction word, semantics, language, plaintext, or translation.",
    }
    FREEZE.write_text(json.dumps(freeze, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
