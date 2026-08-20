#!/usr/bin/env python3
"""Independent accounting validator for the GDT392 pre-image freeze."""
from __future__ import annotations

import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path


def root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("repository root not found")


ROOT = root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt392_special_circle_start_direction_census"
ART = BASE / "artifacts"
INV = ROOT / "experiments/semantic_assumptions/results/special_circle_text_blind_array_inventory.tsv"
FRAME = ART / "gdt392_array_frame.tsv"
FREEZE = ART / "gdt392_pre_image_freeze.json"


def tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(obj: object) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def main() -> int:
    checks: list[dict[str, object]] = []

    def check(name: str, passed: bool, detail: object) -> None:
        checks.append({"check": name, "pass": bool(passed), "detail": detail})

    raw = INV.read_text(encoding="utf-8").splitlines()
    header = raw[0].split("\t")
    pi, fi = header.index("page"), header.index("physical_folio")
    selectors = [(line.split("\t")[pi], line.split("\t")[fi]) for line in raw[1:]]
    check("source_no_f84_selector", all(not p.lower().startswith("f84") and not f.lower().startswith("f84") for p, f in selectors), len(selectors))
    source = tsv(INV)
    frame = tsv(FRAME)
    freeze = json.loads(FREEZE.read_text(encoding="utf-8"))
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in source:
        grouped[row["array_id"]].append(row)
    check("source_504_slots", len(source) == 504, len(source))
    check("source_45_arrays", len(grouped) == 45, len(grouped))
    check("source_23_pages_7_folios", len({r["page"] for r in source}) == 23 and len({r["physical_folio"] for r in source}) == 7, f"{len({r['page'] for r in source})}/{len({r['physical_folio'] for r in source})}")
    contiguous = all(sorted(int(r["slot_index"]) for r in rows) == list(range(1, int(rows[0]["slot_count"]) + 1)) for rows in grouped.values())
    check("source_slots_contiguous", contiguous, "all arrays")
    expected_ids = [rows[0]["array_id"] for _, rows in sorted(((int(rows[0]["array_index"]), rows) for rows in grouped.values()))]
    check("frame_45_unique", len(frame) == 45 and len({r["array_id"] for r in frame}) == 45, len(frame))
    check("frame_inventory_order", [r["array_id"] for r in frame] == expected_ids, frame[:2])
    check("frame_slot_sum", sum(int(r["slot_count"]) for r in frame) == 504, sum(int(r["slot_count"]) for r in frame))
    check("frame_formal_sealed", all(r["formal_access_state"] == "SEALED" for r in frame), "all")
    check("freeze_status", freeze["status"] == "FROZEN_BEFORE_FOCUSED_ARRAY_REVIEW", freeze["status"])
    check("freeze_review_not_performed", freeze["access"]["focused_array_review_performed"] is False, freeze["access"])
    check("freeze_formal_zero", freeze["access"]["voynich_surface_or_formal_rows_read"] == 0, freeze["access"])
    check("freeze_f84_false", freeze["access"]["f84_opened_parsed_retained_or_scored"] is False, freeze["access"])
    check("freeze_review_order", freeze["frame"]["array_review_order"] == expected_ids, expected_ids[:2])
    check("freeze_capacity", "at least 50 directed edges span at least five physical folios" in freeze["eligibility"], freeze["eligibility"])
    for path, expected in freeze["inputs"].items():
        check(f"input_hash:{path}", sha(ROOT / path) == expected, expected)
    for path, expected in freeze["outputs"].items():
        check(f"output_hash:{path}", sha(ROOT / path) == expected, expected)
    body = dict(freeze)
    claimed = body.pop("content_hash")
    check("freeze_content_hash", digest(body) == claimed, claimed)
    failed = sum(not row["pass"] for row in checks)
    result = {
        "schema": "GDT392_PRE_IMAGE_FREEZE_VALIDATION_V1",
        "status": "PASS" if not failed else "FAIL",
        "checks_passed": len(checks) - failed,
        "checks_failed": failed,
        "checks": checks,
        "scope": "Independent reconstruction of the complete 45-array/504-slot frame, order, f84 exclusion, freeze states, and hashes; no visual judgment or Voynich formal identity is evaluated.",
    }
    result["content_hash"] = digest(result)
    out = ART / "gdt392_pre_image_freeze_validation.json"
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(f"{result['status']} {result['checks_passed']}/{len(checks)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
