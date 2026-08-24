#!/usr/bin/env python3
"""Validate the compact Biological renderer manual."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def main() -> None:
    trace = read("THREE_HUNDRED_TWELFTH_281_RENDERER_TRACE.tsv")
    palettes = read("THREE_HUNDRED_TWELFTH_30_MULTISURFACE_PALETTES.tsv")
    wrappers = read("THREE_HUNDRED_TWELFTH_EIGHT_WRAPPER_RULES.tsv")
    residuals = read("THREE_HUNDRED_TWELFTH_12_LOCAL_COPY_EXCEPTIONS.tsv")
    summary = json.loads((HERE / "BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    checks = {
        "fixed_rows_381": summary["fixed_prose_events"] == 381,
        "bio_rows_281": len(trace) == summary["bio_events"] == 281,
        "bio_cards_124": len({row["master_card_id"] for row in trace}) == summary["bio_card_types"] == 124,
        "palettes_30": len(palettes) == summary["multisurface_bio_cards"] == 30,
        "switching_27": sum(int(row["distinct_bio_surfaces"]) > 1 for row in palettes) == summary["cards_switching_surface_inside_bio"] == 27,
        "wrappers_8": len(wrappers) == summary["wrapper_classes"] == 8,
        "powered_210": sum(row["renderer_state"] == "EXECUTABLE_POWERED_CELL" for row in trace) == summary["powered_events"] == 210,
        "unlicensed_71": sum(row["renderer_state"] != "EXECUTABLE_POWERED_CELL" for row in trace) == summary["unlicensed_events"] == 71,
        "palette_hits_227": sum(row["palette_renderer_match"] == "YES" for row in trace) == summary["palette_renderer_hits"] == 227,
        "record_position_269": sum(row["record_position_match"] == "YES" for row in trace) == summary["record_position_hits"] == 269,
        "residuals_12": len(residuals) == summary["local_copy_exceptions"] == 12,
        "event_ids_unique": len({row["event_id"] for row in trace}) == 281,
        "semantics_present": all(row["short_value_de"] for row in trace),
        "wrapper_semantics_none": all(row["semantic_contribution"] == "NONE" for row in wrappers),
        "no_sealed_page": not any(
            row.get("page", "").lower().startswith("f84") or row.get("locus", "").lower().startswith("f84")
            for rows in (trace, palettes, residuals) for row in rows
        ),
    }
    failed = [name for name, passed in checks.items() if not passed]
    result = {"status": "PASS" if not failed else "FAIL", "checks": checks, "failed": failed}
    (HERE / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
