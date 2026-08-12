#!/usr/bin/env python3
"""Freeze a filler-blind complete special-circle star-ray visual census."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent.parent
METHOD = BASE / "SRE001_SPECIAL_CIRCLE_STAR_RAY_EXTENSION_METHOD.md"
SOURCE = BASE / "results/existing_human_exact_locus_annotations.tsv"
OUT = BASE / "results/sre001_special_circle_star_ray_extension_selection.json"
REPORT = BASE / "results/sre001_special_circle_star_ray_extension_selection_report.md"
SOURCE_SHA = "79c7f06e91f90054aff4cdf27f098a5977d820acdf91f239a14c6ddf553a7f61"
MANIFEST_SHA = "317d58fd9ea90392a83d9858a91eada3d0b41416a3c835857dc0154bd123a309"
CANVAS = {
    "f69r": ("1006198", [2793, 3763]),
    "f72r1": ("1006203", [8865, 3018]),
    "f72r2": ("1006203", [8865, 3018]),
    "f73r": ("1006206", [2834, 3761]),
    "f73v": ("1006207", [2979, 3724]),
}
OUTCOMES = [
    "SINGULAR_STAR_OWNED_RAY_COUNTABLE",
    "SINGULAR_STAR_OWNED_RAY_UNCOUNTABLE",
    "SLOT_OR_GROUP_ONLY",
    "NON_STAR_OBJECT",
    "LOCALIZATION_UNRESOLVED",
]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def folio(page: str) -> str:
    match = re.match(r"(f\d+)", page)
    assert match
    return match.group(1)


def canonical(obj: object) -> bytes:
    return (json.dumps(obj, sort_keys=True, separators=(",", ":")) + "\n").encode()


def selected(row: dict[str, str]) -> bool:
    if folio(row["page"]) not in {"f67", "f69", "f71", "f72", "f73"}:
        return False
    tags = set(filter(None, row["object_tags"].split(";")))
    rels = set(filter(None, (row["local_relation_tags"] + ";" + row["unit_relation_tags"]).split(";")))
    return {"STAR_OR_SKY", "LABEL"} <= tags and "REL_EXPLICIT_ATTACHMENT" in rels


def report_text(result: dict) -> str:
    return (
        "# SRE001 special-circle star-ray extension selection\n\n"
        f"Status: **{result['status']}**.\n\n"
        "The complete filler-blind source rule retains **24** candidate inscriptions on "
        "three new physical folios: six f69r/K1 rows, ten f72 rows, and eight f73 rows. "
        "They are bound to four exact official Yale canvases. No Voynich label surface, "
        "source group, formal family/member, parser root/role, or ray-count outcome was opened.\n\n"
        "Inspect the targets once in frozen opaque order. Reopen the stopped f68 association "
        "route only if one new folio supplies at least eight singular star-owned countable "
        "labels, at least two ray counts with three examples each, and no page above 75% of "
        "that folio's qualifying rows.\n\n"
        f"Claim ceiling: {result['claim_ceiling']}\n"
    )


def main() -> None:
    if OUT.exists() or REPORT.exists():
        raise SystemExit("refusing overwrite")
    if sha(SOURCE) != SOURCE_SHA:
        raise SystemExit("source hash mismatch")
    with SOURCE.open(encoding="utf-8", newline="") as handle:
        rows = [row for row in csv.DictReader(handle, delimiter="\t") if selected(row)]
    counts = Counter(row["page"] for row in rows)
    expected = Counter({"f69r": 6, "f72r1": 5, "f72r2": 5, "f73r": 4, "f73v": 4})
    if counts != expected:
        raise SystemExit(f"selection drift: {counts}")
    targets = []
    for row in rows:
        page, locus = row["page"], row["locus"]
        canvas_id, dims = CANVAS[page]
        targets.append({
            "opaque_id": "SR" + hashlib.sha256(f"SRE001|{page}|{locus}".encode()).hexdigest()[:10].upper(),
            "page": page,
            "physical_folio": folio(page),
            "locus": locus,
            "unit": row["unit"],
            "human_certainty": row["certainty"],
            "relation_scope": row["relation_scope"],
            "canvas_id": canvas_id,
            "official_dimensions": dims,
            "review_image_url": f"https://collections.library.yale.edu/iiif/2/{canvas_id}/full/full/0/default.jpg",
        })
    targets.sort(key=lambda row: row["opaque_id"])
    result = {
        "experiment": "SRE001_SPECIAL_CIRCLE_STAR_RAY_EXTENSION_SELECTION",
        "schema": "SRE001_SELECTION_V1",
        "status": "FROZEN_COMPLETE_TWENTY_FOUR_TARGET_THREE_FOLIO_PANEL_BEFORE_IMAGE_ACCESS",
        "decision": "AUTHORIZE_ONE_PASS_SOURCE_BOUND_NATIVE_VISUAL_CAPACITY_CENSUS",
        "selection_rule": "special-circle f67/f69/f71/f72/f73; STAR_OR_SKY and LABEL tags; REL_EXPLICIT_ATTACHMENT in local-or-unit relation",
        "counts": {
            "targets": len(targets),
            "physical_folios": len({row["physical_folio"] for row in targets}),
            "canvases": len({row["canvas_id"] for row in targets}),
            "by_page": dict(sorted(counts.items())),
            "by_folio": dict(sorted(Counter(row["physical_folio"] for row in targets).items())),
        },
        "targets": targets,
        "outcomes": OUTCOMES,
        "capacity_rule": {
            "minimum_countable_singular_owned_on_one_new_folio": 8,
            "minimum_distinct_ray_counts": 2,
            "minimum_examples_in_each_of_two_counts": 3,
            "maximum_one_page_share": 0.75,
        },
        "inputs": {
            str(METHOD.relative_to(ROOT)): sha(METHOD),
            str(SOURCE.relative_to(ROOT)): SOURCE_SHA,
            "yale_manifest_2002046_sha256": MANIFEST_SHA,
        },
        "access": {
            "target_image_bodies_opened": False,
            "voynich_label_surfaces_opened": False,
            "formal_features_opened": False,
            "prior_full_canvas_exposure_disclosed": True,
            "ocr_clip_embedding_or_automated_vision_used": False,
        },
        "claim_ceiling": (
            "This freezes a complete visual capacity census only. A pass cannot establish that any label "
            "encodes ray count, a number, star name, sound, language, cipher, plaintext, meaning, or translation."
        ),
    }
    OUT.write_bytes(canonical(result))
    REPORT.write_text(report_text(result), encoding="utf-8")


if __name__ == "__main__":
    main()
