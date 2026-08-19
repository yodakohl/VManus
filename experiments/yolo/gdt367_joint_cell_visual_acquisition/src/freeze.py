#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from tools.vmanus_experiment import canonical_json_bytes, sha256_file  # noqa:E402

EXP = ROOT / "experiments/yolo/gdt367_joint_cell_visual_acquisition"
ART = EXP / "artifacts"
FIRST_SEL = ROOT / "gdt002_contact_gap_selection.tsv"
FIRST_LOC = ROOT / "gdt002_contact_gap_localizations.tsv"
FIRST_OBS = ROOT / "gdt002_contact_gap_observations.tsv"
REPL_SEL = ROOT / "gdt002_contact_gap_replication_selection.tsv"
REPL_LOC = ROOT / "gdt002_contact_gap_replication_localizations.tsv"
REPL_OBS = ROOT / "gdt002_contact_gap_replication_observations.tsv"
SCHEMA = ART / "gdt367_annotation_schema.tsv"
OUT_TSV = ART / "gdt367_target_manifest.tsv"
OUT_JSON = ART / "gdt367_freeze.json"


def read(path: Path):
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main():
    ART.mkdir(parents=True, exist_ok=True)
    first_sel = {r["target_id"]: r for r in read(FIRST_SEL) if r["physical_folio"] == "f89"}
    first_loc = {r["target_id"]: r for r in read(FIRST_LOC) if r["physical_folio"] == "f89"}
    first_obs = {r["target_id"]: r for r in read(FIRST_OBS) if r["target_id"] in first_sel}
    repl_sel = {r["target_id"]: r for r in read(REPL_SEL)}
    repl_loc = {r["target_id"]: r for r in read(REPL_LOC)}
    repl_obs = {r["target_id"]: r for r in read(REPL_OBS)}
    assert len(first_sel) == len(first_loc) == len(first_obs) == 3
    assert len(repl_sel) == len(repl_loc) == len(repl_obs) == 24

    fields = [
        "gdt367_target_id", "source_target_id", "page", "physical_folio",
        "locus", "array_id", "ordinal", "canvas_id", "canvas_width",
        "canvas_height", "official_image_url", "full_image_sha256",
        "context_xywh", "target_xywh", "localizer_confidence",
        "contact_gap_state", "contact_gap_provenance", "contact_call_source",
        "new_visual_call_state",
    ]
    rows = []
    for source, sels, locs, obs in (
        ("INITIAL_F89", first_sel, first_loc, first_obs),
        ("COMPLETE_ARRAY_REPLICATION", repl_sel, repl_loc, repl_obs),
    ):
        for target_id, s in sels.items():
            l = locs[target_id]
            o = obs[target_id]
            ordinal = s.get("ordinal_in_complete_unit") or s.get("ordinal")
            state = o.get("consensus_state") or o.get("review_state")
            row = {
                "gdt367_target_id": "VG" + hashlib.sha256(s["locus"].encode()).hexdigest()[:14].upper(),
                "source_target_id": target_id,
                "page": s["page"],
                "physical_folio": s["physical_folio"],
                "locus": s["locus"],
                "array_id": s["array_id"],
                "ordinal": ordinal,
                "canvas_id": s["canvas_id"],
                "canvas_width": s.get("width", ""),
                "canvas_height": s.get("height", ""),
                "official_image_url": s["official_image_url"],
                "full_image_sha256": l["full_image_sha256"],
                "context_xywh": l["context_xywh"],
                "target_xywh": l["target_xywh"],
                "localizer_confidence": l["localizer_confidence"],
                "contact_gap_state": state,
                "contact_gap_provenance": o["provenance"],
                "contact_call_source": source,
                "new_visual_call_state": "NOT_YET_REVIEWED",
            }
            assert not row["page"].startswith("f84") and not row["locus"].startswith("f84")
            rows.append(row)
    rows.sort(key=lambda r: (r["page"], r["array_id"], int(r["ordinal"])))
    assert len(rows) == len({r["locus"] for r in rows}) == 27
    assert {r["array_id"] for r in rows} == {"F89R2_L4", "F99V_L1", "F99V_L2", "F100R_L2", "F100V_L1"}
    with OUT_TSV.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fields, delimiter="\t", lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)

    inputs = [FIRST_SEL, FIRST_LOC, FIRST_OBS, REPL_SEL, REPL_LOC, REPL_OBS, SCHEMA, EXP / "METHOD.md"]
    payload = {
        "schema": "GDT367_FREEZE_V1",
        "status": "POSTEXPOSURE_YOLO_ACQUISITION_FROZEN_BEFORE_NEW_VISUAL_CALLS",
        "target_count": 27,
        "physical_folios": sorted({r["physical_folio"] for r in rows}),
        "arrays": {a: sum(r["array_id"] == a for r in rows) for a in sorted({r["array_id"] for r in rows})},
        "contact_gap_counts": {s: sum(r["contact_gap_state"] == s for r in rows) for s in ("CONTACT", "CLEAR_GAP", "UNCERTAIN")},
        "new_axes": ["BROAD_CLOSED_FORM", "FORK_OR_BRANCH", "COLORED_FILL"],
        "selection_rule": "COMPLETE_CANONICAL_27_LOCUS_CONTACT_GAP_PANEL_NO_POST_IMAGE_DROPS",
        "formal_access_before_visual_freeze": False,
        "postexposure": True,
        "single_observer": True,
        "prior_image_exposure": True,
        "f84_accessed": False,
        "inputs": {str(p.relative_to(ROOT)): sha256_file(p) for p in inputs},
        "outputs": {str(OUT_TSV.relative_to(ROOT)): sha256_file(OUT_TSV)},
        "implementation": {str(Path(__file__).relative_to(ROOT)): sha256_file(Path(__file__))},
        "claim_ceiling": "COOBSERVED_ANONYMOUS_VISIBLE_GEOMETRY_FOR_EXPLORATORY_ASSOCIATION_ONLY",
    }
    assert payload["contact_gap_counts"] == {"CONTACT": 8, "CLEAR_GAP": 18, "UNCERTAIN": 1}
    payload["content_hash"] = hashlib.sha256(canonical_json_bytes(payload)).hexdigest()
    OUT_JSON.write_bytes(canonical_json_bytes(payload))


if __name__ == "__main__":
    main()
