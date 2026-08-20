#!/usr/bin/env python3
"""Independent validation of the GDT393 residual-page freeze."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
EXP = ROOT / "experiments/yolo/gdt393_remaining_page_connector_census"
ART = EXP / "artifacts"
FRAME = ART / "gdt393_residual_page_frame.tsv"
FREEZE = ART / "gdt393_pre_image_freeze.json"
OUT = ART / "gdt393_pre_image_freeze_validation.json"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    checks: list[dict[str, object]] = []

    def check(name: str, passed: bool, detail: object) -> None:
        checks.append({"name": name, "pass": bool(passed), "detail": detail})

    freeze = json.loads(FREEZE.read_text(encoding="utf-8"))
    with FRAME.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    expected = {
        "f2r", "f11v", "f17r", "f41v", "f49v", "f66r", "f68v1",
        "f68v3", "f70r2", "f86v4", "f101v", "f116v",
    }
    pages = {row["page"] for row in rows}
    check("exact_residual_page_set", pages == expected, sorted(pages))
    check("unique_pages", len(rows) == len(pages) == 12, len(rows))
    check("positive_role_capacity", all(sum(int(row[k] or 0) for k in ("L_count", "C_count", "R_count")) > 0 for row in rows), len(rows))
    check("no_f84", all(not row["page"].lower().startswith("f84") for row in rows), sorted(pages))
    check("formal_access_locked", all(row["formal_access_state"] == "FORBIDDEN_BEFORE_CAPACITY_GATE" for row in rows), len(rows))
    check("freeze_frame_hash", freeze["outputs"][str(FRAME.relative_to(ROOT))] == digest(FRAME), digest(FRAME))
    check("freeze_counts", freeze["frame_rows"] == 12 and freeze["frame_pages"] == 12, [freeze["frame_rows"], freeze["frame_pages"]])
    check("raw_selector_guard", freeze["f84_selector_guard"] == "RAW_PAGE_PREFIX_REJECTED_BEFORE_ROW_PARSE", freeze["f84_selector_guard"])
    check("no_pre_freeze_image", freeze["image_opened_before_freeze"] is False, freeze["image_opened_before_freeze"])
    check("formal_payload_closed", freeze["f84_formal_payload_opened"] is False and freeze["f84_image_opened"] is False and freeze["formal_access_before_capacity_gate"] is False, False)
    check("prior_metadata_parse_disclosed", "split two forbidden page-description metadata rows" in freeze["prior_workspace_audit_disclosure"], freeze["prior_workspace_audit_disclosure"])
    passed = sum(int(item["pass"]) for item in checks)
    payload = {"experiment_id": "GDT393", "status": "PASS" if passed == len(checks) else "FAIL", "checks_passed": passed, "checks_total": len(checks), "checks": checks}
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"{payload['status']} {passed}/{len(checks)}")
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
