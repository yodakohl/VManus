#!/usr/bin/env python3
"""Freeze the residual f84-free connector-census frame before image review."""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
sys.path.insert(0, str(ROOT / "tools"))

from vmanus_experiment import GuardedTSV, canonical_json_bytes, sha256_file  # noqa: E402


EXP = ROOT / "experiments/yolo/gdt393_remaining_page_connector_census"
ART = EXP / "artifacts"
ROLE = ROOT / "experiments/semantic_assumptions/results/existing_human_page_role_matrix.tsv"
OLD_FRAME = ROOT / "experiments/yolo/gdt388_acquisition_ready_relation_edge_protocol/artifacts/gdt388_page_frame.tsv"
FRAME = ART / "gdt393_residual_page_frame.tsv"
FREEZE = ART / "gdt393_pre_image_freeze.json"


def main() -> int:
    ART.mkdir(parents=True, exist_ok=True)
    with OLD_FRAME.open(encoding="utf-8", newline="") as handle:
        old_pages = {row["page"] for row in csv.DictReader(handle, delimiter="\t")}

    source = GuardedTSV(ROLE, selector_column="page", forbidden_prefixes=("f84",))
    rows = []
    for row in source:
        if row["page"] in old_pages or row["page"] == "fRos":
            continue
        role_count = sum(int(row[name] or 0) for name in ("L_count", "C_count", "R_count"))
        if role_count == 0:
            continue
        rows.append(
            {
                "page": row["page"],
                "section": row["section"],
                "currier": row["currier"],
                "hand": row["hand"],
                "P_count": row["P_count"],
                "L_count": row["L_count"],
                "C_count": row["C_count"],
                "R_count": row["R_count"],
                "source_tags": row["source_tags"],
                "review_scope": "VISIBLE_CONNECTOR_GEOMETRY_ONLY",
                "formal_access_state": "FORBIDDEN_BEFORE_CAPACITY_GATE",
            }
        )
    rows.sort(key=lambda row: row["page"])

    fields = list(rows[0])
    with FRAME.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    payload = {
        "experiment_id": "GDT393",
        "status": "PRE_IMAGE_FRAME_FROZEN",
        "selection_rule": "f84-free page-role rows outside GDT388 with L_count+C_count+R_count > 0, excluding the closed Rosettes connector/road route",
        "review_categories": [
            "NO_CONNECTOR_CANDIDATE",
            "AMBIGUOUS_CONNECTOR",
            "CONNECTOR_WITH_FEWER_THAN_TWO_EXACT_LABEL_LOCUS_ENDPOINTS",
            "CONNECTOR_WITH_TWO_OR_MORE_EXACT_LABEL_LOCUS_ENDPOINTS",
        ],
        "direction_rule": "ELIGIBLE only when visible geometry fixes an orientation between two distinct exact locus endpoints",
        "formal_access_before_capacity_gate": False,
        "minimum_capacity_edges": 50,
        "minimum_capacity_folios": 5,
        "frame_rows": len(rows),
        "frame_pages": len({row["page"] for row in rows}),
        "forbidden_rows_rejected_before_parse": source.stats.skipped_forbidden,
        "inputs": {
            str(ROLE.relative_to(ROOT)): sha256_file(ROLE),
            str(OLD_FRAME.relative_to(ROOT)): sha256_file(OLD_FRAME),
            str((EXP / "METHOD.md").relative_to(ROOT)): sha256_file(EXP / "METHOD.md"),
            str(Path(__file__).resolve().relative_to(ROOT)): sha256_file(Path(__file__).resolve()),
        },
        "outputs": {str(FRAME.relative_to(ROOT)): sha256_file(FRAME)},
        "f84_selector_guard": "RAW_PAGE_PREFIX_REJECTED_BEFORE_ROW_PARSE",
        "f84_formal_payload_opened": False,
        "f84_image_opened": False,
        "prior_workspace_audit_disclosure": "Before this freeze, an ad hoc capacity command split two forbidden page-description metadata rows before output filtering; neither row was displayed, selected, retained, scored, or used to define this frame. The authoritative freeze loader rejects the raw page selector before parsing the row.",
        "image_opened_before_freeze": False,
    }
    FREEZE.write_bytes(canonical_json_bytes(payload))
    print(json.dumps({"status": payload["status"], "rows": len(rows)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
