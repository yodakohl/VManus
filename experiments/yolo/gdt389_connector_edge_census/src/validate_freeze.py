#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


def root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("repository root not found")


ROOT = root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt389_connector_edge_census"
ART = BASE / "artifacts"
FRAME = ROOT / "experiments/yolo/gdt388_acquisition_ready_relation_edge_protocol/artifacts/gdt388_page_frame.tsv"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    checks: list[str] = []

    def check(name: str, condition: bool) -> None:
        assert condition, name
        checks.append(name)

    freeze = json.loads((ART / "gdt389_pre_image_freeze.json").read_text())
    clone = dict(freeze)
    reported = clone.pop("content_hash")
    check("content_hash", reported == hashlib.sha256(json.dumps(clone, sort_keys=True, separators=(",", ":")).encode()).hexdigest())
    for path, digest in freeze["inputs"].items():
        check("input_hash:" + path, sha(ROOT / path) == digest)
    for path, digest in freeze["implementation"].items():
        check("implementation_hash:" + path, sha(ROOT / path) == digest)
    with FRAME.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    pages = sorted(row["page"] for row in rows)
    folios = sorted({row["physical_folio"] for row in rows})
    expected_order = sorted(pages, key=lambda page: hashlib.sha256(("GDT389_PAGE_ORDER_V1|" + page).encode()).hexdigest())
    check("exact_page_universe", freeze["page_universe"]["pages"] == pages and freeze["page_universe"]["page_count"] == 61)
    check("exact_folio_universe", freeze["page_universe"]["physical_folios"] == folios and freeze["page_universe"]["folio_count"] == 30)
    check("deterministic_order", freeze["page_universe"]["review_order"] == expected_order)
    check("no_f84_page", all(not page.lower().startswith("f84") for page in pages))
    check("five_screen_states", len(freeze["allowed_page_screen_states"]) == 5)
    check("direction_rules", "VISIBLE_ARROWHEAD" in freeze["allowed_direction_bases"] and "TEXT_READING_ORDER" in freeze["forbidden_direction_bases"])
    check("capacity_gates", freeze["eligibility"]["minimum_edges"] == 50 and freeze["eligibility"]["minimum_physical_folios"] == 5)
    check("safe_loader", freeze["access"]["raw_canvas_label_allowlist_before_retention"] is True and freeze["access"]["reject_mixed_canvas_with_any_f84_label"] is True)
    check("no_formal_or_automatic_vision", freeze["access"]["formal_identity_access"] is False and freeze["access"]["ocr_or_automated_vision"] is False)
    check("scoring_locked", freeze["scoring_authorized"] is False)
    check("status", freeze["status"] == "FROZEN_BEFORE_IMAGE_ACCESS")
    result = {
        "schema": "GDT389_PRE_IMAGE_FREEZE_VALIDATION_V1",
        "status": "PASS",
        "checks_passed": len(checks),
        "checks_total": len(checks),
        "checks": checks,
        "freeze_hash": sha(ART / "gdt389_pre_image_freeze.json"),
    }
    (ART / "gdt389_pre_image_freeze_validation.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(f"PASS {len(checks)}/{len(checks)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
