#!/usr/bin/env python3
"""Build the target-masked DIC001 drawing-interruption capacity panel."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


BASE = Path(__file__).resolve().parent
RESULTS = BASE / "results"
SOURCE = RESULTS / "source_native_structural_interlinear_v1.tsv"
SPEC = BASE / "DIC001_DRAWING_INTERRUPTION_CAPACITY_SPEC.md"
SCRIPT = Path(__file__).resolve()
OUT_TSV = RESULTS / "dic001_drawing_interruption_capacity.tsv"
OUT_JSON = RESULTS / "dic001_drawing_interruption_capacity.json"
OUT_REPORT = RESULTS / "dic001_drawing_interruption_capacity_report.md"
SOURCE_SHA = "95a15329c61a11c1c4dc671b4df2b3482af9d25a1108eadac2f69b066d3785af"
DRAW = "ZL3b:DRAWING_INTERRUPTION;IT2a:DRAWING_INTERRUPTION;RF1b:DRAWING_INTERRUPTION"
SPACE = "ZL3b:DEFINITE_SPACE;IT2a:DEFINITE_SPACE;RF1b:DEFINITE_SPACE"
FIELDS = (
    "boundary_id", "locus", "page", "physical_folio", "section", "currier",
    "hand", "code", "kind", "left_group_index", "right_group_index",
    "group_count", "normalized_boundary_position", "boundary_class",
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def folio(page: str) -> str:
    match = re.match(r"^(f\d+)", page)
    if not match: raise ValueError(f"bad page {page}")
    return match.group(1)


def main() -> None:
    if sha(SOURCE) != SOURCE_SHA: raise SystemExit("source interlinear drift")
    with SOURCE.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    allowed = {
        "consensus_group_id", "locus", "page", "section", "currier", "hand",
        "code", "kind", "grammar_scope", "group_index", "group_count",
        "right_boundary_profile", "right_boundary_support",
    }
    if not allowed.issubset(rows[0]): raise SystemExit("required metadata fields missing")
    candidates = []
    target_pages = set()
    for row in rows:
        if row["grammar_scope"] != "CONFIRMED_PROSE" or row["right_boundary_profile"] == "LINE_END":
            continue
        profile = row["right_boundary_profile"]
        if profile not in {DRAW, SPACE}: continue
        index, count = int(row["group_index"]), int(row["group_count"])
        if not (1 <= index < count): raise SystemExit(f"bad internal boundary {row['consensus_group_id']}")
        item = {
            "boundary_id": f"{row['locus']}|B{index:03d}", "locus": row["locus"],
            "page": row["page"], "physical_folio": folio(row["page"]),
            "section": row["section"], "currier": row["currier"], "hand": row["hand"],
            "code": row["code"], "kind": row["kind"], "left_group_index": str(index),
            "right_group_index": str(index + 1), "group_count": str(count),
            "normalized_boundary_position": format(index / count, ".12f"),
            "boundary_class": "DRAWING_INTERRUPTION" if profile == DRAW else "DEFINITE_SPACE",
        }
        candidates.append(item)
        if profile == DRAW: target_pages.add(row["page"])
    panel = [item for item in candidates if item["page"] in target_pages]
    if len({item["boundary_id"] for item in panel}) != len(panel): raise SystemExit("duplicate boundary id")
    targets = [item for item in panel if item["boundary_class"] == "DRAWING_INTERRUPTION"]
    controls = [item for item in panel if item["boundary_class"] == "DEFINITE_SPACE"]
    target_folios = Counter(item["physical_folio"] for item in targets)
    control_folios = {item["physical_folio"] for item in controls}
    target_sections = Counter(item["section"] for item in targets)
    target_curriers = Counter(item["currier"] for item in targets)
    gates = {
        "target_boundaries_at_least_200": len(targets) >= 200,
        "target_folios_at_least_30": len(target_folios) >= 30,
        "target_pages_at_least_50": len({item["page"] for item in targets}) >= 50,
        "two_currier_registers": set(target_curriers) >= {"A", "B"},
        "three_sections": len(target_sections) >= 3,
        "maximum_target_folio_share_at_most_015": max(target_folios.values()) / len(targets) <= .15,
        "every_target_folio_has_control": set(target_folios) <= control_folios,
        "twenty_folios_with_at_least_five_targets": sum(value >= 5 for value in target_folios.values()) >= 20,
        "target_mask_contains_no_structural_identity": set(FIELDS).isdisjoint({"family_surface", "sta_codes", "eva", "root", "role"}),
    }
    if not all(gates.values()): raise SystemExit(f"capacity stop: {gates}")
    with OUT_TSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, delimiter="\t", lineterminator="\n")
        writer.writeheader(); writer.writerows(panel)
    result = {
        "experiment": "DIC001_DRAWING_INTERRUPTION_CAPACITY",
        "status": "PASS_SCORE_BLIND_MULTI_FOLIO_CAPACITY",
        "inputs": {SOURCE.name: sha(SOURCE), SPEC.name: sha(SPEC), SCRIPT.name: sha(SCRIPT)},
        "counts": {
            "panel_boundaries": len(panel), "target_boundaries": len(targets),
            "control_boundaries": len(controls), "target_pages": len(target_pages),
            "target_folios": len(target_folios),
            "folios_at_least_two_targets": sum(value >= 2 for value in target_folios.values()),
            "folios_at_least_three_targets": sum(value >= 3 for value in target_folios.values()),
            "folios_at_least_five_targets": sum(value >= 5 for value in target_folios.values()),
            "folios_at_least_ten_targets": sum(value >= 10 for value in target_folios.values()),
            "maximum_target_folio_count": max(target_folios.values()),
            "maximum_target_folio_share": max(target_folios.values()) / len(targets),
            "target_sections": dict(sorted(target_sections.items())),
            "target_curriers": dict(sorted(target_curriers.items())),
        },
        "panel_sha256": sha(OUT_TSV), "gates": gates,
        "target_identity_fields_accessed": False, "ocr_or_image_features_accessed": False,
        "english_glosses": 0,
        "decision": "AUTHORIZE_TARGET_BLIND_DIC001_INSTRUMENT_ONLY",
        "claim_ceiling": "Capacity for a drawing-interruption continuity/restart test only; no continuity result, word, sound, POS, meaning, plaintext, language, cipher, or translation.",
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    c = result["counts"]
    OUT_REPORT.write_text(
        "# DIC001 drawing-interruption continuity capacity\n\n"
        f"Status: **{result['status']}**.\n\n"
        f"The source-native panel has **{c['target_boundaries']}** unanimous drawing interruptions on **{c['target_pages']}** pages and **{c['target_folios']}** physical folios, plus **{c['control_boundaries']:,}** unanimous ordinary spaces on the same pages. **{c['folios_at_least_five_targets']}** folios have at least five targets; the largest folio supplies only **{c['maximum_target_folio_share']:.2%}**. Targets span Currier A/B and sections {', '.join(c['target_sections'])}.\n\n"
        "This repairs an important methodological blind spot: the older parser concatenated across aligned drawing interruptions, but the manuscript has enough source-native evidence to test continuity versus restart without that assumption. No family identity or target grammar score was opened.\n\n"
        "The pass authorizes only target-blind instrument calibration and independent reconstruction. It establishes no continuity result, ownership, word, sound, POS, meaning, plaintext, language, cipher, or translation.\n",
        encoding="utf-8",
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
