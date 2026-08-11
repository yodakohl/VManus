#!/usr/bin/env python3
"""Cheap ownership screen for human ray-counted attached-star labels."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

BASE = Path(__file__).resolve().parent
SOURCE = BASE / "results/existing_human_exact_locus_annotations.tsv"
OUT = BASE / "results/star_label_ray_ownership_preflight.json"
REPORT = BASE / "results/star_label_ray_ownership_preflight_report.md"
SOURCE_SHA = "79c7f06e91f90054aff4cdf27f098a5977d820acdf91f239a14c6ddf553a7f61"
RAY = re.compile(r"\b(?:five|six|seven|eight|nine|\d+) points?\b", re.I)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def report_text(result: dict) -> str:
    return (
        "# Direct star-label ray-count ownership preflight\n\n"
        f"Status: **{result['status']}**\n\n"
        "The human atlas contains 63 ray-counted label rows: 29 on f68r1, 24 on f68r2, and 10 on f70v1. "
        "The 53 f68 rows belong to one physical folio. All ten f70v1 rows are hedged object-context records, "
        "and source-bound inspection finds no leader, enclosure, reserved cell, or other singular label/star connector.\n\n"
        "The route stops before label surfaces or formal features are opened.\n\n"
        f"Claim ceiling: {result['claim_ceiling']}\n"
    )


def main() -> None:
    if OUT.exists() or REPORT.exists():
        raise SystemExit("refusing overwrite")
    if sha(SOURCE) != SOURCE_SHA:
        raise SystemExit("source hash mismatch")
    with SOURCE.open(encoding="utf-8", newline="") as handle:
        candidates = [
            row for row in csv.DictReader(handle, delimiter="\t")
            if RAY.search(row["local_comment"]) and "LABEL" in row["object_tags"].split(";")
        ]
    by_page = Counter(row["page"] for row in candidates)
    by_folio: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in candidates:
        by_folio["f68" if row["page"].startswith("f68") else "f70"].append(row)
    strong = [
        row for row in candidates
        if row["certainty"] == "UNHEDGED"
        and row["relation_scope"] == "EXACT_LOCAL_COMMENT"
        and "REL_EXPLICIT_ATTACHMENT" in row["local_relation_tags"].split(";")
    ]
    strong_by_folio = Counter("f68" if row["page"].startswith("f68") else "f70" for row in strong)
    f70_rows = [row for row in candidates if row["page"] == "f70v1"]
    gates = {
        "exact_candidate_census": len(candidates) == 63 and by_page == Counter({"f68r1": 29, "f68r2": 24, "f70v1": 10}),
        "two_physical_folios_present": set(by_folio) == {"f68", "f70"},
        "at_least_eight_strong_singular_attachments_per_folio": all(strong_by_folio[folio] >= 8 for folio in ("f68", "f70")),
        "all_f70_source_rows_are_hedged_context_only": len(f70_rows) == 10 and all(
            row["certainty"] == "HEDGED"
            and row["relation_scope"] == "OBJECT_CONTEXT_ONLY"
            and "REL_EXPLICIT_ATTACHMENT" not in row["local_relation_tags"].split(";")
            and "REL_EXPLICIT_ATTACHMENT" not in row["unit_relation_tags"].split(";")
            for row in f70_rows
        ),
        "native_f70_has_no_author_visible_singular_connector": False,
        "zero_label_surfaces_or_formal_features_opened": True,
    }
    status = "STOP_UNSCORED_NO_SECOND_FOLIO_SINGULAR_OWNERSHIP"
    result = {
        "experiment": "DIRECT_STAR_LABEL_RAY_OWNERSHIP_PREFLIGHT",
        "status": status,
        "decision": status,
        "inputs": {
            "results/existing_human_exact_locus_annotations.tsv": SOURCE_SHA,
            "yale_canvas_1006201_f70v1_sha256": "c8f24b6be5451aba49eb793784c43cb7fc8341dca8a58ff43fc1eebf4877b60c",
            "yale_manifest_2002046_sha256": "317d58fd9ea90392a83d9858a91eada3d0b41416a3c835857dc0154bd123a309",
        },
        "counts": {
            "candidate_rows": len(candidates),
            "candidate_by_page": dict(sorted(by_page.items())),
            "candidate_by_physical_folio": {key: len(value) for key, value in sorted(by_folio.items())},
            "strong_singular_attachment_by_physical_folio": dict(sorted(strong_by_folio.items())),
            "f70_hedged_context_only_rows": len(f70_rows),
            "label_surfaces_opened": 0,
            "formal_features_constructed": 0,
            "associations_scored": 0,
        },
        "native_visual_observation": (
            "f70v1 places stars, figures, and labels in the same annuli, but shows no leader, enclosure, "
            "reserved cell, or sector boundary fixing each label to one counted star."
        ),
        "gates": gates,
        "claim_ceiling": (
            "This prescore ownership stop establishes no number, ray-count word, star name, sound, "
            "language, cipher, plaintext, meaning, or translation."
        ),
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT.write_text(report_text(result), encoding="utf-8")


if __name__ == "__main__":
    main()
