#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    pages = read(HERE / "PASS972_SIX_PAGE_VISUAL_OWNER_REVISION.tsv")
    labels = read(HERE / "PASS972_F88R_SIXTEEN_LABEL_OWNER_MAP.tsv")
    checks = {
        "six_pages": len(pages) == 6,
        "exact_pages": {r["physical_page"] for r in pages} == {"f10r", "f11r", "f13r", "f55v", "f56r", "f88r"},
        "event_total": sum(int(r["events"]) for r in pages) == 589,
        "all_page_readings": all(r["revised_page_reading_de"] for r in pages),
        "all_visual_owners": len({r["visual_owner_id"] for r in pages}) == 6,
        "sixteen_f88_labels": len(labels) == 16,
        "sixteen_label_events": len({r["event_id"] for r in labels}) == 16,
        "sixteen_label_objects": len({r["visual_object_id"] for r in labels}) == 16,
        "labels_not_operations": all(r["portable_operation_reading_allowed"] == "NO__LABEL_REGISTER" for r in labels),
        "no_empty_cells": all(all(v != "" for v in r.values()) for r in pages + labels),
        "sealed_absent": all("f84" not in "\t".join(r.values()).lower() for r in pages + labels),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "PASS972_VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
