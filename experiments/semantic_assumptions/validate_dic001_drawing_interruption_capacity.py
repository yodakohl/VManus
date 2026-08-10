#!/usr/bin/env python3
"""Independent reconstruction of DIC001 target-masked capacity."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import re
from collections import Counter
from pathlib import Path


BASE = Path(__file__).resolve().parent
R = BASE / "results"
SOURCE = R / "source_native_structural_interlinear_v1.tsv"
SPEC = BASE / "DIC001_DRAWING_INTERRUPTION_CAPACITY_SPEC.md"
PRODUCER = BASE / "audit_dic001_drawing_interruption_capacity.py"
PANEL = R / "dic001_drawing_interruption_capacity.tsv"
RESULT = R / "dic001_drawing_interruption_capacity.json"
REPORT = R / "dic001_drawing_interruption_capacity_report.md"
OUT = R / "dic001_drawing_interruption_capacity_validation.json"
OUT_REPORT = R / "dic001_drawing_interruption_capacity_validation_report.md"
SOURCE_SHA = "95a15329c61a11c1c4dc671b4df2b3482af9d25a1108eadac2f69b066d3785af"
DRAW = "ZL3b:DRAWING_INTERRUPTION;IT2a:DRAWING_INTERRUPTION;RF1b:DRAWING_INTERRUPTION"
SPACE = "ZL3b:DEFINITE_SPACE;IT2a:DEFINITE_SPACE;RF1b:DEFINITE_SPACE"
FIELDS = ["boundary_id", "locus", "page", "physical_folio", "section", "currier", "hand", "code", "kind", "left_group_index", "right_group_index", "group_count", "normalized_boundary_position", "boundary_class"]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def physical(page: str) -> str:
    match = re.fullmatch(r"(f\d+)(?:[rv].*)?", page)
    if match is None: raise AssertionError(page)
    return match.group(1)


def reconstruct(source_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    base = []
    pages = set()
    seen = set()
    for row in source_rows:
        identity = row["consensus_group_id"]
        assert identity not in seen
        seen.add(identity)
        profile = row["right_boundary_profile"]
        if row["grammar_scope"] != "CONFIRMED_PROSE" or profile not in {DRAW, SPACE}:
            continue
        left = int(row["group_index"]); count = int(row["group_count"])
        assert left < count
        record = {
            "boundary_id": f"{row['locus']}|B{left:03d}", "locus": row["locus"], "page": row["page"],
            "physical_folio": physical(row["page"]), "section": row["section"], "currier": row["currier"],
            "hand": row["hand"], "code": row["code"], "kind": row["kind"], "left_group_index": str(left),
            "right_group_index": str(left + 1), "group_count": str(count),
            "normalized_boundary_position": f"{left / count:.12f}",
            "boundary_class": "DRAWING_INTERRUPTION" if profile == DRAW else "DEFINITE_SPACE",
        }
        base.append(record)
        if profile == DRAW: pages.add(row["page"])
    return [record for record in base if record["page"] in pages]


def main() -> None:
    checks = 0
    assert sha(SOURCE) == SOURCE_SHA; checks += 1
    with SOURCE.open(encoding="utf-8", newline="") as handle:
        source_rows = list(csv.DictReader(handle, delimiter="\t"))
    panel = reconstruct(source_rows)
    checks += len(source_rows)
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=FIELDS, delimiter="\t", lineterminator="\n")
    writer.writeheader(); writer.writerows(panel)
    expected_tsv = buffer.getvalue().encode()
    assert PANEL.read_bytes() == expected_tsv; checks += len(panel)
    assert len({row["boundary_id"] for row in panel}) == len(panel); checks += 1
    targets = [row for row in panel if row["boundary_class"] == "DRAWING_INTERRUPTION"]
    controls = [row for row in panel if row["boundary_class"] == "DEFINITE_SPACE"]
    folios = Counter(row["physical_folio"] for row in targets)
    sections = Counter(row["section"] for row in targets)
    curriers = Counter(row["currier"] for row in targets)
    control_folios = {row["physical_folio"] for row in controls}
    gates = {
        "target_boundaries_at_least_200": len(targets) >= 200,
        "target_folios_at_least_30": len(folios) >= 30,
        "target_pages_at_least_50": len({row["page"] for row in targets}) >= 50,
        "two_currier_registers": set(curriers) >= {"A", "B"},
        "three_sections": len(sections) >= 3,
        "maximum_target_folio_share_at_most_015": max(folios.values()) / len(targets) <= .15,
        "every_target_folio_has_control": set(folios) <= control_folios,
        "twenty_folios_with_at_least_five_targets": sum(n >= 5 for n in folios.values()) >= 20,
        "target_mask_contains_no_structural_identity": set(FIELDS).isdisjoint({"family_surface", "sta_codes", "eva", "root", "role"}),
    }
    stored = json.loads(RESULT.read_text())
    expected_counts = {
        "panel_boundaries": len(panel), "target_boundaries": len(targets), "control_boundaries": len(controls),
        "target_pages": len({row["page"] for row in targets}), "target_folios": len(folios),
        "folios_at_least_two_targets": sum(n >= 2 for n in folios.values()),
        "folios_at_least_three_targets": sum(n >= 3 for n in folios.values()),
        "folios_at_least_five_targets": sum(n >= 5 for n in folios.values()),
        "folios_at_least_ten_targets": sum(n >= 10 for n in folios.values()),
        "maximum_target_folio_count": max(folios.values()),
        "maximum_target_folio_share": max(folios.values()) / len(targets),
        "target_sections": dict(sorted(sections.items())), "target_curriers": dict(sorted(curriers.items())),
    }
    assert stored["counts"] == expected_counts; checks += len(expected_counts)
    assert stored["gates"] == gates and all(gates.values()); checks += len(gates)
    assert stored["panel_sha256"] == hashlib.sha256(expected_tsv).hexdigest(); checks += 1
    assert stored["inputs"] == {SOURCE.name: sha(SOURCE), SPEC.name: sha(SPEC), PRODUCER.name: sha(PRODUCER)}; checks += 3
    assert stored["status"] == "PASS_SCORE_BLIND_MULTI_FOLIO_CAPACITY"
    assert stored["decision"] == "AUTHORIZE_TARGET_BLIND_DIC001_INSTRUMENT_ONLY"
    assert stored["target_identity_fields_accessed"] is False and stored["ocr_or_image_features_accessed"] is False and stored["english_glosses"] == 0
    checks += 5
    expected_report = (
        "# DIC001 drawing-interruption continuity capacity\n\n"
        f"Status: **{stored['status']}**.\n\n"
        f"The source-native panel has **{expected_counts['target_boundaries']}** unanimous drawing interruptions on **{expected_counts['target_pages']}** pages and **{expected_counts['target_folios']}** physical folios, plus **{expected_counts['control_boundaries']:,}** unanimous ordinary spaces on the same pages. **{expected_counts['folios_at_least_five_targets']}** folios have at least five targets; the largest folio supplies only **{expected_counts['maximum_target_folio_share']:.2%}**. Targets span Currier A/B and sections {', '.join(expected_counts['target_sections'])}.\n\n"
        "This repairs an important methodological blind spot: the older parser concatenated across aligned drawing interruptions, but the manuscript has enough source-native evidence to test continuity versus restart without that assumption. No family identity or target grammar score was opened.\n\n"
        "The pass authorizes only target-blind instrument calibration and independent reconstruction. It establishes no continuity result, ownership, word, sound, POS, meaning, plaintext, language, cipher, or translation.\n"
    )
    assert REPORT.read_text() == expected_report; checks += 1
    validation = {
        "experiment": "DIC001_DRAWING_INTERRUPTION_CAPACITY_VALIDATION",
        "status": "PASS_INDEPENDENT_TARGET_MASK_RECONSTRUCTION", "checks": checks,
        "source_rows": len(source_rows), "panel_boundaries": len(panel),
        "target_boundaries": len(targets), "control_boundaries": len(controls),
        "target_pages": expected_counts["target_pages"], "target_folios": len(folios),
        "bindings": {path.name: sha(path) for path in (SOURCE, SPEC, PRODUCER, PANEL, RESULT, REPORT)},
        "target_identity_fields_accessed": False, "ocr_or_image_features_accessed": False,
        "english_glosses": 0,
        "claim_ceiling": "Independent capacity reconstruction only; no continuity result, word, sound, POS, meaning, plaintext, language, cipher, or translation.",
    }
    OUT.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_REPORT.write_text(
        "# DIC001 capacity validation\n\n"
        f"Status: **{validation['status']}**.\n\n"
        f"Independent code passed **{checks:,}** checks and reconstructed all **{len(panel):,}** masked boundaries, including **{len(targets)}** drawing interruptions on **{len(folios)}** physical folios, exact gates, bytes, bindings, and report.\n\n"
        "This validates score-blind capacity only and supplies no continuity result, word, meaning, plaintext, or translation.\n",
        encoding="utf-8",
    )
    print(json.dumps(validation, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
