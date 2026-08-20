#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path


def root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("repository root not found")


ROOT = root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt390_q20_inter_record_pointer_census"
ART = BASE / "artifacts"
FRAME = ART / "gdt390_record_frame.tsv"
FREEZE = ART / "gdt390_pre_image_freeze.json"
OUT = ART / "gdt390_pre_image_freeze_validation.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(payload: dict) -> str:
    clone = dict(payload)
    clone.pop("content_hash", None)
    return hashlib.sha256(json.dumps(clone, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def main() -> int:
    with FRAME.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    freeze = json.loads(FREEZE.read_text(encoding="utf-8"))
    checks: list[dict[str, object]] = []
    def check(name: str, passed: bool, detail: object) -> None:
        checks.append({"check": name, "pass": bool(passed), "detail": detail})
        if not passed:
            raise AssertionError(name)
    pages = {row["page"] for row in rows}
    folios = {row["physical_folio"] for row in rows}
    units = {row["unit_id"] for row in rows}
    check("record_count", len(rows) == len(units) == 170, len(rows))
    check("page_count", len(pages) == 13, len(pages))
    check("folio_count", len(folios) == 8, len(folios))
    check("folio_set", folios == {"f104", "f105", "f106", "f107", "f112", "f113", "f114", "f115"}, sorted(folios))
    check("no_f84_page_or_locus", all(not row["page"].lower().startswith("f84") and not row["open_locus"].lower().startswith("f84") and all(not locus.lower().startswith("f84") for locus in row["body_line_loci"].split("|")) for row in rows), "safe")
    check("positive_record_shape", all(int(row["star_ordinal"]) >= 1 and int(row["record_line_count"]) >= 1 for row in rows), "valid")
    check("freeze_content_hash", freeze["content_hash"] == digest(freeze), freeze["content_hash"])
    check("frame_hash_bound", freeze["outputs"][str(FRAME.relative_to(ROOT))] == sha(FRAME), sha(FRAME))
    check("page_counts", freeze["frame"]["page_record_counts"] == dict(sorted(Counter(row["page"] for row in rows).items())), freeze["frame"]["page_record_counts"])
    check("folio_counts", freeze["frame"]["folio_record_counts"] == dict(sorted(Counter(row["physical_folio"] for row in rows).items())), freeze["frame"]["folio_record_counts"])
    check("page_order", freeze["frame"]["page_review_order"] == sorted(pages, key=lambda page: hashlib.sha256(("GDT390_PAGE_ORDER_V1|" + page).encode()).hexdigest()), freeze["frame"]["page_review_order"][:3])
    check("record_order", freeze["frame"]["record_review_order"] == sorted(units, key=lambda unit: hashlib.sha256(("GDT390_RECORD_ORDER_V1|" + unit).encode()).hexdigest()), len(units))
    check("five_states", len(freeze["allowed_page_states"]) == 5, freeze["allowed_page_states"])
    check("capacity", freeze["eligibility"]["minimum_edges"] == 50 and freeze["eligibility"]["minimum_physical_folios"] == 5, freeze["eligibility"])
    check("scoring_locked", freeze["scoring_authorized"] is False, False)
    check("access_locked", freeze["access"]["formal_suffix_fields_parsed_retained_or_displayed"] is False and freeze["access"]["image_access_before_freeze"] is False and freeze["access"]["f84_access"] is False, freeze["access"])
    payload = {
        "schema": "GDT390_PRE_IMAGE_FREEZE_VALIDATION_V1",
        "status": "PASS",
        "checks_passed": len(checks),
        "checks_total": len(checks),
        "freeze_content_hash": freeze["content_hash"],
        "checks": checks,
    }
    payload["content_hash"] = digest(payload)
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(f"PASS {len(checks)}/{len(checks)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
