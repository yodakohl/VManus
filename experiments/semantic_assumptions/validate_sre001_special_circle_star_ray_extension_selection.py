#!/usr/bin/env python3
"""Compact independent reconstruction of the SRE001 source-only selection."""

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
RESULT = BASE / "results/sre001_special_circle_star_ray_extension_selection.json"
REPORT = BASE / "results/sre001_special_circle_star_ray_extension_selection_report.md"
OUT = BASE / "results/sre001_special_circle_star_ray_extension_selection_validation.json"
MANIFEST_SHA = "317d58fd9ea90392a83d9858a91eada3d0b41416a3c835857dc0154bd123a309"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def physical(page: str) -> str:
    return re.match(r"(f\d+)", page).group(1)  # type: ignore[union-attr]


def canonical(obj: object) -> bytes:
    return (json.dumps(obj, sort_keys=True, separators=(",", ":")) + "\n").encode()


def main() -> None:
    if OUT.exists():
        raise SystemExit("refusing overwrite")
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    with SOURCE.open(encoding="utf-8", newline="") as handle:
        source_rows = []
        for row in csv.DictReader(handle, delimiter="\t"):
            tags = set(filter(None, row["object_tags"].split(";")))
            rels = set(filter(None, (row["local_relation_tags"] + ";" + row["unit_relation_tags"]).split(";")))
            if physical(row["page"]) in {"f67", "f69", "f71", "f72", "f73"} and {"STAR_OR_SKY", "LABEL"} <= tags and "REL_EXPLICIT_ATTACHMENT" in rels:
                source_rows.append(row)
    source_keys = {(row["page"], row["locus"], row["unit"], row["certainty"], row["relation_scope"]) for row in source_rows}
    stored_keys = {(row["page"], row["locus"], row["unit"], row["human_certainty"], row["relation_scope"]) for row in result["targets"]}
    expected_page = Counter({"f69r": 6, "f72r1": 5, "f72r2": 5, "f73r": 4, "f73v": 4})
    checks = {
        "canonical_result": RESULT.read_bytes() == canonical(result),
        "complete_source_rule": source_keys == stored_keys and len(source_keys) == 24,
        "exact_page_counts": Counter(row["page"] for row in source_rows) == expected_page,
        "three_physical_folios_four_canvases": {row["physical_folio"] for row in result["targets"]} == {"f69", "f72", "f73"} and len({row["canvas_id"] for row in result["targets"]}) == 4,
        "opaque_order_and_uniqueness": [row["opaque_id"] for row in result["targets"]] == sorted(row["opaque_id"] for row in result["targets"]) and len({row["opaque_id"] for row in result["targets"]}) == 24,
        "exact_capacity_rule": result["capacity_rule"] == {"minimum_countable_singular_owned_on_one_new_folio": 8, "minimum_distinct_ray_counts": 2, "minimum_examples_in_each_of_two_counts": 3, "maximum_one_page_share": 0.75},
        "sealed_access": result["access"] == {"target_image_bodies_opened": False, "voynich_label_surfaces_opened": False, "formal_features_opened": False, "prior_full_canvas_exposure_disclosed": True, "ocr_clip_embedding_or_automated_vision_used": False},
        "input_bindings": result["inputs"] == {str(METHOD.relative_to(ROOT)): sha(METHOD), str(SOURCE.relative_to(ROOT)): sha(SOURCE), "yale_manifest_2002046_sha256": MANIFEST_SHA},
        "report_and_ceiling": REPORT.exists() and all(word in result["claim_ceiling"] for word in ("number", "meaning", "translation")),
    }
    if not all(checks.values()):
        raise SystemExit({key: value for key, value in checks.items() if not value})
    validation = {
        "experiment": "SRE001_SPECIAL_CIRCLE_STAR_RAY_EXTENSION_SELECTION_VALIDATION",
        "status": "PASS_9_CHECK_COMPLETE_SOURCE_ONLY_SELECTION_RECONSTRUCTION",
        "check_count": len(checks),
        "checks": list(checks),
        "source_result_sha256": sha(RESULT),
        "source_report_sha256": sha(REPORT),
        "claim_ceiling": "Validation authorizes one frozen native-visual capacity census and supplies no number, word, meaning, or translation.",
    }
    OUT.write_bytes(canonical(validation))


if __name__ == "__main__":
    main()
