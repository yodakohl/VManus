#!/usr/bin/env python3
"""Aggregate the frozen GDT393 direct-visual census without formal access."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
EXP = ROOT / "experiments/yolo/gdt393_remaining_page_connector_census"
ART = EXP / "artifacts"
RESULT = ART / "gdt393_result.json"


def read_tsv(name: str) -> list[dict[str, str]]:
    with (ART / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    frame = read_tsv("gdt393_residual_page_frame.tsv")
    images = read_tsv("gdt393_image_manifest.tsv")
    obs = read_tsv("gdt393_page_observations.tsv")
    candidates = read_tsv("gdt393_ambiguous_candidates.tsv")
    edges = read_tsv("gdt393_eligible_edge_packet.tsv")
    gates = read_tsv("gdt393_capacity_gates.tsv")
    access = json.loads((ART / "gdt393_access_log.json").read_text(encoding="utf-8"))
    freeze = json.loads((ART / "gdt393_pre_image_freeze.json").read_text(encoding="utf-8"))

    pages = {row["page"] for row in frame}
    if pages != {row["page"] for row in images} or pages != {row["page"] for row in obs}:
        raise ValueError("frame/image/observation page mismatch")
    if any(page.lower().startswith("f84") for page in pages):
        raise ValueError("forbidden page entered retained frame")
    outcomes = Counter(row["page_outcome"] for row in obs)
    eligible_folios = {row["physical_folio"] for row in edges}
    gate_pass = all(row["pass"] == "1" for row in gates)
    if gate_pass or edges:
        raise ValueError("formal score remains locked unless a later capacity packet passes")

    input_paths = [
        ART / "gdt393_pre_image_freeze.json",
        ART / "gdt393_pre_image_freeze_validation.json",
        ART / "gdt393_residual_page_frame.tsv",
        ART / "gdt393_image_manifest.tsv",
        ART / "gdt393_page_observations.tsv",
        ART / "gdt393_ambiguous_candidates.tsv",
        ART / "gdt393_eligible_edge_packet.tsv",
        ART / "gdt393_capacity_gates.tsv",
        ART / "gdt393_access_log.json",
    ]
    docs = [EXP / "METHOD.md", EXP / "REPORT.md", EXP / "README.md"]
    implementations = [Path(__file__).resolve(), EXP / "src/validate.py", EXP / "src/freeze.py", EXP / "src/validate_freeze.py"]

    payload = {
        "experiment_id": "GDT393",
        "status": "COMPLETE_RESIDUAL_CENSUS_ZERO_ELIGIBLE_DIRECTED_EDGES",
        "frame_pages": len(pages),
        "frame_physical_folios": len({row["physical_folio"] for row in images}),
        "reviewed_official_canvases": len({row["canvas_id"] for row in images}),
        "role_counts": {
            "L": sum(int(row["L_count"] or 0) for row in frame),
            "C": sum(int(row["C_count"] or 0) for row in frame),
            "R": sum(int(row["R_count"] or 0) for row in frame),
        },
        "page_outcomes": dict(sorted(outcomes.items())),
        "ambiguous_candidates": len(candidates),
        "eligible_directed_edges": len(edges),
        "eligible_physical_folios": len(eligible_folios),
        "capacity_gate_pass": gate_pass,
        "formal_grounding_score_run": False,
        "formal_identity_rows_joined": 0,
        "review_provenance": "POST_FREEZE_SINGLE_AI_DIRECT_VISUAL_WITH_SAFE_PAGE_FORMAL_EXPOSURE_DISCLOSED",
        "prior_metadata_parse_disclosed": bool(access["f84_metadata_parse_disclosure"]),
        "f84_image_opened": access["f84_image_opened"],
        "f84_formal_payload_opened": access["f84_formal_payload_opened"],
        "decision_basis": "Zero oriented two-locus connectors; inherited 50-edge/5-folio/mobile-null gate fails.",
        "claim_ceiling": "Complete geometry-only capacity census of the residual page-role frame; no parent, reference, operator, syntax, POS, meaning, language, plaintext, or translation.",
        "freeze_status": freeze["status"],
        "input_hashes": {str(path.relative_to(ROOT)): sha(path) for path in input_paths},
        "document_hashes": {str(path.relative_to(ROOT)): sha(path) for path in docs},
        "implementation_hashes": {str(path.relative_to(ROOT)): sha(path) for path in implementations},
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    payload["content_sha256"] = hashlib.sha256(encoded).hexdigest()
    RESULT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": payload["status"], "edges": len(edges)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
